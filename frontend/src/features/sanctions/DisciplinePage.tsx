import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { EstadoCarga, EstadoError, Panel, TituloDePantalla } from '../../components';
import { mensajeDeError } from '../../lib/mensajesDeError';
import { sanctionsApi, type PlayerDiscipline } from './api';
import estilos from './DisciplinePage.module.css';

export function DisciplinePage() {
  const { playerId } = useParams<{ playerId: string }>();
  const [datos, setDatos] = useState<PlayerDiscipline | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    if (!playerId) return;
    let vigente = true;
    setCargando(true);
    setError(null);
    sanctionsApi
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

  if (cargando || error || !datos) {
    return (
      <section>
        <TituloDePantalla>Ficha disciplinaria</TituloDePantalla>
        {error ? (
          <EstadoError mensaje={error} onReintentar={() => setIntento((n) => n + 1)} />
        ) : (
          <EstadoCarga recurso="la ficha disciplinaria" />
        )}
      </section>
    );
  }

  return (
    <section>
      <TituloDePantalla>Ficha disciplinaria</TituloDePantalla>
      <p className={estilos.enlaceEstadisticas}>
        <Link to={`/players/${playerId}/statistics`}>Ver estadísticas del jugador</Link>
      </p>

      <Panel titulo="Resumen">
        <dl className={estilos.datos}>
          <dt>Tarjetas amarillas</dt>
          <dd>{datos.yellow_cards}</dd>
          <dt>Tarjetas rojas</dt>
          <dd>{datos.red_cards}</dd>
          <dt>Estado</dt>
          <dd>{datos.suspended ? 'Suspendido' : 'Al día'}</dd>
        </dl>
      </Panel>
    </section>
  );
}
