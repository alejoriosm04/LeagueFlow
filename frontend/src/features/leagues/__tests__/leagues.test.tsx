import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
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
        '/leagues?page=1&page_size=20': {
          status: 200,
          body: { items: [], page: 1, page_size: 20, total: 0 },
        },
      }),
    );

    render(
      <MemoryRouter>
        <LeaguesPage />
      </MemoryRouter>,
    );

    expect(await screen.findByText(/no hay ligas registradas/i)).toBeInTheDocument();
  });

  it('lista las ligas con enlace a su ficha', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/leagues?page=1&page_size=20': {
          status: 200,
          body: { items: [LIGA], page: 1, page_size: 20, total: 1 },
        },
      }),
    );

    render(
      <MemoryRouter>
        <LeaguesPage />
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
    expect(alerta).toHaveTextContent('Ya existe una liga con ese nombre y temporada.');
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
