import axios, { AxiosInstance } from 'axios';
import { logger } from './logger';
import { AgentMessage } from './types';

/**
 * Infrastructure Integration Module
 * 
 * Connects Energy Agent with infrastructure agents:
 * - Monitoring Agent: Metrics collection and alerting
 * - Logging Agent: Centralized logging and audit trails
 * - Remote Access Agent: Remote debugging and configuration
 */

interface MetricsData {
  source: string;
  source_id?: string;
  metrics: Record<string, any>;
  timestamp: string;
}

interface AlertRule {
  name: string;
  condition: string;
  threshold: number;
  severity: 'critical' | 'warning' | 'info';
  notification_channels: string[];
}

interface LogEntry {
  level: string;
  message: string;
  metadata?: Record<string, any>;
  timestamp: string;
}

export class InfrastructureIntegration {
  private monitoringAgentUrl: string;
  private loggingAgentUrl: string;
  private remoteAccessAgentUrl: string;
  private agentId: string;
  private customerId: string;
  private enabled: boolean;

  private monitoringClient?: AxiosInstance;
  private loggingClient?: AxiosInstance;
  private remoteAccessClient?: AxiosInstance;

  constructor() {
    this.monitoringAgentUrl = process.env.MONITORING_AGENT_URL || 'http://localhost:3001';
    this.loggingAgentUrl = process.env.LOGGING_AGENT_URL || 'http://localhost:3002';
    this.remoteAccessAgentUrl = process.env.REMOTE_ACCESS_AGENT_URL || 'http://localhost:3003';
    this.agentId = process.env.AGENT_ID || 'agent.energy.controller';
    this.customerId = process.env.CUSTOMER_ID || 'customer-001';
    this.enabled = process.env.ENABLE_INFRASTRUCTURE_INTEGRATION === 'true';

    if (this.enabled) {
      this.initializeClients();
      logger.info('Infrastructure integration enabled', {
        monitoring: this.monitoringAgentUrl,
        logging: this.loggingAgentUrl,
        remoteAccess: this.remoteAccessAgentUrl
      });
    } else {
      logger.info('Infrastructure integration disabled');
    }
  }

