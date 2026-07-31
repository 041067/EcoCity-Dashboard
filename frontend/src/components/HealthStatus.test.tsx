import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { HealthStatus } from './HealthStatus';
import { getHealth } from '../services/api';

vi.mock('../services/api', () => ({
  getHealth: vi.fn(),
}));

const mockedGetHealth = vi.mocked(getHealth);

describe('HealthStatus', () => {
  beforeEach(() => {
    mockedGetHealth.mockReset();
  });

  it('mostra estado de carregamento enquanto busca', () => {
    mockedGetHealth.mockReturnValue(new Promise(() => {}));
    render(<HealthStatus />);
    expect(screen.getByText('Verificando conexão...')).toBeInTheDocument();
  });

  it('mostra backend online quando a API responde', async () => {
    mockedGetHealth.mockResolvedValue({
      status: 'online',
      database: 'connected',
    });
    render(<HealthStatus />);
    await waitFor(() => {
      expect(screen.getByText('Backend Online')).toBeInTheDocument();
    });
    expect(screen.getByText('Database: Conectado')).toBeInTheDocument();
  });

  it('mostra erro quando a API falha', async () => {
    mockedGetHealth.mockRejectedValue(new Error('network'));
    render(<HealthStatus />);
    await waitFor(() => {
      expect(
        screen.getByText('Não foi possível conectar ao backend'),
      ).toBeInTheDocument();
    });
  });
});
