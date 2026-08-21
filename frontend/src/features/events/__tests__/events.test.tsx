import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../auth/AuthContext';
import { MatchDetailPage } from '../../matches/MatchDetailPage';

const partido = {
  id: 'm1', league_id: 'l1', home_team_id: 'th', away_team_id: 'ta',
  scheduled_at: '2026-08-01T18:00:00Z', status: 'finished', home_score: 3, away_score: 1,
  created_by: 'u1', created_at: '2026-08-01T00:00:00Z', updated_at: '2026-08-01T00:00:00Z',
};
const evento = (id: string, minute: number, player_id: string) => ({
  id, match_id: 'm1', type: 'GOAL', player_id, team_id: 'th', minute,
  created_by: 'u1', created_at: '2026-08-02T00:00:00Z',
});
const jugadores = {
  th: [{ id: 'p1', team_id: 'th', name: 'Ana Gómez', number: 9, position: null, status: 'active' }],
  ta: [{ id: 'p2', team_id: 'ta', name: 'Luis Paz', number: 7, position: null, status: 'active' }],
};

function stubFetch({ rol = null as string | null, cuadra = false, error = false } = {}) {
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
    if (path === '/teams/th/players') return Response.json({ items: jugadores.th, page: 1, page_size: 20, total: 1 });
    if (path === '/teams/ta/players') return Response.json({ items: jugadores.ta, page: 1, page_size: 20, total: 1 });
    if (path === '/matches/m1/lineup') {
      return Response.json({ match_id: 'm1', status: 'missing', home_players: [], away_players: [] });
    }
    if (path === '/matches/m1/events') {
      if (init?.method === 'POST') {
        if (error) {
          return Response.json(
            { error: { code: 'player_not_in_match', message: 'x', field: null } },
            { status: 409 },
          );
        }
        registrados.push(JSON.parse(String(init.body)));
        return Response.json(evento('e9', 55, 'p1'), { status: 201 });
      }
      const items = [evento('e1', 12, 'p1'), evento('e2', 35, 'p2')];
      return Response.json({
        items,
        consistency: {
          home_goals_recorded: cuadra ? 3 : 1,
          away_goals_recorded: 1,
          home_score: 3,
          away_score: 1,
          matches_official: cuadra,
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

describe('goles del partido', () => {
  it('lista los goles con jugador y minuto sin necesidad de sesión', async () => {
    vi.stubGlobal('fetch', stubFetch().fn);
    renderFicha();
    const seccion = await screen.findByRole('region', { name: /goles/i });
    expect(within(seccion).getByText(/Ana Gómez/)).toBeInTheDocument();
    expect(within(seccion).getByText(/12'/)).toBeInTheDocument();
    expect(within(seccion).getByText(/Luis Paz/)).toBeInTheDocument();
  });

  it('no ofrece formulario a un visitante sin sesión', async () => {
    vi.stubGlobal('fetch', stubFetch().fn);
    renderFicha();
    await screen.findByRole('region', { name: /goles/i });
    expect(screen.queryByRole('button', { name: /registrar gol/i })).not.toBeInTheDocument();
  });

  it('ofrece el formulario al operador y envía el gol', async () => {
    const stub = stubFetch({ rol: 'operador' });
    vi.stubGlobal('fetch', stub.fn);
    renderFicha();
    const boton = await screen.findByRole('button', { name: /registrar gol/i });
    await userEvent.selectOptions(screen.getByLabelText(/jugador/i), 'p1');
    await userEvent.clear(screen.getByLabelText(/minuto/i));
    await userEvent.type(screen.getByLabelText(/minuto/i), '55');
    await userEvent.click(boton);
    await waitFor(() => expect(stub.registrados).toEqual([{ player_id: 'p1', minute: 55 }]));
  });

  it('advierte cuando los goles no cuadran con el marcador', async () => {
    vi.stubGlobal('fetch', stubFetch({ cuadra: false }).fn);
    renderFicha();
    expect(await screen.findByRole('status')).toHaveTextContent(/no coinciden con el marcador/i);
  });

  it('no advierte cuando los goles cuadran', async () => {
    vi.stubGlobal('fetch', stubFetch({ cuadra: true }).fn);
    renderFicha();
    await screen.findByRole('region', { name: /goles/i });
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
  });

  it('traduce el rechazo del jugador ajeno a un mensaje legible', async () => {
    vi.stubGlobal('fetch', stubFetch({ rol: 'operador', error: true }).fn);
    renderFicha();
    const boton = await screen.findByRole('button', { name: /registrar gol/i });
    await userEvent.selectOptions(screen.getByLabelText(/jugador/i), 'p1');
    await userEvent.clear(screen.getByLabelText(/minuto/i));
    await userEvent.type(screen.getByLabelText(/minuto/i), '10');
    await userEvent.click(boton);
    expect(await screen.findByRole('alert')).toHaveTextContent(/no pertenece a ninguno de los dos equipos/i);
  });
});
