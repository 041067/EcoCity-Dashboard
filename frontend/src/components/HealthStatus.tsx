import { useEffect, useState } from 'react';
import { getHealth } from '../services/api';
import type { HealthResponse } from '../types';

export function HealthStatus() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setError('Não foi possível conectar ao backend'));
  }, []);

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        {error}
      </div>
    );
  }

  if (!health) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-gray-500">
        Verificando conexão...
      </div>
    );
  }

  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
      <p className="text-green-700 font-semibold">Backend Online</p>
      <p className="text-green-600 text-sm">
        Database: {health.database === 'connected' ? 'Conectado' : 'Desconectado'}
      </p>
    </div>
  );
}
