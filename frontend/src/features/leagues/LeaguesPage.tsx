import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { leaguesApi } from './api';
import type { League } from './api';

export function LeaguesPage() {
  const [ligas, setLigas] = useState<League[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    leaguesApi
      .listar()
      .then((r) => setLigas(r.items))
      .catch(() => setError('No se pudieron cargar las ligas.'))
      .finally(() => setCargando(false));
  }, []);

  if (cargando) return <p>Cargando ligas…</p>;
  if (error) return <p role="alert">{error}</p>;

  if (ligas.length === 0) {
    return (
      <section>
        <h1>Ligas</h1>
        <p>Aún no hay ligas registradas.</p>
      </section>
    );
  }

  return (
    <section>
      <h1>Ligas</h1>
      <ul>
        {ligas.map((liga) => (
          <li key={liga.id}>
            <Link to={`/leagues/${liga.id}`}>
              {liga.name} — {liga.season}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
