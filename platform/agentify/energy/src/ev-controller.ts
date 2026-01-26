import { logger } from './logger';
import { EnergyApiClient } from './energy-api-client';
import { database } from './database';
import {
  ControlEVChargingRequest,
  MonitorEnergyRequest,
  ChargingMode,
  Loadpoint
} from './types';

export class EVController {
  private energyApi: EnergyApiClient;
  private agentId: string;
  private maxPowerLimit: number;
  private minPowerLimit: number;

  constructor(energyApi: EnergyApiClient) {
    this.energyApi = energyApi;
    this.agentId = process.env.AGENT_ID || 'agent.energy.controller';
    this.maxPowerLimit = parseInt(process.env.MAX_POWER_LIMIT_W || '22080');
    this.minPowerLimit = parseInt(process.env.MIN_POWER_LIMIT_W || '1380');
  }

  async controlEVCharging(request: ControlEVChargingRequest): Promise<any> {
    logger.info('Control EV charging request', { request });

    // Validate request
    this.validateChargingRequest(request);

    const loadpointId = request.loadpoint_id;
    const result: any = {
      success: true,
      loadpoint_id: loadpointId
    };

    try {
      // Get current state
      const currentState = await this.energyApi.getLoadpoint(loadpointId);
      logger.debug('Current loadpoint state', { currentState });

      // Set charging mode if provided
      if (request.mode) {
        await this.energyApi.setChargingMode(loadpointId, request.mode);
        result.mode = request.mode;
      }

      // Set max power if provided
      if (request.max_power !== undefined) {
        const actualPower = await this.energyApi.setMaxPower(loadpointId, request.max_power);
        result.max_power = actualPower;
      }

      // Set min power if provided
      if (request.min_power !== undefined) {
        const actualPower = await this.energyApi.setMinPower(loadpointId, request.min_power);
        result.min_power = actualPower;
      }

      // Enable/disable power tracking if specified
      if (request.enable_tracking === true) {
        await this.energyApi.enablePowerTracking(loadpointId);
        result.power_tracking = true;
      } else if (request.enable_tracking === false) {
        await this.energyApi.disablePowerTracking(loadpointId);
        result.power_tracking = false;
      }

      // Get updated state
      const updatedState = await this.energyApi.getLoadpoint(loadpointId);

      // Store metrics in database
      await database.createEnergyMetrics({
        agent_id: this.agentId,
        loadpoint_id: loadpointId,
        actual_power: updatedState.actual_power,
        desired_power: updatedState.desired_power,
        charging_mode: updatedState.mode,
        timestamp: new Date().toISOString()
      });

      logger.info('EV charging control successful', { result });
      return result;

    } catch (error) {
      logger.error('Failed to control EV charging', { error, request });
      throw error;
    }
  }

  async monitorEnergy(request: MonitorEnergyRequest): Promise<any> {
    logger.info('Monitor energy request', { request });

    try {
      const result: any = {
        source: request.source,
        timestamp: new Date().toISOString()
      };

      if (request.source === 'loadpoint') {
        if (!request.source_id) {
          throw new Error('source_id is required for loadpoint monitoring');
        }
        const loadpoint = await this.energyApi.getLoadpoint(request.source_id);
        result.metrics = {
          id: loadpoint.id,
          name: loadpoint.name,
          actual_power: loadpoint.actual_power,
          desired_power: loadpoint.desired_power,
          max_power: loadpoint.max_power,
          min_power: loadpoint.min_power,
          charging: loadpoint.charging,
          connected: loadpoint.connected,
          mode: loadpoint.mode,
          active_phases: loadpoint.active_phases
        };

        // Store metrics
        await database.createEnergyMetrics({
          agent_id: this.agentId,
          loadpoint_id: loadpoint.id,
          actual_power: loadpoint.actual_power,
          desired_power: loadpoint.desired_power,
          charging_mode: loadpoint.mode,
          timestamp: result.timestamp
        });

      } else if (request.source === 'meter') {
        if (!request.source_id) {
          throw new Error('source_id is required for meter monitoring');
        }
        const meter = await this.energyApi.getMeter(request.source_id);
        const frequency = await this.energyApi.getMeterFrequency(request.source_id);
        const voltage = await this.energyApi.getMeterVoltage(request.source_id);
        const energy = await this.energyApi.getMeterEnergy(request.source_id);

        result.metrics = {
          id: meter.id,
          name: meter.name,
          type: meter.type,
          frequency_Hz: frequency,
          voltage_V: voltage,
          energy_kWh: energy
        };

        // Store metrics
        await database.createEnergyMetrics({
          agent_id: this.agentId,
          meter_id: meter.id,
          grid_frequency: frequency,
          voltage: voltage,
          energy_kwh: energy,
          timestamp: result.timestamp
        });

      } else if (request.source === 'grid') {
        const frequency = await this.energyApi.getGridFrequency();
        result.metrics = {
          frequency_Hz: frequency
        };

        // Store metrics
        await database.createEnergyMetrics({
          agent_id: this.agentId,
          grid_frequency: frequency,
          timestamp: result.timestamp
        });
      }

      logger.info('Energy monitoring successful', { result });
      return result;

    } catch (error) {
      logger.error('Failed to monitor energy', { error, request });
      throw error;
    }
  }

  private validateChargingRequest(request: ControlEVChargingRequest): void {
    // Validate power limits
    if (request.max_power !== undefined) {
      if (request.max_power > this.maxPowerLimit) {
        throw new Error(`Max power ${request.max_power}W exceeds safety limit ${this.maxPowerLimit}W`);
      }
      if (request.max_power < this.minPowerLimit) {
        throw new Error(`Max power ${request.max_power}W below minimum ${this.minPowerLimit}W`);
      }
    }

    if (request.min_power !== undefined) {
      if (request.min_power > this.maxPowerLimit) {
        throw new Error(`Min power ${request.min_power}W exceeds safety limit ${this.maxPowerLimit}W`);
      }
      if (request.min_power < this.minPowerLimit) {
        throw new Error(`Min power ${request.min_power}W below minimum ${this.minPowerLimit}W`);
      }
    }

    // Validate mode
    if (request.mode && !Object.values(ChargingMode).includes(request.mode)) {
      throw new Error(`Invalid charging mode: ${request.mode}`);
    }
  }
}

