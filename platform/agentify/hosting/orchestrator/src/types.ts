/**
 * Type definitions for Hosting Orchestrator
 */

export interface DeploymentConfig {
  agent_id: string;
  customer_id: string;
  image: string;
  env?: Record<string, string>;
  resources?: ResourceLimits;
}

export interface EdgeDeploymentConfig extends DeploymentConfig {
  device_id: string;
}

export interface ResourceLimits {
  cpu?: string; // e.g., "0.5" for 0.5 CPU cores
  memory?: string; // e.g., "512Mi" for 512 MB
  disk?: string; // e.g., "1Gi" for 1 GB
}

export interface Container {
  id: string;
  container_id: string;
  agent_id: string;
  customer_id: string;
  image: string;
  address: string;
  health_url: string;
  status: ContainerStatus;
  health: HealthStatus;
  cpu_usage?: number;
  memory_usage?: number;
  disk_usage?: number;
  load?: number;
  uptime?: number;
  target_type: 'railway' | 'edge';
  target_id?: string; // device_id for edge, railway_service_id for cloud
  created_at: Date;
  updated_at: Date;
}

export type ContainerStatus = 'pending' | 'deploying' | 'running' | 'stopped' | 'error';
export type HealthStatus = 'healthy' | 'degraded' | 'unhealthy' | 'unknown';

export interface HealthCheckResult {
  status: 'ok' | 'error';
  response_time?: number; // milliseconds
  load?: number;
  error_message?: string;
  checked_at: Date;
}

export interface RailwayDeploymentResult {
  service_id: string;
  deployment_id: string;
  url: string;
  status: string;
}

export interface EdgeDeploymentResult {
  container_id: string;
  address: string;
  status: string;
}

// Agent Communication Protocol types
export enum MessageType {
  REQUEST = 'request',
  INFORM = 'inform',
  PROPOSE = 'propose',
  AGREE = 'agree',
  REFUSE = 'refuse',
  CONFIRM = 'confirm',
  FAILURE = 'failure',
  DONE = 'done',
  DISCOVER = 'discover',
  OFFER = 'offer',
  ASSIGN = 'assign',
}

export interface AgentMessage {
  id: string;
  ts: string;
  type: MessageType;
  sender: string;
  to: string[];
  intent: string;
  task?: string;
  payload: Record<string, any>;
  context?: Record<string, any>;
  correlation?: Record<string, any>;
  expected?: Record<string, any>;
  status?: Record<string, any>;
  security?: Record<string, any>;
}

export interface DeploymentRequest {
  agent_id: string;
  customer_id: string;
  image: string;
  env?: Record<string, string>;
  resources?: ResourceLimits;
  target_type: 'railway' | 'edge';
  device_id?: string; // Required for edge deployments
}

export interface DeploymentResponse {
  deployment_id: string;
  container_id?: string;
  address: string;
  health_url: string;
  status: string;
}

export interface ScalingRequest {
  agent_id: string;
  customer_id: string;
  instances: number;
}

export interface AddressRequest {
  agent_id: string;
  customer_id: string;
}

export interface AddressResponse {
  address: string;
  health: HealthStatus;
  uptime?: number;
}

export interface Config {
  port: number;
  supabase_url: string;
  supabase_key: string;
  railway_api_key?: string;
  railway_api_url: string;
  agent_id: string;
  marketplace_url?: string;
}

export interface Device {
  id: string;
  device_id: string;
  customer_id: string;
  name: string;
  tailscale_ip: string;
  status: 'online' | 'offline' | 'claimed' | 'unclaimed';
  capabilities: string[];
  cpu_cores?: number;
  memory_mb?: number;
  disk_gb?: number;
  last_seen?: Date;
  created_at: Date;
  updated_at: Date;
}

