import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { playersApi } from './api';
import type { Player } from './api';

export function PlayersPage() {
  const { teamId } = useParams<{ teamId: string }>();
  const { usuario } = useAuth();
  const [jugadores, setJugadores] = useState<Player[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!teamId) return;
    playersApi
      .listar(teamId)
      .then((r) => setJugadores(r.items))
      .catch(() => setError('No se pudo cargar la plantilla.'))
      .finally(() => setCargando(false));
  }, [teamId]);

  if (cargando) return <p>Cargando plantilla…</p>;
  if (error) return <p role="alert">{error}</p>;

  const esOrganizador = usuario?.role === 'organizador';

  return (
    <section>
      <h1>Plantilla</h1>
      {esOrganizador && teamId && (
        <Link to={`/teams/${teamId}/players/new`}>Registrar jugador</Link>
      )}

      {jugadores.length === 0 ? (
        <p>Aún no hay jugadores registrados.</p>
      ) : (
        <ul>
          {jugadores.map((jugador) => (
            <li key={jugador.id}>
              {jugador.number != null && <span>#{jugador.number} </span>}
              {jugador.name}
              {jugador.position && <span> ({jugador.position})</span>}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
