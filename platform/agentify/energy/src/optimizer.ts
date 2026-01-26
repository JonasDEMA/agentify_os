import { logger } from './logger';
import { EnergyApiClient } from './energy-api-client';
import { database } from './database';
import { OptimizePowerRequest, ChargingMode, Loadpoint } from './types';

// Pricing data structure (can be extended with real pricing API)
interface PricingData {
  current_price_per_kwh: number;
  forecast: Array<{
    timestamp: string;
    price_per_kwh: number;
  }>;
}

// Solar forecast data structure (can be extended with real solar API)
interface SolarForecast {
  current_pv_power: number;
  forecast: Array<{
    timestamp: string;
    pv_power_w: number;
  }>;
}

// Optimization result
interface OptimizationResult {
  success: boolean;
  loadpoint_id: number;
  objective: string;
  optimized_mode: ChargingMode;
  optimized_power: number;
  estimated_savings?: number;
  estimated_renewable_percentage?: number;
  estimated_charge_time_hours?: number;
  reasoning: string;
}

export class PowerOptimizer {
  private energyApi: EnergyApiClient;
  private agentId: string;

  // Default pricing (EUR per kWh) - can be overridden with real data
  private readonly DEFAULT_GRID_PRICE = 0.30;
  private readonly DEFAULT_PEAK_PRICE = 0.40;
  private readonly DEFAULT_OFF_PEAK_PRICE = 0.20;

  // Grid frequency thresholds for balancing
  private readonly GRID_FREQUENCY_NOMINAL = 50.0;
  private readonly GRID_FREQUENCY_TOLERANCE = 0.05;

  constructor(energyApi: EnergyApiClient) {
    this.energyApi = energyApi;
    this.agentId = process.env.AGENT_ID || 'agent.energy.controller';
  }

  async optimizePower(request: OptimizePowerRequest): Promise<OptimizationResult> {
    logger.info('Power optimization request', { request });

    const { loadpoint_id, objective, constraints } = request;

    try {
      // Get current loadpoint state
      const loadpoint = await this.energyApi.getLoadpoint(loadpoint_id);
      
      // Get grid frequency for grid-aware optimization
      const gridFrequency = await this.energyApi.getGridFrequency();

      // Route to appropriate optimization algorithm
      let result: OptimizationResult;

      switch (objective) {
        case 'minimize_cost':
          result = await this.minimizeCost(loadpoint, gridFrequency, constraints);
          break;

        case 'maximize_renewable':
          result = await this.maximizeRenewable(loadpoint, gridFrequency, constraints);
          break;

        case 'balance_grid':
          result = await this.balanceGrid(loadpoint, gridFrequency, constraints);
          break;

        case 'fast_charge':
          result = await this.fastCharge(loadpoint, gridFrequency, constraints);
          break;

        default:
          throw new Error(`Unknown optimization objective: ${objective}`);
      }

      // Apply the optimized settings
      await this.applyOptimization(loadpoint_id, result);

      // Store optimization result in database
      await database.createEnergyMetrics({
        agent_id: this.agentId,
        loadpoint_id: loadpoint_id,
        actual_power: loadpoint.actual_power,
        desired_power: result.optimized_power,
        charging_mode: result.optimized_mode,
        timestamp: new Date().toISOString()
      });

      logger.info('Power optimization successful', { result });
      return result;

    } catch (error) {
      logger.error('Failed to optimize power', { error, request });
      throw error;
    }
  }

