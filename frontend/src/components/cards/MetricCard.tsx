import type { ReactNode } from 'react';

interface MetricCardProps {
  label: string;
  value: string;
  unit?: string;
  icon?: ReactNode;
  tone?: 'emerald' | 'amber' | 'red' | 'sky' | 'violet' | 'default';
}

const TONES: Record<NonNullable<MetricCardProps['tone']>, string> = {
  emerald: 'border-emerald-200 bg-emerald-50 dark:border-emerald-900 dark:bg-emerald-950',
  amber: 'border-amber-200 bg-amber-50 dark:border-amber-900 dark:bg-amber-950',
  red: 'border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950',
  sky: 'border-sky-200 bg-sky-50 dark:border-sky-900 dark:bg-sky-950',
  violet: 'border-violet-200 bg-violet-50 dark:border-violet-900 dark:bg-violet-950',
  default: 'border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900',
};

export function MetricCard({ label, value, unit, icon, tone = 'default' }: MetricCardProps) {
  return (
    <div className={`rounded-xl border p-4 shadow-sm transition hover:shadow-md ${TONES[tone]}`}>
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{label}</p>
        {icon && <span className="text-xl">{icon}</span>}
      </div>
      <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
        {value}
        {unit && <span className="ml-1 text-base font-normal text-gray-500 dark:text-gray-400">{unit}</span>}
      </p>
    </div>
  );
}
