import axios, { AxiosInstance } from 'axios';
import logger from './logger';

const EVCC_URL = process.env.EVCC_URL || 'http://localhost:7070';
const EVCC_API_TIMEOUT = parseInt(process.env.EVCC_API_TIMEOUT || '30000', 10);

/**
 * EVCC System State Interface
 */
export interface EVCCSystemState {
  result: {
    auth: any;
    batteryConfigured: boolean;
    batteryDischargeControl: boolean;
    batteryMode: string;
    batteryPower: number;
    batterySoc: number;
    bufferSoc: number;
    bufferStartSoc: number;
    currency: string;
    gridConfigured: boolean;
    gridPower: number;
    homePower: number;
    loadpoints: EVCCLoadpoint[];
    prioritySoc: number;
    pvConfigured: boolean;
    pvPower: number;
    residualPower: number;
    siteTitle: string;
    smartCostLimit: number;
    tariffCo2: number;
    tariffGrid: number;
    tariffFeedIn: number;
    vehicles: EVCCVehicle[];
    version: string;
  };
}

export interface EVCCLoadpoint {
  id: number;
  mode: 'off' | 'now' | 'minpv' | 'pv';
  title: string;
  chargerFeatureHeating: boolean;
  chargerFeatureIntegratedDevice: boolean;
  chargerIcon: string;
  chargeCurrent: number;
  chargeCurrents: number[];
  chargeDuration: number;
  chargeEstimate: number;
  chargePower: number;
  chargeRemainingDuration: number;
  chargeRemainingEnergy: number;
  chargedEnergy: number;
  charging: boolean;
  connected: boolean;
  connectedDuration: number;
  enabled: boolean;
  hasVehicle: boolean;
  limitEnergy: number;
  limitSoc: number;
  maxCurrent: number;
  minCurrent: number;
  minSoc: number;
  phases: number;
  phasesActive: number;
  phasesEnabled: number;
  pvAction: string;
  pvRemaining: number;
  sessionCo2PerKWh: number;
  sessionEnergy: number;
  sessionPricePerKWh: number;
  sessionSolarPercentage: number;
  smartCostActive: boolean;
  smartCostLimit: number;
  smartCostType: string;
  targetSoc: number;
  targetTime: string;
  vehicleCapacity: number;
  vehicleDetectionActive: boolean;
  vehicleIcon: string;
  vehicleName: string;
  vehicleOdometer: number;
  vehiclePresent: boolean;
  vehicleRange: number;
  vehicleSoc: number;
  vehicleTitle: string;
}

export interface EVCCVehicle {
  name: string;
  title: string;
  icon: string;
  capacity: number;
  phases: number;
  soc: number;
  range: number;
  odometer: number;
}

/**
 * EVCC API Client
 * Wraps the EVCC REST API for TypeScript
 */
