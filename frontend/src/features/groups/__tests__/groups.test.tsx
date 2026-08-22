import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../auth/AuthContext';
import { GroupsPage } from '../GroupsPage';

const ORGANIZADOR = { id: 'u1', username: 'org', role: 'organizador', status: 'active' };

const GRUPO = {
  id: 'g1',
  league_id: 'l1',
  name: 'Grupo A',
  position: null,
  created_at: '2026-08-22T00:00:00Z',
  teams: [{ team_id: 't1', name: 'Ingeniería FC', status: 'active' }],
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

function renderGroupsPage() {
  return render(
    <MemoryRouter initialEntries={['/leagues/l1/groups']}>
      <AuthProvider>
        <Routes>
          <Route path="/leagues/:id/groups" element={<GroupsPage />} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

beforeEach(() => vi.restoreAllMocks());

describe('GroupsPage', () => {
  it('muestra estado vacío cuando la liga no tiene grupos', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/me': { status: 200, body: { user: null } },
        '/leagues/l1/groups': { status: 200, body: { items: [] } },
        '/leagues/l1/teams?include_inactive=false&page=1&page_size=20': {
          status: 200,
          body: { items: [], page: 1, page_size: 20, total: 0 },
        },
      }),
    );

    renderGroupsPage();

    expect(await screen.findByText(/no hay grupos en esta liga/i)).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /crear el primer grupo/i })).not.toBeInTheDocument();
  });

  it('ofrece crear grupo solo al organizador', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/me': { status: 200, body: { user: ORGANIZADOR } },
        '/leagues/l1/groups': { status: 200, body: { items: [] } },
        '/leagues/l1/teams?include_inactive=false&page=1&page_size=20': {
          status: 200,
          body: { items: [], page: 1, page_size: 20, total: 0 },
        },
      }),
    );

    renderGroupsPage();

    expect(await screen.findByRole('link', { name: /crear el primer grupo/i })).toBeInTheDocument();
  });

  it('muestra la composición de los grupos', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/me': { status: 200, body: { user: null } },
        '/leagues/l1/groups': { status: 200, body: { items: [GRUPO] } },
        '/leagues/l1/teams?include_inactive=false&page=1&page_size=20': {
          status: 200,
          body: { items: [{ id: 't1', name: 'Ingeniería FC' }], page: 1, page_size: 20, total: 1 },
        },
      }),
    );

    renderGroupsPage();

    expect(await screen.findByText('Grupo A')).toBeInTheDocument();
    expect(screen.getByText('Ingeniería FC')).toBeInTheDocument();
  });
});
