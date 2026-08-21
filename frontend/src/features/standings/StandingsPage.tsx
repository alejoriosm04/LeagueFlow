import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { DestacadoDePodio, EstadoCarga, EstadoError, EstadoVacio, Panel, TablaDeDatos, TituloDePantalla } from '../../components';
import type { ColumnaDeTabla, DestacadoDeFila } from '../../components';
import { formatearDiferencia } from '../../lib/formato';
import { mensajeDeError } from '../../lib/mensajesDeError';
import { standingsApi } from './api';
import type { StandingsRow } from './api';

/** La tabla nunca se edita: se deriva de los partidos finalizados (FR-002). */
const columnas: ReadonlyArray<ColumnaDeTabla<StandingsRow>> = [
  { clave: 'Pos', encabezado: 'Pos', celda: (f) => <DestacadoDePodio posicion={f.position} /> },
  { clave: 'Equipo', encabezado: 'Equipo', celda: (f) => f.team_name },
  { clave: 'PJ', encabezado: 'PJ', numerica: true, celda: (f) => f.played },
  { clave: 'G', encabezado: 'G', numerica: true, celda: (f) => f.won },
  { clave: 'E', encabezado: 'E', numerica: true, celda: (f) => f.drawn },
  { clave: 'P', encabezado: 'P', numerica: true, celda: (f) => f.lost },
  { clave: 'GF', encabezado: 'GF', numerica: true, celda: (f) => f.goals_for },
  { clave: 'GC', encabezado: 'GC', numerica: true, celda: (f) => f.goals_against },
  {
    clave: 'GD',
    encabezado: 'GD',
    numerica: true,
    celda: (f) => formatearDiferencia(f.goal_difference),
  },
  { clave: 'Pts', encabezado: 'Pts', numerica: true, celda: (f) => f.points },
];

/**
 * Podio (FR-011): se destacan solo las posiciones que existen, así que una
 * liga de dos equipos nunca pinta un tercer puesto.
 */
function destacarPodio(fila: StandingsRow): DestacadoDeFila {
  if (fila.position === 1) return 'podio-1';
  if (fila.position === 2) return 'podio-2';
  if (fila.position === 3) return 'podio-3';
  return undefined;
}

export function StandingsPage() {
  const { id } = useParams<{ id: string }>();
  const [filas, setFilas] = useState<StandingsRow[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    if (!id) return;
    let vigente = true;
    setCargando(true);
    setError(null);
    standingsApi
      .obtener(id)
      .then((clasificacion) => {
        if (vigente) setFilas(clasificacion.items);
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
      <TituloDePantalla>Clasificación</TituloDePantalla>
      {cargando && <EstadoCarga recurso="la clasificación" />}
      {error && <EstadoError mensaje={error} onReintentar={() => setIntento((n) => n + 1)} />}
      {!cargando && !error && filas.length === 0 && (
        <EstadoVacio
          titulo="Todavía no hay equipos en esta liga."
          descripcion="La clasificación se calcula sola a partir de los partidos finalizados. Registra equipos y programa partidos para verla."
        />
      )}
      {!cargando && !error && filas.length > 0 && (
        <Panel titulo="Tabla de posiciones">
          <TablaDeDatos
            columnas={columnas}
            filas={filas}
            claveDeFila={(fila) => fila.team_id}
            descripcion="Puntos por victoria: 3; por empate: 1. El orden aplica puntos, diferencia de goles y goles a favor."
            destacarFila={destacarPodio}
          />
        </Panel>
      )}
    </section>
  );
}
