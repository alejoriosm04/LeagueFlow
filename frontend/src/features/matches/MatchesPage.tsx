import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { teamsApi } from '../teams/api';
import type { Team } from '../teams/api';
import { matchesApi } from './api';
import type { Match, MatchStatus } from './api';

type CalendarFilter = 'all' | MatchStatus;

const titulos: Record<MatchStatus, string> = {
  scheduled: 'Próximos partidos',
  in_progress: 'Partidos en curso',
  finished: 'Partidos jugados',
  cancelled: 'Partidos cancelados',
};

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

function ListaPartidos({ partidos, equipos }: { partidos: Match[]; equipos: Record<string, string> }) {
  const nombre = (teamId: string) => equipos[teamId] ?? teamId.slice(0, 8);
  return (
    <ul>
      {partidos.map((partido) => (
        <li key={partido.id}>
          <Link to={`/matches/${partido.id}`}>
            {nombre(partido.home_team_id)} vs {nombre(partido.away_team_id)}
          </Link>{' '}
          — {formatearFecha(partido.scheduled_at)}
          {partido.status === 'finished' && ` — ${partido.home_score}–${partido.away_score}`}
        </li>
      ))}
    </ul>
  );
}

export function MatchesPage() {
  const { id } = useParams<{ id: string }>();
  const { usuario } = useAuth();
  const [filtro, setFiltro] = useState<CalendarFilter>('all');
  const [grupos, setGrupos] = useState<Partial<Record<MatchStatus, Match[]>>>({});
  const [equipos, setEquipos] = useState<Record<string, string>>({});
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    let vigente = true;
    setCargando(true);
    setError(null);
    const estados: MatchStatus[] = filtro === 'all' ? ['scheduled', 'finished'] : [filtro];
    Promise.all([
      teamsApi.listar(id),
      Promise.all(estados.map((estado) => matchesApi.listarTodos(id, estado))),
    ])
      .then(([teams, colecciones]) => {
        if (!vigente) return;
        const mapa: Record<string, string> = {};
        for (const team of teams.items as Team[]) mapa[team.id] = team.name;
        const nuevos: Partial<Record<MatchStatus, Match[]>> = {};
        estados.forEach((estado, index) => { nuevos[estado] = colecciones[index]; });
        setEquipos(mapa);
        setGrupos(nuevos);
      })
      .catch(() => { if (vigente) setError('No se pudieron cargar los partidos.'); })
      .finally(() => { if (vigente) setCargando(false); });
    return () => { vigente = false; };
  }, [id, filtro]);

  const estadosVisibles: MatchStatus[] = filtro === 'all' ? ['scheduled', 'finished'] : [filtro];
  const total = estadosVisibles.reduce((suma, estado) => suma + (grupos[estado]?.length ?? 0), 0);

  return (
    <section>
      <h1>Partidos</h1>
      {usuario?.role === 'organizador' && id && <Link to={`/leagues/${id}/matches/new`}>Programar partido</Link>}
      <div>
        <label htmlFor="calendar-status">Filtrar por estado</label>
        <select id="calendar-status" value={filtro} onChange={(event) => setFiltro(event.target.value as CalendarFilter)}>
          <option value="all">Todos</option>
          <option value="scheduled">Programados</option>
          <option value="in_progress">En curso</option>
          <option value="finished">Finalizados</option>
          <option value="cancelled">Cancelados</option>
        </select>
      </div>
      {cargando ? <p>Cargando partidos…</p> : error ? <p role="alert">{error}</p> : total === 0 ? (
        <p>Aún no hay partidos en esta liga.</p>
      ) : estadosVisibles.map((estado) => {
        const partidos = grupos[estado] ?? [];
        if (partidos.length === 0) return null;
        return (
          <section key={estado} aria-labelledby={`calendar-${estado}`}>
            <h2 id={`calendar-${estado}`}>{titulos[estado]}</h2>
            <ListaPartidos partidos={partidos} equipos={equipos} />
          </section>
        );
      })}
    </section>
  );
}
