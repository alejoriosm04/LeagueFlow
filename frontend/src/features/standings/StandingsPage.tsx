import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { standingsApi } from './api';
import type { StandingsRow } from './api';

/** La tabla nunca se edita: se deriva de los partidos finalizados (FR-002). */
const columnas = ['Pos', 'Equipo', 'PJ', 'G', 'E', 'P', 'GF', 'GC', 'GD', 'Pts'] as const;

function formatearDiferencia(valor: number): string {
  return valor > 0 ? `+${valor}` : `${valor}`;
}

export function StandingsPage() {
  const { id } = useParams<{ id: string }>();
  const [filas, setFilas] = useState<StandingsRow[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
      .catch(() => {
        if (vigente) setError('No se encontró la liga.');
      })
      .finally(() => {
        if (vigente) setCargando(false);
      });
    return () => {
      vigente = false;
    };
  }, [id]);

  return (
    <section>
      <h1>Clasificación</h1>
      {cargando && <p>Cargando clasificación…</p>}
      {error && <p role="alert">{error}</p>}
      {!cargando && !error && filas.length === 0 && (
        <p>Todavía no hay equipos en esta liga.</p>
      )}
      {!cargando && !error && filas.length > 0 && (
        <table>
          <caption>
            Puntos por victoria: 3; por empate: 1. El orden aplica puntos, diferencia de goles y
            goles a favor.
          </caption>
          <thead>
            <tr>
              {columnas.map((columna) => (
                <th key={columna} scope="col">
                  {columna}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filas.map((fila) => (
              <tr key={fila.team_id}>
                <td>{fila.position}</td>
                <td>{fila.team_name}</td>
                <td>{fila.played}</td>
                <td>{fila.won}</td>
                <td>{fila.drawn}</td>
                <td>{fila.lost}</td>
                <td>{fila.goals_for}</td>
                <td>{fila.goals_against}</td>
                <td>{formatearDiferencia(fila.goal_difference)}</td>
                <td>{fila.points}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
