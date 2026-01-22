/**
 * Alert Engine - Evaluates alert rules and triggers alerts
 */

import axios from 'axios';
import logger from './logger';
import { database } from './database';
import {
  AlertRule,
  Alert,
  AlertStatus,
  MetricsSnapshot,
  ConditionOperator,
} from './types';

export class AlertEngine {
  private alertHistory: Map<string, { timestamp: number; value: number }[]> = new Map();

  /**
   * Evaluate all alert rules against a metrics snapshot
   */
  async evaluateRules(snapshot: MetricsSnapshot): Promise<void> {
    try {
      // Get all enabled alert rules for this customer
      const rules = await database.getAlertRules(snapshot.customer_id);
      const enabledRules = rules.filter(r => r.enabled);

      for (const rule of enabledRules) {
        // Check if rule applies to this source
        if (rule.source_type && rule.source_type !== snapshot.source_type) {
          continue;
        }
        if (rule.source_id && rule.source_id !== snapshot.source_id) {
          continue;
        }

        // Evaluate the rule
        const shouldAlert = await this.checkRule(rule, snapshot);

        if (shouldAlert) {
          await this.triggerAlert(rule, snapshot);
        }
      }
    } catch (error: any) {
      logger.error('Failed to evaluate alert rules', { error: error.message });
    }
  }

  /**
   * Check if an alert rule condition is met
   */
  async checkRule(rule: AlertRule, snapshot: MetricsSnapshot): Promise<boolean> {
    const { condition } = rule;
    const metricValue = this.getMetricValue(snapshot, condition.metric_name);

    if (metricValue === null) {
      return false;
    }

    // Check if condition is met
    const conditionMet = this.evaluateCondition(
      metricValue,
      condition.operator,
      condition.threshold
    );

    // If duration is specified, check if condition has persisted
    if (condition.duration_seconds && condition.duration_seconds > 0) {
      return this.checkDuration(rule.id, metricValue, conditionMet, condition.duration_seconds);
    }

    return conditionMet;
  }

  /**
   * Get metric value from snapshot
   */
  private getMetricValue(snapshot: MetricsSnapshot, metricName: string): number | null {
    const metricMap: Record<string, number> = {
      cpu_usage_percent: snapshot.cpu_usage_percent,
      memory_usage_percent: snapshot.memory_usage_percent,
      disk_usage_percent: snapshot.disk_usage_percent,
      memory_used_bytes: snapshot.memory_used_bytes,
      disk_used_bytes: snapshot.disk_used_bytes,
      network_rx_bytes: snapshot.network_rx_bytes,
      network_tx_bytes: snapshot.network_tx_bytes,
      uptime_seconds: snapshot.uptime_seconds,
      temperature: snapshot.temperature || 0,
    };

    return metricMap[metricName] ?? null;
  }

  /**
   * Evaluate condition operator
   */
  private evaluateCondition(value: number, operator: ConditionOperator, threshold: number): boolean {
    switch (operator) {
      case ConditionOperator.GT:
        return value > threshold;
      case ConditionOperator.GTE:
        return value >= threshold;
      case ConditionOperator.LT:
        return value < threshold;
      case ConditionOperator.LTE:
        return value <= threshold;
      case ConditionOperator.EQ:
        return value === threshold;
      case ConditionOperator.NEQ:
        return value !== threshold;
      default:
        return false;
    }
  }

  /**
   * Check if condition has persisted for the required duration
   */
  private checkDuration(
    ruleId: string,
    value: number,
    conditionMet: boolean,
    durationSeconds: number
  ): boolean {
    const now = Date.now();
    const history = this.alertHistory.get(ruleId) || [];

    if (conditionMet) {
      // Add to history
      history.push({ timestamp: now, value });
      this.alertHistory.set(ruleId, history);

      // Check if condition has persisted for duration
      const cutoff = now - durationSeconds * 1000;
      const persistentHistory = history.filter(h => h.timestamp >= cutoff);

      return persistentHistory.length > 0 && 
             persistentHistory.every(h => h.timestamp >= cutoff);
    } else {
      // Clear history if condition is not met
      this.alertHistory.delete(ruleId);
      return false;
    }
  }

