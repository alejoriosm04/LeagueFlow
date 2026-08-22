import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../auth/AuthContext';
import { MatchesPage } from '../../matches/MatchesPage';
import { StandingsPage } from '../../standings/StandingsPage';
import { exportsApi } from '../api';

vi.mock('../api', () => ({
  exportsApi: {
    descargarClasificacion: vi.fn(),
    descargarCalendario: vi.fn(),
  },
}));

function stubFetch() {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = new URL(String(input));
    const path = url.pathname.replace('/api/v1', '');
    if (path === '/auth/me') return Response.json({ user: null });
    if (path === '/leagues/l1/standings') return Response.json({ league_id: 'l1', items: [] });
    if (path === '/leagues/l1/teams') return Response.json({ items: [], page: 1, page_size: 20, total: 0 });
    if (path === '/leagues/l1/matches') return Response.json({ items: [], page: 1, page_size: 100, total: 0 });
    return Response.json({ error: { code: 'nf', message: 'No encontrado', field: null } }, { status: 404 });
  });
}

function renderPage(kind: 'standings' | 'matches') {
  render(
    <MemoryRouter initialEntries={[`/leagues/l1/${kind}`]}>
      <AuthProvider><Routes>
        <Route path="/leagues/:id/standings" element={<StandingsPage />} />
        <Route path="/leagues/:id/matches" element={<MatchesPage />} />
      </Routes></AuthProvider>
    </MemoryRouter>,
  );
}

beforeEach(() => {
  vi.restoreAllMocks();
  vi.stubGlobal('fetch', stubFetch());
});

describe('descargas CSV públicas', () => {
  it('descarga clasificación sin sesión con una interacción en la vista', async () => {
    renderPage('standings');
    await userEvent.click(await screen.findByRole('button', { name: 'Descargar CSV' }));
    expect(exportsApi.descargarClasificacion).toHaveBeenCalledWith('l1');
  });

  it('descarga calendario sin sesión con una interacción en la vista', async () => {
    renderPage('matches');
    await userEvent.click(await screen.findByRole('button', { name: 'Descargar CSV' }));
    expect(exportsApi.descargarCalendario).toHaveBeenCalledWith('l1');
  });

  it('presenta errores de descarga en una región accesible', async () => {
    vi.mocked(exportsApi.descargarClasificacion).mockRejectedValueOnce(new Error('falló'));
    renderPage('standings');
    await userEvent.click(await screen.findByRole('button', { name: 'Descargar CSV' }));
    expect(await screen.findByRole('status')).not.toBeEmptyDOMElement();
  });
});
