import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useCities, useLatestReport } from '../../hooks/useApiQueries';
import { AsyncState } from '../../components/AsyncState';
import { generateReport } from '../../services/api';
import type { AIReport } from '../../types';

export function ReportsPage() {
  const citiesQuery = useCities();
  const [city, setCity] = useState<string>('');
  const latest = useLatestReport(city || undefined);
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (cityName: string) => generateReport(cityName),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['report'] });
    },
  });

  const report: AIReport | undefined =
    mutation.data ?? (latest.data as AIReport | undefined);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Relatórios IA</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Relatório ambiental gerado pela IA com base nas últimas 24 horas
        </p>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-600 dark:text-gray-300">Cidade</label>
          <select
            value={city}
            onChange={(e) => setCity(e.target.value)}
            className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-emerald-500 focus:outline-none dark:border-gray-700 dark:bg-gray-900 dark:text-white"
          >
            <option value="">Selecione...</option>
            {(citiesQuery.data ?? []).map((c) => (
              <option key={c.id} value={c.name}>
                {c.name}/{c.state}
              </option>
            ))}
          </select>
        </div>
        <button
          type="button"
          disabled={!city || mutation.isPending}
          onClick={() => mutation.mutate(city)}
          className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {mutation.isPending ? 'Gerando...' : '🤖 Gerar relatório'}
        </button>
      </div>

      {mutation.isError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-300">
          Não foi possível gerar o relatório. Verifique se há dados coletados nas últimas 24 horas.
        </div>
      )}

      {!city && (
        <AsyncState isLoading={false} isError={false} isEmpty>
          <></>
        </AsyncState>
      )}

      {city && (
        <AsyncState
          isLoading={latest.isLoading || mutation.isPending}
          isError={false}
          isEmpty={!report}
          error={latest.error}
          onRetry={() => latest.refetch()}
          emptyMessage="Nenhum relatório disponível ainda. Clique em 'Gerar relatório'."
        >
          {report && (
            <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
              <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
                <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                  Relatório — {report.city}
                </h2>
                {report.created_at && (
                  <span className="text-xs text-gray-400">
                    {new Date(report.created_at).toLocaleString('pt-BR')}
                  </span>
                )}
              </div>
              <div className="space-y-4">
                <div>
                  <h3 className="mb-1 text-sm font-semibold text-emerald-600 dark:text-emerald-400">
                    📋 Situação
                  </h3>
                  <p className="whitespace-pre-line text-sm text-gray-700 dark:text-gray-300">
                    {report.summary}
                  </p>
                </div>
                {report.recommendation && (
                  <div>
                    <h3 className="mb-1 text-sm font-semibold text-sky-600 dark:text-sky-400">
                      🏛️ Recomendações
                    </h3>
                    <p className="whitespace-pre-line text-sm text-gray-700 dark:text-gray-300">
                      {report.recommendation}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </AsyncState>
      )}
    </div>
  );
}
