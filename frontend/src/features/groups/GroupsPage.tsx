import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Boton, EstadoCarga, EstadoError, EstadoVacio, Panel, TituloDePantalla } from '../../components';
import { mensajeDeError } from '../../lib/mensajesDeError';
import { useAuth } from '../auth/AuthContext';
import { teamsApi } from '../teams/api';
import { groupsApi } from './api';
import type { GroupWithTeams } from './api';

export function GroupsPage() {
  const { id } = useParams<{ id: string }>();
  const { usuario } = useAuth();
  const [grupos, setGrupos] = useState<GroupWithTeams[]>([]);
  const [equipos, setEquipos] = useState<{ id: string; name: string }[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [intento, setIntento] = useState(0);
  const [seleccion, setSeleccion] = useState<Record<string, string>>({});

  const esOrganizador = usuario?.role === 'organizador';

  useEffect(() => {
    if (!id) return;
    setCargando(true);
    setError(null);
    Promise.all([groupsApi.listar(id), teamsApi.listar(id)])
      .then(([g, t]) => {
        setGrupos(g.items);
        setEquipos(t.items.map((e) => ({ id: e.id, name: e.name })));
      })
      .catch((causa) => setError(mensajeDeError(causa)))
      .finally(() => setCargando(false));
  }, [id, intento]);

  async function recargar() {
    setIntento((n) => n + 1);
  }

  async function eliminar(grupoId: string) {
    if (!id) return;
    try {
      await groupsApi.eliminar(grupoId);
      await recargar();
    } catch (causa) {
      setError(mensajeDeError(causa));
    }
  }

  async function asignar(grupoId: string) {
    const teamId = seleccion[grupoId];
    if (!teamId) return;
    try {
      await groupsApi.asignar(grupoId, teamId);
      await recargar();
    } catch (causa) {
      setError(mensajeDeError(causa));
    }
  }

  async function desasignar(grupoId: string, teamId: string) {
    try {
      await groupsApi.desasignar(grupoId, teamId);
      await recargar();
    } catch (causa) {
      setError(mensajeDeError(causa));
    }
  }

  if (cargando || error) {
    return (
      <section>
        <TituloDePantalla>Grupos</TituloDePantalla>
        {cargando ? (
          <EstadoCarga recurso="los grupos" />
        ) : (
          <EstadoError mensaje={error!} onReintentar={() => setIntento((n) => n + 1)} />
        )}
      </section>
    );
  }

  return (
    <section>
      <TituloDePantalla>Grupos</TituloDePantalla>

      {grupos.length === 0 ? (
        <EstadoVacio
          titulo="Aún no hay grupos en esta liga."
          descripcion={
            esOrganizador
              ? 'Crea el primer grupo para organizar los equipos por división.'
              : 'Cuando la organización defina grupos, aparecerán aquí.'
          }
          accion={
            esOrganizador && id ? { etiqueta: 'Crear el primer grupo', href: `/leagues/${id}/groups/new` } : undefined
          }
        />
      ) : (
        <div>
          {esOrganizador && id && (
            <p>
              <Link to={`/leagues/${id}/groups/new`}>Crear grupo</Link>
            </p>
          )}
          {grupos.map((grupo) => (
            <Panel
              key={grupo.id}
              titulo={grupo.name}
              acciones={
                esOrganizador ? (
                  <Boton variante="destructivo" type="button" onClick={() => eliminar(grupo.id)}>
                    Eliminar
                  </Boton>
                ) : undefined
              }
            >
              {grupo.teams.length === 0 ? (
                <p>Sin equipos asignados.</p>
              ) : (
                <ul>
                  {grupo.teams.map((t) => (
                    <li key={t.team_id}>
                      {t.name}
                      {t.status === 'inactive' ? ' (inactivo)' : ''}
                      {esOrganizador && (
                        <Boton
                          variante="secundario"
                          type="button"
                          onClick={() => desasignar(grupo.id, t.team_id)}
                        >
                          Desasignar
                        </Boton>
                      )}
                    </li>
                  ))}
                </ul>
              )}

              {esOrganizador && (
                <div>
                  <select
                    aria-label={`Equipo para asignar a ${grupo.name}`}
                    value={seleccion[grupo.id] ?? ''}
                    onChange={(e) => setSeleccion((s) => ({ ...s, [grupo.id]: e.target.value }))}
                  >
                    <option value="">Elegir equipo…</option>
                    {equipos
                      .filter((e) => !grupo.teams.some((t) => t.team_id === e.id))
                      .map((e) => (
                        <option key={e.id} value={e.id}>
                          {e.name}
                        </option>
                      ))}
                  </select>
                  <Boton
                    variante="secundario"
                    type="button"
                    disabled={!seleccion[grupo.id]}
                    onClick={() => asignar(grupo.id)}
                  >
                    Asignar
                  </Boton>
                </div>
              )}
            </Panel>
          ))}
        </div>
      )}
    </section>
  );
}
