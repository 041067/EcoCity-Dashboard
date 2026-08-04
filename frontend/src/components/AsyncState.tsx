import type { ReactNode } from 'react';

interface AsyncStateProps {
  isLoading: boolean;
  isError: boolean;
  isEmpty?: boolean;
  error?: unknown;
  onRetry?: () => void;
  emptyMessage?: string;
  children: ReactNode;
}

export function AsyncState({
  isLoading,
  isError,
  isEmpty,
  error,
  onRetry,
  emptyMessage = 'Sem dados disponíveis',
  children,
}: AsyncStateProps) {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-16 text-gray-500 dark:text-gray-400" role="status">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-emerald-500 border-t-transparent" />
        <p>Carregando...</p>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-red-200 bg-red-50 py-12 text-center dark:border-red-800 dark:bg-red-950">
        <p className="text-red-700 dark:text-red-300">Não foi possível carregar os dados</p>
        <p className="max-w-md text-sm text-red-600 dark:text-red-400">
          {error instanceof Error ? error.message : 'Erro desconhecido'}
        </p>
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-700"
          >
            Tentar novamente
          </button>
        )}
      </div>
    );
  }

  if (isEmpty) {
    return (
      <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-gray-300 py-12 text-center text-gray-500 dark:border-gray-700 dark:text-gray-400">
        <span className="text-3xl">🌱</span>
        <p>{emptyMessage}</p>
      </div>
    );
  }

  return <>{children}</>;
}
