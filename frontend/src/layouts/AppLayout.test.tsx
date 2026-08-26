import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { AppLayout } from './AppLayout';

vi.mock('../contexts/useTheme', () => ({
  useTheme: () => ({ theme: 'light', toggleTheme: vi.fn() }),
}));

function renderLayout(path = '/dashboard') {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <AppLayout />
    </MemoryRouter>,
  );
}

describe('AppLayout navigation', () => {
  it('opens and closes the desktop mega menu with the keyboard', () => {
    renderLayout();
    const trigger = screen.getByRole('button', { name: 'Navegação' });

    fireEvent.click(trigger);
    expect(screen.getByRole('region', { name: 'Menu principal expandido' })).toBeInTheDocument();
    expect(screen.getByText('Gestão ESG')).toBeInTheDocument();
    expect(screen.getByText('EcoCity AI')).toBeInTheDocument();

    fireEvent.keyDown(document, { key: 'Escape' });
    expect(screen.queryByRole('region', { name: 'Menu principal expandido' })).not.toBeInTheDocument();
  });

  it('opens a focusable mobile drawer and restores scrolling on close', async () => {
    renderLayout('/esg/copilot');
    fireEvent.click(screen.getByRole('button', { name: 'Abrir menu de navegação' }));

    const drawer = screen.getByRole('dialog', { name: 'Navegação EcoCity' });
    expect(drawer).toBeInTheDocument();
    await waitFor(() => expect(document.body.style.overflow).toBe('hidden'));
    expect(screen.getByRole('link', { name: /Relatórios ESG/i })).toBeInTheDocument();

    const closeButton = screen.getByRole('button', { name: 'Fechar menu' });
    const focusable = drawer.querySelectorAll<HTMLElement>('a[href], button:not([disabled])');
    fireEvent.keyDown(document, { key: 'Tab', shiftKey: true });
    expect(document.activeElement).toBe(focusable[focusable.length - 1]);

    fireEvent.click(closeButton);
    await waitFor(() => expect(document.body.style.overflow).toBe(''));
  });
});
