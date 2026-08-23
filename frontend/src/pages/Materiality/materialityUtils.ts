import type { PriorityLevel } from '../../types';

const PRIORITIES: Record<PriorityLevel, { label: string; className: string; dotClassName: string }> = {
  low: {
    label: 'Baixa',
    className: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200',
    dotClassName: 'bg-emerald-500',
  },
  medium: {
    label: 'Média',
    className: 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-200',
    dotClassName: 'bg-amber-500',
  },
  high: {
    label: 'Alta',
    className: 'bg-orange-100 text-orange-800 dark:bg-orange-950 dark:text-orange-200',
    dotClassName: 'bg-orange-500',
  },
  critical: {
    label: 'Crítica',
    className: 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-200',
    dotClassName: 'bg-red-500',
  },
};

export function priorityMeta(priority: PriorityLevel | null) {
  return priority ? PRIORITIES[priority] : null;
}

export function pointSize(stakeholderScore: number): number {
  return Math.round(Math.min(56, Math.max(30, 24 + stakeholderScore * 0.32)));
}

export function formatScore(score: number | null): string {
  return score === null ? '—' : new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 }).format(score);
}
