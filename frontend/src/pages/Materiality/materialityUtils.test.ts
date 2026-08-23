import { describe, expect, it } from 'vitest';

import { formatScore, pointSize, priorityMeta } from './materialityUtils';

describe('materiality presentation helpers', () => {
  it('maps the priority engine labels and colors', () => {
    expect(priorityMeta('critical')?.label).toBe('Crítica');
    expect(priorityMeta('low')?.dotClassName).toContain('emerald');
  });

  it('keeps stakeholder bubbles within accessible dimensions', () => {
    expect(pointSize(0)).toBe(30);
    expect(pointSize(100)).toBe(56);
    expect(pointSize(60)).toBeGreaterThan(pointSize(40));
  });

  it('formats unavailable and decimal scores consistently', () => {
    expect(formatScore(null)).toBe('—');
    expect(formatScore(79.87)).toBe('80');
  });
});
