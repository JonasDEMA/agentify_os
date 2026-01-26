import EVCCClient, { EVCCLoadpoint, EVCCSystemState } from './evcc-client';
import LoadpointController from './loadpoint-controller';
import logger from './logger';
import { saveOptimizationHistory } from './database';

export type OptimizationObjective = 'minimize_cost' | 'maximize_pv' | 'balance_grid' | 'fast_charge';

export interface OptimizeChargingParams {
  loadpoint_id: number;
  objective: OptimizationObjective;
  constraints?: {
    max_power?: number;
    target_soc?: number;
    deadline?: string;
  };
}

export interface OptimizationDecision {
  mode: 'off' | 'now' | 'minpv' | 'pv';
  max_current?: number;
  phases?: 1 | 3;
}

export interface OptimizeChargingResult {
  success: boolean;
  loadpoint_id: number;
  objective: OptimizationObjective;
  decision: OptimizationDecision;
  reasoning: string;
  metrics: {
    current_pv_power: number;
    current_grid_power: number;
    current_battery_soc: number | null;
    estimated_cost_savings?: number;
    estimated_pv_usage?: number;
  };
}

/**
 * Charging Optimizer
 * Intelligent charging optimization based on different objectives
 */
export class ChargingOptimizer {
  private evccClient: EVCCClient;
  private loadpointController: LoadpointController;

  constructor(evccClient: EVCCClient, loadpointController: LoadpointController) {
    this.evccClient = evccClient;
    this.loadpointController = loadpointController;
  }

  /**
   * Optimize charging based on objective
   */
  async optimizeCharging(params: OptimizeChargingParams): Promise<OptimizeChargingResult> {
    const { loadpoint_id, objective, constraints } = params;

    logger.info('Optimizing charging', { params });

    // Get system state
    const systemState = await this.evccClient.getSystemState();
    const loadpoint = systemState.result.loadpoints.find(lp => lp.id === loadpoint_id);

    if (!loadpoint) {
      throw new Error(`Loadpoint ${loadpoint_id} not found`);
    }

    if (!loadpoint.connected) {
      throw new Error(`No vehicle connected to loadpoint ${loadpoint_id}`);
    }

    // Select optimization algorithm
    let decision: OptimizationDecision;
    let reasoning: string;

    switch (objective) {
      case 'minimize_cost':
        ({ decision, reasoning } = this.minimizeCost(systemState, loadpoint, constraints));
        break;
      case 'maximize_pv':
        ({ decision, reasoning } = this.maximizePV(systemState, loadpoint, constraints));
        break;
      case 'balance_grid':
        ({ decision, reasoning } = this.balanceGrid(systemState, loadpoint, constraints));
        break;
      case 'fast_charge':
        ({ decision, reasoning } = this.fastCharge(systemState, loadpoint, constraints));
        break;
      default:
        throw new Error(`Unknown optimization objective: ${objective}`);
    }

    // Apply decision
    await this.loadpointController.controlLoadpoint({
      loadpoint_id,
      mode: decision.mode,
      max_current: decision.max_current,
      phases: decision.phases,
    });

    // Save optimization history
    await saveOptimizationHistory({
      loadpoint_id,
      objective,
      decision,
      reasoning,
      constraints: constraints || {},
      result: {
        pv_power: systemState.result.pvPower,
        grid_power: systemState.result.gridPower,
        battery_soc: systemState.result.batterySoc,
      },
    });

    return {
      success: true,
      loadpoint_id,
      objective,
      decision,
      reasoning,
      metrics: {
        current_pv_power: systemState.result.pvPower,
        current_grid_power: systemState.result.gridPower,
        current_battery_soc: systemState.result.batterySoc,
      },
    };
  }

  /**
   * Minimize cost optimization
   * Charge during off-peak hours or when PV is available
   */
  private minimizeCost(
    systemState: EVCCSystemState,
    loadpoint: EVCCLoadpoint,
    constraints?: any
  ): { decision: OptimizationDecision; reasoning: string } {
    const currentHour = new Date().getHours();
    const isOffPeak = currentHour < 7 || currentHour >= 22;
    const pvAvailable = systemState.result.pvPower > 1000;

    let decision: OptimizationDecision;
    let reasoning: string;

    if (pvAvailable) {
      // Use PV power when available (free energy)
      decision = { mode: 'pv', phases: 3 };
      reasoning = `PV power available (${systemState.result.pvPower}W). Using PV-only mode for free solar charging.`;
    } else if (isOffPeak) {
      // Charge during off-peak hours
      decision = { mode: 'now', max_current: 16, phases: 3 };
      reasoning = `Off-peak hours (${currentHour}:00). Charging at moderate power to minimize cost.`;
    } else {
      // Peak hours - use minimum PV mode or wait
      if (systemState.result.pvPower > 500) {
        decision = { mode: 'minpv', phases: 1 };
        reasoning = `Peak hours with some PV (${systemState.result.pvPower}W). Using min+PV mode to reduce grid usage.`;
      } else {
        decision = { mode: 'off' };
        reasoning = `Peak hours with no PV. Pausing charging to avoid high electricity costs.`;
      }
    }

    return { decision, reasoning };
  }

