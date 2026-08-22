import { useState } from 'react';
import { Boton, CampoDeFormulario, EstadoError } from '../../components';
import { mensajeDeError } from '../../lib/mensajesDeError';
import type { Player } from '../players/api';
import { eventsApi, type EventType } from './api';

interface Props {
  matchId: string;
  jugadores: Player[];
  onSuccess: () => void;
}

const ETIQUETAS: Record<Extract<EventType, 'YELLOW_CARD' | 'RED_CARD'>, string> = {
  YELLOW_CARD: 'Amarilla',
  RED_CARD: 'Roja',
};

export function CardForm({ matchId, jugadores, onSuccess }: Props) {
  const [playerId, setPlayerId] = useState('');
  const [minuto, setMinuto] = useState('0');
  const [tipo, setTipo] = useState<'YELLOW_CARD' | 'RED_CARD'>('YELLOW_CARD');
  const [fallo, setFallo] = useState<unknown>(null);
  const [enviando, setEnviando] = useState(false);

  async function enviar(evento: React.FormEvent) {
    evento.preventDefault();
    setEnviando(true);
    setFallo(null);
    try {
      await eventsApi.registrar(matchId, { player_id: playerId, minute: Number(minuto), type: tipo });
      setPlayerId('');
      setMinuto('0');
      onSuccess();
    } catch (err) {
      setFallo(err);
    } finally {
      setEnviando(false);
    }
  }

  const mensaje = fallo ? mensajeDeError(fallo) : null;

  return (
    <form onSubmit={(e) => void enviar(e)} className="lf-formulario">
      <CampoDeFormulario id="card-type" etiqueta="Tipo de tarjeta" requerido>
        <select value={tipo} onChange={(e) => setTipo(e.target.value as 'YELLOW_CARD' | 'RED_CARD')}>
          <option value="YELLOW_CARD">{ETIQUETAS.YELLOW_CARD}</option>
          <option value="RED_CARD">{ETIQUETAS.RED_CARD}</option>
        </select>
      </CampoDeFormulario>

      <CampoDeFormulario id="card-player" etiqueta="Jugador" requerido>
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

      <CampoDeFormulario id="card-minute" etiqueta="Minuto" requerido>
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
          Registrar tarjeta
        </Boton>
      </div>
    </form>
  );
}
