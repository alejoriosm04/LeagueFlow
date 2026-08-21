import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { EstadoCarga, EstadoError, EstadoVacio, Panel, TablaDeDatos, TituloDePantalla } from '../../components';
import type { ColumnaDeTabla } from '../../components';
import { mensajeDeError } from '../../lib/mensajesDeError';
import { useAuth } from '../auth/AuthContext';
import { leaguesApi } from './api';
import type { League } from './api';

const columnas: ReadonlyArray<ColumnaDeTabla<League>> = [
  {
    clave: 'nombre',
    encabezado: 'Liga',
    celda: (liga) => <Link to={`/leagues/${liga.id}`}>{liga.name}</Link>,
  },
  { clave: 'temporada', encabezado: 'Temporada', celda: (liga) => liga.season },
  { clave: 'descripcion', encabezado: 'Descripción', celda: (liga) => liga.description ?? '—' },
];

export function LeaguesPage() {
  const { usuario } = useAuth();
  const [ligas, setLigas] = useState<League[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    setCargando(true);
    setError(null);
    leaguesApi
      .listar()
      .then((r) => setLigas(r.items))
      .catch((causa) => setError(mensajeDeError(causa)))
      .finally(() => setCargando(false));
  }, [intento]);

  // FR-027: los estados de carga y error se renderizan DENTRO de la pantalla,
  // conservando su <h1>. Retornarlos antes dejaba la página sin encabezado
  // principal justo cuando el usuario más necesita saber dónde está.
  const esOrganizador = usuario?.role === 'organizador';

  if (cargando || error) {
    return (
      <section>
        <TituloDePantalla>Ligas</TituloDePantalla>
        {cargando ? (
          <EstadoCarga recurso="las ligas" />
        ) : (
          <EstadoError mensaje={error!} onReintentar={() => setIntento((n) => n + 1)} />
        )}
      </section>
    );
  }

  if (ligas.length === 0) {
    return (
      <section>
        <TituloDePantalla>Ligas</TituloDePantalla>
        <EstadoVacio
          titulo="Aún no hay ligas registradas."
          descripcion={
            esOrganizador
              ? 'Crea la primera liga para empezar a registrar equipos y partidos.'
              : 'Cuando la organización cree una liga, aparecerá aquí.'
          }
          accion={esOrganizador ? { etiqueta: 'Crear liga', href: '/leagues/new' } : undefined}
        />
      </section>
    );
  }

  return (
    <section>
      <TituloDePantalla>Ligas</TituloDePantalla>
      <Panel
        titulo="Ligas registradas"
        acciones={esOrganizador ? <Link to="/leagues/new">Crear liga</Link> : undefined}
      >
        <TablaDeDatos
          columnas={columnas}
          filas={ligas}
          claveDeFila={(liga) => liga.id}
          descripcion="Ligas registradas en LeagueFlow"
        />
      </Panel>
    </section>
  );
}
