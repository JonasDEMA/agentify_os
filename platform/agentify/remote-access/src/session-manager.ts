/**
 * Session Manager for Remote Access Agent
 * Handles SSH and VNC session creation and management
 */

import { v4 as uuidv4 } from 'uuid';
import { logger } from './logger';
import { Database } from './database';
import {
  Session,
  SessionType,
  SessionStatus,
  CreateSessionRequest,
  CreateSessionResponse,
  ConnectionInfo,
  AuditAction,
} from './types';

export class SessionManager {
  private database: Database;
  private defaultDurationMinutes = 60;
  private maxDurationMinutes = 480; // 8 hours

  constructor(database: Database) {
    this.database = database;
  }

  /**
   * Create a new SSH session
   */
  async createSSHSession(request: CreateSessionRequest): Promise<CreateSessionResponse> {
    logger.info('Creating SSH session', {
      device_id: request.device_id,
      user_id: request.user_id,
    });

    // Validate access
    const hasAccess = await this.database.checkAccess(
      request.user_id,
      request.device_id,
      request.customer_id
    );

    if (!hasAccess) {
      await this.database.createAuditLog({
        user_id: request.user_id,
        device_id: request.device_id,
        action: AuditAction.ACCESS_DENIED,
        status: 'failure',
        details: { reason: 'No access policy found' },
      });
      throw new Error('Access denied: No permission to access this device');
    }

    // Get device info
    const device = await this.database.getDevice(request.device_id);
    if (!device) {
      throw new Error(`Device not found: ${request.device_id}`);
    }

    if (device.status !== 'online') {
      throw new Error(`Device is offline: ${request.device_id}`);
    }

    if (!device.ssh_enabled) {
      throw new Error(`SSH is not enabled on device: ${request.device_id}`);
    }

    // Calculate expiration
    const duration = Math.min(
      request.duration_minutes || this.defaultDurationMinutes,
      this.maxDurationMinutes
    );
    const expiresAt = new Date(Date.now() + duration * 60 * 1000).toISOString();

    // Create connection info
    const connectionInfo: ConnectionInfo = {
      host: device.tailscale_ip,
      port: 22,
      ssh_command: `ssh root@${device.tailscale_ip}`,
    };

    // Create session
    const session = await this.database.createSession({
      type: SessionType.SSH,
      device_id: request.device_id,
      user_id: request.user_id,
      customer_id: request.customer_id,
      purpose: request.purpose,
      status: SessionStatus.ACTIVE,
      expires_at: expiresAt,
      connection_info: connectionInfo,
      metadata: request.metadata,
    });

    // Audit log
    await this.database.createAuditLog({
      session_id: session.id,
      user_id: request.user_id,
      device_id: request.device_id,
      action: AuditAction.SESSION_CREATE,
      status: 'success',
      details: {
        type: SessionType.SSH,
        duration_minutes: duration,
        purpose: request.purpose,
      },
    });

    logger.info('SSH session created', {
      session_id: session.id,
      device_id: request.device_id,
      expires_at: expiresAt,
    });

    return {
      session_id: session.id,
      type: SessionType.SSH,
      connection_info: connectionInfo,
      expires_at: expiresAt,
    };
  }

