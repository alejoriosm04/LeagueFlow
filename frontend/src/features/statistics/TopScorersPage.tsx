/**
 * Tabla de goleadores de la liga — specs/010-alineaciones-estadisticas.
 *
 * Construida sobre el catálogo de `specs/012-identidad-visual` (SC-010):
 * mismo `TablaDeDatos`, mismos tres estados de pantalla y mismo catálogo de
 * mensajes de error que el resto de la aplicación.
 */

import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { EstadoCarga, EstadoError, EstadoVacio, Panel, TablaDeDatos, TituloDePantalla } from '../../components';
import type { ColumnaDeTabla } from '../../components';
import { mensajeDeError } from '../../lib/mensajesDeError';
import { statisticsApi } from './api';
import type { TopScorerRow } from './api';

/** SC-002: el máximo goleador debe identificarse de inmediato en la interfaz. */
const columnas: ReadonlyArray<ColumnaDeTabla<TopScorerRow>> = [
  { clave: 'Pos', encabezado: 'Pos', numerica: true, celda: (f) => f.rank },
  {
    clave: 'Jugador',
    encabezado: 'Jugador',
    celda: (f) => (
      <>
        <Link to={`/players/${f.player_id}/statistics`}>{f.player_name}</Link>
        {f.is_top_scorer && <strong> · Máximo goleador</strong>}
      </>
    ),
  },
  { clave: 'Equipo', encabezado: 'Equipo', celda: (f) => f.team_name },
  { clave: 'Goles', encabezado: 'Goles', numerica: true, celda: (f) => f.goals },
  { clave: 'PJ', encabezado: 'PJ', numerica: true, celda: (f) => f.matches_played },
];

export function TopScorersPage() {
  const { id } = useParams<{ id: string }>();
  const [filas, setFilas] = useState<TopScorerRow[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    if (!id) return;
    let vigente = true;
    setCargando(true);
    setError(null);
    statisticsApi
      .topScorers(id)
      .then((tabla) => {
        if (vigente) setFilas(tabla.items);
      })
      .catch((causa) => {
        if (vigente) setError(mensajeDeError(causa));
      })
      .finally(() => {
        if (vigente) setCargando(false);
      });
    return () => {
      vigente = false;
    };
  }, [id, intento]);

  return (
    <section>
      <TituloDePantalla>Tabla de goleadores</TituloDePantalla>
      {cargando ? (
        <EstadoCarga recurso="los goleadores" />
      ) : error ? (
        <EstadoError mensaje={error} onReintentar={() => setIntento((n) => n + 1)} />
      ) : filas.length === 0 ? (
        <EstadoVacio
          titulo="Todavía no hay goles registrados en esta liga."
          descripcion="La tabla se completa a medida que se registran goles en los partidos."
        />
      ) : (
        <Panel titulo="Goleadores">
          <TablaDeDatos
            columnas={columnas}
            filas={filas}
            claveDeFila={(fila) => fila.player_id}
            descripcion="Ordenada por goles, de mayor a menor."
          />
        </Panel>
      )}
    </section>
  );
}
