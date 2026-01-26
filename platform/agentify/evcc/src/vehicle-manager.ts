import EVCCClient, { EVCCLoadpoint } from './evcc-client';
import logger from './logger';

export interface SetChargingPlanParams {
  loadpoint_id: number;
  target_time: string;
  target_soc?: number;
  target_energy?: number;
}

export interface SetChargingPlanResult {
  success: boolean;
  loadpoint_id: number;
  plan: {
    target_time: string;
    target_soc?: number;
    target_energy?: number;
    estimated_duration: number;
    estimated_cost?: number;
  };
  reasoning: string;
}

/**
 * Vehicle Manager
 * Manages EV charging plans and vehicle-specific settings
 */
export class VehicleManager {
  private evccClient: EVCCClient;

  constructor(evccClient: EVCCClient) {
    this.evccClient = evccClient;
  }

  /**
   * Set charging plan for a loadpoint
   */
  async setChargingPlan(params: SetChargingPlanParams): Promise<SetChargingPlanResult> {
    const { loadpoint_id, target_time, target_soc, target_energy } = params;

    logger.info('Setting charging plan', { params });

    // Validate loadpoint exists
    const systemState = await this.evccClient.getSystemState();
    const loadpoint = systemState.result.loadpoints.find(lp => lp.id === loadpoint_id);

    if (!loadpoint) {
      throw new Error(`Loadpoint ${loadpoint_id} not found`);
    }

    if (!loadpoint.connected) {
      throw new Error(`No vehicle connected to loadpoint ${loadpoint_id}`);
    }

    // Validate target time
    const targetDate = new Date(target_time);
    if (isNaN(targetDate.getTime())) {
      throw new Error(`Invalid target time: ${target_time}`);
    }

    if (targetDate <= new Date()) {
      throw new Error('Target time must be in the future');
    }

    // Validate target SOC or energy
    if (target_soc === undefined && target_energy === undefined) {
      throw new Error('Either target_soc or target_energy must be specified');
    }

    if (target_soc !== undefined && target_energy !== undefined) {
      throw new Error('Cannot specify both target_soc and target_energy');
    }

    try {
      let reasoning = '';

      // Set target time
      await this.evccClient.setLoadpointTargetTime(loadpoint_id, target_time);
      reasoning += `Set target time to ${target_time}. `;

      // Set target SOC or energy
      if (target_soc !== undefined) {
        this.validateSoc(target_soc);
        await this.evccClient.setLoadpointTargetSoc(loadpoint_id, target_soc);
        reasoning += `Set target SOC to ${target_soc}%. `;
      }

      if (target_energy !== undefined) {
        if (target_energy <= 0) {
          throw new Error('Target energy must be positive');
        }
        await this.evccClient.setLoadpointTargetEnergy(loadpoint_id, target_energy);
        reasoning += `Set target energy to ${target_energy}kWh. `;
      }

      // Get updated loadpoint state
      const updatedSystemState = await this.evccClient.getSystemState();
      const updatedLoadpoint = updatedSystemState.result.loadpoints.find(lp => lp.id === loadpoint_id);

      if (!updatedLoadpoint) {
        throw new Error('Failed to retrieve updated loadpoint state');
      }

      // Calculate estimated duration
      const estimatedDuration = this.calculateEstimatedDuration(updatedLoadpoint, target_soc, target_energy);

      reasoning += `EVCC will optimize charging to reach the target by ${target_time}.`;

      return {
        success: true,
        loadpoint_id,
        plan: {
          target_time,
          target_soc,
          target_energy,
          estimated_duration: estimatedDuration,
        },
        reasoning: reasoning.trim(),
      };
    } catch (error) {
      logger.error('Failed to set charging plan', { loadpoint_id, error });
      throw error;
    }
  }

  /**
   * Calculate estimated charging duration
   */
  private calculateEstimatedDuration(
    loadpoint: EVCCLoadpoint,
    target_soc?: number,
    target_energy?: number
  ): number {
    // If target SOC is specified
    if (target_soc !== undefined && loadpoint.vehicleSoc !== null) {
      const socDifference = target_soc - loadpoint.vehicleSoc;
      if (socDifference <= 0) {
        return 0; // Already at or above target
      }

      const energyNeeded = (socDifference / 100) * loadpoint.vehicleCapacity;
      const chargePower = loadpoint.chargePower || (loadpoint.maxCurrent * 230 * loadpoint.phasesEnabled);
      return (energyNeeded / (chargePower / 1000)) * 3600; // seconds
    }

    // If target energy is specified
    if (target_energy !== undefined) {
      const energyNeeded = target_energy - (loadpoint.chargedEnergy / 1000);
      if (energyNeeded <= 0) {
        return 0; // Already charged enough
      }

      const chargePower = loadpoint.chargePower || (loadpoint.maxCurrent * 230 * loadpoint.phasesEnabled);
      return (energyNeeded / (chargePower / 1000)) * 3600; // seconds
    }

    return 0;
  }

  /**
   * Validate SOC value
   */
  private validateSoc(soc: number): void {
    if (soc < 0 || soc > 100) {
      throw new Error(`SOC ${soc}% must be between 0 and 100`);
    }
  }
}

export default VehicleManager;

