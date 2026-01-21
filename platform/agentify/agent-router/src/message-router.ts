/**
 * Message Router
 * Routes messages between cloud and edge agents
 */

import axios from 'axios';
import { Database } from './database';
import { logger } from './logger';
import {
  AgentMessage,
  AgentLocation,
  RouteResult,
  AgentRegistration,
  QueuedMessage,
} from './types';

export class MessageRouter {
  private database: Database;
  private deviceManagerUrl: string;
  private retryMaxAttempts: number;
  private retryBackoffMs: number;

  constructor(
    database: Database,
    deviceManagerUrl: string,
    retryMaxAttempts: number = 3,
    retryBackoffMs: number = 1000
  ) {
    this.database = database;
    this.deviceManagerUrl = deviceManagerUrl;
    this.retryMaxAttempts = retryMaxAttempts;
    this.retryBackoffMs = retryBackoffMs;
  }

  /**
   * Route a message to target agent(s)
   */
  async routeMessage(message: AgentMessage): Promise<RouteResult[]> {
    const results: RouteResult[] = [];

    // Route to each target agent
    for (const targetAgentId of message.to) {
      const result = await this.routeToAgent(message, targetAgentId);
      results.push(result);
    }

    return results;
  }

  /**
   * Route message to a specific agent
   */
  private async routeToAgent(message: AgentMessage, targetAgentId: string): Promise<RouteResult> {
    try {
      // Look up agent in registry
      const agent = await this.database.getAgent(targetAgentId);

      if (!agent) {
        logger.warn('Agent not found in registry', { agent_id: targetAgentId });
        return {
          success: false,
          delivered: false,
          queued: false,
          error: `Agent not found: ${targetAgentId}`,
        };
      }

      // Check if agent is online
      if (agent.status === 'offline') {
        logger.info('Agent offline, queueing message', { agent_id: targetAgentId });
        await this.queueMessage(message, agent);
        return {
          success: true,
          delivered: false,
          queued: true,
        };
      }

      // Route based on location
      if (agent.location === AgentLocation.CLOUD) {
        return await this.routeToCloud(message, agent);
      } else {
        return await this.routeToEdge(message, agent);
      }
    } catch (error: any) {
      logger.error('Failed to route message', { error, target_agent: targetAgentId });
      return {
        success: false,
        delivered: false,
        queued: false,
        error: error.message,
      };
    }
  }

