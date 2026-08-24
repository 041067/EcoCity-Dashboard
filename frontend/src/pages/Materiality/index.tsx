import { useMemo, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';

import { AsyncState } from '../../components/AsyncState';
import {
  useMaterialityAssessments,
  useMaterialityExplanation,
  useMaterialityExternalEvidence,
  useMaterialityMatrix,
  useMaterialityPriorities,
  useOrganizationStakeholders,
  useOrganizationTopics,
  useOrganizations,
} from '../../hooks/useApiQueries';
import { createMaterialityAssessment } from '../../services/api';
import type {
  FinancialAssessmentInput,
  ImpactAssessmentInput,
  MaterialityAssessment,
  StakeholderAssessmentInput,
} from '../../types';
import { formatScore, pointSize, priorityMeta } from './materialityUtils';

const STEP_TITLES = ['Tema', 'Impacto', 'Financeiro', 'Stakeholders', 'Revisão'];

const IMPACT_FIELDS: { key: keyof ImpactAssessmentInput; label: string; help: string }[] = [
  { key: 'severity', label: 'Severidade', help: 'Quão grave é o impacto potencial?' },
  { key: 'scope', label: 'Escopo', help: 'Qual a abrangência de pessoas, áreas ou ecossistemas afetados?' },
  { key: 'likelihood', label: 'Probabilidade', help: 'Qual a chance de o impacto ocorrer?' },
  { key: 'remediability', label: 'Remediabilidade', help: 'Quão difícil é reparar o impacto?' },
];

const FINANCIAL_FIELDS: { key: keyof FinancialAssessmentInput; label: string; help: string }[] = [
  { key: 'revenue_impact', label: 'Receita', help: 'Potencial de reduzir ou afetar receitas.' },
  { key: 'cost_impact', label: 'Custos', help: 'Potencial de aumentar custos operacionais.' },
  { key: 'asset_impact', label: 'Ativos', help: 'Potencial de afetar ativos ou seu valor.' },
  { key: 'financing_impact', label: 'Financiamento', help: 'Potencial de afetar crédito, capital ou seguros.' },
  { key: 'regulatory_impact', label: 'Regulação', help: 'Exposição a requisitos, multas ou restrições.' },
];

const initialImpact: ImpactAssessmentInput = {
  severity: 3,
  scope: 3,
  likelihood: 3,
  remediability: 3,
};
const initialFinancial: FinancialAssessmentInput = {
  revenue_impact: 3,
  cost_impact: 3,
  asset_impact: 3,
  financing_impact: 3,
  regulatory_impact: 3,
};

function RatingInput({
  id,
  label,
  help,
  value,
  onChange,
}: {
  id: string;
  label: string;
  help: string;
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <fieldset className="rounded-xl border border-gray-200 p-4 dark:border-gray-700">
      <legend className="font-semibold text-gray-900 dark:text-white">{label}</legend>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{help}</p>
      <div className="mt-3 grid grid-cols-5 gap-2" aria-label={label}>
        {[1, 2, 3, 4, 5].map((score) => (
          <label key={score} className="cursor-pointer">
            <input
              type="radio"
              name={id}
              value={score}
              checked={value === score}
              onChange={() => onChange(score)}
              className="peer sr-only"
            />
            <span className="flex h-10 items-center justify-center rounded-lg border border-gray-300 font-bold text-gray-600 peer-checked:border-emerald-600 peer-checked:bg-emerald-600 peer-checked:text-white hover:border-emerald-500 dark:border-gray-600 dark:text-gray-200">
              {score}
            </span>
          </label>
        ))}
      </div>
      <p className="mt-2 text-xs text-gray-400">1 = muito baixo · 5 = muito alto</p>
    </fieldset>
  );
}

function PriorityBadge({ priority }: { priority: MaterialityAssessment['priority_level'] }) {
  const meta = priorityMeta(priority);
  if (!meta) return <span className="text-xs text-gray-400">Em elaboração</span>;
  return <span className={`rounded-full px-2.5 py-1 text-xs font-bold ${meta.className}`}>{meta.label}</span>;
}

function Matrix({
  assessments,
  selectedId,
  onSelect,
}: {
  assessments: MaterialityAssessment[];
  selectedId: number | null;
  onSelect: (assessment: MaterialityAssessment) => void;
}) {
  return (
    <div className="relative h-[390px] overflow-hidden rounded-xl border border-gray-200 bg-gradient-to-tr from-emerald-50 via-white to-orange-50 p-8 dark:border-gray-700 dark:from-emerald-950/30 dark:via-gray-900 dark:to-orange-950/20">
      <div className="pointer-events-none absolute inset-8 border-l border-b border-gray-300 dark:border-gray-600" />
      <div className="pointer-events-none absolute inset-x-8 top-[43%] border-t border-dashed border-gray-300 dark:border-gray-600" />
      <div className="pointer-events-none absolute inset-y-8 left-[51%] border-l border-dashed border-gray-300 dark:border-gray-600" />
      <span className="absolute left-2 top-7 -rotate-90 text-xs font-bold uppercase tracking-widest text-gray-500">Impacto</span>
      <span className="absolute bottom-2 left-1/2 -translate-x-1/2 text-xs font-bold uppercase tracking-widest text-gray-500">Financeiro</span>
      <span className="absolute left-10 top-10 text-xs text-gray-400">100</span>
      <span className="absolute bottom-8 right-10 text-xs text-gray-400">100</span>
      {assessments.map((assessment) => {
        const impact = Math.max(2, Math.min(98, assessment.impact_score ?? 0));
        const financial = Math.max(2, Math.min(98, assessment.financial_score ?? 0));
        const meta = priorityMeta(assessment.priority_level);
        const size = pointSize(assessment.stakeholder_score ?? 0);
        return (
          <button
            key={assessment.id}
            type="button"
            aria-label={`Ver ${assessment.topic.name}`}
            title={assessment.topic.name}
            onClick={() => onSelect(assessment)}
            style={{ bottom: `${impact}%`, left: `${financial}%`, width: size, height: size }}
            className={`absolute z-10 -translate-x-1/2 translate-y-1/2 rounded-full border-4 border-white shadow-lg transition hover:scale-110 focus:outline-none focus:ring-4 focus:ring-emerald-300 dark:border-gray-900 ${meta?.dotClassName ?? 'bg-gray-400'} ${selectedId === assessment.id ? 'ring-4 ring-gray-900 dark:ring-white' : ''}`}
          />
        );
      })}
    </div>
  );
}

export function MaterialityPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const organizationsQuery = useOrganizations();
  const requestedId = Number(params.get('organization'));
  const organizationId = Number.isInteger(requestedId) && requestedId > 0 ? requestedId : organizationsQuery.data?.[0]?.id;
  const [selectedAssessment, setSelectedAssessment] = useState<MaterialityAssessment | null>(null);
  const organizationTopicsQuery = useOrganizationTopics(organizationId);
  const stakeholdersQuery = useOrganizationStakeholders(organizationId);
  const assessmentsQuery = useMaterialityAssessments(organizationId);
  const matrixQuery = useMaterialityMatrix(organizationId);
  const prioritiesQuery = useMaterialityPriorities(organizationId);
  const [step, setStep] = useState(0);
  const [topicId, setTopicId] = useState<number | null>(null);
  const [reportingYear, setReportingYear] = useState(new Date().getFullYear());
  const [impact, setImpact] = useState<ImpactAssessmentInput>(initialImpact);
  const [financial, setFinancial] = useState<FinancialAssessmentInput>(initialFinancial);
  const [stakeholderScores, setStakeholderScores] = useState<Record<number, StakeholderAssessmentInput>>({});
  const [evidenceSource, setEvidenceSource] = useState('');
  const [evidenceDescription, setEvidenceDescription] = useState('');
  const [formError, setFormError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const topics = useMemo(
    () => (organizationTopicsQuery.data ?? []).filter((link) => link.enabled),
    [organizationTopicsQuery.data],
  );
  const stakeholders = stakeholdersQuery.data ?? [];
  const matrixAssessments = matrixQuery.data?.assessments ?? [];
  const selectedTopic = topics.find((link) => link.topic_id === topicId)?.topic;
  const detail = selectedAssessment ?? matrixAssessments[0] ?? null;
  const explanationQuery = useMaterialityExplanation(organizationId, detail?.id);
  const externalEvidenceQuery = useMaterialityExternalEvidence(detail?.id);
  const isLoading = organizationsQuery.isLoading || (Boolean(organizationId) && organizationTopicsQuery.isLoading);
  const queryError = organizationsQuery.error ?? organizationTopicsQuery.error ?? matrixQuery.error;

  function updateStakeholder(stakeholderId: number, field: keyof StakeholderAssessmentInput, value: number) {
    setStakeholderScores((current) => ({
      ...current,
      [stakeholderId]: {
        stakeholder_id: stakeholderId,
        relevance: current[stakeholderId]?.relevance ?? 3,
        concern_level: current[stakeholderId]?.concern_level ?? 3,
        influence: current[stakeholderId]?.influence ?? 3,
        [field]: value,
      },
    }));
  }

  function nextStep() {
    setFormError(null);
    if (step === 0 && !topicId) {
      setFormError('Selecione um tema ESG para continuar.');
      return;
    }
    if (step === 3 && stakeholders.length === 0) {
      setFormError('Cadastre ao menos um stakeholder antes de concluir a avaliação.');
      return;
    }
    setStep((current) => Math.min(STEP_TITLES.length - 1, current + 1));
  }

  async function submit() {
    if (!organizationId || !topicId) return;
    setFormError(null);
    if (stakeholders.length === 0) {
      setFormError('Uma avaliação concluída precisa conter ao menos um stakeholder.');
      return;
    }
    setIsSaving(true);
    try {
      await createMaterialityAssessment(organizationId, {
        topic_id: topicId,
        reporting_year: reportingYear,
        impact,
        financial,
        stakeholders: stakeholders.map((stakeholder) => stakeholderScores[stakeholder.id] ?? {
          stakeholder_id: stakeholder.id,
          relevance: 3,
          concern_level: 3,
          influence: 3,
        }),
        evidences: evidenceSource.trim() && evidenceDescription.trim()
          ? [{ evidence_type: 'manual', source: evidenceSource.trim(), description: evidenceDescription.trim() }]
          : [],
        status: 'completed',
      });
      await Promise.all([assessmentsQuery.refetch(), matrixQuery.refetch(), prioritiesQuery.refetch()]);
      setSelectedAssessment(null);
      setStep(0);
      setTopicId(null);
      setEvidenceSource('');
      setEvidenceDescription('');
    } catch {
      setFormError('Não foi possível concluir a avaliação. Verifique se este tema já foi avaliado neste ano.');
    } finally {
      setIsSaving(false);
    }
  }

  const noOrganizations = !organizationsQuery.isLoading && (organizationsQuery.data?.length ?? 0) === 0;

  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm font-bold uppercase tracking-widest text-emerald-600">EcoCity ESG · Sprint 7</p>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Matriz de Materialidade</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Dupla materialidade calculada no servidor, com critérios e evidências rastreáveis.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {(organizationsQuery.data?.length ?? 0) > 1 && (
            <select
              value={organizationId ?? ''}
              onChange={(event) => navigate(`/esg/materiality?organization=${event.target.value}`)}
              aria-label="Selecionar organização"
              className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-700 dark:bg-gray-900 dark:text-white"
            >
              {organizationsQuery.data?.map((organization) => <option key={organization.id} value={organization.id}>{organization.name}</option>)}
            </select>
          )}
          <Link to={organizationId ? `/esg?organization=${organizationId}` : '/esg'} className="rounded-lg border border-emerald-600 px-3 py-2 text-sm font-semibold text-emerald-700 hover:bg-emerald-50 dark:text-emerald-300">Gerenciar ESG</Link>
        </div>
      </header>

      <AsyncState isLoading={isLoading} isError={Boolean(queryError)} isEmpty={noOrganizations} error={queryError} onRetry={() => organizationsQuery.refetch()} emptyMessage="Configure uma organização ESG antes de avaliar materialidade.">
        <section className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
          <article className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="mb-4 flex items-center justify-between"><div><h2 className="font-bold text-gray-900 dark:text-white">Materialidade {matrixQuery.data?.reporting_year ?? '—'}</h2><p className="text-sm text-gray-500 dark:text-gray-400">X = financeiro · Y = impacto · tamanho = stakeholders</p></div><span className="text-sm font-semibold text-gray-500">{matrixAssessments.length} temas</span></div>
            {matrixAssessments.length ? <Matrix assessments={matrixAssessments} selectedId={detail?.id ?? null} onSelect={setSelectedAssessment} /> : <div className="flex h-[390px] items-center justify-center rounded-xl border border-dashed border-gray-300 text-center text-sm text-gray-500 dark:border-gray-700 dark:text-gray-400">Ainda não há avaliações concluídas para compor a matriz.</div>}
          </article>
          <aside className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <h2 className="font-bold text-gray-900 dark:text-white">{detail ? detail.topic.name : 'Detalhe do tema'}</h2>
            {detail ? <><div className="mt-3 flex items-center justify-between"><span className="text-4xl font-bold text-gray-900 dark:text-white">{formatScore(detail.materiality_score)}</span><PriorityBadge priority={detail.priority_level} /></div><p className="mt-1 text-sm text-gray-500">Materialidade calculada</p><dl className="mt-5 space-y-3 text-sm"><div className="flex justify-between border-b border-gray-100 pb-2 dark:border-gray-800"><dt>Impacto</dt><dd className="font-bold">{formatScore(detail.impact_score)}</dd></div><div className="flex justify-between border-b border-gray-100 pb-2 dark:border-gray-800"><dt>Financeiro</dt><dd className="font-bold">{formatScore(detail.financial_score)}</dd></div><div className="flex justify-between border-b border-gray-100 pb-2 dark:border-gray-800"><dt>Stakeholders</dt><dd className="font-bold">{formatScore(detail.stakeholder_score)}</dd></div></dl><section className="mt-5 rounded-lg border border-emerald-100 bg-emerald-50/50 p-3 text-xs dark:border-emerald-900/60 dark:bg-emerald-950/20"><p className="font-bold text-emerald-800 dark:text-emerald-200">Evidências externas</p>{externalEvidenceQuery.isLoading ? <p className="mt-2 text-gray-500">Carregando evidências externas…</p> : externalEvidenceQuery.data?.length ? <div className="mt-2 space-y-2">{externalEvidenceQuery.data.slice(0, 3).map((evidence) => <div key={evidence.id} className="flex justify-between gap-2"><span>{evidence.indicator_value.indicator.name}<small className="block text-gray-500">{evidence.indicator_value.source}</small></span><strong>{evidence.indicator_value.value.toFixed(1)} {evidence.indicator_value.unit}</strong></div>)}</div> : <p className="mt-2 text-gray-500">Nenhuma evidência externa vinculada ainda.</p>}</section>{selectedAssessment && <details className="mt-5 rounded-lg bg-gray-50 p-3 text-xs dark:bg-gray-800"><summary className="cursor-pointer font-bold text-emerald-700 dark:text-emerald-300">Ver critérios e evidências</summary>{explanationQuery.isLoading ? <p className="mt-2 text-gray-500">Carregando explicação…</p> : explanationQuery.data ? <div className="mt-3 space-y-3"><p>Pesos aplicados: impacto {Math.round(explanationQuery.data.weights.impact * 100)}% · financeiro {Math.round(explanationQuery.data.weights.financial * 100)}% · stakeholders {Math.round(explanationQuery.data.weights.stakeholder * 100)}%</p>{explanationQuery.data.impact_assessment && <p><strong>Impacto:</strong> severidade {explanationQuery.data.impact_assessment.severity}/5 · escopo {explanationQuery.data.impact_assessment.scope}/5 · probabilidade {explanationQuery.data.impact_assessment.likelihood}/5 · remediabilidade {explanationQuery.data.impact_assessment.remediability}/5</p>}{explanationQuery.data.financial_assessment && <p><strong>Financeiro:</strong> receita {explanationQuery.data.financial_assessment.revenue_impact}/5 · custos {explanationQuery.data.financial_assessment.cost_impact}/5 · ativos {explanationQuery.data.financial_assessment.asset_impact}/5 · financiamento {explanationQuery.data.financial_assessment.financing_impact}/5 · regulação {explanationQuery.data.financial_assessment.regulatory_impact}/5</p>}<p><strong>Evidências:</strong> {explanationQuery.data.evidences.length ? explanationQuery.data.evidences.map((evidence) => evidence.source).join(', ') : 'não registradas'}</p></div> : <p className="mt-2 text-gray-500">A explicação não está disponível no momento.</p>}</details>}<p className="mt-5 text-xs text-gray-400">Clique nos pontos da matriz para comparar temas.</p></> : <p className="mt-3 text-sm text-gray-500">Conclua a primeira avaliação para ver a explicação de cada resultado.</p>}
          </aside>
        </section>

        <section className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
          <article className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex flex-wrap gap-2" aria-label="Etapas do wizard">{STEP_TITLES.map((title, index) => <span key={title} className={`rounded-full px-3 py-1 text-xs font-bold ${index === step ? 'bg-emerald-600 text-white' : index < step ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200' : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400'}`}>{index + 1}. {title}</span>)}</div>
            <div className="mt-6"><h2 className="text-lg font-bold text-gray-900 dark:text-white">{STEP_TITLES[step]}</h2>
              {step === 0 && <div className="mt-4 grid gap-4 sm:grid-cols-2"><label><span className="text-sm font-medium">Ano de reporte</span><input type="number" min="2000" max="2100" value={reportingYear} onChange={(event) => setReportingYear(Number(event.target.value))} className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 dark:border-gray-700 dark:bg-gray-950 dark:text-white" /></label><label><span className="text-sm font-medium">Tema ESG</span><select value={topicId ?? ''} onChange={(event) => setTopicId(Number(event.target.value) || null)} className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 dark:border-gray-700 dark:bg-gray-950 dark:text-white"><option value="">Selecione um tema</option>{topics.map((link) => <option key={link.id} value={link.topic_id}>{link.topic.name}</option>)}</select></label><p className="sm:col-span-2 text-sm text-gray-500">{selectedTopic?.description ?? 'Apenas temas ativos no ESG Overview podem ser avaliados.'}</p></div>}
              {step === 1 && <div className="mt-4 grid gap-4 md:grid-cols-2">{IMPACT_FIELDS.map((field) => <RatingInput key={field.key} id={field.key} label={field.label} help={field.help} value={impact[field.key]} onChange={(value) => setImpact((current) => ({ ...current, [field.key]: value }))} />)}</div>}
              {step === 2 && <div className="mt-4 grid gap-4 md:grid-cols-2">{FINANCIAL_FIELDS.map((field) => <RatingInput key={field.key} id={field.key} label={field.label} help={field.help} value={financial[field.key]} onChange={(value) => setFinancial((current) => ({ ...current, [field.key]: value }))} />)}</div>}
              {step === 3 && <div className="mt-4 space-y-4">{stakeholders.length ? stakeholders.map((stakeholder) => { const scores = stakeholderScores[stakeholder.id] ?? { stakeholder_id: stakeholder.id, relevance: 3, concern_level: 3, influence: 3 }; return <div key={stakeholder.id} className="rounded-xl border border-gray-200 p-4 dark:border-gray-700"><h3 className="font-semibold text-gray-900 dark:text-white">{stakeholder.name}</h3><div className="mt-3 grid gap-3 sm:grid-cols-3"><RatingInput id={`relevance-${stakeholder.id}`} label="Relevância" help="Importância do tema" value={scores.relevance} onChange={(value) => updateStakeholder(stakeholder.id, 'relevance', value)} /><RatingInput id={`concern-${stakeholder.id}`} label="Preocupação" help="Nível de preocupação" value={scores.concern_level} onChange={(value) => updateStakeholder(stakeholder.id, 'concern_level', value)} /><RatingInput id={`influence-${stakeholder.id}`} label="Influência" help="Poder de influência" value={scores.influence} onChange={(value) => updateStakeholder(stakeholder.id, 'influence', value)} /></div></div>; }) : <p className="rounded-lg bg-amber-50 p-4 text-sm text-amber-800 dark:bg-amber-950/30 dark:text-amber-200">Não há stakeholders cadastrados. <Link to={organizationId ? `/esg?organization=${organizationId}` : '/esg'} className="font-bold underline">Cadastre-os no ESG Overview</Link> para concluir o cálculo.</p>}</div>}
              {step === 4 && <div className="mt-4 space-y-4"><div className="rounded-xl bg-gray-50 p-4 text-sm dark:bg-gray-800"><p><strong>Tema:</strong> {selectedTopic?.name}</p><p className="mt-1"><strong>Ano:</strong> {reportingYear}</p><p className="mt-1"><strong>Stakeholders:</strong> {stakeholders.length}</p><p className="mt-1 text-gray-500">O servidor calculará as três dimensões e aplicará os pesos 40% / 40% / 20%.</p></div><div className="grid gap-3 sm:grid-cols-2"><label><span className="text-sm font-medium">Fonte da evidência (opcional)</span><input value={evidenceSource} onChange={(event) => setEvidenceSource(event.target.value)} maxLength={500} className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 dark:border-gray-700 dark:bg-gray-950 dark:text-white" placeholder="Ex.: Consulta a stakeholders" /></label><label><span className="text-sm font-medium">Descrição da evidência (opcional)</span><input value={evidenceDescription} onChange={(event) => setEvidenceDescription(event.target.value)} maxLength={4000} className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 dark:border-gray-700 dark:bg-gray-950 dark:text-white" placeholder="Resumo da fonte utilizada" /></label></div></div>}
            </div>
            {formError && <p role="alert" className="mt-5 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{formError}</p>}
            <div className="mt-6 flex justify-between gap-3"><button type="button" onClick={() => { setFormError(null); setStep((current) => Math.max(0, current - 1)); }} disabled={step === 0 || isSaving} className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-semibold disabled:opacity-40 dark:border-gray-700">Voltar</button>{step === STEP_TITLES.length - 1 ? <button type="button" onClick={submit} disabled={isSaving} className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-60">{isSaving ? 'Calculando…' : 'Calcular materialidade'}</button> : <button type="button" onClick={nextStep} className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700">Continuar</button>}</div>
          </article>
          <aside className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900"><h2 className="font-bold text-gray-900 dark:text-white">Temas prioritários</h2>{prioritiesQuery.data?.length ? <ol className="mt-4 space-y-3">{prioritiesQuery.data.map((assessment, index) => <li key={assessment.id} className="flex items-center justify-between gap-3"><span className="flex min-w-0 items-center gap-2"><span className="font-bold text-gray-400">{index + 1}</span><span className="truncate text-sm font-medium">{assessment.topic.name}</span></span><span className="flex items-center gap-2"><PriorityBadge priority={assessment.priority_level} /><strong>{formatScore(assessment.materiality_score)}</strong></span></li>)}</ol> : <p className="mt-3 text-sm text-gray-500">As avaliações concluídas aparecerão aqui em ordem de prioridade.</p>}<div className="mt-6 border-t border-gray-100 pt-4 text-xs text-gray-500 dark:border-gray-800"><p className="font-bold text-gray-700 dark:text-gray-300">Metodologia configurável</p><p className="mt-1">Impacto 40% · Financeiro 40% · Stakeholders 20%. Scores e prioridade são calculados no backend.</p></div></aside>
        </section>
      </AsyncState>
    </div>
  );
}
