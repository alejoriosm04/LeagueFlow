import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { dashboardApi } from './api';
import type { DashboardSummary } from './api';
import { teamsApi } from '../teams/api';
import type { Team } from '../teams/api';

const formatoFecha = new Intl.DateTimeFormat('es', {
  dateStyle: 'medium',
  timeStyle: 'short',
});

function formatearFecha(iso: string): string {
  try {
    return formatoFecha.format(new Date(iso));
  } catch {
    return iso;
  }
}

function formatearDiferencia(valor: number): string {
  return valor > 0 ? `+${valor}` : `${valor}`;
}

export function DashboardPage() {
  const { id } = useParams<{ id: string }>();
  const [resumen, setResumen] = useState<DashboardSummary | null>(null);
  // Match solo trae home_team_id/away_team_id (UUIDs); el mapa id->nombre se
  // resuelve aparte con teamsApi, igual que ya hace MatchesPage.tsx.
  const [equipos, setEquipos] = useState<Record<string, string>>({});
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    let vigente = true;
    setCargando(true);
    setError(null);
    Promise.all([dashboardApi.obtener(id), teamsApi.listar(id)])
      .then(([datos, paginaEquipos]) => {
        if (!vigente) return;
        const mapa: Record<string, string> = {};
        for (const equipo of paginaEquipos.items as Team[]) mapa[equipo.id] = equipo.name;
        setEquipos(mapa);
        setResumen(datos);
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

  const nombre = (teamId: string) => equipos[teamId] ?? teamId.slice(0, 8);

  if (cargando) return <p>Cargando dashboard…</p>;
  if (error) return <p role="alert">{error}</p>;
  if (!resumen || !id) return null;

  return (
    <section>
      <h1>Dashboard de la liga</h1>
      <p>
        <Link to={`/leagues/${id}/matches`}>Ver calendario completo</Link>
        {' · '}
        <Link to={`/leagues/${id}/standings`}>Ver clasificación completa</Link>
      </p>

      <section aria-labelledby="dashboard-recientes">
        <h2 id="dashboard-recientes">Últimos resultados</h2>
        {resumen.recent_matches.length === 0 ? (
          <p>Aún no hay partidos jugados.</p>
        ) : (
          <ul>
            {resumen.recent_matches.map((partido) => (
              <li key={partido.id}>
                <Link to={`/matches/${partido.id}`}>
                  {nombre(partido.home_team_id)} {partido.home_score}–{partido.away_score}{' '}
                  {nombre(partido.away_team_id)}
                </Link>{' '}
                — {formatearFecha(partido.scheduled_at)}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-labelledby="dashboard-proximos">
        <h2 id="dashboard-proximos">Próximos partidos</h2>
        {resumen.upcoming_matches.length === 0 ? (
          <p>Aún no hay próximos partidos.</p>
        ) : (
          <ul>
            {resumen.upcoming_matches.map((partido) => (
              <li key={partido.id}>
                <Link to={`/matches/${partido.id}`}>
                  {nombre(partido.home_team_id)} vs {nombre(partido.away_team_id)}
                </Link>{' '}
                — {formatearFecha(partido.scheduled_at)}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-labelledby="dashboard-clasificacion">
        <h2 id="dashboard-clasificacion">Tabla de posiciones</h2>
        {resumen.top_standings.length === 0 ? (
          <p>Aún no hay equipos.</p>
        ) : (
          <table>
            <caption>
              Primeros {resumen.top_standings.length} lugares de la clasificación.
            </caption>
            <thead>
              <tr>
                <th scope="col">Pos</th>
                <th scope="col">Equipo</th>
                <th scope="col">PJ</th>
                <th scope="col">GD</th>
                <th scope="col">Pts</th>
              </tr>
            </thead>
            <tbody>
              {resumen.top_standings.map((fila) => (
                <tr key={fila.team_id}>
                  <td>{fila.position}</td>
                  <td>{fila.team_name}</td>
                  <td>{fila.played}</td>
                  <td>{formatearDiferencia(fila.goal_difference)}</td>
                  <td>{fila.points}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </section>
  );
}