  private async minimizeCost(
    loadpoint: Loadpoint,
    gridFrequency: number,
    constraints?: Record<string, any>
  ): Promise<OptimizationResult> {
    logger.debug('Optimizing for minimum cost', { loadpoint_id: loadpoint.id });

    // Get current time to determine if peak or off-peak
    const hour = new Date().getHours();
    const isPeakHour = hour >= 7 && hour < 22;

    // Calculate pricing
    const currentPrice = isPeakHour ? this.DEFAULT_PEAK_PRICE : this.DEFAULT_OFF_PEAK_PRICE;
    const maxCost = constraints?.max_cost_per_kwh || Infinity;

    let optimizedMode: ChargingMode;
    let optimizedPower: number;
    let reasoning: string;
    let estimatedSavings = 0;

    if (currentPrice > maxCost) {
      // Price too high, don't charge
      optimizedMode = ChargingMode.OFF;
      optimizedPower = 0;
      reasoning = `Current price ${currentPrice} EUR/kWh exceeds max cost ${maxCost} EUR/kWh. Charging disabled.`;
    } else if (!isPeakHour) {
      // Off-peak hours, charge at maximum power
      optimizedMode = ChargingMode.NOW;
      optimizedPower = loadpoint.max_power;
      estimatedSavings = (this.DEFAULT_PEAK_PRICE - currentPrice) * (loadpoint.max_power / 1000);
      reasoning = `Off-peak hours (${hour}:00). Charging at max power ${optimizedPower}W. Saving ${estimatedSavings.toFixed(2)} EUR/h vs peak.`;
    } else {
      // Peak hours, use solar only if available
      optimizedMode = ChargingMode.PV;
      optimizedPower = loadpoint.min_power;
      reasoning = `Peak hours (${hour}:00). Using solar-only mode to minimize grid cost.`;
    }

    return {
      success: true,
      loadpoint_id: loadpoint.id,
      objective: 'minimize_cost',
      optimized_mode: optimizedMode,
      optimized_power: optimizedPower,
      estimated_savings: estimatedSavings,
      reasoning
    };
  }

  private async maximizeRenewable(
    loadpoint: Loadpoint,
    gridFrequency: number,
    constraints?: Record<string, any>
  ): Promise<OptimizationResult> {
    logger.debug('Optimizing for maximum renewable', { loadpoint_id: loadpoint.id });

    const minRenewablePercentage = constraints?.min_renewable_percentage || 80;
    const hour = new Date().getHours();
    const isDaytime = hour >= 6 && hour < 20;

    let optimizedMode: ChargingMode;
    let optimizedPower: number;
    let reasoning: string;
    let estimatedRenewablePercentage = 0;

    if (isDaytime) {
      // Daytime: prioritize solar charging
      optimizedMode = ChargingMode.PV;
      optimizedPower = loadpoint.max_power;
      estimatedRenewablePercentage = 100;
      reasoning = `Daytime (${hour}:00). Using pure solar mode (pv) for 100% renewable energy.`;
    } else {
      // Nighttime: check if we can use stored solar or must use grid
      if (minRenewablePercentage >= 100) {
        // Can't meet 100% renewable at night, disable charging
        optimizedMode = ChargingMode.OFF;
        optimizedPower = 0;
        estimatedRenewablePercentage = 0;
        reasoning = `Nighttime (${hour}:00). Cannot meet ${minRenewablePercentage}% renewable requirement. Charging disabled.`;
      } else {
        // Use minimum grid power
        optimizedMode = ChargingMode.MINPV;
        optimizedPower = loadpoint.min_power;
        estimatedRenewablePercentage = 30; // Estimate based on minpv mode
        reasoning = `Nighttime (${hour}:00). Using minpv mode for ~${estimatedRenewablePercentage}% renewable energy.`;
      }
    }

    return {
      success: true,
      loadpoint_id: loadpoint.id,
      objective: 'maximize_renewable',
      optimized_mode: optimizedMode,
      optimized_power: optimizedPower,
      estimated_renewable_percentage: estimatedRenewablePercentage,
      reasoning
    };
  }

  private async balanceGrid(
    loadpoint: Loadpoint,
    gridFrequency: number,
    constraints?: Record<string, any>
  ): Promise<OptimizationResult> {
    logger.debug('Optimizing for grid balance', { loadpoint_id: loadpoint.id, gridFrequency });

    const frequencyDeviation = gridFrequency - this.GRID_FREQUENCY_NOMINAL;
    const absDeviation = Math.abs(frequencyDeviation);

    let optimizedMode: ChargingMode;
    let optimizedPower: number;
    let reasoning: string;

    if (absDeviation > this.GRID_FREQUENCY_TOLERANCE) {
      // Grid is unstable
      if (frequencyDeviation > 0) {
        // Frequency too high (excess generation) - increase load
        optimizedMode = ChargingMode.NOW;
        optimizedPower = loadpoint.max_power;
        reasoning = `Grid frequency high (${gridFrequency.toFixed(3)} Hz). Increasing load to ${optimizedPower}W to absorb excess generation.`;
      } else {
        // Frequency too low (excess demand) - reduce load
        optimizedMode = ChargingMode.OFF;
        optimizedPower = 0;
        reasoning = `Grid frequency low (${gridFrequency.toFixed(3)} Hz). Reducing load to 0W to support grid stability.`;
      }
    } else {
      // Grid is stable - use solar-optimized charging
      optimizedMode = ChargingMode.PV;
      optimizedPower = loadpoint.max_power;
      reasoning = `Grid frequency stable (${gridFrequency.toFixed(3)} Hz). Using solar mode for grid-friendly charging.`;
    }

    return {
      success: true,
      loadpoint_id: loadpoint.id,
      objective: 'balance_grid',
      optimized_mode: optimizedMode,
      optimized_power: optimizedPower,
      reasoning
    };
  }

