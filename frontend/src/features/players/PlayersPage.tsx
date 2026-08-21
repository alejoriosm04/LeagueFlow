import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { EstadoCarga, EstadoError, EstadoVacio, Panel, TablaDeDatos, TituloDePantalla } from '../../components';
import type { ColumnaDeTabla } from '../../components';
import { mensajeDeError } from '../../lib/mensajesDeError';
import { useAuth } from '../auth/AuthContext';
import { playersApi } from './api';
import type { Player } from './api';

const columnas: ReadonlyArray<ColumnaDeTabla<Player>> = [
  {
    clave: 'dorsal',
    encabezado: 'Dorsal',
    numerica: true,
    celda: (jugador) => (jugador.number != null ? `#${jugador.number}` : '—'),
  },
  { clave: 'nombre', encabezado: 'Jugador', celda: (jugador) => jugador.name },
  { clave: 'posicion', encabezado: 'Posición', celda: (jugador) => jugador.position ?? '—' },
];

export function PlayersPage() {
  const { teamId } = useParams<{ teamId: string }>();
  const { usuario } = useAuth();
  const [jugadores, setJugadores] = useState<Player[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    if (!teamId) return;
    setCargando(true);
    setError(null);
    playersApi
      .listar(teamId)
      .then((r) => setJugadores(r.items))
      .catch((causa) => setError(mensajeDeError(causa)))
      .finally(() => setCargando(false));
  }, [teamId, intento]);

  // FR-027: los estados de carga y error se renderizan DENTRO de la pantalla,
  // conservando su <h1>. Retornarlos antes dejaba la página sin encabezado
  // principal justo cuando el usuario más necesita saber dónde está.
  const esOrganizador = usuario?.role === 'organizador';

  if (cargando || error) {
    return (
      <section>
        <TituloDePantalla>Plantilla</TituloDePantalla>
        {cargando ? (
          <EstadoCarga recurso="la plantilla" />
        ) : (
          <EstadoError mensaje={error!} onReintentar={() => setIntento((n) => n + 1)} />
        )}
      </section>
    );
  }

  return (
    <section>
      <TituloDePantalla>Plantilla</TituloDePantalla>
      {/* Con la plantilla vacía, la acción la ofrece el estado vacío (FR-014);
          duplicarla aquí dejaría dos enlaces idénticos en la pantalla. */}
      {esOrganizador && teamId && jugadores.length > 0 && (
        <Link to={`/teams/${teamId}/players/new`}>Registrar jugador</Link>
      )}

      {jugadores.length === 0 ? (
        <EstadoVacio
          titulo="Aún no hay jugadores registrados."
          descripcion={
            esOrganizador
              ? 'Registra jugadores para poder anotar sus goles en los partidos.'
              : 'Cuando la organización registre jugadores, aparecerán aquí.'
          }
          accion={
            esOrganizador && teamId
              ? { etiqueta: 'Registrar jugador', href: `/teams/${teamId}/players/new` }
              : undefined
          }
        />
      ) : (
        <Panel titulo="Jugadores">
          <TablaDeDatos
            columnas={columnas}
            filas={jugadores}
            claveDeFila={(jugador) => jugador.id}
            descripcion="Jugadores registrados en el equipo"
          />
        </Panel>
      )}
    </section>
  );
}
