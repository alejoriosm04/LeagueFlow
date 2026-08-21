/**
 * Tipos mínimos de los builtins de Node que usan las dos pruebas de sistema
 * de esta carpeta (contraste y auditoría de tokens).
 *
 * Por qué existe este archivo en vez de `@types/node`: el plan de la spec
 * 012-identidad-visual es de **cero dependencias nuevas**, y `AGENTS.md` §5
 * reserva las decisiones de stack a `specs/001`. Estas dos pruebas necesitan
 * leer archivos .css reales del disco —es justo lo que auditan— y no pueden
 * hacerlo con `import.meta.glob`: Vitest no procesa CSS, así que `?raw`
 * devuelve el proxy de CSS Modules e `?inline` devuelve una cadena vacía, lo
 * que dejaría la auditoría pasando en vacío. Declarar aquí las cuatro
 * funciones que se usan mantiene el type-check estricto sin tocar
 * package.json.
 */

declare module 'node:fs' {
  export function readFileSync(ruta: string, codificacion: 'utf8'): string;
  export function readdirSync(ruta: string): string[];
  export function statSync(ruta: string): { isDirectory(): boolean };
}

declare module 'node:path' {
  export function join(...partes: string[]): string;
  export function dirname(ruta: string): string;
  export function relative(desde: string, hasta: string): string;
}

declare module 'node:url' {
  export function fileURLToPath(url: string | URL): string;
}
