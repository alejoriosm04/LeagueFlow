import { useState } from 'react';
import { Boton, EstadoError } from '../../components';
import { ApiError } from '../../services/apiClient';
import type { Player } from '../players/api';
import { matchesApi } from './api';
import estilos from './LineupForm.module.css';

const mensajes: Record<string, string> = {
  player_not_found: 'Uno de los jugadores seleccionados ya no existe.',
  player_not_in_match: 'El jugador no pertenece a ninguno de los dos equipos del partido.',
  player_not_in_team: 'El jugador pertenece al equipo rival de este partido.',
  lineup_conflicts_with_events:
    'No se puede excluir de la alineación a un jugador con goles ya registrados en este partido.',
};

interface Props {
  matchId: string;
  jugadoresLocal: Player[];
  jugadoresVisitante: Player[];
  seleccionLocal: string[];
  seleccionVisitante: string[];
  onSuccess: () => void;
}

function alternar(lista: string[], id: string): string[] {
  return lista.includes(id) ? lista.filter((existente) => existente !== id) : [...lista, id];
}

export function LineupForm({
  matchId,
  jugadoresLocal,
  jugadoresVisitante,
  seleccionLocal,
  seleccionVisitante,
  onSuccess,
}: Props) {
  const [local, setLocal] = useState<string[]>(seleccionLocal);
  const [visitante, setVisitante] = useState<string[]>(seleccionVisitante);
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function enviar(evento: React.FormEvent) {
    evento.preventDefault();
    setEnviando(true);
    setError(null);
    try {
      await matchesApi.guardarAlineacion(matchId, {
        home_player_ids: local,
        away_player_ids: visitante,
      });
      onSuccess();
    } catch (err) {
      const codigo = err instanceof ApiError ? err.code : '';
      setError(mensajes[codigo] ?? 'No fue posible guardar la alineación.');
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={(e) => void enviar(e)} aria-label="Editar alineación" className="lf-formulario">
      <h3>Editar alineación</h3>

      <div className={estilos.contenedorEquipos}>
        <fieldset className={estilos.fieldset}>
          <legend>Equipo local</legend>
          {jugadoresLocal.length === 0 ? (
            <p className={estilos.vacio}>Este equipo no tiene jugadores registrados.</p>
          ) : (
            <div className={estilos.lista}>
              {jugadoresLocal.map((jugador) => (
                <label key={jugador.id} className={estilos.jugador}>
                  <input
                    type="checkbox"
                    checked={local.includes(jugador.id)}
                    onChange={() => setLocal((valor) => alternar(valor, jugador.id))}
                  />
                  {jugador.name}
                </label>
              ))}
            </div>
          )}
        </fieldset>
        <fieldset className={estilos.fieldset}>
          <legend>Equipo visitante</legend>
          {jugadoresVisitante.length === 0 ? (
            <p className={estilos.vacio}>Este equipo no tiene jugadores registrados.</p>
          ) : (
            <div className={estilos.lista}>
              {jugadoresVisitante.map((jugador) => (
                <label key={jugador.id} className={estilos.jugador}>
                  <input
                    type="checkbox"
                    checked={visitante.includes(jugador.id)}
                    onChange={() => setVisitante((valor) => alternar(valor, jugador.id))}
                  />
                  {jugador.name}
                </label>
              ))}
            </div>
          )}
        </fieldset>
      </div>

      {error && <EstadoError mensaje={error} />}

      <div className="lf-acciones-formulario">
        <Boton type="submit" enviando={enviando}>
          Guardar alineación
        </Boton>
      </div>
    </form>
  );
}
