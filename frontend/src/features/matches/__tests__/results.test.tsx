import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { ResultForm } from '../ResultForm';
import { CorrectionRequestForm } from '../CorrectionRequestForm';
import { CorrectionDecisionForm } from '../CorrectionDecisionForm';

vi.mock('../api', () => ({
  matchesApi: {
    registrarResultado: vi.fn().mockResolvedValue({ status: 'finished' }),
    solicitarCorreccion: vi.fn().mockResolvedValue({ status: 'pending' }),
    decidirCorreccion: vi.fn().mockResolvedValue({ status: 'approved' }),
  },
}));

describe('flujo de resultados', () => {
  it('valida y registra un marcador no negativo', async () => {
    const onSuccess = vi.fn();
    render(<ResultForm matchId="m1" onSuccess={onSuccess} />);
    fireEvent.change(screen.getByLabelText('Goles local'), { target: { value: '3' } });
    fireEvent.change(screen.getByLabelText('Goles visitante'), { target: { value: '1' } });
    fireEvent.click(screen.getByRole('button', { name: 'Registrar resultado' }));
    await waitFor(() => expect(onSuccess).toHaveBeenCalled());
  });

  it('exige motivo para solicitar corrección', async () => {
    render(<CorrectionRequestForm matchId="m1" onSuccess={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: 'Solicitar corrección' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('motivo');
  });

  it('exige motivo al rechazar', async () => {
    render(<CorrectionDecisionForm correctionId="c1" onSuccess={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: 'Rechazar' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('motivo');
  });
});
