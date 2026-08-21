/**
 * Tabla de datos legible — FR-008, FR-030.
 * Contrato: specs/012-identidad-visual/contracts/ui-contracts.md §2
 *
 * Encabezado diferenciado, filas alternas, numéricos a la derecha y
 * envoltorio con desplazamiento propio, alcanzable con teclado.
 */

import type { ReactNode } from 'react';
import estilos from './TablaDeDatos.module.css';

export interface ColumnaDeTabla<T> {
  clave: string;
  encabezado: string;
  /** Alineación a la derecha + cifras tabulares (FR-008). */
  numerica?: boolean;
  celda: (fila: T) => ReactNode;
}

export type DestacadoDeFila = 'podio-1' | 'podio-2' | 'podio-3' | undefined;

interface TablaDeDatosProps<T> {
  columnas: ReadonlyArray<ColumnaDeTabla<T>>;
  filas: readonly T[];
  claveDeFila: (fila: T) => string;
  /** Se usa como <caption> y como etiqueta del contenedor desplazable. */
  descripcion: string;
  destacarFila?: (fila: T, indice: number) => DestacadoDeFila;
}

const clasePorDestacado: Record<NonNullable<DestacadoDeFila>, string> = {
  'podio-1': estilos.podio1,
  'podio-2': estilos.podio2,
  'podio-3': estilos.podio3,
};

export function TablaDeDatos<T>({
  columnas,
  filas,
  claveDeFila,
  descripcion,
  destacarFila,
}: TablaDeDatosProps<T>) {
  return (
    <div className={estilos.contenedor} role="region" aria-label={descripcion} tabIndex={0}>
      <table className={estilos.tabla}>
        <caption className={estilos.leyenda}>{descripcion}</caption>
        <thead>
          <tr className={estilos.encabezado}>
            {columnas.map((columna) => (
              <th
                key={columna.clave}
                scope="col"
                className={columna.numerica ? estilos.numerica : undefined}
              >
                {columna.encabezado}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filas.map((fila, indice) => {
            const destacado = destacarFila?.(fila, indice);
            return (
              <tr
                key={claveDeFila(fila)}
                className={`${estilos.fila} ${destacado ? clasePorDestacado[destacado] : ''}`}
              >
                {columnas.map((columna) => (
                  <td
                    key={columna.clave}
                    className={columna.numerica ? estilos.numerica : undefined}
                  >
                    {columna.celda(fila)}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
