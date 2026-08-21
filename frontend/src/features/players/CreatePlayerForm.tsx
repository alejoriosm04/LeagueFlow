import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Boton, CampoDeFormulario, EstadoError, TituloDePantalla } from '../../components';
import { campoDelError, mensajeDeError } from '../../lib/mensajesDeError';
import { playersApi } from './api';

export function CreatePlayerForm() {
  const { teamId } = useParams<{ teamId: string }>();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [number, setNumber] = useState('');
  const [position, setPosition] = useState('');
  const [fallo, setFallo] = useState<unknown>(null);
  const [enviando, setEnviando] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!teamId) return;
    setFallo(null);
    setEnviando(true);
    try {
      const dorsal = number.trim() === '' ? null : Number(number);
      await playersApi.crear(teamId, { name, number: dorsal, position: position || null });
      navigate(`/teams/${teamId}/players`);
    } catch (err) {
      setFallo(err);
    } finally {
      setEnviando(false);
    }
  }

  const mensaje = fallo ? mensajeDeError(fallo) : null;
  const campo = campoDelError(fallo);
  // El dorsal duplicado llega con `field: "number"`; el resto se muestra como
  // error general del formulario.
  const errorDeDorsal = campo === 'number' ? mensaje : null;

  return (
    <form onSubmit={onSubmit} className="lf-formulario">
      <TituloDePantalla>Registrar jugador</TituloDePantalla>

      <CampoDeFormulario
        id="name"
        etiqueta="Nombre"
        requerido
        error={campo === 'name' ? mensaje : null}
      >
        <input value={name} onChange={(e) => setName(e.target.value)} required />
      </CampoDeFormulario>

      <CampoDeFormulario
        id="number"
        etiqueta="Dorsal"
        ayuda="Entre 1 y 99. Opcional."
        error={errorDeDorsal}
      >
        <input
          type="number"
          min={1}
          max={99}
          value={number}
          onChange={(e) => setNumber(e.target.value)}
        />
      </CampoDeFormulario>

      <CampoDeFormulario id="position" etiqueta="Posición" ayuda="Opcional.">
        <input value={position} onChange={(e) => setPosition(e.target.value)} />
      </CampoDeFormulario>

      {mensaje && !errorDeDorsal && campo !== 'name' && <EstadoError mensaje={mensaje} />}

      <div className="lf-acciones-formulario">
        <Boton type="submit" enviando={enviando}>
          Registrar jugador
        </Boton>
      </div>
    </form>
  );
}