  private async fastCharge(
    loadpoint: Loadpoint,
    gridFrequency: number,
    constraints?: Record<string, any>
  ): Promise<OptimizationResult> {
    logger.debug('Optimizing for fast charge', { loadpoint_id: loadpoint.id });

    const targetSoc = constraints?.target_soc || 100;
    const chargeByTime = constraints?.charge_by_time;
    const maxPowerLimit = constraints?.max_power || loadpoint.max_power;

    let optimizedMode: ChargingMode;
    let optimizedPower: number;
    let reasoning: string;
    let estimatedChargeTimeHours = 0;

    // Check grid frequency for safety
    const frequencyDeviation = Math.abs(gridFrequency - this.GRID_FREQUENCY_NOMINAL);

    if (frequencyDeviation > this.GRID_FREQUENCY_TOLERANCE * 2) {
      // Grid very unstable, reduce power for safety
      optimizedMode = ChargingMode.NOW;
      optimizedPower = loadpoint.min_power;
      reasoning = `Grid unstable (${gridFrequency.toFixed(3)} Hz). Charging at minimum power ${optimizedPower}W for safety.`;
    } else {
      // Grid stable, charge at maximum safe power
      optimizedMode = ChargingMode.NOW;
      optimizedPower = Math.min(maxPowerLimit, loadpoint.max_power);

      // Estimate charge time (assuming 60 kWh battery, current SOC unknown)
      const estimatedBatteryCapacity = 60; // kWh
      const remainingCapacity = estimatedBatteryCapacity * ((100 - targetSoc) / 100);
      estimatedChargeTimeHours = (remainingCapacity * 1000) / optimizedPower;

      reasoning = `Fast charge mode. Charging at maximum power ${optimizedPower}W. Estimated time to ${targetSoc}% SOC: ${estimatedChargeTimeHours.toFixed(1)}h.`;

      if (chargeByTime) {
        reasoning += ` Target completion: ${chargeByTime}.`;
      }
    }

    return {
      success: true,
      loadpoint_id: loadpoint.id,
      objective: 'fast_charge',
      optimized_mode: optimizedMode,
      optimized_power: optimizedPower,
      estimated_charge_time_hours: estimatedChargeTimeHours,
      reasoning
    };
  }

  private async applyOptimization(loadpointId: number, result: OptimizationResult): Promise<void> {
    logger.info('Applying optimization', { loadpointId, result });

    // Set charging mode
    await this.energyApi.setChargingMode(loadpointId, result.optimized_mode);

    // Set power limit if not OFF mode
    if (result.optimized_mode !== ChargingMode.OFF && result.optimized_power > 0) {
      await this.energyApi.setMaxPower(loadpointId, result.optimized_power);

      // Enable power tracking for precise control
      await this.energyApi.enablePowerTracking(loadpointId);
    }

    logger.info('Optimization applied successfully', { loadpointId });
  }

  // Helper method to get pricing data (can be extended with real API)
  private async getPricingData(): Promise<PricingData> {
    // TODO: Integrate with real pricing API (e.g., ENTSO-E, Tibber, etc.)
    const hour = new Date().getHours();
    const isPeakHour = hour >= 7 && hour < 22;

    return {
      current_price_per_kwh: isPeakHour ? this.DEFAULT_PEAK_PRICE : this.DEFAULT_OFF_PEAK_PRICE,
      forecast: []
    };
  }

  // Helper method to get solar forecast (can be extended with real API)
  private async getSolarForecast(): Promise<SolarForecast> {
    // TODO: Integrate with real solar forecast API (e.g., Solcast, forecast.solar, etc.)
    const hour = new Date().getHours();
    const isDaytime = hour >= 6 && hour < 20;

    return {
      current_pv_power: isDaytime ? 5000 : 0, // Estimate
      forecast: []
    };
  }
}

