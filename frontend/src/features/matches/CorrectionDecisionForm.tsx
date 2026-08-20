import { useState } from 'react';
import { ApiError } from '../../services/apiClient';
import { matchesApi } from './api';

export function CorrectionDecisionForm({ correctionId, onSuccess }: { correctionId: string; onSuccess: () => void }) {
  const [reason, setReason] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function decidir(decision: 'approved' | 'rejected') {
    if (decision === 'rejected' && !reason.trim()) {
      setError('El motivo del rechazo es obligatorio.');
      return;
    }
    setError(null);
    setEnviando(true);
    try {
      await matchesApi.decidirCorreccion(correctionId, {
        decision,
        ...(decision === 'rejected' ? { decision_reason: reason.trim() } : {}),
      });
      onSuccess();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No fue posible decidir la corrección.');
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div>
      <label htmlFor={`decision-${correctionId}`}>Motivo del rechazo</label>
      <textarea id={`decision-${correctionId}`} value={reason} onChange={(e) => setReason(e.target.value)} />
      {error && <p role="alert">{error}</p>}
      <button type="button" disabled={enviando} onClick={() => void decidir('approved')}>Aprobar</button>
      <button type="button" disabled={enviando} onClick={() => void decidir('rejected')}>Rechazar</button>
    </div>
  );
}
