/*
 * Catálogo de componentes compartidos — spec 012-identidad-visual.
 * Contrato: specs/012-identidad-visual/contracts/ui-contracts.md
 *
 * Toda pantalla consume desde aquí. Añadir un componente al catálogo es
 * añadir su export en este archivo (SC-010).
 */

/* --- Estructura de aplicación --- */
export { AppShell } from './layout/AppShell';
export { TituloDePantalla } from './layout/TituloDePantalla';
export { secciones, seccionActiva } from './layout/secciones';
export type { Seccion, IdDeSeccion } from './layout/secciones';
export { useLigaEnContexto } from './layout/useLigaEnContexto';
export type { LigaEnContexto } from './layout/useLigaEnContexto';

/* --- Catálogo de datos --- */
export { Panel } from './datos/Panel';
export { TablaDeDatos } from './datos/TablaDeDatos';
export type { ColumnaDeTabla, DestacadoDeFila } from './datos/TablaDeDatos';
export { DistintivoDeEstado, etiquetaDeEstado } from './datos/DistintivoDeEstado';
export type { EstadoDePartido } from './datos/DistintivoDeEstado';
export { FilaDeMarcador } from './datos/FilaDeMarcador';
export { DestacadoDePodio } from './datos/DestacadoDePodio';
export { EscudoEquipo } from './datos/EscudoEquipo';
export { GraficoDeBarras } from './datos/GraficoDeBarras';
export type { BarraDeDatos } from './datos/GraficoDeBarras';

/* --- Estados de pantalla --- */
export { EstadoCarga } from './estado/EstadoCarga';
export { EstadoVacio } from './estado/EstadoVacio';
export { EstadoError } from './estado/EstadoError';

/* --- Formulario --- */
export { Boton } from './formulario/Boton';
export { CampoDeFormulario } from './formulario/CampoDeFormulario';
