import { useEffect, useRef, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Link, useSearchParams } from 'react-router-dom';
import { AsyncState } from '../../components/AsyncState';
import { AppIcon } from '../../components/icons/AppIcon';
import { useOrganizations } from '../../hooks/useApiQueries';
import { generateExecutiveSummary, sendCopilotMessage } from '../../services/api';
import type {
  CopilotChatResponse,
  DataSufficiency,
  ExecutiveSummaryContent,
  GroundedItem,
} from '../../types';

interface Message {
  role: 'user' | 'assistant';
  text: string;
  evidenceIds?: string[];
  limitations?: string[];
}

const SUPPORT_STYLE = {
  high: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200',
  medium: 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-200',
  low: 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-200',
};

function Evidence({ ids }: { ids: string[] }) {
  if (!ids.length) return null;
  return (
    <p className="mt-2 flex flex-wrap gap-1 text-xs text-gray-500 dark:text-gray-400">
      {ids.map((id) => <span key={id} className="rounded bg-gray-100 px-1.5 py-0.5 font-mono dark:bg-gray-800">{id}</span>)}
    </p>
  );
}

function Support({ data }: { data: DataSufficiency }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-800 dark:bg-gray-900">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-xs font-bold uppercase tracking-widest text-gray-500">Suporte dos dados</p>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
            {data.evidence_count} evidência(s) · cobertura {data.coverage_percentage}%
          </p>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-bold uppercase ${SUPPORT_STYLE[data.level]}`}>
          {data.level}
        </span>
      </div>
      {data.missing.length > 0 && <p className="mt-3 text-xs text-amber-700 dark:text-amber-300">Dados ausentes: {data.missing.join(', ')}.</p>}
    </div>
  );
}

function InsightList({ title, items }: { title: string; items: GroundedItem[] }) {
  return (
    <section className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-800 dark:bg-gray-900">
      <h2 className="font-bold text-gray-900 dark:text-white">{title}</h2>
      {items.length ? <div className="mt-3 space-y-3">{items.map((item, index) => (
        <article key={`${item.title}-${index}`} className="border-l-2 border-emerald-500 pl-3">
          <p className="text-sm font-semibold text-gray-900 dark:text-white">{item.title}</p>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">{item.detail}</p>
          <Evidence ids={item.evidence_ids} />
        </article>
      ))}</div> : <p className="mt-3 text-sm text-gray-500">Nenhum registro relevante no contexto atual.</p>}
    </section>
  );
}

export function CopilotPage() {
  const [params] = useSearchParams();
  const organizations = useOrganizations();
  const requestedId = Number(params.get('organization'));
  const organizationId = Number.isInteger(requestedId) && requestedId > 0 ? requestedId : organizations.data?.[0]?.id;
  const [summary, setSummary] = useState<ExecutiveSummaryContent | null>(null);
  const [support, setSupport] = useState<DataSufficiency | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const feed = useRef<HTMLDivElement>(null);

  const summaryMutation = useMutation({
    mutationFn: () => generateExecutiveSummary(organizationId!),
    onSuccess: (result) => {
      setSummary(result.content);
      setSupport(result.data_sufficiency);
    },
  });
  const chatMutation = useMutation({
    mutationFn: (question: string) => sendCopilotMessage(organizationId!, question),
    onSuccess: (result: CopilotChatResponse) => {
      setSupport(result.data_sufficiency);
      setMessages((previous) => [...previous, {
        role: 'assistant', text: result.answer, evidenceIds: result.evidence_ids, limitations: result.limitations,
      }]);
    },
    onError: () => setMessages((previous) => [...previous, {
      role: 'assistant', text: 'O Copilot está temporariamente indisponível. Os motores ESG e seus dados continuam acessíveis.',
    }]),
  });

  useEffect(() => {
    feed.current?.scrollTo({ top: feed.current.scrollHeight, behavior: 'smooth' });
  }, [messages, chatMutation.isPending]);

  const ask = (question?: string) => {
    const value = (question ?? input).trim();
    if (!value || !organizationId || chatMutation.isPending) return;
    setInput('');
    setMessages((previous) => [...previous, { role: 'user', text: value }]);
    chatMutation.mutate(value);
  };
  const noOrganizations = !organizations.isLoading && !organizations.data?.length;

  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm font-bold uppercase tracking-widest text-emerald-600">EcoCity AI · Sprint 10</p>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">ESG AI Copilot</h1>
          <p className="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">Interpreta dados ESG rastreáveis; não recalcula scores nem cria ações automaticamente.</p>
        </div>
        <button type="button" onClick={() => summaryMutation.mutate()} disabled={!organizationId || summaryMutation.isPending} className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-bold text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60">
          <AppIcon name="brain" className="h-4 w-4" />
          {summaryMutation.isPending ? 'Analisando…' : 'Gerar resumo executivo'}
        </button>
      </header>

      <AsyncState isLoading={organizations.isLoading} isError={organizations.isError} isEmpty={noOrganizations} error={organizations.error} onRetry={() => organizations.refetch()} emptyMessage="Crie uma organização ESG antes de usar o Copilot.">
        <>
          {summaryMutation.isError && <p role="alert" className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-200">O Copilot está indisponível neste momento. A plataforma continua operando normalmente com os dados ESG determinísticos.</p>}
          {support && <Support data={support} />}
          {summary && <section className="grid gap-4 lg:grid-cols-2">
            <article className="rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-50 to-cyan-50 p-5 dark:border-emerald-900 dark:from-emerald-950/40 dark:to-gray-900 lg:col-span-2">
              <div className="flex items-center gap-2"><AppIcon name="bot" className="text-emerald-600" /><h2 className="font-bold text-gray-900 dark:text-white">Situação geral</h2></div>
              <p className="mt-3 max-w-4xl text-sm leading-6 text-gray-700 dark:text-gray-200">{summary.overall_situation}</p>
            </article>
            <InsightList title="Temas críticos" items={summary.critical_topics} />
            <InsightList title="Riscos-chave" items={summary.key_risks} />
            <InsightList title="Oportunidades" items={summary.opportunities} />
            <InsightList title="Metas que exigem atenção" items={summary.targets_requiring_attention} />
            <InsightList title="Prioridades recomendadas" items={summary.recommended_priorities} />
            <article className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-800 dark:bg-gray-900">
              <h2 className="font-bold text-gray-900 dark:text-white">Limitações dos dados</h2>
              <ul className="mt-3 space-y-2 text-sm text-gray-600 dark:text-gray-300">
                {summary.data_limitations.length ? summary.data_limitations.map((item) => <li key={item}>• {item}</li>) : <li>Nenhuma limitação adicional identificada.</li>}
              </ul>
            </article>
          </section>}

          <section className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
              <div><h2 className="font-bold text-gray-900 dark:text-white">Converse com o Copilot</h2><p className="text-sm text-gray-500">As respostas usam somente os dados consolidados da organização.</p></div>
              <Link to={`/esg/recommendations${organizationId ? `?organization=${organizationId}` : ''}`} className="inline-flex items-center gap-2 text-sm font-bold text-emerald-700 hover:underline dark:text-emerald-300"><AppIcon name="rocket" className="h-4 w-4" />Ver recomendações</Link>
            </div>
            <div ref={feed} className="mt-4 max-h-96 min-h-40 space-y-3 overflow-y-auto rounded-xl bg-gray-50 p-3 dark:bg-gray-950/50">
              {!messages.length && <p className="p-4 text-center text-sm text-gray-500">Pergunte sobre riscos, metas atrasadas, gaps ou prioridades do próximo trimestre.</p>}
              {messages.map((message, index) => <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}><div className={`max-w-full rounded-2xl px-4 py-3 text-sm sm:max-w-[85%] ${message.role === 'user' ? 'bg-emerald-600 text-white' : 'bg-white text-gray-800 shadow-sm dark:bg-gray-800 dark:text-gray-100'}`}><p className="whitespace-pre-wrap">{message.text}</p><Evidence ids={message.evidenceIds ?? []} />{message.limitations?.length ? <p className="mt-2 text-xs text-amber-700 dark:text-amber-300">Limitações: {message.limitations.join('; ')}.</p> : null}</div></div>)}
              {chatMutation.isPending && <p className="text-sm text-gray-500">O Copilot está analisando os dados…</p>}
            </div>
            <div className="mt-3 flex flex-col gap-2 sm:flex-row"><input value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => event.key === 'Enter' && ask()} maxLength={1000} placeholder="Ex.: Quais metas estão atrasadas?" className="min-h-11 flex-1 rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-900 focus:border-emerald-500 focus:outline-none dark:border-gray-700 dark:bg-gray-950 dark:text-white" /><button type="button" onClick={() => ask()} disabled={!input.trim() || chatMutation.isPending} className="min-h-11 rounded-lg bg-emerald-600 px-5 text-sm font-bold text-white hover:bg-emerald-700 disabled:opacity-50">Enviar</button></div>
            <div className="mt-3 flex flex-wrap gap-2">{['Quais temas exigem atenção imediata?', 'Quais metas estão atrasadas?', 'Que dados estão faltando?'].map((question) => <button type="button" key={question} onClick={() => ask(question)} disabled={chatMutation.isPending} className="rounded-full border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-600 hover:border-emerald-400 hover:text-emerald-700 disabled:opacity-50 dark:border-gray-700 dark:text-gray-300">{question}</button>)}</div>
          </section>
        </>
      </AsyncState>
    </div>
  );
}
