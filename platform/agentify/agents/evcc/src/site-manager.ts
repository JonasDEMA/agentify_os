import EVCCClient from './evcc-client';
import logger from './logger';
import { saveSystemState } from './database';

export interface ManageBatteryParams {
  buffer_soc?: number;
  buffer_start_soc?: number;
  discharge_control?: boolean;
  grid_charge_limit?: number;
}

export interface ManageBatteryResult {
  success: boolean;
  changes: string[];
  current_state: {
    buffer_soc: number;
    buffer_start_soc: number;
    discharge_control: boolean;
    battery_soc: number;
    battery_power: number;
  };
  reasoning: string;
}

export interface SiteStatus {
  grid_power: number;
  pv_power: number;
  battery_power: number;
  battery_soc: number;
  home_power: number;
  residual_power: number;
  battery_configured: boolean;
  pv_configured: boolean;
  grid_configured: boolean;
}

/**
 * Site Manager
 * Manages overall energy system (grid, PV, battery)
 */
export class SiteManager {
  private evccClient: EVCCClient;

  constructor(evccClient: EVCCClient) {
    this.evccClient = evccClient;
  }

  /**
   * Manage battery settings
   */
  async manageBattery(params: ManageBatteryParams): Promise<ManageBatteryResult> {
    const { buffer_soc, buffer_start_soc, discharge_control, grid_charge_limit } = params;

    logger.info('Managing battery', { params });

    const systemState = await this.evccClient.getSystemState();
    const currentState = systemState.result;

    if (!currentState.batteryConfigured) {
      throw new Error('Battery not configured in EVCC system');
    }

    const changes: string[] = [];
    let reasoning = '';

    try {
      // Set buffer SOC
      if (buffer_soc !== undefined) {
        this.validateSoc(buffer_soc);
        if (buffer_soc !== currentState.bufferSoc) {
          await this.evccClient.setBufferSoc(buffer_soc);
          changes.push(`buffer_soc: ${currentState.bufferSoc}% → ${buffer_soc}%`);
          reasoning += `Set battery buffer SOC to ${buffer_soc}% to maintain home energy security. `;
        }
      }

      // Set buffer start SOC
      if (buffer_start_soc !== undefined) {
        this.validateSoc(buffer_start_soc);
        if (buffer_start_soc !== currentState.bufferStartSoc) {
          await this.evccClient.setBufferStartSoc(buffer_start_soc);
          changes.push(`buffer_start_soc: ${currentState.bufferStartSoc}% → ${buffer_start_soc}%`);
          reasoning += `Set battery buffer start SOC to ${buffer_start_soc}%. `;
        }
      }

      // Set discharge control
      if (discharge_control !== undefined) {
        if (discharge_control !== currentState.batteryDischargeControl) {
          await this.evccClient.setBatteryDischargeControl(discharge_control);
          changes.push(`discharge_control: ${currentState.batteryDischargeControl} → ${discharge_control}`);
          reasoning += `${discharge_control ? 'Enabled' : 'Disabled'} battery discharge control. `;
        }
      }

      // Set grid charge limit
      if (grid_charge_limit !== undefined) {
        if (grid_charge_limit < 0) {
          throw new Error('Grid charge limit must be non-negative');
        }
        await this.evccClient.setBatteryGridChargeLimit(grid_charge_limit);
        changes.push(`grid_charge_limit: ${grid_charge_limit}W`);
        reasoning += `Set battery grid charge limit to ${grid_charge_limit}W. `;
      }

      // Get updated state
      const updatedSystemState = await this.evccClient.getSystemState();
      const updatedState = updatedSystemState.result;

      // Save system state to database
      await saveSystemState({
        grid_power: updatedState.gridPower,
        pv_power: updatedState.pvPower,
        battery_power: updatedState.batteryPower,
        battery_soc: updatedState.batterySoc || null,
        home_power: updatedState.homePower,
        loadpoint_states: updatedState.loadpoints,
      });

      if (changes.length === 0) {
        reasoning = 'No changes needed - battery already in desired state.';
      }

      return {
        success: true,
        changes,
        current_state: {
          buffer_soc: updatedState.bufferSoc,
          buffer_start_soc: updatedState.bufferStartSoc,
          discharge_control: updatedState.batteryDischargeControl,
          battery_soc: updatedState.batterySoc,
          battery_power: updatedState.batteryPower,
        },
        reasoning: reasoning.trim(),
      };
    } catch (error) {
      logger.error('Failed to manage battery', { error });
      throw error;
    }
  }

  /**
   * Get site status
   */
  async getSiteStatus(): Promise<SiteStatus> {
    const systemState = await this.evccClient.getSystemState();
    const state = systemState.result;

    return {
      grid_power: state.gridPower,
      pv_power: state.pvPower,
      battery_power: state.batteryPower,
      battery_soc: state.batterySoc,
      home_power: state.homePower,
      residual_power: state.residualPower,
      battery_configured: state.batteryConfigured,
      pv_configured: state.pvConfigured,
      grid_configured: state.gridConfigured,
    };
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

export default SiteManager;