  /**
   * Create a new VNC session
   */
  async createVNCSession(request: CreateSessionRequest): Promise<CreateSessionResponse> {
    logger.info('Creating VNC session', {
      device_id: request.device_id,
      user_id: request.user_id,
    });

    // Validate access
    const hasAccess = await this.database.checkAccess(
      request.user_id,
      request.device_id,
      request.customer_id
    );

    if (!hasAccess) {
      await this.database.createAuditLog({
        user_id: request.user_id,
        device_id: request.device_id,
        action: AuditAction.ACCESS_DENIED,
        status: 'failure',
        details: { reason: 'No access policy found' },
      });
      throw new Error('Access denied: No permission to access this device');
    }

    // Get device info
    const device = await this.database.getDevice(request.device_id);
    if (!device) {
      throw new Error(`Device not found: ${request.device_id}`);
    }

    if (device.status !== 'online') {
      throw new Error(`Device is offline: ${request.device_id}`);
    }

    if (!device.vnc_enabled) {
      throw new Error(`VNC is not enabled on device: ${request.device_id}`);
    }

    // Calculate expiration
    const duration = Math.min(
      request.duration_minutes || this.defaultDurationMinutes,
      this.maxDurationMinutes
    );
    const expiresAt = new Date(Date.now() + duration * 60 * 1000).toISOString();

    // Create connection info
    const vncPort = device.vnc_port || 5900;
    const connectionInfo: ConnectionInfo = {
      host: device.tailscale_ip,
      port: vncPort,
      vnc_url: `vnc://${device.tailscale_ip}:${vncPort}`,
    };

    // Create session
    const session = await this.database.createSession({
      type: SessionType.VNC,
      device_id: request.device_id,
      user_id: request.user_id,
      customer_id: request.customer_id,
      purpose: request.purpose,
      status: SessionStatus.ACTIVE,
      expires_at: expiresAt,
      connection_info: connectionInfo,
      metadata: request.metadata,
    });

    // Audit log
    await this.database.createAuditLog({
      session_id: session.id,
      user_id: request.user_id,
      device_id: request.device_id,
      action: AuditAction.SESSION_CREATE,
      status: 'success',
      details: {
        type: SessionType.VNC,
        duration_minutes: duration,
        purpose: request.purpose,
      },
    });

    logger.info('VNC session created', {
      session_id: session.id,
      device_id: request.device_id,
      expires_at: expiresAt,
    });

    return {
      session_id: session.id,
      type: SessionType.VNC,
      connection_info: connectionInfo,
      expires_at: expiresAt,
    };
  }

  /**
   * List sessions
   */
  async listSessions(filters: {
    user_id?: string;
    device_id?: string;
    customer_id?: string;
    status?: SessionStatus;
  }): Promise<Session[]> {
    return this.database.listSessions(filters);
  }

  /**
   * Get session by ID
   */
  async getSession(sessionId: string): Promise<Session | null> {
    return this.database.getSession(sessionId);
  }

  /**
   * Terminate session
   */
  async terminateSession(sessionId: string, userId: string): Promise<void> {
    logger.info('Terminating session', { session_id: sessionId, user_id: userId });

    const session = await this.database.getSession(sessionId);
    if (!session) {
      throw new Error(`Session not found: ${sessionId}`);
    }

    if (session.status !== SessionStatus.ACTIVE) {
      throw new Error(`Session is not active: ${sessionId}`);
    }

    // Update session status
    const terminatedAt = new Date().toISOString();
    await this.database.updateSessionStatus(sessionId, SessionStatus.TERMINATED, terminatedAt);

    // Audit log
    await this.database.createAuditLog({
      session_id: sessionId,
      user_id: userId,
      device_id: session.device_id,
      action: AuditAction.SESSION_TERMINATE,
      status: 'success',
      details: {
        terminated_by: userId,
        terminated_at: terminatedAt,
      },
    });

    logger.info('Session terminated', { session_id: sessionId });
  }

  /**
   * Expire old sessions (background job)
   */
  async expireOldSessions(): Promise<number> {
    logger.info('Expiring old sessions...');

    const count = await this.database.expireOldSessions();

    if (count > 0) {
      logger.info(`Expired ${count} sessions`);
    }

    return count;
  }

  /**
   * Start background job to expire sessions
   */
  startExpirationJob(intervalMs: number = 60000): void {
    logger.info('Starting session expiration job', { interval_ms: intervalMs });

    setInterval(async () => {
      try {
        await this.expireOldSessions();
      } catch (error: any) {
        logger.error('Failed to expire sessions', { error: error.message });
      }
    }, intervalMs);
  }
}
