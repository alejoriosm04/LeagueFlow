import { useState } from 'react';
import { Boton, CampoDeFormulario, EstadoError } from '../../components';
import { mensajeDeError } from '../../lib/mensajesDeError';
import type { Player } from '../players/api';
import { eventsApi } from './api';

interface Props {
  matchId: string;
  jugadores: Player[];
  onSuccess: () => void;
}

export function GoalForm({ matchId, jugadores, onSuccess }: Props) {
  const [playerId, setPlayerId] = useState('');
  const [minuto, setMinuto] = useState('0');
  const [fallo, setFallo] = useState<unknown>(null);
  const [enviando, setEnviando] = useState(false);

  async function enviar(evento: React.FormEvent) {
    evento.preventDefault();
    setEnviando(true);
    setFallo(null);
    try {
      await eventsApi.registrar(matchId, { player_id: playerId, minute: Number(minuto) });
      setPlayerId('');
      setMinuto('0');
      onSuccess();
    } catch (err) {
      // El catálogo de mensajes que este formulario tenía en local vive ahora
      // en lib/mensajesDeError.ts, compartido por toda la aplicación (FR-015).
      setFallo(err);
    } finally {
      setEnviando(false);
    }
  }

  const mensaje = fallo ? mensajeDeError(fallo) : null;

  return (
    <form onSubmit={(e) => void enviar(e)} className="lf-formulario">
      <CampoDeFormulario id="goal-player" etiqueta="Jugador" requerido>
        <select value={playerId} onChange={(e) => setPlayerId(e.target.value)} required>
          <option value="">Selecciona un jugador</option>
          {jugadores.map((jugador) => (
            <option key={jugador.id} value={jugador.id}>
              {jugador.name}
              {jugador.number !== null ? ` (${jugador.number})` : ''}
            </option>
          ))}
        </select>
      </CampoDeFormulario>

      <CampoDeFormulario id="goal-minute" etiqueta="Minuto" requerido>
        <input
          type="number"
          min={0}
          value={minuto}
          onChange={(e) => setMinuto(e.target.value)}
          required
        />
      </CampoDeFormulario>

      {mensaje && <EstadoError mensaje={mensaje} />}

      <div className="lf-acciones-formulario">
        <Boton type="submit" enviando={enviando}>
          Registrar gol
        </Boton>
      </div>
    </form>
  );
}
