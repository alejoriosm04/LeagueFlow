import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Boton, CampoDeFormulario, EstadoError, TituloDePantalla } from '../../components';
import { campoDelError, mensajeDeError } from '../../lib/mensajesDeError';
import { groupsApi } from './api';

export function GroupForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [position, setPosition] = useState('');
  const [fallo, setFallo] = useState<unknown>(null);
  const [enviando, setEnviando] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!id) return;
    setFallo(null);
    setEnviando(true);
    try {
      const posicion = position.trim() === '' ? null : Number(position);
      await groupsApi.crear(id, { name, position: posicion });
      navigate(`/leagues/${id}/groups`);
    } catch (err) {
      setFallo(err);
    } finally {
      setEnviando(false);
    }
  }

  const mensaje = fallo ? mensajeDeError(fallo) : null;
  const campo = campoDelError(fallo);
  const errorDeNombre = campo === 'name' ? mensaje : null;

  return (
    <form onSubmit={onSubmit} className="lf-formulario">
      <TituloDePantalla>Crear grupo</TituloDePantalla>

      <CampoDeFormulario id="name" etiqueta="Nombre" requerido error={errorDeNombre}>
        <input value={name} onChange={(e) => setName(e.target.value)} required />
      </CampoDeFormulario>

      <CampoDeFormulario id="position" etiqueta="Posición" ayuda="Opcional. Solo afecta el orden de presentación.">
        <input
          type="number"
          value={position}
          onChange={(e) => setPosition(e.target.value)}
        />
      </CampoDeFormulario>

      {mensaje && !campo && <EstadoError mensaje={mensaje} />}

      <div className="lf-acciones-formulario">
        <Boton type="submit" enviando={enviando}>
          Crear grupo
        </Boton>
      </div>
    </form>
  );
}
