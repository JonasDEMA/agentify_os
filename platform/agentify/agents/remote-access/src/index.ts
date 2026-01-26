/**
 * Remote Access Agent - Main Server
 * Provides secure SSH/VNC access to edge devices
 */

import express, { Request, Response } from 'express';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
import { logger } from './logger';
import { Database } from './database';
import { SessionManager } from './session-manager';
import {
  AgentMessage,
  MessageType,
  ApiResponse,
  CreateSessionRequest,
  SessionType,
  SessionStatus,
} from './types';

// Load environment variables
dotenv.config();

const app = express();
app.use(express.json());

// Configuration
const config = {
  port: parseInt(process.env.PORT || '3003'),
  nodeEnv: process.env.NODE_ENV || 'development',
};

// Initialize services
const database = new Database();
const sessionManager = new SessionManager(database);

// Load manifest
const manifest = JSON.parse(
  fs.readFileSync(path.join(__dirname, '../manifest.json'), 'utf-8')
);

/**
 * Health check endpoint
 */
app.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    service: 'remote-access-agent',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
  });
});

/**
 * Manifest endpoint
 */
app.get('/manifest', (req: Request, res: Response) => {
  res.json(manifest);
});

/**
 * Agent Communication Protocol endpoint
 * POST /agent/message
 */
app.post('/agent/message', async (req: Request, res: Response) => {
  try {
    const message: AgentMessage = req.body;

    logger.info('Received agent message', {
      message_id: message.id,
      sender: message.sender,
      intent: message.intent,
    });

    let response: AgentMessage;

    // Route based on intent
    switch (message.intent) {
      case 'create_ssh_session':
        response = await handleCreateSSHSession(message);
        break;

      case 'create_vnc_session':
        response = await handleCreateVNCSession(message);
        break;

      case 'list_sessions':
        response = await handleListSessions(message);
        break;

      case 'terminate_session':
        response = await handleTerminateSession(message);
        break;

      case 'get_session':
        response = await handleGetSession(message);
        break;

      default:
        response = {
          id: `msg-${Date.now()}`,
          ts: new Date().toISOString(),
          type: MessageType.REFUSE,
          sender: 'agent.agentify.remote-access',
          to: [message.sender],
          intent: message.intent,
          payload: {
            error: `Unknown intent: ${message.intent}`,
          },
        };
    }

    res.json(response);
  } catch (error: any) {
    logger.error('Failed to process agent message', { error: error.message });

    const errorResponse: AgentMessage = {
      id: `msg-${Date.now()}`,
      ts: new Date().toISOString(),
      type: MessageType.FAILURE,
      sender: 'agent.agentify.remote-access',
      to: [req.body.sender],
      intent: req.body.intent,
      payload: {
        error: error.message,
      },
    };

    res.status(500).json(errorResponse);
  }
});

/**
 * Handle create SSH session
 */
async function handleCreateSSHSession(message: AgentMessage): Promise<AgentMessage> {
  const { device_id, user_id, customer_id, duration_minutes, purpose, metadata } = message.payload;

  const request: CreateSessionRequest = {
    device_id,
    user_id,
    customer_id,
    type: SessionType.SSH,
    duration_minutes,
    purpose,
    metadata,
  };

  const session = await sessionManager.createSSHSession(request);

  return {
    id: `msg-${Date.now()}`,
    ts: new Date().toISOString(),
    type: MessageType.INFORM,
    sender: 'agent.agentify.remote-access',
    to: [message.sender],
    intent: message.intent,
    payload: {
      session_id: session.session_id,
      type: session.type,
      connection_info: session.connection_info,
      expires_at: session.expires_at,
    },
  };
}

/**
 * Handle create VNC session
 */
async function handleCreateVNCSession(message: AgentMessage): Promise<AgentMessage> {
  const { device_id, user_id, customer_id, duration_minutes, purpose, metadata } = message.payload;

  const request: CreateSessionRequest = {
    device_id,
    user_id,
    customer_id,
    type: SessionType.VNC,
    duration_minutes,
    purpose,
    metadata,
  };

  const session = await sessionManager.createVNCSession(request);

  return {
    id: `msg-${Date.now()}`,
    ts: new Date().toISOString(),
    type: MessageType.INFORM,
    sender: 'agent.agentify.remote-access',
    to: [message.sender],
    intent: message.intent,
    payload: {
      session_id: session.session_id,
      type: session.type,
      connection_info: session.connection_info,
      expires_at: session.expires_at,
    },
  };
}

/**
 * Handle list sessions
 */
async function handleListSessions(message: AgentMessage): Promise<AgentMessage> {
  const { user_id, device_id, customer_id, status } = message.payload;

  const sessions = await sessionManager.listSessions({
    user_id,
    device_id,
    customer_id,
    status,
  });

  return {
    id: `msg-${Date.now()}`,
    ts: new Date().toISOString(),
    type: MessageType.INFORM,
    sender: 'agent.agentify.remote-access',
    to: [message.sender],
    intent: message.intent,
    payload: {
      sessions,
      count: sessions.length,
    },
  };
}

