/**
 * Database client for Supabase
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { Container, HealthCheckResult, Device } from './types';
import { logger } from './logger';

export class Database {
  private client: SupabaseClient;

  constructor(supabaseUrl: string, supabaseKey: string) {
    this.client = createClient(supabaseUrl, supabaseKey);
  }

  /**
   * Create containers table if it doesn't exist
   */
  async initialize(): Promise<void> {
    logger.info('Initializing database tables');

    // Note: In production, use migrations instead of runtime table creation
    // This is just for development convenience
    const { error } = await this.client.rpc('create_hosting_tables');

    if (error && !error.message.includes('already exists')) {
      logger.error('Failed to initialize database', { error });
      throw error;
    }

    logger.info('Database initialized successfully');
  }

  /**
   * Create a new container record
   */
  async createContainer(container: Omit<Container, 'id' | 'created_at' | 'updated_at'>): Promise<Container> {
    const { data, error } = await this.client
      .from('containers')
      .insert({
        container_id: container.container_id,
        agent_id: container.agent_id,
        customer_id: container.customer_id,
        image: container.image,
        address: container.address,
        health_url: container.health_url,
        status: container.status,
        health: container.health,
        target_type: container.target_type,
        target_id: container.target_id,
      })
      .select()
      .single();

    if (error) {
      logger.error('Failed to create container record', { error });
      throw error;
    }

    logger.info('Container record created', { container_id: data.container_id });

    return data as Container;
  }

  /**
   * Get container by ID
   */
  async getContainer(containerId: string): Promise<Container | null> {
    const { data, error } = await this.client
      .from('containers')
      .select('*')
      .eq('container_id', containerId)
      .single();

    if (error) {
      if (error.code === 'PGRST116') {
        // Not found
        return null;
      }
      logger.error('Failed to get container', { error });
      throw error;
    }

    return data as Container;
  }

  /**
   * Get container by agent and customer
   */
  async getContainerByAgent(agentId: string, customerId: string): Promise<Container | null> {
    const { data, error } = await this.client
      .from('containers')
      .select('*')
      .eq('agent_id', agentId)
      .eq('customer_id', customerId)
      .eq('status', 'running')
      .single();

    if (error) {
      if (error.code === 'PGRST116') {
        return null;
      }
      logger.error('Failed to get container by agent', { error });
      throw error;
    }

    return data as Container;
  }

  /**
   * List all containers
   */
  async listContainers(filters?: {
    customer_id?: string;
    status?: string;
    target_type?: 'railway' | 'edge';
  }): Promise<Container[]> {
    let query = this.client.from('containers').select('*');

    if (filters?.customer_id) {
      query = query.eq('customer_id', filters.customer_id);
    }
    if (filters?.status) {
      query = query.eq('status', filters.status);
    }
    if (filters?.target_type) {
      query = query.eq('target_type', filters.target_type);
    }

    const { data, error } = await query;

    if (error) {
      logger.error('Failed to list containers', { error });
      throw error;
    }

    return data as Container[];
  }

  /**
   * Update container status
   */
  async updateContainerStatus(
    containerId: string,
    status: Container['status'],
    health?: Container['health']
  ): Promise<void> {
    const updates: any = { status, updated_at: new Date().toISOString() };
    if (health) {
      updates.health = health;
    }

    const { error } = await this.client
      .from('containers')
      .update(updates)
      .eq('container_id', containerId);

    if (error) {
      logger.error('Failed to update container status', { error });
      throw error;
    }

    logger.info('Container status updated', { container_id: containerId, status, health });
  }

  /**
   * Update container metrics
   */
  async updateContainerMetrics(
    containerId: string,
    metrics: {
      cpu_usage?: number;
      memory_usage?: number;
      disk_usage?: number;
      load?: number;
      uptime?: number;
    }
  ): Promise<void> {
    const { error } = await this.client
      .from('containers')
      .update({ ...metrics, updated_at: new Date().toISOString() })
      .eq('container_id', containerId);

    if (error) {
      logger.error('Failed to update container metrics', { error });
      throw error;
    }
  }

  /**
   * Delete container record
   */
  async deleteContainer(containerId: string): Promise<void> {
    const { error } = await this.client
      .from('containers')
      .delete()
      .eq('container_id', containerId);

    if (error) {
      logger.error('Failed to delete container', { error });
      throw error;
    }

    logger.info('Container record deleted', { container_id: containerId });
  }

  /**
   * Record health check
   */
  async recordHealthCheck(containerId: string, result: HealthCheckResult): Promise<void> {
    const { error } = await this.client.from('health_checks').insert({
      container_id: containerId,
      status: result.status,
      response_time: result.response_time,
      load: result.load,
      error_message: result.error_message,
      checked_at: result.checked_at.toISOString(),
    });

    if (error) {
      logger.error('Failed to record health check', { error });
      // Don't throw - health check recording is not critical
    }
  }

  /**
   * Get recent health checks for a container
   */
  async getHealthChecks(containerId: string, limit: number = 10): Promise<HealthCheckResult[]> {
    const { data, error } = await this.client
      .from('health_checks')
      .select('*')
      .eq('container_id', containerId)
      .order('checked_at', { ascending: false })
      .limit(limit);

    if (error) {
      logger.error('Failed to get health checks', { error });
      return [];
    }

    return data.map((row: any) => ({
      status: row.status,
      response_time: row.response_time,
      load: row.load,
      error_message: row.error_message,
      checked_at: new Date(row.checked_at),
    }));
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
   * List devices
   */
  async listDevices(filters?: {
    customer_id?: string;
    status?: string;
  }): Promise<Device[]> {
    let query = this.client.from('devices').select('*');

    if (filters?.customer_id) {
      query = query.eq('customer_id', filters.customer_id);
    }
    if (filters?.status) {
      query = query.eq('status', filters.status);
    }

    const { data, error } = await query;

    if (error) {
      logger.error('Failed to list devices', { error });
      throw error;
    }

    return data as Device[];
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
}
