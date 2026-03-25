import { Placeholder } from './types';

const base = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000';
const token = process.env.NEXT_PUBLIC_APP_TOKEN ?? 'change-me';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${base}${path}`, {
    ...init,
    headers: {
      'X-API-Token': token,
      ...(init?.headers ?? {})
    }
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function upload(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  return request<{ jobId: string; state: string }>('/api/upload', { method: 'POST', body: formData });
}

export async function sampleUpload() {
  return request<{ jobId: string; state: string }>('/api/sample', { method: 'POST' });
}

export async function parse(jobId: string) {
  return request<{ placeholders: Placeholder[] }>(`/api/parse/${jobId}`, { method: 'POST' });
}

export async function fill(jobId: string, answers: Record<string, string>) {
  return request<{ id: string; state: string }>(`/api/fill/${jobId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ answers, keepUnfilled: false, fieldConfig: [] })
  });
}

export function downloadUrl(jobId: string) {
  return `${base}/api/download/${jobId}`;
}

export { token };
