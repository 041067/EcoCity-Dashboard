import { NavLink, Outlet } from 'react-router-dom';
import { useTheme } from '../contexts/useTheme';

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: '📊' },
  { to: '/mapa', label: 'Mapa', icon: '🗺️' },
  { to: '/relatorios', label: 'Relatórios IA', icon: '🤖' },
  { to: '/alertas', label: 'Alertas', icon: '🔔' },
  { to: '/comparar', label: 'Comparar', icon: '⚖️' },
  { to: '/chat', label: 'Chat IA', icon: '💬' },
];

export function AppLayout() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-950">
      <header className="sticky top-0 z-40 border-b border-gray-200 bg-white/90 backdrop-blur dark:border-gray-800 dark:bg-gray-900/90">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <NavLink to="/" className="flex items-center gap-2 text-xl font-bold text-emerald-600 dark:text-emerald-400">
            <span>🌿</span>
            <span>EcoCity</span>
          </NavLink>

          <nav className="hidden gap-1 md:flex" aria-label="Navegação principal">
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `rounded-lg px-3 py-2 text-sm font-medium transition ${
                    isActive
                      ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300'
                      : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
                  }`
                }
              >
                <span className="mr-1">{item.icon}</span>
                {item.label}
              </NavLink>
            ))}
          </nav>

          <button
            type="button"
            onClick={toggleTheme}
            aria-label={theme === 'light' ? 'Ativar modo escuro' : 'Ativar modo claro'}
            className="rounded-lg border border-gray-200 p-2 text-lg transition hover:bg-gray-100 dark:border-gray-700 dark:hover:bg-gray-800"
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
        </div>

        <nav className="flex gap-1 overflow-x-auto border-t border-gray-200 px-2 py-2 md:hidden dark:border-gray-800" aria-label="Navegação móvel">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `whitespace-nowrap rounded-lg px-3 py-1.5 text-sm font-medium ${
                  isActive
                    ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300'
                    : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
                }`
              }
            >
              <span className="mr-1">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-6">
        <Outlet />
      </main>

      <footer className="border-t border-gray-200 py-4 text-center text-xs text-gray-400 dark:border-gray-800">
        EcoCity Dashboard — Monitoramento Ambiental Inteligente
      </footer>
    </div>
  );
}
