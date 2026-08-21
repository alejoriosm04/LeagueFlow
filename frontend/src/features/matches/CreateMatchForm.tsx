import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Boton, CampoDeFormulario, EstadoCarga, EstadoError, TituloDePantalla } from '../../components';
import { campoDelError, mensajeDeError } from '../../lib/mensajesDeError';
import { teamsApi } from '../teams/api';
import type { Team } from '../teams/api';
import { matchesApi } from './api';

export function CreateMatchForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [equipos, setEquipos] = useState<Team[]>([]);
  const [homeTeamId, setHomeTeamId] = useState('');
  const [awayTeamId, setAwayTeamId] = useState('');
  const [scheduledAt, setScheduledAt] = useState('');
  const [fallo, setFallo] = useState<unknown>(null);
  const [enviando, setEnviando] = useState(false);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    if (!id) return;
    teamsApi
      .listar(id)
      .then((r) => setEquipos(r.items))
      .catch((causa) => setFallo(causa))
      .finally(() => setCargando(false));
  }, [id]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!id) return;
    setFallo(null);
    setEnviando(true);
    try {
      // datetime-local es naive; lo enviamos como UTC con Z para el contrato ISO.
      const iso = scheduledAt ? new Date(scheduledAt).toISOString() : '';
      await matchesApi.crear(id, {
        home_team_id: homeTeamId,
        away_team_id: awayTeamId,
        scheduled_at: iso,
      });
      navigate(`/leagues/${id}/matches`);
    } catch (err) {
      setFallo(err);
    } finally {
      setEnviando(false);
    }
  }

  if (cargando) {
    return (
      <section className="lf-formulario">
        <TituloDePantalla>Programar partido</TituloDePantalla>
        <EstadoCarga recurso="los equipos" />
      </section>
    );
  }

  const mensaje = fallo ? mensajeDeError(fallo) : null;
  const campo = campoDelError(fallo);

  return (
    <form onSubmit={onSubmit} className="lf-formulario">
      <TituloDePantalla>Programar partido</TituloDePantalla>

      <CampoDeFormulario
        id="home"
        etiqueta="Equipo local"
        requerido
        error={campo === 'home_team_id' ? mensaje : null}
      >
        <select value={homeTeamId} onChange={(e) => setHomeTeamId(e.target.value)} required>
          <option value="">Selecciona…</option>
          {equipos.map((t) => (
            <option key={t.id} value={t.id}>
              {t.name}
            </option>
          ))}
        </select>
      </CampoDeFormulario>

      <CampoDeFormulario
        id="away"
        etiqueta="Equipo visitante"
        requerido
        error={campo === 'away_team_id' ? mensaje : null}
      >
        <select value={awayTeamId} onChange={(e) => setAwayTeamId(e.target.value)} required>
          <option value="">Selecciona…</option>
          {equipos.map((t) => (
            <option key={t.id} value={t.id}>
              {t.name}
            </option>
          ))}
        </select>
      </CampoDeFormulario>

      <CampoDeFormulario
        id="when"
        etiqueta="Fecha y hora"
        requerido
        error={campo === 'scheduled_at' ? mensaje : null}
      >
        <input
          type="datetime-local"
          value={scheduledAt}
          onChange={(e) => setScheduledAt(e.target.value)}
          required
        />
      </CampoDeFormulario>

      {mensaje && !campo && <EstadoError mensaje={mensaje} />}

      <div className="lf-acciones-formulario">
        <Boton type="submit" enviando={enviando} disabled={equipos.length < 2}>
          Programar partido
        </Boton>
      </div>
    </form>
  );
}
