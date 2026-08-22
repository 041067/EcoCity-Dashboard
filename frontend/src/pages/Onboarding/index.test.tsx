import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { OnboardingPage } from './index';

vi.mock('../../hooks/useApiQueries', () => ({
  useCities: () => ({ data: [], isLoading: false }),
  useESGTopics: () => ({
    isLoading: false,
    data: [
      { id: 1, code: 'energy', name: 'Energy', pillar: 'E', active: true },
      { id: 2, code: 'community-relations', name: 'Community Relations', pillar: 'S', active: true },
      { id: 3, code: 'ethics', name: 'Ethics', pillar: 'G', active: true },
    ],
  }),
}));

describe('OnboardingPage', () => {
  it('apresenta os passos da configuração ESG', () => {
    render(
      <MemoryRouter>
        <OnboardingPage />
      </MemoryRouter>,
    );

    expect(screen.getByRole('heading', { name: 'Vamos configurar sua base ESG' })).toBeInTheDocument();
    expect(screen.getByText('1. Organização')).toBeInTheDocument();
    expect(screen.getByText('2. Unidades')).toBeInTheDocument();
    expect(screen.getByText('3. Temas ESG acompanhados')).toBeInTheDocument();
    expect(screen.getByText('4. Stakeholders')).toBeInTheDocument();
    expect(screen.getByLabelText('Energy')).toBeInTheDocument();
  });
});
