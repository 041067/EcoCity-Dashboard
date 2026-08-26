import { Suspense, lazy } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './contexts/ThemeProvider';
import { AppLayout } from './layouts/AppLayout';
import { LoadingScreen } from './components/LoadingScreen';

const Landing = lazy(() => import('./pages/Landing').then((m) => ({ default: m.Landing })));
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
const OnboardingPage = lazy(() =>
  import('./pages/Onboarding').then((m) => ({ default: m.OnboardingPage })),
);
const ESGPage = lazy(() => import('./pages/ESG').then((m) => ({ default: m.ESGPage })));
const MaterialityPage = lazy(() =>
  import('./pages/Materiality').then((m) => ({ default: m.MaterialityPage })),
);
const IntelligencePage = lazy(() =>
  import('./pages/Intelligence').then((m) => ({ default: m.IntelligencePage })),
);
const ActionsPage = lazy(() => import('./pages/Actions').then((m) => ({ default: m.ActionsPage })));
const CopilotPage = lazy(() => import('./pages/Copilot').then((m) => ({ default: m.CopilotPage })));
const RecommendationsPage = lazy(() =>
  import('./pages/Recommendations').then((m) => ({ default: m.RecommendationsPage })),
);
const ESGReportsPage = lazy(() =>
  import('./pages/ESGReports').then((m) => ({ default: m.ESGReportsPage })),
);

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
        <Route path="/" element={<Landing />} />
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/mapa" element={<MapPage />} />
          <Route path="/relatorios" element={<ReportsPage />} />
          <Route path="/alertas" element={<AlertsPage />} />
          <Route path="/comparar" element={<ComparePage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/esg" element={<ESGPage />} />
          <Route path="/esg/intelligence" element={<IntelligencePage />} />
          <Route path="/esg/materiality" element={<MaterialityPage />} />
          <Route path="/esg/actions" element={<ActionsPage />} />
          <Route path="/esg/copilot" element={<CopilotPage />} />
          <Route path="/esg/recommendations" element={<RecommendationsPage />} />
          <Route path="/esg/reports" element={<ESGReportsPage />} />
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
