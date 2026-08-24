import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import { AsyncState } from '../../components/AsyncState';
import { AppIcon } from '../../components/icons/AppIcon';
import {
  useActionPlans,
  useESGPriorities,
  useGaps,
  useOpportunities,
  useOrganizations,
  useRisks,
  useTargets,
} from '../../hooks/useApiQueries';
import { runESGAnalysis } from '../../services/api';

const COLORS = {
  low: 'bg-sky-100 text-sky-700 dark:bg-sky-950 dark:text-sky-300',
  medium: 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300',
  high: 'bg-orange-100 text-orange-700 dark:bg-orange-950 dark:text-orange-300',
  critical: 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300',
};

function Badge({ value }: { value: keyof typeof COLORS }) {
  return <span className={`rounded-full px-2 py-1 text-xs font-bold ${COLORS[value]}`}>{value.replace('_', ' ')}</span>;
}

export function ActionsPage() {
  const [params] = useSearchParams();
  const queryClient = useQueryClient();
  const organizations = useOrganizations();
  const requestedId = Number(params.get('organization'));
  const organizationId = Number.isInteger(requestedId) && requestedId > 0 ? requestedId : organizations.data?.[0]?.id;
  const targets = useTargets(organizationId);
  const gaps = useGaps(organizationId);
  const risks = useRisks(organizationId);
  const opportunities = useOpportunities(organizationId);
  const actions = useActionPlans(organizationId);
  const priorities = useESGPriorities(organizationId);
  const analysis = useMutation({
    mutationFn: () => runESGAnalysis(organizationId!),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['esg'] });
    },
  });
  const loading = organizations.isLoading || targets.isLoading || gaps.isLoading || risks.isLoading;
  const error = organizations.error ?? targets.error ?? gaps.error ?? risks.error;
  const openGaps = (gaps.data ?? []).filter((gap) => gap.status === 'open');
  const openRisks = (risks.data ?? []).filter((risk) => risk.status !== 'resolved');

  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm font-bold uppercase tracking-widest text-emerald-600">EcoCity ESG · Sprint 9</p>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Gap &amp; Action Engine</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Prioridades explicáveis, metas monitoradas e execução auditável.</p>
        </div>
        <button type="button" onClick={() => analysis.mutate()} disabled={!organizationId || analysis.isPending} className="inline-flex items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-bold text-white hover:bg-emerald-700 disabled:opacity-60">
          <AppIcon name="brain" className="h-4 w-4" />{analysis.isPending ? 'Analisando…' : 'Executar análise'}
        </button>
      </header>

      {analysis.data && <p className="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-200">Análise concluída: {analysis.data.gaps_open} gap(s), {analysis.data.risks_open} risco(s) e {analysis.data.opportunities_open} oportunidade(s) ativos.</p>}
      {analysis.isError && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">A análise não foi concluída. Os dados persistidos permanecem inalterados.</p>}

      <AsyncState isLoading={loading} isError={Boolean(error)} isEmpty={!organizations.isLoading && !organizationId} error={error} onRetry={() => targets.refetch()} emptyMessage="Crie uma organização ESG para usar o Action Center.">
        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {[
            ['Gaps abertos', openGaps.length, 'alert'], ['Riscos ativos', openRisks.length, 'activity'],
            ['Oportunidades', (opportunities.data ?? []).filter((item) => item.status === 'open').length, 'rocket'],
            ['Planos de ação', (actions.data ?? []).length, 'check'],
          ].map(([label, value, icon]) => <article key={String(label)} className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900"><AppIcon name={icon as Parameters<typeof AppIcon>[0]['name']} className="text-emerald-600" /><p className="mt-4 text-sm text-gray-500">{label}</p><p className="text-3xl font-bold text-gray-900 dark:text-white">{value}</p></article>)}
        </section>

        <section className="grid gap-6 xl:grid-cols-2">
          <article className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center gap-2"><AppIcon name="target" className="text-emerald-600" /><div><h2 className="font-bold text-gray-900 dark:text-white">Target Dashboard</h2><p className="text-sm text-gray-500">Progresso respeita a direção do indicador.</p></div></div>
            <div className="mt-4 space-y-3">{(targets.data ?? []).map((target) => <div key={target.id} className="rounded-xl border border-gray-100 p-3 dark:border-gray-800"><div className="flex justify-between gap-3"><div><p className="font-semibold text-gray-900 dark:text-white">{target.name}</p><p className="text-xs text-gray-500">{target.current_value ?? '—'} / {target.target_value} {target.unit} · até {target.target_year}</p></div><Badge value={target.tracking_status === 'achieved' ? 'low' : target.tracking_status === 'on_track' ? 'low' : target.tracking_status === 'at_risk' ? 'medium' : 'high'} /></div><div className="mt-3 h-2 overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800"><div className="h-full rounded-full bg-emerald-500" style={{ width: `${target.progress_percentage ?? 0}%` }} /></div></div>)}{!targets.data?.length && <p className="py-6 text-center text-sm text-gray-500">Nenhuma meta criada.</p>}</div>
          </article>

          <article className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center gap-2"><AppIcon name="alert" className="text-emerald-600" /><div><h2 className="font-bold text-gray-900 dark:text-white">Risk Matrix</h2><p className="text-sm text-gray-500">Probabilidade × impacto, escala de 1 a 5.</p></div></div>
            <div className="mt-4 grid grid-cols-5 gap-1">{Array.from({ length: 25 }, (_, index) => { const likelihood = 5 - Math.floor(index / 5); const impact = (index % 5) + 1; const count = openRisks.filter((risk) => risk.likelihood === likelihood && risk.impact === impact).length; return <div key={`${likelihood}-${impact}`} className={`flex aspect-square items-center justify-center rounded text-xs font-bold ${count ? 'bg-red-500 text-white' : 'bg-gray-100 text-gray-400 dark:bg-gray-800'}`} title={`Probabilidade ${likelihood}, impacto ${impact}`}>{count || '·'}</div>; })}</div>
            <div className="mt-4 space-y-2">{openRisks.slice(0, 3).map((risk) => <div key={risk.id} className="flex items-center justify-between gap-3 text-sm"><span className="truncate text-gray-700 dark:text-gray-200">{risk.description}</span><Badge value={risk.risk_level} /></div>)}</div>
          </article>
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <article className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900"><h2 className="font-bold text-gray-900 dark:text-white">Action Center</h2><div className="mt-4 space-y-3">{(actions.data ?? []).map((action) => <div key={action.id} className="rounded-xl border border-gray-100 p-3 dark:border-gray-800"><div className="flex justify-between gap-3"><div><p className="font-semibold text-gray-900 dark:text-white">{action.title}</p><p className="text-xs text-gray-500">{action.topic.name} · {action.tasks.length} tarefa(s)</p></div><Badge value={action.priority} /></div><p className="mt-2 text-sm text-gray-500">{action.progress_percentage}% concluído · {action.status}</p></div>)}{!actions.data?.length && <p className="py-6 text-center text-sm text-gray-500">Os planos de ação vinculados a gaps e riscos aparecerão aqui.</p>}</div></article>
          <aside className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900"><h2 className="font-bold text-gray-900 dark:text-white">Prioridades explicáveis</h2><div className="mt-4 space-y-3">{(priorities.data ?? []).map((item) => <div key={item.topic_id} className="rounded-xl border border-gray-100 p-3 dark:border-gray-800"><div className="flex justify-between gap-3"><p className="font-semibold text-gray-900 dark:text-white">{item.topic.name}</p><Badge value={item.priority} /></div><p className="mt-1 text-sm text-gray-500">Score {item.score} · evidências {item.evidence_ids.length}</p><p className="mt-1 text-xs text-gray-400">Mat. {item.breakdown.materiality} · gap {item.breakdown.gap_severity} · risco {item.breakdown.risk} · confiança {item.breakdown.evidence_confidence}</p></div>)}</div></aside>
        </section>
      </AsyncState>
    </div>
  );
}
