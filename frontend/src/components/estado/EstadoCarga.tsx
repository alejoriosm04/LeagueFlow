/**
 * Estado de carga — FR-013.
 * Contrato: specs/012-identidad-visual/contracts/ui-contracts.md §3
 */

import estilos from './estados.module.css';

interface EstadoCargaProps {
  /** "la clasificación", "los partidos"… */
  recurso: string;
}

export function EstadoCarga({ recurso }: EstadoCargaProps) {
  return (
    <p className={`${estilos.bloque} ${estilos.carga}`} role="status" aria-live="polite">
      Cargando {recurso}…
    </p>
  );
}
