import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { EstadoCarga, EstadoError, EstadoVacio, FilaDeMarcador, Panel } from '../../components';
import { formatearFechaHora } from '../../lib/formato';
import { mensajeDeError } from '../../lib/mensajesDeError';
import { useAuth } from '../auth/AuthContext';
import { teamsApi } from '../teams/api';
import type { Team } from '../teams/api';
import { matchesApi } from './api';
import type { Match, MatchStatus } from './api';
import estilos from './MatchesPage.module.css';

type CalendarFilter = 'all' | MatchStatus;

const titulos: Record<MatchStatus, string> = {
  scheduled: 'Próximos partidos',
  in_progress: 'Partidos en curso',
  finished: 'Partidos jugados',
  cancelled: 'Partidos cancelados',
};

type MapaDeEquipos = Record<string, Team>;

function ListaPartidos({ partidos, equipos }: { partidos: Match[]; equipos: MapaDeEquipos }) {
  const equipo = (teamId: string) => ({
    nombre: equipos[teamId]?.name ?? teamId.slice(0, 8),
    crestUrl: equipos[teamId]?.crest_url ?? null,
  });

  return (
    <ul className={estilos.lista}>
      {partidos.map((partido) => (
        <li key={partido.id} className={estilos.item}>
          <FilaDeMarcador
            local={equipo(partido.home_team_id)}
            visitante={equipo(partido.away_team_id)}
            golesLocal={partido.home_score}
            golesVisitante={partido.away_score}
            estado={partido.status}
            href={`/matches/${partido.id}`}
          />
          <p className={estilos.fecha}>{formatearFechaHora(partido.scheduled_at)}</p>
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
  const [equipos, setEquipos] = useState<MapaDeEquipos>({});
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [intento, setIntento] = useState(0);

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
        const mapa: MapaDeEquipos = {};
        for (const team of teams.items as Team[]) mapa[team.id] = team;
        const nuevos: Partial<Record<MatchStatus, Match[]>> = {};
        estados.forEach((estado, index) => {
          nuevos[estado] = colecciones[index];
        });
        setEquipos(mapa);
        setGrupos(nuevos);
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
  }, [id, filtro, intento]);

  const estadosVisibles: MatchStatus[] = filtro === 'all' ? ['scheduled', 'finished'] : [filtro];
  const total = estadosVisibles.reduce((suma, estado) => suma + (grupos[estado]?.length ?? 0), 0);

  return (
    <section>
      <h1>Partidos</h1>

      <div className={estilos.acciones}>
        {/* Con la lista vacía, la acción la ofrece el estado vacío (FR-014);
            duplicarla aquí dejaría dos enlaces idénticos en la pantalla. */}
        {usuario?.role === 'organizador' && id && total > 0 && (
          <Link to={`/leagues/${id}/matches/new`}>Programar partido</Link>
        )}
        <div className={estilos.filtro}>
          <label htmlFor="calendar-status">Filtrar por estado</label>
          <select
            id="calendar-status"
            className={estilos.select}
            value={filtro}
            onChange={(event) => setFiltro(event.target.value as CalendarFilter)}
          >
            <option value="all">Todos</option>
            <option value="scheduled">Programados</option>
            <option value="in_progress">En curso</option>
            <option value="finished">Finalizados</option>
            <option value="cancelled">Cancelados</option>
          </select>
        </div>
      </div>

      {cargando ? (
        <EstadoCarga recurso="los partidos" />
      ) : error ? (
        <EstadoError mensaje={error} onReintentar={() => setIntento((n) => n + 1)} />
      ) : total === 0 ? (
        <EstadoVacio
          titulo="Aún no hay partidos en esta liga."
          descripcion="Cuando se programen partidos aparecerán aquí, agrupados por estado."
          accion={
            usuario?.role === 'organizador' && id
              ? { etiqueta: 'Programar partido', href: `/leagues/${id}/matches/new` }
              : undefined
          }
        />
      ) : (
        estadosVisibles.map((estado) => {
          const partidos = grupos[estado] ?? [];
          if (partidos.length === 0) return null;
          return (
            <Panel key={estado} titulo={titulos[estado]}>
              <ListaPartidos partidos={partidos} equipos={equipos} />
            </Panel>
          );
        })
      )}
    </section>
  );
}
