/**
 * Contenedor con título y acciones — FR-007.
 * Contrato: specs/012-identidad-visual/contracts/ui-contracts.md §2
 */

import type { ReactNode } from 'react';
import estilos from './Panel.module.css';

interface PanelProps {
  titulo?: string;
  acciones?: ReactNode;
  children: ReactNode;
}

export function Panel({ titulo, acciones, children }: PanelProps) {
  return (
    <section className={estilos.panel}>
      {(titulo || acciones) && (
        <div className={estilos.encabezado}>
          {titulo && <h2 className={estilos.titulo}>{titulo}</h2>}
          {acciones && <div className={estilos.acciones}>{acciones}</div>}
        </div>
      )}
      <div className={estilos.cuerpo}>{children}</div>
    </section>
  );
}
