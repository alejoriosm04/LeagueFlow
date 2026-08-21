/**
 * Estructura de aplicación compartida por todas las pantallas — FR-001,
 * FR-040 a FR-042.
 *
 * Garantiza <header role="banner">, <nav aria-label="Secciones"> y <main> en
 * toda pantalla, pública o autenticada (FR-027). No recibe la liga por props:
 * la resuelve con useLigaEnContexto().
 *
 * Marco de aplicación (FR-040): un lienzo claro enmarca una única superficie
 * de marca (`.marco`) que contiene la barra lateral, la cabecera de pantalla
 * y el área de contenido. El contenido se presenta como una superficie clara
 * elevada sobre esa marca (FR-043), así que las pantallas existentes —con su
 * `<h1>` y sus `Panel` en colores claros— no necesitan cambiar para vivir
 * dentro del marco nuevo.
 *
 * La sección activa se calcula contra `coincide`, NUNCA contra `ruta`: Equipos
 * y Jugadores comparten destino, así que deducirlo de la ruta dejaría dos
 * ítems con aria-current="page" a la vez (FR-004, data-model.md §2.1).
 *
 * Sin liga en contexto la navegación NO pinta las seis secciones (FR-006
 * enmendado, SC-011): una lista de elementos deshabilitados ocupa el sitio de
 * la navegación real sin poder usarse. En su lugar queda un único acceso al
 * listado de ligas, que es el paso que de verdad desbloquea las secciones.
 */

import { useState } from 'react';
import type { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { EstadoDeSesion } from './EstadoDeSesion';
import { IconoSeccion } from './IconoSeccion';
import { IndicadorDeLiga } from './IndicadorDeLiga';
import { secciones, seccionActiva } from './secciones';
import { useLigaEnContexto } from './useLigaEnContexto';
import estilos from './AppShell.module.css';

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const { pathname } = useLocation();
  const [navAbierta, setNavAbierta] = useState(false);
  const liga = useLigaEnContexto();
  const leagueId = liga.estado === 'resuelta' ? liga.leagueId : null;
  // Mientras se resuelve no se anuncia la ausencia de liga: es un estado
  // transitorio, no una ausencia. Se reserva el hueco para que el contenido
  // no salte al llegar la respuesta.
  const resolviendo = liga.estado === 'cargando';

  return (
    <div className={estilos.lienzo}>
      <a href="#contenido" className="lf-salto-a-contenido">
        Saltar al contenido
      </a>

      <div className={estilos.marco}>
        <aside className={estilos.aside}>
          <div className={estilos.filaMarca}>
            {/* Dos tramos de color por diseño; el nombre accesible se fija
                explícito para que no dependa de cómo el navegador concatene
                el texto de los dos <span>. */}
            <Link to="/" className={estilos.marca} aria-label="LEAGUEFLOW">
              <span className={estilos.marcaLeague} aria-hidden="true">
                LEAGUE
              </span>
              <span className={estilos.marcaFlow} aria-hidden="true">
                FLOW
              </span>
            </Link>
            {/* Sin secciones que colapsar no hay nada que abrir: el botón
                solo existe cuando la navegación tiene una lista detrás
                (FR-005). */}
            {(leagueId || resolviendo) && (
              <button
                type="button"
                className={estilos.botonMenu}
                aria-expanded={navAbierta}
                aria-controls="navegacion-secciones"
                onClick={() => setNavAbierta((abierta) => !abierta)}
              >
                Menú
              </button>
            )}
          </div>

          <nav
            id="navegacion-secciones"
            aria-label="Secciones"
            className={[estilos.navegacion, leagueId ? '' : estilos.compacta, navAbierta ? estilos.abierta : '']
              .filter(Boolean)
              .join(' ')}
          >
            {leagueId ? (
              <ul className={estilos.lista}>
                {secciones.map((seccion) => {
                  const activa = seccionActiva(seccion, pathname);
                  return (
                    <li key={seccion.id}>
                      <Link
                        to={seccion.ruta(leagueId)}
                        className={`${estilos.item} ${activa ? estilos.activo : ''}`}
                        aria-current={activa ? 'page' : undefined}
                      >
                        <IconoSeccion id={seccion.id} />
                        {seccion.etiqueta}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            ) : (
              <div className={estilos.sinLiga} aria-busy={resolviendo || undefined}>
                {!resolviendo && (
                  <>
                    <p className={estilos.avisoSinLiga}>
                      Selecciona una liga para navegar sus secciones.
                    </p>
                    {/* Estando ya en el listado, el enlace apuntaría a la
                        propia pantalla: el acceso que pide FR-006 ya está
                        cumplido. */}
                    {pathname !== '/leagues' && (
                      <Link to="/leagues" className={estilos.accesoLigas}>
                        Ver ligas
                      </Link>
                    )}
                  </>
                )}
              </div>
            )}
          </nav>
        </aside>

        <div className={estilos.columna}>
          <header className={estilos.cabecera}>
            <div className={estilos.liga}>
              <IndicadorDeLiga />
            </div>
            <EstadoDeSesion />
          </header>

          <main id="contenido" className={estilos.contenido}>
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
