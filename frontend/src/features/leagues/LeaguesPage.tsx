import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { leaguesApi } from './api';
import type { League } from './api';

export function LeaguesPage() {
  const { usuario } = useAuth();
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

  const esOrganizador = usuario?.role === 'organizador';

  if (ligas.length === 0) {
    return (
      <section>
        <h1>Ligas</h1>
        <p>Aún no hay ligas registradas.</p>
        {esOrganizador && <Link to="/leagues/new">Crear liga</Link>}
      </section>
    );
  }

  return (
    <section>
      <h1>Ligas</h1>
      {esOrganizador && <Link to="/leagues/new">Crear liga</Link>}
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
