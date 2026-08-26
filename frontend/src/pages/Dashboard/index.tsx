import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useCities, useESGPriorities, useLatestReadings, useOrganizations, useScores } from '../../hooks/useApiQueries';
import { AsyncState } from '../../components/AsyncState';
import { AppIcon } from '../../components/icons/AppIcon';
import { MapView } from '../../components/map/MapView';
import { DashboardCharts } from './DashboardCharts';
import type { City } from '../../types';

function enrichCities(cities: City[], scores: { city_id: number; score: number }[] | undefined): City[] {
  const scoreMap = new Map((scores ?? []).map((s) => [s.city_id, s.score]));
  return cities.map((c) => ({ ...c, score: scoreMap.get(c.id) }));
}

export function Dashboard() {
  const citiesQuery = useCities();
  const scoresQuery = useScores();
  const readingsQuery = useLatestReadings();
  const organizationsQuery = useOrganizations();
  const organizationId = organizationsQuery.data?.[0]?.id;
  const prioritiesQuery = useESGPriorities(organizationId);
  const [selectedCityId, setSelectedCityId] = useState<number | null>(null);

  const cities = useMemo(
    () => enrichCities(citiesQuery.data ?? [], scoresQuery.data),
    [citiesQuery.data, scoresQuery.data],
  );

  const selectedCity =
    cities.find((c) => c.id === selectedCityId) ??
    cities.find((c) => c.id === (readingsQuery.data?.[0]?.city_id ?? -1)) ??
    cities[0];

  const selectedScore = scoresQuery.data?.find((s) => s.city_id === selectedCity?.id);
  const immediateTopics = (prioritiesQuery.data ?? []).filter((item) => item.priority === 'critical' || item.priority === 'high').slice(0, 3);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Monitoramento em tempo real das cidades
        </p>
      </div>

      {organizationId && <section className="rounded-2xl border border-emerald-200 bg-gradient-to-r from-emerald-50 to-cyan-50 p-5 shadow-sm dark:border-emerald-900 dark:from-emerald-950/40 dark:to-gray-900"><div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center"><div><p className="inline-flex items-center gap-2 text-sm font-bold uppercase tracking-widest text-emerald-700 dark:text-emerald-300"><AppIcon name="bot" className="h-4 w-4" />EcoCity AI</p><h2 className="mt-2 text-lg font-bold text-gray-900 dark:text-white">{immediateTopics.length ? `${immediateTopics.length} tema(s) exigem atenção` : 'Contexto ESG pronto para análise'}</h2><div className="mt-3 flex flex-wrap gap-2">{immediateTopics.map((item) => <span key={item.topic_id} className="rounded-full bg-white px-3 py-1 text-xs font-bold text-gray-700 shadow-sm dark:bg-gray-800 dark:text-gray-200">{item.priority === 'critical' ? '🔴' : '🟠'} {item.topic.name}</span>)}{!immediateTopics.length && <span className="text-sm text-gray-600 dark:text-gray-300">Execute a análise ESG e abra o Copilot para uma interpretação fundamentada.</span>}</div></div><div className="flex flex-col gap-2 sm:items-end"><Link to={`/esg/copilot?organization=${organizationId}`} className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-bold text-white hover:bg-emerald-700"><AppIcon name="brain" className="h-4 w-4" />Ver análise completa</Link><Link to={`/esg/recommendations?organization=${organizationId}`} className="text-center text-sm font-semibold text-emerald-700 hover:underline dark:text-emerald-300">Ver recomendações</Link></div></div></section>}

      <div className="grid gap-4 lg:grid-cols-5">
        <AsyncState
          isLoading={citiesQuery.isLoading}
          isError={citiesQuery.isError}
          isEmpty={cities.length === 0}
          error={citiesQuery.error}
          onRetry={() => citiesQuery.refetch()}
          emptyMessage="Nenhuma cidade cadastrada"
        >
          <div className="flex flex-col gap-3">
            <label className="text-sm font-medium text-gray-600 dark:text-gray-300">
              Cidade selecionada
            </label>
            <select
              value={selectedCity?.id ?? ''}
              onChange={(e) => setSelectedCityId(Number(e.target.value))}
              className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-emerald-500 focus:outline-none dark:border-gray-700 dark:bg-gray-900 dark:text-white"
            >
              {cities.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}/{c.state}
                </option>
              ))}
            </select>
            <div className="h-64 overflow-hidden rounded-xl border border-gray-200 shadow-sm dark:border-gray-800 lg:h-80">
              <MapView cities={cities} selectedCity={selectedCity ?? null} onCitySelect={(c) => setSelectedCityId(c.id)} />
            </div>
            <p className="text-xs text-gray-400">
              Clique em um marcador para selecionar a cidade
            </p>
          </div>
        </AsyncState>

        <div className="lg:col-span-4">
          {selectedCity ? (
            <DashboardCharts city={selectedCity} score={selectedScore} />
          ) : (
            <AsyncState
              isLoading={citiesQuery.isLoading}
              isError={citiesQuery.isError}
              isEmpty
              error={citiesQuery.error}
              emptyMessage="Selecione uma cidade"
            >
              <></>
            </AsyncState>
          )}
        </div>
      </div>
    </div>
  );
}
