import { render, screen, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../auth/AuthContext';
import { ProtectedRoute } from '../../auth/ProtectedRoute';
import { AuditLogPage } from '../AuditLogPage';

const ORGANIZADOR = { id: 'u1', username: 'organizador', role: 'organizador', status: 'active' };

const entrada = (id: string, extra: Record<string, unknown>) => ({
  id,
  method: 'POST',
  path: '/api/v1/leagues',
  status_code: 201,
  actor_id: 'u1',
  actor_username: 'organizador',
  created_at: '2026-08-20T10:00:00Z',
  ...extra,
});

const items = [
  entrada('a1', { created_at: '2026-08-20T12:00:00Z' }),
  entrada('a2', { method: 'POST', path: '/api/v1/auth/login', actor_id: null, actor_username: null, created_at: '2026-08-20T09:00:00Z' }),
];

function stubFetch({ vacio = false, error = false } = {}) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const path = new URL(String(input)).pathname.replace('/api/v1', '');
    if (path === '/auth/me') return Response.json({ user: ORGANIZADOR });
    if (path === '/admin/audit-log') {
      if (error) {
        return Response.json(
          { error: { code: 'internal_error', message: 'boom', field: null } },
          { status: 500 },
        );
      }
      return Response.json({
        items: vacio ? [] : items,
        page: 1,
        page_size: 20,
        total: vacio ? 0 : items.length,
      });
    }
    return Response.json({ error: { code: 'nf', message: 'No encontrado', field: null } }, { status: 404 });
  });
}

function renderPagina() {
  render(
    <MemoryRouter initialEntries={['/admin/audit-log']}>
      <AuthProvider>
        <ProtectedRoute rol="organizador">
          <AuditLogPage />
        </ProtectedRoute>
      </AuthProvider>
    </MemoryRouter>,
  );
}

beforeEach(() => vi.restoreAllMocks());

describe('historial de auditoría', () => {
  it('muestra las columnas y las filas devueltas por auditApi.listar()', async () => {
    vi.stubGlobal('fetch', stubFetch());
    renderPagina();
    expect(await screen.findByRole('heading', { name: /historial de auditoría/i })).toBeInTheDocument();
    await screen.findByRole('table');

    const encabezados = screen.getAllByRole('columnheader').map((c) => c.textContent);
    expect(encabezados).toEqual(['Fecha', 'Actor', 'Método', 'Destino', 'Resultado']);

    const filas = screen.getAllByRole('row').slice(1);
    expect(within(filas[0]).getAllByRole('cell')[3]).toHaveTextContent('/api/v1/leagues');
    // FR-004: el login sin actor determinable se muestra con texto explícito.
    expect(within(filas[1]).getAllByRole('cell')[1]).toHaveTextContent('Actor no determinable');
  });

  it('muestra un estado de carga mientras llega la respuesta', async () => {
    let resolverAudit: (respuesta: Response) => void = () => {};
    const respuestaAudit = new Promise<Response>((resolve) => {
      resolverAudit = resolve;
    });
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL) => {
        const path = new URL(String(input)).pathname.replace('/api/v1', '');
        if (path === '/auth/me') return Response.json({ user: ORGANIZADOR });
        if (path === '/admin/audit-log') return respuestaAudit;
        return Response.json({ error: { code: 'nf', message: 'No encontrado', field: null } }, { status: 404 });
      }),
    );
    renderPagina();
    // El "Cargando…" de ProtectedRoute (mientras resuelve /auth/me) desaparece
    // primero; el propio de AuditLogPage (role="status") es el que se afirma.
    expect(await screen.findByRole('status')).toHaveTextContent(/cargando/i);
    resolverAudit(Response.json({ items: [], page: 1, page_size: 20, total: 0 }));
  });

  it('muestra un error legible si la petición falla', async () => {
    vi.stubGlobal('fetch', stubFetch({ error: true }));
    renderPagina();
    expect(await screen.findByRole('alert')).toBeInTheDocument();
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });

  it('muestra un estado vacío cuando no hay operaciones registradas', async () => {
    vi.stubGlobal('fetch', stubFetch({ vacio: true }));
    renderPagina();
    expect(await screen.findByText(/todavía no hay operaciones registradas/i)).toBeInTheDocument();
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });

  it('ProtectedRoute bloquea a quien no tiene sesión', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => Response.json({ user: null })),
    );
    renderPagina();
    // Sin sesión, ProtectedRoute redirige a /login: no se llega a renderizar la página.
    await vi.waitFor(() => expect(screen.queryByRole('heading', { name: /historial/i })).not.toBeInTheDocument());
  });

  it('ProtectedRoute bloquea a quien no es organizador', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => Response.json({ user: { ...ORGANIZADOR, role: 'operador' } })),
    );
    renderPagina();
    expect(await screen.findByRole('alert')).toHaveTextContent(/no tienes permisos/i);
    expect(screen.queryByRole('heading', { name: /historial/i })).not.toBeInTheDocument();
  });
});
