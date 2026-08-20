import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../auth/AuthContext';
import { LeagueDetailPage } from '../../leagues/LeagueDetailPage';
import { MatchesPage } from '../MatchesPage';

const teams = [
  { id: 't1', name: 'Tigres' },
  { id: 't2', name: 'Halcones' },
];
const base = {
  league_id: 'l1', home_team_id: 't1', away_team_id: 't2', created_by: 'u1',
  created_at: '2026-08-20T00:00:00Z', updated_at: '2026-08-20T00:00:00Z',
};
const scheduled = [
  { ...base, id: 's1', scheduled_at: '2026-09-01T18:00:00Z', status: 'scheduled', home_score: null, away_score: null },
  { ...base, id: 's2', scheduled_at: '2026-09-02T18:00:00Z', status: 'scheduled', home_score: null, away_score: null },
];
const finished = [
  { ...base, id: 'f2', scheduled_at: '2026-08-02T18:00:00Z', status: 'finished', home_score: 3, away_score: 1 },
  { ...base, id: 'f1', scheduled_at: '2026-08-01T18:00:00Z', status: 'finished', home_score: 0, away_score: 0 },
];

function fetchCalendario(vacio = false) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = new URL(String(input));
    const path = url.pathname.replace('/api/v1', '');
    if (path === '/auth/me') return Response.json({ user: null });
    if (path === '/leagues/l1/teams') return Response.json({ items: vacio ? [] : teams, page: 1, page_size: 20, total: vacio ? 0 : 2 });
    if (path === '/leagues/l1/matches') {
      const status = url.searchParams.get('status');
      const items = vacio ? [] : status === 'finished' ? finished : status === 'cancelled' || status === 'in_progress' ? [] : scheduled;
      return Response.json({ items, page: 1, page_size: 100, total: items.length });
    }
    return Response.json({ error: { code: 'nf', message: 'No encontrado', field: null } }, { status: 404 });
  });
}

function renderPage() {
  render(
    <MemoryRouter initialEntries={['/leagues/l1/matches']}>
      <AuthProvider><Routes><Route path="/leagues/:id/matches" element={<MatchesPage />} /></Routes></AuthProvider>
    </MemoryRouter>,
  );
}

beforeEach(() => vi.restoreAllMocks());

describe('calendario público', () => {
  it('agrupa próximos y jugados con nombres, orden y marcador sin sesión', async () => {
    vi.stubGlobal('fetch', fetchCalendario());
    renderPage();
    expect(await screen.findByRole('heading', { name: 'Próximos partidos' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Partidos jugados' })).toBeInTheDocument();
    expect(screen.getAllByText(/Tigres vs Halcones/)).toHaveLength(4);
    expect(screen.getByText(/3–1/)).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /programar partido/i })).not.toBeInTheDocument();
  });

  it('filtra por estado mediante un selector accesible', async () => {
    const fetchMock = fetchCalendario();
    vi.stubGlobal('fetch', fetchMock);
    renderPage();
    const filtro = await screen.findByRole('combobox', { name: 'Filtrar por estado' });
    await userEvent.selectOptions(filtro, 'finished');
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('status=finished'), expect.anything()));
    expect(screen.queryByRole('heading', { name: 'Próximos partidos' })).not.toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Partidos jugados' })).toBeInTheDocument();
  });

  it('muestra un estado vacío en una liga sin equipos ni partidos', async () => {
    vi.stubGlobal('fetch', fetchCalendario(true));
    renderPage();
    expect(await screen.findByText('Aún no hay partidos en esta liga.')).toBeInTheDocument();
  });

  it('llega desde la liga al próximo partido en una interacción', async () => {
    const fetchMock = fetchCalendario();
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const path = new URL(String(input)).pathname.replace('/api/v1', '');
      if (path === '/leagues/l1') {
        return Response.json({ id: 'l1', name: 'Liga pública', season: '2026', description: null });
      }
      return fetchMock(input);
    }));
    render(
      <MemoryRouter initialEntries={['/leagues/l1']}>
        <AuthProvider><Routes>
          <Route path="/leagues/:id" element={<LeagueDetailPage />} />
          <Route path="/leagues/:id/matches" element={<MatchesPage />} />
        </Routes></AuthProvider>
      </MemoryRouter>,
    );
    await userEvent.click(await screen.findByRole('link', { name: 'Ver partidos' }));
    expect(await screen.findByRole('heading', { name: 'Próximos partidos' })).toBeInTheDocument();
    expect(screen.getAllByRole('link', { name: 'Tigres vs Halcones' })[0]).toBeInTheDocument();
  });

  it('recorre dos páginas y muestra los 190 partidos', async () => {
    const partidos = Array.from({ length: 190 }, (_, index) => ({
      ...base,
      id: `p${index}`,
      scheduled_at: new Date(Date.UTC(2027, 0, 1, 0, index)).toISOString(),
      status: 'scheduled',
      home_score: null,
      away_score: null,
    }));
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      const path = url.pathname.replace('/api/v1', '');
      if (path === '/auth/me') return Response.json({ user: null });
      if (path === '/leagues/l1/teams') return Response.json({ items: teams, page: 1, page_size: 20, total: 2 });
      if (path === '/leagues/l1/matches') {
        const status = url.searchParams.get('status');
        if (status === 'finished') return Response.json({ items: [], page: 1, page_size: 100, total: 0 });
        const page = Number(url.searchParams.get('page'));
        return Response.json({ items: page === 1 ? partidos.slice(0, 100) : partidos.slice(100), page, page_size: 100, total: 190 });
      }
      return Response.json({}, { status: 404 });
    }));
    renderPage();
    expect(await screen.findByRole('heading', { name: 'Próximos partidos' })).toBeInTheDocument();
    expect(screen.getAllByRole('link', { name: 'Tigres vs Halcones' })).toHaveLength(190);
  });
});
