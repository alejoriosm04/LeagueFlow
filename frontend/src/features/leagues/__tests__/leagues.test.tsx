import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../auth/AuthContext';
import { CreateLeagueForm } from '../CreateLeagueForm';
import { LeaguesPage } from '../LeaguesPage';

const LIGA = {
  id: 'l1',
  name: 'Interfacultades',
  season: '2026-1',
  description: null,
  created_by: 'u1',
  created_at: '2026-08-19T00:00:00Z',
};

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

beforeEach(() => vi.restoreAllMocks());

describe('LeaguesPage', () => {
  it('muestra un estado vacío legible cuando no hay ligas', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/me': { status: 200, body: { user: null } },
        '/leagues?page=1&page_size=20': {
          status: 200,
          body: { items: [], page: 1, page_size: 20, total: 0 },
        },
      }),
    );

    render(
      <MemoryRouter>
        <AuthProvider>
          <LeaguesPage />
        </AuthProvider>
      </MemoryRouter>,
    );

    expect(await screen.findByText(/no hay ligas registradas/i)).toBeInTheDocument();
    // Sin sesión de organizador no se muestra la acción de crear.
    expect(screen.queryByRole('link', { name: /crear liga/i })).not.toBeInTheDocument();
  });

  it('muestra el enlace para crear liga solo al organizador', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/me': {
          status: 200,
          body: { user: { id: 'u1', username: 'org', role: 'organizador', status: 'active' } },
        },
        '/leagues?page=1&page_size=20': {
          status: 200,
          body: { items: [], page: 1, page_size: 20, total: 0 },
        },
      }),
    );

    render(
      <MemoryRouter>
        <AuthProvider>
          <LeaguesPage />
        </AuthProvider>
      </MemoryRouter>,
    );

    expect(await screen.findByText(/no hay ligas registradas/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /crear liga/i })).toHaveAttribute(
      'href',
      '/leagues/new',
    );
  });

  it('lista las ligas con enlace a su ficha', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/me': { status: 200, body: { user: null } },
        '/leagues?page=1&page_size=20': {
          status: 200,
          body: { items: [LIGA], page: 1, page_size: 20, total: 1 },
        },
      }),
    );

    render(
      <MemoryRouter>
        <AuthProvider>
          <LeaguesPage />
        </AuthProvider>
      </MemoryRouter>,
    );

    const enlace = await screen.findByRole('link', { name: /Interfacultades/ });
    expect(enlace).toHaveAttribute('href', '/leagues/l1');
  });
});

describe('CreateLeagueForm', () => {
  it('muestra el error.message del envelope al recibir 409', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/leagues': {
          status: 409,
          body: {
            error: {
              code: 'league_already_exists',
              message: 'Ya existe una liga con ese nombre y temporada.',
              field: 'name',
            },
          },
        },
      }),
    );

    render(
      <MemoryRouter>
        <CreateLeagueForm />
      </MemoryRouter>,
    );

    await userEvent.type(screen.getByLabelText('Nombre'), 'Interfacultades');
    await userEvent.type(screen.getByLabelText('Temporada'), '2026-1');
    await userEvent.click(screen.getByRole('button', { name: /crear liga/i }));

    const alerta = await screen.findByRole('alert');
    // FR-015 / SC-003 (spec 012): el texto ya no es el `message` del servidor
    // sino la traducción del catálogo, indexada por `code`. La afirmación es
    // la misma —hay un error de campo legible— con el texto que impone el
    // requisito nuevo.
    expect(alerta).toHaveTextContent('Ya existe una liga con ese nombre en esa temporada.');
  });

  it('crea la liga y navega a su ficha', async () => {
    const fetchMock = mockFetch({
      '/leagues': { status: 201, body: LIGA },
    });
    vi.stubGlobal('fetch', fetchMock);

    render(
      <MemoryRouter initialEntries={['/leagues/new']}>
        <Routes>
          <Route path="/leagues/new" element={<CreateLeagueForm />} />
          <Route path="/leagues/:id" element={<div>ficha creada</div>} />
        </Routes>
      </MemoryRouter>,
    );

    await userEvent.type(screen.getByLabelText('Nombre'), 'Interfacultades');
    await userEvent.type(screen.getByLabelText('Temporada'), '2026-1');
    await userEvent.click(screen.getByRole('button', { name: /crear liga/i }));

    expect(await screen.findByText('ficha creada')).toBeInTheDocument();

    const post = fetchMock.mock.calls.find(([, init]) => init?.method === 'POST');
    expect(post).toBeTruthy();
    expect(JSON.parse(String((post?.[1] as RequestInit).body))).toEqual({
      name: 'Interfacultades',
      season: '2026-1',
      description: null,
    });
  });
});
