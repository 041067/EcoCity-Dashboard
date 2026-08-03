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
  temperature?: number;
  humidity?: number;
  windSpeed?: number;
  pm25?: number;
  pm10?: number;
  ozone?: number;
  carbonMonoxide?: number;
  uvIndex?: number;
  aqi?: number;
  score?: number;
  createdAt?: string;
}

export interface ReadingResponse {
  id: number;
  cityId: number;
  cityName?: string;
  temperature: number;
  humidity: number;
  pm25: number;
  pm10: number;
  ozone: number;
  carbonMonoxide: number;
  windSpeed: number;
  uvIndex?: number;
  aqi?: number;
  createdAt?: string;
}

export interface AlertResponse {
  id: number;
  cityId: number;
  cityName?: string;
  severity: 'green' | 'yellow' | 'orange' | 'red' | 'purple';
  title: string;
  description: string;
  createdAt?: string;
}

export interface ScoreResponse {
  cityId: number;
  cityName?: string;
  state?: string;
  score: number;
  classification: string;
  symbol: string;
  aqi: number;
  temperature: number;
  humidity: number;
  windSpeed: number;
  uvIndex: number;
  createdAt?: string;
}

export interface AIReportResponse {
  city: string;
  summary: string;
  recommendation: string;
  createdAt?: string;
}

export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  message: string;
  answer: string;
}
