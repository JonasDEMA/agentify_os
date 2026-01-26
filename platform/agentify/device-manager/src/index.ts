/**
 * Device Manager Service
 * Main entry point
 */

import express, { Request, Response } from 'express';
import dotenv from 'dotenv';
import { v4 as uuidv4 } from 'uuid';
import crypto from 'crypto';
import { TailscaleClient } from './tailscale-client';
import { Database } from './database';
import { logger } from './logger';
import {
  Config,
  ApiResponse,
  DeviceRegistration,
  DeviceListFilters,
  DeviceUpdateRequest,
  DeviceHeartbeat,
} from './types';

// Load environment variables
dotenv.config();

// Configuration
const config: Config = {
  port: parseInt(process.env.PORT || '3001'),
  supabase_url: process.env.SUPABASE_URL || '',
  supabase_key: process.env.SUPABASE_KEY || '',
  tailscale_api_key: process.env.TAILSCALE_API_KEY || '',
  tailscale_tailnet: process.env.TAILSCALE_TAILNET || '',
  tailscale_api_url: process.env.TAILSCALE_API_URL || 'https://api.tailscale.com',
  claim_token_expiry_hours: parseInt(process.env.CLAIM_TOKEN_EXPIRY_HOURS || '24'),
};

// Initialize services
const database = new Database(config.supabase_url, config.supabase_key);
const tailscaleClient = new TailscaleClient(
  config.tailscale_api_key,
  config.tailscale_tailnet,
  config.tailscale_api_url
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
    service: 'device-manager',
    timestamp: new Date().toISOString(),
  });
});

/**
 * Generate claim token
 * POST /api/v1/devices/claim-token
 */
