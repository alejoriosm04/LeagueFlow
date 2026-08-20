import { useCallback, useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
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
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const cargar = useCallback(async () => {
    if (!matchId) return;
    try {
      const [match, history] = await Promise.all([matchesApi.obtener(matchId), matchesApi.listarCorrecciones(matchId)]);
      setPartido(match);
      setCorrecciones(history.items);
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
  return (
    <section>
      <h1>Ficha del partido</h1>
      <p><strong>Estado:</strong> {partido.status}</p>
      <p><strong>Marcador vigente:</strong> {partido.home_score ?? '—'} – {partido.away_score ?? '—'}</p>
      {autenticado && partido.status === 'scheduled' && <ResultForm matchId={matchId} onSuccess={() => void cargar()} />}
      {autenticado && partido.status === 'finished' && <CorrectionRequestForm matchId={matchId} onSuccess={() => void cargar()} />}
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
