/**
 * Monitoring Agent - Main Server
 */

import express, { Request, Response } from 'express';
import dotenv from 'dotenv';
import cron from 'node-cron';
import logger from './logger';
import { database } from './database';
import { metricsCollector } from './metrics-collector';
import { healthChecker } from './health-checker';
import { alertEngine } from './alert-engine';
import {
  AgentMessage,
  MessageType,
  CollectMetricsRequest,
  CheckHealthRequest,
  CreateAlertRuleRequest,
  DashboardDataRequest,
  ApiResponse,
  SourceType,
} from './types';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3005;

app.use(express.json());

// ========== Agent Communication Protocol ==========

/**
 * Agent Communication Protocol endpoint
 */
app.post('/agent/message', async (req: Request, res: Response) => {
  try {
    const message: AgentMessage = req.body;

    logger.info('Received agent message', {
      id: message.id,
      type: message.type,
      intent: message.intent,
      sender: message.sender,
    });

    let response: AgentMessage;

    switch (message.intent) {
      case 'collect_metrics':
        response = await handleCollectMetrics(message);
        break;
      case 'check_health':
        response = await handleCheckHealth(message);
        break;
      case 'create_alert':
        response = await handleCreateAlert(message);
        break;
      case 'get_dashboard_data':
        response = await handleGetDashboardData(message);
        break;
      case 'get_stats':
        response = await handleGetStats(message);
        break;
      default:
        response = {
          id: `response-${message.id}`,
          ts: new Date().toISOString(),
          type: MessageType.REFUSE,
          sender: 'agent.agentify.monitoring',
          to: [message.sender],
          intent: message.intent,
          payload: {
            error: `Unknown intent: ${message.intent}`,
          },
        };
    }

    res.json(response);
  } catch (error: any) {
    logger.error('Error handling agent message', { error: error.message });
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

// ========== Intent Handlers ==========

async function handleCollectMetrics(message: AgentMessage): Promise<AgentMessage> {
  try {
    const request: CollectMetricsRequest = message.payload;

    let snapshot;
    if (request.source_type === SourceType.CONTAINER) {
      snapshot = await metricsCollector.collectFromContainer(request);
    } else if (request.source_type === SourceType.DEVICE) {
      snapshot = await metricsCollector.collectFromDevice(request);
    } else {
      throw new Error(`Unsupported source type: ${request.source_type}`);
    }

    // Evaluate alert rules
    await alertEngine.evaluateRules(snapshot);

    return {
      id: `response-${message.id}`,
      ts: new Date().toISOString(),
      type: MessageType.INFORM,
      sender: 'agent.agentify.monitoring',
      to: [message.sender],
      intent: 'collect_metrics',
      payload: {
        snapshot,
      },
    };
  } catch (error: any) {
    return {
      id: `response-${message.id}`,
      ts: new Date().toISOString(),
      type: MessageType.FAILURE,
      sender: 'agent.agentify.monitoring',
      to: [message.sender],
      intent: 'collect_metrics',
      payload: {
        error: error.message,
      },
    };
  }
}

async function handleCheckHealth(message: AgentMessage): Promise<AgentMessage> {
  try {
    const request: CheckHealthRequest = message.payload;
    const healthCheck = await healthChecker.checkHealth(request);

    return {
      id: `response-${message.id}`,
      ts: new Date().toISOString(),
      type: MessageType.INFORM,
      sender: 'agent.agentify.monitoring',
      to: [message.sender],
      intent: 'check_health',
      payload: {
        health_check: healthCheck,
      },
    };
  } catch (error: any) {
    return {
      id: `response-${message.id}`,
      ts: new Date().toISOString(),
      type: MessageType.FAILURE,
      sender: 'agent.agentify.monitoring',
      to: [message.sender],
      intent: 'check_health',
      payload: {
        error: error.message,
      },
    };
  }
}

async function handleCreateAlert(message: AgentMessage): Promise<AgentMessage> {
  try {
    const request: CreateAlertRuleRequest = message.payload;
    const alertRule = await database.createAlertRule(request);

    return {
      id: `response-${message.id}`,
      ts: new Date().toISOString(),
      type: MessageType.CONFIRM,
      sender: 'agent.agentify.monitoring',
      to: [message.sender],
      intent: 'create_alert',
      payload: {
        alert_rule: alertRule,
      },
    };
  } catch (error: any) {
    return {
      id: `response-${message.id}`,
      ts: new Date().toISOString(),
      type: MessageType.FAILURE,
      sender: 'agent.agentify.monitoring',
      to: [message.sender],
      intent: 'create_alert',
      payload: {
        error: error.message,
      },
    };
  }
}

async function handleGetDashboardData(message: AgentMessage): Promise<AgentMessage> {
  try {
    const request: DashboardDataRequest = message.payload;
    const dashboardData = await database.getDashboardData(request);

    return {
      id: `response-${message.id}`,
      ts: new Date().toISOString(),
      type: MessageType.INFORM,
      sender: 'agent.agentify.monitoring',
      to: [message.sender],
      intent: 'get_dashboard_data',
      payload: {
        dashboard_data: dashboardData,
      },
    };
  } catch (error: any) {
    return {
      id: `response-${message.id}`,
      ts: new Date().toISOString(),
      type: MessageType.FAILURE,
      sender: 'agent.agentify.monitoring',
      to: [message.sender],
      intent: 'get_dashboard_data',
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
      id: `response-${message.id}`,
      ts: new Date().toISOString(),
      type: MessageType.INFORM,
      sender: 'agent.agentify.monitoring',
      to: [message.sender],
      intent: 'get_stats',
      payload: {
        stats,
      },
    };
  } catch (error: any) {
    return {
      id: `response-${message.id}`,
      ts: new Date().toISOString(),
      type: MessageType.FAILURE,
      sender: 'agent.agentify.monitoring',
      to: [message.sender],
      intent: 'get_stats',
      payload: {
        error: error.message,
      },
    };
  }
}

// ========== REST API Endpoints ==========

/**
 * Collect metrics from a source
 */
app.post('/api/v1/metrics/collect', async (req: Request, res: Response) => {
  try {
    const request: CollectMetricsRequest = req.body;

    let snapshot;
    if (request.source_type === SourceType.CONTAINER) {
      snapshot = await metricsCollector.collectFromContainer(request);
    } else if (request.source_type === SourceType.DEVICE) {
      snapshot = await metricsCollector.collectFromDevice(request);
    } else {
      throw new Error(`Unsupported source type: ${request.source_type}`);
    }

    // Evaluate alert rules
    await alertEngine.evaluateRules(snapshot);

    const response: ApiResponse = {
      success: true,
      data: snapshot,
    };

    res.json(response);
  } catch (error: any) {
    logger.error('Error collecting metrics', { error: error.message });
    const response: ApiResponse = {
      success: false,
      error: error.message,
    };
    res.status(500).json(response);
  }
});

/**
 * Get metrics for a source
 */
app.get('/api/v1/metrics/:source_id', async (req: Request, res: Response) => {
  try {
    const { source_id } = req.params;
    const { customer_id, metric_name, start_time, end_time, limit } = req.query;

    const metrics = await database.getMetrics(
      customer_id as string,
      source_id,
      metric_name as string,
      start_time as string,
      end_time as string,
      limit ? parseInt(limit as string) : undefined
    );

    const response: ApiResponse = {
      success: true,
      data: metrics,
    };

    res.json(response);
  } catch (error: any) {
    logger.error('Error getting metrics', { error: error.message });
    const response: ApiResponse = {
      success: false,
      error: error.message,
    };
    res.status(500).json(response);
  }
});

/**
 * Check health of a source
 */
app.post('/api/v1/health/check', async (req: Request, res: Response) => {
  try {
    const request: CheckHealthRequest = req.body;
    const healthCheck = await healthChecker.checkHealth(request);

    const response: ApiResponse = {
      success: true,
      data: healthCheck,
    };

    res.json(response);
  } catch (error: any) {
    logger.error('Error checking health', { error: error.message });
    const response: ApiResponse = {
      success: false,
      error: error.message,
    };
    res.status(500).json(response);
  }
});

/**
 * Get health status for a source
 */
app.get('/api/v1/health/:source_id', async (req: Request, res: Response) => {
  try {
    const { source_id } = req.params;
    const { customer_id } = req.query;

    const healthCheck = await database.getLatestHealthCheck(source_id, customer_id as string);

    const response: ApiResponse = {
      success: true,
      data: healthCheck,
    };

    res.json(response);
  } catch (error: any) {
    logger.error('Error getting health status', { error: error.message });
    const response: ApiResponse = {
      success: false,
      error: error.message,
    };
    res.status(500).json(response);
  }
});

/**
 * Create alert rule
 */
app.post('/api/v1/alerts/rules', async (req: Request, res: Response) => {
  try {
    const request: CreateAlertRuleRequest = req.body;
    const alertRule = await database.createAlertRule(request);

    const response: ApiResponse = {
      success: true,
      data: alertRule,
    };

    res.json(response);
  } catch (error: any) {
    logger.error('Error creating alert rule', { error: error.message });
    const response: ApiResponse = {
      success: false,
      error: error.message,
    };
    res.status(500).json(response);
  }
});

/**
 * Get alert rules
 */
app.get('/api/v1/alerts/rules', async (req: Request, res: Response) => {
  try {
    const { customer_id } = req.query;
    const rules = await database.getAlertRules(customer_id as string);

    const response: ApiResponse = {
      success: true,
      data: rules,
    };

    res.json(response);
  } catch (error: any) {
    logger.error('Error getting alert rules', { error: error.message });
    const response: ApiResponse = {
      success: false,
      error: error.message,
    };
    res.status(500).json(response);
  }
});

/**
 * Update alert rule
 */
app.put('/api/v1/alerts/rules/:rule_id', async (req: Request, res: Response) => {
  try {
    const { rule_id } = req.params;
    const updates = req.body;

    await database.updateAlertRule(rule_id, updates);

    const response: ApiResponse = {
      success: true,
      message: 'Alert rule updated successfully',
    };

    res.json(response);
  } catch (error: any) {
    logger.error('Error updating alert rule', { error: error.message });
    const response: ApiResponse = {
      success: false,
      error: error.message,
    };
    res.status(500).json(response);
  }
});

/**
 * Delete alert rule
 */
app.delete('/api/v1/alerts/rules/:rule_id', async (req: Request, res: Response) => {
  try {
    const { rule_id } = req.params;
    await database.deleteAlertRule(rule_id);

    const response: ApiResponse = {
      success: true,
      message: 'Alert rule deleted successfully',
    };

    res.json(response);
  } catch (error: any) {
    logger.error('Error deleting alert rule', { error: error.message });
    const response: ApiResponse = {
      success: false,
      error: error.message,
    };
    res.status(500).json(response);
  }
});

/**
 * Get alerts
 */
app.get('/api/v1/alerts', async (req: Request, res: Response) => {
  try {
    const { customer_id, status, limit } = req.query;

    const alerts = await database.getAlerts(
      customer_id as string,
      status as any,
      limit ? parseInt(limit as string) : undefined
    );

    const response: ApiResponse = {
      success: true,
      data: alerts,
    };

    res.json(response);
  } catch (error: any) {
    logger.error('Error getting alerts', { error: error.message });
    const response: ApiResponse = {
      success: false,
      error: error.message,
    };
    res.status(500).json(response);
  }
});

/**
 * Acknowledge alert
 */
app.post('/api/v1/alerts/:alert_id/acknowledge', async (req: Request, res: Response) => {
  try {
    const { alert_id } = req.params;
    const { user_id } = req.body;

    await database.acknowledgeAlert(alert_id, user_id);

    const response: ApiResponse = {
      success: true,
      message: 'Alert acknowledged successfully',
    };

    res.json(response);
  } catch (error: any) {
    logger.error('Error acknowledging alert', { error: error.message });
    const response: ApiResponse = {
      success: false,
      error: error.message,
    };
    res.status(500).json(response);
  }
});

/**
 * Resolve alert
 */
app.post('/api/v1/alerts/:alert_id/resolve', async (req: Request, res: Response) => {
  try {
    const { alert_id } = req.params;
    await database.resolveAlert(alert_id);

    const response: ApiResponse = {
      success: true,
      message: 'Alert resolved successfully',
    };

    res.json(response);
  } catch (error: any) {
    logger.error('Error resolving alert', { error: error.message });
    const response: ApiResponse = {
      success: false,
      error: error.message,
    };
    res.status(500).json(response);
  }
});

/**
 * Get dashboard data
 */
app.post('/api/v1/dashboard', async (req: Request, res: Response) => {
  try {
    const request: DashboardDataRequest = req.body;
    const dashboardData = await database.getDashboardData(request);

    const response: ApiResponse = {
      success: true,
      data: dashboardData,
    };

    res.json(response);
  } catch (error: any) {
    logger.error('Error getting dashboard data', { error: error.message });
    const response: ApiResponse = {
      success: false,
      error: error.message,
    };
    res.status(500).json(response);
  }
});

/**
 * Get statistics
 */
app.get('/api/v1/stats/:customer_id', async (req: Request, res: Response) => {
  try {
    const { customer_id } = req.params;
    const stats = await database.getStatistics(customer_id);

    const response: ApiResponse = {
      success: true,
      data: stats,
    };

    res.json(response);
  } catch (error: any) {
    logger.error('Error getting statistics', { error: error.message });
    const response: ApiResponse = {
      success: false,
      error: error.message,
    };
    res.status(500).json(response);
  }
});

/**
 * Health check endpoint
 */
app.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    service: 'monitoring-agent',
    timestamp: new Date().toISOString(),
  });
});

