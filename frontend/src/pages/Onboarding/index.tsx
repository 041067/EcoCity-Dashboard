import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCities, useESGTopics } from '../../hooks/useApiQueries';
import {
  createOrganization,
  createSite,
  createStakeholder,
  saveOrganizationTopic,
  updateESGProfile,
} from '../../services/api';
import type { ESGPillar, ESGTopic, OrganizationType, SiteType, StakeholderType } from '../../types';

type DraftSite = { name: string; site_type: SiteType; city_id: string };

const ORGANIZATION_TYPES: { value: OrganizationType; label: string }[] = [
  { value: 'company', label: 'Empresa' },
  { value: 'municipality', label: 'Município' },
  { value: 'public_agency', label: 'Órgão público' },
  { value: 'university', label: 'Universidade' },
  { value: 'other', label: 'Outro' },
];
const SITE_TYPES: { value: SiteType; label: string }[] = [
  { value: 'headquarters', label: 'Matriz' }, { value: 'factory', label: 'Fábrica' },
  { value: 'warehouse', label: 'Centro de distribuição' }, { value: 'office', label: 'Escritório' },
  { value: 'municipal_region', label: 'Região municipal' }, { value: 'other', label: 'Outra' },
];
const STAKEHOLDERS: { type: StakeholderType; name: string }[] = [
  { type: 'employees', name: 'Funcionários' }, { type: 'customers', name: 'Clientes' },
  { type: 'suppliers', name: 'Fornecedores' }, { type: 'government', name: 'Governo' },
  { type: 'community', name: 'Comunidade' }, { type: 'investors', name: 'Investidores' },
];
const PILLAR_NAMES: Record<ESGPillar, string> = { E: 'Environmental', S: 'Social', G: 'Governance' };

function Checkbox({ checked, label, onChange }: { checked: boolean; label: string; onChange: () => void }) {
  return <label className="flex cursor-pointer items-center gap-3 rounded-xl border border-gray-200 bg-white p-3 text-sm font-medium text-gray-700 hover:border-emerald-400 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200"><input type="checkbox" checked={checked} onChange={onChange} className="h-4 w-4 accent-emerald-600" />{label}</label>;
}

function FormInput({ label, ...props }: React.InputHTMLAttributes<HTMLInputElement> & { label: string }) {
  return <label><span className="text-sm font-medium text-gray-700 dark:text-gray-200">{label}</span><input {...props} className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:border-emerald-500 focus:outline-none dark:border-gray-700 dark:bg-gray-950 dark:text-white" /></label>;
}

