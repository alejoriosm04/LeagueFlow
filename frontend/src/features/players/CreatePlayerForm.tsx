import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ApiError } from '../../services/apiClient';
import { playersApi } from './api';

export function CreatePlayerForm() {
  const { teamId } = useParams<{ teamId: string }>();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [number, setNumber] = useState('');
  const [position, setPosition] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!teamId) return;
    setError(null);
    setEnviando(true);
    try {
      const dorsal = number.trim() === '' ? null : Number(number);
      await playersApi.crear(teamId, {
        name,
        number: dorsal,
        position: position || null,
      });
      navigate(`/teams/${teamId}/players`);
    } catch (err) {
      // 409 / 400: se muestra el error.message del envelope (FR-003, validation).
      setError(err instanceof ApiError ? err.message : 'No fue posible registrar el jugador.');
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={onSubmit} style={{ maxWidth: 420 }}>
      <h1>Registrar jugador</h1>
      <label htmlFor="name">Nombre</label>
      <input id="name" value={name} onChange={(e) => setName(e.target.value)} required />
      <label htmlFor="number">Dorsal (1–99, opcional)</label>
      <input
        id="number"
        type="number"
        min={1}
        max={99}
        value={number}
        onChange={(e) => setNumber(e.target.value)}
      />
      <label htmlFor="position">Posición (opcional)</label>
      <input id="position" value={position} onChange={(e) => setPosition(e.target.value)} />
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={enviando}>
        {enviando ? 'Registrando…' : 'Registrar jugador'}
      </button>
    </form>
  );
}
