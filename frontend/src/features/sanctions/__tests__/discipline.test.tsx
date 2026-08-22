import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MatchDetailPage } from '../../matches/MatchDetailPage';
import { AuthProvider } from '../../auth/AuthContext';
import { DisciplinePage } from '../DisciplinePage';

const partido = {
  id: 'm1', league_id: 'l1', home_team_id: 'th', away_team_id: 'ta',
  scheduled_at: '2026-08-01T18:00:00Z', status: 'finished', home_score: 1, away_score: 0,
  created_by: 'u1', created_at: '2026-08-01T00:00:00Z', updated_at: '2026-08-01T00:00:00Z',
};

function stubFetchPartido({ rol = null as string | null, cardError = false } = {}) {
  const registrados: unknown[] = [];
  const fn = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const path = new URL(String(input)).pathname.replace('/api/v1', '');
    if (path === '/auth/me') {
      return Response.json({ user: rol ? { id: 'u1', username: 'x', role: rol } : null });
    }
    if (path === '/matches/m1') return Response.json(partido);
    if (path === '/matches/m1/result-corrections') {
      return Response.json({ items: [], page: 1, page_size: 20, total: 0 });
    }
    if (path === '/teams/th/players') {
      return Response.json({
        items: [{ id: 'p1', team_id: 'th', name: 'Ana Gómez', number: 9, position: null, status: 'active' }],
        page: 1, page_size: 20, total: 1,
      });
    }
    if (path === '/teams/ta/players') {
      return Response.json({
        items: [{ id: 'p2', team_id: 'ta', name: 'Luis Paz', number: 7, position: null, status: 'active' }],
        page: 1, page_size: 20, total: 1,
      });
    }
    if (path === '/matches/m1/lineup') {
      return Response.json({ match_id: 'm1', status: 'missing', home_players: [], away_players: [] });
    }
    if (path === '/matches/m1/events') {
      if (init?.method === 'POST') {
        if (cardError) {
          return Response.json(
            { error: { code: 'match_not_playable', message: 'x', field: null } },
            { status: 409 },
          );
        }
        registrados.push(JSON.parse(String(init.body)));
        return Response.json(
          {
            id: 'c1', match_id: 'm1', type: 'YELLOW_CARD', player_id: 'p1', team_id: 'th', minute: 20,
            created_by: 'u1', created_at: '2026-08-02T00:00:00Z',
          },
          { status: 201 },
        );
      }
      return Response.json({
        items: [],
        consistency: {
          home_goals_recorded: 0, away_goals_recorded: 0, home_score: 1, away_score: 0,
          matches_official: false,
        },
      });
    }
    return Response.json({ error: { code: 'nf', message: 'No', field: null } }, { status: 404 });
  });
  return { fn, registrados };
}

function renderFicha() {
  render(
    <MemoryRouter initialEntries={['/matches/m1']}>
      <AuthProvider>
        <Routes><Route path="/matches/:matchId" element={<MatchDetailPage />} /></Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

beforeEach(() => vi.restoreAllMocks());

describe('tarjetas del partido', () => {
  it('muestra el formulario de tarjeta solo al operador en partido jugable', async () => {
    vi.stubGlobal('fetch', stubFetchPartido({ rol: 'operador' }).fn);
    renderFicha();
    await screen.findByRole('region', { name: /tarjetas/i });
    expect(screen.getByRole('button', { name: /registrar tarjeta/i })).toBeInTheDocument();
  });

  it('no muestra el formulario de tarjeta sin sesión', async () => {
    vi.stubGlobal('fetch', stubFetchPartido().fn);
    renderFicha();
    await screen.findByRole('region', { name: /tarjetas/i });
    expect(screen.queryByRole('button', { name: /registrar tarjeta/i })).not.toBeInTheDocument();
  });

  it('envía una tarjeta amarilla y refresca', async () => {
    const stub = stubFetchPartido({ rol: 'operador' });
    vi.stubGlobal('fetch', stub.fn);
    renderFicha();
    const seccion = await screen.findByRole('region', { name: /tarjetas/i });
    await userEvent.selectOptions(within(seccion).getByLabelText(/tipo de tarjeta/i), 'YELLOW_CARD');
    await userEvent.selectOptions(within(seccion).getByLabelText(/jugador/i), 'p1');
    await userEvent.clear(within(seccion).getByLabelText(/minuto/i));
    await userEvent.type(within(seccion).getByLabelText(/minuto/i), '20');
    await userEvent.click(within(seccion).getByRole('button', { name: /registrar tarjeta/i }));
    await waitFor(() =>
      expect(stub.registrados).toEqual([{ player_id: 'p1', minute: 20, type: 'YELLOW_CARD' }]),
    );
  });
});

describe('ficha disciplinaria', () => {
  function stubDisciplina(suspended = false) {
    return vi.fn(async (input: RequestInfo | URL) => {
      const path = new URL(String(input)).pathname.replace('/api/v1', '');
      if (path === '/players/p1/discipline') {
        return Response.json({
          player_id: 'p1', yellow_cards: suspended ? 2 : 0, red_cards: suspended ? 0 : 0, suspended,
        });
      }
      return Response.json({ error: { code: 'nf', message: 'No', field: null } }, { status: 404 });
    });
  }

  it('muestra conteos sin sesión', async () => {
    vi.stubGlobal('fetch', stubDisciplina());
    render(
      <MemoryRouter initialEntries={['/players/p1/discipline']}>
        <Routes><Route path="/players/:playerId/discipline" element={<DisciplinePage />} /></Routes>
      </MemoryRouter>,
    );
    expect(await screen.findByText('Al día')).toBeInTheDocument();
    expect(screen.getAllByText('0').length).toBeGreaterThanOrEqual(2);
  });

  it('muestra suspendido cuando aplica', async () => {
    vi.stubGlobal('fetch', stubDisciplina(true));
    render(
      <MemoryRouter initialEntries={['/players/p1/discipline']}>
        <Routes><Route path="/players/:playerId/discipline" element={<DisciplinePage />} /></Routes>
      </MemoryRouter>,
    );
    expect(await screen.findByText('Suspendido')).toBeInTheDocument();
  });
});
