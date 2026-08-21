/**
 * Navegación colapsable — FR-005.
 * spec 012-identidad-visual, Historia 5.
 *
 * jsdom no aplica media queries, así que el botón y el <nav> están siempre en
 * el DOM: lo que se prueba aquí es el contrato de accesibilidad del colapso
 * (aria-expanded, aria-controls, operable con teclado), no el ancho al que
 * ocurre, que es responsabilidad del CSS y se verifica a mano.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../../features/auth/AuthContext';
import { AppShell } from '../layout/AppShell';

function renderShell() {
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: RequestInfo | URL) => {
      const ruta = String(url).replace(/^.*\/api\/v1/, '');
      if (ruta === '/auth/me') return new Response(JSON.stringify({ user: null }), { status: 200 });
      return new Response(
        JSON.stringify({ id: 'l1', name: 'Liga Universitaria', season: '2026', description: null }),
        { status: 200 },
      );
    }),
  );
  return render(
    <MemoryRouter initialEntries={['/leagues/l1/teams']}>
      <AuthProvider>
        <AppShell>
          <h1>Contenido</h1>
        </AppShell>
      </AuthProvider>
    </MemoryRouter>,
  );
}

beforeEach(() => vi.restoreAllMocks());

describe('navegación colapsable', () => {
  it('ofrece un botón de menú que declara qué controla', async () => {
    renderShell();
    const boton = await screen.findByRole('button', { name: 'Menú' });
    expect(boton).toHaveAttribute('aria-controls', 'navegacion-secciones');
    expect(screen.getByRole('navigation', { name: 'Secciones' })).toHaveAttribute(
      'id',
      'navegacion-secciones',
    );
  });

  it('alterna aria-expanded al pulsarlo', async () => {
    renderShell();
    const boton = await screen.findByRole('button', { name: 'Menú' });
    expect(boton).toHaveAttribute('aria-expanded', 'false');

    await userEvent.click(boton);
    expect(boton).toHaveAttribute('aria-expanded', 'true');

    await userEvent.click(boton);
    expect(boton).toHaveAttribute('aria-expanded', 'false');
  });

  it('es operable solo con teclado', async () => {
    renderShell();
    const boton = await screen.findByRole('button', { name: 'Menú' });

    boton.focus();
    expect(boton).toHaveFocus();
    await userEvent.keyboard('{Enter}');
    expect(boton).toHaveAttribute('aria-expanded', 'true');

    await userEvent.keyboard(' ');
    expect(boton).toHaveAttribute('aria-expanded', 'false');
  });

  it('mantiene las seis secciones alcanzables al abrirlo', async () => {
    renderShell();
    const boton = await screen.findByRole('button', { name: 'Menú' });
    await userEvent.click(boton);

    const nav = screen.getByRole('navigation', { name: 'Secciones' });
    for (const etiqueta of ['Dashboard', 'Equipos', 'Jugadores', 'Partidos', 'Tabla', 'Estadísticas']) {
      expect(nav).toHaveTextContent(etiqueta);
    }
  });
});
