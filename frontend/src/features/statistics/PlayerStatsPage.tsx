import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { statisticsApi } from './api';
import type { PlayerStatistics } from './api';

export function PlayerStatsPage() {
  const { playerId } = useParams<{ playerId: string }>();
  const [datos, setDatos] = useState<PlayerStatistics | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!playerId) return;
    let vigente = true;
    setCargando(true);
    setError(null);
    statisticsApi
      .ficha(playerId)
      .then((ficha) => {
        if (vigente) setDatos(ficha);
      })
      .catch(() => {
        if (vigente) setError('No se encontró el jugador.');
      })
      .finally(() => {
        if (vigente) setCargando(false);
      });
    return () => {
      vigente = false;
    };
  }, [playerId]);

  if (cargando) return <p>Cargando ficha…</p>;
  if (error) return <p role="alert">{error}</p>;
  if (!datos) return null;

  return (
    <section>
      <h1>{datos.player_name}</h1>
      <p>
        <strong>Equipo:</strong> {datos.team_name}
      </p>
      <dl>
        <dt>Goles anotados</dt>
        <dd>{datos.goals}</dd>
        <dt>Partidos jugados</dt>
        <dd>{datos.matches_played}</dd>
      </dl>
    </section>
  );
}
