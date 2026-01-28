/**
 * API Service - Handle all backend communication
 */

import axios from 'axios'

// Use environment variable for production, fallback to proxy for development
const API_BASE_URL = import.meta.env.VITE_API_URL
  ? import.meta.env.VITE_API_URL
  : '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface FieldConfig {
  managing_directors: boolean
  revenue: boolean
  employees: boolean
  history: boolean
  news: boolean
}

export interface GapAnalysisData {
  total_companies: number
  complete_records: number
  incomplete_records: number
  missing_fields: Record<string, number>
  completion_rate: number
}

export interface ResearchProgress {
  status: 'idle' | 'processing' | 'complete' | 'error'
  current_company?: string
  processed_count: number
  total_count: number
  progress_percentage: number
}

export interface CompanyData {
  company_name: string
  website?: string
  managing_directors?: string
  revenue?: string
  employees?: string
  history?: string
  news?: string
  enriched?: boolean
}

/**
 * Upload Excel file and get gap analysis
 */
export const uploadExcel = async (file: File): Promise<{
  success: boolean
  gap_analysis: GapAnalysisData
  companies: CompanyData[]
}> => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post('/company/upload_excel', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return response.data
}

/**
 * Configure which fields to extract
 */
export const configureFields = async (config: FieldConfig): Promise<{
  success: boolean
  message: string
}> => {
  const response = await api.post('/company/configure_fields', config)
  return response.data
}

/**
 * Start research process
 */
export const startResearch = async (): Promise<{
  success: boolean
  job_id: string
}> => {
  const response = await api.post('/company/research')
  return response.data
}

/**
 * Get research progress
 */
export const getResearchProgress = async (jobId: string): Promise<ResearchProgress> => {
  const response = await api.get(`/company/research/${jobId}/progress`)
  return response.data
}

/**
 * Get research results
 */
export const getResearchResults = async (jobId: string): Promise<{
  success: boolean
  companies: CompanyData[]
}> => {
  const response = await api.get(`/company/research/${jobId}/results`)
  return response.data
}

/**
 * Export results to Excel
 */
export const exportResults = async (jobId: string): Promise<Blob> => {
  const response = await api.get(`/company/export/${jobId}`, {
    responseType: 'blob',
  })
  return response.data
}

/**
 * Get agent manifest
 */
export const getManifest = async () => {
  const response = await api.get('/agent/manifest')
  return response.data
}

/**
 * Console Logs
 */
export interface ConsoleLogEntry {
  timestamp: string
  level: 'INFO' | 'ERROR' | 'WARNING' | 'DEBUG'
  message: string
}

export const getConsoleLogs = async (): Promise<{
  success: boolean
  logs: ConsoleLogEntry[]
}> => {
  const response = await api.get('/console/logs')
  return response.data
}

export const clearConsoleLogs = async (): Promise<{
  success: boolean
  message: string
}> => {
  const response = await api.post('/console/clear')
  return response.data
}

/**
 * Get all active (running) jobs
 */
export const getActiveJobs = async (): Promise<{
  success: boolean
  jobs: any[]
}> => {
  const response = await api.get('/company/active_jobs')
  return response.data
}

/**
 * Abort a running research job
 */
export const abortResearch = async (jobId: string): Promise<{
  success: boolean
  message: string
}> => {
  const response = await api.post(`/company/research/${jobId}/abort`)
  return response.data
}

export default api

