import { useMemo, useState } from 'react';
import { useCities, useLatestReadings, useScores } from '../../hooks/useApiQueries';
import { AsyncState } from '../../components/AsyncState';
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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Monitoramento em tempo real das cidades
        </p>
      </div>

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
