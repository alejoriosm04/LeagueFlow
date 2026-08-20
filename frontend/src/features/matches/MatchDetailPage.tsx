import { useCallback, useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { eventsApi } from '../events/api';
import type { MatchEvents } from '../events/api';
import { GoalForm } from '../events/GoalForm';
import { playersApi } from '../players/api';
import type { Player } from '../players/api';
import { CorrectionDecisionForm } from './CorrectionDecisionForm';
import { CorrectionRequestForm } from './CorrectionRequestForm';
import { matchesApi } from './api';
import type { Match, ResultCorrection } from './api';
import { ResultForm } from './ResultForm';

function fecha(value: string | null) {
  return value ? new Date(value).toLocaleString('es') : '—';
}

export function MatchDetailPage() {
  const { matchId } = useParams<{ matchId: string }>();
  const { usuario } = useAuth();
  const [partido, setPartido] = useState<Match | null>(null);
  const [correcciones, setCorrecciones] = useState<ResultCorrection[]>([]);
  const [goles, setGoles] = useState<MatchEvents | null>(null);
  const [jugadores, setJugadores] = useState<Player[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const cargar = useCallback(async () => {
    if (!matchId) return;
    try {
      const [match, history, eventos] = await Promise.all([
        matchesApi.obtener(matchId),
        matchesApi.listarCorrecciones(matchId),
        eventsApi.listar(matchId),
      ]);
      setPartido(match);
      setCorrecciones(history.items);
      setGoles(eventos);
      // Los nombres se resuelven por la API pública del dominio Player.
      const plantillas = await Promise.all([
        playersApi.listar(match.home_team_id),
        playersApi.listar(match.away_team_id),
      ]);
      setJugadores(plantillas.flatMap((plantilla) => plantilla.items));
      setError(null);
    } catch {
      setError('No se pudo cargar la ficha del partido.');
    } finally {
      setCargando(false);
    }
  }, [matchId]);
  useEffect(() => { void cargar(); }, [cargar]);
  if (cargando) return <p>Cargando partido…</p>;
  if (error) return <p role="alert">{error}</p>;
  if (!partido || !matchId) return null;
  const autenticado = usuario?.role === 'operador' || usuario?.role === 'organizador';
  const nombreJugador = (id: string) =>
    jugadores.find((jugador) => jugador.id === id)?.name ?? id.slice(0, 8);
  return (
    <section>
      <h1>Ficha del partido</h1>
      <p><strong>Estado:</strong> {partido.status}</p>
      <p><strong>Marcador vigente:</strong> {partido.home_score ?? '—'} – {partido.away_score ?? '—'}</p>
      {autenticado && partido.status === 'scheduled' && <ResultForm matchId={matchId} onSuccess={() => void cargar()} />}
      {autenticado && partido.status === 'finished' && <CorrectionRequestForm matchId={matchId} onSuccess={() => void cargar()} />}
      <section aria-label="Goles">
        <h2>Goles</h2>
        {goles && goles.consistency.matches_official === false && (
          <p role="status">
            Los goles registrados ({goles.consistency.home_goals_recorded}–
            {goles.consistency.away_goals_recorded}) no coinciden con el marcador oficial (
            {goles.consistency.home_score}–{goles.consistency.away_score}). El marcador oficial
            sigue siendo la fuente de la clasificación.
          </p>
        )}
        {goles && goles.items.length === 0 ? (
          <p>No hay goles registrados.</p>
        ) : (
          <ul>
            {goles?.items.map((gol) => (
              <li key={gol.id}>
                {nombreJugador(gol.player_id)} — {gol.minute}'
              </li>
            ))}
          </ul>
        )}
        {autenticado && (partido.status === 'finished' || partido.status === 'in_progress') && (
          <GoalForm matchId={matchId} jugadores={jugadores} onSuccess={() => void cargar()} />
        )}
      </section>
      <h2>Historial de correcciones</h2>
      {correcciones.length === 0 ? <p>No hay correcciones.</p> : (
        <ol>{correcciones.map((correccion) => (
          <li key={correccion.id}>
            <p>{correccion.previous_home_score}–{correccion.previous_away_score} → {correccion.proposed_home_score}–{correccion.proposed_away_score}; estado: {correccion.status}.</p>
            <p>Motivo: {correccion.reason}</p>
            <p>Solicitante: {correccion.requested_by}; fecha: {fecha(correccion.created_at)}</p>
            {correccion.decided_by && <p>Decisor: {correccion.decided_by}; fecha: {fecha(correccion.decided_at)}</p>}
            {correccion.decision_reason && <p>Motivo de decisión: {correccion.decision_reason}</p>}
            {usuario?.role === 'organizador' && correccion.status === 'pending' && correccion.requested_by !== usuario.id && <CorrectionDecisionForm correctionId={correccion.id} onSuccess={() => void cargar()} />}
          </li>
        ))}</ol>
      )}
    </section>
  );
}
