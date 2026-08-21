/**
 * Portada del producto — FR-034, FR-035, FR-046, SC-011, SC-014.
 * spec 012-identidad-visual, Historia 6.
 *
 * La portada no consume contratos nuevos: solo `/auth/me` (estado de sesión)
 * y el listado de ligas ya publicado por `specs/002` (selector de ligas).
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes, useParams } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { Portada } from '../Portada';
import { AuthProvider } from '../../auth/AuthContext';
import { secciones } from '../../../components/layout/secciones';

const LIGAS = [
  { id: 'l1', name: 'Liga Universitaria', season: '2026', description: null },
  { id: 'l2', name: 'Copa Primavera', season: '2026', description: null },
];

function mockFetch(
  usuario: { username: string; role: string } | null,
  opciones: { ligas?: typeof LIGAS | 'error' } = {},
) {
  const ligas = opciones.ligas ?? LIGAS;
  return vi.fn(async (url: RequestInfo | URL) => {
    const ruta = String(url).replace(/^.*\/api\/v1/, '');
    if (ruta === '/auth/me') {
      return new Response(JSON.stringify({ user: usuario }), { status: 200 });
    }
    if (ruta.startsWith('/leagues')) {
      if (ligas === 'error') {
        return new Response(
          JSON.stringify({ error: { code: 'server_error', message: 'boom', field: null } }),
          { status: 500 },
        );
      }
      return new Response(
        JSON.stringify({ items: ligas, page: 1, page_size: 20, total: ligas.length }),
        { status: 200 },
      );
    }
    return new Response(JSON.stringify({ user: null }), { status: 200 });
  });
}

function renderPortada(
  usuario: { username: string; role: string } | null = null,
  opciones: { ligas?: typeof LIGAS | 'error' } = {},
) {
  vi.stubGlobal('fetch', mockFetch(usuario, opciones));
  return render(
    <MemoryRouter>
      <AuthProvider>
        <Portada />
      </AuthProvider>
    </MemoryRouter>,
  );
}

beforeEach(() => vi.restoreAllMocks());

describe('portada (FR-034)', () => {
  it('presenta la marca y la propuesta de valor', async () => {
    renderPortada();

    expect(await screen.findByRole('heading', { level: 1, name: 'LeagueFlow' })).toBeInTheDocument();
    expect(screen.getByText(/clasificación que se calcula sola/i)).toBeInTheDocument();
  });

  it('sin sesión, la acción principal lleva a iniciar sesión', async () => {
    renderPortada();

    const accion = await screen.findByRole('link', { name: 'Iniciar sesión' });
    expect(accion).toHaveAttribute('href', '/login');
    expect(screen.queryByRole('link', { name: 'Ver mis ligas' })).not.toBeInTheDocument();
  });

  it('con sesión, la acción principal lleva a las ligas y saluda al usuario', async () => {
    renderPortada({ username: 'jonathan', role: 'organizador' });

    const accion = await screen.findByRole('link', { name: 'Ver mis ligas' });
    expect(accion).toHaveAttribute('href', '/leagues');
    expect(screen.getByText('jonathan')).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'Iniciar sesión' })).not.toBeInTheDocument();
  });

  it('presenta una tarjeta por sección del producto, desde la fuente única', async () => {
    renderPortada();

    await screen.findByRole('heading', { level: 1, name: 'LeagueFlow' });
    for (const seccion of secciones) {
      expect(screen.getByRole('heading', { level: 3, name: seccion.etiqueta })).toBeInTheDocument();
    }
  });

  it('marca como próximas las secciones aún no entregadas, con texto y no solo con color', async () => {
    renderPortada();

    await screen.findByRole('heading', { level: 1, name: 'LeagueFlow' });
    const pendientes = secciones.filter((seccion) => seccion.pendiente);
    expect(screen.getAllByText('Próximamente')).toHaveLength(pendientes.length);
  });
});

function DestinoDeLiga() {
  const { id } = useParams();
  return <p>Detalle de la liga {id}</p>;
}

describe('selector de ligas (FR-046, SC-014)', () => {
  it('lista las ligas reales y navega en una sola interacción', async () => {
    const usuario = userEvent.setup();
    vi.stubGlobal('fetch', mockFetch(null));
    render(
      <MemoryRouter initialEntries={['/']}>
        <AuthProvider>
          <Routes>
            <Route path="/" element={<Portada />} />
            <Route path="/leagues/:id" element={<DestinoDeLiga />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>,
    );

    const boton = await screen.findByRole('button', { name: /Liga Universitaria/ });
    expect(screen.getByRole('button', { name: /Copa Primavera/ })).toBeInTheDocument();

    await usuario.click(boton);

    expect(await screen.findByText('Detalle de la liga l1')).toBeInTheDocument();
  });

  it('sin ligas registradas, ofrece el estado vacío en vez de una lista rota', async () => {
    renderPortada(null, { ligas: [] });

    expect(await screen.findByText('Aún no hay ligas registradas.')).toBeInTheDocument();
  });

  it('si la liga falla, muestra el error en español y permite reintentar', async () => {
    renderPortada(null, { ligas: 'error' });

    expect(await screen.findByRole('alert')).toHaveTextContent(/./);
    expect(screen.getByRole('button', { name: 'Reintentar' })).toBeInTheDocument();
  });
});
