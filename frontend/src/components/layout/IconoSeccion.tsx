/**
 * Marca visual no textual de cada sección — FR-041.
 *
 * Cada sección lleva su propio glifo, no solo su etiqueta: así la
 * identificación no depende únicamente del texto ni del color. Los trazos
 * usan `currentColor`, así que heredan el color del enlace que los contiene
 * y no necesitan su propia regla para el estado activo.
 *
 * Referencia visual: maqueta `LeagueFlow Wow` (Claude Design), aportada por
 * el equipo — ver spec.md, Assumption "Maqueta de referencia del marco".
 */

import type { IdDeSeccion } from './secciones';
import estilos from './IconoSeccion.module.css';

interface IconoSeccionProps {
  id: IdDeSeccion;
}

export function IconoSeccion({ id }: IconoSeccionProps) {
  switch (id) {
    case 'dashboard':
      return (
        <span className={estilos.icono} aria-hidden="true">
          <span className={estilos.grid}>
            <span />
            <span />
            <span />
            <span />
          </span>
        </span>
      );
    case 'equipos':
      return (
        <span className={estilos.icono} aria-hidden="true">
          <span className={estilos.cuadro} />
        </span>
      );
    case 'jugadores':
      return (
        <span className={estilos.icono} aria-hidden="true">
          <span className={estilos.circulo} />
        </span>
      );
    case 'partidos':
      return (
        <span className={estilos.icono} aria-hidden="true">
          <span className={estilos.rombo} />
        </span>
      );
    case 'tabla':
      return (
        <span className={estilos.icono} aria-hidden="true">
          <span className={estilos.barras}>
            <span />
            <span />
            <span />
          </span>
        </span>
      );
    case 'estadisticas':
      return (
        <span className={estilos.icono} aria-hidden="true">
          <span className={estilos.mediocirculo} />
        </span>
      );
    default:
      return null;
  }
}
