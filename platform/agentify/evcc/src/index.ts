import express, { Request, Response } from 'express';
import fs from 'fs';
import path from 'path';
import logger from './logger';
import EVCCClient from './evcc-client';
import LoadpointController from './loadpoint-controller';
import SiteManager from './site-manager';
import VehicleManager from './vehicle-manager';
import ChargingOptimizer from './charging-optimizer';
import InfrastructureIntegration from './infrastructure-integration';

const PORT = parseInt(process.env.PORT || '3004', 10);
const EVCC_URL = process.env.EVCC_URL || 'http://localhost:7070';

// Initialize components
const evccClient = new EVCCClient(EVCC_URL);
const loadpointController = new LoadpointController(evccClient);
const siteManager = new SiteManager(evccClient);
const vehicleManager = new VehicleManager(evccClient);
const chargingOptimizer = new ChargingOptimizer(evccClient, loadpointController);
const infrastructure = new InfrastructureIntegration();

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
  res.json({ status: 'healthy', agent: manifest.agent_id });
});

/**
 * Manifest endpoint
 */
app.get('/manifest', (req: Request, res: Response) => {
  res.json(manifest);
});

/**
 * Agent Communication Protocol endpoint
 */
app.post('/agent/message', async (req: Request, res: Response) => {
  const message = req.body;
  logger.info('Received agent message', { message });

  try {
    // Validate message format
    if (!message.type || !message.sender || !message.content) {
      return res.status(400).json({
        type: 'FAILURE',
        sender: manifest.agent_id,
        receiver: message.sender,
        content: { error: 'Invalid message format' },
      });
    }

    // Handle REQUEST messages
    if (message.type === 'REQUEST') {
      const { tool, parameters } = message.content;

      let result;
      switch (tool) {
        case 'control_loadpoint':
          result = await handleControlLoadpoint(parameters);
          break;
        case 'get_system_status':
          result = await handleGetSystemStatus(parameters);
          break;
        case 'set_charging_plan':
          result = await handleSetChargingPlan(parameters);
          break;
        case 'manage_battery':
          result = await handleManageBattery(parameters);
          break;
        case 'optimize_charging':
          result = await handleOptimizeCharging(parameters);
          break;
        default:
          throw new Error(`Unknown tool: ${tool}`);
      }

      return res.json({
        type: 'DONE',
        sender: manifest.agent_id,
        receiver: message.sender,
        content: result,
      });
    }

    // Handle other message types
    return res.json({
      type: 'INFORM',
      sender: manifest.agent_id,
      receiver: message.sender,
      content: { message: 'Message received' },
    });
  } catch (error: any) {
    logger.error('Error handling agent message', { error });
    return res.status(500).json({
      type: 'FAILURE',
      sender: manifest.agent_id,
      receiver: message.sender,
      content: { error: error.message },
    });
  }
});

/**
 * Tool handlers
 */

async function handleControlLoadpoint(params: any) {
  const result = await loadpointController.controlLoadpoint(params);
  
  // Send metrics and logs
  const loadpoint = await loadpointController.getLoadpointStatus(params.loadpoint_id);
  await infrastructure.sendChargingMetrics(params.loadpoint_id, {
    mode: loadpoint.mode,
    power: loadpoint.chargePower,
    current: loadpoint.chargeCurrent,
    energy: loadpoint.chargedEnergy,
    soc: loadpoint.vehicleSoc,
    phases: loadpoint.phasesEnabled,
  });
  await infrastructure.logChargingAction('control_loadpoint', params.loadpoint_id, result);
  
  return result;
}

async function handleGetSystemStatus(params: any) {
  const siteStatus = await siteManager.getSiteStatus();
  const loadpoints = await loadpointController.getAllLoadpoints();
  
  // Send site metrics
  await infrastructure.sendSiteMetrics({
    grid_power: siteStatus.grid_power,
    pv_power: siteStatus.pv_power,
    battery_power: siteStatus.battery_power,
    battery_soc: siteStatus.battery_soc,
    home_power: siteStatus.home_power,
  });
  
  return {
    site: siteStatus,
    loadpoints,
  };
}

async function handleSetChargingPlan(params: any) {
  const result = await vehicleManager.setChargingPlan(params);
  await infrastructure.logChargingAction('set_charging_plan', params.loadpoint_id, result);
  return result;
}

async function handleManageBattery(params: any) {
  const result = await siteManager.manageBattery(params);
  await infrastructure.logChargingAction('manage_battery', 0, result);
  return result;
}

async function handleOptimizeCharging(params: any) {
  const result = await chargingOptimizer.optimizeCharging(params);

  // Send optimization metrics
  await infrastructure.sendOptimizationMetrics(params.loadpoint_id, {
    objective: result.objective,
    decision: result.decision,
    pv_power: result.metrics.current_pv_power,
    grid_power: result.metrics.current_grid_power,
  });
  await infrastructure.logOptimizationAction(result.objective, params.loadpoint_id, result);

  return result;
}

/**
 * Start server
 */
async function startServer() {
  try {
    // Setup default alerts
    await infrastructure.setupDefaultAlerts();

    // Start Express server
    app.listen(PORT, () => {
      logger.info(`EVCC Agent started on port ${PORT}`, {
        agent_id: manifest.agent_id,
        evcc_url: EVCC_URL,
      });
    });
  } catch (error) {
    logger.error('Failed to start server', { error });
    process.exit(1);
  }
}

// Handle graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  process.exit(0);
});

// Start the server
startServer();

