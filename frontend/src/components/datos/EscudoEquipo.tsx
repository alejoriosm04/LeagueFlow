/**
 * Escudo de equipo con sustituto de iniciales — FR-012.
 * Contrato: specs/012-identidad-visual/contracts/ui-contracts.md §2
 *
 * Los escudos son enlaces externos (Assumption de la spec). Si `crestUrl`
 * falta O falla al cargar, se muestran las iniciales en el mismo cuadro.
 *
 * `circular` existe porque la maqueta de referencia usa badges redondos en
 * el bloque de próximo partido y en la tabla de posiciones; el sustituto de
 * iniciales adopta la misma forma para que el hueco no cambie de silueta
 * según haya escudo o no.
 */

import { useState } from 'react';
import { inicialesDeEquipo } from '../../lib/formato';
import estilos from './EscudoEquipo.module.css';

interface EscudoEquipoProps {
  nombre: string;
  crestUrl?: string | null;
  tamano?: 'sm' | 'md' | 'lg';
  circular?: boolean;
}

const claseDeTamano = { sm: estilos.sm, md: estilos.md, lg: estilos.lg } as const;

export function EscudoEquipo({
  nombre,
  crestUrl,
  tamano = 'sm',
  circular = false,
}: EscudoEquipoProps) {
  const [fallo, setFallo] = useState(false);
  const clase = `${claseDeTamano[tamano]} ${circular ? estilos.circular : ''}`;

  if (crestUrl && !fallo) {
    return (
      <img
        src={crestUrl}
        alt={`Escudo de ${nombre}`}
        className={`${estilos.escudo} ${clase}`}
        onError={() => setFallo(true)}
      />
    );
  }

  return (
    <span className={`${estilos.sustituto} ${clase}`} aria-hidden="true" title={nombre}>
      {inicialesDeEquipo(nombre)}
    </span>
  );
}
