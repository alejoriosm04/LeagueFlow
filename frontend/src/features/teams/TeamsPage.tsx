import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { EscudoEquipo, EstadoCarga, EstadoError, EstadoVacio, Panel, TablaDeDatos, TituloDePantalla } from '../../components';
import type { ColumnaDeTabla } from '../../components';
import { mensajeDeError } from '../../lib/mensajesDeError';
import { useAuth } from '../auth/AuthContext';
import { teamsApi } from './api';
import type { Team } from './api';

const columnas: ReadonlyArray<ColumnaDeTabla<Team>> = [
  {
    clave: 'escudo',
    encabezado: 'Escudo',
    celda: (equipo) => <EscudoEquipo nombre={equipo.name} crestUrl={equipo.crest_url} />,
  },
  {
    clave: 'nombre',
    encabezado: 'Equipo',
    celda: (equipo) => <Link to={`/teams/${equipo.id}/players`}>{equipo.name}</Link>,
  },
  { clave: 'colores', encabezado: 'Colores', celda: (equipo) => equipo.colors ?? '—' },
];

export function TeamsPage() {
  const { id } = useParams<{ id: string }>();
  const { usuario } = useAuth();
  const [equipos, setEquipos] = useState<Team[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    if (!id) return;
    setCargando(true);
    setError(null);
    teamsApi
      .listar(id)
      .then((r) => setEquipos(r.items))
      .catch((causa) => setError(mensajeDeError(causa)))
      .finally(() => setCargando(false));
  }, [id, intento]);

  // FR-027: los estados de carga y error se renderizan DENTRO de la pantalla,
  // conservando su <h1>. Retornarlos antes dejaba la página sin encabezado
  // principal justo cuando el usuario más necesita saber dónde está.
  const esOrganizador = usuario?.role === 'organizador';

  if (cargando || error) {
    return (
      <section>
        <TituloDePantalla>Equipos</TituloDePantalla>
        {cargando ? (
          <EstadoCarga recurso="los equipos" />
        ) : (
          <EstadoError mensaje={error!} onReintentar={() => setIntento((n) => n + 1)} />
        )}
      </section>
    );
  }

  return (
    <section>
      <TituloDePantalla>Equipos</TituloDePantalla>

      {equipos.length === 0 ? (
        // FR-014: la acción se ofrece solo a quien puede ejecutarla; a un
        // espectador se le informa del estado sin darle un botón vedado.
        <EstadoVacio
          titulo="Aún no hay equipos registrados."
          descripcion={
            esOrganizador
              ? 'Registra el primer equipo para empezar a programar partidos.'
              : 'Cuando la organización registre equipos, aparecerán aquí.'
          }
          accion={
            esOrganizador && id
              ? { etiqueta: 'Registrar el primer equipo', href: `/leagues/${id}/teams/new` }
              : undefined
          }
        />
      ) : (
        <Panel
          titulo="Equipos de la liga"
          acciones={
            esOrganizador && id ? (
              <Link to={`/leagues/${id}/teams/new`}>Registrar equipo</Link>
            ) : undefined
          }
        >
          <TablaDeDatos
            columnas={columnas}
            filas={equipos}
            claveDeFila={(equipo) => equipo.id}
            descripcion="Equipos registrados en la liga"
          />
        </Panel>
      )}
    </section>
  );
}
