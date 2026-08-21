import { useState } from 'react';
import { Boton, CampoDeFormulario, EstadoError } from '../../components';
import { mensajeDeError } from '../../lib/mensajesDeError';
import { matchesApi } from './api';

export function CorrectionDecisionForm({
  correctionId,
  onSuccess,
}: {
  correctionId: string;
  onSuccess: () => void;
}) {
  const [reason, setReason] = useState('');
  const [errorLocal, setErrorLocal] = useState<string | null>(null);
  const [fallo, setFallo] = useState<unknown>(null);
  const [enviando, setEnviando] = useState(false);

  async function decidir(decision: 'approved' | 'rejected') {
    if (decision === 'rejected' && !reason.trim()) {
      setErrorLocal('El motivo del rechazo es obligatorio.');
      return;
    }
    setErrorLocal(null);
    setFallo(null);
    setEnviando(true);
    try {
      await matchesApi.decidirCorreccion(correctionId, {
        decision,
        ...(decision === 'rejected' ? { decision_reason: reason.trim() } : {}),
      });
      onSuccess();
    } catch (err) {
      setFallo(err);
    } finally {
      setEnviando(false);
    }
  }

  const mensajeGeneral = fallo ? mensajeDeError(fallo) : null;

  return (
    <div className="lf-formulario">
      <CampoDeFormulario id={`decision-${correctionId}`} etiqueta="Motivo del rechazo" error={errorLocal}>
        <textarea value={reason} onChange={(e) => setReason(e.target.value)} />
      </CampoDeFormulario>

      {mensajeGeneral && <EstadoError mensaje={mensajeGeneral} />}

      <div className="lf-acciones-formulario">
        <Boton type="button" enviando={enviando} onClick={() => void decidir('approved')}>
          Aprobar
        </Boton>
        {/* Rechazar es la acción destructiva de esta pantalla (FR-007). */}
        <Boton
          type="button"
          variante="destructivo"
          disabled={enviando}
          onClick={() => void decidir('rejected')}
        >
          Rechazar
        </Boton>
      </div>
    </div>
  );
}
