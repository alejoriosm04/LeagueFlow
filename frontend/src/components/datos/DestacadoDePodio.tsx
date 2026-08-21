/**
 * Destacado de las posiciones de podio — FR-011, FR-028.
 * Contrato: specs/012-identidad-visual/contracts/ui-contracts.md §2
 *
 * Texto "1.º/2.º/3.º" más medalla. Con menos de tres equipos se destacan solo
 * las posiciones existentes: el componente decide por posición, así que una
 * liga de dos equipos nunca pinta un tercer puesto.
 */

import estilos from './DestacadoDePodio.module.css';

const medallas: Record<number, string> = { 1: '🥇', 2: '🥈', 3: '🥉' };

interface DestacadoDePodioProps {
  posicion: number;
}

export function DestacadoDePodio({ posicion }: DestacadoDePodioProps) {
  if (posicion < 1 || posicion > 3) {
    return <span className={estilos.plano}>{posicion}.º</span>;
  }

  return (
    <span className={estilos.podio}>
      <span aria-hidden="true">{medallas[posicion]}</span> {posicion}.º
    </span>
  );
}
