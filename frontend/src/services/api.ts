import axios from 'axios';
import type {
  AIReport,
  Alert,
  ChatRequest,
  ChatResponse,
  City,
  ESGProfile,
  ESGIndicator,
  ESGTopic,
  HealthResponse,
  MaterialityAssessment,
  MaterialityAssessmentCreate,
  MaterialityExplanation,
  MaterialityExternalEvidence,
  MaterialityMatrix,
  Organization,
  OrganizationESGTopic,
  OrganizationOverview,
  Reading,
  Score,
  Site,
  SiteSyncResponse,
  Stakeholder,
  StakeholderAssessment,
  StakeholderAssessmentInput,
  IndicatorValue,
  ProviderStatus,
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

type OrganizationPayload = Omit<Organization, 'id' | 'created_at' | 'updated_at'>;
type SitePayload = Omit<Site, 'id' | 'organization_id' | 'city' | 'created_at' | 'updated_at'>;
type ProfilePayload = Omit<ESGProfile, 'id' | 'organization_id' | 'created_at' | 'updated_at'>;
type StakeholderPayload = Omit<Stakeholder, 'id' | 'organization_id' | 'created_at' | 'updated_at'>;

export async function createOrganization(payload: OrganizationPayload): Promise<Organization> {
  const { data } = await api.post<Organization>('/esg/organizations', payload);
  return data;
}

export async function getOrganizations(): Promise<Organization[]> {
  const { data } = await api.get<Organization[]>('/esg/organizations');
  return data;
}

export async function getOrganization(organizationId: number): Promise<Organization> {
  const { data } = await api.get<Organization>(`/esg/organizations/${organizationId}`);
  return data;
}

export async function createSite(organizationId: number, payload: SitePayload): Promise<Site> {
  const { data } = await api.post<Site>(`/esg/organizations/${organizationId}/sites`, payload);
  return data;
}

export async function getSites(organizationId: number): Promise<Site[]> {
  const { data } = await api.get<Site[]>(`/esg/organizations/${organizationId}/sites`);
  return data;
}

export async function updateESGProfile(organizationId: number, payload: ProfilePayload): Promise<ESGProfile> {
  const { data } = await api.put<ESGProfile>(`/esg/organizations/${organizationId}/profile`, payload);
  return data;
}

export async function createStakeholder(
  organizationId: number,
  payload: StakeholderPayload,
): Promise<Stakeholder> {
  const { data } = await api.post<Stakeholder>(`/esg/organizations/${organizationId}/stakeholders`, payload);
  return data;
}

export async function getStakeholders(organizationId: number): Promise<Stakeholder[]> {
  const { data } = await api.get<Stakeholder[]>(`/esg/organizations/${organizationId}/stakeholders`);
  return data;
}

export async function getESGTopics(): Promise<ESGTopic[]> {
  const { data } = await api.get<ESGTopic[]>('/esg/topics');
  return data;
}

export async function saveOrganizationTopic(
  organizationId: number,
  payload: Pick<OrganizationESGTopic, 'topic_id' | 'enabled' | 'priority' | 'notes'>,
): Promise<OrganizationESGTopic> {
  const { data } = await api.post<OrganizationESGTopic>(`/esg/organizations/${organizationId}/topics`, payload);
  return data;
}

export async function getOrganizationTopics(organizationId: number): Promise<OrganizationESGTopic[]> {
  const { data } = await api.get<OrganizationESGTopic[]>(`/esg/organizations/${organizationId}/topics`);
  return data;
}

export async function getOrganizationOverview(organizationId: number): Promise<OrganizationOverview> {
  const { data } = await api.get<OrganizationOverview>(`/esg/organizations/${organizationId}/overview`);
  return data;
}

export async function createMaterialityAssessment(
  organizationId: number,
  payload: MaterialityAssessmentCreate,
): Promise<MaterialityAssessment> {
  const { data } = await api.post<MaterialityAssessment>(`/esg/organizations/${organizationId}/materiality`, payload);
  return data;
}

export async function getMaterialityAssessments(
  organizationId: number,
  reportingYear?: number,
): Promise<MaterialityAssessment[]> {
  const { data } = await api.get<MaterialityAssessment[]>(`/esg/organizations/${organizationId}/materiality`, {
    params: reportingYear ? { reporting_year: reportingYear } : undefined,
  });
  return data;
}

export async function getMaterialityMatrix(
  organizationId: number,
  reportingYear?: number,
): Promise<MaterialityMatrix> {
  const { data } = await api.get<MaterialityMatrix>(`/esg/organizations/${organizationId}/materiality/matrix`, {
    params: reportingYear ? { reporting_year: reportingYear } : undefined,
  });
  return data;
}

export async function getMaterialityPriorities(
  organizationId: number,
  reportingYear?: number,
): Promise<MaterialityAssessment[]> {
  const { data } = await api.get<MaterialityAssessment[]>(`/esg/organizations/${organizationId}/materiality/priorities`, {
    params: reportingYear ? { reporting_year: reportingYear } : undefined,
  });
  return data;
}

export async function getMaterialityExplanation(
  organizationId: number,
  assessmentId: number,
): Promise<MaterialityExplanation> {
  const { data } = await api.get<MaterialityExplanation>(
    `/esg/organizations/${organizationId}/materiality/${assessmentId}/explanation`,
  );
  return data;
}

export async function saveMaterialityStakeholderAssessment(
  assessmentId: number,
  payload: StakeholderAssessmentInput,
): Promise<StakeholderAssessment> {
  const { data } = await api.post<StakeholderAssessment>(
    `/esg/materiality/${assessmentId}/stakeholders`,
    payload,
  );
  return data;
}

export async function getESGIndicators(category?: string): Promise<ESGIndicator[]> {
  const { data } = await api.get<ESGIndicator[]>('/esg/indicators', { params: category ? { category } : undefined });
  return data;
}

export async function getProviderStatuses(): Promise<ProviderStatus[]> {
  const { data } = await api.get<ProviderStatus[]>('/esg/providers');
  return data;
}

export async function getOrganizationIndicators(organizationId: number, category?: string): Promise<IndicatorValue[]> {
  const { data } = await api.get<IndicatorValue[]>(`/esg/organizations/${organizationId}/indicators`, {
    params: category ? { category } : undefined,
  });
  return data;
}

export async function getSiteIndicators(siteId: number, category?: string): Promise<IndicatorValue[]> {
  const { data } = await api.get<IndicatorValue[]>(`/esg/sites/${siteId}/indicators`, {
    params: category ? { category } : undefined,
  });
  return data;
}

export async function getSiteClimateRisk(siteId: number): Promise<IndicatorValue[]> {
  const { data } = await api.get<IndicatorValue[]>(`/esg/sites/${siteId}/climate-risk`);
  return data;
}

export async function getSiteAirQuality(siteId: number): Promise<IndicatorValue[]> {
  const { data } = await api.get<IndicatorValue[]>(`/esg/sites/${siteId}/air-quality`);
  return data;
}

export async function getSiteEnergy(siteId: number): Promise<IndicatorValue[]> {
  const { data } = await api.get<IndicatorValue[]>(`/esg/sites/${siteId}/energy`);
  return data;
}

export async function syncSiteIntelligence(siteId: number): Promise<SiteSyncResponse> {
  const { data } = await api.post<SiteSyncResponse>(`/esg/sites/${siteId}/sync`);
  return data;
}

export async function getMaterialityExternalEvidence(assessmentId: number): Promise<MaterialityExternalEvidence[]> {
  const { data } = await api.get<MaterialityExternalEvidence[]>(`/esg/materiality/${assessmentId}/evidence`);
  return data;
}

export default api;
