/**
 * Ficha individual de estadísticas de un jugador —
 * specs/010-alineaciones-estadisticas.
 *
 * Construida sobre el catálogo de `specs/012-identidad-visual` (SC-010).
 */

import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { EstadoCarga, EstadoError, Panel, TituloDePantalla } from '../../components';
import { mensajeDeError } from '../../lib/mensajesDeError';
import { statisticsApi } from './api';
import type { PlayerStatistics } from './api';
import estilos from './PlayerStatsPage.module.css';

export function PlayerStatsPage() {
  const { playerId } = useParams<{ playerId: string }>();
  const [datos, setDatos] = useState<PlayerStatistics | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [intento, setIntento] = useState(0);

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
      .catch((causa) => {
        if (vigente) setError(mensajeDeError(causa));
      })
      .finally(() => {
        if (vigente) setCargando(false);
      });
    return () => {
      vigente = false;
    };
  }, [playerId, intento]);

  // FR-027: carga y error se renderizan DENTRO de la pantalla, con un <h1>
  // propio — igual que el resto de fichas de la aplicación.
  if (cargando || error || !datos) {
    return (
      <section>
        <TituloDePantalla>Ficha de jugador</TituloDePantalla>
        {error ? (
          <EstadoError mensaje={error} onReintentar={() => setIntento((n) => n + 1)} />
        ) : (
          <EstadoCarga recurso="la ficha del jugador" />
        )}
      </section>
    );
  }

  return (
    <section>
      <TituloDePantalla>{datos.player_name}</TituloDePantalla>

      <Panel titulo="Estadísticas">
        <p className={estilos.equipo}>
          <strong>Equipo:</strong> {datos.team_name}
        </p>
        <dl className={estilos.datos}>
          <dt>Goles anotados</dt>
          <dd>{datos.goals}</dd>
          <dt>Partidos jugados</dt>
          <dd>{datos.matches_played}</dd>
        </dl>
      </Panel>
    </section>
  );
}
