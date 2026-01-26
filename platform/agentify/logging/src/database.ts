/**
 * Database client for Logging Agent
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js';
import logger from './logger';
import {
  LogEntry,
  SearchLogsRequest,
  SearchLogsResponse,
  RetentionPolicy,
  RetentionStats,
  ExportJob,
  LogLevel,
  SourceType,
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

  // ========== Log Management ==========

  async createLog(log: Omit<LogEntry, 'id'>): Promise<LogEntry> {
    const { data, error } = await this.supabase
      .from('logs')
      .insert(log)
      .select()
      .single();

    if (error) {
      logger.error('Failed to create log', { error });
      throw new Error(`Failed to create log: ${error.message}`);
    }

    return data;
  }

  async createLogs(logs: Omit<LogEntry, 'id'>[]): Promise<LogEntry[]> {
    const { data, error } = await this.supabase
      .from('logs')
      .insert(logs)
      .select();

    if (error) {
      logger.error('Failed to create logs', { error });
      throw new Error(`Failed to create logs: ${error.message}`);
    }

    return data;
  }

  async searchLogs(request: SearchLogsRequest): Promise<SearchLogsResponse> {
    let query = this.supabase
      .from('logs')
      .select('*', { count: 'exact' })
      .eq('customer_id', request.customer_id);

    // Apply filters
    if (request.source_type) {
      query = query.eq('source_type', request.source_type);
    }

    if (request.source_id) {
      query = query.eq('source_id', request.source_id);
    }

    if (request.level) {
      query = query.eq('level', request.level);
    }

    if (request.start_time) {
      query = query.gte('timestamp', request.start_time);
    }

    if (request.end_time) {
      query = query.lte('timestamp', request.end_time);
    }

    if (request.tags && request.tags.length > 0) {
      query = query.contains('tags', request.tags);
    }

    if (request.query) {
      query = query.ilike('message', `%${request.query}%`);
    }

    // Pagination
    const limit = request.limit || 100;
    const offset = request.offset || 0;

    query = query
      .order('timestamp', { ascending: false })
      .range(offset, offset + limit - 1);

    const { data, error, count } = await query;

    if (error) {
      logger.error('Failed to search logs', { error });
      throw new Error(`Failed to search logs: ${error.message}`);
    }

    return {
      logs: data || [],
      count: data?.length || 0,
      has_more: count ? count > offset + limit : false,
      total: count || 0,
    };
  }

  async getLogsBySource(
    sourceId: string,
    customerId: string,
    limit: number = 100
  ): Promise<LogEntry[]> {
    const { data, error } = await this.supabase
      .from('logs')
      .select('*')
      .eq('source_id', sourceId)
      .eq('customer_id', customerId)
      .order('timestamp', { ascending: false })
      .limit(limit);

    if (error) {
      logger.error('Failed to get logs by source', { error });
      throw new Error(`Failed to get logs: ${error.message}`);
    }

    return data || [];
  }

  async deleteOldLogs(retentionDays: number, customerId: string): Promise<number> {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - retentionDays);

    const { data, error } = await this.supabase
      .from('logs')
      .delete()
      .eq('customer_id', customerId)
      .lt('timestamp', cutoffDate.toISOString())
      .select();

    if (error) {
      logger.error('Failed to delete old logs', { error });
      throw new Error(`Failed to delete old logs: ${error.message}`);
    }

    return data?.length || 0;
  }

  // ========== Retention Policy Management ==========

  async getRetentionPolicy(customerId: string): Promise<RetentionPolicy | null> {
    const { data, error } = await this.supabase
      .from('retention_policies')
      .select('*')
      .eq('customer_id', customerId)
      .single();

    if (error && error.code !== 'PGRST116') {
      logger.error('Failed to get retention policy', { error });
      throw new Error(`Failed to get retention policy: ${error.message}`);
    }

    return data;
  }

  async createRetentionPolicy(
    policy: Omit<RetentionPolicy, 'id' | 'created_at' | 'updated_at'>
  ): Promise<RetentionPolicy> {
    const { data, error } = await this.supabase
      .from('retention_policies')
      .insert(policy)
      .select()
      .single();

    if (error) {
      logger.error('Failed to create retention policy', { error });
      throw new Error(`Failed to create retention policy: ${error.message}`);
    }

    return data;
  }

  async updateRetentionPolicy(
    policyId: string,
    updates: Partial<RetentionPolicy>
  ): Promise<void> {
    const { error } = await this.supabase
      .from('retention_policies')
      .update({ ...updates, updated_at: new Date().toISOString() })
      .eq('id', policyId);

    if (error) {
      logger.error('Failed to update retention policy', { error });
      throw new Error(`Failed to update retention policy: ${error.message}`);
    }
  }

  // ========== Export Job Management ==========

  async createExportJob(
    job: Omit<ExportJob, 'id' | 'created_at'>
  ): Promise<ExportJob> {
    const { data, error } = await this.supabase
      .from('export_jobs')
      .insert(job)
      .select()
      .single();

    if (error) {
      logger.error('Failed to create export job', { error });
      throw new Error(`Failed to create export job: ${error.message}`);
    }

    return data;
  }

  async updateExportJob(
    jobId: string,
    updates: Partial<ExportJob>
  ): Promise<void> {
    const { error } = await this.supabase
      .from('export_jobs')
      .update(updates)
      .eq('id', jobId);

    if (error) {
      logger.error('Failed to update export job', { error });
      throw new Error(`Failed to update export job: ${error.message}`);
    }
  }

  async getExportJob(jobId: string): Promise<ExportJob | null> {
    const { data, error } = await this.supabase
      .from('export_jobs')
      .select('*')
      .eq('id', jobId)
      .single();

    if (error && error.code !== 'PGRST116') {
      logger.error('Failed to get export job', { error });
      throw new Error(`Failed to get export job: ${error.message}`);
    }

    return data;
  }

  async listExportJobs(customerId: string): Promise<ExportJob[]> {
    const { data, error } = await this.supabase
      .from('export_jobs')
      .select('*')
      .eq('customer_id', customerId)
      .order('created_at', { ascending: false });

    if (error) {
      logger.error('Failed to list export jobs', { error });
      throw new Error(`Failed to list export jobs: ${error.message}`);
    }

    return data || [];
  }

  // ========== Statistics ==========

  async getStatistics(customerId: string): Promise<RetentionStats> {
    const { data: logs, error } = await this.supabase
      .from('logs')
      .select('timestamp, level')
      .eq('customer_id', customerId);

    if (error) {
      logger.error('Failed to get statistics', { error });
      throw new Error(`Failed to get statistics: ${error.message}`);
    }

    if (!logs || logs.length === 0) {
      return {
        total_logs: 0,
        oldest_log: new Date().toISOString(),
        newest_log: new Date().toISOString(),
        size_bytes: 0,
        logs_by_level: {
          [LogLevel.DEBUG]: 0,
          [LogLevel.INFO]: 0,
          [LogLevel.WARN]: 0,
          [LogLevel.ERROR]: 0,
          [LogLevel.FATAL]: 0,
        },
      };
    }

    const timestamps = logs.map((l) => new Date(l.timestamp).getTime());
    const oldest = new Date(Math.min(...timestamps)).toISOString();
    const newest = new Date(Math.max(...timestamps)).toISOString();

    const logsByLevel = logs.reduce((acc, log) => {
      acc[log.level as LogLevel] = (acc[log.level as LogLevel] || 0) + 1;
      return acc;
    }, {} as Record<LogLevel, number>);

    return {
      total_logs: logs.length,
      oldest_log: oldest,
      newest_log: newest,
      size_bytes: JSON.stringify(logs).length,
      logs_by_level: {
        [LogLevel.DEBUG]: logsByLevel[LogLevel.DEBUG] || 0,
        [LogLevel.INFO]: logsByLevel[LogLevel.INFO] || 0,
        [LogLevel.WARN]: logsByLevel[LogLevel.WARN] || 0,
        [LogLevel.ERROR]: logsByLevel[LogLevel.ERROR] || 0,
        [LogLevel.FATAL]: logsByLevel[LogLevel.FATAL] || 0,
      },
    };
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
}

export const database = new Database();

