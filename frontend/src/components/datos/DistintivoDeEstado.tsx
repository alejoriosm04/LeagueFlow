/**
 * Estado de un partido — FR-010, FR-028.
 * Contrato: specs/012-identidad-visual/contracts/ui-contracts.md §2
 *
 * El texto es obligatorio; el color es redundante. Quitar el color no debe
 * quitar la información.
 */

import type { MatchStatus } from '../../features/matches/api';
import estilos from './DistintivoDeEstado.module.css';

export type EstadoDePartido = MatchStatus;

export const etiquetaDeEstado: Record<EstadoDePartido, string> = {
  scheduled: 'Programado',
  in_progress: 'En curso',
  finished: 'Finalizado',
  cancelled: 'Cancelado',
};

interface DistintivoDeEstadoProps {
  estado: EstadoDePartido;
}

export function DistintivoDeEstado({ estado }: DistintivoDeEstadoProps) {
  return (
    <span className={`${estilos.distintivo} ${estilos[estado]}`}>
      {etiquetaDeEstado[estado]}
    </span>
  );
}
