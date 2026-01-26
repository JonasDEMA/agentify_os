import { logger } from './logger';
import { EnergyApiClient } from './energy-api-client';
import { database } from './database';
import { ManageFCRRequest, FCRModule, FCRModuleInit, FCRDynamicInput } from './types';

export class FCRManager {
  private energyApi: EnergyApiClient;
  private agentId: string;

  constructor(energyApi: EnergyApiClient) {
    this.energyApi = energyApi;
    this.agentId = process.env.AGENT_ID || 'agent.energy.controller';
  }

  async manageFCR(request: ManageFCRRequest): Promise<any> {
    logger.info('Manage FCR request', { request });

    const { action, module_id } = request;

    try {
      switch (action) {
        case 'register':
          return await this.registerModule(module_id);
        
        case 'unregister':
          return await this.unregisterModule(module_id);
        
        case 'initialize':
          if (request.power_limit === undefined) {
            throw new Error('power_limit is required for initialize action');
          }
          return await this.initializeModule(module_id, request.power_limit);
        
        case 'get_status':
          return await this.getModuleStatus(module_id);
        
        case 'set_output':
          if (request.power === undefined) {
            throw new Error('power is required for set_output action');
          }
          return await this.setOutput(module_id, request.power);
        
        default:
          throw new Error(`Unknown FCR action: ${action}`);
      }
    } catch (error) {
      logger.error('Failed to manage FCR', { error, request });
      throw error;
    }
  }

  private async registerModule(moduleId: string): Promise<any> {
    logger.info('Registering FCR module', { moduleId });

    // Register with Energy API
    const module = await this.energyApi.registerFCRModule(moduleId);

    // Store in database
    await database.createFCRProcess({
      module_id: moduleId,
      loadpoint_id: module.loadpoint_id,
      power_limit: module.power_limit,
      initialized: false,
      status: 'registered'
    });

    logger.info('FCR module registered', { module });
    return {
      success: true,
      module_id: moduleId,
      status: {
        loadpoint_id: module.loadpoint_id,
        power_limit: module.power_limit,
        registered: true
      }
    };
  }

  private async unregisterModule(moduleId: string): Promise<any> {
    logger.info('Unregistering FCR module', { moduleId });

    // Unregister from Energy API
    await this.energyApi.unregisterFCRModule(moduleId);

    // Delete from database
    await database.deleteFCRProcess(moduleId);

    logger.info('FCR module unregistered', { moduleId });
    return {
      success: true,
      module_id: moduleId,
      status: {
        registered: false
      }
    };
  }

  private async initializeModule(moduleId: string, powerLimit: number): Promise<any> {
    logger.info('Initializing FCR module', { moduleId, powerLimit });

    // Update database status
    await database.updateFCRProcess(moduleId, {
      status: 'initializing'
    });

    // Initialize with Energy API
    const initState = await this.energyApi.initializeFCRModule(moduleId, powerLimit);

    // Update database with results
    await database.updateFCRProcess(moduleId, {
      power_limit: initState.power_limit,
      vehicle_min_power: initState.vehicle_min_power,
      vehicle_max_power: initState.vehicle_max_power,
      initialized: initState.ready,
      status: initState.ready ? 'ready' : 'initializing'
    });

    logger.info('FCR module initialization complete', { moduleId, initState });
    return {
      success: true,
      module_id: moduleId,
      status: {
        initializing: initState.initializing,
        ready: initState.ready,
        vehicle_min_power: initState.vehicle_min_power,
        vehicle_max_power: initState.vehicle_max_power,
        power_limit: initState.power_limit
      }
    };
  }

  private async getModuleStatus(moduleId: string): Promise<any> {
    logger.info('Getting FCR module status', { moduleId });

    // Get from Energy API
    const module = await this.energyApi.getFCRModule(moduleId);
    const initState = await this.energyApi.getFCRModuleInitState(moduleId);
    const dynamicInput = await this.energyApi.getFCRDynamicInput(moduleId);

    // Get from database
    const dbProcess = await database.getFCRProcess(moduleId);

    return {
      success: true,
      module_id: moduleId,
      status: {
        loadpoint_id: module.loadpoint_id,
        power_limit: module.power_limit,
        initialized: initState.ready,
        vehicle_min_power: initState.vehicle_min_power,
        vehicle_max_power: initState.vehicle_max_power,
        current_state: {
          charging: dynamicInput.charging,
          desired_power: dynamicInput.desired_power,
          actual_power: dynamicInput.actual_power,
          grid_frequency: dynamicInput.grid_frequency,
          soc: dynamicInput.soc
        },
        db_status: dbProcess?.status
      }
    };
  }

  private async setOutput(moduleId: string, power: number): Promise<any> {
    logger.info('Setting FCR output', { moduleId, power });

    // Set output via Energy API
    const actualPower = await this.energyApi.setFCROutput(moduleId, power);

    // Update database status
    await database.updateFCRProcess(moduleId, {
      status: 'active'
    });

    logger.info('FCR output set', { moduleId, power, actualPower });
    return {
      success: true,
      module_id: moduleId,
      status: {
        requested_power: power,
        actual_power: actualPower
      }
    };
  }
}

