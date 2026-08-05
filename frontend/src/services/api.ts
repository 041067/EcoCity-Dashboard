import axios from 'axios';
import type {
  AIReport,
  Alert,
  ChatRequest,
  ChatResponse,
  City,
  HealthResponse,
  Reading,
  Score,
} from '../types';

function resolveApiBase(): string {
  const configured = import.meta.env.VITE_API_URL;
  if (!configured) return '/api/v1';
  const trimmed = configured.replace(/\/+$/, '');
  return trimmed.endsWith('/api/v1') ? trimmed : `${trimmed}/api/v1`;
}

const api = axios.create({
  baseURL: resolveApiBase(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await api.get<HealthResponse>(`/health`);
  return data;
}

export async function getCities(): Promise<City[]> {
  const { data } = await api.get<City[]>('/cities');
  return data;
}

export async function getLatestReadings(): Promise<Reading[]> {
  const { data } = await api.get<Reading[]>('/readings/latest');
  return data;
}

export async function getHistory(
  city?: string,
  startDate?: string,
  endDate?: string,
): Promise<Reading[]> {
  const params: Record<string, string> = {};
  if (city) params.city = city;
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;
  const { data } = await api.get<Reading[]>('/readings/history', { params });
  return data;
}

export async function getScores(): Promise<Score[]> {
  const { data } = await api.get<Score[]>('/scores');
  return data;
}

export async function getAlerts(city?: string): Promise<Alert[]> {
  const params: Record<string, string> = {};
  if (city) params.city = city;
  const { data } = await api.get<Alert[]>('/alerts', { params });
  return data;
}

export async function generateReport(city: string): Promise<AIReport> {
  const { data } = await api.post<AIReport>('/ai/report', null, { params: { city } });
  return data;
}

export async function getLatestReport(city: string): Promise<AIReport> {
  const { data } = await api.get<AIReport>('/ai/reports', { params: { city } });
  return data;
}

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const { data } = await api.post<ChatResponse>('/ai/chat', request);
  return data;
}

export async function collectReadings(): Promise<unknown[]> {
  const { data } = await api.post<unknown[]>('/readings/collect');
  return data;
}

export default api;