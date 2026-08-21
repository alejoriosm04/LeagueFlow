import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../auth/AuthContext';
import { CreateTeamForm } from '../CreateTeamForm';
import { TeamsPage } from '../TeamsPage';

const EQUIPO = {
  id: 't1',
  league_id: 'l1',
  name: 'Ingeniería FC',
  crest_url: null,
  colors: 'azul/blanco',
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

function renderTeamsPage() {
  return render(
    <MemoryRouter initialEntries={['/leagues/l1/teams']}>
      <AuthProvider>
        <Routes>
          <Route path="/leagues/:id/teams" element={<TeamsPage />} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

beforeEach(() => vi.restoreAllMocks());

describe('TeamsPage', () => {
  it('muestra estado vacío cuando la liga no tiene equipos', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/me': { status: 200, body: { user: null } },
        '/leagues/l1/teams?include_inactive=false&page=1&page_size=20': {
          status: 200,
          body: { items: [], page: 1, page_size: 20, total: 0 },
        },
      }),
    );

    renderTeamsPage();

    expect(await screen.findByText(/no hay equipos registrados/i)).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /registrar equipo/i })).not.toBeInTheDocument();
  });

  it('muestra el enlace para registrar equipo solo al organizador', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/me': { status: 200, body: { user: ORGANIZADOR } },
        '/leagues/l1/teams?include_inactive=false&page=1&page_size=20': {
          status: 200,
          body: { items: [], page: 1, page_size: 20, total: 0 },
        },
      }),
    );

    renderTeamsPage();

    expect(await screen.findByText(/no hay equipos registrados/i)).toBeInTheDocument();
    // FR-014 (spec 012): la acción del estado vacío dice qué hacer a
    // continuación, y su etiqueta la fija el escenario 12 de quickstart.md:
    // "Registrar el primer equipo". Mismo destino, misma afirmación.
    expect(screen.getByRole('link', { name: /registrar el primer equipo/i })).toHaveAttribute(
      'href',
      '/leagues/l1/teams/new',
    );
  });

  it('lista equipos con escudo por defecto cuando crest_url es nulo', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/me': { status: 200, body: { user: null } },
        '/leagues/l1/teams?include_inactive=false&page=1&page_size=20': {
          status: 200,
          body: { items: [EQUIPO], page: 1, page_size: 20, total: 1 },
        },
      }),
    );

    renderTeamsPage();

    expect(await screen.findByText('Ingeniería FC')).toBeInTheDocument();
    // crest_url nulo -> no se renderiza <img>, sino las iniciales del equipo.
    // FR-012 (spec 012) pide "las iniciales del equipo", no una sola letra:
    // "Ingeniería FC" -> "IF". Misma afirmación, texto que impone el requisito.
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
    expect(screen.getByText('IF')).toBeInTheDocument();
  });
});

describe('CreateTeamForm', () => {
  it('muestra el error.message del envelope al recibir 409', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/leagues/l1/teams': {
          status: 409,
          body: {
            error: {
              code: 'team_name_duplicate',
              message: 'Ya existe un equipo con ese nombre en esta liga.',
              field: 'name',
            },
          },
        },
      }),
    );

    render(
      <MemoryRouter initialEntries={['/leagues/l1/teams/new']}>
        <Routes>
          <Route path="/leagues/:id/teams/new" element={<CreateTeamForm />} />
        </Routes>
      </MemoryRouter>,
    );

    await userEvent.type(screen.getByLabelText('Nombre'), 'Ingeniería FC');
    await userEvent.click(screen.getByRole('button', { name: /registrar equipo/i }));

    const alerta = await screen.findByRole('alert');
    // FR-015 / SC-003 (spec 012): el texto ya no es el `message` del servidor
    // sino la traducción del catálogo, indexada por `code`. La afirmación es
    // la misma —hay un error de campo legible— con el texto que impone el
    // requisito nuevo.
    expect(alerta).toHaveTextContent('Ya hay un equipo con ese nombre en esta liga.');
  });

  it('registra el equipo y navega al listado', async () => {
    const fetchMock = mockFetch({
      '/leagues/l1/teams': { status: 201, body: EQUIPO },
    });
    vi.stubGlobal('fetch', fetchMock);

    render(
      <MemoryRouter initialEntries={['/leagues/l1/teams/new']}>
        <Routes>
          <Route path="/leagues/:id/teams/new" element={<CreateTeamForm />} />
          <Route path="/leagues/:id/teams" element={<div>listado de equipos</div>} />
        </Routes>
      </MemoryRouter>,
    );

    await userEvent.type(screen.getByLabelText('Nombre'), 'Ingeniería FC');
    await userEvent.type(screen.getByLabelText('Colores'), 'azul/blanco');
    await userEvent.click(screen.getByRole('button', { name: /registrar equipo/i }));

    expect(await screen.findByText('listado de equipos')).toBeInTheDocument();

    const post = fetchMock.mock.calls.find(([, init]) => init?.method === 'POST');
    expect(post).toBeTruthy();
    expect(JSON.parse(String((post?.[1] as RequestInit).body))).toEqual({
      name: 'Ingeniería FC',
      crest_url: null,
      colors: 'azul/blanco',
    });
  });
});
