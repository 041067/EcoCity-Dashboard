import { HealthStatus } from '../components/HealthStatus';

export function Home() {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4">
          <h1 className="text-3xl font-bold text-gray-900">
            EcoCity Dashboard
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Monitoramento Ambiental Inteligente
          </p>
        </div>
      </header>
      <main className="max-w-7xl mx-auto py-6 px-4">
        <HealthStatus />
      </main>
    </div>
  );
}
