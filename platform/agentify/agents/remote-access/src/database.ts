/**
 * Database client for Remote Access Agent
 * Manages sessions, access policies, and audit logs in Supabase
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { logger } from './logger';
import {
  Session,
  SessionStatus,
  AccessPolicy,
  AuditLog,
  Device,
} from './types';

export class Database {
  private supabase: SupabaseClient;

  constructor() {
    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_KEY;

    if (!supabaseUrl || !supabaseKey) {
      throw new Error('SUPABASE_URL and SUPABASE_KEY must be set');
    }

    this.supabase = createClient(supabaseUrl, supabaseKey);
  }

  /**
   * Initialize database tables
   */
  async initialize(): Promise<void> {
    logger.info('Initializing database tables...');
    
    // Tables will be created via Supabase migrations
    // This method can be used for any runtime initialization
    
    logger.info('Database initialized successfully');
  }

  // ========== Session Management ==========

  /**
   * Create a new session
   */
  async createSession(session: Omit<Session, 'id' | 'created_at'>): Promise<Session> {
    const { data, error } = await this.supabase
      .from('remote_access_sessions')
      .insert({
        type: session.type,
        device_id: session.device_id,
        user_id: session.user_id,
        customer_id: session.customer_id,
        purpose: session.purpose,
        status: session.status,
        expires_at: session.expires_at,
        connection_info: session.connection_info,
        metadata: session.metadata || {},
      })
      .select()
      .single();

    if (error) {
      logger.error('Failed to create session', { error });
      throw new Error(`Failed to create session: ${error.message}`);
    }

    return data as Session;
  }

  /**
   * Get session by ID
   */
  async getSession(sessionId: string): Promise<Session | null> {
    const { data, error } = await this.supabase
      .from('remote_access_sessions')
      .select('*')
      .eq('id', sessionId)
      .single();

    if (error) {
      if (error.code === 'PGRST116') {
        return null;
      }
      logger.error('Failed to get session', { error, sessionId });
      throw new Error(`Failed to get session: ${error.message}`);
    }

    return data as Session;
  }

  /**
   * List sessions with filters
   */
  async listSessions(filters: {
    user_id?: string;
    device_id?: string;
    customer_id?: string;
    status?: SessionStatus;
    limit?: number;
  }): Promise<Session[]> {
    let query = this.supabase
      .from('remote_access_sessions')
      .select('*')
      .order('created_at', { ascending: false });

    if (filters.user_id) {
      query = query.eq('user_id', filters.user_id);
    }
    if (filters.device_id) {
      query = query.eq('device_id', filters.device_id);
    }
    if (filters.customer_id) {
      query = query.eq('customer_id', filters.customer_id);
    }
    if (filters.status) {
      query = query.eq('status', filters.status);
    }
    if (filters.limit) {
      query = query.limit(filters.limit);
    }

    const { data, error } = await query;

    if (error) {
      logger.error('Failed to list sessions', { error, filters });
      throw new Error(`Failed to list sessions: ${error.message}`);
    }

    return data as Session[];
  }

  /**
   * Update session status
   */
  async updateSessionStatus(
    sessionId: string,
    status: SessionStatus,
    terminatedAt?: string
  ): Promise<void> {
    const updates: any = { status };
    if (terminatedAt) {
      updates.terminated_at = terminatedAt;
    }

    const { error } = await this.supabase
      .from('remote_access_sessions')
      .update(updates)
      .eq('id', sessionId);

    if (error) {
      logger.error('Failed to update session status', { error, sessionId, status });
      throw new Error(`Failed to update session status: ${error.message}`);
    }
  }

  /**
   * Expire old sessions
   */
  async expireOldSessions(): Promise<number> {
    const now = new Date().toISOString();

    const { data, error } = await this.supabase
      .from('remote_access_sessions')
      .update({ status: SessionStatus.EXPIRED })
      .eq('status', SessionStatus.ACTIVE)
      .lt('expires_at', now)
      .select();

    if (error) {
      logger.error('Failed to expire old sessions', { error });
      throw new Error(`Failed to expire old sessions: ${error.message}`);
    }

    return data?.length || 0;
  }

  // ========== Access Policy Management ==========

  /**
   * Get access policy for user
   */
  async getAccessPolicy(userId: string, customerId: string): Promise<AccessPolicy | null> {
    const { data, error } = await this.supabase
      .from('access_policies')
      .select('*')
      .eq('user_id', userId)
      .eq('customer_id', customerId)
      .single();

    if (error) {
      if (error.code === 'PGRST116') {
        return null;
      }
      logger.error('Failed to get access policy', { error, userId });
      throw new Error(`Failed to get access policy: ${error.message}`);
    }

    return data as AccessPolicy;
  }

  /**
   * Check if user has access to device
   */
  async checkAccess(userId: string, deviceId: string, customerId: string): Promise<boolean> {
    const policy = await this.getAccessPolicy(userId, customerId);

    if (!policy) {
      return false;
    }

    // Check if device is in allowed list (empty array means all devices)
    if (policy.device_ids.length > 0 && !policy.device_ids.includes(deviceId)) {
      return false;
    }

    return true;
  }

  // ========== Audit Logging ==========

  /**
   * Create audit log entry
   */
  async createAuditLog(log: Omit<AuditLog, 'id' | 'timestamp'>): Promise<void> {
    const { error } = await this.supabase
      .from('remote_access_audit_logs')
      .insert({
        session_id: log.session_id,
        user_id: log.user_id,
        device_id: log.device_id,
        action: log.action,
        status: log.status,
        details: log.details,
        ip_address: log.ip_address,
        user_agent: log.user_agent,
      });

    if (error) {
      logger.error('Failed to create audit log', { error, log });
      // Don't throw - audit logging should not break the main flow
    }
  }

  /**
   * Get audit logs with filters
   */
  async getAuditLogs(filters: {
    user_id?: string;
    device_id?: string;
    session_id?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
  }): Promise<AuditLog[]> {
    let query = this.supabase
      .from('remote_access_audit_logs')
      .select('*')
      .order('timestamp', { ascending: false });

    if (filters.user_id) {
      query = query.eq('user_id', filters.user_id);
    }
    if (filters.device_id) {
      query = query.eq('device_id', filters.device_id);
    }
    if (filters.session_id) {
      query = query.eq('session_id', filters.session_id);
    }
    if (filters.start_date) {
      query = query.gte('timestamp', filters.start_date);
    }
    if (filters.end_date) {
      query = query.lte('timestamp', filters.end_date);
    }
    if (filters.limit) {
      query = query.limit(filters.limit);
    }

    const { data, error } = await query;

    if (error) {
      logger.error('Failed to get audit logs', { error, filters });
      throw new Error(`Failed to get audit logs: ${error.message}`);
    }

    return data as AuditLog[];
  }

  // ========== Device Management ==========

  /**
   * Get device by ID
   */
  async getDevice(deviceId: string): Promise<Device | null> {
    const { data, error } = await this.supabase
      .from('devices')
      .select('*')
      .eq('id', deviceId)
      .single();

    if (error) {
      if (error.code === 'PGRST116') {
        return null;
      }
      logger.error('Failed to get device', { error, deviceId });
      throw new Error(`Failed to get device: ${error.message}`);
    }

    return data as Device;
  }

  // ========== Statistics ==========

  /**
   * Get statistics
   */
  async getStatistics(): Promise<{
    total_sessions: number;
    active_sessions: number;
    total_users: number;
    total_devices: number;
  }> {
    const [totalSessions, activeSessions, totalPolicies] = await Promise.all([
      this.supabase.from('remote_access_sessions').select('id', { count: 'exact', head: true }),
      this.supabase
        .from('remote_access_sessions')
        .select('id', { count: 'exact', head: true })
        .eq('status', SessionStatus.ACTIVE),
      this.supabase.from('access_policies').select('id', { count: 'exact', head: true }),
    ]);

    return {
      total_sessions: totalSessions.count || 0,
      active_sessions: activeSessions.count || 0,
      total_users: totalPolicies.count || 0,
      total_devices: 0, // Can be enhanced
    };
  }
}

