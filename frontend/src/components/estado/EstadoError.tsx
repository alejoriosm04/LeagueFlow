/**
 * Estado de error — FR-015, FR-016.
 * Contrato: specs/012-identidad-visual/contracts/ui-contracts.md §3
 *
 * El mensaje llega YA traducido por mensajesDeError: este componente no
 * interpreta códigos ni muestra nada del servidor. Vive dentro de <main>, así
 * que el shell sobrevive al error y la aplicación sigue navegable (FR-016).
 */

import estilos from './estados.module.css';

interface EstadoErrorProps {
  mensaje: string;
  onReintentar?: () => void;
}

export function EstadoError({ mensaje, onReintentar }: EstadoErrorProps) {
  return (
    <div className={`${estilos.bloque} ${estilos.error}`} role="alert">
      <span className={estilos.rotulo}>Error</span>
      <p className={estilos.mensaje}>{mensaje}</p>
      {onReintentar && (
        <button type="button" className={estilos.accion} onClick={onReintentar}>
          Reintentar
        </button>
      )}
    </div>
  );
}
