/**
 * Type definitions for Device Manager
 */

export interface Device {
  id: string;
  device_id: string;
  customer_id: string;
  name: string;
  type: DeviceType;
  status: DeviceStatus;
  tailscale_ip: string;
  tailscale_hostname?: string;
  tailscale_node_id?: string;
  capabilities: DeviceCapabilities;
  metadata?: Record<string, any>;
  last_seen?: Date;
  created_at: Date;
  updated_at: Date;
}

export type DeviceType = 'raspberry_pi' | 'generic_linux' | 'other';

export type DeviceStatus = 'unclaimed' | 'claimed' | 'online' | 'offline' | 'error';

export interface DeviceCapabilities {
  cpu_cores: number;
  cpu_model?: string;
  memory_mb: number;
  disk_gb: number;
  architecture: string; // arm64, amd64, etc.
  os: string;
  os_version: string;
  docker_version?: string;
  network_interfaces: string[];
  has_gpu?: boolean;
}

export interface DeviceRegistration {
  device_id: string;
  name: string;
  type: DeviceType;
  capabilities: DeviceCapabilities;
  tailscale_ip: string;
  tailscale_hostname?: string;
  tailscale_node_id?: string;
}

export interface DeviceClaimToken {
  id: string;
  token: string;
  device_id?: string;
  customer_id: string;
  expires_at: Date;
  claimed: boolean;
  created_at: Date;
}

export interface DeviceHeartbeat {
  device_id: string;
  timestamp: Date;
  status: DeviceStatus;
  metrics?: DeviceMetrics;
}

export interface DeviceMetrics {
  cpu_usage: number; // percentage
  memory_usage: number; // percentage
  disk_usage: number; // percentage
  temperature?: number; // celsius
  uptime: number; // seconds
  load_average?: number[];
}

export interface TailscaleDevice {
  id: string;
  name: string;
  hostname: string;
  addresses: string[];
  nodeId: string;
  user: string;
  online: boolean;
  lastSeen: string;
  os: string;
  clientVersion: string;
}

export interface TailscaleAuthKey {
  key: string;
  expires: string;
  capabilities: {
    devices: {
      create: {
        reusable: boolean;
        ephemeral: boolean;
        preauthorized: boolean;
        tags: string[];
      };
    };
  };
}

export interface Config {
  port: number;
  supabase_url: string;
  supabase_key: string;
  tailscale_api_key: string;
  tailscale_tailnet: string;
  tailscale_api_url: string;
  claim_token_expiry_hours: number;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface DeviceListFilters {
  customer_id?: string;
  status?: DeviceStatus;
  type?: DeviceType;
  limit?: number;
  offset?: number;
}

export interface DeviceUpdateRequest {
  name?: string;
  status?: DeviceStatus;
  capabilities?: Partial<DeviceCapabilities>;
  metadata?: Record<string, any>;
}

