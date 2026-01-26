/**
 * Health Checker - Performs health checks on containers and devices
 */

import Docker from 'dockerode';
import axios from 'axios';
import logger from './logger';
import { database } from './database';
import {
  CheckHealthRequest,
  HealthCheck,
  HealthCheckResult,
  HealthStatus,
  SourceType,
  MetricsSnapshot,
} from './types';

export class HealthChecker {
  private docker: Docker;

  constructor() {
    this.docker = new Docker();
  }

  /**
   * Check health of a container
   */
  async checkContainer(containerId: string, customerId: string): Promise<HealthCheck> {
    try {
      const container = this.docker.getContainer(containerId);
      const info = await container.inspect();

      // Get latest metrics snapshot
      const snapshot = await database.getLatestSnapshot(containerId, customerId);

      const checks: HealthCheckResult[] = [];

      // Check if container is running
      checks.push({
        name: 'container_running',
        status: info.State.Running ? HealthStatus.HEALTHY : HealthStatus.UNHEALTHY,
        message: info.State.Running ? 'Container is running' : 'Container is not running',
      });

      // Check metrics if available
      if (snapshot) {
        checks.push(...this.runHealthChecks(snapshot));
      }

      // Calculate overall status and score
      const { status, score } = this.calculateOverallHealth(checks);

      const healthCheck: HealthCheck = {
        id: '', // Will be set by database
        timestamp: new Date().toISOString(),
        source_type: SourceType.CONTAINER,
        source_id: containerId,
        customer_id: customerId,
        status,
        checks,
        overall_score: score,
      };

      // Store health check
      const result = await database.createHealthCheck(healthCheck);

      logger.info('Health check completed for container', {
        container_id: containerId,
        status,
        score,
      });

      return result;
    } catch (error: any) {
      logger.error('Failed to check container health', {
        container_id: containerId,
        error: error.message,
      });
      throw error;
    }
  }

  /**
   * Check health of a device
   */
  async checkDevice(deviceId: string, customerId: string): Promise<HealthCheck> {
    try {
      const deviceInfo = await database.getDeviceInfo(deviceId);
      if (!deviceInfo) {
        throw new Error(`Device ${deviceId} not found`);
      }

      const checks: HealthCheckResult[] = [];

      // Check if device is online
      checks.push({
        name: 'device_online',
        status: deviceInfo.status === 'online' ? HealthStatus.HEALTHY : HealthStatus.UNHEALTHY,
        message: deviceInfo.status === 'online' ? 'Device is online' : 'Device is offline',
      });

      // Get latest metrics snapshot
      const snapshot = await database.getLatestSnapshot(deviceId, customerId);

      if (snapshot) {
        checks.push(...this.runHealthChecks(snapshot));

        // Check temperature (Raspberry Pi specific)
        if (snapshot.temperature !== undefined) {
          checks.push(this.checkTemperature(snapshot.temperature));
        }
      }

      // Calculate overall status and score
      const { status, score } = this.calculateOverallHealth(checks);

      const healthCheck: HealthCheck = {
        id: '',
        timestamp: new Date().toISOString(),
        source_type: SourceType.DEVICE,
        source_id: deviceId,
        customer_id: customerId,
        status,
        checks,
        overall_score: score,
      };

      // Store health check
      const result = await database.createHealthCheck(healthCheck);

      logger.info('Health check completed for device', {
        device_id: deviceId,
        status,
        score,
      });

      return result;
    } catch (error: any) {
      logger.error('Failed to check device health', {
        device_id: deviceId,
        error: error.message,
      });
      throw error;
    }
  }

  /**
   * Run health checks based on metrics snapshot
   */
  private runHealthChecks(snapshot: MetricsSnapshot): HealthCheckResult[] {
    const checks: HealthCheckResult[] = [];

    // CPU usage check
    checks.push(this.checkCpuUsage(snapshot.cpu_usage_percent));

    // Memory usage check
    checks.push(this.checkMemoryUsage(snapshot.memory_usage_percent));

    // Disk usage check
    checks.push(this.checkDiskUsage(snapshot.disk_usage_percent));

    return checks;
  }

