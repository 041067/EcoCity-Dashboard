import { useMemo } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { AppIcon } from '../../components/icons/AppIcon';
import { AsyncState } from '../../components/AsyncState';
import {
  useOrganizationSites,
  useOrganizations,
  useProviderStatuses,
  useSiteAirQuality,
  useSiteClimateRisk,
  useSiteEnergy,
  useSiteIndicators,
} from '../../hooks/useApiQueries';
import { syncSiteIntelligence } from '../../services/api';
import type { FreshnessStatus, IndicatorValue, ProviderStatus } from '../../types';

const PROVIDER_NAMES: Record<string, string> = {
  open_meteo: 'Open-Meteo',
  openaq: 'OpenAQ',
  nasa_power: 'NASA POWER',
  inpe: 'INPE',
  aneel: 'ANEEL',
  climate_risk_engine: 'Motor de risco climático',
};

function latestByCode(values: IndicatorValue[]) {
  const latest = new Map<string, IndicatorValue>();
  values.forEach((value) => {
    if (!latest.has(value.indicator.code)) latest.set(value.indicator.code, value);
  });
  return latest;
}

function riskLabel(value?: IndicatorValue) {
  const metadata = value?.source_metadata;
  const level = typeof metadata?.risk_level === 'string' ? metadata.risk_level : undefined;
  return level ? level[0].toUpperCase() + level.slice(1) : 'Sem dados';
}

function airLabel(value?: IndicatorValue) {
  if (!value) return 'Sem dados';
  if (value.value <= 12) return 'Boa';
  if (value.value <= 35) return 'Moderada';
  return 'Atenção';
}

function StatusDot({ status }: { status: ProviderStatus['status'] }) {
  const colors = { online: 'bg-emerald-500', degraded: 'bg-amber-500', offline: 'bg-red-500', unknown: 'bg-gray-400' };
  return <span className={`h-2.5 w-2.5 rounded-full ${colors[status]}`} aria-label={status} />;
}

