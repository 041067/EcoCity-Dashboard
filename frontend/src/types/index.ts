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

export type OrganizationType = 'company' | 'municipality' | 'public_agency' | 'university' | 'other';
export type SiteType = 'headquarters' | 'factory' | 'warehouse' | 'office' | 'municipal_region' | 'other';
export type StakeholderType =
  | 'employees'
  | 'customers'
  | 'suppliers'
  | 'investors'
  | 'government'
  | 'community'
  | 'environment'
  | 'partners'
  | 'other';
export type ESGPillar = 'E' | 'S' | 'G';
export type ESGMaturityLevel = 'initial' | 'developing' | 'structured' | 'advanced';

export interface Organization {
  id: number;
  name: string;
  organization_type: OrganizationType;
  industry_sector?: string | null;
  document?: string | null;
  country: string;
  state?: string | null;
  city?: string | null;
  employee_count?: number | null;
  description?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface Site {
  id: number;
  organization_id: number;
  name: string;
  site_type: SiteType;
  latitude?: number | null;
  longitude?: number | null;
  city_id?: number | null;
  city?: City | null;
  employee_count?: number | null;
  area_m2?: number | null;
  created_at?: string;
  updated_at?: string;
}

export interface ESGProfile {
  id: number;
  organization_id: number;
  reporting_year: number;
  environmental_enabled: boolean;
  social_enabled: boolean;
  governance_enabled: boolean;
  sustainability_strategy?: string | null;
  esg_maturity_level: ESGMaturityLevel;
  created_at?: string;
  updated_at?: string;
}

export interface Stakeholder {
  id: number;
  organization_id: number;
  name: string;
  stakeholder_type: StakeholderType;
  influence_level: number;
  impact_level: number;
  description?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface ESGTopic {
  id: number;
  code: string;
  name: string;
  pillar: ESGPillar;
  description?: string | null;
  active: boolean;
}

export interface OrganizationESGTopic {
  id: number;
  organization_id: number;
  topic_id: number;
  enabled: boolean;
  priority: number;
  notes?: string | null;
  topic: ESGTopic;
  created_at?: string;
  updated_at?: string;
}

export interface OrganizationOverview {
  organization: string;
  sites: number;
  stakeholders: number;
  esg_topics: number;
  environmental_topics: number;
  social_topics: number;
  governance_topics: number;
}
