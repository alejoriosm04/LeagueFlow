import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../auth/AuthContext';
import { CreateMatchForm } from '../CreateMatchForm';
import { MatchesPage } from '../MatchesPage';

const EQUIPO_A = {
  id: 't1',
  league_id: 'l1',
  name: 'Ingeniería FC',
  crest_url: null,
  colors: null,
  status: 'active',
  created_by: 'u1',
  created_at: '2026-08-19T00:00:00Z',
};

const EQUIPO_B = {
  ...EQUIPO_A,
  id: 't2',
  name: 'Medicina FC',
};

const PARTIDO = {
  id: 'm1',
  league_id: 'l1',
  home_team_id: 't1',
  away_team_id: 't2',
  scheduled_at: '2026-09-01T18:00:00Z',
  status: 'scheduled',
  home_score: null,
  away_score: null,
  created_by: 'u1',
  created_at: '2026-08-19T00:00:00Z',
  updated_at: '2026-08-19T00:00:00Z',
};

const ORGANIZADOR = { id: 'u1', username: 'org', role: 'organizador', status: 'active' };

function mockFetch(respuestas: Record<string, { status: number; body: unknown }>) {
  return vi.fn(async (url: RequestInfo | URL, init?: RequestInit) => {
    void init;
    const ruta = String(url).replace(/^.*\/api\/v1/, '');
    const clave = Object.keys(respuestas).find((k) => ruta === k || ruta.startsWith(k + '?'));
    // Exact match first, then path without query for POST targets
    let r = clave ? respuestas[clave] : undefined;
    if (!r) {
      const sinQuery = ruta.split('?')[0];
      r = respuestas[sinQuery];
    }
    if (!r) {
      r = { status: 404, body: { error: { code: 'nf', message: 'x', field: null } } };
    }
    return new Response(JSON.stringify(r.body), {
      status: r.status,
      headers: { 'Content-Type': 'application/json' },
    });
  });
}

beforeEach(() => vi.restoreAllMocks());

describe('MatchesPage', () => {
  it('muestra estado vacío cuando no hay partidos', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/me': { status: 200, body: { user: null } },
        '/leagues/l1/matches?page=1&page_size=100&status=scheduled': {
          status: 200,
          body: { items: [], page: 1, page_size: 100, total: 0 },
        },
        '/leagues/l1/matches?page=1&page_size=100&status=finished': {
          status: 200,
          body: { items: [], page: 1, page_size: 100, total: 0 },
        },
        '/leagues/l1/teams?include_inactive=false&page=1&page_size=20': {
          status: 200,
          body: { items: [], page: 1, page_size: 20, total: 0 },
        },
      }),
    );

    render(
      <MemoryRouter initialEntries={['/leagues/l1/matches']}>
        <AuthProvider>
          <Routes>
            <Route path="/leagues/:id/matches" element={<MatchesPage />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>,
    );

    expect(await screen.findByText(/no hay partidos en esta liga/i)).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /programar partido/i })).not.toBeInTheDocument();
  });

  it('muestra el enlace para programar solo al organizador', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/me': { status: 200, body: { user: ORGANIZADOR } },
        '/leagues/l1/matches?page=1&page_size=100&status=scheduled': {
          status: 200,
          body: { items: [], page: 1, page_size: 100, total: 0 },
        },
        '/leagues/l1/matches?page=1&page_size=100&status=finished': {
          status: 200,
          body: { items: [], page: 1, page_size: 100, total: 0 },
        },
        '/leagues/l1/teams?include_inactive=false&page=1&page_size=20': {
          status: 200,
          body: { items: [], page: 1, page_size: 20, total: 0 },
        },
      }),
    );

    render(
      <MemoryRouter initialEntries={['/leagues/l1/matches']}>
        <AuthProvider>
          <Routes>
            <Route path="/leagues/:id/matches" element={<MatchesPage />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>,
    );

    expect(await screen.findByText(/no hay partidos en esta liga/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /programar partido/i })).toHaveAttribute(
      'href',
      '/leagues/l1/matches/new',
    );
  });

  it('lista partidos con nombres de equipo', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/me': { status: 200, body: { user: null } },
        '/leagues/l1/matches?page=1&page_size=100&status=scheduled': {
          status: 200,
          body: { items: [PARTIDO], page: 1, page_size: 100, total: 1 },
        },
        '/leagues/l1/matches?page=1&page_size=100&status=finished': {
          status: 200,
          body: { items: [], page: 1, page_size: 100, total: 0 },
        },
        '/leagues/l1/teams?include_inactive=false&page=1&page_size=20': {
          status: 200,
          body: { items: [EQUIPO_A, EQUIPO_B], page: 1, page_size: 20, total: 2 },
        },
      }),
    );

    render(
      <MemoryRouter initialEntries={['/leagues/l1/matches']}>
        <AuthProvider>
          <Routes>
            <Route path="/leagues/:id/matches" element={<MatchesPage />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>,
    );

    // FR-009 (spec 012): el marcador pasa al formato único
    // "LOCAL 3 — 1 VISITANTE", así que el texto "X vs Y" ya no existe
    // salvo en partidos sin resultado. Se consulta por rol y por el
    // nombre del equipo, que es lo estable frente al remarcado.
    const fila = await screen.findByRole('link', { name: /Ingeniería FC/ });
    expect(fila).toHaveAccessibleName(/Medicina FC/);
  });
});

