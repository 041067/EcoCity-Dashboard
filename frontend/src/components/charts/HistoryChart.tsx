import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { Reading } from '../../types';

interface HistoryChartProps {
  title: string;
  readings: Reading[];
  dataKey: keyof Reading;
  color: string;
  unit?: string;
  formatter?: (v: number) => string;
}

function formatTime(value?: string): string {
  if (!value) return '';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return '';
  return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

export function HistoryChart({ title, readings, dataKey, color, unit, formatter }: HistoryChartProps) {
  const data = [...readings]
    .reverse()
    .map((r) => ({ ...r, _time: formatTime(r.created_at), _value: Number(r[dataKey]) || 0 }));

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-800 dark:bg-gray-900">
      <h3 className="mb-3 text-sm font-semibold text-gray-700 dark:text-gray-300">{title}</h3>
      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 10, bottom: 5, left: -15 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} />
            <XAxis dataKey="_time" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip
              formatter={(value) =>
                formatter ? formatter(Number(value)) : [`${Number(value).toFixed(1)}${unit ? ` ${unit}` : ''}`, title]
              }
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="_value"
              name={title}
              stroke={color}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
