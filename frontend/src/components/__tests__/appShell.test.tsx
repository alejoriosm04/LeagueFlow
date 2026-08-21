/**
 * Estructura de aplicación — FR-001, FR-004, FR-027, SC-001.
 * spec 012-identidad-visual, Historia 1.
 */

import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AppShell } from '../layout/AppShell';
import { AuthProvider } from '../../features/auth/AuthContext';

const USUARIO = { id: 'u1', username: 'ana.gomez', role: 'organizador', status: 'active' };
const LIGA = { id: 'l1', name: 'Liga Universitaria', season: '2026', description: null };

function mockFetch(usuario: unknown = null) {
  return vi.fn(async (url: RequestInfo | URL) => {
    const ruta = String(url).replace(/^.*\/api\/v1/, '');
    if (ruta === '/auth/me') {
      return new Response(JSON.stringify({ user: usuario }), { status: 200 });
    }
    if (ruta === '/teams/t1') {
      return new Response(JSON.stringify({ id: 't1', league_id: 'l1', name: 'EAFIT' }), {
        status: 200,
      });
    }
    if (ruta.startsWith('/leagues/')) {
      return new Response(JSON.stringify(LIGA), { status: 200 });
    }
    return new Response(JSON.stringify({ error: { code: 'nf', message: 'x', field: null } }), {
      status: 404,
    });
  });
}

function renderEn(ruta: string, usuario: unknown = null) {
  vi.stubGlobal('fetch', mockFetch(usuario));
  return render(
    <MemoryRouter initialEntries={[ruta]}>
      <AuthProvider>
        <AppShell>
          <h1>Contenido</h1>
        </AppShell>
      </AuthProvider>
    </MemoryRouter>,
  );
}

/** Todas las secciones marcadas como activas en la pantalla actual. */
function seccionesActivas(): string[] {
  return screen
    .getAllByRole('link')
    .filter((el) => el.getAttribute('aria-current') === 'page')
    .map((el) => el.textContent ?? '');
}

beforeEach(() => vi.restoreAllMocks());

describe('AppShell', () => {
  it('muestra la misma cabecera y navegación en una ruta pública', async () => {
    renderEn('/leagues/l1/teams');

    expect(await screen.findByRole('banner')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'LEAGUEFLOW' })).toBeInTheDocument();
    expect(screen.getByRole('navigation', { name: 'Secciones' })).toBeInTheDocument();
    expect(screen.getByRole('main')).toBeInTheDocument();
  });

  it('muestra la misma cabecera y navegación en una ruta autenticada', async () => {
    renderEn('/leagues/l1/standings', USUARIO);

    expect(await screen.findByRole('banner')).toBeInTheDocument();
    expect(screen.getByRole('navigation', { name: 'Secciones' })).toBeInTheDocument();
  });

  it('ofrece las seis secciones del mockup', async () => {
    renderEn('/leagues/l1/teams');

    const nav = await screen.findByRole('navigation', { name: 'Secciones' });
    for (const etiqueta of ['Dashboard', 'Equipos', 'Jugadores', 'Partidos', 'Tabla', 'Estadísticas']) {
      expect(nav).toHaveTextContent(etiqueta);
    }
  });

  it('marca como máximo una sección activa, y en /leagues/:id/teams es Equipos y no Jugadores', async () => {
    renderEn('/leagues/l1/teams');
    await screen.findByRole('navigation', { name: 'Secciones' });

    // Equipos y Jugadores comparten destino: si la activación se dedujera de
    // la ruta, aquí habría dos aria-current a la vez (FR-004).
    expect(seccionesActivas()).toEqual(['Equipos']);
  });

  it('marca Jugadores, y solo Jugadores, en la ruta de jugadores de un equipo', async () => {
    renderEn('/teams/t1/players');
    // La liga se resuelve con el league_id del equipo, así que la navegación
    // sigue viva fuera de /leagues/:id.
    await screen.findByRole('link', { name: 'Jugadores' });

    expect(seccionesActivas()).toEqual(['Jugadores']);
  });

  it('no marca ninguna sección activa en una pantalla sin liga', async () => {
    renderEn('/login');
    await screen.findByRole('navigation', { name: 'Secciones' });

    expect(seccionesActivas()).toEqual([]);
  });

  it('muestra usuario y rol cuando hay sesión', async () => {
    renderEn('/leagues/l1/teams', USUARIO);

    expect(await screen.findByText('ana.gomez')).toBeInTheDocument();
    expect(screen.getByText('organizador')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Cerrar sesión' })).toBeInTheDocument();
  });

  it('ofrece iniciar sesión cuando no hay sesión', async () => {
    renderEn('/leagues/l1/teams');

    expect(await screen.findByRole('link', { name: 'Iniciar sesión' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Cerrar sesión' })).not.toBeInTheDocument();
  });

  it('expone un enlace para saltar al contenido', async () => {
    renderEn('/leagues/l1/teams');

    expect(await screen.findByRole('link', { name: 'Saltar al contenido' })).toBeInTheDocument();
  });
});