  /**
   * Maximize PV optimization
   * Maximize use of solar energy for charging
   */
  private maximizePV(
    systemState: EVCCSystemState,
    loadpoint: EVCCLoadpoint,
    constraints?: any
  ): { decision: OptimizationDecision; reasoning: string } {
    const pvPower = systemState.result.pvPower;
    const gridPower = systemState.result.gridPower;
    const batteryPower = systemState.result.batteryPower;

    let decision: OptimizationDecision;
    let reasoning: string;

    if (pvPower > 5000) {
      // High PV production - charge at maximum power
      decision = { mode: 'pv', max_current: 32, phases: 3 };
      reasoning = `High PV production (${pvPower}W). Charging at maximum power (3-phase, 32A) to maximize solar usage.`;
    } else if (pvPower > 2000) {
      // Moderate PV production - charge at moderate power
      decision = { mode: 'pv', max_current: 16, phases: 3 };
      reasoning = `Moderate PV production (${pvPower}W). Charging at moderate power (3-phase, 16A) to use available solar.`;
    } else if (pvPower > 1000) {
      // Low PV production - single phase charging
      decision = { mode: 'pv', max_current: 10, phases: 1 };
      reasoning = `Low PV production (${pvPower}W). Charging at low power (1-phase, 10A) to match solar output.`;
    } else {
      // Very low PV - use minpv mode to maintain minimum charging
      decision = { mode: 'minpv', phases: 1 };
      reasoning = `Very low PV production (${pvPower}W). Using min+PV mode to maintain slow charging with minimal grid usage.`;
    }

    return { decision, reasoning };
  }

  /**
   * Balance grid optimization
   * Help balance grid load and support grid stability
   */
  private balanceGrid(
    systemState: EVCCSystemState,
    loadpoint: EVCCLoadpoint,
    constraints?: any
  ): { decision: OptimizationDecision; reasoning: string } {
    const gridPower = systemState.result.gridPower;
    const pvPower = systemState.result.pvPower;
    const batteryPower = systemState.result.batteryPower;

    let decision: OptimizationDecision;
    let reasoning: string;

    // If exporting to grid (negative grid power), increase charging
    if (gridPower < -1000) {
      decision = { mode: 'pv', max_current: 32, phases: 3 };
      reasoning = `Exporting ${Math.abs(gridPower)}W to grid. Increasing charging to consume excess power locally.`;
    }
    // If importing heavily from grid, reduce charging
    else if (gridPower > 5000) {
      decision = { mode: 'pv', phases: 1 };
      reasoning = `High grid import (${gridPower}W). Reducing charging to PV-only mode to reduce grid stress.`;
    }
    // Moderate grid usage - balance with PV
    else if (gridPower > 2000) {
      decision = { mode: 'minpv', max_current: 10, phases: 1 };
      reasoning = `Moderate grid import (${gridPower}W). Using min+PV mode to balance grid load.`;
    }
    // Low grid usage - can charge more
    else {
      decision = { mode: 'minpv', max_current: 16, phases: 3 };
      reasoning = `Low grid import (${gridPower}W). Charging at moderate power to utilize available capacity.`;
    }

    return { decision, reasoning };
  }

  /**
   * Fast charge optimization
   * Charge as quickly as possible while respecting safety constraints
   */
  private fastCharge(
    systemState: EVCCSystemState,
    loadpoint: EVCCLoadpoint,
    constraints?: any
  ): { decision: OptimizationDecision; reasoning: string } {
    const maxPower = constraints?.max_power;
    const maxCurrent = maxPower ? Math.min(32, Math.floor(maxPower / (230 * 3))) : 32;

    let decision: OptimizationDecision;
    let reasoning: string;

    // Check if vehicle supports 3-phase charging
    const supports3Phase = loadpoint.phases >= 3;

    if (supports3Phase) {
      decision = { mode: 'now', max_current: maxCurrent, phases: 3 };
      reasoning = `Fast charging at maximum safe power (3-phase, ${maxCurrent}A = ${maxCurrent * 230 * 3}W). Vehicle supports 3-phase charging.`;
    } else {
      decision = { mode: 'now', max_current: maxCurrent, phases: 1 };
      reasoning = `Fast charging at maximum safe power (1-phase, ${maxCurrent}A = ${maxCurrent * 230}W). Vehicle limited to 1-phase charging.`;
    }

    if (constraints?.target_soc) {
      reasoning += ` Target SOC: ${constraints.target_soc}%.`;
    }

    if (constraints?.deadline) {
      reasoning += ` Deadline: ${constraints.deadline}.`;
    }

    return { decision, reasoning };
  }
}

export default ChargingOptimizer;
