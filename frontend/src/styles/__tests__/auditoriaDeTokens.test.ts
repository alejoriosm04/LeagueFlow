/**
 * Auditoría de tokens — FR-019, FR-020, SC-009.
 * spec 012-identidad-visual, Historia 4.
 *
 * Comprobación directa de "0 definiciones de paleta o de tamaños propios en
 * pantallas individuales": recorre todas las hojas de estilo del proyecto y
 * falla si alguna, distinta de tokens.css, declara un color literal.
 */

import { readFileSync, readdirSync, statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join, relative } from 'node:path';
import { describe, expect, it } from 'vitest';

const raizSrc = join(dirname(fileURLToPath(import.meta.url)), '..', '..');

/** Recorre src/ entero: una hoja nueva entra en la auditoría sola. */
function hojasDeEstilo(directorio: string): string[] {
  return readdirSync(directorio).flatMap((entrada) => {
    const ruta = join(directorio, entrada);
    if (statSync(ruta).isDirectory()) return hojasDeEstilo(ruta);
    return ruta.endsWith('.css') ? [ruta] : [];
  });
}

/** Colores literales: #rgb, #rrggbb, rgb(), rgba(), hsl(), hsla(). */
const LITERAL_DE_COLOR = /#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?)\s*\(/g;

const hojas: Array<[string, string]> = hojasDeEstilo(raizSrc)
  .filter((ruta) => !ruta.endsWith('tokens.css'))
  .map((ruta) => [relative(raizSrc, ruta), readFileSync(ruta, 'utf8')]);

describe('auditoría de tokens (SC-009)', () => {
  it('encuentra hojas de estilo que auditar', () => {
    expect(hojas.length).toBeGreaterThan(0);
  });

  it.each(hojas)('%s no declara ningún color literal', (nombre, contenido) => {
    const encontrados = contenido.match(LITERAL_DE_COLOR) ?? [];
    expect(
      encontrados,
      `${nombre} declara colores literales (${encontrados.join(', ')}). ` +
        'Todo color vive en styles/tokens.css y se consume con var(--lf-…).',
    ).toEqual([]);
  });

  it('todas las hojas de componente consumen el sistema por custom property', () => {
    // Una hoja de componente sin una sola var(--lf-…) es señal de que se está
    // estilando por fuera del sistema.
    for (const [nombre, contenido] of hojas.filter(([r]) => r.endsWith('.module.css'))) {
      expect(contenido, `${nombre} no usa ningún token`).toMatch(/var\(--lf-/);
    }
  });
});
