/**
 * Botón con jerarquía y bloqueo de reenvío — FR-007, FR-018.
 * Contrato: specs/012-identidad-visual/contracts/ui-contracts.md §2
 *
 * `enviando` es el mecanismo ÚNICO de bloqueo de reenvío: deshabilita, marca
 * aria-busy y muestra "Enviando…". Ninguna pantalla implementa el suyo.
 */

import type { ButtonHTMLAttributes, ReactNode } from 'react';
import estilos from './Boton.module.css';

interface BotonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: 'primario' | 'secundario' | 'destructivo';
  enviando?: boolean;
  children: ReactNode;
}

export function Boton({
  variante = 'primario',
  enviando = false,
  children,
  disabled,
  className,
  ...resto
}: BotonProps) {
  return (
    <button
      {...resto}
      className={`${estilos.boton} ${estilos[variante]} ${className ?? ''}`}
      disabled={disabled || enviando}
      aria-busy={enviando || undefined}
    >
      {enviando ? 'Enviando…' : children}
    </button>
  );
}
