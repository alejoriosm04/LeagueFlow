/**
 * Contraste del sistema visual — FR-023, SC-004.
 * spec 012-identidad-visual, Historia 4.
 *
 * Convierte SC-004 en un gate de CI en lugar de una inspección manual: lee
 * los pares texto/fondo declarados en tokens.css, resuelve sus valores reales
 * y calcula el ratio WCAG 2.1. Añadir un color al sistema sin declararlo como
 * par, o bajar su contraste, hace fallar esta prueba.
 */

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { describe, expect, it } from 'vitest';

const raizEstilos = join(dirname(fileURLToPath(import.meta.url)), '..');
const tokens = readFileSync(join(raizEstilos, 'tokens.css'), 'utf8');

/** Valor de cada --lf-color-* declarado en :root. */
function leerColores(css: string): Record<string, string> {
  const colores: Record<string, string> = {};
  for (const [, nombre, valor] of css.matchAll(/--lf-color-([a-z-]+):\s*(#[0-9a-fA-F]{6});/g)) {
    colores[nombre] = valor;
  }
  return colores;
}

/** Pares declarados en el bloque `pares-de-contraste` de tokens.css. */
function leerPares(css: string): Array<[string, string]> {
  const bloque = css.match(/pares-de-contraste([\s\S]*?)fin-pares-de-contraste/);
  if (!bloque) throw new Error('tokens.css no declara el bloque pares-de-contraste');
  return [...bloque[1].matchAll(/^\s*\*?\s*([a-z-]+) sobre ([a-z-]+)\s*$/gm)].map(
    ([, frente, fondo]) => [frente, fondo],
  );
}

function luminancia(hex: string): number {
  const canales = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);
  const lineal = canales.map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4));
  return 0.2126 * lineal[0] + 0.7152 * lineal[1] + 0.0722 * lineal[2];
}

function ratio(a: string, b: string): number {
  const [claro, oscuro] = [luminancia(a), luminancia(b)].sort((x, y) => y - x);
  return (claro + 0.05) / (oscuro + 0.05);
}

const colores = leerColores(tokens);
const pares = leerPares(tokens);

describe('contraste de los tokens (FR-023)', () => {
  it('declara pares de contraste que revisar', () => {
    expect(pares.length).toBeGreaterThan(10);
  });

  it.each(pares)('%s sobre %s alcanza 4.5:1', (frente, fondo) => {
    expect(colores[frente], `--lf-color-${frente} no está declarado`).toBeDefined();
    expect(colores[fondo], `--lf-color-${fondo} no está declarado`).toBeDefined();
    expect(ratio(colores[frente], colores[fondo])).toBeGreaterThanOrEqual(4.5);
  });

  it('el borde de los controles alcanza 3:1 contra la superficie', () => {
    // No es texto, así que le aplica el umbral de componente de interfaz.
    expect(ratio(colores['borde-fuerte'], colores['superficie'])).toBeGreaterThanOrEqual(3);
  });
});