  /**
   * Trigger an alert
   */
  async triggerAlert(rule: AlertRule, snapshot: MetricsSnapshot): Promise<Alert> {
    try {
      const metricValue = this.getMetricValue(snapshot, rule.condition.metric_name)!;

      // Check if there's already an active alert for this rule
      const existingAlerts = await database.getAlerts(snapshot.customer_id, AlertStatus.ACTIVE);
      const activeAlert = existingAlerts.find(a => 
        a.rule_id === rule.id && 
        a.source_id === snapshot.source_id &&
        a.status === AlertStatus.ACTIVE
      );

      if (activeAlert) {
        logger.debug('Alert already active for rule', { rule_id: rule.id });
        return activeAlert;
      }

      // Create new alert
      const alert: Omit<Alert, 'id'> = {
        rule_id: rule.id,
        customer_id: snapshot.customer_id,
        source_type: snapshot.source_type,
        source_id: snapshot.source_id,
        severity: rule.severity,
        status: AlertStatus.ACTIVE,
        title: rule.name,
        message: `${rule.condition.metric_name} is ${metricValue.toFixed(2)} (threshold: ${rule.condition.threshold})`,
        metric_value: metricValue,
        threshold: rule.condition.threshold,
        triggered_at: new Date().toISOString(),
      };

      const createdAlert = await database.createAlert(alert);

      logger.warn('Alert triggered', {
        alert_id: createdAlert.id,
        rule_name: rule.name,
        severity: rule.severity,
        source_id: snapshot.source_id,
      });

      // Send notifications
      await this.sendNotification(createdAlert, rule.channels);

      return createdAlert;
    } catch (error: any) {
      logger.error('Failed to trigger alert', { error: error.message });
      throw error;
    }
  }

  /**
   * Send alert notification to configured channels
   */
  async sendNotification(alert: Alert, channels: string[]): Promise<void> {
    for (const channel of channels) {
      try {
        if (channel.startsWith('http://') || channel.startsWith('https://')) {
          // Webhook notification
          await axios.post(channel, {
            alert_id: alert.id,
            severity: alert.severity,
            title: alert.title,
            message: alert.message,
            source_id: alert.source_id,
            triggered_at: alert.triggered_at,
          }, { timeout: 5000 });

          logger.info('Sent webhook notification', { channel, alert_id: alert.id });
        } else if (channel.startsWith('agent.')) {
          // Agent message notification
          // This would integrate with the Agent Router
          logger.info('Would send agent message notification', { channel, alert_id: alert.id });
        } else if (channel.includes('@')) {
          // Email notification (placeholder)
          logger.info('Would send email notification', { channel, alert_id: alert.id });
        } else {
          logger.warn('Unknown notification channel', { channel });
        }
      } catch (error: any) {
        logger.error('Failed to send notification', {
          channel,
          alert_id: alert.id,
          error: error.message,
        });
      }
    }
  }

  /**
   * Auto-resolve alerts when condition clears
   */
  async autoResolveAlerts(): Promise<void> {
    try {
      // Get all active alerts
      const { data: alerts } = await database['supabase']
        .from('alerts')
        .select('*, alert_rules(*)')
        .eq('status', AlertStatus.ACTIVE);

      if (!alerts) return;

      for (const alert of alerts) {
        const rule = alert.alert_rules;
        if (!rule) continue;

        // Get latest snapshot for this source
        const snapshot = await database.getLatestSnapshot(alert.source_id, alert.customer_id);
        if (!snapshot) continue;

        // Check if condition is still met
        const conditionMet = await this.checkRule(rule, snapshot);

        if (!conditionMet) {
          // Auto-resolve the alert
          await database.resolveAlert(alert.id);
          logger.info('Auto-resolved alert', { alert_id: alert.id });
        }
      }
    } catch (error: any) {
      logger.error('Failed to auto-resolve alerts', { error: error.message });
    }
  }
}

export const alertEngine = new AlertEngine();

