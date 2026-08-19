import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ApiError } from '../../services/apiClient';
import { leaguesApi } from './api';

export function CreateLeagueForm() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [season, setSeason] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      const creada = await leaguesApi.crear({
        name,
        season,
        description: description || null,
      });
      navigate(`/leagues/${creada.id}`);
    } catch (err) {
      // FR-002 / FR-001: al recibir 409 o 400 se muestra el `error.message`
      // del envelope, listo para el usuario.
      setError(err instanceof ApiError ? err.message : 'No fue posible crear la liga.');
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={onSubmit} style={{ maxWidth: 420 }}>
      <h1>Crear liga</h1>
      <label htmlFor="name">Nombre</label>
      <input id="name" value={name} onChange={(e) => setName(e.target.value)} required />
      <label htmlFor="season">Temporada</label>
      <input id="season" value={season} onChange={(e) => setSeason(e.target.value)} required />
      <label htmlFor="description">Descripción (opcional)</label>
      <textarea
        id="description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={enviando}>
        {enviando ? 'Creando…' : 'Crear liga'}
      </button>
    </form>
  );
}
