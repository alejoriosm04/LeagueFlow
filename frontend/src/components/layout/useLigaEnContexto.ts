/**
 * Liga en contexto — FR-002, FR-006.
 * Contrato: specs/012-identidad-visual/contracts/ui-contracts.md §1
 *
 * Se DERIVA de la ruta actual; no se persiste (ni localStorage ni estado
 * global). El shell la resuelve solo, sin que ninguna pantalla tenga que
 * informarla:
 *
 *   /leagues/:id/...        -> el id está en la ruta
 *   /teams/:teamId/...      -> se resuelve con el `league_id` del equipo
 *   /matches/:matchId       -> se resuelve con el `league_id` del partido
 *   resto                   -> sin liga
 *
 * Las dos rutas indirectas importan para FR-004: sin ellas, la navegación
 * quedaría inerte en las pantallas de jugadores y de detalle de partido, y la
 * sección Jugadores no podría resaltarse nunca.
 *
 * Todo se cachea en memoria por id mientras dure la navegación, así que la
 * resolución cuesta una petición la primera vez y ninguna después.
 */

import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { leaguesApi } from '../../features/leagues/api';
import { matchesApi } from '../../features/matches/api';
import { teamsApi } from '../../features/teams/api';

export type LigaEnContexto =
  | { estado: 'sin-liga' }
  | { estado: 'cargando' }
  | { estado: 'resuelta'; leagueId: string; nombre: string }
  | { estado: 'no-encontrada'; leagueId: string };

const nombrePorLiga = new Map<string, string>();
const ligaPorEquipo = new Map<string, string>();
const ligaPorPartido = new Map<string, string>();

/** Qué hay que resolver para saber la liga de esta ruta. */
type Origen =
  | { tipo: 'ninguno' }
  | { tipo: 'liga'; id: string }
  | { tipo: 'equipo'; id: string }
  | { tipo: 'partido'; id: string };

function origenDeLaRuta(pathname: string): Origen {
  const partes = pathname.split('/').filter(Boolean);
  // `new` es la pantalla de creación, no un identificador.
  if (partes[0] === 'leagues' && partes[1] && partes[1] !== 'new') {
    return { tipo: 'liga', id: partes[1] };
  }
  if (partes[0] === 'teams' && partes[1]) return { tipo: 'equipo', id: partes[1] };
  if (partes[0] === 'matches' && partes[1]) return { tipo: 'partido', id: partes[1] };
  return { tipo: 'ninguno' };
}

async function resolverLeagueId(origen: Origen): Promise<string | null> {
  switch (origen.tipo) {
    case 'liga':
      return origen.id;
    case 'equipo': {
      const cacheado = ligaPorEquipo.get(origen.id);
      if (cacheado) return cacheado;
      const equipo = await teamsApi.obtener(origen.id);
      ligaPorEquipo.set(origen.id, equipo.league_id);
      return equipo.league_id;
    }
    case 'partido': {
      const cacheado = ligaPorPartido.get(origen.id);
      if (cacheado) return cacheado;
      const partido = await matchesApi.obtener(origen.id);
      ligaPorPartido.set(origen.id, partido.league_id);
      return partido.league_id;
    }
    default:
      return null;
  }
}

export function useLigaEnContexto(): LigaEnContexto {
  const { pathname } = useLocation();
  const origen = origenDeLaRuta(pathname);
  const claveDeOrigen = `${origen.tipo}:${'id' in origen ? origen.id : ''}`;

  const [liga, setLiga] = useState<LigaEnContexto>(() =>
    origen.tipo === 'ninguno' ? { estado: 'sin-liga' } : { estado: 'cargando' },
  );

  useEffect(() => {
    const actual = origenDeLaRuta(pathname);
    if (actual.tipo === 'ninguno') {
      setLiga({ estado: 'sin-liga' });
      return;
    }

    let vigente = true;
    setLiga({ estado: 'cargando' });

    void (async () => {
      try {
        const leagueId = await resolverLeagueId(actual);
        if (!vigente) return;
        if (!leagueId) {
          setLiga({ estado: 'sin-liga' });
          return;
        }
        const cacheado = nombrePorLiga.get(leagueId);
        if (cacheado) {
          setLiga({ estado: 'resuelta', leagueId, nombre: cacheado });
          return;
        }
        const ligaResuelta = await leaguesApi.obtener(leagueId);
        nombrePorLiga.set(ligaResuelta.id, ligaResuelta.name);
        if (vigente) {
          setLiga({ estado: 'resuelta', leagueId, nombre: ligaResuelta.name });
        }
      } catch {
        if (!vigente) return;
        const id = 'id' in actual ? actual.id : '';
        setLiga({ estado: 'no-encontrada', leagueId: id });
      }
    })();

    return () => {
      vigente = false;
    };
    // `claveDeOrigen` resume el origen: cambia solo cuando cambia lo que hay
    // que resolver, no en cada navegación dentro de la misma liga.
  }, [claveDeOrigen, pathname]);

  return liga;
}
