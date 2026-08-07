import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { CityMapBackground } from './CityMapBackground';

const NAV_LINKS = [
  { href: '#problema', label: 'O Problema' },
  { href: '#solucao', label: 'A Solução' },
  { href: '#recursos', label: 'Recursos' },
  { href: '#metricas', label: 'Métricas' },
];

const HERO_CHIPS = ['Dados em tempo real', 'IA Generativa', 'Monitoramento Ambiental'];

const SOLUTION_CARDS = [
  { icon: '🌦️', title: 'Clima', description: 'Dados meteorológicos em tempo real.' },
  { icon: '🌎', title: 'Qualidade do Ar', description: 'Monitoramento contínuo.' },
  { icon: '🤖', title: 'IA Generativa', description: 'Relatórios automáticos.' },
  { icon: '🗺️', title: 'Mapas', description: 'Visualização geográfica.' },
  { icon: '📈', title: 'Dashboard', description: 'Indicadores em tempo real.' },
  { icon: '🚨', title: 'Alertas', description: 'Eventos críticos automaticamente detectados.' },
];

const FEATURE_GROUPS = [
  {
    icon: '📡',
    title: 'Monitoramento',
    items: ['Temperatura', 'Umidade', 'Vento', 'Índice UV', 'AQI'],
  },
  {
    icon: '🧠',
    title: 'Inteligência Artificial',
    items: ['Chat IA', 'Relatórios', 'Recomendações'],
  },
];

const METRICS = [
  { value: '5', label: 'Cidades Monitoradas' },
  { value: '24h', label: 'Histórico Inteligente' },
  { value: '15 min', label: 'Atualização automática' },
];

const PROBLEM_STEPS = [
  { icon: '🏙️', label: 'Cidade', sub: 'Sensores e órgãos públicos' },
  { icon: '🌦️', label: 'Clima', sub: 'Boletins meteorológicos' },
  { icon: '🌫️', label: 'Poluição', sub: 'Qualidade do ar' },
  { icon: '🚗', label: 'Trânsito', sub: 'Mobilidade urbana' },
];

function Eyebrow({ dark = false, children }: { dark?: boolean; children: ReactNode }) {
  return (
    <p className={`text-sm font-bold uppercase tracking-widest ${dark ? 'text-emerald-400' : 'text-emerald-600'}`}>
      {children}
    </p>
  );
}

