import { useQuery } from '@tanstack/react-query';
import {
  getAlerts,
  getCities,
  getLatestReadings,
  getLatestReport,
  getScores,
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