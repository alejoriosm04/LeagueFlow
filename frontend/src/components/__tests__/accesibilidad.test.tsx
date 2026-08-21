/**
 * Accesibilidad del catálogo — FR-024, FR-025, FR-026, FR-028.
 * spec 012-identidad-visual, Historia 4.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../features/auth/AuthContext';
import { AppShell } from '../layout/AppShell';
import { Boton } from '../formulario/Boton';
import { CampoDeFormulario } from '../formulario/CampoDeFormulario';
import { DistintivoDeEstado } from '../datos/DistintivoDeEstado';
import { DestacadoDePodio } from '../datos/DestacadoDePodio';
import { EstadoError } from '../estado/EstadoError';

function FormularioDePrueba({ alEnviar = vi.fn() }) {
  return (
    <form onSubmit={alEnviar}>
      <CampoDeFormulario id="nombre" etiqueta="Nombre" requerido>
        <input />
      </CampoDeFormulario>
      <CampoDeFormulario id="dorsal" etiqueta="Dorsal" ayuda="Entre 1 y 99.">
        <input type="number" />
      </CampoDeFormulario>
      <Boton type="submit">Guardar</Boton>
    </form>
  );
}

describe('recorrido por teclado (FR-025)', () => {
  it('alcanza todos los controles del formulario con Tab, en orden', async () => {
    render(<FormularioDePrueba />);

    await userEvent.tab();
    expect(screen.getByLabelText('Nombre')).toHaveFocus();

    await userEvent.tab();
    expect(screen.getByLabelText('Dorsal')).toHaveFocus();

    await userEvent.tab();
    expect(screen.getByRole('button', { name: 'Guardar' })).toHaveFocus();
  });

  it('activa el botón de envío con el teclado', async () => {
    const alEnviar = vi.fn((e: React.FormEvent) => e.preventDefault());
    render(<FormularioDePrueba alEnviar={alEnviar} />);

    await userEvent.tab();
    await userEvent.tab();
    await userEvent.tab();
    await userEvent.keyboard('{Enter}');

    expect(alEnviar).toHaveBeenCalled();
  });

  it('salta los controles deshabilitados durante un envío en curso', async () => {
    render(
      <form>
        <CampoDeFormulario id="nombre" etiqueta="Nombre">
          <input />
        </CampoDeFormulario>
        <Boton type="submit" enviando>
          Guardar
        </Boton>
      </form>,
    );

    await userEvent.tab();
    expect(screen.getByLabelText('Nombre')).toHaveFocus();
    await userEvent.tab();
    expect(screen.getByRole('button')).not.toHaveFocus();
  });
});

describe('etiquetas asociadas (FR-026)', () => {
  it('todo campo del catálogo tiene su etiqueta', () => {
    render(<FormularioDePrueba />);
    // Si algún control quedara sin etiqueta asociada, estas consultas fallan.
    expect(screen.getByLabelText('Nombre')).toBeInTheDocument();
    expect(screen.getByLabelText('Dorsal')).toBeInTheDocument();
  });
});

describe('nada depende solo del color (FR-028)', () => {
  it('el estado del partido lleva su texto', () => {
    render(<DistintivoDeEstado estado="cancelled" />);
    expect(screen.getByText('Cancelado')).toBeInTheDocument();
  });

  it('el podio lleva su texto', () => {
    const { container } = render(<DestacadoDePodio posicion={2} />);
    expect(container.textContent).toContain('2.º');
  });

  it('el error lleva su rótulo', () => {
    render(<EstadoError mensaje="Algo falló." />);
    expect(screen.getByRole('alert')).toHaveTextContent('Error');
  });

  it('la sección activa se marca con aria-current, no solo con color', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: RequestInfo | URL) => {
        const ruta = String(url).replace(/^.*\/api\/v1/, '');
        if (ruta === '/auth/me') return new Response(JSON.stringify({ user: null }), { status: 200 });
        return new Response(
          JSON.stringify({ id: 'l1', name: 'Liga', season: '2026', description: null }),
          { status: 200 },
        );
      }),
    );

    render(
      <MemoryRouter initialEntries={['/leagues/l1/standings']}>
        <AuthProvider>
          <AppShell>
            <h1>Contenido</h1>
          </AppShell>
        </AuthProvider>
      </MemoryRouter>,
    );

    const activa = await screen.findByRole('link', { name: 'Tabla' });
    expect(activa).toHaveAttribute('aria-current', 'page');
  });
});

describe('estructura semántica (FR-027)', () => {
  it('el shell expone banner, navegación y main', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => new Response(JSON.stringify({ user: null }), { status: 200 })),
    );

    render(
      <MemoryRouter initialEntries={['/login']}>
        <AuthProvider>
          <AppShell>
            <h1>Iniciar sesión</h1>
          </AppShell>
        </AuthProvider>
      </MemoryRouter>,
    );

    expect(await screen.findByRole('banner')).toBeInTheDocument();
    expect(screen.getByRole('navigation', { name: 'Secciones' })).toBeInTheDocument();
    expect(screen.getByRole('main')).toBeInTheDocument();
    expect(screen.getAllByRole('heading', { level: 1 })).toHaveLength(1);
  });
});
