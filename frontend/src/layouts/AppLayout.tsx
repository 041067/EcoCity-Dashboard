import { useEffect, useRef, useState } from 'react';
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom';
import { AppIcon, type IconName } from '../components/icons/AppIcon';
import { useTheme } from '../contexts/useTheme';

interface NavItem {
  to: string;
  label: string;
  description: string;
  icon: IconName;
}

interface NavGroup {
  id: string;
  title: string;
  description: string;
  items: readonly NavItem[];
}

const NAV_GROUPS = [
  {
    id: 'esg',
    title: 'Gestão ESG',
    description: 'Estratégia, materialidade e execução.',
    items: [
      { to: '/esg', label: 'Visão ESG', description: 'Organização e temas', icon: 'leaf' },
      { to: '/esg/intelligence', label: 'Inteligência', description: 'Evidências e indicadores', icon: 'activity' },
      { to: '/esg/materiality', label: 'Materialidade', description: 'Temas prioritários', icon: 'target' },
      { to: '/esg/actions', label: 'Ações ESG', description: 'Gaps, riscos e metas', icon: 'check' },
    ],
  },
  {
    id: 'copilot',
    title: 'EcoCity AI',
    description: 'Análises fundamentadas e rastreáveis.',
    items: [
      { to: '/esg/copilot', label: 'ESG AI Copilot', description: 'Perguntas estratégicas', icon: 'bot' },
      { to: '/esg/recommendations', label: 'Recomendações', description: 'Aprovação humana', icon: 'rocket' },
      { to: '/esg/reports', label: 'Relatórios ESG', description: 'Histórico executivo', icon: 'document' },
    ],
  },
  {
    id: 'monitoring',
    title: 'Monitoramento',
    description: 'Dados ambientais urbanos em tempo real.',
    items: [
      { to: '/dashboard', label: 'Dashboard', description: 'Visão operacional', icon: 'chart' },
      { to: '/mapa', label: 'Mapa', description: 'Cidades monitoradas', icon: 'map' },
      { to: '/alertas', label: 'Alertas', description: 'Ocorrências ambientais', icon: 'bell' },
      { to: '/comparar', label: 'Comparar', description: 'Indicadores por cidade', icon: 'scale' },
    ],
  },
  {
    id: 'assistant',
    title: 'Assistente ambiental',
    description: 'Recursos da plataforma legada.',
    items: [
      { to: '/relatorios', label: 'Relatórios IA', description: 'Resumo por cidade', icon: 'document' },
      { to: '/chat', label: 'Chat ambiental', description: 'Perguntas sobre cidades', icon: 'chat' },
    ],
  },
] as const satisfies readonly NavGroup[];

const MOBILE_SHORTCUTS = [
  { to: '/dashboard', label: 'Início', description: 'Dashboard', icon: 'chart' },
  { to: '/esg/copilot', label: 'Copilot', description: 'Análise ESG', icon: 'bot' },
  { to: '/esg/actions', label: 'Ações', description: 'Prioridades', icon: 'check' },
] as const satisfies readonly NavItem[];

function isCurrentPath(pathname: string, to: string) {
  return to === '/esg' ? pathname === to : pathname === to || pathname.startsWith(`${to}/`);
}

function MegaLink({ item, onNavigate }: { item: NavItem; onNavigate: () => void }) {
  return (
    <NavLink
      to={item.to}
      end={item.to === '/esg' || item.to === '/dashboard'}
      onClick={onNavigate}
      className={({ isActive }) => `group flex min-h-16 gap-3 rounded-xl p-3 transition focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900 ${isActive ? 'bg-emerald-100 text-emerald-900 dark:bg-emerald-900/50 dark:text-emerald-100' : 'text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800'}`}
    >
      <span className="mt-0.5 rounded-lg bg-emerald-100 p-2 text-emerald-700 transition group-hover:bg-emerald-200 dark:bg-emerald-950 dark:text-emerald-300 dark:group-hover:bg-emerald-900"><AppIcon name={item.icon} className="h-4 w-4" /></span>
      <span className="min-w-0"><span className="block text-sm font-bold">{item.label}</span><span className="mt-0.5 block truncate text-xs text-gray-500 dark:text-gray-400">{item.description}</span></span>
    </NavLink>
  );
}

