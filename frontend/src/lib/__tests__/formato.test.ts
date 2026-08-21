/**
 * Reglas de formato compartidas — FR-009, FR-022.
 * spec 012-identidad-visual, Historia 2.
 */

import { describe, expect, it } from 'vitest';
import {
  formatearDiferencia,
  formatearFecha,
  formatearFechaHora,
  formatearMarcador,
  inicialesDeEquipo,
} from '../formato';

describe('formatearFecha', () => {
  it('usa el formato medio en español', () => {
    expect(formatearFecha('2026-08-20T19:30:00Z')).toMatch(/2026/);
    expect(formatearFecha('2026-08-20T19:30:00Z')).toMatch(/ago/i);
  });

  it('devuelve la entrada sin romper si la fecha no es válida', () => {
    expect(formatearFecha('no-es-una-fecha')).toBe('no-es-una-fecha');
  });
});

describe('formatearFechaHora', () => {
  it('añade la hora al formato de fecha', () => {
    const conHora = formatearFechaHora('2026-08-20T19:30:00Z');
    expect(conHora).toMatch(/2026/);
    expect(conHora).toMatch(/\d{1,2}:\d{2}/);
  });

  it('es el mismo formato se llame desde donde se llame', () => {
    expect(formatearFechaHora('2026-08-20T19:30:00Z')).toBe(
      formatearFechaHora('2026-08-20T19:30:00Z'),
    );
  });
});

describe('formatearMarcador', () => {
  it('usa el formato único "LOCAL 3 — 1 VISITANTE" (FR-009)', () => {
    expect(formatearMarcador('EAFIT', 3, 1, 'CES')).toBe('EAFIT 3 — 1 CES');
  });

  it('mantiene el formato con marcadores en cero', () => {
    expect(formatearMarcador('Alfa', 0, 0, 'Bravo')).toBe('Alfa 0 — 0 Bravo');
  });
});

describe('formatearDiferencia', () => {
  it('pone signo explícito en los positivos', () => {
    expect(formatearDiferencia(4)).toBe('+4');
  });

  it('deja el cero sin signo', () => {
    expect(formatearDiferencia(0)).toBe('0');
  });

  it('conserva el signo de los negativos', () => {
    expect(formatearDiferencia(-2)).toBe('-2');
  });
});

describe('inicialesDeEquipo', () => {
  it('toma la inicial de cada palabra, hasta tres', () => {
    expect(inicialesDeEquipo('Deportivo Cali')).toBe('DC');
    expect(inicialesDeEquipo('Club Atlético de Nacional')).toBe('CAD');
  });

  it('con una sola palabra toma sus tres primeras letras', () => {
    expect(inicialesDeEquipo('EAFIT')).toBe('EAF');
  });

  it('ignora los espacios sobrantes', () => {
    expect(inicialesDeEquipo('  Ingeniería   FC  ')).toBe('IF');
  });

  it('no revienta con un nombre vacío', () => {
    expect(inicialesDeEquipo('   ')).toBe('?');
  });
});
