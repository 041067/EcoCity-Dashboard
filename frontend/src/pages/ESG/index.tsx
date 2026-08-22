import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { AsyncState } from '../../components/AsyncState';
import { useOrganization, useOrganizationOverview, useOrganizations, useOrganizationSites, useOrganizationStakeholders, useOrganizationTopics } from '../../hooks/useApiQueries';
import type { ESGPillar } from '../../types';

const PILLARS: { key: ESGPillar; title: string; count: 'environmental_topics' | 'social_topics' | 'governance_topics'; color: string }[] = [
  { key: 'E', title: 'Environmental', count: 'environmental_topics', color: 'border-emerald-500 text-emerald-700 dark:text-emerald-300' },
  { key: 'S', title: 'Social', count: 'social_topics', color: 'border-sky-500 text-sky-700 dark:text-sky-300' },
  { key: 'G', title: 'Governance', count: 'governance_topics', color: 'border-violet-500 text-violet-700 dark:text-violet-300' },
];

function Metric({ label, value }: { label: string; value: string | number }) {
  return <article className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-800 dark:bg-gray-900"><p className="text-sm text-gray-500 dark:text-gray-400">{label}</p><p className="mt-1 text-2xl font-bold text-gray-900 dark:text-white">{value}</p></article>;
}

export function ESGPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const organizationsQuery = useOrganizations();
  const requestedId = Number(params.get('organization'));
  const organizationId = Number.isInteger(requestedId) && requestedId > 0 ? requestedId : organizationsQuery.data?.[0]?.id;
  const organizationQuery = useOrganization(organizationId);
  const overviewQuery = useOrganizationOverview(organizationId);
  const topicsQuery = useOrganizationTopics(organizationId);
  const sitesQuery = useOrganizationSites(organizationId);
  const stakeholdersQuery = useOrganizationStakeholders(organizationId);
  const topicsByPillar: Record<ESGPillar, string[]> = { E: [], S: [], G: [] };
  for (const link of topicsQuery.data ?? []) if (link.enabled) topicsByPillar[link.topic.pillar].push(link.topic.name);
  const noOrganizations = !organizationsQuery.isLoading && (organizationsQuery.data?.length ?? 0) === 0;
  const isLoading = organizationsQuery.isLoading || (Boolean(organizationId) && overviewQuery.isLoading);
  const queryError = organizationsQuery.error ?? overviewQuery.error;

  return <div className="space-y-6"><div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><p className="text-sm font-bold uppercase tracking-widest text-emerald-600">EcoCity ESG</p><h1 className="text-2xl font-bold text-gray-900 dark:text-white">ESG Overview</h1><p className="text-sm text-gray-500 dark:text-gray-400">Estrutura ESG da organização, sem score ou materialidade nesta fase.</p></div><div className="flex gap-2">{(organizationsQuery.data?.length ?? 0) > 1 && <select value={organizationId ?? ''} onChange={(event) => navigate(`/esg?organization=${event.target.value}`)} aria-label="Selecionar organização" className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-gray-700 dark:bg-gray-900 dark:text-white">{organizationsQuery.data?.map((organization) => <option key={organization.id} value={organization.id}>{organization.name}</option>)}</select>}<Link to="/onboarding" className="rounded-lg bg-emerald-600 px-3 py-2 text-sm font-semibold text-white hover:bg-emerald-700">Nova organização</Link></div></div>
    <AsyncState isLoading={isLoading} isError={Boolean(queryError)} isEmpty={noOrganizations} error={queryError} onRetry={() => organizationsQuery.refetch()} emptyMessage="Nenhuma organização configurada. Inicie o onboarding ESG.">{organizationQuery.data && overviewQuery.data && <><section className="rounded-2xl border border-gray-200 bg-gradient-to-r from-emerald-50 to-cyan-50 p-6 dark:border-gray-800 dark:from-emerald-950/40 dark:to-gray-900"><p className="text-2xl font-bold text-gray-900 dark:text-white">{organizationQuery.data.name}</p><p className="mt-1 text-sm text-gray-600 dark:text-gray-300">{organizationQuery.data.industry_sector ?? 'Setor não informado'} · {organizationQuery.data.country}{organizationQuery.data.city ? ` · ${organizationQuery.data.city}` : ''}</p></section>
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"><Metric label="Sites" value={overviewQuery.data.sites} /><Metric label="Stakeholders" value={overviewQuery.data.stakeholders} /><Metric label="Temas monitorados" value={overviewQuery.data.esg_topics} /><Metric label="Maturidade" value="Em estruturação" /></section>
      <section className="grid gap-4 lg:grid-cols-3">{PILLARS.map((pillar) => <article key={pillar.key} className={`rounded-2xl border border-gray-200 border-t-4 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900 ${pillar.color}`}><div className="flex items-baseline justify-between"><h2 className="font-bold">{pillar.title}</h2><span className="text-2xl font-bold">{overviewQuery.data[pillar.count]}</span></div><ul className="mt-4 space-y-2 text-sm text-gray-600 dark:text-gray-300">{topicsByPillar[pillar.key].length ? topicsByPillar[pillar.key].map((topic) => <li key={topic}>• {topic}</li>) : <li className="text-gray-400">Nenhum tema selecionado</li>}</ul></article>)}</section>
      <section className="grid gap-4 lg:grid-cols-2"><article className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900"><h2 className="font-bold text-gray-900 dark:text-white">Unidades e contexto ambiental</h2><ul className="mt-3 space-y-2 text-sm text-gray-600 dark:text-gray-300">{(sitesQuery.data ?? []).length ? sitesQuery.data?.map((site) => <li key={site.id} className="rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-800"><span className="font-medium">{site.name}</span>{site.city ? ` · ${site.city.name}/${site.city.state}` : ' · sem cidade vinculada'}</li>) : <li className="text-gray-400">Nenhuma unidade cadastrada</li>}</ul></article><article className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900"><h2 className="font-bold text-gray-900 dark:text-white">Stakeholders</h2><ul className="mt-3 flex flex-wrap gap-2">{(stakeholdersQuery.data ?? []).length ? stakeholdersQuery.data?.map((stakeholder) => <li key={stakeholder.id} className="rounded-full bg-sky-50 px-3 py-1 text-sm text-sky-800 dark:bg-sky-950 dark:text-sky-200">{stakeholder.name}</li>) : <li className="text-sm text-gray-400">Nenhum stakeholder cadastrado</li>}</ul></article></section>
      <p className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-200">A Sprint 6 organiza dados e temas ESG. A matriz de materialidade e qualquer ESG Score serão introduzidos somente na Sprint 7.</p>
    </>}</AsyncState>
  </div>;
}
