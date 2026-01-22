/**
 * Logging Agent - Main Server
 */

import express, { Request, Response } from 'express';
import dotenv from 'dotenv';
import { WebSocketServer, WebSocket } from 'ws';
import http from 'http';
import logger from './logger';
import { database } from './database';
import { logCollector } from './log-collector';
import {
  AgentMessage,
  MessageType,
  ApiResponse,
  CollectLogsRequest,
  SearchLogsRequest,
  StreamLogsRequest,
  SourceType,
  LogLevel,
  ExportFormat,
  ExportDestination,
} from './types';

dotenv.config();

const app = express();
app.use(express.json());

const config = {
  port: parseInt(process.env.PORT || '3004'),
  nodeEnv: process.env.NODE_ENV || 'development',
  logRetentionDays: parseInt(process.env.LOG_RETENTION_DAYS || '30'),
  logCleanupIntervalMs: parseInt(process.env.LOG_CLEANUP_INTERVAL_MS || '86400000'), // 24 hours
};

// ========== Agent Communication Protocol ==========

/**
 * Handle agent messages
 * POST /agent/message
 */
app.post('/agent/message', async (req: Request, res: Response) => {
  try {
    const message: AgentMessage = req.body;

    logger.info('Received agent message', {
      intent: message.intent,
      sender: message.sender,
    });

    let response: AgentMessage;

    switch (message.intent) {
      case 'collect_logs':
        response = await handleCollectLogs(message);
        break;

      case 'search_logs':
        response = await handleSearchLogs(message);
        break;

      case 'stream_logs':
        response = await handleStreamLogs(message);
        break;

      case 'export_logs':
        response = await handleExportLogs(message);
        break;

      case 'get_stats':
        response = await handleGetStats(message);
        break;

      default:
        response = {
          id: `msg-${Date.now()}`,
          ts: new Date().toISOString(),
          type: MessageType.REFUSE,
          sender: 'agent.agentify.logging',
          to: [message.sender],
          intent: message.intent,
          payload: {
            error: `Unknown intent: ${message.intent}`,
          },
        };
    }

    res.json(response);
  } catch (error: any) {
    logger.error('Error handling agent message', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

// ========== Intent Handlers ==========

async function handleCollectLogs(message: AgentMessage): Promise<AgentMessage> {
  try {
    const request: CollectLogsRequest = message.payload;

    let logs;
    if (request.source_type === SourceType.CONTAINER) {
      logs = await logCollector.collectFromContainer(request);
    } else if (request.source_type === SourceType.DEVICE) {
      logs = await logCollector.collectFromDevice(request);
    } else {
      throw new Error(`Unsupported source type: ${request.source_type}`);
    }

    return {
      id: `msg-${Date.now()}`,
      ts: new Date().toISOString(),
      type: MessageType.INFORM,
      sender: 'agent.agentify.logging',
      to: [message.sender],
      intent: message.intent,
      payload: {
        logs,
        count: logs.length,
      },
    };
  } catch (error: any) {
    return {
      id: `msg-${Date.now()}`,
      ts: new Date().toISOString(),
      type: MessageType.FAILURE,
      sender: 'agent.agentify.logging',
      to: [message.sender],
      intent: message.intent,
      payload: {
        error: error.message,
      },
    };
  }
}

async function handleSearchLogs(message: AgentMessage): Promise<AgentMessage> {
  try {
    const request: SearchLogsRequest = message.payload;
    const result = await database.searchLogs(request);

    return {
      id: `msg-${Date.now()}`,
      ts: new Date().toISOString(),
      type: MessageType.INFORM,
      sender: 'agent.agentify.logging',
      to: [message.sender],
      intent: message.intent,
      payload: result,
    };
  } catch (error: any) {
    return {
      id: `msg-${Date.now()}`,
      ts: new Date().toISOString(),
      type: MessageType.FAILURE,
      sender: 'agent.agentify.logging',
      to: [message.sender],
      intent: message.intent,
      payload: {
        error: error.message,
      },
    };
  }
}

async function handleStreamLogs(message: AgentMessage): Promise<AgentMessage> {
  // Streaming is handled via WebSocket, not via agent messages
  return {
    id: `msg-${Date.now()}`,
    ts: new Date().toISOString(),
    type: MessageType.INFORM,
    sender: 'agent.agentify.logging',
    to: [message.sender],
    intent: message.intent,
    payload: {
      message: 'Use WebSocket endpoint /api/v1/logs/stream for real-time streaming',
    },
  };
}

async function handleExportLogs(message: AgentMessage): Promise<AgentMessage> {
  try {
    const { search, format, destination } = message.payload;

    // Create export job
    const job = await database.createExportJob({
      customer_id: search.customer_id,
      status: 'pending',
      format: format || ExportFormat.JSON,
      destination: destination || ExportDestination.LOCAL,
      log_count: 0,
    });

    // Start export in background (simplified - would use queue in production)
    processExportJob(job.id, search, format);

    return {
      id: `msg-${Date.now()}`,
      ts: new Date().toISOString(),
      type: MessageType.INFORM,
      sender: 'agent.agentify.logging',
      to: [message.sender],
      intent: message.intent,
      payload: {
        job_id: job.id,
        status: 'pending',
      },
    };
  } catch (error: any) {
    return {
      id: `msg-${Date.now()}`,
      ts: new Date().toISOString(),
      type: MessageType.FAILURE,
      sender: 'agent.agentify.logging',
      to: [message.sender],
      intent: message.intent,
      payload: {
        error: error.message,
      },
    };
  }
}

async function handleGetStats(message: AgentMessage): Promise<AgentMessage> {
  try {
    const { customer_id } = message.payload;
    const stats = await database.getStatistics(customer_id);

    return {
      id: `msg-${Date.now()}`,
      ts: new Date().toISOString(),
      type: MessageType.INFORM,
      sender: 'agent.agentify.logging',
      to: [message.sender],
      intent: message.intent,
      payload: stats,
    };
  } catch (error: any) {
    return {
      id: `msg-${Date.now()}`,
      ts: new Date().toISOString(),
      type: MessageType.FAILURE,
      sender: 'agent.agentify.logging',
      to: [message.sender],
      intent: message.intent,
      payload: {
        error: error.message,
      },
    };
  }
}

// ========== REST API Endpoints ==========

/**
 * Health check
 * GET /health
 */
app.get('/health', (req: Request, res: Response) => {
  res.json({
    success: true,
    data: {
      status: 'healthy',
      service: 'logging-agent',
      version: '1.0.0',
      timestamp: new Date().toISOString(),
    },
  } as ApiResponse);
});

/**
 * Collect logs
 * POST /api/v1/logs/collect
 */
app.post('/api/v1/logs/collect', async (req: Request, res: Response) => {
  try {
    const request: CollectLogsRequest = req.body;

    if (!request.source_type || !request.source_id || !request.customer_id) {
      return res.status(400).json({
        success: false,
        error: 'source_type, source_id, and customer_id are required',
      } as ApiResponse);
    }

    let logs;
    if (request.source_type === SourceType.CONTAINER) {
      logs = await logCollector.collectFromContainer(request);
    } else if (request.source_type === SourceType.DEVICE) {
      logs = await logCollector.collectFromDevice(request);
    } else {
      return res.status(400).json({
        success: false,
        error: `Unsupported source type: ${request.source_type}`,
      } as ApiResponse);
    }

    res.json({
      success: true,
      data: { logs, count: logs.length },
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to collect logs', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Search logs
 * POST /api/v1/logs/search
 */
app.post('/api/v1/logs/search', async (req: Request, res: Response) => {
  try {
    const request: SearchLogsRequest = req.body;

    if (!request.customer_id) {
      return res.status(400).json({
        success: false,
        error: 'customer_id is required',
      } as ApiResponse);
    }

    const result = await database.searchLogs(request);

    res.json({
      success: true,
      data: result,
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to search logs', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Export logs
 * POST /api/v1/logs/export
 */
app.post('/api/v1/logs/export', async (req: Request, res: Response) => {
  try {
    const { search, format, destination } = req.body;

    if (!search || !search.customer_id) {
      return res.status(400).json({
        success: false,
        error: 'search.customer_id is required',
      } as ApiResponse);
    }

    const job = await database.createExportJob({
      customer_id: search.customer_id,
      status: 'pending',
      format: format || ExportFormat.JSON,
      destination: destination || ExportDestination.LOCAL,
      log_count: 0,
    });

    // Start export in background
    processExportJob(job.id, search, format);

    res.json({
      success: true,
      data: job,
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to create export job', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Get export job status
 * GET /api/v1/logs/export/:job_id
 */
app.get('/api/v1/logs/export/:job_id', async (req: Request, res: Response) => {
  try {
    const { job_id } = req.params;

    const job = await database.getExportJob(job_id);

    if (!job) {
      return res.status(404).json({
        success: false,
        error: 'Export job not found',
      } as ApiResponse);
    }

    res.json({
      success: true,
      data: job,
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to get export job', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Get retention policy
 * GET /api/v1/retention-policies/:customer_id
 */
app.get('/api/v1/retention-policies/:customer_id', async (req: Request, res: Response) => {
  try {
    const { customer_id } = req.params;

    const policy = await database.getRetentionPolicy(customer_id);

    res.json({
      success: true,
      data: policy,
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to get retention policy', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Create retention policy
 * POST /api/v1/retention-policies
 */
app.post('/api/v1/retention-policies', async (req: Request, res: Response) => {
  try {
    const policy = await database.createRetentionPolicy(req.body);

    res.json({
      success: true,
      data: policy,
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to create retention policy', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Get statistics
 * GET /api/v1/stats/:customer_id
 */
app.get('/api/v1/stats/:customer_id', async (req: Request, res: Response) => {
  try {
    const { customer_id } = req.params;

    const stats = await database.getStatistics(customer_id);

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

// ========== WebSocket Server for Log Streaming ==========

const server = http.createServer(app);
const wss = new WebSocketServer({ server, path: '/api/v1/logs/stream' });

wss.on('connection', (ws: WebSocket, req: http.IncomingMessage) => {
  logger.info('WebSocket client connected');

  ws.on('message', async (data: string) => {
    try {
      const request: StreamLogsRequest = JSON.parse(data.toString());

      logger.info('Starting log stream', {
        source_type: request.source_type,
        source_id: request.source_id,
      });

      // Start streaming logs
      const cleanup = await logCollector.streamLogs(request, (log) => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify(log));
        }
      });

      // Cleanup on disconnect
      ws.on('close', () => {
        logger.info('WebSocket client disconnected');
        cleanup();
      });
    } catch (error: any) {
      logger.error('Error in WebSocket stream', { error });
      ws.send(JSON.stringify({ error: error.message }));
    }
  });

  ws.on('error', (error) => {
    logger.error('WebSocket error', { error });
  });
});

// ========== Background Jobs ==========

/**
 * Process export job (simplified - would use queue in production)
 */
async function processExportJob(
  jobId: string,
  search: SearchLogsRequest,
  format: ExportFormat
): Promise<void> {
  try {
    await database.updateExportJob(jobId, { status: 'running' });

    const result = await database.searchLogs({
      ...search,
      limit: 10000, // Max export limit
    });

    // In production, this would write to S3/GCS/etc
    // For now, just mark as completed
    await database.updateExportJob(jobId, {
      status: 'completed',
      log_count: result.count,
      completed_at: new Date().toISOString(),
    });

    logger.info('Export job completed', { job_id: jobId, count: result.count });
  } catch (error: any) {
    logger.error('Export job failed', { job_id: jobId, error });
    await database.updateExportJob(jobId, {
      status: 'failed',
      error: error.message,
      completed_at: new Date().toISOString(),
    });
  }
}

/**
 * Cleanup old logs based on retention policy
 */
async function cleanupOldLogs(): Promise<void> {
  try {
    logger.info('Starting log cleanup job');

    // Get all customers (simplified - would paginate in production)
    // For now, use default retention policy
    const deletedCount = await database.deleteOldLogs(
      config.logRetentionDays,
      '*' // Would iterate through customers in production
    );

    logger.info('Log cleanup completed', { deleted_count: deletedCount });
  } catch (error: any) {
    logger.error('Log cleanup failed', { error });
  }
}

/**
 * Start server
 */
async function start() {
  try {
    // Initialize database
    await database.initialize();

    // Start log cleanup job
    setInterval(cleanupOldLogs, config.logCleanupIntervalMs);

    // Start HTTP + WebSocket server
    server.listen(config.port, () => {
      logger.info('Logging Agent started', {
        port: config.port,
        env: config.nodeEnv,
        retention_days: config.logRetentionDays,
      });
    });
  } catch (error) {
    logger.error('Failed to start Logging Agent', { error });
    process.exit(1);
  }
}

// Start the server
start();

