/**
 * Metrics Collector - Collects metrics from containers and devices
 */

import Docker from 'dockerode';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import logger from './logger';
import { database } from './database';
import {
  CollectMetricsRequest,
  MetricsSnapshot,
  SourceType,
  Metric,
  MetricType,
} from './types';

export class MetricsCollector {
  private docker: Docker;

  constructor() {
    this.docker = new Docker();
  }

  /**
   * Collect metrics from a container
   */
  async collectFromContainer(request: CollectMetricsRequest): Promise<MetricsSnapshot> {
    try {
      const container = this.docker.getContainer(request.source_id);

      // Get container stats
      const stats = await container.stats({ stream: false });

      // Parse stats into MetricsSnapshot
      const snapshot = this.parseContainerStats(
        stats,
        request.source_id,
        request.customer_id
      );

      // Store snapshot in database
      await database.createMetricsSnapshot(snapshot);

      logger.info('Collected metrics from container', {
        container_id: request.source_id,
        cpu: snapshot.cpu_usage_percent,
        memory: snapshot.memory_usage_percent,
      });

      return snapshot;
    } catch (error: any) {
      logger.error('Failed to collect metrics from container', {
        container_id: request.source_id,
        error: error.message,
      });
      throw error;
    }
  }

  /**
   * Collect metrics from a device
   */
  async collectFromDevice(request: CollectMetricsRequest): Promise<MetricsSnapshot> {
    try {
      const deviceInfo = await database.getDeviceInfo(request.source_id);
      if (!deviceInfo) {
        throw new Error(`Device ${request.source_id} not found`);
      }

      if (deviceInfo.status !== 'online') {
        throw new Error(`Device ${request.source_id} is offline`);
      }

      // Fetch metrics from device via HTTP
      const response = await axios.get(
        `http://${deviceInfo.tailscale_ip}:3000/metrics`,
        { timeout: 10000 }
      );

      const snapshot: MetricsSnapshot = {
        timestamp: new Date().toISOString(),
        source_type: SourceType.DEVICE,
        source_id: request.source_id,
        customer_id: request.customer_id,
        ...response.data,
      };

      // Store snapshot in database
      await database.createMetricsSnapshot(snapshot);

      logger.info('Collected metrics from device', {
        device_id: request.source_id,
        cpu: snapshot.cpu_usage_percent,
        memory: snapshot.memory_usage_percent,
      });

      return snapshot;
    } catch (error: any) {
      logger.error('Failed to collect metrics from device', {
        device_id: request.source_id,
        error: error.message,
      });
      throw error;
    }
  }

  /**
   * Parse Docker container stats into MetricsSnapshot
   */
  private parseContainerStats(
    stats: any,
    sourceId: string,
    customerId: string
  ): MetricsSnapshot {
    // Calculate CPU usage
    const cpuDelta = stats.cpu_stats.cpu_usage.total_usage - 
                     stats.precpu_stats.cpu_usage.total_usage;
    const systemDelta = stats.cpu_stats.system_cpu_usage - 
                        stats.precpu_stats.system_cpu_usage;
    const cpuCount = stats.cpu_stats.online_cpus || 1;
    const cpuUsagePercent = (cpuDelta / systemDelta) * cpuCount * 100;

    // Calculate memory usage
    const memoryUsed = stats.memory_stats.usage || 0;
    const memoryLimit = stats.memory_stats.limit || 1;
    const memoryUsagePercent = (memoryUsed / memoryLimit) * 100;

    // Network stats
    let networkRx = 0;
    let networkTx = 0;
    if (stats.networks) {
      Object.values(stats.networks).forEach((net: any) => {
        networkRx += net.rx_bytes || 0;
        networkTx += net.tx_bytes || 0;
      });
    }

    // Disk stats (simplified - would need more detailed implementation)
    const diskUsagePercent = 0; // Placeholder
    const diskUsedBytes = 0;
    const diskTotalBytes = 0;

    return {
      timestamp: new Date().toISOString(),
      source_type: SourceType.CONTAINER,
      source_id: sourceId,
      customer_id: customerId,
      cpu_usage_percent: Math.min(100, Math.max(0, cpuUsagePercent)),
      memory_usage_percent: Math.min(100, Math.max(0, memoryUsagePercent)),
      memory_used_bytes: memoryUsed,
      memory_total_bytes: memoryLimit,
      disk_usage_percent: diskUsagePercent,
      disk_used_bytes: diskUsedBytes,
      disk_total_bytes: diskTotalBytes,
      network_rx_bytes: networkRx,
      network_tx_bytes: networkTx,
      uptime_seconds: 0, // Would need to calculate from container start time
    };
  }

  /**
   * Collect metrics for all containers/devices of a customer
   */
  async collectAll(customerId: string): Promise<void> {
    try {
      // Get all containers for customer
      const { data: containers } = await database['supabase']
        .from('containers')
        .select('*')
        .eq('customer_id', customerId)
        .eq('status', 'running');

      if (containers) {
        for (const container of containers) {
          try {
            await this.collectFromContainer({
              source_type: SourceType.CONTAINER,
              source_id: container.id,
              customer_id: customerId,
            });
          } catch (error: any) {
            logger.error('Failed to collect from container', {
              container_id: container.id,
              error: error.message,
            });
          }
        }
      }

      // Get all devices for customer
      const { data: devices } = await database['supabase']
        .from('devices')
        .select('*')
        .eq('customer_id', customerId)
        .eq('status', 'online');

      if (devices) {
        for (const device of devices) {
          try {
            await this.collectFromDevice({
              source_type: SourceType.DEVICE,
              source_id: device.id,
              customer_id: customerId,
            });
          } catch (error: any) {
            logger.error('Failed to collect from device', {
              device_id: device.id,
              error: error.message,
            });
          }
        }
      }

      logger.info('Collected metrics for all sources', { customer_id: customerId });
    } catch (error: any) {
      logger.error('Failed to collect all metrics', { error: error.message });
    }
  }
}

export const metricsCollector = new MetricsCollector();

