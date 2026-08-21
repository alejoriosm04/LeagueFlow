# Contrato de interfaz de usuario — `012-identidad-visual`

**Fecha**: 2026-08-20 | **Spec**: [../spec.md](../spec.md) |
**Plan**: [../plan.md](../plan.md)

> **Esta historia no publica ni modifica ningún contrato de API** (FR-032). Los
> contratos HTTP siguen siendo exactamente los de `specs/001` a `specs/009`; no
> hay `*.openapi.yaml` nuevo en esta carpeta y no lo habrá.
>
> Lo que se versiona aquí es la otra frontera del sistema: el **contrato de los
> componentes de presentación**. Es lo que `specs/010-alineaciones-estadisticas`
> y `specs/011-dashboard-liga` van a consumir sin volver a tomar decisiones de
> estilo (SC-010). Cambiarlo después es un cambio incompatible y debe
> documentarse en la spec que lo introduzca, igual que un contrato de API
> (Principio III).

Todos los componentes viven en `frontend/src/components/` y se exportan desde
`frontend/src/components/index.ts`. Nomenclatura de props en español, como el
resto del código del frontend.

## 1. Estructura de aplicación

### `AppShell`

```ts
interface AppShellProps {
  children: React.ReactNode;   // el área de contenido (<main>)
}
```

Garantiza `<header role="banner">`, `<nav aria-label="Secciones">` y `<main>`
en toda pantalla (FR-001, FR-027). No recibe la liga en contexto por props: la
resuelve con `useLigaEnContexto()`.

### `useLigaEnContexto()`

```ts
type LigaEnContexto =
  | { estado: 'sin-liga' }
  | { estado: 'cargando' }
  | { estado: 'resuelta'; leagueId: string; nombre: string }
  | { estado: 'no-encontrada'; leagueId: string };

function useLigaEnContexto(): LigaEnContexto;
```

Derivada de la ruta; no se persiste (FR-002, FR-006). **El shell la resuelve
solo: ninguna pantalla tiene que informarla.**

| Ruta | Cómo se resuelve |
|---|---|
| `/leagues/:id/…` | el id está en la ruta |
| `/teams/:teamId/…` | con el `league_id` del equipo (`specs/003`) |
| `/matches/:matchId` | con el `league_id` del partido (`specs/005`) |
| resto | sin liga |

Las dos rutas indirectas no son un adorno: sin ellas la navegación quedaría
inerte en las pantallas de jugadores y de detalle de partido, y la sección
Jugadores —cuyo `coincide` son precisamente rutas `/teams/:teamId/players`— no
podría resaltarse nunca (FR-004). Todo se cachea en memoria por id, así que la
resolución cuesta una petición la primera vez y ninguna después.

### `secciones.ts`

```ts
interface Seccion {
  id: 'dashboard' | 'equipos' | 'jugadores' | 'partidos' | 'tabla' | 'estadisticas';
  etiqueta: string;                 // texto visible, en español
  ruta: (leagueId: string) => string;      // a dónde navega el ítem
  coincide: readonly string[];             // patrones de ruta que lo marcan activo
  requiereLiga: true;
  pendiente?: 'specs/010' | 'specs/011';
}

export const secciones: readonly Seccion[];
```

Fuente única de la navegación (FR-003). Añadir una sección es añadir una
entrada aquí, nunca marcado nuevo en una pantalla.

`ruta` y `coincide` están separados porque **Equipos y Jugadores comparten
destino** (los jugadores se consultan por equipo, `specs/004`) pero nunca deben
estar activos a la vez. `aria-current="page"` se calcula contra `coincide`, de
modo que en cualquier ruta hay **como máximo una** sección activa (FR-004); en
las rutas sin liga no hay ninguna. Deducirlo de `ruta` marcaría dos ítems en
`/leagues/:id/teams`.

## 2. Catálogo de componentes

### `Panel`

```ts
interface PanelProps {
  titulo?: string;                  // se renderiza como <h2>
  acciones?: React.ReactNode;       // botones o enlaces alineados al título
  children: React.ReactNode;
}
```

### `TablaDeDatos`

```ts
interface ColumnaDeTabla<T> {
  clave: string;
  encabezado: string;
  numerica?: boolean;               // alineación a la derecha + tabular-nums (FR-008)
  celda: (fila: T) => React.ReactNode;
}

interface TablaDeDatosProps<T> {
  columnas: ReadonlyArray<ColumnaDeTabla<T>>;
  filas: readonly T[];
  claveDeFila: (fila: T) => string;
  descripcion: string;              // <caption> y aria-label del contenedor con scroll
  destacarFila?: (fila: T, indice: number) => 'podio-1' | 'podio-2' | 'podio-3' | undefined;
}
```

