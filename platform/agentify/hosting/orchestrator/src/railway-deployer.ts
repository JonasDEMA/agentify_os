/**
 * Railway Deployer
 * Handles deployment of agent containers to Railway cloud platform
 */

import axios, { AxiosInstance } from 'axios';
import { DeploymentConfig, RailwayDeploymentResult } from './types';
import { logger } from './logger';

export class RailwayDeployer {
  private client: AxiosInstance;
  private apiKey: string;
  private projectId?: string;

  constructor(apiKey: string, apiUrl: string = 'https://backboard.railway.app/graphql/v2') {
    this.apiKey = apiKey;
    this.client = axios.create({
      baseURL: apiUrl,
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });
  }

  /**
   * Deploy an agent container to Railway
   */
  async deploy(config: DeploymentConfig): Promise<RailwayDeploymentResult> {
    logger.info('Deploying to Railway', {
      agent_id: config.agent_id,
      customer_id: config.customer_id,
    });

    try {
      // Step 1: Create or get project
      const projectId = await this.ensureProject(config.customer_id);

      // Step 2: Create service
      const serviceId = await this.createService(projectId, config);

      // Step 3: Deploy container
      const deploymentId = await this.deployContainer(projectId, serviceId, config);

      // Step 4: Get deployment URL
      const url = await this.getServiceUrl(projectId, serviceId);

      logger.info('Railway deployment successful', {
        service_id: serviceId,
        deployment_id: deploymentId,
        url,
      });

      return {
        service_id: serviceId,
        deployment_id: deploymentId,
        url,
        status: 'deploying',
      };
    } catch (error) {
      logger.error('Railway deployment failed', { error });
      throw error;
    }
  }

  /**
   * Ensure project exists for customer
   */
  private async ensureProject(customerId: string): Promise<string> {
    if (this.projectId) {
      return this.projectId;
    }

    // For now, use a single project for all deployments
    // In production, you might want one project per customer
    const query = `
      query {
        projects {
          edges {
            node {
              id
              name
            }
          }
        }
      }
    `;

    const response = await this.client.post('', { query });
    const projects = response.data.data.projects.edges;

    if (projects.length > 0) {
      this.projectId = projects[0].node.id;
      return this.projectId;
    }

    // Create new project if none exists
    return await this.createProject(customerId);
  }

  /**
   * Create a new Railway project
   */
  private async createProject(customerId: string): Promise<string> {
    const mutation = `
      mutation ProjectCreate($input: ProjectCreateInput!) {
        projectCreate(input: $input) {
          id
          name
        }
      }
    `;

    const variables = {
      input: {
        name: `agentify-${customerId}`,
        description: `Agentify agents for customer ${customerId}`,
      },
    };

    const response = await this.client.post('', { query: mutation, variables });
    const projectId = response.data.data.projectCreate.id;

    logger.info('Created Railway project', { project_id: projectId, customer_id: customerId });

    this.projectId = projectId;
    return projectId;
  }

  /**
   * Create a service in the project
   */
  private async createService(projectId: string, config: DeploymentConfig): Promise<string> {
    const mutation = `
      mutation ServiceCreate($input: ServiceCreateInput!) {
        serviceCreate(input: $input) {
          id
          name
        }
      }
    `;

    const serviceName = `${config.agent_id.replace(/\./g, '-')}-${config.customer_id}`;

    const variables = {
      input: {
        projectId,
        name: serviceName,
        source: {
          image: config.image,
        },
      },
    };

    const response = await this.client.post('', { query: mutation, variables });
    const serviceId = response.data.data.serviceCreate.id;

    logger.info('Created Railway service', { service_id: serviceId, name: serviceName });

    return serviceId;
  }

  /**
   * Deploy container to service
   */
  private async deployContainer(
    projectId: string,
    serviceId: string,
    config: DeploymentConfig
  ): Promise<string> {
    // Set environment variables
    if (config.env) {
      await this.setEnvironmentVariables(projectId, serviceId, config.env);
    }

    // Trigger deployment
    const mutation = `
      mutation ServiceInstanceDeploy($input: ServiceInstanceDeployInput!) {
        serviceInstanceDeploy(input: $input) {
          id
        }
      }
    `;

    const variables = {
      input: {
        serviceId,
      },
    };

    const response = await this.client.post('', { query: mutation, variables });
    const deploymentId = response.data.data.serviceInstanceDeploy.id;

    logger.info('Triggered Railway deployment', { deployment_id: deploymentId });

    return deploymentId;
  }

  /**
   * Set environment variables for service
   */
  private async setEnvironmentVariables(
    projectId: string,
    serviceId: string,
    env: Record<string, string>
  ): Promise<void> {
    const mutation = `
      mutation VariableCollectionUpsert($input: VariableCollectionUpsertInput!) {
        variableCollectionUpsert(input: $input)
      }
    `;

    for (const [key, value] of Object.entries(env)) {
      const variables = {
        input: {
          projectId,
          serviceId,
          environmentId: projectId, // Use project ID as environment ID for simplicity
          variables: {
            [key]: value,
          },
        },
      };

      await this.client.post('', { query: mutation, variables });
    }

    logger.info('Set environment variables', { service_id: serviceId, count: Object.keys(env).length });
  }

  /**
   * Get service URL
   */
  private async getServiceUrl(projectId: string, serviceId: string): Promise<string> {
    const query = `
      query Service($id: String!) {
        service(id: $id) {
          id
          name
          serviceInstances {
            edges {
              node {
                domains {
                  serviceDomains {
                    domain
                  }
                }
              }
            }
          }
        }
      }
    `;

    const variables = { id: serviceId };

    const response = await this.client.post('', { query, variables });
    const service = response.data.data.service;

    if (service.serviceInstances.edges.length > 0) {
      const domains = service.serviceInstances.edges[0].node.domains.serviceDomains;
      if (domains.length > 0) {
        return `https://${domains[0].domain}`;
      }
    }

    // If no domain yet, return placeholder
    return `https://${serviceId}.railway.app`;
  }

  /**
   * Stop a service
   */
  async stop(serviceId: string): Promise<void> {
    logger.info('Stopping Railway service', { service_id: serviceId });

    const mutation = `
      mutation ServiceDelete($id: String!) {
        serviceDelete(id: $id)
      }
    `;

    const variables = { id: serviceId };

    await this.client.post('', { query: mutation, variables });

    logger.info('Railway service stopped', { service_id: serviceId });
  }

  /**
   * Delete a service
   */
  async delete(serviceId: string): Promise<void> {
    await this.stop(serviceId);
  }

  /**
   * Get deployment status
   */
  async getDeploymentStatus(deploymentId: string): Promise<string> {
    const query = `
      query Deployment($id: String!) {
        deployment(id: $id) {
          id
          status
        }
      }
    `;

    const variables = { id: deploymentId };

    const response = await this.client.post('', { query, variables });
    return response.data.data.deployment.status;
  }

  /**
   * Health check for deployed service
   */
  async healthCheck(url: string): Promise<boolean> {
    try {
      const response = await axios.get(`${url}/health`, { timeout: 5000 });
      return response.status === 200;
    } catch (error) {
      logger.warn('Health check failed', { url, error });
      return false;
    }
  }
}

