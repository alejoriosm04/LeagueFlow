/**
 * Catálogo de datos — FR-008 a FR-012, FR-028.
 * spec 012-identidad-visual, Historia 2.
 */

import { fireEvent, render, screen, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { DestacadoDePodio } from '../datos/DestacadoDePodio';
import { DistintivoDeEstado } from '../datos/DistintivoDeEstado';
import { EscudoEquipo } from '../datos/EscudoEquipo';
import { FilaDeMarcador } from '../datos/FilaDeMarcador';
import { TablaDeDatos } from '../datos/TablaDeDatos';
import type { EstadoDePartido } from '../datos/DistintivoDeEstado';

describe('DistintivoDeEstado', () => {
  it.each([
    ['scheduled', 'Programado'],
    ['in_progress', 'En curso'],
    ['finished', 'Finalizado'],
    ['cancelled', 'Cancelado'],
  ])('identifica el estado %s por su texto, no solo por color', (estado, etiqueta) => {
    render(<DistintivoDeEstado estado={estado as EstadoDePartido} />);
    expect(screen.getByText(etiqueta)).toBeInTheDocument();
  });
});

describe('EscudoEquipo', () => {
  it('muestra el escudo cuando hay URL', () => {
    render(<EscudoEquipo nombre="EAFIT" crestUrl="https://ejemplo.test/e.png" />);
    expect(screen.getByRole('img', { name: 'Escudo de EAFIT' })).toBeInTheDocument();
  });

  it('cae a las iniciales cuando falta la URL', () => {
    render(<EscudoEquipo nombre="Deportivo Cali" crestUrl={null} />);
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
    expect(screen.getByText('DC')).toBeInTheDocument();
  });

  it('cae a las iniciales cuando la URL existe pero no carga', () => {
    render(<EscudoEquipo nombre="Deportivo Cali" crestUrl="https://ejemplo.test/roto.png" />);
    fireEvent.error(screen.getByRole('img'));
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
    expect(screen.getByText('DC')).toBeInTheDocument();
  });
});

describe('DestacadoDePodio', () => {
  it.each([
    [1, '🥇 1.º'],
    [2, '🥈 2.º'],
    [3, '🥉 3.º'],
  ])('marca la posición %i con texto además de medalla', (posicion, esperado) => {
    const { container } = render(<DestacadoDePodio posicion={posicion} />);
    expect(container.textContent).toBe(esperado);
  });

  it('deja plana cualquier posición fuera del podio', () => {
    const { container } = render(<DestacadoDePodio posicion={4} />);
    expect(container.textContent).toBe('4.º');
  });
});

describe('FilaDeMarcador', () => {
  // Nombres de dos palabras a propósito: si el nombre fuera de una sola, sus
  // iniciales coincidirían con el propio nombre y la consulta por texto sería
  // ambigua entre el sustituto del escudo y la etiqueta del equipo.
  const equipos = {
    local: { nombre: 'EAFIT Verde', crestUrl: null },
    visitante: { nombre: 'CES Azul', crestUrl: null },
  };

  it('usa el formato "LOCAL 3 — 1 VISITANTE"', () => {
    render(
      <FilaDeMarcador {...equipos} golesLocal={3} golesVisitante={1} estado="finished" />,
    );
    expect(screen.getByText('3 — 1')).toBeInTheDocument();
    expect(screen.getByText('EAFIT Verde')).toBeInTheDocument();
    expect(screen.getByText('CES Azul')).toBeInTheDocument();
  });

  it('muestra "vs" cuando el partido no tiene resultado', () => {
    render(
      <FilaDeMarcador {...equipos} golesLocal={null} golesVisitante={null} estado="scheduled" />,
    );
    expect(screen.getByText('vs')).toBeInTheDocument();
    expect(screen.getByText('Programado')).toBeInTheDocument();
  });

  it('enlaza al detalle cuando recibe href', () => {
    render(
      <MemoryRouter>
        <FilaDeMarcador {...equipos} golesLocal={2} golesVisitante={2} estado="finished" href="/matches/m1" />
      </MemoryRouter>,
    );
    expect(screen.getByRole('link')).toHaveAttribute('href', '/matches/m1');
  });
});

describe('TablaDeDatos', () => {
  interface Fila {
    id: string;
    equipo: string;
    puntos: number;
  }
  const filas: Fila[] = [
    { id: 'a', equipo: 'Alfa', puntos: 9 },
    { id: 'b', equipo: 'Bravo', puntos: 4 },
  ];
  const columnas = [
    { clave: 'equipo', encabezado: 'Equipo', celda: (f: Fila) => f.equipo },
    { clave: 'puntos', encabezado: 'Pts', numerica: true, celda: (f: Fila) => f.puntos },
  ];

  function renderTabla() {
    return render(
      <TablaDeDatos
        columnas={columnas}
        filas={filas}
        claveDeFila={(f) => f.id}
        descripcion="Clasificación de prueba"
      />,
    );
  }

  it('expone encabezados de columna accesibles', () => {
    renderTabla();
    expect(screen.getAllByRole('columnheader').map((c) => c.textContent)).toEqual(['Equipo', 'Pts']);
  });

  it('alinea a la derecha las columnas numéricas', () => {
    const { container } = renderTabla();
    const encabezadoPuntos = screen.getByRole('columnheader', { name: 'Pts' });
    const encabezadoEquipo = screen.getByRole('columnheader', { name: 'Equipo' });
    // La clase de alineación numérica se aplica a la columna de puntos y no a
    // la de texto (FR-008). Se comprueba por clase porque jsdom no calcula
    // el CSS de los módulos.
    expect(encabezadoPuntos.className).not.toBe('');
    expect(encabezadoPuntos.className).not.toBe(encabezadoEquipo.className);
    expect(container.querySelector('caption')).toHaveTextContent('Clasificación de prueba');
  });

  it('hace el contenedor desplazable alcanzable con teclado (FR-030)', () => {
    renderTabla();
    const region = screen.getByRole('region', { name: 'Clasificación de prueba' });
    expect(region).toHaveAttribute('tabindex', '0');
  });

  it('renderiza una fila por elemento', () => {
    renderTabla();
    const filasRenderizadas = screen.getAllByRole('row').slice(1);
    expect(filasRenderizadas).toHaveLength(2);
    expect(within(filasRenderizadas[0]).getAllByRole('cell')[0]).toHaveTextContent('Alfa');
  });
});
