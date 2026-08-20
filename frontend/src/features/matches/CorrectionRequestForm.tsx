import { useState } from 'react';
import { ApiError } from '../../services/apiClient';
import { matchesApi } from './api';

export function CorrectionRequestForm({ matchId, onSuccess }: { matchId: string; onSuccess: () => void }) {
  const [homeScore, setHomeScore] = useState('');
  const [awayScore, setAwayScore] = useState('');
  const [reason, setReason] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!reason.trim()) {
      setError('El motivo de la corrección es obligatorio.');
      return;
    }
    const home = Number(homeScore);
    const away = Number(awayScore);
    if (homeScore === '' || awayScore === '' || !Number.isInteger(home) || !Number.isInteger(away) || home < 0 || away < 0) {
      setError('Los goles deben ser enteros mayores o iguales a cero.');
      return;
    }
    setError(null);
    setEnviando(true);
    try {
      await matchesApi.solicitarCorreccion(matchId, { home_score: home, away_score: away, reason: reason.trim() });
      onSuccess();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No fue posible solicitar la corrección.');
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={onSubmit} noValidate>
      <h2>Solicitar corrección</h2>
      <label htmlFor="correction-home">Nuevo marcador local</label>
      <input id="correction-home" type="number" min="0" step="1" required value={homeScore} onChange={(e) => setHomeScore(e.target.value)} />
      <label htmlFor="correction-away">Nuevo marcador visitante</label>
      <input id="correction-away" type="number" min="0" step="1" required value={awayScore} onChange={(e) => setAwayScore(e.target.value)} />
      <label htmlFor="correction-reason">Motivo</label>
      <textarea id="correction-reason" required value={reason} onChange={(e) => setReason(e.target.value)} />
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={enviando}>{enviando ? 'Solicitando…' : 'Solicitar corrección'}</button>
    </form>
  );
}