  private checkCpuUsage(cpuPercent: number): HealthCheckResult {
    let status: HealthStatus;
    let message: string;

    if (cpuPercent < 80) {
      status = HealthStatus.HEALTHY;
      message = `CPU usage is normal (${cpuPercent.toFixed(1)}%)`;
    } else if (cpuPercent < 95) {
      status = HealthStatus.DEGRADED;
      message = `CPU usage is high (${cpuPercent.toFixed(1)}%)`;
    } else {
      status = HealthStatus.UNHEALTHY;
      message = `CPU usage is critical (${cpuPercent.toFixed(1)}%)`;
    }

    return {
      name: 'cpu_usage',
      status,
      message,
      value: cpuPercent,
      threshold: 80,
    };
  }

  private checkMemoryUsage(memoryPercent: number): HealthCheckResult {
    let status: HealthStatus;
    let message: string;

    if (memoryPercent < 80) {
      status = HealthStatus.HEALTHY;
      message = `Memory usage is normal (${memoryPercent.toFixed(1)}%)`;
    } else if (memoryPercent < 95) {
      status = HealthStatus.DEGRADED;
      message = `Memory usage is high (${memoryPercent.toFixed(1)}%)`;
    } else {
      status = HealthStatus.UNHEALTHY;
      message = `Memory usage is critical (${memoryPercent.toFixed(1)}%)`;
    }

    return {
      name: 'memory_usage',
      status,
      message,
      value: memoryPercent,
      threshold: 80,
    };
  }

  private checkDiskUsage(diskPercent: number): HealthCheckResult {
    let status: HealthStatus;
    let message: string;

    if (diskPercent < 80) {
      status = HealthStatus.HEALTHY;
      message = `Disk usage is normal (${diskPercent.toFixed(1)}%)`;
    } else if (diskPercent < 90) {
      status = HealthStatus.DEGRADED;
      message = `Disk usage is high (${diskPercent.toFixed(1)}%)`;
    } else {
      status = HealthStatus.UNHEALTHY;
      message = `Disk usage is critical (${diskPercent.toFixed(1)}%)`;
    }

    return {
      name: 'disk_usage',
      status,
      message,
      value: diskPercent,
      threshold: 80,
    };
  }

  private checkTemperature(temperature: number): HealthCheckResult {
    let status: HealthStatus;
    let message: string;

    if (temperature < 70) {
      status = HealthStatus.HEALTHY;
      message = `Temperature is normal (${temperature.toFixed(1)}°C)`;
    } else if (temperature < 80) {
      status = HealthStatus.DEGRADED;
      message = `Temperature is high (${temperature.toFixed(1)}°C)`;
    } else {
      status = HealthStatus.UNHEALTHY;
      message = `Temperature is critical (${temperature.toFixed(1)}°C)`;
    }

    return {
      name: 'temperature',
      status,
      message,
      value: temperature,
      threshold: 70,
    };
  }

  /**
   * Calculate overall health status and score
   */
  private calculateOverallHealth(checks: HealthCheckResult[]): { status: HealthStatus; score: number } {
    if (checks.length === 0) {
      return { status: HealthStatus.UNKNOWN, score: 0 };
    }

    const statusScores = {
      [HealthStatus.HEALTHY]: 100,
      [HealthStatus.DEGRADED]: 50,
      [HealthStatus.UNHEALTHY]: 0,
      [HealthStatus.UNKNOWN]: 0,
    };

    // Calculate average score
    const totalScore = checks.reduce((sum, check) => sum + statusScores[check.status], 0);
    const score = totalScore / checks.length;

    // Determine overall status
    let status: HealthStatus;
    if (checks.some(c => c.status === HealthStatus.UNHEALTHY)) {
      status = HealthStatus.UNHEALTHY;
    } else if (checks.some(c => c.status === HealthStatus.DEGRADED)) {
      status = HealthStatus.DEGRADED;
    } else if (checks.every(c => c.status === HealthStatus.HEALTHY)) {
      status = HealthStatus.HEALTHY;
    } else {
      status = HealthStatus.UNKNOWN;
    }

    return { status, score };
  }

  /**
   * Check health based on request
   */
  async checkHealth(request: CheckHealthRequest): Promise<HealthCheck> {
    if (request.source_type === SourceType.CONTAINER) {
      return this.checkContainer(request.source_id, request.customer_id);
    } else if (request.source_type === SourceType.DEVICE) {
      return this.checkDevice(request.source_id, request.customer_id);
    } else {
      throw new Error(`Unsupported source type: ${request.source_type}`);
    }
  }
}

export const healthChecker = new HealthChecker();

