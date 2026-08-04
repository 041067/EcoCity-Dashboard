import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { City, Score } from '../../types';
import { getHistory } from '../../services/api';
import { AsyncState } from '../../components/AsyncState';
import { HistoryChart } from '../../components/charts/HistoryChart';
import { MetricCard } from '../../components/cards/MetricCard';

interface DashboardChartsProps {
  city: City;
  score?: Score;
}

function scoreTone(score?: number): 'emerald' | 'amber' | 'red' | 'default' {
  if (score === undefined) return 'default';
  if (score >= 70) return 'emerald';
  if (score >= 40) return 'amber';
  return 'red';
}

export function DashboardCharts({ city, score }: DashboardChartsProps) {
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    setEnabled(true);
  }, []);

  const history = useQuery({
    queryKey: ['history', city.id],
    queryFn: () => getHistory(city.name),
    enabled,
  });

  const latest = history.data?.[0];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
        <MetricCard
          label="Temperatura"
          value={latest ? latest.temperature.toFixed(1) : '—'}
          unit="°C"
          icon="🌡️"
          tone="red"
        />
        <MetricCard
          label="Umidade"
          value={latest ? latest.humidity.toFixed(0) : '—'}
          unit="%"
          icon="💧"
          tone="sky"
        />
        <MetricCard
          label="Vento"
          value={latest ? latest.wind_speed.toFixed(0) : '—'}
          unit="km/h"
          icon="🌬️"
          tone="violet"
        />
        <MetricCard
          label="Índice UV"
          value={latest ? latest.uv_index.toFixed(1) : '—'}
          icon="☀️"
          tone="amber"
        />
        <MetricCard
          label="AQI"
          value={latest?.aqi !== undefined ? String(latest.aqi) : '—'}
          icon="🏭"
          tone={latest?.aqi && latest.aqi > 100 ? 'red' : 'emerald'}
        />
        <MetricCard
          label="Eco Score"
          value={score ? String(Math.round(score.score)) : '—'}
          icon={score?.symbol ?? '🌿'}
          tone={scoreTone(score?.score)}
        />
      </div>

      {score && (
        <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
              Eco Score — {score.city_name}
            </h3>
            <span className="rounded-full px-3 py-1 text-sm font-bold text-white bg-emerald-600">
              {score.symbol} {score.classification} ({Math.round(score.score)})
            </span>
          </div>
          <div className="mt-3 h-3 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
            <div
              className="h-full rounded-full bg-gradient-to-r from-red-500 via-amber-500 to-emerald-500"
              style={{ width: `${Math.max(0, Math.min(100, score.score))}%` }}
            />
          </div>
        </div>
      )}

      <AsyncState
        isLoading={history.isLoading}
        isError={history.isError}
        isEmpty={!history.data || history.data.length === 0}
        error={history.error}
        onRetry={() => history.refetch()}
        emptyMessage="Sem histórico nas últimas 24 horas"
      >
        <div className="grid gap-4 lg:grid-cols-2">
          <HistoryChart title="Temperatura (°C)" readings={history.data ?? []} dataKey="temperature" color="#ef4444" />
          <HistoryChart title="Umidade (%)" readings={history.data ?? []} dataKey="humidity" color="#0ea5e9" />
          <HistoryChart title="Velocidade do vento (km/h)" readings={history.data ?? []} dataKey="wind_speed" color="#8b5cf6" />
          <HistoryChart title="Qualidade do ar (PM2.5 µg/m³)" readings={history.data ?? []} dataKey="pm25" color="#10b981" />
        </div>
      </AsyncState>
    </div>
  );
}
