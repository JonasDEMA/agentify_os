/**
 * Edge Deployer
 * Handles deployment of agent containers to edge devices (Raspberry Pi)
 */

import Dockerode from 'dockerode';
import { EdgeDeploymentConfig, EdgeDeploymentResult, ResourceLimits } from './types';
import { logger } from './logger';

export class EdgeDeployer {
  private dockerClients: Map<string, Dockerode>;

  constructor() {
    this.dockerClients = new Map();
  }

  /**
   * Get or create Docker client for a device
   * Uses Tailscale network to connect to edge devices
   */
  private getDockerClient(deviceId: string, deviceAddress: string): Dockerode {
    if (this.dockerClients.has(deviceId)) {
      return this.dockerClients.get(deviceId)!;
    }

    // Connect to Docker daemon on edge device via Tailscale
    const client = new Dockerode({
      host: deviceAddress,
      port: 2375,
      protocol: 'http',
    });

    this.dockerClients.set(deviceId, client);
    return client;
  }

  /**
   * Deploy an agent container to edge device
   */
  async deploy(config: EdgeDeploymentConfig, deviceAddress: string): Promise<EdgeDeploymentResult> {
    logger.info('Deploying to edge device', {
      agent_id: config.agent_id,
      customer_id: config.customer_id,
      device_id: config.device_id,
    });

    try {
      const docker = this.getDockerClient(config.device_id, deviceAddress);

      // Pull image
      await this.pullImage(docker, config.image);

      // Create container
      const container = await this.createContainer(docker, config);

      // Start container
      await container.start();

      // Get container info
      const info = await container.inspect();
      const address = this.getContainerAddress(info, deviceAddress);

      logger.info('Edge deployment successful', {
        container_id: info.Id,
        address,
      });

      return {
        container_id: info.Id,
        address,
        status: 'running',
      };
    } catch (error) {
      logger.error('Edge deployment failed', { error });
      throw error;
    }
  }

  /**
   * Pull Docker image
   */
  private async pullImage(docker: Dockerode, image: string): Promise<void> {
    logger.info('Pulling image', { image });

    return new Promise((resolve, reject) => {
      docker.pull(image, (err: any, stream: any) => {
        if (err) {
          reject(err);
          return;
        }

        docker.modem.followProgress(stream, (err: any, output: any) => {
          if (err) {
            reject(err);
          } else {
            logger.info('Image pulled successfully', { image });
            resolve();
          }
        });
      });
    });
  }

  /**
   * Create container with configuration
   */
  private async createContainer(
    docker: Dockerode,
    config: EdgeDeploymentConfig
  ): Promise<Dockerode.Container> {
    const containerName = `${config.agent_id.replace(/\./g, '-')}-${config.customer_id}`;

    // Convert resource limits to Docker format
    const hostConfig: any = {
      RestartPolicy: {
        Name: 'unless-stopped',
      },
    };

    if (config.resources) {
      hostConfig.Memory = this.parseMemory(config.resources.memory);
      hostConfig.NanoCpus = this.parseCpu(config.resources.cpu);
    }

    const containerConfig: any = {
      Image: config.image,
      name: containerName,
      Env: this.formatEnvVars(config.env || {}),
      HostConfig: hostConfig,
      Labels: {
        'agentify.agent_id': config.agent_id,
        'agentify.customer_id': config.customer_id,
        'agentify.device_id': config.device_id,
      },
    };

    logger.info('Creating container', { name: containerName });

    const container = await docker.createContainer(containerConfig);
    return container;
  }

  /**
   * Get container address
   */
  private getContainerAddress(info: any, deviceAddress: string): string {
    // Get the first exposed port
    const ports = Object.keys(info.Config.ExposedPorts || {});
    if (ports.length > 0) {
      const port = ports[0].split('/')[0];
      return `http://${deviceAddress}:${port}`;
    }

    // Default to port 8000
    return `http://${deviceAddress}:8000`;
  }

  /**
   * Format environment variables for Docker
   */
  private formatEnvVars(env: Record<string, string>): string[] {
    return Object.entries(env).map(([key, value]) => `${key}=${value}`);
  }

  /**
   * Parse memory limit to bytes
   */
  private parseMemory(memory?: string): number | undefined {
    if (!memory) return undefined;

    const units: Record<string, number> = {
      'b': 1,
      'k': 1024,
      'm': 1024 * 1024,
      'g': 1024 * 1024 * 1024,
    };

    const match = memory.toLowerCase().match(/^(\d+)([bkmg])?i?$/);
    if (!match) return undefined;

    const value = parseInt(match[1]);
    const unit = match[2] || 'b';

    return value * units[unit];
  }

  /**
   * Parse CPU limit to nano CPUs
   */
  private parseCpu(cpu?: string): number | undefined {
    if (!cpu) return undefined;

    const value = parseFloat(cpu);
    return Math.floor(value * 1e9); // Convert to nano CPUs
  }

  /**
   * Stop a container
   */
  async stop(deviceId: string, deviceAddress: string, containerId: string): Promise<void> {
    logger.info('Stopping edge container', { device_id: deviceId, container_id: containerId });

    const docker = this.getDockerClient(deviceId, deviceAddress);
    const container = docker.getContainer(containerId);

    await container.stop();

    logger.info('Edge container stopped', { container_id: containerId });
  }

  /**
   * Delete a container
   */
  async delete(deviceId: string, deviceAddress: string, containerId: string): Promise<void> {
    logger.info('Deleting edge container', { device_id: deviceId, container_id: containerId });

    const docker = this.getDockerClient(deviceId, deviceAddress);
    const container = docker.getContainer(containerId);

    // Stop if running
    try {
      await container.stop();
    } catch (error) {
      // Container might already be stopped
    }

    // Remove container
    await container.remove();

    logger.info('Edge container deleted', { container_id: containerId });
  }

  /**
   * Get container status
   */
  async getStatus(deviceId: string, deviceAddress: string, containerId: string): Promise<string> {
    const docker = this.getDockerClient(deviceId, deviceAddress);
    const container = docker.getContainer(containerId);

    const info = await container.inspect();
    return info.State.Status;
  }

  /**
   * Health check for edge container
   */
  async healthCheck(address: string): Promise<boolean> {
    try {
      const axios = require('axios');
      const response = await axios.get(`${address}/health`, { timeout: 5000 });
      return response.status === 200;
    } catch (error) {
      logger.warn('Edge health check failed', { address, error });
      return false;
    }
  }

  /**
   * Get container logs
   */
  async getLogs(
    deviceId: string,
    deviceAddress: string,
    containerId: string,
    tail: number = 100
  ): Promise<string> {
    const docker = this.getDockerClient(deviceId, deviceAddress);
    const container = docker.getContainer(containerId);

    const logs = await container.logs({
      stdout: true,
      stderr: true,
      tail,
    });

    return logs.toString();
  }

  /**
   * Get container stats
   */
  async getStats(deviceId: string, deviceAddress: string, containerId: string): Promise<any> {
    const docker = this.getDockerClient(deviceId, deviceAddress);
    const container = docker.getContainer(containerId);

    const stats = await container.stats({ stream: false });
    return stats;
  }
}

