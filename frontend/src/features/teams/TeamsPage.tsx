import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { teamsApi } from './api';
import type { Team } from './api';

function TeamCrest({ name, crestUrl }: { name: string; crestUrl: string | null }) {
  const [fallo, setFallo] = useState(false);

  if (!crestUrl || fallo) {
    return <span aria-hidden="true">{name.charAt(0).toUpperCase()}</span>;
  }
  return (
    <img
      src={crestUrl}
      alt={`Escudo de ${name}`}
      style={{ width: 32, height: 32, objectFit: 'contain' }}
      onError={() => setFallo(true)}
    />
  );
}

export function TeamsPage() {
  const { id } = useParams<{ id: string }>();
  const { usuario } = useAuth();
  const [equipos, setEquipos] = useState<Team[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    teamsApi
      .listar(id)
      .then((r) => setEquipos(r.items))
      .catch(() => setError('No se pudieron cargar los equipos.'))
      .finally(() => setCargando(false));
  }, [id]);

  if (cargando) return <p>Cargando equipos…</p>;
  if (error) return <p role="alert">{error}</p>;

  const esOrganizador = usuario?.role === 'organizador';

  return (
    <section>
      <h1>Equipos</h1>
      {esOrganizador && id && <Link to={`/leagues/${id}/teams/new`}>Registrar equipo</Link>}

      {equipos.length === 0 ? (
        <p>Aún no hay equipos registrados.</p>
      ) : (
        <ul>
          {equipos.map((equipo) => (
            <li key={equipo.id} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <TeamCrest name={equipo.name} crestUrl={equipo.crest_url} />
              {equipo.name}
              {equipo.colors && <span>({equipo.colors})</span>}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
