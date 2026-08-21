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

const finishedMatches = Array.from({ length: 3 }, (_, i) => ({
  ...baseMatch,
  id: `f${i}`,
  scheduled_at: `2026-08-0${i + 1}T18:00:00Z`,
  status: 'finished' as const,
  home_score: i + 1,
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
  proximosVacio = false,
  finalizadosVacio = false,
  clasificacionVacia = false,
  error = false,
} = {}) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = new URL(String(input));
    const path = url.pathname.replace('/api/v1', '');
    if (path === '/auth/me') return Response.json({ user: null });
    if (path === '/leagues/l1/teams') {
      return Response.json({ items: teams, page: 1, page_size: 20, total: teams.length });
    }
    // Conteos y "goles por fecha" (DashboardPage): se derivan de las mismas
    // listas por estado que ya usa el resto de la suite.
    if (path === '/leagues/l1/matches') {
      const estado = url.searchParams.get('status');
      const items =
        estado === 'finished' ? (finalizadosVacio ? [] : finishedMatches) :
        estado === 'scheduled' ? (proximosVacio ? [] : upcomingMatches) :
        [];
      return Response.json({ items, page: 1, page_size: 100, total: items.length });
    }
    if (path.startsWith('/teams/') && path.endsWith('/players')) {
      return Response.json({ items: [], page: 1, page_size: 1, total: 2 });
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
        recent_matches: finalizadosVacio ? [] : finishedMatches,
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
  it('muestra las cuatro tarjetas del panel y la tabla con hasta 5 filas', async () => {
    vi.stubGlobal('fetch', stubFetch());
    renderDashboard();

    expect(await screen.findByRole('heading', { name: 'Próximo partido' })).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { name: 'Rendimiento de la temporada' }),
    ).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Tabla de posiciones' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Goles por fecha' })).toBeInTheDocument();

    // El enfrentamiento es un único enlace al partido, con ambos equipos.
    const proximo = screen.getByRole('heading', { name: 'Próximo partido' }).closest('section')!;
    const enlace = within(proximo).getByRole('link', { name: /Tigres/ });
    expect(enlace).toHaveAttribute('href', '/matches/s0');
    expect(enlace).toHaveTextContent('Halcones');

    expect(screen.getByRole('table')).toBeInTheDocument();
    const filas = screen.getAllByRole('row').slice(1);
    expect(filas).toHaveLength(5);
    expect(within(filas[0]).getAllByRole('cell')[1]).toHaveTextContent('Tigres');
  });

  it('no repite el próximo partido en una segunda tarjeta (una sola fuente de "qué sigue")', async () => {
    vi.stubGlobal('fetch', stubFetch());
    renderDashboard();
    await screen.findByRole('heading', { name: 'Próximo partido' });
    expect(screen.queryByRole('heading', { name: 'Próximos partidos' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Últimos resultados' })).not.toBeInTheDocument();
  });

  it('reparte los partidos jugados en local / empate / visitante, y suman el total', async () => {
    vi.stubGlobal('fetch', stubFetch());
    renderDashboard();
    const tarjeta = await screen.findByRole('heading', { name: 'Rendimiento de la temporada' });
    const seccion = tarjeta.closest('section')!;

    // Los 3 finalizados del stub tienen home_score 1..3 y away_score 0:
    // los tres los gana el local.
    const valor = (etiqueta: string) =>
      within(seccion).getByText(etiqueta).parentElement!.querySelector('dd')!.textContent;
    expect(valor('Jugados')).toBe('3');
    expect(valor('Gana local')).toBe('3');
    expect(valor('Empates')).toBe('0');
    expect(valor('Gana visitante')).toBe('0');
  });

  it('muestra un mensaje de estado vacío propio cuando un bloque llega vacío', async () => {
    vi.stubGlobal(
      'fetch',
      stubFetch({ proximosVacio: true, finalizadosVacio: true, clasificacionVacia: true }),
    );
    renderDashboard();

    expect(await screen.findByText('No hay próximos partidos.')).toBeInTheDocument();
    expect(screen.getByText('Aún no hay equipos.')).toBeInTheDocument();
    expect(
      screen.getByText('Aún no hay goles registrados en partidos finalizados.'),
    ).toBeInTheDocument();
    expect(screen.getByText('Aún no hay partidos jugados en esta liga.')).toBeInTheDocument();
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });

  it('es accesible en sesión anónima sin redirección al login', async () => {
    vi.stubGlobal('fetch', stubFetch());
    renderDashboard();
    await screen.findByRole('heading', { name: 'Próximo partido' });
    expect(screen.queryByText(/iniciar sesión/i)).not.toBeInTheDocument();
  });

  it('cada tarjeta ofrece su propio enlace de acción (soporte de SC-001)', async () => {
    vi.stubGlobal('fetch', stubFetch());
    renderDashboard();
    expect(await screen.findByRole('link', { name: 'Ver calendario' })).toHaveAttribute(
      'href',
      '/leagues/l1/matches',
    );
    expect(screen.getByRole('link', { name: 'Ver tabla completa' })).toHaveAttribute(
      'href',
      '/leagues/l1/standings',
    );
    expect(screen.getByRole('link', { name: 'Ver estadísticas' })).toHaveAttribute(
      'href',
      '/leagues/l1/top-scorers',
    );
  });

  it('muestra un error legible si la liga no existe', async () => {
    vi.stubGlobal('fetch', stubFetch({ error: true }));
    renderDashboard();
    // Mensaje del catálogo compartido (lib/mensajesDeError.ts), no un literal
    // propio de esta pantalla — mismo criterio que el resto de la app.
    expect(await screen.findByRole('alert')).toHaveTextContent(/no encontramos la liga/i);
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
    expect(await screen.findByRole('heading', { name: 'Próximo partido' })).toBeInTheDocument();
  });
});
