/**
 * Database client for Device Manager
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js';
import {
  Device,
  DeviceClaimToken,
  DeviceHeartbeat,
  DeviceListFilters,
  DeviceUpdateRequest,
} from './types';
import { logger } from './logger';

export class Database {
  private client: SupabaseClient;

  constructor(supabaseUrl: string, supabaseKey: string) {
    this.client = createClient(supabaseUrl, supabaseKey);
  }

  /**
   * Initialize database tables
   */
  async initialize(): Promise<void> {
    logger.info('Initializing device management database tables');

    // Note: In production, use migrations instead of runtime table creation
    const { error } = await this.client.rpc('create_device_tables');

    if (error && !error.message.includes('already exists')) {
      logger.error('Failed to initialize database', { error });
      throw error;
    }

    logger.info('Database initialized successfully');
  }

  /**
   * Create a new device
   */
  async createDevice(device: Omit<Device, 'id' | 'created_at' | 'updated_at'>): Promise<Device> {
    const { data, error } = await this.client
      .from('devices')
      .insert({
        device_id: device.device_id,
        customer_id: device.customer_id,
        name: device.name,
        type: device.type,
        status: device.status,
        tailscale_ip: device.tailscale_ip,
        tailscale_hostname: device.tailscale_hostname,
        tailscale_node_id: device.tailscale_node_id,
        capabilities: device.capabilities,
        metadata: device.metadata,
        last_seen: device.last_seen,
      })
      .select()
      .single();

    if (error) {
      logger.error('Failed to create device', { error });
      throw error;
    }

    logger.info('Device created', { device_id: data.device_id });

    return data as Device;
  }

  /**
   * Get device by ID
   */
  async getDevice(deviceId: string): Promise<Device | null> {
    const { data, error } = await this.client
      .from('devices')
      .select('*')
      .eq('device_id', deviceId)
      .single();

    if (error) {
      if (error.code === 'PGRST116') {
        return null;
      }
      logger.error('Failed to get device', { error });
      throw error;
    }

    return data as Device;
  }

  /**
   * List devices with filters
   */
  async listDevices(filters?: DeviceListFilters): Promise<Device[]> {
    let query = this.client.from('devices').select('*');

    if (filters?.customer_id) {
      query = query.eq('customer_id', filters.customer_id);
    }
    if (filters?.status) {
      query = query.eq('status', filters.status);
    }
    if (filters?.type) {
      query = query.eq('type', filters.type);
    }

    if (filters?.limit) {
      query = query.limit(filters.limit);
    }
    if (filters?.offset) {
      query = query.range(filters.offset, filters.offset + (filters.limit || 10) - 1);
    }

    const { data, error } = await query.order('created_at', { ascending: false });

    if (error) {
      logger.error('Failed to list devices', { error });
      throw error;
    }

    return data as Device[];
  }

  /**
   * Update device
   */
  async updateDevice(deviceId: string, updates: DeviceUpdateRequest): Promise<Device> {
    const { data, error } = await this.client
      .from('devices')
      .update({
        ...updates,
        updated_at: new Date().toISOString(),
      })
      .eq('device_id', deviceId)
      .select()
      .single();

    if (error) {
      logger.error('Failed to update device', { error });
      throw error;
    }

    logger.info('Device updated', { device_id: deviceId });

    return data as Device;
  }

  /**
   * Update device status
   */
  async updateDeviceStatus(deviceId: string, status: Device['status']): Promise<void> {
    const { error } = await this.client
      .from('devices')
      .update({
        status,
        last_seen: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      })
      .eq('device_id', deviceId);

    if (error) {
      logger.error('Failed to update device status', { error });
      throw error;
    }

    logger.info('Device status updated', { device_id: deviceId, status });
  }

  /**
   * Delete device
   */
  async deleteDevice(deviceId: string): Promise<void> {
    const { error } = await this.client
      .from('devices')
      .delete()
      .eq('device_id', deviceId);

    if (error) {
      logger.error('Failed to delete device', { error });
      throw error;
    }

    logger.info('Device deleted', { device_id: deviceId });
  }

  /**
   * Create claim token
   */
  async createClaimToken(token: Omit<DeviceClaimToken, 'id' | 'created_at'>): Promise<DeviceClaimToken> {
    const { data, error } = await this.client
      .from('device_claim_tokens')
      .insert({
        token: token.token,
        device_id: token.device_id,
        customer_id: token.customer_id,
        expires_at: token.expires_at.toISOString(),
        claimed: token.claimed,
      })
      .select()
      .single();

    if (error) {
      logger.error('Failed to create claim token', { error });
      throw error;
    }

    logger.info('Claim token created', { customer_id: token.customer_id });

    return data as DeviceClaimToken;
  }

  /**
   * Get claim token
   */
  async getClaimToken(token: string): Promise<DeviceClaimToken | null> {
    const { data, error } = await this.client
      .from('device_claim_tokens')
      .select('*')
      .eq('token', token)
      .single();

    if (error) {
      if (error.code === 'PGRST116') {
        return null;
      }
      logger.error('Failed to get claim token', { error });
      throw error;
    }

    return data as DeviceClaimToken;
  }

  /**
   * Mark claim token as used
   */
  async markClaimTokenUsed(token: string, deviceId: string): Promise<void> {
    const { error } = await this.client
      .from('device_claim_tokens')
      .update({
        claimed: true,
        device_id: deviceId,
      })
      .eq('token', token);

    if (error) {
      logger.error('Failed to mark claim token as used', { error });
      throw error;
    }

    logger.info('Claim token marked as used', { token, device_id: deviceId });
  }

  /**
   * Record device heartbeat
   */
  async recordHeartbeat(heartbeat: DeviceHeartbeat): Promise<void> {
    const { error } = await this.client.from('device_heartbeats').insert({
      device_id: heartbeat.device_id,
      timestamp: heartbeat.timestamp.toISOString(),
      status: heartbeat.status,
      metrics: heartbeat.metrics,
    });

    if (error) {
      logger.error('Failed to record heartbeat', { error });
      // Don't throw - heartbeat recording is not critical
    }

    // Update device last_seen
    await this.updateDeviceStatus(heartbeat.device_id, heartbeat.status);
  }

  /**
   * Get recent heartbeats for a device
   */
  async getHeartbeats(deviceId: string, limit: number = 10): Promise<DeviceHeartbeat[]> {
    const { data, error } = await this.client
      .from('device_heartbeats')
      .select('*')
      .eq('device_id', deviceId)
      .order('timestamp', { ascending: false })
      .limit(limit);

    if (error) {
      logger.error('Failed to get heartbeats', { error });
      return [];
    }

    return data.map((row: any) => ({
      device_id: row.device_id,
      timestamp: new Date(row.timestamp),
      status: row.status,
      metrics: row.metrics,
    }));
  }

  /**
   * Get devices by customer
   */
  async getDevicesByCustomer(customerId: string): Promise<Device[]> {
    return this.listDevices({ customer_id: customerId });
  }

  /**
   * Get online devices count
   */
  async getOnlineDevicesCount(customerId?: string): Promise<number> {
    let query = this.client
      .from('devices')
      .select('*', { count: 'exact', head: true })
      .eq('status', 'online');

    if (customerId) {
      query = query.eq('customer_id', customerId);
    }

    const { count, error } = await query;

    if (error) {
      logger.error('Failed to get online devices count', { error });
      return 0;
    }

    return count || 0;
  }
}