app.post('/api/v1/devices/claim-token', async (req: Request, res: Response) => {
  try {
    const { customer_id } = req.body;

    if (!customer_id) {
      return res.status(400).json({
        success: false,
        error: 'customer_id is required',
      } as ApiResponse);
    }

    // Generate random token
    const token = crypto.randomBytes(32).toString('hex');

    // Calculate expiry
    const expiresAt = new Date();
    expiresAt.setHours(expiresAt.getHours() + config.claim_token_expiry_hours);

    // Create claim token in database
    const claimToken = await database.createClaimToken({
      token,
      customer_id,
      expires_at: expiresAt,
      claimed: false,
    });

    // Create Tailscale auth key
    const tailscaleAuthKey = await tailscaleClient.createAuthKey({
      reusable: false,
      ephemeral: false,
      preauthorized: true,
      tags: ['tag:agentify-edge', `tag:customer-${customer_id}`],
    });

    logger.info('Claim token generated', { customer_id, token });

    res.json({
      success: true,
      data: {
        claim_token: token,
        tailscale_auth_key: tailscaleAuthKey.key,
        expires_at: expiresAt.toISOString(),
        instructions: {
          step1: 'Install Tailscale on your device',
          step2: `Run: tailscale up --authkey=${tailscaleAuthKey.key}`,
          step3: 'Run the Agentify device registration script with the claim token',
        },
      },
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to generate claim token', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Register device
 * POST /api/v1/devices/register
 */
app.post('/api/v1/devices/register', async (req: Request, res: Response) => {
  try {
    const { claim_token, ...deviceInfo }: { claim_token: string } & DeviceRegistration = req.body;

    if (!claim_token) {
      return res.status(400).json({
        success: false,
        error: 'claim_token is required',
      } as ApiResponse);
    }

    // Validate claim token
    const claimTokenRecord = await database.getClaimToken(claim_token);

    if (!claimTokenRecord) {
      return res.status(404).json({
        success: false,
        error: 'Invalid claim token',
      } as ApiResponse);
    }

    if (claimTokenRecord.claimed) {
      return res.status(400).json({
        success: false,
        error: 'Claim token already used',
      } as ApiResponse);
    }

    if (new Date() > new Date(claimTokenRecord.expires_at)) {
      return res.status(400).json({
        success: false,
        error: 'Claim token expired',
      } as ApiResponse);
    }

    // Create device
    const device = await database.createDevice({
      device_id: deviceInfo.device_id,
      customer_id: claimTokenRecord.customer_id,
      name: deviceInfo.name,
      type: deviceInfo.type,
      status: 'online',
      tailscale_ip: deviceInfo.tailscale_ip,
      tailscale_hostname: deviceInfo.tailscale_hostname,
      tailscale_node_id: deviceInfo.tailscale_node_id,
      capabilities: deviceInfo.capabilities,
    });

    // Mark claim token as used
    await database.markClaimTokenUsed(claim_token, device.device_id);

    logger.info('Device registered', {
      device_id: device.device_id,
      customer_id: device.customer_id,
    });

    res.json({
      success: true,
      data: device,
      message: 'Device registered successfully',
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to register device', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Get device by ID
 * GET /api/v1/devices/:device_id
 */
app.get('/api/v1/devices/:device_id', async (req: Request, res: Response) => {
  try {
    const { device_id } = req.params;

    const device = await database.getDevice(device_id);

    if (!device) {
      return res.status(404).json({
        success: false,
        error: 'Device not found',
      } as ApiResponse);
    }

    res.json({
      success: true,
      data: device,
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to get device', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * List devices
 * GET /api/v1/devices
 */
app.get('/api/v1/devices', async (req: Request, res: Response) => {
  try {
    const filters: DeviceListFilters = {
      customer_id: req.query.customer_id as string,
      status: req.query.status as any,
      type: req.query.type as any,
      limit: req.query.limit ? parseInt(req.query.limit as string) : undefined,
      offset: req.query.offset ? parseInt(req.query.offset as string) : undefined,
    };

    const devices = await database.listDevices(filters);

    res.json({
      success: true,
      data: devices,
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to list devices', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Update device
 * PUT /api/v1/devices/:device_id
 */
app.put('/api/v1/devices/:device_id', async (req: Request, res: Response) => {
  try {
    const { device_id } = req.params;
    const updates: DeviceUpdateRequest = req.body;

    const device = await database.updateDevice(device_id, updates);

    res.json({
      success: true,
      data: device,
      message: 'Device updated successfully',
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to update device', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Update device status
 * PUT /api/v1/devices/:device_id/status
 */
app.put('/api/v1/devices/:device_id/status', async (req: Request, res: Response) => {
  try {
    const { device_id } = req.params;
    const { status } = req.body;

    if (!status) {
      return res.status(400).json({
        success: false,
        error: 'status is required',
      } as ApiResponse);
    }

    await database.updateDeviceStatus(device_id, status);

    res.json({
      success: true,
      message: 'Device status updated successfully',
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to update device status', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Delete device
 * DELETE /api/v1/devices/:device_id
 */
app.delete('/api/v1/devices/:device_id', async (req: Request, res: Response) => {
  try {
    const { device_id } = req.params;

    // Get device to check if it exists and get Tailscale info
    const device = await database.getDevice(device_id);

    if (!device) {
      return res.status(404).json({
        success: false,
        error: 'Device not found',
      } as ApiResponse);
    }

    // Delete from Tailscale if node ID exists
    if (device.tailscale_node_id) {
      try {
        await tailscaleClient.deleteDevice(device.tailscale_node_id);
      } catch (error) {
        logger.warn('Failed to delete device from Tailscale', { error, device_id });
        // Continue with database deletion even if Tailscale deletion fails
      }
    }

    // Delete from database
    await database.deleteDevice(device_id);

    res.json({
      success: true,
      message: 'Device deleted successfully',
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to delete device', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Device heartbeat
 * POST /api/v1/devices/:device_id/heartbeat
 */
app.post('/api/v1/devices/:device_id/heartbeat', async (req: Request, res: Response) => {
  try {
    const { device_id } = req.params;
    const { status, metrics } = req.body;

    const heartbeat: DeviceHeartbeat = {
      device_id,
      timestamp: new Date(),
      status: status || 'online',
      metrics,
    };

    await database.recordHeartbeat(heartbeat);

    res.json({
      success: true,
      message: 'Heartbeat recorded',
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to record heartbeat', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Get device heartbeats
 * GET /api/v1/devices/:device_id/heartbeats
 */
app.get('/api/v1/devices/:device_id/heartbeats', async (req: Request, res: Response) => {
  try {
    const { device_id } = req.params;
    const limit = req.query.limit ? parseInt(req.query.limit as string) : 10;

    const heartbeats = await database.getHeartbeats(device_id, limit);

    res.json({
      success: true,
      data: heartbeats,
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to get heartbeats', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Get Tailscale devices
 * GET /api/v1/tailscale/devices
 */
app.get('/api/v1/tailscale/devices', async (req: Request, res: Response) => {
  try {
    const devices = await tailscaleClient.listDevices();

    res.json({
      success: true,
      data: devices,
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to list Tailscale devices', { error });
    res.status(500).json({
      success: false,
      error: error.message,
    } as ApiResponse);
  }
});

/**
 * Get device statistics
 * GET /api/v1/devices/stats
 */
app.get('/api/v1/devices/stats', async (req: Request, res: Response) => {
  try {
    const { customer_id } = req.query;

    const onlineCount = await database.getOnlineDevicesCount(customer_id as string);
    const allDevices = await database.listDevices({
      customer_id: customer_id as string,
    });

    const stats = {
      total: allDevices.length,
      online: onlineCount,
      offline: allDevices.filter((d) => d.status === 'offline').length,
      claimed: allDevices.filter((d) => d.status !== 'unclaimed').length,
      unclaimed: allDevices.filter((d) => d.status === 'unclaimed').length,
      by_type: {
        raspberry_pi: allDevices.filter((d) => d.type === 'raspberry_pi').length,
        generic_linux: allDevices.filter((d) => d.type === 'generic_linux').length,
        other: allDevices.filter((d) => d.type === 'other').length,
      },
    };

    res.json({
      success: true,
      data: stats,
    } as ApiResponse);
  } catch (error: any) {
    logger.error('Failed to get device stats', { error });
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

    // Start Express server
    app.listen(config.port, () => {
      logger.info(`Device Manager started`, {
        port: config.port,
      });
    });
  } catch (error) {
    logger.error('Failed to start Device Manager', { error });
    process.exit(1);
  }
}

// Start the server
start();

