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

export type MaterialityStatus = 'draft' | 'in_review' | 'completed';
export type PriorityLevel = 'low' | 'medium' | 'high' | 'critical';
export type EvidenceType = 'manual' | 'internal_data' | 'external_data' | 'document' | 'stakeholder';

export interface ImpactAssessmentInput {
  severity: number;
  scope: number;
  likelihood: number;
  remediability: number;
}

export interface FinancialAssessmentInput {
  revenue_impact: number;
  cost_impact: number;
  asset_impact: number;
  financing_impact: number;
  regulatory_impact: number;
}

export interface StakeholderAssessmentInput {
  stakeholder_id: number;
  relevance: number;
  concern_level: number;
  influence: number;
  comment?: string | null;
}

export interface AssessmentEvidenceInput {
  evidence_type: EvidenceType;
  source: string;
  description: string;
  reference?: string | null;
}

export interface MaterialityAssessmentCreate {
  topic_id: number;
  reporting_year: number;
  impact?: ImpactAssessmentInput;
  financial?: FinancialAssessmentInput;
  stakeholders?: StakeholderAssessmentInput[];
  evidences?: AssessmentEvidenceInput[];
  status: MaterialityStatus;
}

export interface ImpactAssessment extends ImpactAssessmentInput {
  id: number;
  materiality_assessment_id: number;
}

export interface FinancialAssessment extends FinancialAssessmentInput {
  id: number;
  materiality_assessment_id: number;
}

export interface StakeholderAssessment extends StakeholderAssessmentInput {
  id: number;
  materiality_assessment_id: number;
  stakeholder: Stakeholder;
  created_at?: string;
  updated_at?: string;
}

export interface AssessmentEvidence extends AssessmentEvidenceInput {
  id: number;
  materiality_assessment_id: number;
  created_at?: string;
}

export interface MaterialityAssessment {
  id: number;
  organization_id: number;
  topic_id: number;
  reporting_year: number;
  impact_score: number | null;
  financial_score: number | null;
  stakeholder_score: number | null;
  materiality_score: number | null;
  priority_level: PriorityLevel | null;
  status: MaterialityStatus;
  topic: ESGTopic;
  impact_assessment: ImpactAssessment | null;
  financial_assessment: FinancialAssessment | null;
  stakeholder_assessments: StakeholderAssessment[];
  evidences: AssessmentEvidence[];
  created_at?: string;
  updated_at?: string;
}

export interface MaterialityMatrix {
  reporting_year: number | null;
  assessments: MaterialityAssessment[];
}

export interface MaterialityExplanation {
  topic: string;
  reporting_year: number;
  status: MaterialityStatus;
  materiality_score: number | null;
  priority: PriorityLevel | null;
  components: { impact: number | null; financial: number | null; stakeholder: number | null };
  impact_assessment: ImpactAssessment | null;
  financial_assessment: FinancialAssessment | null;
  stakeholder_assessments: StakeholderAssessment[];
  evidences: AssessmentEvidence[];
  weights: { impact: number; financial: number; stakeholder: number };
}

export interface ESGIndicator {
  id: number;
  code: string;
  name: string;
  pillar: ESGPillar;
  category: string;
  unit: string;
  description?: string | null;
  source_type: string;
  active: boolean;
}

export type FreshnessStatus = 'fresh' | 'aging' | 'stale';

export interface IndicatorValue {
  id: number;
  indicator: ESGIndicator;
  organization_id: number;
  site_id: number;
  site_name?: string | null;
  value: number;
  unit: string;
  source: string;
  source_reference?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  observed_at?: string | null;
  collected_at: string;
  source_metadata?: Record<string, unknown> | null;
  quality_score: number;
  freshness_score: number;
  freshness_status: FreshnessStatus;
  relevance_score: number;
  confidence_score: number;
}

export interface ProviderStatus {
  name: string;
  display_name: string;
  status: 'unknown' | 'online' | 'degraded' | 'offline';
  last_sync?: string | null;
  data_categories: string[];
  priority: number;
  last_message?: string | null;
}

export interface ProviderSyncItem {
  provider: string;
  status: string;
  cached: boolean;
  values_collected: number;
  duration_ms?: number | null;
  message?: string | null;
}

export interface SiteSyncResponse {
  site_id: number;
  results: ProviderSyncItem[];
}

export interface MaterialityExternalEvidence {
  id: number;
  relevance: string;
  linked_at?: string | null;
  indicator_value: IndicatorValue;
}
