import { createClient, SupabaseClient } from '@supabase/supabase-js';
import logger from './logger';

const supabaseUrl = process.env.SUPABASE_URL || '';
const supabaseKey = process.env.SUPABASE_KEY || '';

if (!supabaseUrl || !supabaseKey) {
  logger.warn('Supabase credentials not configured. Database features will be disabled.');
}

export const supabase: SupabaseClient = createClient(supabaseUrl, supabaseKey);

/**
 * Database schema for EVCC Agent
 * 
 * Tables:
 * - evcc_loadpoints: Loadpoint state tracking
 * - evcc_charging_sessions: Charging session history
 * - evcc_optimization_history: Optimization decision history
 * - evcc_system_state: System state snapshots
 */

export interface LoadpointState {
  id: string;
  loadpoint_id: number;
  mode: string;
  enabled: boolean;
  charging: boolean;
  current_power: number;
  charged_energy: number;
  vehicle_soc: number | null;
  limit_soc: number | null;
  limit_energy: number | null;
  phases: number;
  updated_at: string;
}

export interface ChargingSession {
  id: string;
  loadpoint_id: number;
  vehicle_name: string | null;
  start_time: string;
  end_time: string | null;
  start_soc: number | null;
  end_soc: number | null;
  energy_charged: number;
  cost: number | null;
  pv_energy: number | null;
  grid_energy: number | null;
  created_at: string;
}

export interface OptimizationHistory {
  id: string;
  loadpoint_id: number;
  objective: string;
  decision: any;
  reasoning: string;
  constraints: any;
  result: any;
  created_at: string;
}

export interface SystemState {
  id: string;
  grid_power: number;
  pv_power: number;
  battery_power: number;
  battery_soc: number | null;
  home_power: number;
  loadpoint_states: any;
  created_at: string;
}

/**
 * Save loadpoint state to database
 */
export async function saveLoadpointState(state: Omit<LoadpointState, 'id' | 'updated_at'>): Promise<void> {
  try {
    const { error } = await supabase
      .from('evcc_loadpoints')
      .upsert({
        ...state,
        updated_at: new Date().toISOString(),
      }, {
        onConflict: 'loadpoint_id',
      });

    if (error) {
      logger.error('Failed to save loadpoint state', { error });
    }
  } catch (err) {
    logger.error('Database error saving loadpoint state', { err });
  }
}

/**
 * Save charging session to database
 */
export async function saveChargingSession(session: Omit<ChargingSession, 'id' | 'created_at'>): Promise<void> {
  try {
    const { error } = await supabase
      .from('evcc_charging_sessions')
      .insert({
        ...session,
        created_at: new Date().toISOString(),
      });

    if (error) {
      logger.error('Failed to save charging session', { error });
    }
  } catch (err) {
    logger.error('Database error saving charging session', { err });
  }
}

/**
 * Save optimization history to database
 */
export async function saveOptimizationHistory(history: Omit<OptimizationHistory, 'id' | 'created_at'>): Promise<void> {
  try {
    const { error } = await supabase
      .from('evcc_optimization_history')
      .insert({
        ...history,
        created_at: new Date().toISOString(),
      });

    if (error) {
      logger.error('Failed to save optimization history', { error });
    }
  } catch (err) {
    logger.error('Database error saving optimization history', { err });
  }
}

/**
 * Save system state snapshot to database
 */
export async function saveSystemState(state: Omit<SystemState, 'id' | 'created_at'>): Promise<void> {
  try {
    const { error } = await supabase
      .from('evcc_system_state')
      .insert({
        ...state,
        created_at: new Date().toISOString(),
      });

    if (error) {
      logger.error('Failed to save system state', { error });
    }
  } catch (err) {
    logger.error('Database error saving system state', { err });
  }
}

export default supabase;

