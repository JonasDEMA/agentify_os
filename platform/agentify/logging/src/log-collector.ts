/**
 * Log Collector - Collects logs from containers and devices
 */

import Docker from 'dockerode';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import logger from './logger';
import { database } from './database';
import {
  CollectLogsRequest,
  LogEntry,
  LogLevel,
  SourceType,
  StreamLogsRequest,
} from './types';

export class LogCollector {
  private docker: Docker;

  constructor() {
    this.docker = new Docker();
  }

  /**
   * Collect logs from a container
   */
  async collectFromContainer(request: CollectLogsRequest): Promise<LogEntry[]> {
    try {
      const container = this.docker.getContainer(request.source_id);

      // Get container info
      const containerInfo = await database.getContainerInfo(request.source_id);
      if (!containerInfo) {
        throw new Error(`Container ${request.source_id} not found`);
      }

      // Build log options
      const logOptions: any = {
        stdout: true,
        stderr: true,
        timestamps: true,
      };

      if (request.since) {
        logOptions.since = Math.floor(new Date(request.since).getTime() / 1000);
      }

      if (request.until) {
        logOptions.until = Math.floor(new Date(request.until).getTime() / 1000);
      }

      if (request.tail) {
        logOptions.tail = request.tail;
      }

      // Get logs from Docker
      const logStream = await container.logs(logOptions);
      const logLines = logStream.toString('utf-8').split('\n').filter(Boolean);

      // Parse logs into LogEntry format
      const logs: LogEntry[] = logLines.map((line) => {
        return this.parseLogLine(line, request.source_id, request.customer_id, SourceType.CONTAINER);
      });

      // Store logs in database
      if (logs.length > 0) {
        await database.createLogs(logs);
      }

      logger.info('Collected logs from container', {
        container_id: request.source_id,
        count: logs.length,
      });

      return logs;
    } catch (error: any) {
      logger.error('Failed to collect logs from container', {
        container_id: request.source_id,
        error: error.message,
      });
      throw error;
    }
  }

  /**
   * Collect logs from a device
   */
  async collectFromDevice(request: CollectLogsRequest): Promise<LogEntry[]> {
    try {
      const deviceInfo = await database.getDeviceInfo(request.source_id);
      if (!deviceInfo) {
        throw new Error(`Device ${request.source_id} not found`);
      }

      if (deviceInfo.status !== 'online') {
        throw new Error(`Device ${request.source_id} is offline`);
      }

      // Build query parameters
      const params: any = {};
      if (request.since) params.since = request.since;
      if (request.until) params.until = request.until;
      if (request.tail) params.tail = request.tail;

      // Fetch logs from device via HTTP
      const response = await axios.get(
        `http://${deviceInfo.tailscale_ip}:3000/logs`,
        {
          params,
          timeout: 30000,
        }
      );

      const logs: LogEntry[] = response.data.logs.map((log: any) => ({
        ...log,
        id: uuidv4(),
        customer_id: request.customer_id,
        source_type: SourceType.DEVICE,
        source_id: request.source_id,
      }));

      // Store logs in database
      if (logs.length > 0) {
        await database.createLogs(logs);
      }

      logger.info('Collected logs from device', {
        device_id: request.source_id,
        count: logs.length,
      });

      return logs;
    } catch (error: any) {
      logger.error('Failed to collect logs from device', {
        device_id: request.source_id,
        error: error.message,
      });
      throw error;
    }
  }

  /**
   * Stream logs in real-time
   */
  async streamLogs(
    request: StreamLogsRequest,
    callback: (log: LogEntry) => void
  ): Promise<() => void> {
    if (request.source_type === SourceType.CONTAINER) {
      return this.streamContainerLogs(request, callback);
    } else if (request.source_type === SourceType.DEVICE) {
      return this.streamDeviceLogs(request, callback);
    } else {
      throw new Error(`Unsupported source type: ${request.source_type}`);
    }
  }

  /**
   * Stream container logs
   */
  private async streamContainerLogs(
    request: StreamLogsRequest,
    callback: (log: LogEntry) => void
  ): Promise<() => void> {
    const container = this.docker.getContainer(request.source_id);

    const stream = await container.logs({
      follow: true,
      stdout: true,
      stderr: true,
      timestamps: true,
    });

    stream.on('data', (chunk: Buffer) => {
      const lines = chunk.toString('utf-8').split('\n').filter(Boolean);
      lines.forEach((line) => {
        const log = this.parseLogLine(line, request.source_id, request.customer_id, SourceType.CONTAINER);
        
        // Apply filters
        if (request.level && log.level !== request.level) return;
        if (request.filter && !log.message.includes(request.filter)) return;

        callback(log);
      });
    });

    // Return cleanup function
    return () => {
      stream.destroy();
    };
  }

  /**
   * Stream device logs (placeholder - would use WebSocket in production)
   */
  private async streamDeviceLogs(
    request: StreamLogsRequest,
    callback: (log: LogEntry) => void
  ): Promise<() => void> {
    // In production, this would establish a WebSocket connection to the device
    // For now, we'll poll the device periodically
    let isActive = true;
    let lastTimestamp = new Date().toISOString();

    const poll = async () => {
      if (!isActive) return;

      try {
        const logs = await this.collectFromDevice({
          source_type: SourceType.DEVICE,
          source_id: request.source_id,
          customer_id: request.customer_id,
          since: lastTimestamp,
        });

        logs.forEach((log) => {
          // Apply filters
          if (request.level && log.level !== request.level) return;
          if (request.filter && !log.message.includes(request.filter)) return;

          callback(log);
          lastTimestamp = log.timestamp;
        });
      } catch (error: any) {
        logger.error('Error polling device logs', { error: error.message });
      }

      if (isActive) {
        setTimeout(poll, 2000); // Poll every 2 seconds
      }
    };

    poll();

    // Return cleanup function
    return () => {
      isActive = false;
    };
  }

  /**
   * Parse a log line into LogEntry format
   */
  private parseLogLine(
    line: string,
    sourceId: string,
    customerId: string,
    sourceType: SourceType
  ): LogEntry {
    // Remove Docker header (8 bytes)
    const cleanLine = line.replace(/^.{8}/, '');

    // Try to parse timestamp
    const timestampMatch = cleanLine.match(/^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)\s+(.*)$/);

    let timestamp: string;
    let message: string;

    if (timestampMatch) {
      timestamp = timestampMatch[1];
      message = timestampMatch[2];
    } else {
      timestamp = new Date().toISOString();
      message = cleanLine;
    }

    // Detect log level from message
    let level = LogLevel.INFO;
    const lowerMessage = message.toLowerCase();

    if (lowerMessage.includes('error') || lowerMessage.includes('err:')) {
      level = LogLevel.ERROR;
    } else if (lowerMessage.includes('warn') || lowerMessage.includes('warning')) {
      level = LogLevel.WARN;
    } else if (lowerMessage.includes('debug')) {
      level = LogLevel.DEBUG;
    } else if (lowerMessage.includes('fatal') || lowerMessage.includes('critical')) {
      level = LogLevel.FATAL;
    }

    // Try to parse JSON metadata
    let metadata: Record<string, any> | undefined;
    try {
      const jsonMatch = message.match(/\{.*\}/);
      if (jsonMatch) {
        metadata = JSON.parse(jsonMatch[0]);
      }
    } catch {
      // Not JSON, ignore
    }

    return {
      id: uuidv4(),
      timestamp,
      level,
      source_type: sourceType,
      source_id: sourceId,
      customer_id: customerId,
      message,
      metadata,
    };
  }
}

export const logCollector = new LogCollector();

