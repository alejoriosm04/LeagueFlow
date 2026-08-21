/**
 * Estado vacío — FR-014.
 * Contrato: specs/012-identidad-visual/contracts/ui-contracts.md §3
 *
 * La acción es OPCIONAL a propósito: solo se pasa si el usuario actual puede
 * ejecutarla. A un espectador se le informa del estado sin ofrecerle una
 * acción que no tiene permitida.
 */

import { Link } from 'react-router-dom';
import estilos from './estados.module.css';

interface EstadoVacioProps {
  titulo: string;
  descripcion: string;
  accion?: { etiqueta: string; href: string };
}

export function EstadoVacio({ titulo, descripcion, accion }: EstadoVacioProps) {
  return (
    <div className={estilos.bloque}>
      <p className={estilos.titulo}>{titulo}</p>
      <p className={estilos.descripcion}>{descripcion}</p>
      {accion && (
        <Link to={accion.href} className={estilos.accion}>
          {accion.etiqueta}
        </Link>
      )}
    </div>
  );
}
