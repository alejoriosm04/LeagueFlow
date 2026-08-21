import { useState } from 'react';
import { Boton, CampoDeFormulario, EstadoError } from '../../components';
import { campoDelError, mensajeDeError } from '../../lib/mensajesDeError';
import { matchesApi } from './api';

export function ResultForm({ matchId, onSuccess }: { matchId: string; onSuccess: () => void }) {
  const [homeScore, setHomeScore] = useState('');
  const [awayScore, setAwayScore] = useState('');
  const [errorLocal, setErrorLocal] = useState<string | null>(null);
  const [fallo, setFallo] = useState<unknown>(null);
  const [enviando, setEnviando] = useState(false);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    const home = Number(homeScore);
    const away = Number(awayScore);
    if (!Number.isInteger(home) || !Number.isInteger(away) || home < 0 || away < 0) {
      setErrorLocal('Los goles deben ser enteros mayores o iguales a cero.');
      return;
    }
    setErrorLocal(null);
    setFallo(null);
    setEnviando(true);
    try {
      await matchesApi.registrarResultado(matchId, { home_score: home, away_score: away });
      onSuccess();
    } catch (err) {
      setFallo(err);
    } finally {
      setEnviando(false);
    }
  }

  const mensaje = errorLocal ?? (fallo ? mensajeDeError(fallo) : null);
  const campo = errorLocal ? null : campoDelError(fallo);

  return (
    <form onSubmit={onSubmit} className="lf-formulario">
      <h2>Registrar resultado</h2>

      <CampoDeFormulario
        id="result-home"
        etiqueta="Goles local"
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
        id="result-away"
        etiqueta="Goles visitante"
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

      {mensaje && !campo && <EstadoError mensaje={mensaje} />}

      <div className="lf-acciones-formulario">
        <Boton type="submit" enviando={enviando}>
          Registrar resultado
        </Boton>
      </div>
    </form>
  );
}