export class EVCCClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: EVCC_URL,
      timeout: EVCC_API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    logger.info('EVCC Client initialized', { url: EVCC_URL });
  }

  /**
   * Get complete system state
   */
  async getSystemState(): Promise<EVCCSystemState> {
    try {
      const response = await this.client.get<EVCCSystemState>('/api/state');
      return response.data;
    } catch (error) {
      logger.error('Failed to get system state', { error });
      throw new Error(`Failed to get EVCC system state: ${error}`);
    }
  }

  /**
   * Set loadpoint mode
   */
  async setLoadpointMode(loadpointId: number, mode: 'off' | 'now' | 'minpv' | 'pv'): Promise<void> {
    try {
      await this.client.post(`/api/loadpoints/${loadpointId}/mode/${mode}`);
      logger.info('Set loadpoint mode', { loadpointId, mode });
    } catch (error) {
      logger.error('Failed to set loadpoint mode', { loadpointId, mode, error });
      throw new Error(`Failed to set loadpoint mode: ${error}`);
    }
  }

  /**
   * Set loadpoint minimum current
   */
  async setLoadpointMinCurrent(loadpointId: number, current: number): Promise<void> {
    try {
      await this.client.post(`/api/loadpoints/${loadpointId}/mincurrent/${current}`);
      logger.info('Set loadpoint min current', { loadpointId, current });
    } catch (error) {
      logger.error('Failed to set loadpoint min current', { loadpointId, current, error });
      throw new Error(`Failed to set loadpoint min current: ${error}`);
    }
  }

  /**
   * Set loadpoint maximum current
   */
  async setLoadpointMaxCurrent(loadpointId: number, current: number): Promise<void> {
    try {
      await this.client.post(`/api/loadpoints/${loadpointId}/maxcurrent/${current}`);
      logger.info('Set loadpoint max current', { loadpointId, current });
    } catch (error) {
      logger.error('Failed to set loadpoint max current', { loadpointId, current, error });
      throw new Error(`Failed to set loadpoint max current: ${error}`);
    }
  }

  /**
   * Set loadpoint SOC limit
   */
  async setLoadpointLimitSoc(loadpointId: number, soc: number): Promise<void> {
    try {
      await this.client.post(`/api/loadpoints/${loadpointId}/limitsoc/${soc}`);
      logger.info('Set loadpoint limit SOC', { loadpointId, soc });
    } catch (error) {
      logger.error('Failed to set loadpoint limit SOC', { loadpointId, soc, error });
      throw new Error(`Failed to set loadpoint limit SOC: ${error}`);
    }
  }

  /**
   * Set loadpoint energy limit
   */
  async setLoadpointLimitEnergy(loadpointId: number, energy: number): Promise<void> {
    try {
      await this.client.post(`/api/loadpoints/${loadpointId}/limitenergy/${energy}`);
      logger.info('Set loadpoint limit energy', { loadpointId, energy });
    } catch (error) {
      logger.error('Failed to set loadpoint limit energy', { loadpointId, energy, error });
      throw new Error(`Failed to set loadpoint limit energy: ${error}`);
    }
  }

  /**
   * Set loadpoint phases
   */
  async setLoadpointPhases(loadpointId: number, phases: number): Promise<void> {
    try {
      await this.client.post(`/api/loadpoints/${loadpointId}/phases/${phases}`);
      logger.info('Set loadpoint phases', { loadpointId, phases });
    } catch (error) {
      logger.error('Failed to set loadpoint phases', { loadpointId, phases, error });
      throw new Error(`Failed to set loadpoint phases: ${error}`);
    }
  }

  /**
   * Set loadpoint target SOC
   */
  async setLoadpointTargetSoc(loadpointId: number, soc: number): Promise<void> {
    try {
      await this.client.post(`/api/loadpoints/${loadpointId}/target/soc/${soc}`);
      logger.info('Set loadpoint target SOC', { loadpointId, soc });
    } catch (error) {
      logger.error('Failed to set loadpoint target SOC', { loadpointId, soc, error });
      throw new Error(`Failed to set loadpoint target SOC: ${error}`);
    }
  }

  /**
   * Set loadpoint target time
   */
  async setLoadpointTargetTime(loadpointId: number, time: string): Promise<void> {
    try {
      await this.client.post(`/api/loadpoints/${loadpointId}/target/time/${time}`);
      logger.info('Set loadpoint target time', { loadpointId, time });
    } catch (error) {
      logger.error('Failed to set loadpoint target time', { loadpointId, time, error });
      throw new Error(`Failed to set loadpoint target time: ${error}`);
    }
  }

  /**
   * Set loadpoint target energy
   */
  async setLoadpointTargetEnergy(loadpointId: number, energy: number): Promise<void> {
    try {
      await this.client.post(`/api/loadpoints/${loadpointId}/target/energy/${energy}`);
      logger.info('Set loadpoint target energy', { loadpointId, energy });
    } catch (error) {
      logger.error('Failed to set loadpoint target energy', { loadpointId, energy, error });
      throw new Error(`Failed to set loadpoint target energy: ${error}`);
    }
  }

  /**
   * Set battery buffer SOC
   */
  async setBufferSoc(soc: number): Promise<void> {
    try {
      await this.client.post(`/api/buffersoc/${soc}`);
      logger.info('Set buffer SOC', { soc });
    } catch (error) {
      logger.error('Failed to set buffer SOC', { soc, error });
      throw new Error(`Failed to set buffer SOC: ${error}`);
    }
  }

  /**
   * Set battery buffer start SOC
   */
  async setBufferStartSoc(soc: number): Promise<void> {
    try {
      await this.client.post(`/api/bufferstartsoc/${soc}`);
      logger.info('Set buffer start SOC', { soc });
    } catch (error) {
      logger.error('Failed to set buffer start SOC', { soc, error });
      throw new Error(`Failed to set buffer start SOC: ${error}`);
    }
  }

  /**
   * Set battery discharge control
   */
  async setBatteryDischargeControl(enabled: boolean): Promise<void> {
    try {
      await this.client.post(`/api/batterydischargecontrol/${enabled}`);
      logger.info('Set battery discharge control', { enabled });
    } catch (error) {
      logger.error('Failed to set battery discharge control', { enabled, error });
      throw new Error(`Failed to set battery discharge control: ${error}`);
    }
  }

  /**
   * Set battery grid charge limit
   */
  async setBatteryGridChargeLimit(limit: number): Promise<void> {
    try {
      await this.client.post(`/api/batterygridchargelimit/${limit}`);
      logger.info('Set battery grid charge limit', { limit });
    } catch (error) {
      logger.error('Failed to set battery grid charge limit', { limit, error });
      throw new Error(`Failed to set battery grid charge limit: ${error}`);
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<boolean> {
    try {
      await this.client.get('/health');
      return true;
    } catch (error) {
      logger.error('EVCC health check failed', { error });
      return false;
    }
  }
}

export default EVCCClient;