function Hero() {
  return (
    <section id="inicio" className="relative flex min-h-[calc(100vh-4rem)] items-center overflow-hidden bg-slate-950">
      <CityMapBackground />

      <div className="pointer-events-none absolute bottom-16 right-8 z-10 hidden w-80 lg:block">
        <div className="animate-float rounded-2xl border border-emerald-400/30 bg-slate-950/70 p-5 shadow-2xl shadow-emerald-500/10 backdrop-blur-md">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" />
              <span className="text-sm font-semibold text-white">EcoCity · São Paulo</span>
            </div>
            <span className="rounded-full bg-emerald-400/20 px-2 py-0.5 text-xs font-semibold text-emerald-300">
              ● Ao vivo
            </span>
          </div>
          <div className="mt-4">
            <p className="text-xs uppercase tracking-wide text-slate-400">Eco Score</p>
            <p className="text-4xl font-extrabold text-emerald-400">
              87<span className="text-lg font-semibold text-slate-400">/100</span>
            </p>
            <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-700">
              <div className="h-full w-[87%] rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400" />
            </div>
          </div>
          <svg viewBox="0 0 300 80" className="mt-4 w-full" aria-hidden="true">
            <polygon
              points="0,60 30,52 60,58 90,40 120,46 150,30 180,36 210,22 240,28 270,14 300,18 300,80 0,80"
              fill="#34d399"
              opacity="0.15"
            />
            <polyline
              points="0,60 30,52 60,58 90,40 120,46 150,30 180,36 210,22 240,28 270,14 300,18"
              fill="none"
              stroke="#34d399"
              strokeWidth="2.5"
              strokeLinecap="round"
            />
          </svg>
          <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
            <div className="rounded-lg bg-slate-800/60 p-2.5">
              <p className="text-xs text-slate-400">Temperatura</p>
              <p className="font-semibold text-white">24.5°C</p>
            </div>
            <div className="rounded-lg bg-slate-800/60 p-2.5">
              <p className="text-xs text-slate-400">AQI</p>
              <p className="font-semibold text-white">42 · Bom</p>
            </div>
            <div className="rounded-lg bg-slate-800/60 p-2.5">
              <p className="text-xs text-slate-400">Umidade</p>
              <p className="font-semibold text-white">61%</p>
            </div>
            <div className="rounded-lg bg-slate-800/60 p-2.5">
              <p className="text-xs text-slate-400">Alertas IA</p>
              <p className="font-semibold text-emerald-300">Nenhum risco</p>
            </div>
          </div>
        </div>
      </div>

      <div className="relative z-10 mx-auto w-full max-w-7xl px-4 py-24">
        <div className="max-w-3xl">
          <p className="inline-flex items-center gap-2 rounded-full border border-emerald-400/40 bg-emerald-400/10 px-4 py-1.5 text-sm font-medium text-emerald-300">
            <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
            IA para transformar dados ambientais em decisões inteligentes
          </p>
          <h1 className="mt-6 text-4xl font-extrabold text-white sm:text-5xl lg:text-6xl">
            🌎 EcoCity Dashboard
          </h1>
          <p className="mt-5 text-xl font-semibold text-cyan-300 sm:text-2xl">
            Transformando dados ambientais em decisões inteligentes para cidades mais sustentáveis.
          </p>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-slate-300 sm:text-lg">
            O EcoCity Dashboard é uma plataforma de monitoramento ambiental baseada em Inteligência
            Artificial que coleta dados públicos em tempo real, gera análises inteligentes,
            identifica riscos e oferece uma visão unificada para apoiar decisões em iniciativas de
            Smart Cities.
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-4">
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 rounded-full bg-emerald-500 px-8 py-4 text-lg font-bold text-white shadow-lg shadow-emerald-500/30 transition hover:scale-105 hover:bg-emerald-400"
            >
              🚀 Acessar Dashboard
            </Link>
            <a
              href="#solucao"
              className="rounded-full border border-slate-500 px-8 py-4 text-lg font-semibold text-slate-200 transition hover:border-emerald-400 hover:text-emerald-300"
            >
              Conhecer a plataforma
            </a>
          </div>
          <div className="mt-10 flex flex-wrap gap-3">
            {HERO_CHIPS.map((chip) => (
              <span
                key={chip}
                className="rounded-full border border-slate-700 bg-slate-800/60 px-4 py-1.5 text-sm font-medium text-slate-200"
              >
                {chip}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="absolute bottom-6 left-1/2 z-10 -translate-x-1/2 animate-bounce text-2xl text-slate-400" aria-hidden="true">
        ↓
      </div>
    </section>
  );
}

function Problem() {
  return (
    <section id="problema" className="bg-slate-50 py-24">
      <div className="mx-auto grid max-w-7xl items-center gap-16 px-4 lg:grid-cols-2">
        <div>
          <Eyebrow>O Problema</Eyebrow>
          <h2 className="mt-4 text-3xl font-extrabold text-slate-900 sm:text-4xl">
            As cidades geram milhões de dados.
            <span className="block text-emerald-600">
              Mas poucos deles se transformam em decisões.
            </span>
          </h2>
          <p className="mt-6 text-lg leading-relaxed text-slate-600">
            Mudanças climáticas, ondas de calor, baixa qualidade do ar e eventos extremos exigem
            monitoramento constante. Entretanto, muitas cidades ainda trabalham com informações
            descentralizadas e análises manuais.
          </p>
          <ul className="mt-8 space-y-4">
            {[
              ['📂', 'Informações descentralizadas', 'Cada secretaria guarda seus próprios dados, sem conexão entre eles.'],
              ['⏳', 'Análises manuais e lentas', 'Boletins levam dias para sair — tempo demais para reagir.'],
              ['⚠️', 'Decisões reativas', 'Sem visão unificada, as cidades agem depois do evento, não antes.'],
            ].map(([icon, title, sub]) => (
              <li key={title} className="flex items-start gap-4">
                <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-white text-xl shadow-sm ring-1 ring-slate-200">
                  {icon}
                </span>
                <div>
                  <p className="font-semibold text-slate-800">{title}</p>
                  <p className="text-sm text-slate-500">{sub}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className="flex justify-center">
          <div className="w-full max-w-sm rounded-3xl border border-slate-200 bg-white p-6 shadow-xl shadow-slate-200/60">
            <div className="space-y-0">
              {PROBLEM_STEPS.map((step, i) => (
                <div key={step.label}>
                  <div className="flex items-center gap-4 rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4">
                    <span className="text-2xl">{step.icon}</span>
                    <div>
                      <p className="font-bold text-slate-800">{step.label}</p>
                      <p className="text-xs text-slate-500">{step.sub}</p>
                    </div>
                  </div>
                  {i < PROBLEM_STEPS.length - 1 && (
                    <div className="my-1 flex justify-center py-1 text-lg text-slate-400" aria-hidden="true">
                      ↓
                    </div>
                  )}
                </div>
              ))}
              <div className="mt-1 flex items-center gap-4 rounded-2xl border-2 border-dashed border-red-300 bg-red-50 px-5 py-4">
                <span className="text-2xl">⚠️</span>
                <div>
                  <p className="font-bold text-red-600">Dados espalhados</p>
                  <p className="text-xs text-red-400">Informações desconectadas, sem análise</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Solution() {
  return (
    <section id="solucao" className="relative overflow-hidden bg-slate-950 py-24">
      <div className="absolute -top-40 left-1/2 h-96 w-[800px] -translate-x-1/2 rounded-full bg-emerald-500/10 blur-3xl" aria-hidden="true" />
      <div className="relative mx-auto max-w-7xl px-4">
        <div className="text-center">
          <Eyebrow dark>A Solução</Eyebrow>
          <h2 className="mt-4 text-3xl font-extrabold text-white sm:text-4xl">
            Uma plataforma inteligente para cidades.
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-slate-400">
            Todo o ecossistema ambiental urbano em um único lugar, com dados conectados e análises
            geradas por Inteligência Artificial.
          </p>
        </div>
        <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {SOLUTION_CARDS.map((card) => (
            <div
              key={card.title}
              className="group rounded-2xl border border-white/10 bg-white/5 p-6 transition hover:border-emerald-400/50 hover:bg-white/10"
            >
              <span className="text-3xl">{card.icon}</span>
              <h3 className="mt-4 text-lg font-bold text-white">{card.title}</h3>
              <p className="mt-1 text-sm text-slate-400">{card.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Features() {
  return (
    <section id="recursos" className="bg-white py-24">
      <div className="mx-auto max-w-7xl px-4">
        <div className="text-center">
          <Eyebrow>Recursos</Eyebrow>
          <h2 className="mt-4 text-3xl font-extrabold text-slate-900 sm:text-4xl">
            Tudo o que uma cidade precisa para decidir melhor.
          </h2>
        </div>
        <div className="mt-14 grid gap-8 md:grid-cols-2">
          {FEATURE_GROUPS.map((group) => (
            <div key={group.title} className="rounded-3xl border border-slate-200 bg-slate-50 p-8">
              <div className="flex items-center gap-3">
                <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-500 to-emerald-500 text-2xl">
                  {group.icon}
                </span>
                <h3 className="text-xl font-bold text-slate-900">{group.title}</h3>
              </div>
              <ul className="mt-6 grid gap-3 sm:grid-cols-2">
                {group.items.map((item) => (
                  <li
                    key={item}
                    className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-700"
                  >
                    <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-100 text-xs font-bold text-emerald-600">
                      ✔
                    </span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Metrics() {
  return (
    <section id="metricas" className="bg-slate-950 py-24">
      <div className="mx-auto max-w-7xl px-4">
        <h2 className="text-center text-3xl font-extrabold text-white sm:text-4xl">
          Inteligência em escala urbana.
        </h2>
        <div className="mt-14 grid gap-8 sm:grid-cols-3">
          {METRICS.map((metric) => (
            <div
              key={metric.label}
              className="rounded-3xl border border-white/10 bg-gradient-to-b from-white/10 to-transparent p-8 text-center"
            >
              <p className="bg-gradient-to-r from-cyan-400 to-emerald-400 bg-clip-text text-6xl font-extrabold text-transparent">
                {metric.value}
              </p>
              <p className="mt-3 text-lg font-semibold text-slate-300">{metric.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function FinalCta() {
  return (
    <section className="relative flex min-h-screen items-center justify-center overflow-hidden bg-slate-950 text-center">
      <div className="absolute inset-0 bg-gradient-to-b from-slate-950 via-emerald-950/40 to-slate-950" aria-hidden="true" />
      <div
        className="absolute left-1/2 top-1/2 h-[600px] w-[900px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-emerald-500/10 blur-3xl"
        aria-hidden="true"
      />
      <div className="relative z-10 mx-auto max-w-3xl px-4">
        <p className="text-5xl" aria-hidden="true">
          🌎
        </p>
        <h2 className="mt-6 text-4xl font-extrabold text-white sm:text-5xl">
          O futuro das cidades começa com{' '}
          <span className="bg-gradient-to-r from-cyan-400 to-emerald-400 bg-clip-text text-transparent">
            dados inteligentes
          </span>
          .
        </h2>
        <p className="mt-6 text-lg text-slate-400">
          Monitore, analise e decida com a plataforma de inteligência ambiental feita para Smart
          Cities.
        </p>
        <Link
          to="/dashboard"
          className="mt-10 inline-flex items-center gap-2 rounded-full bg-emerald-500 px-10 py-5 text-xl font-bold text-white shadow-xl shadow-emerald-500/40 transition hover:scale-105 hover:bg-emerald-400"
        >
          🚀 Abrir Plataforma
        </Link>
      </div>
    </section>
  );
}

export function Landing() {
  return (
    <div className="scroll-smooth bg-white text-slate-900">
      <header className="sticky top-0 z-50 border-b border-white/10 bg-slate-950/80 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <a href="#inicio" className="flex items-center gap-2 text-xl font-bold text-emerald-400">
            <span>🌿</span>
            <span>EcoCity</span>
          </a>
          <nav className="hidden items-center gap-6 md:flex" aria-label="Navegação da página">
            {NAV_LINKS.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="text-sm font-medium text-slate-300 transition hover:text-emerald-400"
              >
                {link.label}
              </a>
            ))}
          </nav>
          <Link
            to="/dashboard"
            className="rounded-full bg-emerald-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-400"
          >
            Acessar Dashboard
          </Link>
        </div>
      </header>

      <Hero />
      <Problem />
      <Solution />
      <Features />
      <Metrics />
      <FinalCta />

      <footer className="border-t border-white/10 bg-slate-950 py-6 text-center text-xs text-slate-500">
        🌿 EcoCity Dashboard — Monitoramento Ambiental Inteligente · MIT License
      </footer>
    </div>
  );
}