describe('CreateMatchForm', () => {
  it('muestra el error.message del envelope al recibir 409', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/leagues/l1/teams?include_inactive=false&page=1&page_size=20': {
          status: 200,
          body: { items: [EQUIPO_A, EQUIPO_B], page: 1, page_size: 20, total: 2 },
        },
        '/leagues/l1/matches': {
          status: 409,
          body: {
            error: {
              code: 'match_same_team',
              message: 'Un equipo no puede enfrentarse a sí mismo.',
              field: null,
            },
          },
        },
      }),
    );

    render(
      <MemoryRouter initialEntries={['/leagues/l1/matches/new']}>
        <Routes>
          <Route path="/leagues/:id/matches/new" element={<CreateMatchForm />} />
        </Routes>
      </MemoryRouter>,
    );

    await screen.findByLabelText('Equipo local');
    await userEvent.selectOptions(screen.getByLabelText('Equipo local'), 't1');
    await userEvent.selectOptions(screen.getByLabelText('Equipo visitante'), 't1');
    await userEvent.type(screen.getByLabelText('Fecha y hora'), '2026-09-01T18:00');
    await userEvent.click(screen.getByRole('button', { name: /programar partido/i }));

    const alerta = await screen.findByRole('alert');
    // FR-015 / SC-003 (spec 012): el texto sale del catálogo en español
    // indexado por `code`, no del `message` del servidor. Misma regla, misma
    // afirmación, redacción del catálogo.
    expect(alerta).toHaveTextContent('Un equipo no puede jugar contra sí mismo.');
  });

  it('programa el partido y navega al listado', async () => {
    const fetchMock = mockFetch({
      '/leagues/l1/teams?include_inactive=false&page=1&page_size=20': {
        status: 200,
        body: { items: [EQUIPO_A, EQUIPO_B], page: 1, page_size: 20, total: 2 },
      },
      '/leagues/l1/matches': { status: 201, body: PARTIDO },
    });
    vi.stubGlobal('fetch', fetchMock);

    render(
      <MemoryRouter initialEntries={['/leagues/l1/matches/new']}>
        <Routes>
          <Route path="/leagues/:id/matches/new" element={<CreateMatchForm />} />
          <Route path="/leagues/:id/matches" element={<div>listado de partidos</div>} />
        </Routes>
      </MemoryRouter>,
    );

    await screen.findByLabelText('Equipo local');
    await userEvent.selectOptions(screen.getByLabelText('Equipo local'), 't1');
    await userEvent.selectOptions(screen.getByLabelText('Equipo visitante'), 't2');
    await userEvent.type(screen.getByLabelText('Fecha y hora'), '2026-09-01T18:00');
    await userEvent.click(screen.getByRole('button', { name: /programar partido/i }));

    expect(await screen.findByText('listado de partidos')).toBeInTheDocument();
  });
});