function Freshness({ status }: { status: FreshnessStatus }) {
  const labels = { fresh: 'Atualizado', aging: 'Em envelhecimento', stale: 'Desatualizado' };
  const styles = { fresh: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300', aging: 'bg-amber-50 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300', stale: 'bg-red-50 text-red-700 dark:bg-red-950/50 dark:text-red-300' };
  return <span className={`rounded-full px-2 py-1 text-xs font-semibold ${styles[status]}`}>{labels[status]}</span>;
}

function IntelligenceCard({
  icon,
  title,
  value,
  detail,
  indicator,
}: {
  icon: Parameters<typeof AppIcon>[0]['name'];
  title: string;
  value: string;
  detail: string;
  indicator?: IndicatorValue;
}) {
  return (
    <article className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
      <div className="flex items-start justify-between gap-3">
        <div className="rounded-xl bg-emerald-50 p-2.5 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300"><AppIcon name={icon} /></div>
        {indicator && <Freshness status={indicator.freshness_status} />}
      </div>
      <p className="mt-5 text-sm font-medium text-gray-500 dark:text-gray-400">{title}</p>
      <p className="mt-1 text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{detail}</p>
    </article>
  );
}

export function IntelligencePage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const organizationsQuery = useOrganizations();
  const requestedOrganization = Number(params.get('organization'));
  const organizationId = Number.isInteger(requestedOrganization) && requestedOrganization > 0
    ? requestedOrganization
    : organizationsQuery.data?.[0]?.id;
  const sitesQuery = useOrganizationSites(organizationId);
  const requestedSite = Number(params.get('site'));
  const siteId = Number.isInteger(requestedSite) && requestedSite > 0 ? requestedSite : sitesQuery.data?.[0]?.id;
  const risksQuery = useSiteClimateRisk(siteId);
  const airQuery = useSiteAirQuality(siteId);
  const energyQuery = useSiteEnergy(siteId);
  const territoryQuery = useSiteIndicators(siteId, 'territory');
  const providersQuery = useProviderStatuses();
  const syncMutation = useMutation({
    mutationFn: () => syncSiteIntelligence(siteId!),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['esg', 'site-'] });
      await queryClient.invalidateQueries({ queryKey: ['esg', 'providers'] });
    },
  });

  const latestRisks = useMemo(() => latestByCode(risksQuery.data ?? []), [risksQuery.data]);
  const latestAir = useMemo(() => latestByCode(airQuery.data ?? []), [airQuery.data]);
  const latestEnergy = useMemo(() => latestByCode(energyQuery.data ?? []), [energyQuery.data]);
  const latestTerritory = useMemo(() => latestByCode(territoryQuery.data ?? []), [territoryQuery.data]);
  const selectedSite = sitesQuery.data?.find((site) => site.id === siteId);
  const heatRisk = latestRisks.get('CLIMATE_HEAT_RISK');
  const waterRisk = latestRisks.get('WATER_STRESS_SIGNAL') ?? latestRisks.get('WATER_DROUGHT_RISK');
  const pm25 = latestAir.get('AIR_PM25');
  const solar = latestEnergy.get('ENERGY_SOLAR_POTENTIAL') ?? latestEnergy.get('ENERGY_SOLAR_RADIATION');
  const alerts = [...latestTerritory.values()].reduce((sum, value) => sum + value.value, 0);
  const isLoading = organizationsQuery.isLoading || (Boolean(organizationId) && sitesQuery.isLoading);
  const queryError = organizationsQuery.error ?? sitesQuery.error ?? risksQuery.error ?? airQuery.error ?? energyQuery.error;
  const noOrganizations = !organizationsQuery.isLoading && !organizationsQuery.data?.length;
  const noSites = !sitesQuery.isLoading && organizationId && !sitesQuery.data?.length;

  function updateSelection(nextOrganization?: number, nextSite?: number) {
    const organization = nextOrganization ?? organizationId;
    const site = nextSite ?? siteId;
    const query = new URLSearchParams();
    if (organization) query.set('organization', String(organization));
    if (site) query.set('site', String(site));
    navigate(`/esg/intelligence?${query.toString()}`);
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm font-bold uppercase tracking-widest text-emerald-600">EcoCity ESG · Sprint 8</p>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Inteligência Externa</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Indicadores rastreáveis, fontes públicas e riscos determinísticos por unidade.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {(organizationsQuery.data?.length ?? 0) > 1 && <select value={organizationId ?? ''} onChange={(event) => updateSelection(Number(event.target.value), undefined)} aria-label="Selecionar organização" className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-700 dark:bg-gray-900 dark:text-white">{organizationsQuery.data?.map((organization) => <option key={organization.id} value={organization.id}>{organization.name}</option>)}</select>}
          <Link to={organizationId ? `/esg?organization=${organizationId}` : '/esg'} className="rounded-lg border border-emerald-600 px-3 py-2 text-sm font-semibold text-emerald-700 hover:bg-emerald-50 dark:text-emerald-300">Visão ESG</Link>
        </div>
      </header>

      <AsyncState isLoading={isLoading} isError={Boolean(queryError)} isEmpty={Boolean(noOrganizations || noSites)} error={queryError} onRetry={() => sitesQuery.refetch()} emptyMessage={noSites ? 'Cadastre uma unidade com latitude e longitude para ativar a inteligência externa.' : 'Configure uma organização ESG antes de acessar os indicadores.'}>
        {selectedSite && <>
          <section className="flex flex-col justify-between gap-4 rounded-2xl border border-gray-200 bg-gradient-to-r from-emerald-50 to-cyan-50 p-6 dark:border-gray-800 dark:from-emerald-950/40 dark:to-gray-900 sm:flex-row sm:items-center">
            <div><p className="text-sm font-semibold text-emerald-700 dark:text-emerald-300">UNIDADE MONITORADA</p><h2 className="mt-1 text-xl font-bold text-gray-900 dark:text-white">{selectedSite.name}</h2><p className="mt-1 text-sm text-gray-600 dark:text-gray-300">{selectedSite.latitude != null && selectedSite.longitude != null ? `${selectedSite.latitude.toFixed(4)}, ${selectedSite.longitude.toFixed(4)}` : 'Localização pendente'}</p></div>
            <div className="flex gap-2"><select value={siteId ?? ''} onChange={(event) => updateSelection(undefined, Number(event.target.value))} aria-label="Selecionar unidade" className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-700 dark:bg-gray-900 dark:text-white">{sitesQuery.data?.map((site) => <option key={site.id} value={site.id}>{site.name}</option>)}</select><button type="button" onClick={() => syncMutation.mutate()} disabled={syncMutation.isPending || selectedSite.latitude == null || selectedSite.longitude == null} className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-3 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"><AppIcon name="sensor" className="h-4 w-4" />{syncMutation.isPending ? 'Sincronizando' : 'Sincronizar'}</button></div>
          </section>
          {syncMutation.isError && <p role="alert" className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">Não foi possível iniciar a sincronização. Os últimos dados válidos foram preservados.</p>}
          {syncMutation.data && <p className="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-200">Sincronização concluída: {syncMutation.data.results.filter((result) => result.status === 'success').length} fonte(s) atualizada(s); fontes indisponíveis permanecem isoladas.</p>}
          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            <IntelligenceCard icon="sun" title="Risco climático" value={riskLabel(heatRisk)} detail="Exposição ao calor por regra determinística" indicator={heatRisk} />
            <IntelligenceCard icon="air" title="Qualidade do ar" value={airLabel(pm25)} detail={pm25 ? `PM2.5: ${pm25.value.toFixed(1)} ${pm25.unit}` : 'Aguardando observação'} indicator={pm25} />
            <IntelligenceCard icon="water" title="Risco hídrico" value={riskLabel(waterRisk)} detail="Precipitação e evapotranspiração" indicator={waterRisk} />
            <IntelligenceCard icon="energy" title="Potencial solar" value={solar ? `${solar.value.toFixed(1)} ${solar.unit}` : 'Sem dados'} detail="Contexto energético e climatológico" indicator={solar} />
            <IntelligenceCard icon="alert" title="Alertas ambientais" value={String(alerts)} detail="Queimadas e desmatamento no raio configurado" indicator={[...latestTerritory.values()][0]} />
          </section>

          <section className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
            <article className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900"><div className="flex items-center gap-2"><AppIcon name="document" className="text-emerald-600" /><div><h2 className="font-bold text-gray-900 dark:text-white">Indicadores com proveniência</h2><p className="text-sm text-gray-500 dark:text-gray-400">Cada observação preserva fonte, unidade, localização e horário.</p></div></div><div className="mt-4 divide-y divide-gray-100 dark:divide-gray-800">{[...latestAir.values(), ...latestEnergy.values(), ...latestRisks.values()].slice(0, 8).map((value) => <div key={value.id} className="flex flex-col gap-2 py-3 sm:flex-row sm:items-center sm:justify-between"><div><p className="font-medium text-gray-900 dark:text-white">{value.indicator.name}</p><p className="text-xs text-gray-500">{PROVIDER_NAMES[value.source] ?? value.source} · observado {value.observed_at ? new Date(value.observed_at).toLocaleString('pt-BR') : 'não informado'}</p></div><div className="flex items-center gap-3"><Freshness status={value.freshness_status} /><span className="text-sm font-bold text-gray-900 dark:text-white">{value.value.toFixed(1)} {value.unit}</span></div></div>)}{!latestAir.size && !latestEnergy.size && !latestRisks.size && <p className="py-8 text-center text-sm text-gray-500">Ainda não há dados sincronizados para esta unidade.</p>}</div></article>
            <aside className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900"><div className="flex items-center gap-2"><AppIcon name="sensor" className="text-emerald-600" /><h2 className="font-bold text-gray-900 dark:text-white">Fontes de dados</h2></div><ul className="mt-4 space-y-3">{(providersQuery.data ?? []).map((provider) => <li key={provider.name} className="flex items-center justify-between gap-3"><div className="flex items-center gap-2"><StatusDot status={provider.status} /><span className="text-sm font-medium text-gray-700 dark:text-gray-200">{provider.display_name}</span></div><span className="text-xs text-gray-500">{provider.last_sync ? new Date(provider.last_sync).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : 'Aguardando sync'}</span></li>)}</ul><p className="mt-5 border-t border-gray-100 pt-4 text-xs text-gray-500 dark:border-gray-800">Uma indisponibilidade externa não interrompe o EcoCity: o último valor válido permanece disponível com seu status de atualização.</p></aside>
          </section>
        </>}
      </AsyncState>
    </div>
  );
}
