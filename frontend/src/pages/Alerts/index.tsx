import { useMemo, useState } from 'react';
import { useAlerts, useCities } from '../../hooks/useApiQueries';
import { AsyncState } from '../../components/AsyncState';
import type { Alert } from '../../types';

const SEVERITY_STYLES: Record<string, { bg: string; icon: string; label: string }> = {
  danger: { bg: 'border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-950', icon: '🔴', label: 'Crítico' },
  warning: { bg: 'border-amber-300 bg-amber-50 dark:border-amber-800 dark:bg-amber-950', icon: '🟡', label: 'Atenção' },
  info: { bg: 'border-emerald-300 bg-emerald-50 dark:border-emerald-800 dark:bg-emerald-950', icon: '🟢', label: 'Normal' },
};

export function AlertsPage() {
  const [cityFilter, setCityFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const citiesQuery = useCities();
  const alertsQuery = useAlerts(cityFilter || undefined);

  const filtered = useMemo(() => {
    const items = alertsQuery.data ?? [];
    if (!severityFilter) return items;
    return items.filter((a: Alert) => a.severity === severityFilter);
  }, [alertsQuery.data, severityFilter]);

  const severityCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const a of alertsQuery.data ?? []) {
      counts[a.severity] = (counts[a.severity] ?? 0) + 1;
    }
    return counts;
  }, [alertsQuery.data]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Alertas Ambientais</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Regras automáticas: AQI &gt; 100, temperatura &gt; 38°C, ventos fortes, UV extremo
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {(['danger', 'warning', 'info'] as const).map((sev) => {
          const style = SEVERITY_STYLES[sev];
          return (
            <div key={sev} className={`rounded-xl border p-4 ${style.bg}`}>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-300">
                {style.icon} {style.label}
              </p>
              <p className="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
                {severityCounts[sev] ?? 0}
              </p>
            </div>
          );
        })}
        <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-300">📊 Total</p>
          <p className="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
            {(alertsQuery.data ?? []).length}
          </p>
        </div>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row">
        <select
          value={cityFilter}
          onChange={(e) => setCityFilter(e.target.value)}
          className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-emerald-500 focus:outline-none dark:border-gray-700 dark:bg-gray-900 dark:text-white"
          aria-label="Filtrar por cidade"
        >
          <option value="">Todas as cidades</option>
          {(citiesQuery.data ?? []).map((c) => (
            <option key={c.id} value={c.name}>
              {c.name}
            </option>
          ))}
        </select>
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-emerald-500 focus:outline-none dark:border-gray-700 dark:bg-gray-900 dark:text-white"
          aria-label="Filtrar por severidade"
        >
          <option value="">Todas as severidades</option>
          <option value="danger">Crítico</option>
          <option value="warning">Atenção</option>
          <option value="info">Normal</option>
        </select>
      </div>

      <AsyncState
        isLoading={alertsQuery.isLoading}
        isError={alertsQuery.isError}
        isEmpty={filtered.length === 0}
        error={alertsQuery.error}
        onRetry={() => alertsQuery.refetch()}
        emptyMessage="Nenhum alerta encontrado com os filtros atuais"
      >
        <ul className="space-y-3">
          {filtered.map((alert) => {
            const style = SEVERITY_STYLES[alert.severity] ?? SEVERITY_STYLES.info;
            return (
              <li
                key={alert.id}
                className={`flex flex-col gap-1 rounded-xl border p-4 sm:flex-row sm:items-center sm:justify-between ${style.bg}`}
              >
                <div className="flex items-start gap-3">
                  <span className="text-xl">{style.icon}</span>
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">{alert.title}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{alert.description}</p>
                  </div>
                </div>
                <div className="flex shrink-0 items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                  <span className="font-medium">{alert.city_name}</span>
                  {alert.created_at && (
                    <span>{new Date(alert.created_at).toLocaleString('pt-BR')}</span>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      </AsyncState>
    </div>
  );
}
