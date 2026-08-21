/**
 * Indicador de la liga en contexto en la cabecera — FR-002, FR-006.
 *
 * Mientras la liga carga muestra el estado neutro en vez de parpadear con un
 * valor incorrecto (research.md §5).
 */

import { inicialesDe } from '../../lib/formato';
import { useLigaEnContexto } from './useLigaEnContexto';
import estilos from './IndicadorDeLiga.module.css';

export function IndicadorDeLiga() {
  const liga = useLigaEnContexto();

  if (liga.estado === 'resuelta') {
    return (
      <p className={estilos.contenedor}>
        <span className={estilos.sigla} aria-hidden="true">
          {inicialesDe(liga.nombre)}
        </span>
        <span className={estilos.etiqueta}>Liga</span>
        <span className={estilos.nombre} title={liga.nombre}>
          {liga.nombre}
        </span>
      </p>
    );
  }

  if (liga.estado === 'cargando') {
    return (
      <p className={estilos.contenedor}>
        <span className={estilos.neutro}>Cargando la liga…</span>
      </p>
    );
  }

  if (liga.estado === 'no-encontrada') {
    return (
      <p className={estilos.contenedor}>
        <span className={estilos.neutro}>Liga no encontrada</span>
      </p>
    );
  }

  return (
    <p className={estilos.contenedor}>
      <span className={estilos.neutro}>Sin liga seleccionada</span>
    </p>
  );
}
