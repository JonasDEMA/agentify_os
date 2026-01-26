/**
 * Database client for Monitoring Agent
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js';
import logger from './logger';
import {
  Metric,
  MetricsSnapshot,
  HealthCheck,
  AlertRule,
  Alert,
  CreateAlertRuleRequest,
  AlertStatus,
  DashboardDataRequest,
  DashboardData,
  TimeSeriesDataPoint,
} from './types';

export class Database {
  private supabase: SupabaseClient;

  constructor() {
    const supabaseUrl = process.env.SUPABASE_URL!;
    const supabaseKey = process.env.SUPABASE_KEY!;

    if (!supabaseUrl || !supabaseKey) {
      throw new Error('SUPABASE_URL and SUPABASE_KEY must be set');
    }

    this.supabase = createClient(supabaseUrl, supabaseKey);
  }

  async initialize(): Promise<void> {
    logger.info('Database client initialized');
  }

  // ========== Metrics Management ==========

  async createMetric(metric: Omit<Metric, 'id'>): Promise<Metric> {
    const { data, error } = await this.supabase
      .from('metrics')
      .insert(metric)
      .select()
      .single();

    if (error) {
      logger.error('Failed to create metric', { error });
      throw new Error(`Failed to create metric: ${error.message}`);
    }

    return data;
  }

  async createMetrics(metrics: Omit<Metric, 'id'>[]): Promise<Metric[]> {
    const { data, error } = await this.supabase
      .from('metrics')
      .insert(metrics)
      .select();

    if (error) {
      logger.error('Failed to create metrics', { error });
      throw new Error(`Failed to create metrics: ${error.message}`);
    }

    return data;
  }

  async createMetricsSnapshot(snapshot: Omit<MetricsSnapshot, 'id'>): Promise<MetricsSnapshot> {
    const { data, error } = await this.supabase
      .from('metrics_snapshots')
      .insert(snapshot)
      .select()
      .single();

    if (error) {
      logger.error('Failed to create metrics snapshot', { error });
      throw new Error(`Failed to create metrics snapshot: ${error.message}`);
    }

    return data;
  }

  async getLatestSnapshot(sourceId: string, customerId: string): Promise<MetricsSnapshot | null> {
    const { data, error } = await this.supabase
      .from('metrics_snapshots')
      .select('*')
      .eq('source_id', sourceId)
      .eq('customer_id', customerId)
      .order('timestamp', { ascending: false })
      .limit(1)
      .single();

    if (error && error.code !== 'PGRST116') {
      logger.error('Failed to get latest snapshot', { error });
      throw new Error(`Failed to get latest snapshot: ${error.message}`);
    }

    return data;
  }

  async getMetrics(
    customerId: string,
    sourceId?: string,
    metricName?: string,
    startTime?: string,
    endTime?: string,
    limit: number = 1000
  ): Promise<Metric[]> {
    let query = this.supabase
      .from('metrics')
      .select('*')
      .eq('customer_id', customerId);

    if (sourceId) {
      query = query.eq('source_id', sourceId);
    }

    if (metricName) {
      query = query.eq('metric_name', metricName);
    }

    if (startTime) {
      query = query.gte('timestamp', startTime);
    }

    if (endTime) {
      query = query.lte('timestamp', endTime);
    }

    query = query.order('timestamp', { ascending: false }).limit(limit);

    const { data, error } = await query;

    if (error) {
      logger.error('Failed to get metrics', { error });
      throw new Error(`Failed to get metrics: ${error.message}`);
    }

    return data || [];
  }

  async deleteOldMetrics(retentionDays: number, customerId: string): Promise<number> {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - retentionDays);

    const { data, error } = await this.supabase
      .from('metrics')
      .delete()
      .eq('customer_id', customerId)
      .lt('timestamp', cutoffDate.toISOString())
      .select();

    if (error) {
      logger.error('Failed to delete old metrics', { error });
      throw new Error(`Failed to delete old metrics: ${error.message}`);
    }

    return data?.length || 0;
  }

  // ========== Health Check Management ==========

  async createHealthCheck(healthCheck: Omit<HealthCheck, 'id'>): Promise<HealthCheck> {
    const { data, error } = await this.supabase
      .from('health_checks')
      .insert(healthCheck)
      .select()
      .single();

    if (error) {
      logger.error('Failed to create health check', { error });
      throw new Error(`Failed to create health check: ${error.message}`);
    }

    return data;
  }

  async getLatestHealthCheck(sourceId: string, customerId: string): Promise<HealthCheck | null> {
    const { data, error } = await this.supabase
      .from('health_checks')
      .select('*')
      .eq('source_id', sourceId)
      .eq('customer_id', customerId)
      .order('timestamp', { ascending: false })
      .limit(1)
      .single();

    if (error && error.code !== 'PGRST116') {
      logger.error('Failed to get latest health check', { error });
      throw new Error(`Failed to get latest health check: ${error.message}`);
    }

    return data;
  }

  async getHealthCheckHistory(
    sourceId: string,
    customerId: string,
    limit: number = 100
  ): Promise<HealthCheck[]> {
    const { data, error } = await this.supabase
      .from('health_checks')
      .select('*')
      .eq('source_id', sourceId)
      .eq('customer_id', customerId)
      .order('timestamp', { ascending: false })
      .limit(limit);

    if (error) {
      logger.error('Failed to get health check history', { error });
      throw new Error(`Failed to get health check history: ${error.message}`);
    }

    return data || [];
  }

  // ========== Alert Rule Management ==========

  async createAlertRule(request: CreateAlertRuleRequest): Promise<AlertRule> {
    const rule = {
      ...request,
      enabled: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    const { data, error } = await this.supabase
      .from('alert_rules')
      .insert(rule)
      .select()
      .single();

    if (error) {
      logger.error('Failed to create alert rule', { error });
      throw new Error(`Failed to create alert rule: ${error.message}`);
    }

    return data;
  }

  async getAlertRules(customerId: string): Promise<AlertRule[]> {
    const { data, error } = await this.supabase
      .from('alert_rules')
      .select('*')
      .eq('customer_id', customerId)
      .order('created_at', { ascending: false });

    if (error) {
      logger.error('Failed to get alert rules', { error });
      throw new Error(`Failed to get alert rules: ${error.message}`);
    }

    return data || [];
  }

  async getAlertRule(ruleId: string): Promise<AlertRule | null> {
    const { data, error } = await this.supabase
      .from('alert_rules')
      .select('*')
      .eq('id', ruleId)
      .single();

    if (error && error.code !== 'PGRST116') {
      logger.error('Failed to get alert rule', { error });
      throw new Error(`Failed to get alert rule: ${error.message}`);
    }

    return data;
  }

  async updateAlertRule(ruleId: string, updates: Partial<AlertRule>): Promise<void> {
    const { error } = await this.supabase
      .from('alert_rules')
      .update({ ...updates, updated_at: new Date().toISOString() })
      .eq('id', ruleId);

    if (error) {
      logger.error('Failed to update alert rule', { error });
      throw new Error(`Failed to update alert rule: ${error.message}`);
    }
  }

  async deleteAlertRule(ruleId: string): Promise<void> {
    const { error } = await this.supabase
      .from('alert_rules')
      .delete()
      .eq('id', ruleId);

    if (error) {
      logger.error('Failed to delete alert rule', { error });
      throw new Error(`Failed to delete alert rule: ${error.message}`);
    }
  }

  // ========== Alert Management ==========

  async createAlert(alert: Omit<Alert, 'id'>): Promise<Alert> {
    const { data, error } = await this.supabase
      .from('alerts')
      .insert(alert)
      .select()
      .single();

    if (error) {
      logger.error('Failed to create alert', { error });
      throw new Error(`Failed to create alert: ${error.message}`);
    }

    return data;
  }

  async getAlerts(
    customerId: string,
    status?: AlertStatus,
    limit: number = 100
  ): Promise<Alert[]> {
    let query = this.supabase
      .from('alerts')
      .select('*')
      .eq('customer_id', customerId);

    if (status) {
      query = query.eq('status', status);
    }

    query = query.order('triggered_at', { ascending: false }).limit(limit);

    const { data, error } = await query;

    if (error) {
      logger.error('Failed to get alerts', { error });
      throw new Error(`Failed to get alerts: ${error.message}`);
    }

    return data || [];
  }

  async acknowledgeAlert(alertId: string, userId: string): Promise<void> {
    const { error } = await this.supabase
      .from('alerts')
      .update({
        status: AlertStatus.ACKNOWLEDGED,
        acknowledged_at: new Date().toISOString(),
        acknowledged_by: userId,
      })
      .eq('id', alertId);

    if (error) {
      logger.error('Failed to acknowledge alert', { error });
      throw new Error(`Failed to acknowledge alert: ${error.message}`);
    }
  }

  async resolveAlert(alertId: string): Promise<void> {
    const { error } = await this.supabase
      .from('alerts')
      .update({
        status: AlertStatus.RESOLVED,
        resolved_at: new Date().toISOString(),
      })
      .eq('id', alertId);

    if (error) {
      logger.error('Failed to resolve alert', { error });
      throw new Error(`Failed to resolve alert: ${error.message}`);
    }
  }

  // ========== Dashboard Data ==========

  async getDashboardData(request: DashboardDataRequest): Promise<DashboardData> {
    const { customer_id, source_type, source_id, time_range, metrics, aggregation } = request;

    // Get metrics snapshots for the time range
    let query = this.supabase
      .from('metrics_snapshots')
      .select('*')
      .eq('customer_id', customer_id)
      .gte('timestamp', time_range.start)
      .lte('timestamp', time_range.end)
      .order('timestamp', { ascending: true });

    if (source_type) {
      query = query.eq('source_type', source_type);
    }

    if (source_id) {
      query = query.eq('source_id', source_id);
    }

    const { data, error } = await query;

    if (error) {
      logger.error('Failed to get dashboard data', { error });
      throw new Error(`Failed to get dashboard data: ${error.message}`);
    }

    if (!data || data.length === 0) {
      return { metrics: {}, summary: {} };
    }

    // Build time series data
    const metricsData: Record<string, TimeSeriesDataPoint[]> = {};
    const summary: Record<string, number> = {};

    const metricNames = metrics || [
      'cpu_usage_percent',
      'memory_usage_percent',
      'disk_usage_percent',
    ];

    metricNames.forEach((metricName) => {
      metricsData[metricName] = data.map((snapshot: any) => ({
        timestamp: snapshot.timestamp,
        value: snapshot[metricName] || 0,
      }));

      // Calculate summary (average by default)
      const values = data.map((s: any) => s[metricName] || 0);
      const sum = values.reduce((a: number, b: number) => a + b, 0);
      summary[metricName] = values.length > 0 ? sum / values.length : 0;
    });

    return { metrics: metricsData, summary };
  }

  // ========== Container/Device Info ==========

  async getContainerInfo(containerId: string): Promise<any> {
    const { data, error } = await this.supabase
      .from('containers')
      .select('*')
      .eq('id', containerId)
      .single();

    if (error && error.code !== 'PGRST116') {
      logger.error('Failed to get container info', { error });
      throw new Error(`Failed to get container info: ${error.message}`);
    }

    return data;
  }

  async getDeviceInfo(deviceId: string): Promise<any> {
    const { data, error } = await this.supabase
      .from('devices')
      .select('*')
      .eq('id', deviceId)
      .single();

    if (error && error.code !== 'PGRST116') {
      logger.error('Failed to get device info', { error });
      throw new Error(`Failed to get device info: ${error.message}`);
    }

    return data;
  }

  // ========== Statistics ==========

  async getStatistics(customerId: string): Promise<any> {
    const [metricsCount, healthChecksCount, alertsCount, activeAlertsCount] = await Promise.all([
      this.getMetricsCount(customerId),
      this.getHealthChecksCount(customerId),
      this.getAlertsCount(customerId),
      this.getActiveAlertsCount(customerId),
    ]);

    return {
      metrics_count: metricsCount,
      health_checks_count: healthChecksCount,
      alerts_count: alertsCount,
      active_alerts_count: activeAlertsCount,
    };
  }

  private async getMetricsCount(customerId: string): Promise<number> {
    const { count, error } = await this.supabase
      .from('metrics')
      .select('*', { count: 'exact', head: true })
      .eq('customer_id', customerId);

    if (error) {
      logger.error('Failed to get metrics count', { error });
      return 0;
    }

    return count || 0;
  }

  private async getHealthChecksCount(customerId: string): Promise<number> {
    const { count, error } = await this.supabase
      .from('health_checks')
      .select('*', { count: 'exact', head: true })
      .eq('customer_id', customerId);

    if (error) {
      logger.error('Failed to get health checks count', { error });
      return 0;
    }

    return count || 0;
  }

  private async getAlertsCount(customerId: string): Promise<number> {
    const { count, error } = await this.supabase
      .from('alerts')
      .select('*', { count: 'exact', head: true })
      .eq('customer_id', customerId);

    if (error) {
      logger.error('Failed to get alerts count', { error });
      return 0;
    }

    return count || 0;
  }

  private async getActiveAlertsCount(customerId: string): Promise<number> {
    const { count, error } = await this.supabase
      .from('alerts')
      .select('*', { count: 'exact', head: true })
      .eq('customer_id', customerId)
      .eq('status', AlertStatus.ACTIVE);

    if (error) {
      logger.error('Failed to get active alerts count', { error });
      return 0;
    }

    return count || 0;
  }
}

export const database = new Database();

