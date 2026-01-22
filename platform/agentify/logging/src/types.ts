/**
 * Type definitions for Logging Agent
 */

// ========== Log Types ==========

export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error',
  FATAL = 'fatal',
}

export enum SourceType {
  AGENT = 'agent',
  CONTAINER = 'container',
  DEVICE = 'device',
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: LogLevel;
  source_type: SourceType;
  source_id: string;
  customer_id: string;
  message: string;
  metadata?: Record<string, any>;
  tags?: string[];
}

export interface CollectLogsRequest {
  source_type: SourceType;
  source_id: string;
  customer_id: string;
  since?: string;
  until?: string;
  tail?: number;
  follow?: boolean;
}

export interface SearchLogsRequest {
  query?: string;
  source_type?: SourceType;
  source_id?: string;
  customer_id: string;
  level?: LogLevel;
  start_time?: string;
  end_time?: string;
  tags?: string[];
  limit?: number;
  offset?: number;
}

export interface SearchLogsResponse {
  logs: LogEntry[];
  count: number;
  has_more: boolean;
  total?: number;
}

export interface StreamLogsRequest {
  source_type: SourceType;
  source_id: string;
  customer_id: string;
  level?: LogLevel;
  filter?: string;
}

// ========== Retention Policy Types ==========

export interface RetentionPolicy {
  id: string;
  customer_id: string;
  source_type?: SourceType;
  level?: LogLevel;
  retention_days: number;
  compression_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface RetentionStats {
  total_logs: number;
  oldest_log: string;
  newest_log: string;
  size_bytes: number;
  logs_by_level: Record<LogLevel, number>;
}

// ========== Export Types ==========

export enum ExportFormat {
  JSON = 'json',
  CSV = 'csv',
  TEXT = 'text',
}

export enum ExportDestination {
  S3 = 's3',
  GCS = 'gcs',
  LOCAL = 'local',
  HTTP = 'http',
}

export interface ExportLogsRequest {
  search: SearchLogsRequest;
  format: ExportFormat;
  destination: ExportDestination;
  destination_config: Record<string, any>;
}

export interface ExportJob {
  id: string;
  customer_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  format: ExportFormat;
  destination: ExportDestination;
  log_count: number;
  created_at: string;
  completed_at?: string;
  error?: string;
  download_url?: string;
}

// ========== Agent Communication Protocol Types ==========

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

// ========== API Response Types ==========

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// ========== Container/Device Info ==========

export interface ContainerInfo {
  id: string;
  name: string;
  agent_id: string;
  customer_id: string;
  location: 'cloud' | 'edge';
  device_id?: string;
  status: string;
}

export interface DeviceInfo {
  id: string;
  name: string;
  customer_id: string;
  tailscale_ip: string;
  status: 'online' | 'offline';
}

