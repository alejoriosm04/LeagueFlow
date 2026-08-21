/**
 * Portada del producto — FR-034, FR-046, Historia 6.
 *
 * Es la pantalla de `/`, la primera que ve cualquiera que llega. Solo
 * consume el contrato de listado de ligas que ya publica `specs/002`
 * (FR-035): nada nuevo en la API.
 *
 * El selector de ligas (FR-046) deja elegir la liga de trabajo en una sola
 * interacción (SC-014), con sus tres estados de pantalla — carga, vacío y
 * error — igual que cualquier otra pantalla que carga datos (FR-013).
 *
 * Las tarjetas de sección se generan desde `secciones.ts`, la misma fuente que
 * alimenta la navegación: añadir una sección al producto no obliga a tocar
 * este marcado (data-model.md §2.3).
 */

import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { EstadoCarga, EstadoError, EstadoVacio } from '../../components';
import { inicialesDe } from '../../lib/formato';
import { mensajeDeError } from '../../lib/mensajesDeError';
import { useAuth } from '../auth/AuthContext';
import { secciones } from '../../components/layout/secciones';
import { leaguesApi } from '../leagues/api';
import type { League } from '../leagues/api';
import estilos from './Portada.module.css';

const CAPACIDADES = ['Programa', 'Registra', 'Corrige', 'Clasifica', 'Analiza'] as const;

const PASOS = [
  {
    titulo: 'Crea la liga',
    detalle: 'Nombre y temporada. El organizador la abre y queda visible para todos.',
  },
  {
    titulo: 'Inscribe equipos y jugadores',
    detalle: 'Cada equipo con su escudo; cada jugador con su dorsal y su posición.',
  },
  {
    titulo: 'Juega la temporada',
    detalle: 'Programa los partidos, registra resultados y goles: la tabla se actualiza sola.',
  },
];

function SelectorDeLigas() {
  const navigate = useNavigate();
  const { usuario } = useAuth();
  const [ligas, setLigas] = useState<League[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    let vigente = true;
    setError(null);
    leaguesApi
      .listar()
      .then((r) => {
        if (vigente) setLigas(r.items);
      })
      .catch((causa) => {
        if (vigente) setError(mensajeDeError(causa));
      });
    return () => {
      vigente = false;
    };
  }, [intento]);

  const esOrganizador = usuario?.role === 'organizador';

  return (
    <section className={estilos.selector} aria-labelledby="portada-selector">
      <h2 id="portada-selector" className={estilos.tituloSelector}>
        Elige una liga para empezar
      </h2>
      <p className={estilos.subtituloSelector}>
        Las secciones del menú se activan con la liga en contexto.
      </p>

      {error ? (
        <EstadoError mensaje={error} onReintentar={() => setIntento((n) => n + 1)} />
      ) : ligas === null ? (
        <EstadoCarga recurso="las ligas" />
      ) : ligas.length === 0 ? (
        <EstadoVacio
          titulo="Aún no hay ligas registradas."
          descripcion={
            esOrganizador
              ? 'Crea la primera liga para empezar a registrar equipos y partidos.'
              : 'Cuando la organización cree una liga, aparecerá aquí.'
          }
          accion={esOrganizador ? { etiqueta: 'Crear liga', href: '/leagues/new' } : undefined}
        />
      ) : (
        <ul className={estilos.listaLigas}>
          {ligas.map((liga) => (
            <li key={liga.id}>
              <button
                type="button"
                className={estilos.itemLiga}
                onClick={() => navigate(`/leagues/${liga.id}`)}
              >
                <span className={estilos.itemLigaSigla} aria-hidden="true">
                  {inicialesDe(liga.name)}
                </span>
                <span className={estilos.itemLigaTexto}>
                  <span className={estilos.itemLigaNombre}>{liga.name}</span>
                  <span className={estilos.itemLigaMeta}>Temporada {liga.season}</span>
                </span>
                <span className={estilos.itemLigaFlecha} aria-hidden="true">
                  →
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export function Portada() {
  const { usuario } = useAuth();

  return (
    <div className={estilos.portada}>
      <div className={estilos.principalFila}>
        <section className={estilos.principal}>
          {/* Formas de identidad. aria-hidden: son decoración, no contenido. */}
          <span className={estilos.orbeUno} aria-hidden="true" />
          <span className={estilos.orbeDos} aria-hidden="true" />

          <div className={estilos.principalTexto}>
            <p className={estilos.antetitulo}>Ligas amateur, gestionadas en serio</p>
            <h1 className={estilos.titulo}>LeagueFlow</h1>
            <p className={estilos.entradilla}>
              Toda la temporada en un solo lugar: equipos, jugadores, calendario, resultados y
              una clasificación que se calcula sola.
            </p>

            <div className={estilos.acciones}>
              {usuario ? (
                <Link to="/leagues" className={estilos.accionPrincipal}>
                  Ver mis ligas
                </Link>
              ) : (
                <Link to="/login" className={estilos.accionPrincipal}>
                  Iniciar sesión
                </Link>
              )}
              <Link to="/leagues" className={estilos.accionSecundaria}>
                Explorar ligas
              </Link>
            </div>

            <p className={estilos.nota}>
              {usuario ? (
                <>
                  Sesión iniciada como <strong>{usuario.username}</strong>.
                </>
              ) : (
                'Consultar es público. Iniciar sesión solo hace falta para registrar información.'
              )}
            </p>

            <ul className={estilos.capacidades}>
              {CAPACIDADES.map((capacidad) => (
                <li key={capacidad} className={estilos.capacidad}>
                  {capacidad}
                </li>
              ))}
            </ul>
          </div>
        </section>

        <SelectorDeLigas />
      </div>

      <section className={estilos.bloque} aria-labelledby="portada-secciones">
        <h2 id="portada-secciones" className={estilos.tituloBloque}>
          Qué encontrarás dentro
        </h2>
        <ul className={estilos.tarjetas}>
          {secciones.map((seccion) => (
            <li key={seccion.id} className={estilos.tarjeta}>
              <div className={estilos.tarjetaCabecera}>
                <h3 className={estilos.tarjetaTitulo}>{seccion.etiqueta}</h3>
              </div>
              <p className={estilos.tarjetaTexto}>{seccion.descripcion}</p>
            </li>
          ))}
        </ul>
      </section>

      <section className={estilos.bloque} aria-labelledby="portada-pasos">
        <h2 id="portada-pasos" className={estilos.tituloBloque}>
          Cómo se pone en marcha
        </h2>
        <ol className={estilos.pasos}>
          {PASOS.map((paso, indice) => (
            <li key={paso.titulo} className={estilos.paso}>
              <span className={estilos.pasoNumero} aria-hidden="true">
                {indice + 1}
              </span>
              <div>
                <h3 className={estilos.pasoTitulo}>{paso.titulo}</h3>
                <p className={estilos.pasoTexto}>{paso.detalle}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}
