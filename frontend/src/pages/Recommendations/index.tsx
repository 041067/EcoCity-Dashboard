import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import { AppIcon } from '../../components/icons/AppIcon';
import { AsyncState } from '../../components/AsyncState';
import { useAIRecommendations, useOrganizations } from '../../hooks/useApiQueries';
import {
  createActionFromAIRecommendation,
  dismissAIRecommendation,
  generateAIRecommendations,
} from '../../services/api';
import type { AIRecommendation } from '../../types';

const PRIORITY_STYLE = {
  low: 'bg-sky-100 text-sky-800 dark:bg-sky-950 dark:text-sky-200',
  medium: 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-200',
  high: 'bg-orange-100 text-orange-800 dark:bg-orange-950 dark:text-orange-200',
  critical: 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-200',
};

const HORIZON_LABEL = { immediate: 'Imediato', short_term: 'Curto prazo', medium_term: 'Médio prazo', long_term: 'Longo prazo' };

function Evidence({ ids }: { ids: string[] }) {
  return ids.length ? <div className="mt-3 flex flex-wrap gap-1">{ids.map((id) => <span key={id} className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs text-gray-600 dark:bg-gray-800 dark:text-gray-300">{id}</span>)}</div> : null;
}

function RecommendationCard({
  item,
  onDismiss,
  onCreateAction,
  pending,
}: {
  item: AIRecommendation;
  onDismiss: (id: number) => void;
  onCreateAction: (id: number, responsible: string, dueDate: string) => void;
  pending: boolean;
}) {
  const [responsible, setResponsible] = useState('');
  const [dueDate, setDueDate] = useState('');
  const canApprove = item.status === 'pending';
  return <article className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900"><div className="flex flex-col justify-between gap-3 sm:flex-row"><div><div className="flex flex-wrap items-center gap-2"><span className={`rounded-full px-2.5 py-1 text-xs font-bold uppercase ${PRIORITY_STYLE[item.priority]}`}>{item.priority}</span><span className="text-xs font-semibold uppercase tracking-wide text-gray-500">{item.topic.name} · {HORIZON_LABEL[item.time_horizon]}</span></div><h2 className="mt-3 text-lg font-bold text-gray-900 dark:text-white">{item.title}</h2></div><span className="text-xs font-medium text-gray-500">{item.status === 'converted' ? 'Ação criada' : item.status === 'dismissed' ? 'Descartada' : 'Aguardando aprovação'}</span></div><div className="mt-4 grid gap-3 sm:grid-cols-2"><div><p className="text-xs font-bold uppercase tracking-wide text-gray-500">Justificativa</p><p className="mt-1 text-sm leading-6 text-gray-700 dark:text-gray-300">{item.rationale}</p></div><div><p className="text-xs font-bold uppercase tracking-wide text-gray-500">Impacto esperado</p><p className="mt-1 text-sm leading-6 text-gray-700 dark:text-gray-300">{item.expected_impact}</p></div></div><Evidence ids={item.evidence_ids} />{canApprove && <div className="mt-4 grid gap-2 border-t border-gray-100 pt-4 sm:grid-cols-[1fr_11rem_auto_auto] dark:border-gray-800"><input value={responsible} onChange={(event) => setResponsible(event.target.value)} maxLength={160} placeholder="Responsável (opcional)" aria-label={`Responsável para ${item.title}`} className="min-h-10 rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-900 dark:border-gray-700 dark:bg-gray-950 dark:text-white" /><input value={dueDate} onChange={(event) => setDueDate(event.target.value)} type="date" aria-label={`Prazo para ${item.title}`} className="min-h-10 rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-900 dark:border-gray-700 dark:bg-gray-950 dark:text-white" /><button type="button" onClick={() => onDismiss(item.id)} disabled={pending} className="min-h-10 rounded-lg border border-gray-300 px-3 text-sm font-semibold text-gray-700 hover:bg-gray-50 disabled:opacity-50 dark:border-gray-700 dark:text-gray-200 dark:hover:bg-gray-800">Descartar</button><button type="button" onClick={() => onCreateAction(item.id, responsible, dueDate)} disabled={pending} className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg bg-emerald-600 px-3 text-sm font-bold text-white hover:bg-emerald-700 disabled:opacity-50"><AppIcon name="check" className="h-4 w-4" />Criar ação</button></div>}</article>;
}

export function RecommendationsPage() {
  const [params] = useSearchParams();
  const client = useQueryClient();
  const organizations = useOrganizations();
  const requestedId = Number(params.get('organization'));
  const organizationId = Number.isInteger(requestedId) && requestedId > 0 ? requestedId : organizations.data?.[0]?.id;
  const recommendations = useAIRecommendations(organizationId);
  const [notice, setNotice] = useState<string | null>(null);
  const refresh = async () => { await client.invalidateQueries({ queryKey: ['esg', 'ai-recommendations', organizationId] }); await client.invalidateQueries({ queryKey: ['esg', 'actions', organizationId] }); };
  const generate = useMutation({ mutationFn: () => generateAIRecommendations(organizationId!), onSuccess: async (result) => { setNotice(result.cached ? 'As recomendações existentes continuam válidas para o contexto atual.' : 'Novas recomendações foram geradas. Revise-as antes de criar uma ação.'); await refresh(); } });
  const dismiss = useMutation({ mutationFn: (id: number) => dismissAIRecommendation(organizationId!, id), onSuccess: refresh });
  const createAction = useMutation({ mutationFn: ({ id, responsible, dueDate }: { id: number; responsible: string; dueDate: string }) => createActionFromAIRecommendation(organizationId!, id, { responsible_area: responsible || undefined, due_date: dueDate || undefined }), onSuccess: async () => { setNotice('Plano de ação criado após aprovação humana.'); await refresh(); } });
  const noOrganizations = !organizations.isLoading && !organizations.data?.length;

  return <div className="space-y-6"><header className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><p className="text-sm font-bold uppercase tracking-widest text-emerald-600">EcoCity AI · Sprint 10</p><h1 className="text-2xl font-bold text-gray-900 dark:text-white">Central de recomendações</h1><p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Cada proposta precisa de aprovação explícita antes de se tornar um plano de ação.</p></div><button type="button" onClick={() => generate.mutate()} disabled={!organizationId || generate.isPending} className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-bold text-white hover:bg-emerald-700 disabled:opacity-60"><AppIcon name="brain" className="h-4 w-4" />{generate.isPending ? 'Analisando…' : 'Gerar recomendações'}</button></header>{notice && <p className="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-200">{notice}</p>}{generate.isError && <p role="alert" className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-200">O serviço de IA está indisponível. Nenhum plano de ação foi criado ou alterado.</p>}<AsyncState isLoading={organizations.isLoading || recommendations.isLoading} isError={organizations.isError || recommendations.isError} isEmpty={noOrganizations || (!recommendations.data?.length && !generate.isPending)} error={organizations.error ?? recommendations.error} onRetry={() => recommendations.refetch()} emptyMessage={noOrganizations ? 'Crie uma organização ESG para usar recomendações.' : 'Ainda não há recomendações. Gere uma análise baseada no contexto ESG.'}><div className="space-y-4">{(recommendations.data ?? []).map((item) => <RecommendationCard key={item.id} item={item} onDismiss={(id) => dismiss.mutate(id)} onCreateAction={(id, responsible, dueDate) => createAction.mutate({ id, responsible, dueDate })} pending={dismiss.isPending || createAction.isPending} />)}</div></AsyncState></div>;
}
