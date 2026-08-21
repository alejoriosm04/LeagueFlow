import { render, screen, within } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../auth/AuthContext';
import { PlayerStatsPage } from '../PlayerStatsPage';
import { TopScorersPage } from '../TopScorersPage';

const fila = (rank: number, player_name: string, extra: Partial<Record<string, unknown>>) => ({
  rank,
  player_id: `p${rank}`,
  player_name,
  team_id: `t${rank}`,
  team_name: `Equipo ${rank}`,
  goals: 0,
  matches_played: 0,
  is_top_scorer: false,
  ...extra,
});

const items = [
  fila(1, 'Ana Goleadora', { goals: 5, matches_played: 3, is_top_scorer: true }),
  fila(2, 'Beto Anotador', { goals: 2, matches_played: 4, is_top_scorer: false }),
  fila(3, 'Caro Delantera', { goals: 1, matches_played: 1, is_top_scorer: false }),
];

function stubFetch({ vacio = false, error = false } = {}) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const path = new URL(String(input)).pathname.replace('/api/v1', '');
    if (path === '/auth/me') return Response.json({ user: null });
    if (path === '/leagues/l1/top-scorers') {
      if (error) return Response.json({ error: { code: 'league_not_found', message: 'La liga no existe.', field: null } }, { status: 404 });
      return Response.json({ items: vacio ? [] : items });
    }
    if (path === '/players/p1/statistics') {
      return Response.json({
        player_id: 'p1',
        player_name: 'Ana Goleadora',
        team_id: 't1',
        team_name: 'Equipo 1',
        goals: 5,
        matches_played: 3,
      });
    }
    if (path === '/players/sin-datos/statistics') {
      return Response.json({
        player_id: 'sin-datos',
        player_name: 'Sin Participaciones',
        team_id: 't9',
        team_name: 'Equipo 9',
        goals: 0,
        matches_played: 0,
      });
    }
    if (path === '/players/inexistente/statistics') {
      return Response.json({ error: { code: 'player_not_found', message: 'El jugador no existe.', field: null } }, { status: 404 });
    }
    return Response.json({ error: { code: 'nf', message: 'No encontrado', field: null } }, { status: 404 });
  });
}

function renderTopScorers() {
  render(
    <MemoryRouter initialEntries={['/leagues/l1/top-scorers']}>
      <AuthProvider>
        <Routes>
          <Route path="/leagues/:id/top-scorers" element={<TopScorersPage />} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

function renderPlayerStats(playerId: string) {
  render(
    <MemoryRouter initialEntries={[`/players/${playerId}/statistics`]}>
      <AuthProvider>
        <Routes>
          <Route path="/players/:playerId/statistics" element={<PlayerStatsPage />} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

beforeEach(() => vi.restoreAllMocks());

describe('tabla de goleadores pública', () => {
  it('muestra la tabla ordenada por goles descendente', async () => {
    vi.stubGlobal('fetch', stubFetch());
    renderTopScorers();
    expect(await screen.findByRole('heading', { name: /tabla de goleadores/i })).toBeInTheDocument();

    const filas = screen.getAllByRole('row').slice(1);
    expect(filas.map((f) => within(f).getAllByRole('cell')[1].textContent)).toEqual([
      expect.stringContaining('Ana Goleadora'),
      expect.stringContaining('Beto Anotador'),
      expect.stringContaining('Caro Delantera'),
    ]);
    expect(within(filas[0]).getAllByRole('cell')[3]).toHaveTextContent('5');
  });

  it('resalta al máximo goleador para identificación inmediata (SC-002)', async () => {
    vi.stubGlobal('fetch', stubFetch());
    renderTopScorers();
    const filaTop = await screen.findByRole('row', { name: /Ana Goleadora/ });
    expect(filaTop).toHaveTextContent(/máximo goleador/i);
    const filaSegunda = screen.getByRole('row', { name: /Beto Anotador/ });
    expect(filaSegunda).not.toHaveTextContent(/máximo goleador/i);
  });

  it('es accesible sin sesión y no ofrece ningún control de edición', async () => {
    vi.stubGlobal('fetch', stubFetch());
    renderTopScorers();
    await screen.findByRole('table');
    expect(screen.queryByText(/iniciar sesión/i)).not.toBeInTheDocument();
    expect(screen.queryAllByRole('button')).toHaveLength(0);
    expect(screen.queryAllByRole('checkbox')).toHaveLength(0);
  });

  it('muestra un estado vacío cuando la liga no tiene goleadores', async () => {
    vi.stubGlobal('fetch', stubFetch({ vacio: true }));
    renderTopScorers();
    expect(await screen.findByText(/todavía no hay goles registrados/i)).toBeInTheDocument();
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });

  it('muestra un error legible si la liga no existe', async () => {
    vi.stubGlobal('fetch', stubFetch({ error: true }));
    renderTopScorers();
    expect(await screen.findByRole('alert')).toHaveTextContent(/no se encontró la liga/i);
  });
});

describe('ficha individual pública', () => {
  it('muestra goles y partidos jugados del jugador', async () => {
    vi.stubGlobal('fetch', stubFetch());
    renderPlayerStats('p1');
    expect(await screen.findByRole('heading', { name: 'Ana Goleadora' })).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('muestra ceros en vez de un error para un jugador sin participaciones', async () => {
    vi.stubGlobal('fetch', stubFetch());
    renderPlayerStats('sin-datos');
    await screen.findByRole('heading', { name: 'Sin Participaciones' });
    const valores = screen.getAllByRole('definition').map((d) => d.textContent);
    expect(valores).toEqual(['0', '0']);
  });

  it('muestra un error legible si el jugador no existe', async () => {
    vi.stubGlobal('fetch', stubFetch());
    renderPlayerStats('inexistente');
    expect(await screen.findByRole('alert')).toHaveTextContent(/no se encontró el jugador/i);
  });
});
