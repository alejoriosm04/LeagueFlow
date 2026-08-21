import { useCallback, useEffect, useState } from 'react';
import { EstadoCarga, EstadoError, FilaDeMarcador, Panel } from '../../components';
import { formatearFechaHora } from '../../lib/formato';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { teamsApi } from '../teams/api';
import type { Team } from '../teams/api';
import { eventsApi } from '../events/api';
import type { MatchEvents } from '../events/api';
import { GoalForm } from '../events/GoalForm';
import { playersApi } from '../players/api';
import type { Player } from '../players/api';
import { CorrectionDecisionForm } from './CorrectionDecisionForm';
import { CorrectionRequestForm } from './CorrectionRequestForm';
import { LineupForm } from './LineupForm';
import { matchesApi } from './api';
import type { Match, MatchLineupView, ResultCorrection } from './api';
import { ResultForm } from './ResultForm';
import estilos from './MatchDetailPage.module.css';

const etiquetaAlineacion: Record<MatchLineupView['status'], string> = {
  registered: 'Alineación registrada',
  missing: 'Alineación no registrada',
};

function fecha(value: string | null) {
  return value ? formatearFechaHora(value) : '—';
}

/**
 * Estado de una solicitud de corrección. Es un vocabulario propio de
 * `ResultCorrection` (`pending`/`approved`/`rejected`), distinto del de un
 * partido (`DistintivoDeEstado` es `MatchStatus`): se resuelve aquí en vez de
 * forzar ese componente a cubrir dos dominios (FR-010, FR-028 — el texto
 * identifica el estado, el color es redundante).
 */
const ETIQUETA_CORRECCION: Record<ResultCorrection['status'], string> = {
  pending: 'Pendiente',
  approved: 'Aprobada',
  rejected: 'Rechazada',
};

function PildoraDeCorreccion({ estado }: { estado: ResultCorrection['status'] }) {
  return <span className={`${estilos.pildora} ${estilos[estado]}`}>{ETIQUETA_CORRECCION[estado]}</span>;
}

