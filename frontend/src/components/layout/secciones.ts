/**
 * Fuente única de la navegación de la aplicación — FR-003.
 * Contrato: specs/012-identidad-visual/contracts/ui-contracts.md §1
 *
 * `ruta` y `coincide` son campos distintos a propósito: Equipos y Jugadores
 * comparten destino (los jugadores se consultan por equipo, specs/004) pero
 * nunca deben estar activos a la vez. `aria-current="page"` se calcula contra
 * `coincide`, nunca contra `ruta`, de modo que en cualquier ruta hay como
 * máximo una sección activa (FR-004). Ver data-model.md §2.1.
 *
 * Añadir una sección es añadir una entrada aquí, nunca marcado nuevo en una
 * pantalla.
 */

export type IdDeSeccion =
  | 'dashboard'
  | 'equipos'
  | 'jugadores'
  | 'partidos'
  | 'tabla'
  | 'estadisticas';

export interface Seccion {
  id: IdDeSeccion;
  etiqueta: string;
  /** A dónde navega el ítem. */
  ruta: (leagueId: string) => string;
  /** Patrones de ruta que lo marcan activo. `:param` casa con un segmento. */
  coincide: readonly string[];
  /** Qué ofrece la sección. Lo usa la portada para presentarla (FR-034). */
  descripcion: string;
  requiereLiga: true;
}

export const secciones: readonly Seccion[] = [
  {
    id: 'dashboard',
    etiqueta: 'Dashboard',
    ruta: (id) => `/leagues/${id}/dashboard`,
    coincide: ['/leagues/:id/dashboard'],
    descripcion:
      'El pulso de la liga: resultados recientes, próximos partidos y líderes en una sola pantalla.',
    requiereLiga: true,
  },
  {
    id: 'equipos',
    etiqueta: 'Equipos',
    ruta: (id) => `/leagues/${id}/teams`,
    coincide: ['/leagues/:id/teams', '/leagues/:id/teams/new'],
    descripcion:
      'Los equipos inscritos, con su escudo y su plantilla al día.',
    requiereLiga: true,
  },
  {
    id: 'jugadores',
    etiqueta: 'Jugadores',
    // Navega al listado de equipos para elegir uno; se resalta solo en las
    // rutas de jugadores.
    ruta: (id) => `/leagues/${id}/teams`,
    coincide: ['/teams/:teamId/players', '/teams/:teamId/players/new'],
    descripcion:
      'La plantilla de cada equipo, con dorsal y posición.',
    requiereLiga: true,
  },
  {
    id: 'partidos',
    etiqueta: 'Partidos',
    ruta: (id) => `/leagues/${id}/matches`,
    coincide: ['/leagues/:id/matches', '/leagues/:id/matches/new', '/matches/:matchId'],
    descripcion:
      'Programa la jornada, registra el resultado y tramita las correcciones.',
    requiereLiga: true,
  },
  {
    id: 'tabla',
    etiqueta: 'Tabla',
    ruta: (id) => `/leagues/${id}/standings`,
    coincide: ['/leagues/:id/standings'],
    descripcion:
      'La clasificación al día: puntos, diferencia de goles y podio destacado.',
    requiereLiga: true,
  },
  {
    id: 'estadisticas',
    etiqueta: 'Estadísticas',
    // La sección "Estadísticas" del mockup aterriza en la tabla de
    // goleadores (specs/010): es la vista agregada por liga que existe hoy.
    // La ficha individual de jugador (/players/:playerId/statistics) no
    // tiene entrada propia en la navegación, pero se resalta como la misma
    // sección al llegar a ella desde un enlace de jugador.
    ruta: (id) => `/leagues/${id}/top-scorers`,
    coincide: ['/leagues/:id/top-scorers', '/players/:playerId/statistics'],
    descripcion:
      'Goleadores y rendimiento por jugador a partir de los goles registrados.',
    requiereLiga: true,
  },
];

/**
 * ¿La ruta actual activa esta sección? Compara segmento a segmento; `:param`
 * casa con cualquier segmento no vacío.
 */
export function seccionActiva(seccion: Seccion, rutaActual: string): boolean {
  const actual = rutaActual.split('/').filter(Boolean);
  return seccion.coincide.some((patron) => {
    const partes = patron.split('/').filter(Boolean);
    if (partes.length !== actual.length) return false;
    return partes.every((parte, i) => parte.startsWith(':') || parte === actual[i]);
  });
}