// ========== Background Jobs ==========

/**
 * Metrics collection job - runs every 1 minute
 */
cron.schedule('*/1 * * * *', async () => {
  logger.info('Running metrics collection job');
  try {
    // Get all customers (simplified - would need proper customer management)
    const { data: customers } = await database['supabase']
      .from('customers')
      .select('id');

    if (customers) {
      for (const customer of customers) {
        await metricsCollector.collectAll(customer.id);
      }
    }
  } catch (error: any) {
    logger.error('Metrics collection job failed', { error: error.message });
  }
});

/**
 * Health check job - runs every 5 minutes
 */
cron.schedule('*/5 * * * *', async () => {
  logger.info('Running health check job');
  try {
    const { data: containers } = await database['supabase']
      .from('containers')
      .select('*')
      .eq('status', 'running');

    if (containers) {
      for (const container of containers) {
        try {
          await healthChecker.checkContainer(container.id, container.customer_id);
        } catch (error: any) {
          logger.error('Health check failed', { container_id: container.id, error: error.message });
        }
      }
    }

    const { data: devices } = await database['supabase']
      .from('devices')
      .select('*')
      .eq('status', 'online');

    if (devices) {
      for (const device of devices) {
        try {
          await healthChecker.checkDevice(device.id, device.customer_id);
        } catch (error: any) {
          logger.error('Health check failed', { device_id: device.id, error: error.message });
        }
      }
    }
  } catch (error: any) {
    logger.error('Health check job failed', { error: error.message });
  }
});

