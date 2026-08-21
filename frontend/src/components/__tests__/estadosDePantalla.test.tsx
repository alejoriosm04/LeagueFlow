/**
 * Estados de pantalla — FR-013 a FR-016, SC-002.
 * spec 012-identidad-visual, Historia 3.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { EstadoCarga } from '../estado/EstadoCarga';
import { EstadoError } from '../estado/EstadoError';
import { EstadoVacio } from '../estado/EstadoVacio';

describe('EstadoCarga', () => {
  it('se anuncia como estado en vivo y nombra el recurso', () => {
    render(<EstadoCarga recurso="la clasificación" />);
    const estado = screen.getByRole('status');
    expect(estado).toHaveTextContent('Cargando la clasificación…');
    expect(estado).toHaveAttribute('aria-live', 'polite');
  });
});

describe('EstadoVacio', () => {
  it('dice qué hacer a continuación', () => {
    render(
      <MemoryRouter>
        <EstadoVacio
          titulo="Aún no hay equipos registrados."
          descripcion="Registra el primer equipo para empezar a programar partidos."
        />
      </MemoryRouter>,
    );
    expect(screen.getByText('Aún no hay equipos registrados.')).toBeInTheDocument();
    expect(screen.getByText(/registra el primer equipo/i)).toBeInTheDocument();
  });

  it('ofrece la acción solo cuando se le pasa (FR-014)', () => {
    const { rerender } = render(
      <MemoryRouter>
        <EstadoVacio titulo="Vacío" descripcion="Sin permisos para actuar." />
      </MemoryRouter>,
    );
    // Sin acción: un espectador ve el estado, no un botón que no puede usar.
    expect(screen.queryByRole('link')).not.toBeInTheDocument();

    rerender(
      <MemoryRouter>
        <EstadoVacio
          titulo="Vacío"
          descripcion="Puedes actuar."
          accion={{ etiqueta: 'Registrar el primer equipo', href: '/leagues/l1/teams/new' }}
        />
      </MemoryRouter>,
    );
    expect(screen.getByRole('link', { name: 'Registrar el primer equipo' })).toHaveAttribute(
      'href',
      '/leagues/l1/teams/new',
    );
  });
});

describe('EstadoError', () => {
  it('se anuncia como alerta y muestra el mensaje ya traducido', () => {
    render(<EstadoError mensaje="No encontramos la liga que buscas." />);
    expect(screen.getByRole('alert')).toHaveTextContent('No encontramos la liga que buscas.');
  });

  it('se distingue por texto además de por color (FR-028)', () => {
    render(<EstadoError mensaje="Algo falló." />);
    expect(screen.getByRole('alert')).toHaveTextContent('Error');
  });

  it('ofrece reintentar cuando la pantalla puede repetir la consulta', async () => {
    const reintentar = vi.fn();
    render(<EstadoError mensaje="Algo falló." onReintentar={reintentar} />);
    await userEvent.click(screen.getByRole('button', { name: 'Reintentar' }));
    expect(reintentar).toHaveBeenCalledOnce();
  });

  it('no ofrece reintentar cuando no se le pasa la acción', () => {
    render(<EstadoError mensaje="Algo falló." />);
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });
});
