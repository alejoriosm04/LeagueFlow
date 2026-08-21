import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../auth/AuthContext';
import { CreatePlayerForm } from '../CreatePlayerForm';
import { PlayersPage } from '../PlayersPage';

const JUGADOR = {
  id: 'p1',
  team_id: 't1',
  name: 'Andrés Gómez',
  number: 10,
  position: 'delantero',
  status: 'active',
  created_by: 'u1',
  created_at: '2026-08-19T00:00:00Z',
};

const ORGANIZADOR = { id: 'u1', username: 'org', role: 'organizador', status: 'active' };

function mockFetch(respuestas: Record<string, { status: number; body: unknown }>) {
  return vi.fn(async (url: RequestInfo | URL, init?: RequestInit) => {
    void init;
    const ruta = String(url).replace(/^.*\/api\/v1/, '');
    const clave = Object.keys(respuestas).find((k) => ruta === k);
    const r = clave
      ? respuestas[clave]
      : { status: 404, body: { error: { code: 'nf', message: 'x', field: null } } };
    return new Response(JSON.stringify(r.body), {
      status: r.status,
      headers: { 'Content-Type': 'application/json' },
    });
  });
}

function renderPlayersPage() {
  return render(
    <MemoryRouter initialEntries={['/teams/t1/players']}>
      <AuthProvider>
        <Routes>
          <Route path="/teams/:teamId/players" element={<PlayersPage />} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

beforeEach(() => vi.restoreAllMocks());

describe('PlayersPage', () => {
  it('muestra estado vacío cuando el equipo no tiene jugadores', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/me': { status: 200, body: { user: null } },
        '/teams/t1/players?include_inactive=false&page=1&page_size=20': {
          status: 200,
          body: { items: [], page: 1, page_size: 20, total: 0 },
        },
      }),
    );

    renderPlayersPage();

    expect(await screen.findByText(/no hay jugadores registrados/i)).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /registrar jugador/i })).not.toBeInTheDocument();
  });

  it('muestra el enlace para registrar jugador solo al organizador', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/me': { status: 200, body: { user: ORGANIZADOR } },
        '/teams/t1/players?include_inactive=false&page=1&page_size=20': {
          status: 200,
          body: { items: [], page: 1, page_size: 20, total: 0 },
        },
      }),
    );

    renderPlayersPage();

    expect(await screen.findByText(/no hay jugadores registrados/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /registrar jugador/i })).toHaveAttribute(
      'href',
      '/teams/t1/players/new',
    );
  });

  it('lista jugadores con dorsal y posición', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/me': { status: 200, body: { user: null } },
        '/teams/t1/players?include_inactive=false&page=1&page_size=20': {
          status: 200,
          body: { items: [JUGADOR], page: 1, page_size: 20, total: 1 },
        },
      }),
    );

    renderPlayersPage();

    expect(await screen.findByText(/Andrés Gómez/)).toBeInTheDocument();
    expect(screen.getByText(/#10/)).toBeInTheDocument();
    expect(screen.getByText(/delantero/)).toBeInTheDocument();
  });
});

describe('CreatePlayerForm', () => {
  it('muestra el error.message del envelope al recibir 409', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/teams/t1/players': {
          status: 409,
          body: {
            error: {
              code: 'player_number_duplicate',
              message: 'Ya existe un jugador con ese dorsal en este equipo.',
              field: 'number',
            },
          },
        },
      }),
    );

    render(
      <MemoryRouter initialEntries={['/teams/t1/players/new']}>
        <Routes>
          <Route path="/teams/:teamId/players/new" element={<CreatePlayerForm />} />
        </Routes>
      </MemoryRouter>,
    );

    await userEvent.type(screen.getByLabelText('Nombre'), 'Andrés Gómez');
    await userEvent.type(screen.getByLabelText(/Dorsal/), '10');
    await userEvent.click(screen.getByRole('button', { name: /registrar jugador/i }));

    const alerta = await screen.findByRole('alert');
    // FR-015 / SC-003 (spec 012): el texto ya no es el `message` del servidor
    // sino la traducción del catálogo, indexada por `code`. La afirmación es
    // la misma —hay un error de campo legible— con el texto que impone el
    // requisito nuevo.
    expect(alerta).toHaveTextContent('Ese dorsal ya está asignado a otro jugador del equipo.');
  });

  it('registra el jugador y navega a la plantilla', async () => {
    const fetchMock = mockFetch({
      '/teams/t1/players': { status: 201, body: JUGADOR },
    });
    vi.stubGlobal('fetch', fetchMock);

    render(
      <MemoryRouter initialEntries={['/teams/t1/players/new']}>
        <Routes>
          <Route path="/teams/:teamId/players/new" element={<CreatePlayerForm />} />
          <Route path="/teams/:teamId/players" element={<div>plantilla</div>} />
        </Routes>
      </MemoryRouter>,
    );

    await userEvent.type(screen.getByLabelText('Nombre'), 'Andrés Gómez');
    await userEvent.type(screen.getByLabelText(/Dorsal/), '10');
    await userEvent.type(screen.getByLabelText(/Posición/), 'delantero');
    await userEvent.click(screen.getByRole('button', { name: /registrar jugador/i }));

    expect(await screen.findByText('plantilla')).toBeInTheDocument();

    const post = fetchMock.mock.calls.find(([, init]) => init?.method === 'POST');
    expect(post).toBeTruthy();
    expect(JSON.parse(String((post?.[1] as RequestInit).body))).toEqual({
      name: 'Andrés Gómez',
      number: 10,
      position: 'delantero',
    });
  });
});
