/**
 * Type definitions for Monitoring Agent
 */

// ========== Metric Types ==========

export enum MetricType {
  GAUGE = 'gauge',
  COUNTER = 'counter',
  HISTOGRAM = 'histogram',
}

export enum SourceType {
  AGENT = 'agent',
  CONTAINER = 'container',
  DEVICE = 'device',
}

export interface Metric {
  id: string;
  timestamp: string;
  source_type: SourceType;
  source_id: string;
  customer_id: string;
  metric_name: string;
  metric_type: MetricType;
  value: number;
  unit: string;
  labels?: Record<string, string>;
  metadata?: Record<string, any>;
}

export interface CollectMetricsRequest {
  source_type: SourceType;
  source_id: string;
  customer_id: string;
  metrics?: string[]; // Specific metrics to collect, or all if not specified
}

export interface MetricsSnapshot {
  timestamp: string;
  source_type: SourceType;
  source_id: string;
  customer_id: string;
  cpu_usage_percent: number;
  memory_usage_percent: number;
  memory_used_bytes: number;
  memory_total_bytes: number;
  disk_usage_percent: number;
  disk_used_bytes: number;
  disk_total_bytes: number;
  network_rx_bytes: number;
  network_tx_bytes: number;
  uptime_seconds: number;
  load_average?: number[];
  temperature?: number;
}

// ========== Health Check Types ==========

export enum HealthStatus {
  HEALTHY = 'healthy',
  DEGRADED = 'degraded',
  UNHEALTHY = 'unhealthy',
  UNKNOWN = 'unknown',
}

export interface HealthCheck {
  id: string;
  timestamp: string;
  source_type: SourceType;
  source_id: string;
  customer_id: string;
  status: HealthStatus;
  checks: HealthCheckResult[];
  overall_score: number; // 0-100
}

export interface HealthCheckResult {
  name: string;
  status: HealthStatus;
  message: string;
  value?: number;
  threshold?: number;
  duration_ms?: number;
}

export interface CheckHealthRequest {
  source_type: SourceType;
  source_id: string;
  customer_id: string;
}

// ========== Alert Types ==========

export enum AlertSeverity {
  INFO = 'info',
  WARNING = 'warning',
  CRITICAL = 'critical',
  EMERGENCY = 'emergency',
}

export enum AlertStatus {
  ACTIVE = 'active',
  ACKNOWLEDGED = 'acknowledged',
  RESOLVED = 'resolved',
}

export enum ConditionOperator {
  GT = 'gt',
  GTE = 'gte',
  LT = 'lt',
  LTE = 'lte',
  EQ = 'eq',
  NEQ = 'neq',
}

export interface AlertCondition {
  metric_name: string;
  operator: ConditionOperator;
  threshold: number;
  duration_seconds?: number; // Alert only if condition persists for this duration
}

export interface AlertRule {
  id: string;
  customer_id: string;
  name: string;
  description?: string;
  source_type?: SourceType;
  source_id?: string;
  condition: AlertCondition;
  severity: AlertSeverity;
  channels: string[];
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface Alert {
  id: string;
  rule_id: string;
  customer_id: string;
  source_type: SourceType;
  source_id: string;
  severity: AlertSeverity;
  status: AlertStatus;
  title: string;
  message: string;
  metric_value: number;
  threshold: number;
  triggered_at: string;
  acknowledged_at?: string;
  acknowledged_by?: string;
  resolved_at?: string;
  metadata?: Record<string, any>;
}

export interface CreateAlertRuleRequest {
  customer_id: string;
  name: string;
  description?: string;
  source_type?: SourceType;
  source_id?: string;
  condition: AlertCondition;
  severity: AlertSeverity;
  channels: string[];
}

// ========== Dashboard Types ==========

export interface DashboardDataRequest {
  customer_id: string;
  source_type?: SourceType;
  source_id?: string;
  time_range: {
    start: string;
    end: string;
  };
  metrics?: string[];
  aggregation?: 'avg' | 'min' | 'max' | 'sum';
  interval?: string; // e.g., '5m', '1h', '1d'
}

export interface TimeSeriesDataPoint {
  timestamp: string;
  value: number;
}

export interface DashboardData {
  metrics: Record<string, TimeSeriesDataPoint[]>;
  summary: Record<string, number>;
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

