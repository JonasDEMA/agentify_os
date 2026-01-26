import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { logger } from './logger';
import { EnergyMetrics, FCRProcess } from './types';

class Database {
  private supabase: SupabaseClient;
  private customerId: string;

  constructor() {
    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_KEY;
    this.customerId = process.env.CUSTOMER_ID || 'customer-001';

    if (!supabaseUrl || !supabaseKey) {
      throw new Error('SUPABASE_URL and SUPABASE_KEY must be set');
    }

    this.supabase = createClient(supabaseUrl, supabaseKey);
    logger.info('Database client initialized');
  }

  // Energy Metrics Methods
  async createEnergyMetrics(metrics: Omit<EnergyMetrics, 'id' | 'created_at'>): Promise<EnergyMetrics> {
    const { data, error } = await this.supabase
      .from('energy_metrics')
      .insert([{
        ...metrics,
        customer_id: this.customerId,
        timestamp: metrics.timestamp || new Date().toISOString()
      }])
      .select()
      .single();

    if (error) {
      logger.error('Failed to create energy metrics', { error });
      throw error;
    }

    logger.debug('Created energy metrics', { id: data.id });
    return data;
  }

  async getEnergyMetrics(filters: {
    loadpoint_id?: number;
    meter_id?: number;
    start_time?: string;
    end_time?: string;
    limit?: number;
  }): Promise<EnergyMetrics[]> {
    let query = this.supabase
      .from('energy_metrics')
      .select('*')
      .eq('customer_id', this.customerId)
      .order('timestamp', { ascending: false });

    if (filters.loadpoint_id) {
      query = query.eq('loadpoint_id', filters.loadpoint_id);
    }

    if (filters.meter_id) {
      query = query.eq('meter_id', filters.meter_id);
    }

    if (filters.start_time) {
      query = query.gte('timestamp', filters.start_time);
    }

    if (filters.end_time) {
      query = query.lte('timestamp', filters.end_time);
    }

    if (filters.limit) {
      query = query.limit(filters.limit);
    }

    const { data, error } = await query;

    if (error) {
      logger.error('Failed to get energy metrics', { error, filters });
      throw error;
    }

    return data || [];
  }

  async getLatestEnergyMetrics(loadpointId: number): Promise<EnergyMetrics | null> {
    const { data, error } = await this.supabase
      .from('energy_metrics')
      .select('*')
      .eq('customer_id', this.customerId)
      .eq('loadpoint_id', loadpointId)
      .order('timestamp', { ascending: false })
      .limit(1)
      .single();

    if (error && error.code !== 'PGRST116') { // PGRST116 = no rows returned
      logger.error('Failed to get latest energy metrics', { error, loadpointId });
      throw error;
    }

    return data || null;
  }

  // FCR Process Methods
  async createFCRProcess(process: Omit<FCRProcess, 'id' | 'created_at' | 'updated_at'>): Promise<FCRProcess> {
    const { data, error } = await this.supabase
      .from('fcr_processes')
      .insert([{
        ...process,
        customer_id: this.customerId
      }])
      .select()
      .single();

    if (error) {
      logger.error('Failed to create FCR process', { error });
      throw error;
    }

    logger.info('Created FCR process', { module_id: data.module_id });
    return data;
  }

  async getFCRProcess(moduleId: string): Promise<FCRProcess | null> {
    const { data, error } = await this.supabase
      .from('fcr_processes')
      .select('*')
      .eq('customer_id', this.customerId)
      .eq('module_id', moduleId)
      .single();

    if (error && error.code !== 'PGRST116') {
      logger.error('Failed to get FCR process', { error, moduleId });
      throw error;
    }

    return data || null;
  }

  async updateFCRProcess(moduleId: string, updates: Partial<FCRProcess>): Promise<FCRProcess> {
    const { data, error } = await this.supabase
      .from('fcr_processes')
      .update({
        ...updates,
        updated_at: new Date().toISOString()
      })
      .eq('customer_id', this.customerId)
      .eq('module_id', moduleId)
      .select()
      .single();

    if (error) {
      logger.error('Failed to update FCR process', { error, moduleId });
      throw error;
    }

    logger.info('Updated FCR process', { module_id: moduleId });
    return data;
  }

  async deleteFCRProcess(moduleId: string): Promise<void> {
    const { error } = await this.supabase
      .from('fcr_processes')
      .delete()
      .eq('customer_id', this.customerId)
      .eq('module_id', moduleId);

    if (error) {
      logger.error('Failed to delete FCR process', { error, moduleId });
      throw error;
    }

    logger.info('Deleted FCR process', { module_id: moduleId });
  }
}

export const database = new Database();

