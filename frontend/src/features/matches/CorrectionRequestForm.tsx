import { useState } from 'react';
import { Boton, CampoDeFormulario, EstadoError } from '../../components';
import { campoDelError, mensajeDeError } from '../../lib/mensajesDeError';
import { matchesApi } from './api';

export function CorrectionRequestForm({
  matchId,
  onSuccess,
}: {
  matchId: string;
  onSuccess: () => void;
}) {
  const [homeScore, setHomeScore] = useState('');
  const [awayScore, setAwayScore] = useState('');
  const [reason, setReason] = useState('');
  const [errorLocal, setErrorLocal] = useState<{ campo: string | null; texto: string } | null>(null);
  const [fallo, setFallo] = useState<unknown>(null);
  const [enviando, setEnviando] = useState(false);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!reason.trim()) {
      setErrorLocal({ campo: 'reason', texto: 'El motivo de la corrección es obligatorio.' });
      return;
    }
    const home = Number(homeScore);
    const away = Number(awayScore);
    if (
      homeScore === '' ||
      awayScore === '' ||
      !Number.isInteger(home) ||
      !Number.isInteger(away) ||
      home < 0 ||
      away < 0
    ) {
      setErrorLocal({
        campo: 'home_score',
        texto: 'Los goles deben ser enteros mayores o iguales a cero.',
      });
      return;
    }
    setErrorLocal(null);
    setFallo(null);
    setEnviando(true);
    try {
      await matchesApi.solicitarCorreccion(matchId, {
        home_score: home,
        away_score: away,
        reason: reason.trim(),
      });
      onSuccess();
    } catch (err) {
      setFallo(err);
    } finally {
      setEnviando(false);
    }
  }

  const mensaje = errorLocal?.texto ?? (fallo ? mensajeDeError(fallo) : null);
  const campo = errorLocal ? errorLocal.campo : campoDelError(fallo);

  return (
    <form onSubmit={onSubmit} noValidate className="lf-formulario">
      <h2>Solicitar corrección</h2>

      <CampoDeFormulario
        id="correction-home"
        etiqueta="Nuevo marcador local"
        requerido
        error={campo === 'home_score' ? mensaje : null}
      >
        <input
          type="number"
          min="0"
          step="1"
          required
          value={homeScore}
          onChange={(e) => setHomeScore(e.target.value)}
        />
      </CampoDeFormulario>

      <CampoDeFormulario
        id="correction-away"
        etiqueta="Nuevo marcador visitante"
        requerido
        error={campo === 'away_score' ? mensaje : null}
      >
        <input
          type="number"
          min="0"
          step="1"
          required
          value={awayScore}
          onChange={(e) => setAwayScore(e.target.value)}
        />
      </CampoDeFormulario>

      <CampoDeFormulario
        id="correction-reason"
        etiqueta="Motivo"
        requerido
        error={campo === 'reason' ? mensaje : null}
      >
        <textarea required value={reason} onChange={(e) => setReason(e.target.value)} />
      </CampoDeFormulario>

      {mensaje && !campo && <EstadoError mensaje={mensaje} />}

      <div className="lf-acciones-formulario">
        <Boton type="submit" enviando={enviando}>
          Solicitar corrección
        </Boton>
      </div>
    </form>
  );
}
