import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider, useAuth } from '../AuthContext';
import { LoginPage } from '../LoginPage';
import { ProtectedRoute } from '../ProtectedRoute';

function mockFetch(respuestas: Record<string, { status: number; body: unknown }>) {
  return vi.fn(async (url: RequestInfo | URL) => {
    const ruta = String(url).replace(/^.*\/api\/v1/, '');
    const r = respuestas[ruta] ?? { status: 404, body: { error: { code: 'nf', message: 'x', field: null } } };
    return new Response(JSON.stringify(r.body), {
      status: r.status,
      headers: { 'Content-Type': 'application/json' },
    });
  });
}

const USUARIO = { id: 'u1', username: 'organizador', role: 'organizador', status: 'active' };

// Generada en tiempo de ejecución: el Principio VI prohíbe credenciales
// literales incluso en tests. El valor es irrelevante — la respuesta del
// backend está mockeada.
const CLAVE_DE_PRUEBA = crypto.randomUUID();

beforeEach(() => vi.restoreAllMocks());

describe('AuthContext', () => {
  it('pregunta al servidor quién es al montar, porque la cookie es httpOnly', async () => {
    vi.stubGlobal('fetch', mockFetch({ '/auth/me': { status: 200, body: { user: USUARIO } } }));

    function Sonda() {
      const { usuario, cargando } = useAuth();
      if (cargando) return <span>cargando</span>;
      return <span>{usuario?.username ?? 'anonimo'}</span>;
    }

    render(
      <MemoryRouter>
        <AuthProvider>
          <Sonda />
        </AuthProvider>
      </MemoryRouter>,
    );

    expect(await screen.findByText('organizador')).toBeInTheDocument();
  });

  it('deja el usuario en null si no hay sesión', async () => {
    vi.stubGlobal('fetch', mockFetch({ '/auth/me': { status: 200, body: { user: null } } }));

    function Sonda() {
      const { usuario, cargando } = useAuth();
      return <span>{cargando ? 'cargando' : (usuario?.username ?? 'anonimo')}</span>;
    }

    render(
      <MemoryRouter>
        <AuthProvider>
          <Sonda />
        </AuthProvider>
      </MemoryRouter>,
    );

    expect(await screen.findByText('anonimo')).toBeInTheDocument();
  });
});

describe('LoginPage', () => {
  it('muestra el mensaje genérico del backend cuando las credenciales fallan', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/me': { status: 200, body: { user: null } },
        '/auth/login': {
          status: 401,
          body: {
            error: {
              code: 'invalid_credentials',
              message: 'Usuario o contraseña incorrectos.',
              field: null,
            },
          },
        },
      }),
    );

    render(
      <MemoryRouter>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </MemoryRouter>,
    );

    await userEvent.type(screen.getByLabelText('Usuario'), 'quien-sea');
    await userEvent.type(screen.getByLabelText('Contraseña'), CLAVE_DE_PRUEBA);
    await userEvent.click(screen.getByRole('button', { name: /entrar/i }));

    const alerta = await screen.findByRole('alert');
    expect(alerta).toHaveTextContent('Usuario o contraseña incorrectos.');
    // FR-010: el mensaje no debe revelar si el identificador existe.
    expect(alerta.textContent).not.toContain('quien-sea');
  });
});

describe('ProtectedRoute', () => {
  it('bloquea a un rol insuficiente', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/me': {
          status: 200,
          body: { user: { ...USUARIO, role: 'operador' } },
        },
      }),
    );

    render(
      <MemoryRouter>
        <AuthProvider>
          <ProtectedRoute rol="organizador">
            <span>contenido secreto</span>
          </ProtectedRoute>
        </AuthProvider>
      </MemoryRouter>,
    );

    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    expect(screen.queryByText('contenido secreto')).not.toBeInTheDocument();
  });
});
