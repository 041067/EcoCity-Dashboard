import { useQuery } from '@tanstack/react-query';
import {
  getAlerts,
  getCities,
  getESGTopics,
  getLatestReadings,
  getLatestReport,
  getOrganization,
  getOrganizationOverview,
  getOrganizations,
  getOrganizationTopics,
  getScores,
  getSites,
  getStakeholders,
} from '../services/api';

export function useCities() {
  return useQuery({
    queryKey: ['cities'],
    queryFn: getCities,
    staleTime: 60_000,
  });
}

export function useLatestReadings() {
  return useQuery({
    queryKey: ['latest-readings'],
    queryFn: getLatestReadings,
    refetchInterval: 60_000,
  });
}

export function useScores() {
  return useQuery({
    queryKey: ['scores'],
    queryFn: getScores,
    refetchInterval: 60_000,
  });
}

export function useAlerts(city?: string) {
  return useQuery({
    queryKey: ['alerts', city ?? 'all'],
    queryFn: () => getAlerts(city),
    refetchInterval: 60_000,
  });
}

export function useLatestReport(city?: string) {
  return useQuery({
    queryKey: ['report', city ?? ''],
    queryFn: () => getLatestReport(city!),
    enabled: Boolean(city),
    retry: false,
  });
}

export function useOrganizations() {
  return useQuery({ queryKey: ['esg', 'organizations'], queryFn: getOrganizations });
}

export function useOrganization(organizationId?: number) {
  return useQuery({
    queryKey: ['esg', 'organization', organizationId],
    queryFn: () => getOrganization(organizationId!),
    enabled: Boolean(organizationId),
  });
}

export function useESGTopics() {
  return useQuery({ queryKey: ['esg', 'topics'], queryFn: getESGTopics, staleTime: 300_000 });
}

export function useOrganizationOverview(organizationId?: number) {
  return useQuery({
    queryKey: ['esg', 'overview', organizationId],
    queryFn: () => getOrganizationOverview(organizationId!),
    enabled: Boolean(organizationId),
  });
}

export function useOrganizationTopics(organizationId?: number) {
  return useQuery({
    queryKey: ['esg', 'organization-topics', organizationId],
    queryFn: () => getOrganizationTopics(organizationId!),
    enabled: Boolean(organizationId),
  });
}

export function useOrganizationSites(organizationId?: number) {
  return useQuery({
    queryKey: ['esg', 'sites', organizationId],
    queryFn: () => getSites(organizationId!),
    enabled: Boolean(organizationId),
  });
}

export function useOrganizationStakeholders(organizationId?: number) {
  return useQuery({
    queryKey: ['esg', 'stakeholders', organizationId],
    queryFn: () => getStakeholders(organizationId!),
    enabled: Boolean(organizationId),
  });
}
