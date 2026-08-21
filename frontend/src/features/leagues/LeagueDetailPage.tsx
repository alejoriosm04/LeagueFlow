import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { EstadoCarga, EstadoError, Panel, TituloDePantalla } from '../../components';
import { mensajeDeError } from '../../lib/mensajesDeError';
import { leaguesApi } from './api';
import type { League } from './api';
import estilos from './LeagueDetailPage.module.css';

export function LeagueDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [liga, setLiga] = useState<League | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    if (!id) return;
    setCargando(true);
    setError(null);
    leaguesApi
      .obtener(id)
      .then(setLiga)
      .catch((causa) => setError(mensajeDeError(causa)))
      .finally(() => setCargando(false));
  }, [id, intento]);

  // FR-027: los estados de carga y error se renderizan DENTRO de la pantalla,
  // conservando su <h1>. Retornarlos antes dejaba la página sin encabezado
  // principal justo cuando el usuario más necesita saber dónde está.
  if (cargando || error) {
    return (
      <section>
        <TituloDePantalla>Liga</TituloDePantalla>
        {cargando ? (
          <EstadoCarga recurso="la liga" />
        ) : (
          <EstadoError mensaje={error!} onReintentar={() => setIntento((n) => n + 1)} />
        )}
      </section>
    );
  }
  if (!liga) return null;

  return (
    <section>
      <TituloDePantalla>{liga.name}</TituloDePantalla>

      <Panel titulo="Datos de la liga">
        <dl className={estilos.datos}>
          <dt>Temporada</dt>
          <dd>{liga.season}</dd>
          {liga.description && (
            <>
              <dt>Descripción</dt>
              <dd>{liga.description}</dd>
            </>
          )}
        </dl>
      </Panel>

      <Panel titulo="Accesos">
        <p className={estilos.accesos}>
          <Link to={`/leagues/${liga.id}/dashboard`}>Ver dashboard</Link>
          <Link to={`/leagues/${liga.id}/teams`}>Ver equipos</Link>
          <Link to={`/leagues/${liga.id}/matches`}>Ver partidos</Link>
          <Link to={`/leagues/${liga.id}/standings`}>Ver clasificación</Link>
          <Link to={`/leagues/${liga.id}/top-scorers`}>Ver goleadores</Link>
        </p>
      </Panel>
    </section>
  );
}
