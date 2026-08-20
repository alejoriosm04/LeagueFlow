import { useState } from 'react';
import { ApiError } from '../../services/apiClient';
import { matchesApi } from './api';

export function ResultForm({ matchId, onSuccess }: { matchId: string; onSuccess: () => void }) {
  const [homeScore, setHomeScore] = useState('');
  const [awayScore, setAwayScore] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    const home = Number(homeScore);
    const away = Number(awayScore);
    if (!Number.isInteger(home) || !Number.isInteger(away) || home < 0 || away < 0) {
      setError('Los goles deben ser enteros mayores o iguales a cero.');
      return;
    }
    setError(null);
    setEnviando(true);
    try {
      await matchesApi.registrarResultado(matchId, { home_score: home, away_score: away });
      onSuccess();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No fue posible registrar el resultado.');
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={onSubmit}>
      <h2>Registrar resultado</h2>
      <label htmlFor="result-home">Goles local</label>
      <input id="result-home" type="number" min="0" step="1" required value={homeScore} onChange={(e) => setHomeScore(e.target.value)} />
      <label htmlFor="result-away">Goles visitante</label>
      <input id="result-away" type="number" min="0" step="1" required value={awayScore} onChange={(e) => setAwayScore(e.target.value)} />
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={enviando}>{enviando ? 'Registrando…' : 'Registrar resultado'}</button>
    </form>
  );
}
