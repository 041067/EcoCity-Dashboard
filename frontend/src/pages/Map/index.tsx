import { useCities, useScores } from '../../hooks/useApiQueries';
import { AsyncState } from '../../components/AsyncState';
import { MapView } from '../../components/map/MapView';
import type { City } from '../../types';

export function MapPage() {
  const citiesQuery = useCities();
  const scoresQuery = useScores();

  const scoreMap = new Map((scoresQuery.data ?? []).map((s) => [s.city_id, s.score]));
  const cities: City[] = (citiesQuery.data ?? []).map((c) => ({
    ...c,
    score: scoreMap.get(c.id),
  }));

  const legend = [
    { color: '#10b981', label: 'Excelente (70-100)' },
    { color: '#fbbf24', label: 'Moderado (40-69)' },
    { color: '#ef4444', label: 'Crítico (0-39)' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Mapa Ambiental</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Status do Eco Score por cidade monitorada
        </p>
      </div>

      <div className="flex flex-wrap gap-3">
        {legend.map((item) => (
          <span
            key={item.label}
            className="flex items-center gap-2 rounded-full border border-gray-200 bg-white px-3 py-1 text-xs font-medium text-gray-600 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
          >
            <span className="h-3 w-3 rounded-full" style={{ backgroundColor: item.color }} />
            {item.label}
          </span>
        ))}
      </div>

      <AsyncState
        isLoading={citiesQuery.isLoading || scoresQuery.isLoading}
        isError={citiesQuery.isError || scoresQuery.isError}
        isEmpty={cities.length === 0}
        error={citiesQuery.error ?? scoresQuery.error}
        onRetry={() => {
          void citiesQuery.refetch();
          void scoresQuery.refetch();
        }}
        emptyMessage="Nenhuma cidade cadastrada"
      >
        <div className="h-[28rem] overflow-hidden rounded-xl border border-gray-200 shadow-sm dark:border-gray-800 lg:h-[32rem]">
          <MapView cities={cities} selectedCity={null} onCitySelect={() => undefined} />
        </div>
      </AsyncState>
    </div>
  );
}
