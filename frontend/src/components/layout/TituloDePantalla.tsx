/**
 * Título de la pantalla actual — FR-027, FR-042.
 * Contrato: specs/012-identidad-visual/contracts/ui-contracts.md §1
 *
 * La pantalla sigue declarando su propio título, pero se PINTA en la
 * cabecera del marco, sobre la superficie de marca, como en la maqueta de
 * referencia. Se resuelve con un portal en vez de con un contexto de texto
 * por dos razones:
 *
 *  1. El título puede ser marcado, no solo una cadena (el nombre de una liga
 *     truncado, por ejemplo), y un portal admite cualquier `ReactNode`.
 *  2. Fuera del `AppShell` —una pantalla renderizada suelta en una prueba de
 *     componente— no hay destino, así que el `<h1>` se pinta en su sitio
 *     natural. Las pruebas siguen encontrándolo por rol sin conocer el
 *     shell, y la pantalla nunca se queda sin encabezado principal (FR-027).
 *
 * Sigue habiendo exactamente un `<h1>` por pantalla: el portal lo mueve de
 * sitio, no lo duplica.
 */

import { createContext, useContext } from 'react';
import type { ReactNode } from 'react';
import { createPortal } from 'react-dom';
import estilos from './TituloDePantalla.module.css';

/** Dónde vive el `<h1>`. `null` = no hay shell: se pinta en su lugar. */
export const DestinoDelTitulo = createContext<HTMLElement | null>(null);

interface TituloDePantallaProps {
  children: ReactNode;
}

export function TituloDePantalla({ children }: TituloDePantallaProps) {
  const destino = useContext(DestinoDelTitulo);
  const titulo = <h1 className={estilos.titulo}>{children}</h1>;

  return destino ? createPortal(titulo, destino) : titulo;
}
