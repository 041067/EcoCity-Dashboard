export interface HealthResponse {
  status: string;
  database: string;
}

export interface City {
  id: number;
  name: string;
  state: string;
  latitude: number;
  longitude: number;
  score?: number;
  created_at?: string;
}

export interface Reading {
  id: number;
  city_id: number;
  city_name?: string;
  temperature: number;
  humidity: number;
  pm25: number;
  pm10: number;
  ozone: number;
  carbon_monoxide: number;
  wind_speed: number;
  uv_index: number;
  aqi?: number;
  created_at?: string;
}

export interface Alert {
  id: number;
  city_id: number;
  city_name?: string;
  severity: string;
  title: string;
  description: string;
  created_at?: string;
}

export interface Score {
  city_id: number;
  city_name?: string;
  state?: string;
  score: number;
  classification: string;
  symbol: string;
  aqi: number;
  temperature: number;
  humidity: number;
  wind_speed: number;
  uv_index: number;
  created_at?: string;
}

export interface AIReport {
  city: string;
  summary: string;
  recommendation: string;
  created_at?: string;
}

export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  message: string;
  answer: string;
}