export function MatchDetailPage() {
  const { matchId } = useParams<{ matchId: string }>();
  const { usuario } = useAuth();
  const [partido, setPartido] = useState<Match | null>(null);
  const [correcciones, setCorrecciones] = useState<ResultCorrection[]>([]);
  const [goles, setGoles] = useState<MatchEvents | null>(null);
  const [alineacion, setAlineacion] = useState<MatchLineupView | null>(null);
  const [jugadores, setJugadores] = useState<Player[]>([]);
  const [equipos, setEquipos] = useState<{ local: Team | null; visitante: Team | null }>({
    local: null,
    visitante: null,
  });
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [intento, setIntento] = useState(0);
  const cargar = useCallback(async () => {
    if (!matchId) return;
    setCargando(true);
    try {
      const [match, history, eventos, lineup] = await Promise.all([
        matchesApi.obtener(matchId),
        matchesApi.listarCorrecciones(matchId),
        eventsApi.listar(matchId),
        matchesApi.obtenerAlineacion(matchId),
      ]);
      setPartido(match);
      setCorrecciones(history.items);
      setGoles(eventos);
      setAlineacion(lineup);
      // Los nombres se resuelven por la API pública del dominio Player.
      const plantillas = await Promise.all([
        playersApi.listar(match.home_team_id),
        playersApi.listar(match.away_team_id),
      ]);
      setJugadores(plantillas.flatMap((plantilla) => plantilla.items));
      // Nombre y escudo para la fila de marcador (FR-009, FR-012). Si el
      // equipo no se puede resolver, la fila cae al identificador abreviado:
      // la ficha del partido no depende de esta consulta.
      const [local, visitante] = await Promise.all([
        teamsApi.obtener(match.home_team_id).catch(() => null),
        teamsApi.obtener(match.away_team_id).catch(() => null),
      ]);
      setEquipos({ local, visitante });
      setError(null);
    } catch {
      setError('No se pudo cargar la ficha del partido.');
    } finally {
      setCargando(false);
    }
  }, [matchId]);
  // `intento` no lo lee `cargar`; solo dispara un reintento manual desde
  // EstadoError cuando la carga inicial falla (mismo patrón que MatchesPage).
  useEffect(() => { void cargar(); }, [cargar, intento]);

  // FR-027: carga y error se renderizan DENTRO de la pantalla, conservando su
  // <h1> — igual que en MatchesPage. Volver antes dejaba la ficha sin
  // encabezado principal justo cuando el usuario más necesita saber dónde
  // está.
  if (cargando || error || !partido || !matchId) {
    return (
      <section>
        <h1>Ficha del partido</h1>
        {error ? (
          <EstadoError mensaje={error} onReintentar={() => setIntento((n) => n + 1)} />
        ) : (
          <EstadoCarga recurso="la ficha del partido" />
        )}
      </section>
    );
  }

  const autenticado = usuario?.role === 'operador' || usuario?.role === 'organizador';
  const nombreJugador = (id: string) =>
    jugadores.find((jugador) => jugador.id === id)?.name ?? id.slice(0, 8);

  return (
    <section className={estilos.pagina}>
      <h1>Ficha del partido</h1>

      <Panel>
        <div className={estilos.resumen}>
          <FilaDeMarcador
            local={{
              nombre: equipos.local?.name ?? partido.home_team_id.slice(0, 8),
              crestUrl: equipos.local?.crest_url,
            }}
            visitante={{
              nombre: equipos.visitante?.name ?? partido.away_team_id.slice(0, 8),
              crestUrl: equipos.visitante?.crest_url,
            }}
            golesLocal={partido.home_score}
            golesVisitante={partido.away_score}
            estado={partido.status}
          />
          <p className={estilos.fecha}>{formatearFechaHora(partido.scheduled_at)}</p>
        </div>
      </Panel>

      {/* Acción principal de un partido programado: registrar el resultado
          la lleva directo al pie del resumen, antes de goles y correcciones
          (que para un partido sin jugar todavía no aplican). */}
      {autenticado && partido.status === 'scheduled' && (
        <ResultForm matchId={matchId} onSuccess={() => void cargar()} />
      )}

      <p><strong>Estado:</strong> {partido.status}</p>
      <p><strong>Marcador vigente:</strong> {partido.home_score ?? '—'} – {partido.away_score ?? '—'}</p>
      {autenticado && partido.status === 'scheduled' && <ResultForm matchId={matchId} onSuccess={() => void cargar()} />}
      {autenticado && partido.status === 'finished' && <CorrectionRequestForm matchId={matchId} onSuccess={() => void cargar()} />}
      <section aria-label="Alineación">
        <h2>Alineación</h2>
        <p>{alineacion ? etiquetaAlineacion[alineacion.status] : 'Cargando…'}</p>
        {alineacion?.status === 'registered' && (
          <div>
            <div>
              <h3>Local</h3>
              <ul>
                {alineacion.home_players.map((j) => (
                  <li key={j.player_id}>
                    <Link to={`/players/${j.player_id}/statistics`}>{j.player_name}</Link>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3>Visitante</h3>
              <ul>
                {alineacion.away_players.map((j) => (
                  <li key={j.player_id}>
                    <Link to={`/players/${j.player_id}/statistics`}>{j.player_name}</Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
        {autenticado && alineacion && (
          <LineupForm
            matchId={matchId}
            jugadoresLocal={jugadores.filter((j) => j.team_id === partido.home_team_id)}
            jugadoresVisitante={jugadores.filter((j) => j.team_id === partido.away_team_id)}
            seleccionLocal={alineacion.home_players.map((j) => j.player_id)}
            seleccionVisitante={alineacion.away_players.map((j) => j.player_id)}
            onSuccess={() => void cargar()}
          />
        )}
      </section>
      <section aria-label="Goles">
        <Panel titulo="Goles">
          {goles && goles.consistency.matches_official === false && (
            <p role="status" className={estilos.aviso}>
              Los goles registrados ({goles.consistency.home_goals_recorded}–
              {goles.consistency.away_goals_recorded}) no coinciden con el marcador oficial (
              {goles.consistency.home_score}–{goles.consistency.away_score}). El marcador oficial
              sigue siendo la fuente de la clasificación.
            </p>
          )}
          {goles && goles.items.length === 0 ? (
            <p className={estilos.textoVacio}>No hay goles registrados.</p>
          ) : (
            <ul className={estilos.golesLista}>
              {goles?.items.map((gol) => (
                <li key={gol.id} className={estilos.golItem}>
                  <span className={estilos.golMarcador} aria-hidden="true" />
                  <span className={estilos.golJugador}>{nombreJugador(gol.player_id)}</span>
                  <span className={estilos.golMinuto}>{gol.minute}&apos;</span>
                </li>
              ))}
            </ul>
          )}
        </Panel>
        {/* El formulario vive fuera del panel, justo debajo: es la acción
            sobre esos datos, no otro dato más dentro de la tarjeta. */}
        {autenticado && (partido.status === 'finished' || partido.status === 'in_progress') && (
          <GoalForm matchId={matchId} jugadores={jugadores} onSuccess={() => void cargar()} />
        )}
      </section>

      {/* Correcciones: solicitud y su historial viven juntas, al final —
          ambas son la misma conversación sobre el resultado ya jugado. */}
      {autenticado && partido.status === 'finished' && (
        <CorrectionRequestForm matchId={matchId} onSuccess={() => void cargar()} />
      )}

      <section aria-label="Historial de correcciones">
        <Panel titulo="Historial de correcciones">
          {correcciones.length === 0 ? (
            <p className={estilos.textoVacio}>No hay correcciones.</p>
          ) : (
            <ol className={estilos.correcciones}>
              {correcciones.map((correccion) => (
                <li key={correccion.id} className={estilos.correccionItem}>
                  <div className={estilos.correccionCabecera}>
                    <span className={estilos.correccionMarcador}>
                      {correccion.previous_home_score}–{correccion.previous_away_score}
                      <span aria-hidden="true"> → </span>
                      {correccion.proposed_home_score}–{correccion.proposed_away_score}
                    </span>
                    <PildoraDeCorreccion estado={correccion.status} />
                  </div>
                  <p className={estilos.correccionMotivo}>{correccion.reason}</p>
                  <p className={estilos.correccionMeta}>
                    Solicitante: {correccion.requested_by} · {fecha(correccion.created_at)}
                  </p>
                  {correccion.decided_by && (
                    <p className={estilos.correccionMeta}>
                      Decisor: {correccion.decided_by} · {fecha(correccion.decided_at)}
                    </p>
                  )}
                  {correccion.decision_reason && (
                    <p className={estilos.correccionMeta}>
                      Motivo de decisión: {correccion.decision_reason}
                    </p>
                  )}
                  {usuario?.role === 'organizador' &&
                    correccion.status === 'pending' &&
                    correccion.requested_by !== usuario.id && (
                      <CorrectionDecisionForm
                        correctionId={correccion.id}
                        onSuccess={() => void cargar()}
                      />
                    )}
                </li>
              ))}
            </ol>
          )}
        </Panel>
      </section>
    </section>
  );
}