function MobileLink({ item, onNavigate }: { item: NavItem; onNavigate: () => void }) {
  return (
    <NavLink
      to={item.to}
      end={item.to === '/esg' || item.to === '/dashboard'}
      onClick={onNavigate}
      className={({ isActive }) => `flex min-h-12 items-center gap-3 rounded-xl px-3 py-2 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-emerald-500 ${isActive ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-100' : 'text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800'}`}
    >
      <AppIcon name={item.icon} className="h-5 w-5 text-emerald-600 dark:text-emerald-300" />
      <span className="min-w-0"><span className="block">{item.label}</span><span className="block truncate text-xs font-normal text-gray-500 dark:text-gray-400">{item.description}</span></span>
    </NavLink>
  );
}

export function AppLayout() {
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const [desktopOpen, setDesktopOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const desktopMenuRef = useRef<HTMLDivElement>(null);
  const desktopTriggerRef = useRef<HTMLButtonElement>(null);
  const mobileDrawerRef = useRef<HTMLElement>(null);
  const mobileCloseRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!desktopOpen) return undefined;
    const closeOnOutsidePointer = (event: PointerEvent) => {
      if (!desktopMenuRef.current?.contains(event.target as Node)) setDesktopOpen(false);
    };
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setDesktopOpen(false);
        desktopTriggerRef.current?.focus();
      }
    };
    document.addEventListener('pointerdown', closeOnOutsidePointer);
    document.addEventListener('keydown', closeOnEscape);
    return () => {
      document.removeEventListener('pointerdown', closeOnOutsidePointer);
      document.removeEventListener('keydown', closeOnEscape);
    };
  }, [desktopOpen]);

  useEffect(() => {
    if (!mobileOpen) return undefined;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    mobileCloseRef.current?.focus();
    const manageFocus = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setMobileOpen(false);
        return;
      }
      if (event.key !== 'Tab' || !mobileDrawerRef.current) return;
      const focusable = Array.from(mobileDrawerRef.current.querySelectorAll<HTMLElement>('a[href], button:not([disabled])'));
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };
    document.addEventListener('keydown', manageFocus);
    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener('keydown', manageFocus);
    };
  }, [mobileOpen]);

  const activeGroup = NAV_GROUPS.find((group) => group.items.some((item) => isCurrentPath(location.pathname, item.to)));

  return (
    <div className="min-h-screen overflow-x-clip bg-gray-100 dark:bg-gray-950">
      <header className="sticky top-0 z-40 border-b border-gray-200 bg-white/95 backdrop-blur dark:border-gray-800 dark:bg-gray-900/95">
        <div className="mx-auto flex min-h-16 max-w-7xl items-center justify-between gap-3 px-4 sm:px-6">
          <Link to="/" className="flex shrink-0 items-center gap-2 text-lg font-bold text-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 dark:text-emerald-400 dark:focus:ring-offset-gray-900" aria-label="EcoCity, página inicial">
            <span className="rounded-lg bg-emerald-100 p-1.5 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"><AppIcon name="leaf" className="h-5 w-5" /></span>
            <span>EcoCity</span>
          </Link>

          <div className="hidden items-center gap-2 lg:flex" ref={desktopMenuRef}>
            <NavLink to="/dashboard" end className={({ isActive }) => `min-h-10 rounded-lg px-3 py-2 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-emerald-500 ${isActive ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-100' : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'}`}>Dashboard</NavLink>
            <NavLink to="/esg/copilot" className={({ isActive }) => `min-h-10 rounded-lg px-3 py-2 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-emerald-500 ${isActive ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-100' : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'}`}>Copilot ESG</NavLink>
            <button ref={desktopTriggerRef} type="button" onClick={() => setDesktopOpen((open) => !open)} aria-expanded={desktopOpen} aria-controls="ecocity-mega-menu" className={`inline-flex min-h-10 items-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-emerald-500 ${desktopOpen || activeGroup ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-100' : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'}`}>
              Navegação <span aria-hidden="true" className={`text-xs transition ${desktopOpen ? 'rotate-180' : ''}`}>⌄</span>
            </button>
          </div>

          <div className="flex items-center gap-1.5">
            <button type="button" onClick={toggleTheme} aria-label={theme === 'light' ? 'Ativar modo escuro' : 'Ativar modo claro'} className="inline-flex min-h-11 min-w-11 items-center justify-center rounded-lg border border-gray-200 p-2 transition hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-500 dark:border-gray-700 dark:hover:bg-gray-800"><AppIcon name={theme === 'light' ? 'moon' : 'sun'} className="h-5 w-5" /></button>
            <button type="button" onClick={() => setMobileOpen(true)} aria-label="Abrir menu de navegação" aria-expanded={mobileOpen} className="inline-flex min-h-11 min-w-11 items-center justify-center rounded-lg border border-gray-200 p-2 transition hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-500 lg:hidden dark:border-gray-700 dark:hover:bg-gray-800"><AppIcon name="menu" className="h-5 w-5" /></button>
          </div>
        </div>

        {desktopOpen && <div id="ecocity-mega-menu" className="absolute left-0 right-0 top-full hidden border-b border-gray-200 bg-white shadow-xl lg:block dark:border-gray-800 dark:bg-gray-900" role="region" aria-label="Menu principal expandido"><div className="mx-auto grid max-w-7xl gap-3 px-6 py-5 xl:grid-cols-4">{NAV_GROUPS.map((group) => <section key={group.id} className="rounded-2xl border border-gray-100 p-3 dark:border-gray-800"><h2 className="px-1 text-sm font-bold text-gray-900 dark:text-white">{group.title}</h2><p className="px-1 pt-0.5 text-xs text-gray-500 dark:text-gray-400">{group.description}</p><div className="mt-3 space-y-1">{group.items.map((item) => <MegaLink key={item.to} item={item} onNavigate={() => setDesktopOpen(false)} />)}</div></section>)}</div></div>}
      </header>

      {mobileOpen && <div className="fixed inset-0 z-50 lg:hidden"><button type="button" aria-label="Fechar menu de navegação" className="absolute inset-0 cursor-default bg-gray-950/45 backdrop-blur-[1px]" onClick={() => setMobileOpen(false)} /><aside ref={mobileDrawerRef} role="dialog" aria-modal="true" aria-label="Navegação EcoCity" className="absolute inset-y-0 right-0 flex w-full max-w-sm flex-col bg-white shadow-2xl dark:bg-gray-900"><div className="flex min-h-16 items-center justify-between border-b border-gray-200 px-4 dark:border-gray-800"><span className="flex items-center gap-2 font-bold text-emerald-600 dark:text-emerald-300"><AppIcon name="leaf" className="h-5 w-5" />EcoCity</span><button ref={mobileCloseRef} type="button" aria-label="Fechar menu" onClick={() => setMobileOpen(false)} className="inline-flex min-h-11 min-w-11 items-center justify-center rounded-lg border border-gray-200 text-gray-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 dark:border-gray-700 dark:text-gray-200"><AppIcon name="close" className="h-5 w-5" /></button></div><nav className="min-h-0 flex-1 overflow-y-auto p-4" aria-label="Navegação móvel"><p className="px-2 text-xs font-bold uppercase tracking-widest text-gray-500">Acesso rápido</p><div className="mt-2 grid grid-cols-3 gap-2">{MOBILE_SHORTCUTS.map((item) => <NavLink key={item.to} to={item.to} end={item.to === '/dashboard'} onClick={() => setMobileOpen(false)} className={({ isActive }) => `flex min-h-20 flex-col items-center justify-center gap-1 rounded-xl p-2 text-center text-xs font-bold focus:outline-none focus:ring-2 focus:ring-emerald-500 ${isActive ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-100' : 'bg-gray-50 text-gray-700 dark:bg-gray-800 dark:text-gray-200'}`}><AppIcon name={item.icon} className="h-5 w-5 text-emerald-600 dark:text-emerald-300" />{item.label}</NavLink>)}</div>{NAV_GROUPS.map((group) => <section key={group.id} className="mt-6"><h2 className="px-2 text-xs font-bold uppercase tracking-widest text-gray-500">{group.title}</h2><div className="mt-2 space-y-1">{group.items.map((item) => <MobileLink key={item.to} item={item} onNavigate={() => setMobileOpen(false)} />)}</div></section>)}</nav><div className="border-t border-gray-200 p-4 text-xs text-gray-500 dark:border-gray-800 dark:text-gray-400">Navegação responsiva preparada para experiências mobile.</div></aside></div>}

      <main className="mx-auto max-w-7xl px-4 py-5 sm:px-6 sm:py-6"><Outlet /></main>
      <footer className="border-t border-gray-200 px-4 py-4 text-center text-xs text-gray-400 dark:border-gray-800">EcoCity Dashboard — Monitoramento Ambiental Inteligente</footer>
    </div>
  );
}
