/**
 * Tailscale API Client
 * Handles Tailscale network management for edge devices
 */

import axios, { AxiosInstance } from 'axios';
import { TailscaleDevice, TailscaleAuthKey } from './types';
import { logger } from './logger';

export class TailscaleClient {
  private client: AxiosInstance;
  private tailnet: string;

  constructor(apiKey: string, tailnet: string, apiUrl: string = 'https://api.tailscale.com') {
    this.tailnet = tailnet;
    this.client = axios.create({
      baseURL: `${apiUrl}/api/v2`,
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });
  }

  /**
   * List all devices in the Tailscale network
   */
  async listDevices(): Promise<TailscaleDevice[]> {
    try {
      const response = await this.client.get(`/tailnet/${this.tailnet}/devices`);
      
      return response.data.devices.map((device: any) => ({
        id: device.id,
        name: device.name,
        hostname: device.hostname,
        addresses: device.addresses,
        nodeId: device.nodeId,
        user: device.user,
        online: device.online,
        lastSeen: device.lastSeen,
        os: device.os,
        clientVersion: device.clientVersion,
      }));
    } catch (error) {
      logger.error('Failed to list Tailscale devices', { error });
      throw error;
    }
  }

  /**
   * Get a specific device by ID
   */
  async getDevice(deviceId: string): Promise<TailscaleDevice | null> {
    try {
      const response = await this.client.get(`/device/${deviceId}`);
      
      const device = response.data;
      return {
        id: device.id,
        name: device.name,
        hostname: device.hostname,
        addresses: device.addresses,
        nodeId: device.nodeId,
        user: device.user,
        online: device.online,
        lastSeen: device.lastSeen,
        os: device.os,
        clientVersion: device.clientVersion,
      };
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      logger.error('Failed to get Tailscale device', { error, deviceId });
      throw error;
    }
  }

  /**
   * Create an auth key for device registration
   * This key will be used by new devices to join the Tailscale network
   */
  async createAuthKey(options?: {
    reusable?: boolean;
    ephemeral?: boolean;
    preauthorized?: boolean;
    tags?: string[];
    expirySeconds?: number;
  }): Promise<TailscaleAuthKey> {
    try {
      const payload = {
        capabilities: {
          devices: {
            create: {
              reusable: options?.reusable ?? true,
              ephemeral: options?.ephemeral ?? false,
              preauthorized: options?.preauthorized ?? true,
              tags: options?.tags ?? ['tag:agentify-edge'],
            },
          },
        },
        expirySeconds: options?.expirySeconds ?? 7776000, // 90 days default
      };

      const response = await this.client.post(`/tailnet/${this.tailnet}/keys`, payload);

      logger.info('Created Tailscale auth key', {
        reusable: options?.reusable,
        ephemeral: options?.ephemeral,
      });

      return {
        key: response.data.key,
        expires: response.data.expires,
        capabilities: payload.capabilities,
      };
    } catch (error) {
      logger.error('Failed to create Tailscale auth key', { error });
      throw error;
    }
  }

  /**
   * Delete an auth key
   */
  async deleteAuthKey(keyId: string): Promise<void> {
    try {
      await this.client.delete(`/tailnet/${this.tailnet}/keys/${keyId}`);
      logger.info('Deleted Tailscale auth key', { keyId });
    } catch (error) {
      logger.error('Failed to delete Tailscale auth key', { error, keyId });
      throw error;
    }
  }

  /**
   * Delete a device from the Tailscale network
   */
  async deleteDevice(deviceId: string): Promise<void> {
    try {
      await this.client.delete(`/device/${deviceId}`);
      logger.info('Deleted Tailscale device', { deviceId });
    } catch (error) {
      logger.error('Failed to delete Tailscale device', { error, deviceId });
      throw error;
    }
  }

  /**
   * Set device tags
   */
  async setDeviceTags(deviceId: string, tags: string[]): Promise<void> {
    try {
      await this.client.post(`/device/${deviceId}/tags`, { tags });
      logger.info('Set Tailscale device tags', { deviceId, tags });
    } catch (error) {
      logger.error('Failed to set Tailscale device tags', { error, deviceId });
      throw error;
    }
  }

  /**
   * Check if a device is online
   */
  async isDeviceOnline(deviceId: string): Promise<boolean> {
    const device = await this.getDevice(deviceId);
    return device?.online ?? false;
  }
}