  /**
   * Route message to cloud agent
   */
  private async routeToCloud(
    message: AgentMessage,
    agent: AgentRegistration
  ): Promise<RouteResult> {
    try {
      logger.info('Routing message to cloud agent', {
        agent_id: agent.agent_id,
        address: agent.address,
      });

      // Send HTTP POST to agent's /agent/message endpoint
      const response = await axios.post(
        `${agent.address}/agent/message`,
        message,
        {
          timeout: 30000, // 30 second timeout
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      logger.info('Message delivered to cloud agent', {
        agent_id: agent.agent_id,
        status: response.status,
      });

      return {
        success: true,
        delivered: true,
        queued: false,
        response: response.data,
      };
    } catch (error: any) {
      logger.error('Failed to deliver message to cloud agent', {
        error: error.message,
        agent_id: agent.agent_id,
      });

      // Queue message for retry
      await this.queueMessage(message, agent);

      return {
        success: false,
        delivered: false,
        queued: true,
        error: error.message,
      };
    }
  }

  /**
   * Route message to edge agent
   */
  private async routeToEdge(
    message: AgentMessage,
    agent: AgentRegistration
  ): Promise<RouteResult> {
    try {
      if (!agent.device_id) {
        throw new Error('Edge agent missing device_id');
      }

      logger.info('Routing message to edge agent', {
        agent_id: agent.agent_id,
        device_id: agent.device_id,
        address: agent.address,
      });

      // Check if device is online
      const deviceStatus = await this.getDeviceStatus(agent.device_id);

      if (!deviceStatus || deviceStatus.status === 'offline') {
        logger.info('Edge device offline, queueing message', { device_id: agent.device_id });
        await this.queueMessage(message, agent);
        return {
          success: true,
          delivered: false,
          queued: true,
        };
      }

      // Send HTTP POST to agent via Tailscale IP
      // Agent address should be in format: http://<tailscale-ip>:<port>
      const response = await axios.post(
        `${agent.address}/agent/message`,
        message,
        {
          timeout: 30000, // 30 second timeout
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      logger.info('Message delivered to edge agent', {
        agent_id: agent.agent_id,
        status: response.status,
      });

      return {
        success: true,
        delivered: true,
        queued: false,
        response: response.data,
      };
    } catch (error: any) {
      logger.error('Failed to deliver message to edge agent', {
        error: error.message,
        agent_id: agent.agent_id,
      });

      // Queue message for retry
      await this.queueMessage(message, agent);

      return {
        success: false,
        delivered: false,
        queued: true,
        error: error.message,
      };
    }
  }

  /**
   * Queue message for later delivery
   */
  private async queueMessage(message: AgentMessage, agent: AgentRegistration): Promise<void> {
    const queuedMessage: Omit<QueuedMessage, 'id' | 'created_at'> = {
      message,
      target_agent_id: agent.agent_id,
      target_location: agent.location,
      target_device_id: agent.device_id,
      retry_count: 0,
      max_retries: this.retryMaxAttempts,
      next_retry_at: new Date(Date.now() + this.retryBackoffMs),
      delivered: false,
    };

    await this.database.queueMessage(queuedMessage);
  }

  /**
   * Process pending messages for an agent
   */
  async processPendingMessages(agentId: string): Promise<number> {
    const pendingMessages = await this.database.getPendingMessages(agentId);

    let deliveredCount = 0;

    for (const queuedMsg of pendingMessages) {
      try {
        const agent = await this.database.getAgent(agentId);

        if (!agent || agent.status === 'offline') {
          logger.info('Agent still offline, skipping', { agent_id: agentId });
          continue;
        }

        // Attempt delivery
        const result = await this.routeToAgent(queuedMsg.message, agentId);

        if (result.delivered) {
          // Mark as delivered
          await this.database.markMessageDelivered(queuedMsg.id);
          deliveredCount++;
        } else {
          // Update retry count
          const newRetryCount = queuedMsg.retry_count + 1;

          if (newRetryCount >= queuedMsg.max_retries) {
            // Max retries reached, mark as failed
            await this.database.markMessageDelivered(queuedMsg.id);
            logger.warn('Message max retries reached', {
              message_id: queuedMsg.id,
              agent_id: agentId,
            });
          } else {
            // Schedule next retry with exponential backoff
            const nextRetryAt = new Date(
              Date.now() + this.retryBackoffMs * Math.pow(2, newRetryCount)
            );

            await this.database.updateMessageRetry(
              queuedMsg.id,
              newRetryCount,
              nextRetryAt,
              result.error
            );
          }
        }
      } catch (error: any) {
        logger.error('Failed to process pending message', {
          error: error.message,
          message_id: queuedMsg.id,
        });
      }
    }

    return deliveredCount;
  }

  /**
   * Get device status from Device Manager
   */
  private async getDeviceStatus(deviceId: string): Promise<{ status: string } | null> {
    try {
      const response = await axios.get(
        `${this.deviceManagerUrl}/api/v1/devices/${deviceId}`,
        {
          timeout: 5000,
        }
      );

      if (response.data.success) {
        return {
          status: response.data.data.status,
        };
      }

      return null;
    } catch (error: any) {
      logger.error('Failed to get device status', { error: error.message, device_id: deviceId });
      return null;
    }
  }

  /**
   * Start background job to process pending messages
   */
  startMessageProcessor(intervalMs: number = 10000): NodeJS.Timeout {
    logger.info('Starting message processor', { interval_ms: intervalMs });

    return setInterval(async () => {
      try {
        // Get all agents with pending messages
        const stats = await this.database.getStatistics();

        if (stats.pending_messages > 0) {
          logger.info('Processing pending messages', { count: stats.pending_messages });

          // Get all online agents
          const agents = await this.database.discoverAgents();

          for (const agent of agents) {
            await this.processPendingMessages(agent.agent_id);
          }
        }
      } catch (error: any) {
        logger.error('Error in message processor', { error: error.message });
      }
    }, intervalMs);
  }
}

