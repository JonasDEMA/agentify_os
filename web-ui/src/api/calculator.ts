/**
 * Calculator API client
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface CalculateRequest {
  num1: number;
  num2: number;
  operator: string;
  locale?: string;
  decimals?: number;
}

export interface CalculateResponse {
  job_id: string;
  status: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: string;
  result?: string | {
    num1: number;
    num2: number;
    operator: string;
    locale: string;
    decimals: number;
    raw_result: number;
    formatted_result: string;
  };
  error?: string;
}

/**
 * Submit a calculation request
 */
export async function calculateRequest(
  num1: number,
  num2: number,
  operator: string,
  locale: string = 'en-US',
  decimals: number = 2
): Promise<CalculateResponse> {
  const response = await fetch(`${API_BASE_URL}/api/calculate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      num1,
      num2,
      operator,
      locale,
      decimals,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to submit calculation');
  }

  return response.json();
}

/**
 * Get job status
 */
export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  const response = await fetch(`${API_BASE_URL}/api/calculate/${jobId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get job status');
  }

  return response.json();
}

/**
 * Poll job status until completion
 */
export async function pollJobStatus(
  jobId: string,
  maxAttempts: number = 30,
  intervalMs: number = 1000
): Promise<JobStatusResponse> {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const status = await getJobStatus(jobId);

    if (status.status === 'done' || status.status === 'failed') {
      return status;
    }

    // Wait before next poll
    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }

  throw new Error('Job polling timeout');
}

