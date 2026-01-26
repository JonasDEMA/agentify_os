import axios, { AxiosInstance } from 'axios';
import { logger } from './logger';
import {
  EnergyApiResponse,
  Loadpoint,
  LoadpointState,
  Power,
  Meter,
  Frequency,
  Voltage,
  Energy,
  FCRModule,
  FCRModuleInit,
  FCRStaticInput,
  FCRDynamicInput,
  ChargingMode
} from './types';

export class EnergyApiClient {
  private client: AxiosInstance;
  private baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || process.env.ENERGY_API_BASE_URL || 'http://localhost:8000/energy-api/v1';
    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    logger.info(`Energy API Client initialized with base URL: ${this.baseUrl}`);
  }

  // Loadpoint Methods
  async getLoadpoints(): Promise<Loadpoint[]> {
    const response = await this.client.get<EnergyApiResponse<Loadpoint[]>>('/devices/loadpoints');
    this.checkResponse(response.data);
    return response.data.result;
  }

  async getLoadpoint(id: number): Promise<Loadpoint> {
    const response = await this.client.get<EnergyApiResponse<Loadpoint>>(`/devices/loadpoints/${id}`);
    this.checkResponse(response.data);
    return response.data.result;
  }

  async getLoadpointState(id: number): Promise<LoadpointState> {
    const response = await this.client.get<EnergyApiResponse<LoadpointState>>(`/devices/loadpoints/${id}/state`);
    this.checkResponse(response.data);
    return response.data.result;
  }

  async getLoadpointActualPower(id: number): Promise<number> {
    const response = await this.client.get<EnergyApiResponse<Power>>(`/devices/loadpoints/${id}/actual_power`);
    this.checkResponse(response.data);
    return response.data.result.power_W;
  }

  async getLoadpointMaxPower(id: number): Promise<number> {
    const response = await this.client.get<EnergyApiResponse<Power>>(`/devices/loadpoints/${id}/max_power`);
    this.checkResponse(response.data);
    return response.data.result.power_W;
  }

  async setChargingMode(id: number, mode: ChargingMode): Promise<void> {
    const response = await this.client.post<EnergyApiResponse>(`/devices/loadpoints/${id}/mode/${mode}`);
    this.checkResponse(response.data);
    logger.info(`Set charging mode to ${mode} for loadpoint ${id}`);
  }

  async setMaxPower(id: number, power: number): Promise<number> {
    const response = await this.client.post<EnergyApiResponse<Power>>(`/devices/loadpoints/${id}/max_power/${power}`);
    this.checkResponse(response.data);
    logger.info(`Set max power to ${power}W for loadpoint ${id}`);
    return response.data.result.power_W;
  }

  async setMinPower(id: number, power: number): Promise<number> {
    const response = await this.client.post<EnergyApiResponse<Power>>(`/devices/loadpoints/${id}/min_power/${power}`);
    this.checkResponse(response.data);
    logger.info(`Set min power to ${power}W for loadpoint ${id}`);
    return response.data.result.power_W;
  }

  async enablePowerTracking(id: number): Promise<void> {
    const response = await this.client.post<EnergyApiResponse>(`/devices/loadpoints/${id}/enable_power_tracking`);
    this.checkResponse(response.data);
    logger.info(`Enabled power tracking for loadpoint ${id}`);
  }

  async disablePowerTracking(id: number): Promise<void> {
    const response = await this.client.post<EnergyApiResponse>(`/devices/loadpoints/${id}/disable_power_tracking`);
    this.checkResponse(response.data);
    logger.info(`Disabled power tracking for loadpoint ${id}`);
  }

  // Meter Methods
  async getMeters(): Promise<Meter[]> {
    const response = await this.client.get<EnergyApiResponse<Meter[]>>('/devices/meters');
    this.checkResponse(response.data);
    return response.data.result;
  }

  async getMeter(id: number): Promise<Meter> {
    const response = await this.client.get<EnergyApiResponse<Meter>>(`/devices/meters/${id}`);
    this.checkResponse(response.data);
    return response.data.result;
  }

  async getMeterFrequency(id: number): Promise<number> {
    const response = await this.client.get<EnergyApiResponse<Frequency>>(`/devices/meters/${id}/frequency`);
    this.checkResponse(response.data);
    return response.data.result.frequency_Hz;
  }

  async getMeterVoltage(id: number): Promise<number> {
    const response = await this.client.get<EnergyApiResponse<Voltage>>(`/devices/meters/${id}/voltage`);
    this.checkResponse(response.data);
    return response.data.result.voltage_V;
  }

  async getMeterEnergy(id: number): Promise<number> {
    const response = await this.client.get<EnergyApiResponse<Energy>>(`/devices/meters/${id}/energy`);
    this.checkResponse(response.data);
    return response.data.result.energy_kWh;
  }

  // Grid Methods
  async getGridFrequency(): Promise<number> {
    const response = await this.client.get<EnergyApiResponse<Frequency>>('/systems/grid/frequency');
    this.checkResponse(response.data);
    return response.data.result.frequency_Hz;
  }

  async setCustomGridFrequency(frequency: number): Promise<number> {
    const response = await this.client.post<EnergyApiResponse<Frequency>>(`/systems/grid/frequency/${frequency}`);
    this.checkResponse(response.data);
    return response.data.result.frequency_Hz;
  }

  // FCR Methods
  async getFCRModules(): Promise<FCRModule[]> {
    const response = await this.client.get<EnergyApiResponse<FCRModule[]>>('/applications/fcr/modules');
    this.checkResponse(response.data);
    return response.data.result;
  }

  async getFCRModule(moduleId: string): Promise<FCRModule> {
    const response = await this.client.get<EnergyApiResponse<FCRModule>>(`/applications/fcr/modules/${moduleId}`);
    this.checkResponse(response.data);
    return response.data.result;
  }

  async registerFCRModule(moduleId: string): Promise<FCRModule> {
    const response = await this.client.post<EnergyApiResponse<FCRModule>>(`/applications/fcr/modules/${moduleId}`);
    this.checkResponse(response.data);
    logger.info(`Registered FCR module: ${moduleId}`);
    return response.data.result;
  }

  async unregisterFCRModule(moduleId: string): Promise<void> {
    const response = await this.client.delete<EnergyApiResponse>(`/applications/fcr/modules/${moduleId}`);
    this.checkResponse(response.data);
    logger.info(`Unregistered FCR module: ${moduleId}`);
  }

  async initializeFCRModule(moduleId: string, powerLimit: number): Promise<FCRModuleInit> {
    const response = await this.client.post<EnergyApiResponse<FCRModuleInit>>(`/applications/fcr/modules/${moduleId}/init/${powerLimit}`);
    this.checkResponse(response.data);
    logger.info(`Initialized FCR module ${moduleId} with power limit ${powerLimit}%`);
    return response.data.result;
  }

  async getFCRModuleInitState(moduleId: string): Promise<FCRModuleInit> {
    const response = await this.client.get<EnergyApiResponse<FCRModuleInit>>(`/applications/fcr/modules/${moduleId}/init`);
    this.checkResponse(response.data);
    return response.data.result;
  }

  async getFCRStaticInput(moduleId: string): Promise<FCRStaticInput> {
    const response = await this.client.get<EnergyApiResponse<FCRStaticInput>>(`/applications/fcr/modules/${moduleId}/static_input`);
    this.checkResponse(response.data);
    return response.data.result;
  }

  async getFCRDynamicInput(moduleId: string): Promise<FCRDynamicInput> {
    const response = await this.client.get<EnergyApiResponse<FCRDynamicInput>>(`/applications/fcr/modules/${moduleId}/dynamic_input`);
    this.checkResponse(response.data);
    return response.data.result;
  }

  async setFCROutput(moduleId: string, power: number): Promise<number> {
    const response = await this.client.post<EnergyApiResponse<Power>>(`/applications/fcr/modules/${moduleId}/output/${power}`);
    this.checkResponse(response.data);
    return response.data.result.power_W;
  }

  // Helper method to check response status
  private checkResponse(response: EnergyApiResponse): void {
    if (response.status_code !== 0) {
      throw new Error(`Energy API error: ${response.status_msg} (code: ${response.status_code})`);
    }
  }
}

