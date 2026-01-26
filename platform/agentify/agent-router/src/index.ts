/**
 * Agent Router Service
 * Main entry point
 */

import express, { Request, Response } from 'express';
import dotenv from 'dotenv';
import { Database } from './database';
import { MessageRouter } from './message-router';
import { logger } from './logger';
import {
  Config,
  ApiResponse,
  AgentMessage,
  AgentRegistration,
  AgentLocation,
  AgentDiscoveryRequest,
} from './types';

// Load environment variables
dotenv.config();

// Configuration
const config: Config = {
  port: parseInt(process.env.PORT || '3002'),
  supabase_url: process.env.SUPABASE_URL || '',
  supabase_key: process.env.SUPABASE_KEY || '',
  redis_url: process.env.REDIS_URL || '',
  device_manager_url: process.env.DEVICE_MANAGER_URL || 'http://localhost:3001',
  message_ttl_seconds: parseInt(process.env.MESSAGE_TTL_SECONDS || '86400'),
  retry_max_attempts: parseInt(process.env.RETRY_MAX_ATTEMPTS || '3'),
  retry_backoff_ms: parseInt(process.env.RETRY_BACKOFF_MS || '1000'),
};

// Initialize services
const database = new Database(config.supabase_url, config.supabase_key);
const messageRouter = new MessageRouter(
  database,
  config.device_manager_url,
  config.retry_max_attempts,
  config.retry_backoff_ms
);

// Create Express app
const app = express();
app.use(express.json());

/**
 * Health check endpoint
 */
app.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'ok',
    service: 'agent-router',
    timestamp: new Date().toISOString(),
  });
});

/**
 * Register agent
 * POST /api/v1/agents/register
 */
app.post('/api/v1/agents/register', async (req: Request, res: Response) => {
  try {
    const agentData: Omit<AgentRegistration, 'last_seen'> = req.body;

    if (!agentData.agent_id || !agentData.location || !agentData.address) {
      return res.status(400).json({
        success: false,
        error: 'agent_id, location, and address are required',
      } as ApiResponse);
    }

    const agent = await database.registerAgent(agentData);

    // Process any pending messages for this agent
    const deliveredCount = await messageRouter.processPendingMessages(agent.agent_id);

    logger.info('Agent registered', {
      agent_id: agent.agent_id,
      pending_messages_delivered: deliveredCount,
    });

    res.json({
      success: true,
      data: agent,
      message: `Agent registered successfully. ${deliveredCount} pending messages delivered.`,
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to register agent', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Unregister agent
 * DELETE /api/v1/agents/:agent_id
 */
app.delete('/api/v1/agents/:agent_id', async (req: Request, res: Response) => {
  try {
    const { agent_id } = req.params;

    await database.unregisterAgent(agent_id);

    res.json({
      success: true,
      message: 'Agent unregistered successfully',
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to unregister agent', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Update agent status
 * PUT /api/v1/agents/:agent_id/status
 */
app.put('/api/v1/agents/:agent_id/status', async (req: Request, res: Response) => {
  try {
    const { agent_id } = req.params;
    const { status } = req.body;

    if (!status || !['online', 'offline'].includes(status)) {
      return res.status(400).json({
        success: false,
        error: 'status must be "online" or "offline"',
      } as ApiResponse);
    }

    await database.updateAgentStatus(agent_id, status);

    // If agent came online, process pending messages
    if (status === 'online') {
      const deliveredCount = await messageRouter.processPendingMessages(agent_id);
      logger.info('Processed pending messages for agent', {
        agent_id,
        delivered_count: deliveredCount,
      });
    }

    res.json({
      success: true,
      message: 'Agent status updated successfully',
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to update agent status', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Discover agents
 * POST /api/v1/agents/discover
 */
app.post('/api/v1/agents/discover', async (req: Request, res: Response) => {
  try {
    const { capabilities, location, customer_id }: AgentDiscoveryRequest = req.body;

    const agents = await database.discoverAgents(
      capabilities,
      location as AgentLocation,
      customer_id
    );

    res.json({
      success: true,
      data: { agents },
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to discover agents', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Get agent by ID
 * GET /api/v1/agents/:agent_id
 */
app.get('/api/v1/agents/:agent_id', async (req: Request, res: Response) => {
  try {
    const { agent_id } = req.params;

    const agent = await database.getAgent(agent_id);

    if (!agent) {
      return res.status(404).json({
        success: false,
        error: 'Agent not found',
      } as ApiResponse);
    }

    res.json({
      success: true,
      data: agent,
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to get agent', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Route message to agent(s)
 * POST /api/v1/route
 */
app.post('/api/v1/route', async (req: Request, res: Response) => {
  try {
    const message: AgentMessage = req.body;

    if (!message.to || message.to.length === 0) {
      return res.status(400).json({
        success: false,
        error: 'message.to is required and must contain at least one agent ID',
      } as ApiResponse);
    }

    logger.info('Routing message', {
      message_id: message.id,
      sender: message.sender,
      to: message.to,
      intent: message.intent,
    });

    const results = await messageRouter.routeMessage(message);

    // Check if all messages were delivered
    const allDelivered = results.every((r) => r.delivered);
    const anyQueued = results.some((r) => r.queued);

    res.json({
      success: true,
      data: {
        results,
        all_delivered: allDelivered,
        any_queued: anyQueued,
      },
      message: allDelivered
        ? 'All messages delivered'
        : anyQueued
        ? 'Some messages queued for later delivery'
        : 'Some messages failed',
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to route message', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Get pending messages for an agent
 * GET /api/v1/agents/:agent_id/pending
 */
app.get('/api/v1/agents/:agent_id/pending', async (req: Request, res: Response) => {
  try {
    const { agent_id } = req.params;
    const limit = req.query.limit ? parseInt(req.query.limit as string) : 10;

    const messages = await database.getPendingMessages(agent_id, limit);

    res.json({
      success: true,
      data: { messages },
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to get pending messages', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Get router statistics
 * GET /api/v1/stats
 */
app.get('/api/v1/stats', async (req: Request, res: Response) => {
  try {
    const stats = await database.getStatistics();

    res.json({
      success: true,
      data: stats,
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to get statistics', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Start server
 */
async function start() {
  try {
    // Initialize database
    await database.initialize();

    // Start message processor
    messageRouter.startMessageProcessor(10000); // Process every 10 seconds

    // Start cleanup job (every hour)
    setInterval(async () => {
      try {
        const count = await database.cleanupDeliveredMessages(24);
        logger.info('Cleaned up delivered messages', { count });
      } catch (error: any) {
        logger.error('Failed to cleanup messages', { error: error.message });
      }
    }, 3600000); // 1 hour

    // Start Express server
    app.listen(config.port, () => {
      logger.info(`Agent Router started`, {
        port: config.port,
      });
    });
  } catch (error) {
    logger.error('Failed to start Agent Router', { error });
    process.exit(1);
  }
}

// Start the server
start();

