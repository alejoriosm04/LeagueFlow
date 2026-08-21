/**
 * Dashboard general de la liga — specs/011-dashboard-liga.
 *
 * Construida sobre el catálogo de `specs/012-identidad-visual` (SC-010):
 * mismo `Panel`, `TablaDeDatos`, `EscudoEquipo`, `GraficoDeBarras` y mismos
 * tres estados de pantalla que el resto de la aplicación.
 *
 * FR-032/FR-035: esta historia no publica ningún contrato de API nuevo. Las
 * tarjetas se calculan a partir de endpoints YA publicados por `specs/003`
 * (equipos), `specs/004` (jugadores), `specs/005` (partidos) y el resumen de
 * `specs/011`, combinados en el cliente. Ningún dato se inventa: donde el
 * dominio no tiene el campo que la maqueta da por hecho, la tarjeta se
 * adapta a lo que sí existe — ver spec.md, sección "Tarjetas del panel".
 */

import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { DestacadoDePodio, EscudoEquipo, EstadoCarga, EstadoError, EstadoVacio, GraficoDeBarras, Panel, TablaDeDatos, TituloDePantalla } from '../../components';
import type { BarraDeDatos, ColumnaDeTabla, DestacadoDeFila } from '../../components';
import { formatearDiferencia, formatearFecha, formatearFechaHora } from '../../lib/formato';
import { mensajeDeError } from '../../lib/mensajesDeError';
import { teamsApi } from '../teams/api';
import type { Team } from '../teams/api';
import { matchesApi } from '../matches/api';
import type { Match, MatchStatus } from '../matches/api';
import { playersApi } from '../players/api';
import type { StandingsRow } from '../standings/api';
import { dashboardApi } from './api';
import type { DashboardSummary } from './api';
import estilos from './DashboardPage.module.css';

type MapaDeEquipos = Record<string, Team>;

/** Últimas fechas con partidos jugados que se muestran en el gráfico. */
const FECHAS_EN_GRAFICO = 12;

function destacarPodio(fila: StandingsRow): DestacadoDeFila {
  if (fila.position === 1) return 'podio-1';
  if (fila.position === 2) return 'podio-2';
  if (fila.position === 3) return 'podio-3';
  return undefined;
}

/** `GET .../matches?status=X&page_size=1`: solo interesa `.total` (conteo
    barato, sin traer los partidos). */
async function contarPartidos(leagueId: string, status: MatchStatus): Promise<number> {
  const pagina = await matchesApi.listar(leagueId, 1, 1, status);
  return pagina.total;
}

/** Goles por fecha de partido. No hay "jornada" en el dominio de `specs/005`,
    así que se agrupa por la fecha real del calendario, que sí existe. Las
    fechas sin partidos no aparecen: no son "cero goles", son huecos. */
