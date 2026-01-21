/**
 * Type definitions for Agent Router
 */

// Configuration
export interface Config {
  port: number;
  supabase_url: string;
  supabase_key: string;
  redis_url: string;
  device_manager_url: string;
  message_ttl_seconds: number;
  retry_max_attempts: number;
  retry_backoff_ms: number;
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

// Agent location types
export enum AgentLocation {
  CLOUD = 'cloud',
  EDGE = 'edge',
}

export interface AgentRegistration {
  agent_id: string;
  location: AgentLocation;
  address: string;
  device_id?: string; // For edge agents
  customer_id: string;
  capabilities: string[];
  status: 'online' | 'offline';
  last_seen: Date;
  metadata?: Record<string, any>;
}

// Message queue types
export interface QueuedMessage {
  id: string;
  message: AgentMessage;
  target_agent_id: string;
  target_location: AgentLocation;
  target_device_id?: string;
  retry_count: number;
  max_retries: number;
  created_at: Date;
  next_retry_at?: Date;
  delivered: boolean;
  delivered_at?: Date;
  error?: string;
}

// Routing types
export interface RouteResult {
  success: boolean;
  delivered: boolean;
  queued: boolean;
  response?: AgentMessage;
  error?: string;
}

// API Response
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Agent discovery
export interface AgentDiscoveryRequest {
  capabilities?: string[];
  location?: AgentLocation;
  customer_id?: string;
}

export interface AgentDiscoveryResponse {
  agents: AgentRegistration[];
}

// WebSocket message types
export enum WSMessageType {
  REGISTER = 'register',
  AGENT_MESSAGE = 'agent_message',
  HEARTBEAT = 'heartbeat',
  ACK = 'ack',
  ERROR = 'error',
}

export interface WSMessage {
  type: WSMessageType;
  payload: any;
}

// Device status
export interface DeviceStatus {
  device_id: string;
  status: 'online' | 'offline';
  tailscale_ip: string;
  last_seen: Date;
}

