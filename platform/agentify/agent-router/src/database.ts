/**
 * Database client for Agent Router
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { AgentRegistration, AgentLocation, QueuedMessage, AgentMessage } from './types';
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
    logger.info('Initializing agent router database tables');

    // Note: In production, use migrations instead of runtime table creation
    const { error } = await this.client.rpc('create_agent_router_tables');

    if (error && !error.message.includes('already exists')) {
      logger.error('Failed to initialize database', { error });
      throw error;
    }

    logger.info('Database initialized successfully');
  }

  /**
   * Register an agent
   */
  async registerAgent(agent: Omit<AgentRegistration, 'last_seen'>): Promise<AgentRegistration> {
    const { data, error } = await this.client
      .from('agent_registry')
      .upsert(
        {
          agent_id: agent.agent_id,
          location: agent.location,
          address: agent.address,
          device_id: agent.device_id,
          customer_id: agent.customer_id,
          capabilities: agent.capabilities,
          status: agent.status,
          metadata: agent.metadata,
          last_seen: new Date().toISOString(),
        },
        { onConflict: 'agent_id' }
      )
      .select()
      .single();

    if (error) {
      logger.error('Failed to register agent', { error });
      throw error;
    }

    logger.info('Agent registered', { agent_id: agent.agent_id, location: agent.location });

    return data as AgentRegistration;
  }

  /**
   * Get agent by ID
   */
  async getAgent(agentId: string): Promise<AgentRegistration | null> {
    const { data, error } = await this.client
      .from('agent_registry')
      .select('*')
      .eq('agent_id', agentId)
      .single();

    if (error) {
      if (error.code === 'PGRST116') {
        return null;
      }
      logger.error('Failed to get agent', { error });
      throw error;
    }

    return data as AgentRegistration;
  }

  /**
   * Discover agents by capabilities
   */
  async discoverAgents(
    capabilities?: string[],
    location?: AgentLocation,
    customerId?: string
  ): Promise<AgentRegistration[]> {
    let query = this.client.from('agent_registry').select('*').eq('status', 'online');

    if (customerId) {
      query = query.eq('customer_id', customerId);
    }

    if (location) {
      query = query.eq('location', location);
    }

    if (capabilities && capabilities.length > 0) {
      // Filter agents that have at least one of the required capabilities
      query = query.overlaps('capabilities', capabilities);
    }

    const { data, error } = await query.order('last_seen', { ascending: false });

    if (error) {
      logger.error('Failed to discover agents', { error });
      throw error;
    }

    return data as AgentRegistration[];
  }

  /**
   * Update agent status
   */
  async updateAgentStatus(agentId: string, status: 'online' | 'offline'): Promise<void> {
    const { error } = await this.client
      .from('agent_registry')
      .update({
        status,
        last_seen: new Date().toISOString(),
      })
      .eq('agent_id', agentId);

    if (error) {
      logger.error('Failed to update agent status', { error });
      throw error;
    }

    logger.info('Agent status updated', { agent_id: agentId, status });
  }

  /**
   * Unregister agent
   */
  async unregisterAgent(agentId: string): Promise<void> {
    const { error } = await this.client.from('agent_registry').delete().eq('agent_id', agentId);

    if (error) {
      logger.error('Failed to unregister agent', { error });
      throw error;
    }

    logger.info('Agent unregistered', { agent_id: agentId });
  }

  /**
   * Queue a message for delivery
   */
  async queueMessage(message: Omit<QueuedMessage, 'id' | 'created_at'>): Promise<QueuedMessage> {
    const { data, error } = await this.client
      .from('message_queue')
      .insert({
        message: message.message,
        target_agent_id: message.target_agent_id,
        target_location: message.target_location,
        target_device_id: message.target_device_id,
        retry_count: message.retry_count,
        max_retries: message.max_retries,
        next_retry_at: message.next_retry_at?.toISOString(),
        delivered: message.delivered,
        delivered_at: message.delivered_at?.toISOString(),
        error: message.error,
      })
      .select()
      .single();

    if (error) {
      logger.error('Failed to queue message', { error });
      throw error;
    }

    logger.info('Message queued', {
      message_id: data.id,
      target_agent: message.target_agent_id,
    });

    return data as QueuedMessage;
  }

  /**
   * Get pending messages for an agent
   */
  async getPendingMessages(agentId: string, limit: number = 10): Promise<QueuedMessage[]> {
    const { data, error } = await this.client
      .from('message_queue')
      .select('*')
      .eq('target_agent_id', agentId)
      .eq('delivered', false)
      .lte('next_retry_at', new Date().toISOString())
      .order('created_at', { ascending: true })
      .limit(limit);

    if (error) {
      logger.error('Failed to get pending messages', { error });
      return [];
    }

    return data as QueuedMessage[];
  }

  /**
   * Mark message as delivered
   */
  async markMessageDelivered(messageId: string): Promise<void> {
    const { error } = await this.client
      .from('message_queue')
      .update({
        delivered: true,
        delivered_at: new Date().toISOString(),
      })
      .eq('id', messageId);

    if (error) {
      logger.error('Failed to mark message as delivered', { error });
      throw error;
    }

    logger.info('Message marked as delivered', { message_id: messageId });
  }

  /**
   * Update message retry count
   */
  async updateMessageRetry(
    messageId: string,
    retryCount: number,
    nextRetryAt: Date,
    error?: string
  ): Promise<void> {
    const { error: updateError } = await this.client
      .from('message_queue')
      .update({
        retry_count: retryCount,
        next_retry_at: nextRetryAt.toISOString(),
        error,
      })
      .eq('id', messageId);

    if (updateError) {
      logger.error('Failed to update message retry', { error: updateError });
      throw updateError;
    }

    logger.info('Message retry updated', { message_id: messageId, retry_count: retryCount });
  }

  /**
   * Delete old delivered messages
   */
  async cleanupDeliveredMessages(olderThanHours: number = 24): Promise<number> {
    const cutoffDate = new Date();
    cutoffDate.setHours(cutoffDate.getHours() - olderThanHours);

    const { data, error } = await this.client
      .from('message_queue')
      .delete()
      .eq('delivered', true)
      .lt('delivered_at', cutoffDate.toISOString())
      .select('id');

    if (error) {
      logger.error('Failed to cleanup delivered messages', { error });
      return 0;
    }

    const count = data?.length || 0;
    logger.info('Cleaned up delivered messages', { count });

    return count;
  }

  /**
   * Get agents by device ID
   */
  async getAgentsByDevice(deviceId: string): Promise<AgentRegistration[]> {
    const { data, error } = await this.client
      .from('agent_registry')
      .select('*')
      .eq('device_id', deviceId)
      .eq('status', 'online');

    if (error) {
      logger.error('Failed to get agents by device', { error });
      return [];
    }

    return data as AgentRegistration[];
  }

  /**
   * Get statistics
   */
  async getStatistics(): Promise<{
    total_agents: number;
    cloud_agents: number;
    edge_agents: number;
    online_agents: number;
    pending_messages: number;
  }> {
    const [agentsResult, messagesResult] = await Promise.all([
      this.client.from('agent_registry').select('location, status', { count: 'exact' }),
      this.client
        .from('message_queue')
        .select('id', { count: 'exact', head: true })
        .eq('delivered', false),
    ]);

    const agents = agentsResult.data || [];
    const cloudAgents = agents.filter((a) => a.location === 'cloud').length;
    const edgeAgents = agents.filter((a) => a.location === 'edge').length;
    const onlineAgents = agents.filter((a) => a.status === 'online').length;

    return {
      total_agents: agents.length,
      cloud_agents: cloudAgents,
      edge_agents: edgeAgents,
      online_agents: onlineAgents,
      pending_messages: messagesResult.count || 0,
    };
  }
}