function golesPorFecha(partidos: Match[]): BarraDeDatos[] {
  const porFecha = new Map<string, number>();
  for (const partido of partidos) {
    const clave = partido.scheduled_at.slice(0, 10);
    const goles = (partido.home_score ?? 0) + (partido.away_score ?? 0);
    porFecha.set(clave, (porFecha.get(clave) ?? 0) + goles);
  }
  return [...porFecha.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .slice(-FECHAS_EN_GRAFICO)
    .map(([fechaIso, valor]) => ({ etiqueta: formatearFecha(fechaIso), valor }));
}

/**
 * Desenlace de los partidos ya jugados. La maqueta rotula esta tarjeta
 * "GANADOS / EMPATES / PERDIDOS", pero eso es el balance de UN equipo: a
 * nivel de liga cada victoria es también una derrota, así que "ganados" y
 * "perdidos" serían siempre el mismo número. El equivalente correcto —y que
 * sí suma el total— es cómo se repartieron esos partidos entre local,
 * empate y visitante (ver spec.md).
 */
interface Desenlaces {
  jugados: number;
  local: number;
  empates: number;
  visitante: number;
}

function desenlacesDe(partidos: Match[]): Desenlaces {
  let local = 0;
  let empates = 0;
  let visitante = 0;
  for (const partido of partidos) {
    const casa = partido.home_score ?? 0;
    const fuera = partido.away_score ?? 0;
    if (casa > fuera) local += 1;
    else if (casa < fuera) visitante += 1;
    else empates += 1;
  }
  return { jugados: partidos.length, local, empates, visitante };
}

export function DashboardPage() {
  const { id } = useParams<{ id: string }>();
  const [resumen, setResumen] = useState<DashboardSummary | null>(null);
  // Match solo trae home_team_id/away_team_id (UUIDs); el mapa id->equipo se
  // resuelve aparte con teamsApi, igual que ya hace MatchesPage.tsx.
  const [equipos, setEquipos] = useState<MapaDeEquipos>({});
  const [totalEquipos, setTotalEquipos] = useState<number | null>(null);
  const [totalJugadores, setTotalJugadores] = useState<number | null>(null);
  const [desenlaces, setDesenlaces] = useState<Desenlaces | null>(null);
  const [pendientes, setPendientes] = useState(0);
  const [goles, setGoles] = useState<BarraDeDatos[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    if (!id) return;
    let vigente = true;
    setCargando(true);
    setError(null);
    (async () => {
      try {
        const [datos, paginaEquipos, programados, enCurso, finalizados] = await Promise.all([
          dashboardApi.obtener(id),
          teamsApi.listar(id),
          contarPartidos(id, 'scheduled'),
          contarPartidos(id, 'in_progress'),
          matchesApi.listarTodos(id, 'finished'),
        ]);
        if (!vigente) return;
        const mapa: MapaDeEquipos = {};
        for (const equipo of paginaEquipos.items as Team[]) mapa[equipo.id] = equipo;
        // Un jugador por equipo, en paralelo: acotado por el número de
        // equipos de la liga (dominio de ligas amateur, specs/003).
        const plantillas = await Promise.all(
          (paginaEquipos.items as Team[]).map((equipo) =>
            playersApi.listar(equipo.id, false, 1, 1),
          ),
        );
        if (!vigente) return;
        setEquipos(mapa);
        setResumen(datos);
        setTotalEquipos(paginaEquipos.total);
        setTotalJugadores(plantillas.reduce((suma, p) => suma + p.total, 0));
        setDesenlaces(desenlacesDe(finalizados));
        setPendientes(programados + enCurso);
        setGoles(golesPorFecha(finalizados));
      } catch (causa) {
        if (vigente) setError(mensajeDeError(causa));
      } finally {
        if (vigente) setCargando(false);
      }
    })();
    return () => {
      vigente = false;
    };
  }, [id, intento]);

  const nombreEquipo = (teamId: string) => equipos[teamId]?.name ?? teamId.slice(0, 8);
  const escudoEquipo = (teamId: string) => equipos[teamId]?.crest_url ?? null;

  const totalTemporada = (desenlaces?.jugados ?? 0) + pendientes;
  const porcentajeCompletado =
    totalTemporada > 0 ? Math.round((100 * (desenlaces?.jugados ?? 0)) / totalTemporada) : 0;

  /** Badge circular + nombre, como la columna EQUIPO de la maqueta. */
  const columnas: ReadonlyArray<ColumnaDeTabla<StandingsRow>> = [
    { clave: 'Pos', encabezado: 'Pos', celda: (f) => <DestacadoDePodio posicion={f.position} /> },
    {
      clave: 'Equipo',
      encabezado: 'Equipo',
      celda: (f) => (
        <span className={estilos.celdaEquipo}>
          <EscudoEquipo nombre={f.team_name} crestUrl={escudoEquipo(f.team_id)} circular />
          {f.team_name}
        </span>
      ),
    },
    { clave: 'PJ', encabezado: 'PJ', numerica: true, celda: (f) => f.played },
    {
      clave: 'DG',
      encabezado: 'DG',
      numerica: true,
      celda: (f) => formatearDiferencia(f.goal_difference),
    },
    { clave: 'Pts', encabezado: 'Pts', numerica: true, celda: (f) => f.points },
  ];

  return (
    <section>
      <TituloDePantalla>Dashboard de la liga</TituloDePantalla>

      {cargando ? (
        <EstadoCarga recurso="el dashboard" />
      ) : error ? (
        <EstadoError mensaje={error} onReintentar={() => setIntento((n) => n + 1)} />
      ) : (
        resumen && (
          <div className={estilos.rejilla}>
            <div className={`${estilos.tarjeta} ${estilos.span5}`}>
              <Panel
                titulo="Próximo partido"
                acciones={<Link to={`/leagues/${id}/matches`}>Ver calendario</Link>}
              >
                {resumen.upcoming_matches.length === 0 ? (
                  <EstadoVacio
                    titulo="No hay próximos partidos."
                    descripcion="Cuando se programe uno, aparecerá aquí."
                  />
                ) : (
                  (() => {
                    const proximo = resumen.upcoming_matches[0];
                    return (
                      <div className={estilos.proximoPartido}>
                        {/* La maqueta rotula aquí "Jornada 13 · … · Cancha
                            Municipal". `Match` (specs/005) no tiene jornada
                            ni sede, así que se muestra lo que sí existe: la
                            fecha y hora programadas. */}
                        <p className={estilos.proximoFecha}>
                          {formatearFechaHora(proximo.scheduled_at)}
                        </p>
                        <Link to={`/matches/${proximo.id}`} className={estilos.enfrentamiento}>
                          <span className={estilos.ladoEquipo}>
                            <EscudoEquipo
                              nombre={nombreEquipo(proximo.home_team_id)}
                              crestUrl={escudoEquipo(proximo.home_team_id)}
                              tamano="lg"
                              circular
                            />
                            <span className={estilos.nombreEquipo}>
                              {nombreEquipo(proximo.home_team_id)}
                            </span>
                          </span>
                          <span className={estilos.versus}>VS</span>
                          <span className={estilos.ladoEquipo}>
                            <EscudoEquipo
                              nombre={nombreEquipo(proximo.away_team_id)}
                              crestUrl={escudoEquipo(proximo.away_team_id)}
                              tamano="lg"
                              circular
                            />
                            <span className={estilos.nombreEquipo}>
                              {nombreEquipo(proximo.away_team_id)}
                            </span>
                          </span>
                        </Link>
                      </div>
                    );
                  })()
                )}
              </Panel>
            </div>

            <div className={`${estilos.tarjeta} ${estilos.span7}`}>
              <Panel
                titulo="Rendimiento de la temporada"
                acciones={<Link to={`/leagues/${id}/top-scorers`}>Ver estadísticas</Link>}
              >
                {desenlaces && desenlaces.jugados > 0 ? (
                  <>
                    <div
                      className={estilos.barraEstado}
                      role="img"
                      aria-label={
                        `${desenlaces.local} ganados por el local, ` +
                        `${desenlaces.empates} empatados, ` +
                        `${desenlaces.visitante} ganados por el visitante`
                      }
                    >
                      <span
                        className={estilos.segmentoLocal}
                        style={{ width: `${(100 * desenlaces.local) / desenlaces.jugados}%` }}
                      />
                      <span
                        className={estilos.segmentoEmpates}
                        style={{ width: `${(100 * desenlaces.empates) / desenlaces.jugados}%` }}
                      />
                      <span
                        className={estilos.segmentoVisitante}
                        style={{ width: `${(100 * desenlaces.visitante) / desenlaces.jugados}%` }}
                      />
                    </div>
                    <dl className={estilos.metricasTemporada}>
                      <div>
                        <dt>Jugados</dt>
                        <dd>{desenlaces.jugados}</dd>
                      </div>
                      <div>
                        <dt>Gana local</dt>
                        <dd className={estilos.valorLocal}>{desenlaces.local}</dd>
                      </div>
                      <div>
                        <dt>Empates</dt>
                        <dd className={estilos.valorEmpates}>{desenlaces.empates}</dd>
                      </div>
                      <div>
                        <dt>Gana visitante</dt>
                        <dd className={estilos.valorVisitante}>{desenlaces.visitante}</dd>
                      </div>
                    </dl>
                  </>
                ) : (
                  <p className={estilos.textoVacio}>Aún no hay partidos jugados en esta liga.</p>
                )}
              </Panel>
            </div>

            <div className={`${estilos.tarjeta} ${estilos.span7}`}>
              <Panel
                titulo="Tabla de posiciones"
                acciones={<Link to={`/leagues/${id}/standings`}>Ver tabla completa</Link>}
              >
                {resumen.top_standings.length === 0 ? (
                  <EstadoVacio
                    titulo="Aún no hay equipos."
                    descripcion="La clasificación aparecerá cuando la liga tenga equipos registrados."
                  />
                ) : (
                  <TablaDeDatos
                    columnas={columnas}
                    filas={resumen.top_standings}
                    claveDeFila={(fila) => fila.team_id}
                    descripcion={`Primeros ${resumen.top_standings.length} lugares de la clasificación.`}
                    destacarFila={destacarPodio}
                  />
                )}
              </Panel>
            </div>

            {/* Una sola tarjeta de rejilla (span 5) con el gráfico arriba y
                los contadores debajo: `align-items: stretch` la estira a la
                altura de "Tabla de posiciones" sin dejar hueco al lado. */}
            <div className={`${estilos.tarjeta} ${estilos.span5} ${estilos.columnaSecundaria}`}>
              <Panel titulo="Goles por fecha">
                {goles.length === 0 ? (
                  <p className={estilos.textoVacio}>
                    Aún no hay goles registrados en partidos finalizados.
                  </p>
                ) : (
                  <GraficoDeBarras
                    datos={goles}
                    descripcion={`Goles anotados en las últimas ${goles.length} fechas con partidos.`}
                    destacarUltima
                  />
                )}
              </Panel>

              <div className={estilos.metricas}>
                <div className={estilos.metrica}>
                  <span className={estilos.metricaEtiqueta}>Equipos</span>
                  <span className={estilos.metricaValor}>{totalEquipos ?? '—'}</span>
                </div>
                <div className={estilos.metrica}>
                  <span className={estilos.metricaEtiqueta}>Jugadores</span>
                  <span className={estilos.metricaValor}>{totalJugadores ?? '—'}</span>
                </div>
              </div>

              <div className={estilos.temporadaCompletada}>
                <div className={estilos.temporadaTexto}>
                  <p className={estilos.temporadaEtiqueta}>Temporada completada</p>
                  <p className={estilos.temporadaPorcentaje}>{porcentajeCompletado}%</p>
                  <p className={estilos.temporadaDetalle}>
                    {desenlaces?.jugados ?? 0} de {totalTemporada} partidos jugados
                  </p>
                </div>
                {/* El porcentaje ya está escrito al lado: el anillo lo
                    ilustra, no es la única forma de leerlo (FR-028). */}
                <div
                  className={estilos.anillo}
                  aria-hidden="true"
                  style={{ ['--lf-anillo-pct' as string]: `${porcentajeCompletado}%` }}
                />
              </div>
            </div>
          </div>
        )
      )}
    </section>
  );
}
