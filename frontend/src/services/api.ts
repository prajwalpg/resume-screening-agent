import type { HealthStatus, ScreeningData } from '../types';

const API_BASE = '/api';

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Failed to fetch health');
  return res.json();
}

export async function fetchScreenings(): Promise<ScreeningData[]> {
  const res = await fetch(`${API_BASE}/screenings`);
  if (!res.ok) throw new Error('Failed to fetch screenings');
  return res.json();
}

export async function fetchScreening(id: string): Promise<ScreeningData> {
  const res = await fetch(`${API_BASE}/screenings/${id}`);
  if (!res.ok) throw new Error('Failed to fetch screening details');
  return res.json();
}

export async function runDemoScreening(): Promise<ScreeningData> {
  const res = await fetch(`${API_BASE}/screenings/demo`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to run demo screening');
  return res.json();
}

export async function runCustomScreening(
  jdFile: File | null,
  resumeFiles: File[]
): Promise<ScreeningData> {
  const formData = new FormData();
  if (jdFile) {
    formData.append('jd_file', jdFile);
  }
  resumeFiles.forEach((file) => {
    formData.append('resume_files', file);
  });

  const res = await fetch(`${API_BASE}/screenings/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || 'Failed to execute screening run');
  }
  return res.json();
}

export async function fetchComparison(candidates: any[]): Promise<any> {
  const res = await fetch(`${API_BASE}/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ candidates }),
  });
  if (!res.ok) throw new Error('Failed to calculate comparison');
  return res.json();
}

export function getExportUrl(screeningId: string, format: 'csv' | 'json' | 'report'): string {
  return `${API_BASE}/screenings/${screeningId}/export/${format}`;
}
