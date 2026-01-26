/**
 * Hosting Orchestrator Agent
 * Main entry point
 */

import express, { Request, Response } from 'express';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
import { RailwayDeployer } from './railway-deployer';
import { EdgeDeployer } from './edge-deployer';
import { Database } from './database';
import { logger } from './logger';
import {
  AgentMessage,
  MessageType,
  DeploymentRequest,
  DeploymentResponse,
  AddressRequest,
  AddressResponse,
  Config,
  EdgeDeploymentConfig,
} from './types';

// Load environment variables
dotenv.config();

// Configuration
const config: Config = {
  port: parseInt(process.env.PORT || '3000'),
  supabase_url: process.env.SUPABASE_URL || '',
  supabase_key: process.env.SUPABASE_KEY || '',
  railway_api_key: process.env.RAILWAY_API_KEY,
  railway_api_url: process.env.RAILWAY_API_URL || 'https://backboard.railway.app/graphql/v2',
  agent_id: 'agent.agentify.hosting-orchestrator',
  marketplace_url: process.env.MARKETPLACE_URL,
};

// Initialize services
const database = new Database(config.supabase_url, config.supabase_key);
const railwayDeployer = config.railway_api_key
  ? new RailwayDeployer(config.railway_api_key, config.railway_api_url)
  : null;
const edgeDeployer = new EdgeDeployer();

// Create Express app
const app = express();
app.use(express.json());

// Load manifest
const manifest = JSON.parse(
  fs.readFileSync(path.join(__dirname, '../manifest.json'), 'utf-8')
);

/**
 * Health check endpoint
 */
app.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'ok',
    agent_id: config.agent_id,
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
 * Agent message endpoint
 * Handles Agent Communication Protocol messages
 */
app.post('/agent/message', async (req: Request, res: Response) => {
  try {
    const message: AgentMessage = req.body;

    logger.info('Received agent message', {
      type: message.type,
      intent: message.intent,
      sender: message.sender,
    });

    // Route message based on intent
    let response: AgentMessage;

    switch (message.intent) {
      case 'deploy_to_railway':
        response = await handleRailwayDeployment(message);
        break;

      case 'deploy_to_edge':
        response = await handleEdgeDeployment(message);
        break;

      case 'get_address':
        response = await handleGetAddress(message);
        break;

      case 'stop_container':
        response = await handleStopContainer(message);
        break;

      case 'delete_container':
        response = await handleDeleteContainer(message);
        break;

      case 'health_check':
        response = await handleHealthCheck(message);
        break;

      default:
        response = createErrorResponse(message, `Unknown intent: ${message.intent}`);
    }

    res.json(response);
  } catch (error: any) {
    logger.error('Error handling agent message', { error });
    res.status(500).json({
      type: MessageType.FAILURE,
      sender: config.agent_id,
      to: [req.body.sender],
      intent: req.body.intent,
      payload: {
        error: error.message,
      },
    });
  }
});

/**
 * Handle Railway deployment request
 */
async function handleRailwayDeployment(message: AgentMessage): Promise<AgentMessage> {
  if (!railwayDeployer) {
    return createErrorResponse(message, 'Railway API key not configured');
  }

  const request: DeploymentRequest = message.payload as DeploymentRequest;

  try {
    // Deploy to Railway
    const result = await railwayDeployer.deploy({
      agent_id: request.agent_id,
      customer_id: request.customer_id,
      image: request.image,
      env: request.env,
      resources: request.resources,
    });

    // Create container record in database
    const container = await database.createContainer({
      container_id: result.service_id,
      agent_id: request.agent_id,
      customer_id: request.customer_id,
      image: request.image,
      address: result.url,
      health_url: `${result.url}/health`,
      status: 'deploying',
      health: 'unknown',
      target_type: 'railway',
      target_id: result.service_id,
    });

    const response: DeploymentResponse = {
      deployment_id: result.deployment_id,
      container_id: result.service_id,
      address: result.url,
      health_url: `${result.url}/health`,
      status: 'deploying',
    };

    return createSuccessResponse(message, response);
  } catch (error: any) {
    return createErrorResponse(message, error.message);
  }
}

/**
 * Handle edge deployment request
 */
async function handleEdgeDeployment(message: AgentMessage): Promise<AgentMessage> {
  const request: EdgeDeploymentConfig = message.payload as EdgeDeploymentConfig;

  if (!request.device_id) {
    return createErrorResponse(message, 'device_id is required for edge deployment');
  }

  try {
    // Get device info from database
    const device = await database.getDevice(request.device_id);

    if (!device) {
      return createErrorResponse(message, 'Device not found');
    }

    if (device.status !== 'online') {
      return createErrorResponse(message, `Device is ${device.status}`);
    }

    // Deploy to edge device
    const result = await edgeDeployer.deploy(request, device.tailscale_ip);

    // Create container record in database
    const container = await database.createContainer({
      container_id: result.container_id,
      agent_id: request.agent_id,
      customer_id: request.customer_id,
      image: request.image,
      address: result.address,
      health_url: `${result.address}/health`,
      status: 'running',
      health: 'unknown',
      target_type: 'edge',
      target_id: request.device_id,
    });

    const response: DeploymentResponse = {
      deployment_id: result.container_id,
      container_id: result.container_id,
      address: result.address,
      health_url: `${result.address}/health`,
      status: 'running',
    };

    return createSuccessResponse(message, response);
  } catch (error: any) {
    return createErrorResponse(message, error.message);
  }
}

