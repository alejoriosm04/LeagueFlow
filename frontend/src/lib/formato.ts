/**
 * Reglas de formato compartidas — FR-009, FR-022.
 * Contrato: specs/012-identidad-visual/contracts/ui-contracts.md §5
 *
 * Único lugar donde se decide cómo se ve una fecha, una hora, un marcador o
 * una diferencia de goles. Ninguna pantalla vuelve a instanciar un
 * Intl.DateTimeFormat propio.
 */

const formatoFecha = new Intl.DateTimeFormat('es', { dateStyle: 'medium' });
const formatoFechaHora = new Intl.DateTimeFormat('es', {
  dateStyle: 'medium',
  timeStyle: 'short',
});

/** "20 ago 2026". Si la fecha no es válida, devuelve la entrada sin romper. */
export function formatearFecha(iso: string): string {
  try {
    const fecha = new Date(iso);
    if (Number.isNaN(fecha.getTime())) return iso;
    return formatoFecha.format(fecha);
  } catch {
    return iso;
  }
}

/** "20 ago 2026, 19:30". */
export function formatearFechaHora(iso: string): string {
  try {
    const fecha = new Date(iso);
    if (Number.isNaN(fecha.getTime())) return iso;
    return formatoFechaHora.format(fecha);
  } catch {
    return iso;
  }
}

/** "EAFIT 3 — 1 CES" — el mismo formato en toda la aplicación (FR-009). */
export function formatearMarcador(
  local: string,
  golesLocal: number,
  golesVisitante: number,
  visitante: string,
): string {
  return `${local} ${golesLocal} — ${golesVisitante} ${visitante}`;
}

/** Diferencia de goles con signo explícito en positivos: "+4", "0", "-2". */
export function formatearDiferencia(valor: number): string {
  return valor > 0 ? `+${valor}` : String(valor);
}

/**
 * Iniciales para el sustituto de escudo: hasta 3 caracteres en mayúscula.
 * "Deportivo Cali" -> "DC"; "EAFIT" -> "EAF".
 */
export function inicialesDeEquipo(nombre: string): string {
  const palabras = nombre.trim().split(/\s+/).filter(Boolean);
  if (palabras.length === 0) return '?';
  if (palabras.length === 1) return palabras[0].slice(0, 3).toUpperCase();
  return palabras
    .slice(0, 3)
    .map((palabra) => palabra[0])
    .join('')
    .toUpperCase();
}

/**
 * Misma regla que `inicialesDeEquipo`, con su propio nombre para el
 * indicador de liga y el selector de la portada (FR-040, FR-046): "iniciales
 * de equipo" no describía bien su uso ahí.
 */
export const inicialesDe = inicialesDeEquipo;
