/**
 * Catálogo de formulario — FR-017, FR-018, FR-026.
 * spec 012-identidad-visual, Historia 3.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { Boton } from '../formulario/Boton';
import { CampoDeFormulario } from '../formulario/CampoDeFormulario';

describe('CampoDeFormulario', () => {
  it('asocia la etiqueta al control (FR-026)', () => {
    render(
      <CampoDeFormulario id="nombre" etiqueta="Nombre">
        <input />
      </CampoDeFormulario>,
    );
    expect(screen.getByLabelText('Nombre')).toBeInTheDocument();
  });

  it('no mete el asterisco de obligatorio en el nombre accesible', () => {
    render(
      <CampoDeFormulario id="nombre" etiqueta="Nombre" requerido>
        <input />
      </CampoDeFormulario>,
    );
    // Si el asterisco contaminara la etiqueta, esta consulta fallaría.
    expect(screen.getByLabelText('Nombre')).toBeInTheDocument();
  });

  it('liga la ayuda con aria-describedby', () => {
    render(
      <CampoDeFormulario id="dorsal" etiqueta="Dorsal" ayuda="Entre 1 y 99.">
        <input />
      </CampoDeFormulario>,
    );
    const control = screen.getByLabelText('Dorsal');
    expect(control.getAttribute('aria-describedby')).toContain('dorsal-ayuda');
    expect(screen.getByText('Entre 1 y 99.')).toBeInTheDocument();
  });

  it('muestra el error junto al campo y lo marca inválido (FR-017)', () => {
    render(
      <CampoDeFormulario id="nombre" etiqueta="Nombre" error="Ya hay un equipo con ese nombre.">
        <input />
      </CampoDeFormulario>,
    );
    const control = screen.getByLabelText('Nombre');
    expect(control).toHaveAttribute('aria-invalid', 'true');
    expect(control.getAttribute('aria-describedby')).toContain('nombre-error');
    expect(screen.getByRole('alert')).toHaveTextContent('Ya hay un equipo con ese nombre.');
  });

  it('no marca inválido cuando no hay error', () => {
    render(
      <CampoDeFormulario id="nombre" etiqueta="Nombre">
        <input />
      </CampoDeFormulario>,
    );
    expect(screen.getByLabelText('Nombre')).not.toHaveAttribute('aria-invalid');
  });
});

describe('Boton', () => {
  it('bloquea el reenvío mientras hay un envío en curso (FR-018)', async () => {
    const alPulsar = vi.fn();
    render(
      <Boton enviando onClick={alPulsar}>
        Registrar equipo
      </Boton>,
    );
    const boton = screen.getByRole('button');
    expect(boton).toBeDisabled();
    expect(boton).toHaveAttribute('aria-busy', 'true');
    expect(boton).toHaveTextContent('Enviando…');

    await userEvent.click(boton);
    expect(alPulsar).not.toHaveBeenCalled();
  });

  it('vuelve a estar disponible cuando el envío termina', () => {
    const { rerender } = render(<Boton enviando>Registrar equipo</Boton>);
    expect(screen.getByRole('button')).toBeDisabled();

    // Tanto si hubo éxito como si hubo error, el usuario no queda atrapado.
    rerender(<Boton enviando={false}>Registrar equipo</Boton>);
    const boton = screen.getByRole('button', { name: 'Registrar equipo' });
    expect(boton).toBeEnabled();
    expect(boton).not.toHaveAttribute('aria-busy');
  });

  it('ofrece las tres variantes de jerarquía con clases distintas', () => {
    const { rerender, container } = render(<Boton variante="primario">A</Boton>);
    const primario = container.querySelector('button')!.className;
    rerender(<Boton variante="secundario">A</Boton>);
    const secundario = container.querySelector('button')!.className;
    rerender(<Boton variante="destructivo">A</Boton>);
    const destructivo = container.querySelector('button')!.className;

    expect(new Set([primario, secundario, destructivo]).size).toBe(3);
  });
});
