import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Boton, CampoDeFormulario, EstadoError } from '../../components';
import { campoDelError, mensajeDeError } from '../../lib/mensajesDeError';
import { leaguesApi } from './api';

export function CreateLeagueForm() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [season, setSeason] = useState('');
  const [description, setDescription] = useState('');
  const [fallo, setFallo] = useState<unknown>(null);
  const [enviando, setEnviando] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setFallo(null);
    setEnviando(true);
    try {
      const creada = await leaguesApi.crear({ name, season, description: description || null });
      navigate(`/leagues/${creada.id}`);
    } catch (err) {
      setFallo(err);
    } finally {
      setEnviando(false);
    }
  }

  const mensaje = fallo ? mensajeDeError(fallo) : null;
  const campo = campoDelError(fallo);

  return (
    <form onSubmit={onSubmit} className="lf-formulario">
      <h1>Crear liga</h1>

      <CampoDeFormulario
        id="name"
        etiqueta="Nombre"
        requerido
        error={campo === 'name' ? mensaje : null}
      >
        <input value={name} onChange={(e) => setName(e.target.value)} required />
      </CampoDeFormulario>

      <CampoDeFormulario
        id="season"
        etiqueta="Temporada"
        requerido
        error={campo === 'season' ? mensaje : null}
      >
        <input value={season} onChange={(e) => setSeason(e.target.value)} required />
      </CampoDeFormulario>

      <CampoDeFormulario id="description" etiqueta="Descripción" ayuda="Opcional.">
        <textarea value={description} onChange={(e) => setDescription(e.target.value)} />
      </CampoDeFormulario>

      {mensaje && !campo && <EstadoError mensaje={mensaje} />}

      <div className="lf-acciones-formulario">
        <Boton type="submit" enviando={enviando}>
          Crear liga
        </Boton>
      </div>
    </form>
  );
}
