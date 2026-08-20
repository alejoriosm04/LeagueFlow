import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { teamsApi } from '../teams/api';
import type { Team } from '../teams/api';
import { matchesApi } from './api';
import type { Match } from './api';

function formatearFecha(iso: string): string {
  try {
    return new Date(iso).toLocaleString('es', {
      dateStyle: 'medium',
      timeStyle: 'short',
    });
  } catch {
    return iso;
  }
}

export function MatchesPage() {
  const { id } = useParams<{ id: string }>();
  const { usuario } = useAuth();
  const [partidos, setPartidos] = useState<Match[]>([]);
  const [equipos, setEquipos] = useState<Record<string, string>>({});
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    Promise.all([matchesApi.listar(id), teamsApi.listar(id)])
      .then(([matches, teams]) => {
        setPartidos(matches.items);
        const mapa: Record<string, string> = {};
        for (const t of teams.items as Team[]) {
          mapa[t.id] = t.name;
        }
        setEquipos(mapa);
      })
      .catch(() => setError('No se pudieron cargar los partidos.'))
      .finally(() => setCargando(false));
  }, [id]);

  if (cargando) return <p>Cargando partidos…</p>;
  if (error) return <p role="alert">{error}</p>;

  const esOrganizador = usuario?.role === 'organizador';
  const nombre = (teamId: string) => equipos[teamId] ?? teamId.slice(0, 8);

  return (
    <section>
      <h1>Partidos</h1>
      {esOrganizador && id && (
        <Link to={`/leagues/${id}/matches/new`}>Programar partido</Link>
      )}

      {partidos.length === 0 ? (
        <p>Aún no hay partidos programados.</p>
      ) : (
        <ul>
          {partidos.map((p) => (
            <li key={p.id}>
              {nombre(p.home_team_id)} vs {nombre(p.away_team_id)} —{' '}
              {formatearFecha(p.scheduled_at)} ({p.status})
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
