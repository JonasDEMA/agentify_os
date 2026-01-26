import axios, { AxiosInstance } from 'axios';
import logger from './logger';

const MONITORING_AGENT_URL = process.env.MONITORING_AGENT_URL || '';
const LOGGING_AGENT_URL = process.env.LOGGING_AGENT_URL || '';
const REMOTE_ACCESS_AGENT_URL = process.env.REMOTE_ACCESS_AGENT_URL || '';
const ENABLE_INFRASTRUCTURE_INTEGRATION = process.env.ENABLE_INFRASTRUCTURE_INTEGRATION === 'true';

/**
 * Infrastructure Integration
 * Integrates with Monitoring, Logging, and Remote Access agents
 */
export class InfrastructureIntegration {
  private monitoringClient: AxiosInstance | null = null;
  private loggingClient: AxiosInstance | null = null;
  private remoteAccessClient: AxiosInstance | null = null;

  constructor() {
    if (!ENABLE_INFRASTRUCTURE_INTEGRATION) {
      logger.info('Infrastructure integration disabled');
      return;
    }

    // Initialize monitoring client
    if (MONITORING_AGENT_URL) {
      this.monitoringClient = axios.create({
        baseURL: MONITORING_AGENT_URL,
        timeout: 5000,
        headers: { 'Content-Type': 'application/json' },
      });
      logger.info('Monitoring Agent integration enabled', { url: MONITORING_AGENT_URL });
    }

    // Initialize logging client
    if (LOGGING_AGENT_URL) {
      this.loggingClient = axios.create({
        baseURL: LOGGING_AGENT_URL,
        timeout: 5000,
        headers: { 'Content-Type': 'application/json' },
      });
      logger.info('Logging Agent integration enabled', { url: LOGGING_AGENT_URL });
    }

    // Initialize remote access client
    if (REMOTE_ACCESS_AGENT_URL) {
      this.remoteAccessClient = axios.create({
        baseURL: REMOTE_ACCESS_AGENT_URL,
        timeout: 5000,
        headers: { 'Content-Type': 'application/json' },
      });
      logger.info('Remote Access Agent integration enabled', { url: REMOTE_ACCESS_AGENT_URL });
    }
  }

  /**
   * Send metrics to Monitoring Agent
   */
  async sendMetrics(metricsData: any): Promise<void> {
    if (!this.monitoringClient) return;

    try {
      await this.monitoringClient.post('/agent/message', {
        type: 'REQUEST',
        sender: 'agent.evcc.controller',
        receiver: 'agent.monitoring',
        content: {
          tool: 'collect_metrics',
          parameters: {
            source: 'evcc_agent',
            metrics: metricsData,
          },
        },
      });
    } catch (error) {
      logger.warn('Failed to send metrics to Monitoring Agent', { error });
    }
  }

  /**
   * Send charging metrics
   */
  async sendChargingMetrics(loadpointId: number, metrics: {
    mode: string;
    power: number;
    current: number;
    energy: number;
    soc: number | null;
    phases: number;
  }): Promise<void> {
    await this.sendMetrics({
      type: 'charging',
      loadpoint_id: loadpointId,
      ...metrics,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Send optimization metrics
   */
  async sendOptimizationMetrics(loadpointId: number, optimization: {
    objective: string;
    decision: any;
    pv_power: number;
    grid_power: number;
  }): Promise<void> {
    await this.sendMetrics({
      type: 'optimization',
      loadpoint_id: loadpointId,
      ...optimization,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Send site metrics
   */
  async sendSiteMetrics(metrics: {
    grid_power: number;
    pv_power: number;
    battery_power: number;
    battery_soc: number | null;
    home_power: number;
  }): Promise<void> {
    await this.sendMetrics({
      type: 'site',
      ...metrics,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Send log to Logging Agent
   */
  async sendLog(logEntry: {
    level: string;
    message: string;
    metadata?: any;
  }): Promise<void> {
    if (!this.loggingClient) return;

    try {
      await this.loggingClient.post('/agent/message', {
        type: 'REQUEST',
        sender: 'agent.evcc.controller',
        receiver: 'agent.logging',
        content: {
          tool: 'log_event',
          parameters: {
            source: 'evcc_agent',
            level: logEntry.level,
            message: logEntry.message,
            metadata: logEntry.metadata,
            timestamp: new Date().toISOString(),
          },
        },
      });
    } catch (error) {
      logger.warn('Failed to send log to Logging Agent', { error });
    }
  }

  /**
   * Log charging action
   */
  async logChargingAction(action: string, loadpointId: number, details: any): Promise<void> {
    await this.sendLog({
      level: 'info',
      message: `Charging action: ${action}`,
      metadata: {
        action,
        loadpoint_id: loadpointId,
        ...details,
      },
    });
  }

  /**
   * Log optimization action
   */
  async logOptimizationAction(objective: string, loadpointId: number, result: any): Promise<void> {
    await this.sendLog({
      level: 'info',
      message: `Optimization: ${objective}`,
      metadata: {
        objective,
        loadpoint_id: loadpointId,
        ...result,
      },
    });
  }

  /**
   * Create alert rule in Monitoring Agent
   */
  async createAlert(alertRule: {
    name: string;
    condition: string;
    threshold: number;
    severity: string;
    message: string;
  }): Promise<void> {
    if (!this.monitoringClient) return;

    try {
      await this.monitoringClient.post('/agent/message', {
        type: 'REQUEST',
        sender: 'agent.evcc.controller',
        receiver: 'agent.monitoring',
        content: {
          tool: 'create_alert_rule',
          parameters: {
            source: 'evcc_agent',
            ...alertRule,
          },
        },
      });
    } catch (error) {
      logger.warn('Failed to create alert rule', { error });
    }
  }

  /**
   * Setup default alert rules
   */
  async setupDefaultAlerts(): Promise<void> {
    logger.info('Setting up default alert rules');

    // Alert for high grid power during charging
    await this.createAlert({
      name: 'High Grid Power During Charging',
      condition: 'grid_power > threshold',
      threshold: 10000,
      severity: 'warning',
      message: 'Grid power exceeds 10kW during EV charging',
    });

    // Alert for charging failure
    await this.createAlert({
      name: 'Charging Failure',
      condition: 'charging_error',
      threshold: 1,
      severity: 'critical',
      message: 'EV charging error detected',
    });

    // Alert for low battery SOC
    await this.createAlert({
      name: 'Low Home Battery SOC',
      condition: 'battery_soc < threshold',
      threshold: 10,
      severity: 'warning',
      message: 'Home battery SOC below 10%',
    });

    logger.info('Default alert rules created');
  }
}

export default InfrastructureIntegration;
