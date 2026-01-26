import express, { Request, Response } from 'express';
import dotenv from 'dotenv';
import { logger } from './logger';
import { EnergyApiClient } from './energy-api-client';
import { EVController } from './ev-controller';
import { FCRManager } from './fcr-manager';
import { PowerOptimizer } from './optimizer';
import { InfrastructureIntegration } from './infrastructure-integration';
import {
  AgentMessage,
  ControlEVChargingRequest,
  MonitorEnergyRequest,
  ManageFCRRequest,
  OptimizePowerRequest
} from './types';

// Load environment variables
dotenv.config();

const app = express();
const port = process.env.PORT || 3000;
const agentId = process.env.AGENT_ID || 'agent.energy.controller';

// Middleware
app.use(express.json());

// Initialize components
const energyApi = new EnergyApiClient();
const evController = new EVController(energyApi);
const fcrManager = new FCRManager(energyApi);
const powerOptimizer = new PowerOptimizer(energyApi);
const infrastructure = new InfrastructureIntegration();

// Setup infrastructure integration on startup
(async () => {
  try {
    await infrastructure.setupDefaultAlerts();
    logger.info('Infrastructure integration initialized');
  } catch (error: any) {
    logger.warn('Failed to initialize infrastructure integration', { error: error.message });
  }
})();

// Agent Communication Protocol Endpoint
app.post('/agent/message', async (req: Request, res: Response) => {
  const message: AgentMessage = req.body;
  logger.info('Received agent message', { type: message.type, sender: message.sender });

  try {
    let response: AgentMessage;

    if (message.type === 'REQUEST') {
      const tool = message.content.tool;
      const parameters = message.content.parameters;

      let result: any;

      switch (tool) {
        case 'control_ev_charging':
          result = await evController.controlEVCharging(parameters as ControlEVChargingRequest);

          // Send metrics and logs to infrastructure agents
          if (result.success) {
            const req = parameters as ControlEVChargingRequest;
            await infrastructure.sendChargingMetrics(req.loadpoint_id, {
              mode: req.mode,
              power: req.max_power || 0
            });
            await infrastructure.logChargingAction('control_ev_charging', req.loadpoint_id, {
              mode: req.mode,
              max_power: req.max_power,
              enable_power_tracking: req.enable_power_tracking
            });
          }
          break;

        case 'monitor_energy':
          result = await evController.monitorEnergy(parameters as MonitorEnergyRequest);

          // Send energy metrics to infrastructure agents
          if (result.success && result.data) {
            const req = parameters as MonitorEnergyRequest;
            await infrastructure.sendChargingMetrics(req.loadpoint_id, {
              mode: result.data.loadpoint?.mode || 'unknown',
              power: result.data.loadpoint?.chargePower || 0,
              energy: result.data.meter?.energy,
              soc: result.data.loadpoint?.vehicleSoc,
              gridFrequency: result.data.grid?.frequency
            });
          }
          break;

        case 'manage_fcr':
          result = await fcrManager.manageFCR(parameters as ManageFCRRequest);

          // Log FCR actions
          if (result.success) {
            const req = parameters as ManageFCRRequest;
            await infrastructure.sendLog({
              level: 'info',
              message: `FCR action: ${req.action}`,
              metadata: { action: req.action, ...req },
              timestamp: new Date().toISOString()
            });
          }
          break;

        case 'optimize_power':
          result = await powerOptimizer.optimizePower(parameters as OptimizePowerRequest);

          // Send optimization metrics and logs
          if (result.success) {
            const req = parameters as OptimizePowerRequest;
            await infrastructure.sendOptimizationMetrics(req.loadpoint_id, {
              objective: req.objective,
              mode: result.optimized_mode || 'unknown',
              power: result.optimized_power || 0,
              estimatedSavings: result.estimated_savings,
              renewablePercentage: result.renewable_percentage
            });
            await infrastructure.logOptimizationAction(req.objective, req.loadpoint_id, result);
          }
          break;

        default:
          throw new Error(`Unknown tool: ${tool}`);
      }

      response = {
        type: 'CONFIRM',
        sender: agentId,
        receiver: message.sender,
        content: result,
        conversation_id: message.conversation_id,
        timestamp: new Date().toISOString()
      };

    } else if (message.type === 'DISCOVER') {
      // Respond with agent capabilities
      response = {
        type: 'INFORM',
        sender: agentId,
        receiver: message.sender,
        content: {
          agent_id: agentId,
          capabilities: [
            'ev_charging_control',
            'energy_metering',
            'grid_monitoring',
            'fcr_management',
            'power_optimization'
          ],
          tools: [
            'control_ev_charging',
            'monitor_energy',
            'manage_fcr',
            'optimize_power'
          ]
        },
        conversation_id: message.conversation_id,
        timestamp: new Date().toISOString()
      };

    } else {
      throw new Error(`Unsupported message type: ${message.type}`);
    }

    res.json(response);

  } catch (error: any) {
    logger.error('Error processing agent message', { error: error.message });

    const errorResponse: AgentMessage = {
      type: 'FAILURE',
      sender: agentId,
      receiver: message.sender,
      content: {
        error: error.message,
        stack: error.stack
      },
      conversation_id: message.conversation_id,
      timestamp: new Date().toISOString()
    };

    res.status(500).json(errorResponse);
  }
});

// Health check endpoint
app.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    agent_id: agentId,
    timestamp: new Date().toISOString()
  });
});

// REST API Endpoints (for direct access)

// Loadpoint endpoints
app.get('/api/loadpoints', async (req: Request, res: Response) => {
  try {
    const loadpoints = await energyApi.getLoadpoints();
    res.json({ success: true, data: loadpoints });
  } catch (error: any) {
    logger.error('Failed to get loadpoints', { error: error.message });
    res.status(500).json({ success: false, error: error.message });
  }
});

app.get('/api/loadpoints/:id', async (req: Request, res: Response) => {
  try {
    const id = parseInt(req.params.id);
    const loadpoint = await energyApi.getLoadpoint(id);
    res.json({ success: true, data: loadpoint });
  } catch (error: any) {
    logger.error('Failed to get loadpoint', { error: error.message });
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/loadpoints/:id/control', async (req: Request, res: Response) => {
  try {
    const id = parseInt(req.params.id);
    const request: ControlEVChargingRequest = {
      loadpoint_id: id,
      ...req.body
    };
    const result = await evController.controlEVCharging(request);
    res.json({ success: true, data: result });
  } catch (error: any) {
    logger.error('Failed to control loadpoint', { error: error.message });
    res.status(500).json({ success: false, error: error.message });
  }
});

// Start server
app.listen(port, () => {
  logger.info(`Energy Agent started on port ${port}`);
  logger.info(`Agent ID: ${agentId}`);
  logger.info(`Energy API: ${process.env.ENERGY_API_BASE_URL}`);
});

