import { Suspense, lazy } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './contexts/ThemeProvider';
import { AppLayout } from './layouts/AppLayout';
import { LoadingScreen } from './components/LoadingScreen';

const Dashboard = lazy(() =>
  import('./pages/Dashboard').then((m) => ({ default: m.Dashboard })),
);
const MapPage = lazy(() => import('./pages/Map').then((m) => ({ default: m.MapPage })));
const ReportsPage = lazy(() =>
  import('./pages/Reports').then((m) => ({ default: m.ReportsPage })),
);
const AlertsPage = lazy(() =>
  import('./pages/Alerts').then((m) => ({ default: m.AlertsPage })),
);
const ComparePage = lazy(() =>
  import('./pages/Compare').then((m) => ({ default: m.ComparePage })),
);
const ChatPage = lazy(() => import('./pages/Chat').then((m) => ({ default: m.ChatPage })));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export function AppRoutes() {
  return (
    <Suspense fallback={<LoadingScreen />}>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/mapa" element={<MapPage />} />
          <Route path="/relatorios" element={<ReportsPage />} />
          <Route path="/alertas" element={<AlertsPage />} />
          <Route path="/comparar" element={<ComparePage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </Suspense>
  );
}

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