/**
 * Handle get address request
 */
async function handleGetAddress(message: AgentMessage): Promise<AgentMessage> {
  const request: AddressRequest = message.payload as AddressRequest;

  try {
    const container = await database.getContainerByAgent(request.agent_id, request.customer_id);

    if (!container) {
      return createErrorResponse(message, 'Container not found');
    }

    const response: AddressResponse = {
      address: container.address,
      health: container.health,
      uptime: container.uptime,
    };

    return createSuccessResponse(message, response);
  } catch (error: any) {
    return createErrorResponse(message, error.message);
  }
}

/**
 * Handle stop container request
 */
async function handleStopContainer(message: AgentMessage): Promise<AgentMessage> {
  const { container_id } = message.payload;

  try {
    const container = await database.getContainer(container_id);

    if (!container) {
      return createErrorResponse(message, 'Container not found');
    }

    if (container.target_type === 'railway' && railwayDeployer) {
      await railwayDeployer.stop(container_id);
    } else if (container.target_type === 'edge' && container.target_id) {
      const device = await database.getDevice(container.target_id);
      if (!device) {
        return createErrorResponse(message, 'Device not found');
      }
      await edgeDeployer.stop(device.device_id, device.tailscale_ip, container_id);
    }

    await database.updateContainerStatus(container_id, 'stopped', 'unknown');

    return createSuccessResponse(message, { container_id, status: 'stopped' });
  } catch (error: any) {
    return createErrorResponse(message, error.message);
  }
}

/**
 * Handle delete container request
 */
async function handleDeleteContainer(message: AgentMessage): Promise<AgentMessage> {
  const { container_id } = message.payload;

  try {
    const container = await database.getContainer(container_id);

    if (!container) {
      return createErrorResponse(message, 'Container not found');
    }

    if (container.target_type === 'railway' && railwayDeployer) {
      await railwayDeployer.delete(container_id);
    } else if (container.target_type === 'edge' && container.target_id) {
      const device = await database.getDevice(container.target_id);
      if (!device) {
        return createErrorResponse(message, 'Device not found');
      }
      await edgeDeployer.delete(device.device_id, device.tailscale_ip, container_id);
    }

    await database.deleteContainer(container_id);

    return createSuccessResponse(message, { container_id, status: 'deleted' });
  } catch (error: any) {
    return createErrorResponse(message, error.message);
  }
}

/**
 * Handle health check request
 */
async function handleHealthCheck(message: AgentMessage): Promise<AgentMessage> {
  const { container_id } = message.payload;

  try {
    const container = await database.getContainer(container_id);

    if (!container) {
      return createErrorResponse(message, 'Container not found');
    }

    // Perform health check
    const startTime = Date.now();
    let isHealthy = false;

    if (container.target_type === 'railway' && railwayDeployer) {
      isHealthy = await railwayDeployer.healthCheck(container.address);
    } else if (container.target_type === 'edge') {
      isHealthy = await edgeDeployer.healthCheck(container.address);
    }

    const responseTime = Date.now() - startTime;

    // Record health check
    await database.recordHealthCheck(container_id, {
      status: isHealthy ? 'ok' : 'error',
      response_time: responseTime,
      checked_at: new Date(),
    });

    // Update container health
    const health = isHealthy ? 'healthy' : 'unhealthy';
    await database.updateContainerStatus(container_id, container.status, health);

    return createSuccessResponse(message, {
      container_id,
      health,
      response_time: responseTime,
    });
  } catch (error: any) {
    return createErrorResponse(message, error.message);
  }
}

/**
 * Create success response message
 */
function createSuccessResponse(request: AgentMessage, payload: any): AgentMessage {
  return {
    id: generateId(),
    ts: new Date().toISOString(),
    type: MessageType.INFORM,
    sender: config.agent_id,
    to: [request.sender],
    intent: `${request.intent}_complete`,
    payload,
  };
}

/**
 * Create error response message
 */
function createErrorResponse(request: AgentMessage, error: string): AgentMessage {
  return {
    id: generateId(),
    ts: new Date().toISOString(),
    type: MessageType.FAILURE,
    sender: config.agent_id,
    to: [request.sender],
    intent: request.intent,
    payload: { error },
  };
}

/**
 * Generate unique ID
 */
function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Start server
 */
async function start() {
  try {
    // Initialize database
    await database.initialize();

    // Start Express server
    app.listen(config.port, () => {
      logger.info(`Hosting Orchestrator started`, {
        port: config.port,
        agent_id: config.agent_id,
      });
    });
  } catch (error) {
    logger.error('Failed to start Hosting Orchestrator', { error });
    process.exit(1);
  }
}

// Start the server
start();


