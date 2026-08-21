import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Boton, CampoDeFormulario, EstadoError } from '../../components';
import { campoDelError, mensajeDeError } from '../../lib/mensajesDeError';
import { teamsApi } from './api';

export function CreateTeamForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [crestUrl, setCrestUrl] = useState('');
  const [colors, setColors] = useState('');
  const [fallo, setFallo] = useState<unknown>(null);
  const [enviando, setEnviando] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!id) return;
    setFallo(null);
    setEnviando(true);
    try {
      await teamsApi.crear(id, { name, crest_url: crestUrl || null, colors: colors || null });
      navigate(`/leagues/${id}/teams`);
    } catch (err) {
      setFallo(err);
    } finally {
      setEnviando(false);
    }
  }

  const mensaje = fallo ? mensajeDeError(fallo) : null;
  const campo = campoDelError(fallo);
  // El nombre duplicado es el error de campo típico de esta pantalla: el
  // envelope informa `field: "name"` y el mensaje se pinta junto al campo.
  // Un error sin campo (permisos, red) NO se pinta ahí: iría junto a un campo
  // que no tiene nada que ver, así que se muestra como error del formulario.
  const errorDeNombre = campo === 'name' ? mensaje : null;

  return (
    <form onSubmit={onSubmit} className="lf-formulario">
      <h1>Registrar equipo</h1>

      <CampoDeFormulario id="name" etiqueta="Nombre" requerido error={errorDeNombre}>
        <input value={name} onChange={(e) => setName(e.target.value)} required />
      </CampoDeFormulario>

      <CampoDeFormulario
        id="crestUrl"
        etiqueta="Escudo"
        ayuda="URL https del escudo. Opcional: si falta, se muestran las iniciales del equipo."
        error={campo === 'crest_url' ? mensaje : null}
      >
        <input value={crestUrl} onChange={(e) => setCrestUrl(e.target.value)} />
      </CampoDeFormulario>

      <CampoDeFormulario id="colors" etiqueta="Colores" ayuda="Opcional.">
        <input value={colors} onChange={(e) => setColors(e.target.value)} />
      </CampoDeFormulario>

      {mensaje && !campo && <EstadoError mensaje={mensaje} />}

      <div className="lf-acciones-formulario">
        <Boton type="submit" enviando={enviando}>
          Registrar equipo
        </Boton>
      </div>
    </form>
  );
}
