import EVCCClient, { EVCCLoadpoint } from './evcc-client';
import logger from './logger';
import { saveLoadpointState } from './database';

const MAX_CURRENT_LIMIT_A = parseFloat(process.env.MAX_CURRENT_LIMIT_A || '32');
const MIN_CURRENT_LIMIT_A = parseFloat(process.env.MIN_CURRENT_LIMIT_A || '6');

export interface ControlLoadpointParams {
  loadpoint_id: number;
  mode?: 'off' | 'now' | 'minpv' | 'pv';
  min_current?: number;
  max_current?: number;
  limit_soc?: number;
  limit_energy?: number;
  phases?: 1 | 3;
}

export interface ControlLoadpointResult {
  success: boolean;
  loadpoint_id: number;
  changes: string[];
  current_state: Partial<EVCCLoadpoint>;
  reasoning: string;
}

/**
 * Loadpoint Controller
 * Manages individual EV charging points
 */
export class LoadpointController {
  private evccClient: EVCCClient;

  constructor(evccClient: EVCCClient) {
    this.evccClient = evccClient;
  }

  /**
   * Control a loadpoint with validation and safety checks
   */
  async controlLoadpoint(params: ControlLoadpointParams): Promise<ControlLoadpointResult> {
    const { loadpoint_id, mode, min_current, max_current, limit_soc, limit_energy, phases } = params;

    logger.info('Controlling loadpoint', { params });

    // Validate loadpoint exists
    const systemState = await this.evccClient.getSystemState();
    const loadpoint = systemState.result.loadpoints.find(lp => lp.id === loadpoint_id);

    if (!loadpoint) {
      throw new Error(`Loadpoint ${loadpoint_id} not found`);
    }

    const changes: string[] = [];
    let reasoning = '';

    // Validate and apply changes
    try {
      // Set mode
      if (mode !== undefined && mode !== loadpoint.mode) {
        await this.evccClient.setLoadpointMode(loadpoint_id, mode);
        changes.push(`mode: ${loadpoint.mode} → ${mode}`);
        reasoning += `Changed charging mode to ${mode}. `;
      }

      // Set minimum current
      if (min_current !== undefined) {
        this.validateCurrent(min_current, 'minimum');
        if (min_current !== loadpoint.minCurrent) {
          await this.evccClient.setLoadpointMinCurrent(loadpoint_id, min_current);
          changes.push(`min_current: ${loadpoint.minCurrent}A → ${min_current}A`);
          reasoning += `Set minimum current to ${min_current}A. `;
        }
      }

      // Set maximum current
      if (max_current !== undefined) {
        this.validateCurrent(max_current, 'maximum');
        if (max_current !== loadpoint.maxCurrent) {
          await this.evccClient.setLoadpointMaxCurrent(loadpoint_id, max_current);
          changes.push(`max_current: ${loadpoint.maxCurrent}A → ${max_current}A`);
          reasoning += `Set maximum current to ${max_current}A. `;
        }
      }

      // Set SOC limit
      if (limit_soc !== undefined) {
        this.validateSoc(limit_soc);
        if (limit_soc !== loadpoint.limitSoc) {
          await this.evccClient.setLoadpointLimitSoc(loadpoint_id, limit_soc);
          changes.push(`limit_soc: ${loadpoint.limitSoc}% → ${limit_soc}%`);
          reasoning += `Set SOC limit to ${limit_soc}%. `;
        }
      }

      // Set energy limit
      if (limit_energy !== undefined) {
        if (limit_energy < 0) {
          throw new Error('Energy limit must be non-negative');
        }
        if (limit_energy !== loadpoint.limitEnergy) {
          await this.evccClient.setLoadpointLimitEnergy(loadpoint_id, limit_energy);
          changes.push(`limit_energy: ${loadpoint.limitEnergy}kWh → ${limit_energy}kWh`);
          reasoning += `Set energy limit to ${limit_energy}kWh. `;
        }
      }

      // Set phases
      if (phases !== undefined) {
        if (phases !== 1 && phases !== 3) {
          throw new Error('Phases must be 1 or 3');
        }
        // Safety check: don't switch phases while charging
        if (loadpoint.charging) {
          throw new Error('Cannot switch phases while actively charging (safety constraint)');
        }
        if (phases !== loadpoint.phasesEnabled) {
          await this.evccClient.setLoadpointPhases(loadpoint_id, phases);
          changes.push(`phases: ${loadpoint.phasesEnabled}p → ${phases}p`);
          reasoning += `Switched to ${phases}-phase charging. `;
        }
      }

      // Get updated state
      const updatedSystemState = await this.evccClient.getSystemState();
      const updatedLoadpoint = updatedSystemState.result.loadpoints.find(lp => lp.id === loadpoint_id);

      if (!updatedLoadpoint) {
        throw new Error(`Failed to retrieve updated loadpoint state`);
      }

      // Save state to database
      await saveLoadpointState({
        loadpoint_id,
        mode: updatedLoadpoint.mode,
        enabled: updatedLoadpoint.enabled,
        charging: updatedLoadpoint.charging,
        current_power: updatedLoadpoint.chargePower,
        charged_energy: updatedLoadpoint.chargedEnergy,
        vehicle_soc: updatedLoadpoint.vehicleSoc || null,
        limit_soc: updatedLoadpoint.limitSoc || null,
        limit_energy: updatedLoadpoint.limitEnergy || null,
        phases: updatedLoadpoint.phasesEnabled,
      });

      if (changes.length === 0) {
        reasoning = 'No changes needed - loadpoint already in desired state.';
      }

      return {
        success: true,
        loadpoint_id,
        changes,
        current_state: updatedLoadpoint,
        reasoning: reasoning.trim(),
      };
    } catch (error) {
      logger.error('Failed to control loadpoint', { loadpoint_id, error });
      throw error;
    }
  }

  /**
   * Validate current value
   */
  private validateCurrent(current: number, type: 'minimum' | 'maximum'): void {
    if (current < MIN_CURRENT_LIMIT_A) {
      throw new Error(`${type} current ${current}A is below minimum safe limit ${MIN_CURRENT_LIMIT_A}A`);
    }
    if (current > MAX_CURRENT_LIMIT_A) {
      throw new Error(`${type} current ${current}A exceeds maximum limit ${MAX_CURRENT_LIMIT_A}A`);
    }
  }

  /**
   * Validate SOC value
   */
  private validateSoc(soc: number): void {
    if (soc < 0 || soc > 100) {
      throw new Error(`SOC ${soc}% must be between 0 and 100`);
    }
  }

  /**
   * Get loadpoint status
   */
  async getLoadpointStatus(loadpoint_id: number): Promise<EVCCLoadpoint> {
    const systemState = await this.evccClient.getSystemState();
    const loadpoint = systemState.result.loadpoints.find(lp => lp.id === loadpoint_id);

    if (!loadpoint) {
      throw new Error(`Loadpoint ${loadpoint_id} not found`);
    }

    return loadpoint;
  }

  /**
   * Get all loadpoints
   */
  async getAllLoadpoints(): Promise<EVCCLoadpoint[]> {
    const systemState = await this.evccClient.getSystemState();
    return systemState.result.loadpoints;
  }
}

export default LoadpointController;
