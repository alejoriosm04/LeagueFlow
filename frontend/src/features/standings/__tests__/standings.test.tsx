import { render, screen, within } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../auth/AuthContext';
import { LeagueDetailPage } from '../../leagues/LeagueDetailPage';
import { StandingsPage } from '../StandingsPage';

const fila = (position: number, team_name: string, extra: Record<string, number>) => ({
  position,
  team_id: `t${position}`,
  team_name,
  played: 0,
  won: 0,
  drawn: 0,
  lost: 0,
  goals_for: 0,
  goals_against: 0,
  goal_difference: 0,
  points: 0,
  ...extra,
});

const items = [
  fila(1, 'Alfa', { played: 2, won: 2, goals_for: 5, goals_against: 1, goal_difference: 4, points: 6 }),
  fila(2, 'Delta', { played: 2, won: 1, drawn: 1, goals_for: 3, goals_against: 1, goal_difference: 2, points: 4 }),
  fila(3, 'Bravo', { played: 1, lost: 1, goals_for: 0, goals_against: 2, goal_difference: -2, points: 0 }),
];

function stubFetch({ vacio = false, error = false } = {}) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const path = new URL(String(input)).pathname.replace('/api/v1', '');
    if (path === '/auth/me') return Response.json({ user: null });
    if (path === '/leagues/l1') return Response.json({ id: 'l1', name: 'Liga Amateur', season: '2026', description: null, created_by: 'u1', created_at: '2026-08-01T00:00:00Z' });
    if (path === '/leagues/l1/standings') {
      if (error) return Response.json({ error: { code: 'league_not_found', message: 'La liga no existe.', field: null } }, { status: 404 });
      return Response.json({ league_id: 'l1', items: vacio ? [] : items });
    }
    return Response.json({ error: { code: 'nf', message: 'No encontrado', field: null } }, { status: 404 });
  });
}

function renderStandings() {
  render(
    <MemoryRouter initialEntries={['/leagues/l1/standings']}>
      <AuthProvider>
        <Routes>
          <Route path="/leagues/:id/standings" element={<StandingsPage />} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

beforeEach(() => vi.restoreAllMocks());

describe('clasificación pública', () => {
  it('muestra los diez encabezados y las filas en el orden que entrega la API', async () => {
    vi.stubGlobal('fetch', stubFetch());
    renderStandings();
    expect(await screen.findByRole('heading', { name: /clasificación/i })).toBeInTheDocument();

    const encabezados = screen.getAllByRole('columnheader').map((c) => c.textContent);
    expect(encabezados).toEqual(['Pos', 'Equipo', 'PJ', 'G', 'E', 'P', 'GF', 'GC', 'GD', 'Pts']);

    const filas = screen.getAllByRole('row').slice(1);
    expect(filas.map((f) => within(f).getAllByRole('cell')[1].textContent)).toEqual([
      'Alfa',
      'Delta',
      'Bravo',
    ]);
    // La celda de posición cambia de "1" a "🥇 1.º" por FR-011 (spec 012):
    // el podio debe distinguirse por TEXTO, no solo por color. No es un
    // ajuste de selector ni una prueba debilitada: se afirma exactamente lo
    // mismo (valores y orden), con el texto que el requisito nuevo impone.
    expect(within(filas[0]).getAllByRole('cell').map((c) => c.textContent)).toEqual([
      '🥇 1.º', 'Alfa', '2', '2', '0', '0', '5', '1', '+4', '6',
    ]);
  });

  it('muestra la diferencia de goles negativa con su signo', async () => {
    vi.stubGlobal('fetch', stubFetch());
    renderStandings();
    const bravo = await screen.findByRole('row', { name: /Bravo/ });
    expect(within(bravo).getAllByRole('cell')[8]).toHaveTextContent('-2');
  });

  it('es accesible sin sesión y no ofrece ningún control de edición', async () => {
    vi.stubGlobal('fetch', stubFetch());
    renderStandings();
    await screen.findByRole('table');
    expect(screen.queryByText(/iniciar sesión/i)).not.toBeInTheDocument();
    expect(screen.queryAllByRole('button')).toHaveLength(0);
    expect(screen.queryAllByRole('textbox')).toHaveLength(0);
    expect(screen.queryAllByRole('spinbutton')).toHaveLength(0);
  });

  it('muestra un estado vacío cuando la liga aún no tiene equipos', async () => {
    vi.stubGlobal('fetch', stubFetch({ vacio: true }));
    renderStandings();
    expect(await screen.findByText(/todavía no hay equipos/i)).toBeInTheDocument();
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });

  it('muestra un error legible si la liga no existe', async () => {
    vi.stubGlobal('fetch', stubFetch({ error: true }));
    renderStandings();
    // FR-015 / SC-003 (spec 012): el mensaje ya no lo escribe la pantalla ni
    // viene del servidor ("La liga no existe."), sino del catálogo en español
    // indexado por `code`. La afirmación sigue siendo la misma: hay un error
    // legible, sin detalles técnicos.
    expect(await screen.findByRole('alert')).toHaveTextContent(
      /no encontramos la liga que buscas/i,
    );
    expect(screen.getByRole('alert')).not.toHaveTextContent('league_not_found');
  });

  it('se descubre desde el detalle de la liga', async () => {
    vi.stubGlobal('fetch', stubFetch());
    render(
      <MemoryRouter initialEntries={['/leagues/l1']}>
        <AuthProvider>
          <Routes>
            <Route path="/leagues/:id" element={<LeagueDetailPage />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>,
    );
    const enlace = await screen.findByRole('link', { name: /ver clasificación/i });
    expect(enlace).toHaveAttribute('href', '/leagues/l1/standings');
  });
});