Encabezado diferenciado, filas alternas y envoltorio con desplazamiento propio
(`role="region"`, `tabIndex=0`) para FR-030.

### `FilaDeMarcador`

```ts
interface FilaDeMarcadorProps {
  local: { nombre: string; crestUrl?: string | null };
  visitante: { nombre: string; crestUrl?: string | null };
  golesLocal: number | null;        // null => partido sin resultado registrado
  golesVisitante: number | null;
  estado: EstadoDePartido;
  href?: string;                    // enlace al detalle del partido
}
```

Formato único "LOCAL 3 — 1 VISITANTE" (FR-009). Sin resultado, muestra "vs".

### `DistintivoDeEstado`

```ts
type EstadoDePartido = 'scheduled' | 'in_progress' | 'finished' | 'cancelled';

interface DistintivoDeEstadoProps {
  estado: EstadoDePartido;
}
```

Etiquetas fijas: **Programado**, **En curso**, **Finalizado**, **Cancelado**.
El texto es obligatorio; el color es redundante (FR-010, FR-028).

### `Boton`

```ts
interface BotonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: 'primario' | 'secundario' | 'destructivo';   // por defecto 'primario'
  enviando?: boolean;               // deshabilita, pone aria-busy y texto "Enviando…"
}
```

`enviando` es el mecanismo único de bloqueo de reenvío (FR-018).

### `CampoDeFormulario`

```ts
interface CampoDeFormularioProps {
  id: string;
  etiqueta: string;                 // <label for={id}>, obligatoria (FR-026)
  ayuda?: string;                   // ligada por aria-describedby
  error?: string | null;            // ligada por aria-describedby + aria-invalid (FR-017)
  requerido?: boolean;
  children: React.ReactNode;        // el <input>/<select>/<textarea> real
}
```

### `DestacadoDePodio`

```ts
interface DestacadoDePodioProps {
  posicion: number;                 // 1 | 2 | 3 destacan; el resto se renderiza plano
}
```

Texto "1.º/2.º/3.º" + medalla; nunca solo color (FR-011, FR-028).

### `EscudoEquipo`

```ts
interface EscudoEquipoProps {
  nombre: string;                   // origen de las iniciales del sustituto
  crestUrl?: string | null;
  tamano?: 'sm' | 'md';             // por defecto 'sm'
}
```

Si `crestUrl` falta **o falla al cargar**, muestra las iniciales ocupando el
mismo cuadro (FR-012).

## 3. Estados de pantalla

```ts
interface EstadoCargaProps {
  recurso: string;                  // "la clasificación", "los partidos"…
}

interface EstadoVacioProps {
  titulo: string;
  descripcion: string;              // qué hacer a continuación (FR-014)
  accion?: { etiqueta: string; href: string };   // solo si el rol actual puede ejecutarla
}

interface EstadoErrorProps {
  mensaje: string;                  // ya traducido por mensajesDeError (FR-015)
  onReintentar?: () => void;
}
```

## 4. Catálogo de mensajes de error

```ts
function mensajeDeError(error: unknown): string;
```

Traduce el `code` del envelope `{error:{code,message,field}}` de
[`specs/001/contracts/conventions.md`](../../001-fundacion-y-autenticacion/contracts/conventions.md)
a español. **Nunca** devuelve el `message` del servidor ni el `code` crudo; los
códigos desconocidos y los fallos de red caen en un mensaje genérico
("No fue posible completar la operación. Inténtalo de nuevo."). Garantía
verificable de FR-015 y SC-003.

## 5. Reglas de formato

```ts
function formatearFecha(iso: string): string;          // 20 ago 2026
function formatearFechaHora(iso: string): string;      // 20 ago 2026, 19:30
function formatearMarcador(local: string, gl: number, gv: number, visitante: string): string;
function formatearDiferencia(valor: number): string;   // +4 | 0 | -2
function inicialesDeEquipo(nombre: string): string;    // "Deportivo Cali" -> DC
```

## 6. Contrato de estilo

- Los valores visuales se consumen **solo** por custom property
  (`var(--lf-…)`), declaradas en `frontend/src/styles/tokens.css`. Un color,
  tamaño de fuente o espaciado literal fuera de ese archivo es una violación de
  FR-020 y falla la prueba de auditoría de tokens
  ([research.md §9](../research.md)).
- Todo elemento interactivo hereda el `:focus-visible` definido en
  `global.css`; ninguna hoja de componente puede anularlo con `outline: none`
  (FR-024).
- Ninguna información se transmite solo por color (FR-028): estado de partido,
  podio y error llevan siempre texto o forma.
