// Agent Communication Protocol Types
export type AgentMessageType = 
  | 'REQUEST' | 'INFORM' | 'DISCOVER' | 'PROPOSE' 
  | 'AGREE' | 'REFUSE' | 'CONFIRM' | 'FAILURE' | 'DONE' | 'OFFER' | 'ASSIGN';

export interface AgentMessage {
  type: AgentMessageType;
  sender: string;
  receiver: string;
  content: any;
  conversation_id?: string;
  timestamp?: string;
  metadata?: Record<string, any>;
}

// Energy API Response Types
export interface EnergyApiResponse<T = any> {
  status_code: number;
  status_msg: string;
  result: T;
}

// Loadpoint Types
export enum ChargingMode {
  OFF = 'off',
  NOW = 'now',
  PV = 'pv',
  MINPV = 'minpv'
}

export enum LoadpointPhases {
  NOT_CONNECTED = 0,
  ONE_PHASE = 1,
  THREE_PHASE = 3
}

export interface Loadpoint {
  id: number;
  name: string;
  max_power: number;
  min_power: number;
  max_power_vehicle?: number;
  min_power_vehicle?: number;
  actual_power: number;
  desired_power: number;
  target_power?: number;
  active_phases: LoadpointPhases;
  charging: boolean;
  connected: boolean;
  mode: ChargingMode;
}

export interface LoadpointState {
  connected: boolean;
  charging: boolean;
  mode: string;
}

export interface Power {
  power_W: number;
}

// Meter Types
export interface Meter {
  id: number;
  type: string;
  name: string;
  certified: boolean;
}

export interface Frequency {
  frequency_Hz: number;
}

export interface Voltage {
  voltage_V: number;
}

export interface Energy {
  energy_kWh: number;
}

// Grid Types
export interface GridMetrics {
  frequency_Hz: number;
  timestamp: string;
}

// FCR Types
export interface FCRModule {
  module_id: string;
  loadpoint_id?: number;
  power_limit: number;
  initialized?: boolean;
}

export interface FCRModuleInit {
  initializing: boolean;
  ready: boolean;
  vehicle_min_power: number;
  vehicle_max_power: number;
  power_limit: number;
}

export interface FCRStaticInput {
  loadpoint_max_power: number;
  loadpoint_min_power: number;
}

export interface FCRDynamicInput {
  charging: boolean;
  desired_power: number;
  actual_power: number;
  grid_frequency: number;
  soc?: number;
  soc_limit?: number;
}

// Tool Request Types
export interface ControlEVChargingRequest {
  loadpoint_id: number;
  mode?: ChargingMode;
  max_power?: number;
  min_power?: number;
  enable_tracking?: boolean;
}

export interface MonitorEnergyRequest {
  source: 'loadpoint' | 'meter' | 'grid';
  source_id?: number;
}

export interface ManageFCRRequest {
  action: 'register' | 'unregister' | 'initialize' | 'get_status' | 'set_output';
  module_id: string;
  power_limit?: number;
  power?: number;
}

export interface OptimizePowerRequest {
  loadpoint_id: number;
  objective: 'minimize_cost' | 'maximize_renewable' | 'balance_grid' | 'fast_charge';
  constraints?: Record<string, any>;
}

// Database Types
export interface EnergyMetrics {
  id?: string;
  customer_id: string;
  agent_id: string;
  loadpoint_id?: number;
  meter_id?: number;
  actual_power?: number;
  desired_power?: number;
  grid_frequency?: number;
  voltage?: number;
  energy_kwh?: number;
  charging_mode?: string;
  timestamp: string;
  created_at?: string;
}

export interface FCRProcess {
  id?: string;
  customer_id: string;
  module_id: string;
  loadpoint_id?: number;
  power_limit: number;
  initialized: boolean;
  vehicle_min_power?: number;
  vehicle_max_power?: number;
  status: 'registered' | 'initializing' | 'ready' | 'active' | 'stopped';
  created_at?: string;
  updated_at?: string;
}