/**
 * Handle get session
 */
async function handleGetSession(message: AgentMessage): Promise<AgentMessage> {
  const { session_id } = message.payload;

  const session = await sessionManager.getSession(session_id);

  if (!session) {
    return {
      id: `msg-${Date.now()}`,
      ts: new Date().toISOString(),
      type: MessageType.FAILURE,
      sender: 'agent.agentify.remote-access',
      to: [message.sender],
      intent: message.intent,
      payload: {
        error: `Session not found: ${session_id}`,
      },
    };
  }

  return {
    id: `msg-${Date.now()}`,
    ts: new Date().toISOString(),
    type: MessageType.INFORM,
    sender: 'agent.agentify.remote-access',
    to: [message.sender],
    intent: message.intent,
    payload: {
      session,
    },
  };
}

/**
 * Handle terminate session
 */
async function handleTerminateSession(message: AgentMessage): Promise<AgentMessage> {
  const { session_id, user_id } = message.payload;

  await sessionManager.terminateSession(session_id, user_id);

  return {
    id: `msg-${Date.now()}`,
    ts: new Date().toISOString(),
    type: MessageType.CONFIRM,
    sender: 'agent.agentify.remote-access',
    to: [message.sender],
    intent: message.intent,
    payload: {
      session_id,
      status: 'terminated',
    },
  };
}

/**
 * REST API Endpoints
 */

/**
 * Create SSH session
 * POST /api/v1/sessions/ssh
 */
app.post('/api/v1/sessions/ssh', async (req: Request, res: Response) => {
  try {
    const request: CreateSessionRequest = {
      ...req.body,
      type: SessionType.SSH,
    };

    const session = await sessionManager.createSSHSession(request);

    res.json({
      success: true,
      data: session,
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to create SSH session', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Create VNC session
 * POST /api/v1/sessions/vnc
 */
app.post('/api/v1/sessions/vnc', async (req: Request, res: Response) => {
  try {
    const request: CreateSessionRequest = {
      ...req.body,
      type: SessionType.VNC,
    };

    const session = await sessionManager.createVNCSession(request);

    res.json({
      success: true,
      data: session,
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to create VNC session', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * List sessions
 * GET /api/v1/sessions
 */
app.get('/api/v1/sessions', async (req: Request, res: Response) => {
  try {
    const filters = {
      user_id: req.query.user_id as string,
      device_id: req.query.device_id as string,
      customer_id: req.query.customer_id as string,
      status: req.query.status as SessionStatus,
    };

    const sessions = await sessionManager.listSessions(filters);

    res.json({
      success: true,
      data: { sessions, count: sessions.length },
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to list sessions', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Get session by ID
 * GET /api/v1/sessions/:session_id
 */
app.get('/api/v1/sessions/:session_id', async (req: Request, res: Response) => {
  try {
    const { session_id } = req.params;

    const session = await sessionManager.getSession(session_id);

    if (!session) {
      return res.status(404).json({
        success: false,
        error: 'Session not found',
      } as ApiResponse);
    }

    res.json({
      success: true,
      data: session,
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to get session', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Terminate session
 * DELETE /api/v1/sessions/:session_id
 */
app.delete('/api/v1/sessions/:session_id', async (req: Request, res: Response) => {
  try {
    const { session_id } = req.params;
    const { user_id } = req.body;

    if (!user_id) {
      return res.status(400).json({
        success: false,
        error: 'user_id is required',
      } as ApiResponse);
    }

    await sessionManager.terminateSession(session_id, user_id);

    res.json({
      success: true,
      message: 'Session terminated successfully',
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to terminate session', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Get audit logs
 * GET /api/v1/audit-logs
 */
app.get('/api/v1/audit-logs', async (req: Request, res: Response) => {
  try {
    const filters = {
      user_id: req.query.user_id as string,
      device_id: req.query.device_id as string,
      session_id: req.query.session_id as string,
      start_date: req.query.start_date as string,
      end_date: req.query.end_date as string,
      limit: req.query.limit ? parseInt(req.query.limit as string) : 100,
    };

    const logs = await database.getAuditLogs(filters);

    res.json({
      success: true,
      data: { logs, count: logs.length },
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to get audit logs', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Get statistics
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

    // Start session expiration job (every 60 seconds)
    sessionManager.startExpirationJob(60000);

    // Start Express server
    app.listen(config.port, () => {
      logger.info(`Remote Access Agent started`, {
        port: config.port,
        env: config.nodeEnv,
      });
    });
  } catch (error) {
    logger.error('Failed to start Remote Access Agent', { error });
    process.exit(1);
  }
}

// Start the server
start();

