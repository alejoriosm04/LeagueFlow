/**
 * Fila de marcador — FR-009.
 * Contrato: specs/012-identidad-visual/contracts/ui-contracts.md §2
 *
 * Formato único "LOCAL 3 — 1 VISITANTE" en toda la aplicación. Sin resultado
 * registrado muestra "vs".
 */

import { Link } from 'react-router-dom';
import { DistintivoDeEstado } from './DistintivoDeEstado';
import type { EstadoDePartido } from './DistintivoDeEstado';
import { EscudoEquipo } from './EscudoEquipo';
import estilos from './FilaDeMarcador.module.css';

interface EquipoDelMarcador {
  nombre: string;
  crestUrl?: string | null;
}

interface FilaDeMarcadorProps {
  local: EquipoDelMarcador;
  visitante: EquipoDelMarcador;
  golesLocal: number | null;
  golesVisitante: number | null;
  estado: EstadoDePartido;
  href?: string;
}

export function FilaDeMarcador({
  local,
  visitante,
  golesLocal,
  golesVisitante,
  estado,
  href,
}: FilaDeMarcadorProps) {
  const hayResultado = golesLocal !== null && golesVisitante !== null;

  const contenido = (
    <>
      <span className={estilos.equipo}>
        <EscudoEquipo nombre={local.nombre} crestUrl={local.crestUrl} />
        {/* Truncado visual conservando el texto íntegro en `title`
            (Assumption "Textos largos"). */}
        <span className={estilos.nombre} title={local.nombre}>
          {local.nombre}
        </span>
      </span>

      {hayResultado ? (
        <span className={estilos.marcador}>
          {golesLocal} — {golesVisitante}
        </span>
      ) : (
        <span className={estilos.sinResultado}>vs</span>
      )}

      <span className={`${estilos.equipo} ${estilos.visitante}`}>
        <span className={estilos.nombre} title={visitante.nombre}>
          {visitante.nombre}
        </span>
        <EscudoEquipo nombre={visitante.nombre} crestUrl={visitante.crestUrl} />
      </span>

      <span className={estilos.estado}>
        <DistintivoDeEstado estado={estado} />
      </span>
    </>
  );

  if (href) {
    return (
      <Link to={href} className={`${estilos.fila} ${estilos.enlace}`}>
        {contenido}
      </Link>
    );
  }

  return <div className={estilos.fila}>{contenido}</div>;
}
