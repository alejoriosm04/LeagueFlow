import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../auth/AuthContext';
import { LeagueDetailPage } from '../../leagues/LeagueDetailPage';
import { DashboardPage } from '../DashboardPage';

const teams = [
  { id: 't1', name: 'Tigres' },
  { id: 't2', name: 'Halcones' },
  { id: 't3', name: 'Leones' },
];

const baseMatch = {
  league_id: 'l1', home_team_id: 't1', away_team_id: 't2', created_by: 'u1',
  created_at: '2026-08-20T00:00:00Z', updated_at: '2026-08-20T00:00:00Z',
};

const recentMatches = Array.from({ length: 5 }, (_, i) => ({
  ...baseMatch,
  id: `f${i}`,
  scheduled_at: `2026-08-0${i + 1}T18:00:00Z`,
  status: 'finished' as const,
  home_score: i,
  away_score: 0,
}));

const upcomingMatches = Array.from({ length: 5 }, (_, i) => ({
  ...baseMatch,
  id: `s${i}`,
  scheduled_at: `2026-09-0${i + 1}T18:00:00Z`,
  status: 'scheduled' as const,
  home_score: null,
  away_score: null,
}));

const fila = (position: number, team_name: string, team_id: string) => ({
  position,
  team_id,
  team_name,
  played: 2,
  won: 1,
  drawn: 0,
  lost: 1,
  goals_for: 3,
  goals_against: 2,
  goal_difference: 1,
  points: 3,
});

const topStandings = [
  fila(1, 'Tigres', 't1'),
  fila(2, 'Halcones', 't2'),
  fila(3, 'Leones', 't3'),
  fila(4, 'Osos', 't4'),
  fila(5, 'Lobos', 't5'),
];

function stubFetch({
  recientesVacio = false,
  proximosVacio = false,
  clasificacionVacia = false,
  error = false,
} = {}) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const path = new URL(String(input)).pathname.replace('/api/v1', '');
    if (path === '/auth/me') return Response.json({ user: null });
    if (path === '/leagues/l1/teams') {
      return Response.json({ items: teams, page: 1, page_size: 20, total: teams.length });
    }
    if (path === '/leagues/l1/dashboard') {
      if (error) {
        return Response.json(
          { error: { code: 'league_not_found', message: 'La liga no existe.', field: null } },
          { status: 404 },
        );
      }
      return Response.json({
        league_id: 'l1',
        recent_matches: recientesVacio ? [] : recentMatches,
        upcoming_matches: proximosVacio ? [] : upcomingMatches,
        top_standings: clasificacionVacia ? [] : topStandings,
      });
    }
    return Response.json({ error: { code: 'nf', message: 'No encontrado', field: null } }, { status: 404 });
  });
}

function renderDashboard() {
  render(
    <MemoryRouter initialEntries={['/leagues/l1/dashboard']}>
      <AuthProvider>
        <Routes>
          <Route path="/leagues/:id/dashboard" element={<DashboardPage />} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

beforeEach(() => vi.restoreAllMocks());

describe('dashboard general de la liga', () => {
  it('muestra los tres bloques con encabezado en español y hasta 5 filas cada uno', async () => {
    vi.stubGlobal('fetch', stubFetch());
    renderDashboard();

    expect(await screen.findByRole('heading', { name: 'Últimos resultados' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Próximos partidos' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Tabla de posiciones' })).toBeInTheDocument();

    const recientes = screen.getByRole('heading', { name: 'Últimos resultados' })
      .closest('section')!;
    expect(within(recientes).getAllByRole('link', { name: /Tigres/ })).toHaveLength(5);
    const proximos = screen.getByRole('heading', { name: 'Próximos partidos' })
      .closest('section')!;
    expect(within(proximos).getAllByRole('link', { name: /Tigres/ })).toHaveLength(5);

    expect(screen.getByRole('table')).toBeInTheDocument();
    const filas = screen.getAllByRole('row').slice(1);
    expect(filas).toHaveLength(5);
    expect(within(filas[0]).getAllByRole('cell')[1]).toHaveTextContent('Tigres');
  });

  it('muestra un mensaje de estado vacío propio cuando un bloque llega vacío', async () => {
    vi.stubGlobal(
      'fetch',
      stubFetch({ recientesVacio: true, proximosVacio: true, clasificacionVacia: true }),
    );
    renderDashboard();

    expect(await screen.findByText('Aún no hay partidos jugados.')).toBeInTheDocument();
    expect(screen.getByText('Aún no hay próximos partidos.')).toBeInTheDocument();
    expect(screen.getByText('Aún no hay equipos.')).toBeInTheDocument();
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });

  it('cada bloque llega vacío de forma independiente (equipos sin partidos)', async () => {
    vi.stubGlobal('fetch', stubFetch({ recientesVacio: true, proximosVacio: true }));
    renderDashboard();

    expect(await screen.findByText('Aún no hay partidos jugados.')).toBeInTheDocument();
    expect(screen.getByText('Aún no hay próximos partidos.')).toBeInTheDocument();
    // La clasificación NO está vacía en este caso (Assumption "Bloque de
    // clasificación 'vacío'" de spec.md): sigue mostrando su tabla.
    expect(screen.getByRole('table')).toBeInTheDocument();
  });

  it('es accesible en sesión anónima sin redirección al login', async () => {
    vi.stubGlobal('fetch', stubFetch());
    renderDashboard();
    await screen.findByRole('heading', { name: 'Últimos resultados' });
    expect(screen.queryByText(/iniciar sesión/i)).not.toBeInTheDocument();
  });

  it('ofrece un enlace a la clasificación completa (soporte de SC-001)', async () => {
    vi.stubGlobal('fetch', stubFetch());
    renderDashboard();
    const enlace = await screen.findByRole('link', { name: 'Ver clasificación completa' });
    expect(enlace).toHaveAttribute('href', '/leagues/l1/standings');
    const calendario = screen.getByRole('link', { name: 'Ver calendario completo' });
    expect(calendario).toHaveAttribute('href', '/leagues/l1/matches');
  });

  it('muestra un error legible si la liga no existe', async () => {
    vi.stubGlobal('fetch', stubFetch({ error: true }));
    renderDashboard();
    expect(await screen.findByRole('alert')).toHaveTextContent(/no se encontró la liga/i);
  });

  it('se descubre desde el detalle de la liga en una interacción', async () => {
    const fetchMock = stubFetch();
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL) => {
        const path = new URL(String(input)).pathname.replace('/api/v1', '');
        if (path === '/leagues/l1') {
          return Response.json({
            id: 'l1', name: 'Liga pública', season: '2026', description: null,
          });
        }
        return fetchMock(input);
      }),
    );
    render(
      <MemoryRouter initialEntries={['/leagues/l1']}>
        <AuthProvider>
          <Routes>
            <Route path="/leagues/:id" element={<LeagueDetailPage />} />
            <Route path="/leagues/:id/dashboard" element={<DashboardPage />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>,
    );
    await userEvent.click(await screen.findByRole('link', { name: 'Ver dashboard' }));
    expect(await screen.findByRole('heading', { name: 'Últimos resultados' })).toBeInTheDocument();
  });
});
