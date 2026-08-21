import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { statisticsApi } from './api';
import type { TopScorerRow } from './api';

/** SC-002: el máximo goleador debe identificarse de inmediato en la interfaz. */
const columnas = ['Pos', 'Jugador', 'Equipo', 'Goles', 'PJ'] as const;

export function TopScorersPage() {
  const { id } = useParams<{ id: string }>();
  const [filas, setFilas] = useState<TopScorerRow[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
      <h1>Tabla de goleadores</h1>
      {cargando && <p>Cargando goleadores…</p>}
      {error && <p role="alert">{error}</p>}
      {!cargando && !error && filas.length === 0 && (
        <p>Todavía no hay goles registrados en esta liga.</p>
      )}
      {!cargando && !error && filas.length > 0 && (
        <table>
          <caption>Ordenada por goles, de mayor a menor.</caption>
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
              <tr key={fila.player_id}>
                <td>{fila.rank}</td>
                <td>
                  <Link to={`/players/${fila.player_id}/statistics`}>{fila.player_name}</Link>
                  {fila.is_top_scorer && <strong> · Máximo goleador</strong>}
                </td>
                <td>{fila.team_name}</td>
                <td>{fila.goals}</td>
                <td>{fila.matches_played}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
