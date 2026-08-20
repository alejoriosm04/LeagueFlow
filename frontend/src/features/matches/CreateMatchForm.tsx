import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ApiError } from '../../services/apiClient';
import { teamsApi } from '../teams/api';
import type { Team } from '../teams/api';
import { matchesApi } from './api';

export function CreateMatchForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [equipos, setEquipos] = useState<Team[]>([]);
  const [homeTeamId, setHomeTeamId] = useState('');
  const [awayTeamId, setAwayTeamId] = useState('');
  const [scheduledAt, setScheduledAt] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    if (!id) return;
    teamsApi
      .listar(id)
      .then((r) => setEquipos(r.items))
      .catch(() => setError('No se pudieron cargar los equipos.'))
      .finally(() => setCargando(false));
  }, [id]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!id) return;
    setError(null);
    setEnviando(true);
    try {
      // datetime-local es naive; lo enviamos como UTC con Z para el contrato ISO.
      const iso = scheduledAt ? new Date(scheduledAt).toISOString() : '';
      await matchesApi.crear(id, {
        home_team_id: homeTeamId,
        away_team_id: awayTeamId,
        scheduled_at: iso,
      });
      navigate(`/leagues/${id}/matches`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No fue posible programar el partido.');
    } finally {
      setEnviando(false);
    }
  }

  if (cargando) return <p>Cargando equipos…</p>;

  return (
    <form onSubmit={onSubmit} style={{ maxWidth: 420 }}>
      <h1>Programar partido</h1>
      <label htmlFor="home">Equipo local</label>
      <select
        id="home"
        value={homeTeamId}
        onChange={(e) => setHomeTeamId(e.target.value)}
        required
      >
        <option value="">Selecciona…</option>
        {equipos.map((t) => (
          <option key={t.id} value={t.id}>
            {t.name}
          </option>
        ))}
      </select>
      <label htmlFor="away">Equipo visitante</label>
      <select
        id="away"
        value={awayTeamId}
        onChange={(e) => setAwayTeamId(e.target.value)}
        required
      >
        <option value="">Selecciona…</option>
        {equipos.map((t) => (
          <option key={t.id} value={t.id}>
            {t.name}
          </option>
        ))}
      </select>
      <label htmlFor="when">Fecha y hora</label>
      <input
        id="when"
        type="datetime-local"
        value={scheduledAt}
        onChange={(e) => setScheduledAt(e.target.value)}
        required
      />
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={enviando || equipos.length < 2}>
        {enviando ? 'Programando…' : 'Programar partido'}
      </button>
    </form>
  );
}
