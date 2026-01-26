/**
 * Type definitions for Remote Access Agent
 */

// ========== Session Types ==========

export enum SessionType {
  SSH = 'ssh',
  VNC = 'vnc',
}

export enum SessionStatus {
  ACTIVE = 'active',
  EXPIRED = 'expired',
  TERMINATED = 'terminated',
}

export interface Session {
  id: string;
  type: SessionType;
  device_id: string;
  user_id: string;
  customer_id: string;
  purpose: string;
  status: SessionStatus;
  created_at: string;
  expires_at: string;
  terminated_at?: string;
  connection_info: ConnectionInfo;
  metadata?: Record<string, any>;
}

export interface ConnectionInfo {
  ssh_command?: string;
  vnc_url?: string;
  host: string;
  port: number;
  tunnel_port?: number;
}

export interface CreateSessionRequest {
  device_id: string;
  user_id: string;
  customer_id: string;
  type: SessionType;
  duration_minutes?: number;
  purpose: string;
  metadata?: Record<string, any>;
}

export interface CreateSessionResponse {
  session_id: string;
  type: SessionType;
  connection_info: ConnectionInfo;
  expires_at: string;
}

// ========== Access Control Types ==========

export interface AccessPolicy {
  id: string;
  user_id: string;
  customer_id: string;
  device_ids: string[];
  allowed_session_types: SessionType[];
  max_duration_minutes: number;
  requires_approval: boolean;
  requires_mfa: boolean;
  created_at: string;
  updated_at: string;
}

export interface AccessRequest {
  id: string;
  user_id: string;
  device_id: string;
  session_type: SessionType;
  purpose: string;
  status: 'pending' | 'approved' | 'denied';
  requested_at: string;
  reviewed_at?: string;
  reviewed_by?: string;
}

// ========== Audit Types ==========

export interface AuditLog {
  id: string;
  session_id?: string;
  user_id: string;
  device_id?: string;
  action: AuditAction;
  status: 'success' | 'failure';
  details: Record<string, any>;
  ip_address?: string;
  user_agent?: string;
  timestamp: string;
}

export enum AuditAction {
  SESSION_CREATE = 'session_create',
  SESSION_TERMINATE = 'session_terminate',
  SESSION_EXPIRE = 'session_expire',
  ACCESS_DENIED = 'access_denied',
  POLICY_UPDATE = 'policy_update',
  TUNNEL_OPEN = 'tunnel_open',
  TUNNEL_CLOSE = 'tunnel_close',
}

// ========== Device Types ==========

export interface Device {
  id: string;
  name: string;
  tailscale_ip: string;
  customer_id: string;
  status: 'online' | 'offline';
  ssh_enabled: boolean;
  vnc_enabled: boolean;
  vnc_port?: number;
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