  private initializeClients(): void {
    this.monitoringClient = axios.create({
      baseURL: this.monitoringAgentUrl,
      timeout: 5000,
      headers: { 'Content-Type': 'application/json' }
    });

    this.loggingClient = axios.create({
      baseURL: this.loggingAgentUrl,
      timeout: 5000,
      headers: { 'Content-Type': 'application/json' }
    });

    this.remoteAccessClient = axios.create({
      baseURL: this.remoteAccessAgentUrl,
      timeout: 5000,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  // Monitoring Agent Integration

  async sendMetrics(metricsData: MetricsData): Promise<void> {
    if (!this.enabled || !this.monitoringClient) return;

    try {
      const message: AgentMessage = {
        type: 'REQUEST',
        sender: this.agentId,
        receiver: 'agent.agentify.monitoring',
        content: {
          tool: 'collect_metrics',
          parameters: {
            source: metricsData.source,
            source_id: metricsData.source_id,
            customer_id: this.customerId,
            metrics: metricsData.metrics
          }
        },
        timestamp: metricsData.timestamp
      };

      await this.monitoringClient.post('/agent/message', message);
      logger.debug('Sent metrics to Monitoring Agent', { source: metricsData.source });
    } catch (error: any) {
      logger.warn('Failed to send metrics to Monitoring Agent', { error: error.message });
    }
  }

  async createAlert(alertRule: AlertRule): Promise<void> {
    if (!this.enabled || !this.monitoringClient) return;

    try {
      const message: AgentMessage = {
        type: 'REQUEST',
        sender: this.agentId,
        receiver: 'agent.agentify.monitoring',
        content: {
          tool: 'create_alert',
          parameters: {
            customer_id: this.customerId,
            agent_id: this.agentId,
            ...alertRule
          }
        },
        timestamp: new Date().toISOString()
      };

      await this.monitoringClient.post('/agent/message', message);
      logger.info('Created alert rule', { name: alertRule.name });
    } catch (error: any) {
      logger.warn('Failed to create alert rule', { error: error.message });
    }
  }

  // Logging Agent Integration

  async sendLog(logEntry: LogEntry): Promise<void> {
    if (!this.enabled || !this.loggingClient) return;

    try {
      const message: AgentMessage = {
        type: 'REQUEST',
        sender: this.agentId,
        receiver: 'agent.agentify.logging',
        content: {
          tool: 'collect_logs',
          parameters: {
            agent_id: this.agentId,
            customer_id: this.customerId,
            logs: [logEntry]
          }
        },
        timestamp: logEntry.timestamp
      };

      await this.loggingClient.post('/agent/message', message);
    } catch (error: any) {
      // Don't log errors about logging to avoid infinite loops
    }
  }

  // Helper Methods for Common Integration Patterns

  /**
   * Send EV charging metrics to Monitoring Agent
   */
  async sendChargingMetrics(loadpointId: number, metrics: {
    mode: string;
    power: number;
    energy?: number;
    soc?: number;
    gridFrequency?: number;
  }): Promise<void> {
    await this.sendMetrics({
      source: 'energy-agent',
      source_id: `loadpoint-${loadpointId}`,
      metrics: {
        charging_mode: metrics.mode,
        power_w: metrics.power,
        energy_kwh: metrics.energy,
        soc_percent: metrics.soc,
        grid_frequency_hz: metrics.gridFrequency
      },
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Send optimization metrics to Monitoring Agent
   */
  async sendOptimizationMetrics(loadpointId: number, optimization: {
    objective: string;
    mode: string;
    power: number;
    estimatedSavings?: number;
    renewablePercentage?: number;
  }): Promise<void> {
    await this.sendMetrics({
      source: 'energy-agent',
      source_id: `optimization-${loadpointId}`,
      metrics: {
        optimization_objective: optimization.objective,
        optimized_mode: optimization.mode,
        optimized_power_w: optimization.power,
        estimated_savings_eur: optimization.estimatedSavings,
        renewable_percentage: optimization.renewablePercentage
      },
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Log charging action for audit trail
   */
  async logChargingAction(action: string, loadpointId: number, details: Record<string, any>): Promise<void> {
    await this.sendLog({
      level: 'info',
      message: `Charging action: ${action}`,
      metadata: {
        action,
        loadpoint_id: loadpointId,
        ...details
      },
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Log optimization action for audit trail
   */
  async logOptimizationAction(objective: string, loadpointId: number, result: Record<string, any>): Promise<void> {
    await this.sendLog({
      level: 'info',
      message: `Power optimization: ${objective}`,
      metadata: {
        objective,
        loadpoint_id: loadpointId,
        ...result
      },
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Log critical error for alerting
   */
  async logCriticalError(error: string, context: Record<string, any>): Promise<void> {
    await this.sendLog({
      level: 'error',
      message: error,
      metadata: {
        severity: 'critical',
        ...context
      },
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Setup default alert rules for Energy Agent
   */
  async setupDefaultAlerts(): Promise<void> {
    if (!this.enabled) return;

    logger.info('Setting up default alert rules...');

    // Alert: Power limit exceeded
    await this.createAlert({
      name: 'energy-power-limit-exceeded',
      condition: 'power_w > threshold',
      threshold: 22080, // MAX_POWER_LIMIT_W
      severity: 'critical',
      notification_channels: ['email', 'slack']
    });

    // Alert: Grid frequency out of range
    await this.createAlert({
      name: 'energy-grid-frequency-critical',
      condition: 'grid_frequency_hz < 49.8 OR grid_frequency_hz > 50.2',
      threshold: 0.2,
      severity: 'critical',
      notification_channels: ['email', 'slack', 'sms']
    });

    // Alert: Charging mode changed
    await this.createAlert({
      name: 'energy-charging-mode-changed',
      condition: 'charging_mode != previous_value',
      threshold: 0,
      severity: 'info',
      notification_channels: ['slack']
    });

    // Alert: Optimization executed
    await this.createAlert({
      name: 'energy-optimization-executed',
      condition: 'optimization_objective != null',
      threshold: 0,
      severity: 'info',
      notification_channels: ['slack']
    });

    logger.info('Default alert rules created');
  }
}
