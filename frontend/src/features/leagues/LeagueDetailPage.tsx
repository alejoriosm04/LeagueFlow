import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { leaguesApi } from './api';
import type { League } from './api';

export function LeagueDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [liga, setLiga] = useState<League | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    leaguesApi
      .obtener(id)
      .then(setLiga)
      .catch(() => setError('No se encontró la liga.'))
      .finally(() => setCargando(false));
  }, [id]);

  if (cargando) return <p>Cargando…</p>;
  if (error) return <p role="alert">{error}</p>;
  if (!liga) return null;

  return (
    <section>
      <h1>{liga.name}</h1>
      <p>
        <strong>Temporada:</strong> {liga.season}
      </p>
      {liga.description && <p>{liga.description}</p>}
    </section>
  );
}
