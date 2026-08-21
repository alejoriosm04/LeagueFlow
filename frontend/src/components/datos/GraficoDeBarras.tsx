/**
 * Gráfico de barras — catálogo de `specs/012-identidad-visual`.
 * Contrato: specs/012-identidad-visual/contracts/ui-contracts.md §2
 *
 * Cada valor se imprime como texto sobre la barra: el color nunca es el
 * único portador de la información (FR-028), así que no hace falta un rol
 * ARIA especial ni una tabla oculta en paralelo — el propio texto visible ya
 * es lo que lee un lector de pantalla. Por eso `destacarUltima` puede pintar
 * la barra más reciente en acento sin incumplir FR-028: su valor sigue
 * escrito encima igual que el de las demás.
 */

import estilos from './GraficoDeBarras.module.css';

export interface BarraDeDatos {
  etiqueta: string;
  valor: number;
}

interface GraficoDeBarrasProps {
  datos: readonly BarraDeDatos[];
  /** Resume el gráfico para quien lo recorre con lector de pantalla. */
  descripcion: string;
  /** Pinta la última barra en acento (la fecha más reciente). */
  destacarUltima?: boolean;
}

export function GraficoDeBarras({
  datos,
  descripcion,
  destacarUltima = false,
}: GraficoDeBarrasProps) {
  const maximo = Math.max(1, ...datos.map((d) => d.valor));

  return (
    <div className={estilos.contenedor} role="group" aria-label={descripcion}>
      {datos.map((barra, indice) => {
        const ultima = destacarUltima && indice === datos.length - 1;
        return (
          <div key={`${barra.etiqueta}-${indice}`} className={estilos.columna}>
            <span className={estilos.valor}>{barra.valor}</span>
            <span
              className={`${estilos.barra} ${ultima ? estilos.destacada : ''}`}
              style={{ height: `${Math.max(4, (barra.valor / maximo) * 100)}%` }}
            />
            <span className={estilos.etiqueta}>{barra.etiqueta}</span>
          </div>
        );
      })}
    </div>
  );
}
