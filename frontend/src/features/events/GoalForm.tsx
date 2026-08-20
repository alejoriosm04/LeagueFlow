import { useState } from 'react';
import { ApiError } from '../../services/apiClient';
import type { Player } from '../players/api';
import { eventsApi } from './api';

const mensajes: Record<string, string> = {
  player_not_in_match: 'El jugador no pertenece a ninguno de los dos equipos del partido.',
  player_not_in_lineup: 'El jugador no figura en la alineación registrada del partido.',
  match_not_playable: 'Solo un partido en curso o finalizado admite goles.',
};

interface Props {
  matchId: string;
  jugadores: Player[];
  onSuccess: () => void;
}

export function GoalForm({ matchId, jugadores, onSuccess }: Props) {
  const [playerId, setPlayerId] = useState('');
  const [minuto, setMinuto] = useState('0');
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function enviar(evento: React.FormEvent) {
    evento.preventDefault();
    setEnviando(true);
    setError(null);
    try {
      await eventsApi.registrar(matchId, { player_id: playerId, minute: Number(minuto) });
      setPlayerId('');
      setMinuto('0');
      onSuccess();
    } catch (err) {
      const codigo = err instanceof ApiError ? err.code : '';
      setError(mensajes[codigo] ?? 'No fue posible registrar el gol.');
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={(e) => void enviar(e)}>
      <label htmlFor="goal-player">Jugador</label>
      <select
        id="goal-player"
        value={playerId}
        onChange={(e) => setPlayerId(e.target.value)}
        required
      >
        <option value="">Selecciona un jugador</option>
        {jugadores.map((jugador) => (
          <option key={jugador.id} value={jugador.id}>
            {jugador.name}
            {jugador.number !== null ? ` (${jugador.number})` : ''}
          </option>
        ))}
      </select>

      <label htmlFor="goal-minute">Minuto</label>
      <input
        id="goal-minute"
        type="number"
        min={0}
        value={minuto}
        onChange={(e) => setMinuto(e.target.value)}
        required
      />

      <button type="submit" disabled={enviando}>
        {enviando ? 'Registrando…' : 'Registrar gol'}
      </button>
      {error && <p role="alert">{error}</p>}
    </form>
  );
}
