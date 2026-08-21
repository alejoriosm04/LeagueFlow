/**
 * Campo de formulario con etiqueta, ayuda y error — FR-017, FR-026.
 * Contrato: specs/012-identidad-visual/contracts/ui-contracts.md §2
 *
 * La etiqueta es obligatoria y va asociada por `for`/`id`. La ayuda y el error
 * se ligan con aria-describedby, y el error marca aria-invalid en el control,
 * para que un lector de pantalla los anuncie junto al campo.
 */

import { cloneElement, isValidElement } from 'react';
import type { ReactElement, ReactNode } from 'react';
import estilos from './CampoDeFormulario.module.css';

interface CampoDeFormularioProps {
  id: string;
  etiqueta: string;
  ayuda?: string;
  error?: string | null;
  requerido?: boolean;
  children: ReactNode;
}

export function CampoDeFormulario({
  id,
  etiqueta,
  ayuda,
  error,
  requerido,
  children,
}: CampoDeFormularioProps) {
  const idAyuda = ayuda ? `${id}-ayuda` : undefined;
  const idError = error ? `${id}-error` : undefined;
  const descritoPor = [idAyuda, idError].filter(Boolean).join(' ') || undefined;

  // El control real lo pasa la pantalla; aquí se le añaden los enlaces de
  // accesibilidad sin que cada formulario tenga que recordarlos.
  const control = isValidElement(children)
    ? cloneElement(children as ReactElement<Record<string, unknown>>, {
        id,
        'aria-describedby': descritoPor,
        'aria-invalid': error ? true : undefined,
      })
    : children;

  return (
    <div className={`${estilos.campo} ${error ? estilos.conError : ''}`}>
      {/* El asterisco va FUERA del <label> a propósito: dentro contaminaría
          el nombre accesible del campo ("Usuario *") y rompería tanto a un
          lector de pantalla como a las consultas por etiqueta. La obligación
          real la marca el atributo `required` del control. */}
      <span className={estilos.filaEtiqueta}>
        <label htmlFor={id} className={estilos.etiqueta}>
          {etiqueta}
        </label>
        {requerido && (
          <span className={estilos.requerido} aria-hidden="true">
            *
          </span>
        )}
      </span>
      {ayuda && (
        <span id={idAyuda} className={estilos.ayuda}>
          {ayuda}
        </span>
      )}
      {control}
      {/* role="alert" para que un lector de pantalla anuncie el error al
          aparecer, no solo al enfocar el campo (FR-017, FR-026). */}
      {error && (
        <span id={idError} className={estilos.error} role="alert">
          {error}
        </span>
      )}
    </div>
  );
}
