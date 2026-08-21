/**
 * Liga en contexto e inercia de la navegación sin liga — FR-002, FR-006.
 * spec 012-identidad-visual, Historia 1.
 */

import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AppShell } from '../layout/AppShell';
import { AuthProvider } from '../../features/auth/AuthContext';

const LIGA = { id: 'l1', name: 'Liga Universitaria', season: '2026', description: null };

function mockFetch(ligaOk = true) {
  return vi.fn(async (url: RequestInfo | URL) => {
    const ruta = String(url).replace(/^.*\/api\/v1/, '');
    if (ruta === '/auth/me') return new Response(JSON.stringify({ user: null }), { status: 200 });
    if (ruta === '/matches/m1') {
      return new Response(JSON.stringify({ id: 'm1', league_id: 'l1' }), { status: 200 });
    }
    if (ruta.startsWith('/leagues/') && ligaOk) {
      return new Response(JSON.stringify(LIGA), { status: 200 });
    }
    return new Response(
      JSON.stringify({ error: { code: 'not_found', message: 'x', field: null } }),
      { status: 404 },
    );
  });
}

function renderEn(ruta: string, ligaOk = true) {
  vi.stubGlobal('fetch', mockFetch(ligaOk));
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

beforeEach(() => vi.restoreAllMocks());

describe('liga en contexto', () => {
  it('muestra el nombre de la liga dentro de /leagues/:id', async () => {
    renderEn('/leagues/l1/teams');

    expect(await screen.findByText('Liga Universitaria')).toBeInTheDocument();
  });

  it('resuelve la liga del partido en /matches/:matchId, que no la lleva en la ruta', async () => {
    renderEn('/matches/m1');

    expect(await screen.findByText('Liga Universitaria')).toBeInTheDocument();
  });

  it.each(['/', '/login', '/leagues', '/leagues/new'])(
    'muestra "Sin liga seleccionada" en %s',
    async (ruta) => {
      renderEn(ruta);

      expect(await screen.findByText('Sin liga seleccionada')).toBeInTheDocument();
    },
  );

  it('sin liga no ofrece secciones, ni siquiera deshabilitadas, y sí la salida a las ligas', async () => {
    renderEn('/login');

    await screen.findByText('Sin liga seleccionada');
    const nav = screen.getByRole('navigation', { name: 'Secciones' });

    // FR-006 enmendado: la lista de secciones no se pinta en absoluto. Ni
    // enlace, ni texto suelto, ni elemento deshabilitado ocupando su sitio.
    for (const etiqueta of ['Dashboard', 'Equipos', 'Jugadores', 'Partidos', 'Tabla', 'Estadísticas']) {
      expect(screen.queryByRole('link', { name: etiqueta })).not.toBeInTheDocument();
      expect(nav).not.toHaveTextContent(etiqueta);
    }
    // SC-011: cero elementos deshabilitados en la navegación.
    expect(nav.querySelectorAll('[aria-disabled="true"]')).toHaveLength(0);
    // Y se dice qué hacer, con salida al listado de ligas (FR-006).
    expect(nav).toHaveTextContent('Selecciona una liga para navegar sus secciones.');
    expect(screen.getByRole('link', { name: 'Ver ligas' })).toBeInTheDocument();
  });

  it('informa que la liga no existe sin romper la navegación', async () => {
    renderEn('/leagues/inexistente/teams', false);

    expect(await screen.findByText('Liga no encontrada')).toBeInTheDocument();
    expect(screen.getByRole('navigation', { name: 'Secciones' })).toBeInTheDocument();
  });
});