/**
 * Alert evaluation job - runs every 30 seconds
 */
cron.schedule('*/30 * * * * *', async () => {
  logger.debug('Running alert evaluation job');
  try {
    await alertEngine.autoResolveAlerts();
  } catch (error: any) {
    logger.error('Alert evaluation job failed', { error: error.message });
  }
});

/**
 * Metrics cleanup job - runs daily at 2 AM
 */
cron.schedule('0 2 * * *', async () => {
  logger.info('Running metrics cleanup job');
  try {
    const retentionDays = parseInt(process.env.METRICS_RETENTION_DAYS || '30');
    const { data: customers } = await database['supabase']
      .from('customers')
      .select('id');

    if (customers) {
      for (const customer of customers) {
        const deleted = await database.deleteOldMetrics(retentionDays, customer.id);
        logger.info('Deleted old metrics', { customer_id: customer.id, count: deleted });
      }
    }
  } catch (error: any) {
    logger.error('Metrics cleanup job failed', { error: error.message });
  }
});

// ========== Server Startup ==========

async function start() {
  try {
    await database.initialize();

    app.listen(PORT, () => {
      logger.info(`Monitoring Agent listening on port ${PORT}`);
      logger.info('Agent ID: agent.agentify.monitoring');
      logger.info('Capabilities: metrics_collection, health_monitoring, alerting');
    });
  } catch (error: any) {
    logger.error('Failed to start server', { error: error.message });
    process.exit(1);
  }
}

start();