export function OnboardingPage() {
  const navigate = useNavigate();
  const citiesQuery = useCities();
  const topicsQuery = useESGTopics();
  const [name, setName] = useState('');
  const [organizationType, setOrganizationType] = useState<OrganizationType>('company');
  const [industrySector, setIndustrySector] = useState('');
  const [state, setState] = useState('');
  const [city, setCity] = useState('');
  const [sites, setSites] = useState<DraftSite[]>([]);
  const [topicIds, setTopicIds] = useState<number[]>([]);
  const [stakeholderTypes, setStakeholderTypes] = useState<StakeholderType[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const topicsByPillar = useMemo(() => {
    const groups: Record<ESGPillar, ESGTopic[]> = { E: [], S: [], G: [] };
    for (const topic of topicsQuery.data ?? []) groups[topic.pillar].push(topic);
    return groups;
  }, [topicsQuery.data]);

  function toggle<T>(value: T, values: T[], setValues: React.Dispatch<React.SetStateAction<T[]>>) {
    setValues(values.includes(value) ? values.filter((item) => item !== value) : [...values, value]);
  }
  function updateSite(index: number, field: keyof DraftSite, value: string) {
    setSites((items) => items.map((site, itemIndex) => itemIndex === index ? { ...site, [field]: value } : site));
  }
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    if (!name.trim()) return setError('Informe o nome da organização para continuar.');
    setIsSubmitting(true);
    try {
      const organization = await createOrganization({ name: name.trim(), organization_type: organizationType, industry_sector: industrySector.trim() || null, country: 'Brasil', state: state.trim() || null, city: city.trim() || null });
      const selectedPillars = new Set((topicsQuery.data ?? []).filter((topic) => topicIds.includes(topic.id)).map((topic) => topic.pillar));
      await updateESGProfile(organization.id, { reporting_year: new Date().getFullYear(), environmental_enabled: selectedPillars.has('E'), social_enabled: selectedPillars.has('S'), governance_enabled: selectedPillars.has('G'), esg_maturity_level: 'initial', sustainability_strategy: null });
      await Promise.all(sites.filter((site) => site.name.trim()).map((site) => createSite(organization.id, { name: site.name.trim(), site_type: site.site_type, city_id: site.city_id ? Number(site.city_id) : null, latitude: null, longitude: null, employee_count: null, area_m2: null })));
      await Promise.all(topicIds.map((topic_id) => saveOrganizationTopic(organization.id, { topic_id, enabled: true, priority: 3, notes: null })));
      await Promise.all(stakeholderTypes.map((stakeholder_type) => {
        const stakeholder = STAKEHOLDERS.find((item) => item.type === stakeholder_type)!;
        return createStakeholder(organization.id, { name: stakeholder.name, stakeholder_type, influence_level: 3, impact_level: 3, description: null });
      }));
      navigate(`/esg?organization=${organization.id}`);
    } catch {
      setError('Não foi possível concluir o onboarding. Revise os dados e tente novamente.');
    } finally { setIsSubmitting(false); }
  }

  return <main className="min-h-screen bg-slate-50 px-4 py-10 dark:bg-gray-950"><form onSubmit={submit} className="mx-auto max-w-4xl space-y-8"><header className="text-center"><p className="text-sm font-bold uppercase tracking-widest text-emerald-600">EcoCity ESG</p><h1 className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">Vamos configurar sua base ESG</h1><p className="mt-2 text-gray-600 dark:text-gray-400">Comece com a estrutura que dará contexto aos seus dados ambientais.</p></header>
    <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900"><h2 className="text-lg font-bold text-gray-900 dark:text-white">1. Organização</h2><div className="mt-4 grid gap-4 sm:grid-cols-2"><div className="sm:col-span-2"><FormInput label="Nome da organização *" value={name} onChange={(event) => setName(event.target.value)} required maxLength={200} placeholder="Ex.: Eco Industries S.A." /></div><label><span className="text-sm font-medium text-gray-700 dark:text-gray-200">Tipo</span><select value={organizationType} onChange={(event) => setOrganizationType(event.target.value as OrganizationType)} className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 dark:border-gray-700 dark:bg-gray-950 dark:text-white">{ORGANIZATION_TYPES.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}</select></label><FormInput label="Setor" value={industrySector} onChange={(event) => setIndustrySector(event.target.value)} maxLength={120} placeholder="Ex.: Indústria" /><FormInput label="Estado" value={state} onChange={(event) => setState(event.target.value)} maxLength={100} placeholder="SP" /><FormInput label="Cidade" value={city} onChange={(event) => setCity(event.target.value)} maxLength={100} placeholder="São Paulo" /></div></section>
    <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900"><div className="flex items-center justify-between gap-4"><div><h2 className="text-lg font-bold text-gray-900 dark:text-white">2. Unidades</h2><p className="text-sm text-gray-500 dark:text-gray-400">Vincule unidades às cidades já monitoradas, quando houver correspondência.</p></div><button type="button" onClick={() => setSites((items) => [...items, { name: '', site_type: 'office', city_id: '' }])} className="rounded-lg border border-emerald-600 px-3 py-2 text-sm font-semibold text-emerald-700 hover:bg-emerald-50 dark:text-emerald-400">Adicionar unidade</button></div>{sites.length === 0 ? <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">Você pode adicionar unidades agora ou depois.</p> : <div className="mt-4 space-y-3">{sites.map((site, index) => <div key={index} className="grid gap-3 rounded-xl border border-gray-200 p-3 sm:grid-cols-4 dark:border-gray-700"><input value={site.name} onChange={(event) => updateSite(index, 'name', event.target.value)} maxLength={200} placeholder="Nome da unidade" className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-gray-700 dark:bg-gray-950 dark:text-white" /><select value={site.site_type} onChange={(event) => updateSite(index, 'site_type', event.target.value)} className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-gray-700 dark:bg-gray-950 dark:text-white">{SITE_TYPES.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}</select><select value={site.city_id} onChange={(event) => updateSite(index, 'city_id', event.target.value)} className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-gray-700 dark:bg-gray-950 dark:text-white"><option value="">Sem vínculo de cidade</option>{(citiesQuery.data ?? []).map((item) => <option key={item.id} value={item.id}>{item.name}/{item.state}</option>)}</select><button type="button" onClick={() => setSites((items) => items.filter((_, itemIndex) => itemIndex !== index))} className="rounded-lg px-3 py-2 text-sm font-semibold text-red-600 hover:bg-red-50">Remover</button></div>)}</div>}</section>
    <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900"><h2 className="text-lg font-bold text-gray-900 dark:text-white">3. Temas ESG acompanhados</h2><p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Selecione os temas relevantes. Ainda não há nota ou cálculo de materialidade.</p>{topicsQuery.isLoading ? <p className="mt-4 text-sm text-gray-500">Carregando catálogo ESG…</p> : <div className="mt-4 grid gap-5 md:grid-cols-3">{(['E', 'S', 'G'] as ESGPillar[]).map((pillar) => <div key={pillar}><h3 className="mb-2 font-bold text-gray-800 dark:text-white">{PILLAR_NAMES[pillar]}</h3><div className="space-y-2">{topicsByPillar[pillar].map((topic) => <Checkbox key={topic.id} label={topic.name} checked={topicIds.includes(topic.id)} onChange={() => toggle(topic.id, topicIds, setTopicIds)} />)}</div></div>)}</div>}</section>
    <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900"><h2 className="text-lg font-bold text-gray-900 dark:text-white">4. Stakeholders</h2><p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Você poderá aprofundar influência e impacto na Sprint 7.</p><div className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">{STAKEHOLDERS.map((stakeholder) => <Checkbox key={stakeholder.type} label={stakeholder.name} checked={stakeholderTypes.includes(stakeholder.type)} onChange={() => toggle(stakeholder.type, stakeholderTypes, setStakeholderTypes)} />)}</div></section>
    {error && <p role="alert" className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}<div className="flex justify-end"><button type="submit" disabled={isSubmitting || topicsQuery.isLoading} className="rounded-lg bg-emerald-600 px-6 py-3 font-semibold text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60">{isSubmitting ? 'Configurando…' : 'Concluir e ver ESG Overview'}</button></div>
  </form></main>;
}
