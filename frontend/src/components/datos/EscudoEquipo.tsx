/**
 * Escudo de equipo con sustituto de iniciales — FR-012.
 * Contrato: specs/012-identidad-visual/contracts/ui-contracts.md §2
 *
 * Los escudos son enlaces externos (Assumption de la spec). Si `crestUrl`
 * falta O falla al cargar, se muestran las iniciales en el mismo cuadro.
 */

import { useState } from 'react';
import { inicialesDeEquipo } from '../../lib/formato';
import estilos from './EscudoEquipo.module.css';

interface EscudoEquipoProps {
  nombre: string;
  crestUrl?: string | null;
  tamano?: 'sm' | 'md';
}

export function EscudoEquipo({ nombre, crestUrl, tamano = 'sm' }: EscudoEquipoProps) {
  const [fallo, setFallo] = useState(false);
  const clase = tamano === 'md' ? estilos.md : estilos.sm;

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
