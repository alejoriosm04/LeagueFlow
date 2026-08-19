import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ApiError } from '../../services/apiClient';
import { teamsApi } from './api';

export function CreateTeamForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [crestUrl, setCrestUrl] = useState('');
  const [colors, setColors] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!id) return;
    setError(null);
    setEnviando(true);
    try {
      await teamsApi.crear(id, {
        name,
        crest_url: crestUrl || null,
        colors: colors || null,
      });
      navigate(`/leagues/${id}/teams`);
    } catch (err) {
      // 409 / 400: se muestra el error.message del envelope (FR-002, validation).
      setError(err instanceof ApiError ? err.message : 'No fue posible registrar el equipo.');
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={onSubmit} style={{ maxWidth: 420 }}>
      <h1>Registrar equipo</h1>
      <label htmlFor="name">Nombre</label>
      <input id="name" value={name} onChange={(e) => setName(e.target.value)} required />
      <label htmlFor="crestUrl">Escudo (URL https, opcional)</label>
      <input id="crestUrl" value={crestUrl} onChange={(e) => setCrestUrl(e.target.value)} />
      <label htmlFor="colors">Colores (opcional)</label>
      <input id="colors" value={colors} onChange={(e) => setColors(e.target.value)} />
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={enviando}>
        {enviando ? 'Registrando…' : 'Registrar equipo'}
      </button>
    </form>
  );
}
