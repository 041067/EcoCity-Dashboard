import { useMemo, useState } from 'react';
import { useCities, useScores } from '../../hooks/useApiQueries';
import { AsyncState } from '../../components/AsyncState';
import type { Score } from '../../types';

function Metric({ label, a, b, unit, better }: { label: string; a?: number; b?: number; unit: string; better: 'higher' | 'lower' }) {
  const fmt = (v?: number) => (v === undefined ? '—' : `${Number.isInteger(v) ? v : v.toFixed(1)}${unit}`);
  const winner = (x?: number, y?: number) => {
    if (x === undefined || y === undefined) return null;
    if (better === 'higher') return x > y ? 'a' : x < y ? 'b' : null;
    return x < y ? 'a' : x > y ? 'b' : null;
  };
  const w = winner(a, b);
  return (
    <div className="grid grid-cols-3 items-center gap-2 border-b border-gray-100 py-3 last:border-0 dark:border-gray-800">
      <p className={`text-right font-bold ${w === 'a' ? 'text-emerald-600 dark:text-emerald-400' : ''}`}>{fmt(a)}</p>
      <p className="text-center text-sm text-gray-500 dark:text-gray-400">{label}</p>
      <p className={`font-bold ${w === 'b' ? 'text-emerald-600 dark:text-emerald-400' : ''}`}>{fmt(b)}</p>
    </div>
  );
}

export function ComparePage() {
  const citiesQuery = useCities();
  const scoresQuery = useScores();
  const [cityAId, setCityAId] = useState<number | null>(null);
  const [cityBId, setCityBId] = useState<number | null>(null);

  const cities = citiesQuery.data ?? [];
  const cityA = cities.find((c) => c.id === cityAId);
  const cityB = cities.find((c) => c.id === cityBId);

  const scoreOf = (id?: number | null): Score | undefined =>
    scoresQuery.data?.find((s) => s.city_id === id);

  const scoreA = scoreOf(cityAId);
  const scoreB = scoreOf(cityBId);

  const comparison = useMemo(() => {
    if (!cityA && !cityB) return null;
    return [
      { label: 'Eco Score', a: scoreA?.score, b: scoreB?.score, unit: '', better: 'higher' as const },
      { label: 'Temperatura', a: scoreA?.temperature, b: scoreB?.temperature, unit: '°C', better: 'lower' as const },
      { label: 'Umidade', a: scoreA?.humidity, b: scoreB?.humidity, unit: '%', better: 'lower' as const },
      { label: 'AQI', a: scoreA?.aqi, b: scoreB?.aqi, unit: '', better: 'lower' as const },
      { label: 'Vento', a: scoreA?.wind_speed, b: scoreB?.wind_speed, unit: ' km/h', better: 'lower' as const },
      { label: 'Índice UV', a: scoreA?.uv_index, b: scoreB?.uv_index, unit: '', better: 'lower' as const },
    ];
  }, [cityA, cityB, scoreA, scoreB]);

  const otherCities = (selectedId: number | null) => cities.filter((c) => c.id !== selectedId);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Comparador de Cidades</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Compare o desempenho ambiental entre duas cidades
        </p>
      </div>

      <AsyncState
        isLoading={citiesQuery.isLoading || scoresQuery.isLoading}
        isError={citiesQuery.isError || scoresQuery.isError}
        isEmpty={cities.length < 2}
        error={citiesQuery.error ?? scoresQuery.error}
        onRetry={() => {
          void citiesQuery.refetch();
          void scoresQuery.refetch();
        }}
        emptyMessage="Cadastre pelo menos duas cidades para comparar"
      >
        <div className="grid gap-6 lg:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-600 dark:text-gray-300">
              Cidade A
            </label>
            <select
              value={cityAId ?? ''}
              onChange={(e) => setCityAId(Number(e.target.value) || null)}
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-emerald-500 focus:outline-none dark:border-gray-700 dark:bg-gray-900 dark:text-white"
            >
              <option value="">Selecione...</option>
              {otherCities(cityBId).map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}/{c.state}
                </option>
              ))}
            </select>
            {scoreA && (
              <div className="mt-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-center dark:border-emerald-900 dark:bg-emerald-950">
                <p className="text-sm text-emerald-700 dark:text-emerald-300">{scoreA.city_name}</p>
                <p className="text-4xl font-bold text-emerald-700 dark:text-emerald-300">
                  {scoreA.symbol} {Math.round(scoreA.score)}
                </p>
                <p className="text-sm text-emerald-600 dark:text-emerald-400">{scoreA.classification}</p>
              </div>
            )}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-600 dark:text-gray-300">
              Cidade B
            </label>
            <select
              value={cityBId ?? ''}
              onChange={(e) => setCityBId(Number(e.target.value) || null)}
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-emerald-500 focus:outline-none dark:border-gray-700 dark:bg-gray-900 dark:text-white"
            >
              <option value="">Selecione...</option>
              {otherCities(cityAId).map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}/{c.state}
                </option>
              ))}
            </select>
            {scoreB && (
              <div className="mt-3 rounded-xl border border-sky-200 bg-sky-50 p-4 text-center dark:border-sky-900 dark:bg-sky-950">
                <p className="text-sm text-sky-700 dark:text-sky-300">{scoreB.city_name}</p>
                <p className="text-4xl font-bold text-sky-700 dark:text-sky-300">
                  {scoreB.symbol} {Math.round(scoreB.score)}
                </p>
                <p className="text-sm text-sky-600 dark:text-sky-400">{scoreB.classification}</p>
              </div>
            )}
          </div>
        </div>

        {cityA && cityB && comparison && (
          <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="grid grid-cols-3 border-b border-gray-200 pb-2 dark:border-gray-800">
              <p className="text-right font-bold text-emerald-600 dark:text-emerald-400">{cityA.name}</p>
              <p className="text-center text-sm font-semibold text-gray-500 dark:text-gray-400">Métrica</p>
              <p className="font-bold text-sky-600 dark:text-sky-400">{cityB.name}</p>
            </div>
            {comparison.map((m) => (
              <Metric key={m.label} {...m} />
            ))}
          </div>
        )}
      </AsyncState>
    </div>
  );
}
