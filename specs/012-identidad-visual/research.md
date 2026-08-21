# Phase 0 — Research: Identidad visual y experiencia de usuario consistente

**Feature**: `012-identidad-visual` | **Fecha**: 2026-08-20 |
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Esta historia **no re-decide el stack** (`AGENTS.md` §5): React 18 + TypeScript
+ Vite + React Router + Vitest/RTL vienen fijados por
[`specs/001-fundacion-y-autenticacion/plan.md`](../001-fundacion-y-autenticacion/plan.md).
Lo que se investiga aquí es exclusivamente **cómo se construye la capa de
presentación** sobre ese stack ya decidido.

## 0. Punto de partida (estado real del frontend, 2026-08-20)

Medido sobre la rama `012-identidad-visual`:

- **No existe ningún archivo CSS en el repositorio.** El único estilo es un
  bloque de `style={{…}}` en línea en `frontend/src/App.tsx` (cabecera con
  `borderBottom: '1px solid #ddd'`). Todas las demás pantallas van sin estilo.
- La cabecera actual muestra la marca, un enlace a Ligas y el estado de sesión;
  **no hay navegación lateral, ni indicador de liga en contexto, ni sección
  activa** (FR-001 a FR-006 sin cubrir).
- Cada pantalla resuelve por su cuenta carga/vacío/error con `<p>` sueltos y
  textos distintos; `StandingsPage` y `MatchesPage` los escriben de forma
  parecida pero no idéntica (FR-013 a FR-016 sin cubrir).
- `MatchesPage` ya centraliza un `Intl.DateTimeFormat('es')` **local al
  archivo**; ninguna otra pantalla lo reutiliza (FR-022 sin cubrir).
- El marcador se pinta como `3–1` en `MatchesPage` y no con el formato
  "LOCAL 3 — 1 VISITANTE" exigido por FR-009.
- `Team` ya expone `crest_url: string | null`
  (`frontend/src/features/teams/api.ts`), pero **ninguna pantalla lo renderiza**
  (FR-012 sin cubrir).
- Suite de referencia: **9 archivos, 44 pruebas, 100% en verde**
  (`npx vitest run`). Es la línea base de no regresión de FR-033 y SC-008.
- Reparto de consultas en las pruebas actuales: 28 `getByLabelText`,
  25 `findByRole`, 19 `getByRole`, 10 `queryByRole`, 7 `getAllByRole` —
  accesibles y estables frente al remarcado— y **26 consultas por texto**
  (`findByText`/`getByText`/`queryByText`/`getAllByText`), que son la zona de
  riesgo cuando el texto pase a vivir dentro de un componente compartido.
- `@playwright/test` **no está instalado** y `frontend/e2e/` está vacío a
  propósito (ver su `README.md`). No hay, por tanto, suite de extremo a extremo
  que mantener en verde: la no regresión de esta historia se mide con Vitest.

## 1. Estrategia de estilos

**Decisión**: CSS nativo con **custom properties** para los valores compartidos
(`src/styles/tokens.css`) + **CSS Modules** (`Componente.module.css`) para el
estilo de cada componente. Cero dependencias nuevas.

**Rationale**:

- Vite ya compila `.css` y `.module.css` sin configuración ni plugins: no se
  añade nada a `package.json`, no se toca `vite.config.ts`, no cambia el
  pipeline de CI.
- FR-019/FR-020 y SC-009 exigen poder **auditar** que ninguna pantalla define
  su paleta o sus tamaños. Con custom properties eso es una búsqueda mecánica:
  un color literal (`#`, `rgb(`) fuera de `tokens.css` es una violación, y se
  puede comprobar en una prueba (§9).
- CSS Modules aísla por componente, lo que evita que una pantalla pise a otra
  sin necesidad de una convención de nombres disciplinada.
- Vitest con `jsdom` no procesa CSS por defecto: los `import './X.module.css'`
  son inocuos en las pruebas y no ralentizan la suite existente.

**Alternativas descartadas**:

| Alternativa | Por qué se descarta |
|---|---|
| Tailwind CSS | Añade dependencia, configuración de build y un paso de PostCSS. Sobre todo: con utilidades en el marcado, SC-009 ("0 definiciones de paleta o tamaños propios en pantallas individuales") deja de ser auditable — cada pantalla puede escribir `p-[13px]` sin que se note. |
| CSS-in-JS (styled-components / emotion) | Dependencia en tiempo de ejecución, coste en el render y fricción con RTL. No aporta nada que las custom properties no den ya. |
| Biblioteca de componentes (MUI, Chakra) | Impone su propio sistema visual, contradice la referencia obligatoria del mockup de `docs/enunciado.md` §2 y arrastra una superficie enorme de dependencias para ocho componentes. |
| Seguir con estilos en línea | No permite `:focus-visible`, `:hover`, `@media` ni filas alternas — es decir, no puede cumplir FR-005, FR-008, FR-024 ni FR-029. |

## 2. Dónde viven los valores visuales

**Decisión**: `frontend/src/styles/tokens.css` (única fuente de verdad) +
`frontend/src/styles/global.css` (reset mínimo, tipografía base, estilo de
`:focus-visible`, comportamiento de `html/body`). Ambos se importan **una sola
vez** en `frontend/src/main.tsx`.

**Rationale**: un único punto de importación hace que ninguna pantalla pueda
"olvidarse" del sistema, y que `specs/010` y `specs/011` lo hereden sin
importar nada (SC-010). Los tokens en `:root` quedan disponibles en toda la
aplicación, incluidas las hojas de los CSS Modules.

**Alternativa descartada**: un archivo de tokens en TypeScript (`tokens.ts`)
consumido por estilos en línea — vuelve al problema de §1 y duplica el valor en
dos lenguajes.

## 3. Paleta y contraste (FR-023, SC-004)

**Decisión**: tema claro único (Assumption de la spec), con los pares de color
verificados **antes** de escribir el CSS. Ratios WCAG 2.1 calculados sobre los
valores definitivos:

| Uso | Texto | Fondo | Ratio |
|---|---|---|---|
| Texto principal sobre página | `#14213d` | `#f5f7fa` | 14.88:1 |
| Texto principal sobre panel | `#14213d` | `#ffffff` | 15.97:1 |
| Texto principal sobre fila alterna | `#14213d` | `#eef2f7` | 14.21:1 |
| Texto secundario sobre página | `#4a5568` | `#f5f7fa` | 7.01:1 |
| Texto de botón primario | `#ffffff` | `#0b4fa2` | 7.91:1 |
| Texto de botón destructivo | `#ffffff` | `#a41d1d` | 7.58:1 |
| Enlace sobre panel | `#0b4fa2` | `#ffffff` | 7.91:1 |
| Distintivo "Programado" | `#0b3f86` | `#dbe7fb` | 8.14:1 |
| Distintivo "En curso" | `#7a4b00` | `#fdecc8` | 6.35:1 |
| Distintivo "Finalizado" | `#14532d` | `#d6efdd` | 7.48:1 |
| Distintivo "Cancelado" | `#3f4650` | `#e6e8eb` | 7.76:1 |
| Fila de podio | `#14213d` | `#fff4d6` | 14.58:1 |
| Mensaje de error | `#a41d1d` | `#f5f7fa` | 7.06:1 |

El mínimo de la tabla es **6.35:1**, con margen sobre el 4.5:1 exigido, de modo
que un ajuste menor de tono no rompe el criterio. Para bordes de controles
(no texto, WCAG 1.4.11 pide 3:1) se usa `#6b7684`: 4.62:1 sobre blanco, 4.30:1
sobre la página.

**Rationale**: fijar la paleta con los ratios ya medidos convierte SC-004 en
una propiedad del sistema y no en una revisión manual pantalla por pantalla.

**Alternativa descartada**: elegir colores "de marca" primero y auditar el
contraste al final — es el orden que obliga a rehacer el CSS.

## 4. Estructura de aplicación (FR-001 a FR-006)

**Decisión**: un componente `AppShell` en `src/components/layout/` que envuelve
`<AppRoutes />` dentro de `App.tsx`, con `<header>`, `<nav>` y `<main>`
semánticos. Las secciones se declaran **una sola vez** en
`src/components/layout/secciones.ts`: Dashboard, Equipos, Jugadores, Partidos,
Tabla, Estadísticas (orden literal del mockup de `docs/enunciado.md` §2).

**Rationale**: `App.tsx` ya es el único punto por el que pasan todas las rutas,
públicas y protegidas, así que envolver ahí cubre FR-001 sin tocar
`routes.tsx`. Una lista de secciones declarativa evita que cada pantalla
reescriba la navegación (SC-001).

**Sección activa (FR-004)**: la activación **no** se delega al `end`/`isActive`
por defecto de `NavLink`, porque Equipos y Jugadores comparten destino
(`/leagues/:id/teams`) y eso dejaría dos ítems con `aria-current="page"` a la
vez. Cada sección declara sus propios patrones en `coincide`
([data-model.md](./data-model.md) §2.1) y el shell calcula contra ellos: como
máximo una sección activa en cualquier ruta, ninguna en las rutas sin liga. Se
sigue usando `NavLink` para navegar, pero `aria-current` y el estilo activo los
gobierna `coincide`. El distintivo no cromático es doble: barra lateral sólida
en el borde izquierdo del ítem + peso tipográfico. El color es el tercer canal,
nunca el único (FR-028).

**Alternativa descartada**: un `<Layout>` por ruta en `routes.tsx` — repite el
mismo envoltorio doce veces y deja fuera cualquier ruta futura por olvido.

## 5. Liga en contexto (FR-002, FR-006)

**Decisión**: hook `useLigaEnContexto()` que lee el `:id` de liga de la ruta
actual (`useMatch` sobre los patrones `/leagues/:id/*`) y resuelve el nombre
con `leaguesApi.obtener(id)`, cacheado en memoria por `id` mientras dure la
sesión de navegación. En las rutas sin liga (`/`, `/login`, `/leagues`,
`/leagues/new`) devuelve `null` y la cabecera muestra "Sin liga seleccionada".

**Rationale**: la spec es explícita (Assumption "Liga en contexto") en que se
**deriva de la navegación y no se persiste**. No hay estado global nuevo, no
hay entidad nueva, no hay endpoint nuevo — solo una lectura del contrato ya
publicado por `specs/002`.

**Caso `/matches/:matchId`** (ruta que no lleva el `:id` de liga): el partido ya
expone `league_id` en su respuesta; la pantalla de detalle informa la liga al
shell mediante el mismo hook, que acepta un `league_id` explícito como origen
alternativo. Si aún no ha cargado, el indicador muestra el estado neutro en vez
de parpadear con un valor incorrecto.

**Alternativa descartada**: guardar la última liga visitada en `localStorage` —
contradice la Assumption de la spec y produce una cabecera que miente cuando el
usuario abre una URL directa.

## 6. Navegación colapsable (FR-005, FR-029, FR-030)

**Decisión**: un `<button>` "Menú" visible solo por debajo de 768 px, con
`aria-expanded` y `aria-controls` apuntando al `<nav>`; el colapso lo gobierna
una media query, no JavaScript de medición. Tres puntos de corte: ≥1024 px
(navegación lateral fija, como el mockup), 768–1023 px (lateral estrecha),
<768 px (colapsada tras el botón).

**Rationale**: sin dependencias, sin `matchMedia` en el render (que obligaría a
mockearlo en Vitest) y operable con teclado por construcción, al ser un botón
real.

**Tablas anchas (FR-030)**: envoltorio `<div class="tabla-scroll">` con
`overflow-x: auto`, `role="region"`, `aria-label` y `tabIndex={0}` para que el
desplazamiento sea alcanzable con teclado. La página nunca desplaza en
horizontal; la tabla sí, dentro de su contenedor.

**Alternativa descartada**: convertir las tablas en tarjetas apiladas en móvil —
duplica el marcado de cada listado y rompería las consultas de las pruebas
existentes según el ancho del entorno.

## 7. Estados de pantalla (FR-013 a FR-016)

**Decisión**: tres componentes en `src/components/estado/` —`EstadoCarga`,
`EstadoVacio`, `EstadoError`— con contrato fijo:

- `EstadoCarga`: `role="status"` + `aria-live="polite"`, texto "Cargando …".
- `EstadoVacio`: título, explicación y **acción opcional**; la acción se pasa
  solo si el usuario actual puede ejecutarla (un espectador ve el estado sin
  botón, según la Assumption "Estados vacíos según permisos").
- `EstadoError`: `role="alert"`, mensaje en español y acción "Reintentar"
  cuando la pantalla puede repetir la consulta.

**Rationale**: los tres estados ya existen dispersos en cada pantalla; el
trabajo es unificarlos, no inventarlos. Centralizarlos es lo que hace medible
SC-002 y lo que garantiza FR-016 (el shell sobrevive al error porque el error
vive dentro de `<main>`, nunca lo reemplaza).

## 8. Mensajes de error en español (FR-015, SC-003)

**Decisión**: catálogo `src/lib/mensajesDeError.ts` que traduce el `code` del
envelope `{error:{code,message,field}}`
([`specs/001/contracts/conventions.md`](../001-fundacion-y-autenticacion/contracts/conventions.md))
a un texto en español, con un mensaje genérico de reserva para códigos
desconocidos y para fallos de red. **El `message` que devuelve el servidor no se
renderiza nunca directamente.**

**Rationale**: es la única forma de garantizar SC-003 ("0 casos") sin depender
de que cada endpoint responda ya traducido, y es coherente con el estándar de
seguridad de la constitución ("sin stack traces al cliente"). `ApiError` ya
expone `code`, `field` y `status`, así que no hace falta tocar `apiClient.ts`.

**Errores de campo (FR-017)**: cuando `error.field` viene informado, el mensaje
se pinta junto al campo y se asocia con `aria-describedby` + `aria-invalid`; si
no, se muestra como error de formulario.

**Alternativa descartada**: mostrar `error.message` tal cual — hoy funciona por
casualidad (el backend responde en español) y basta un mensaje nuevo sin
traducir para incumplir SC-003.

## 9. Estrategia de pruebas (FR-033, SC-008)

**Decisión**:

1. **Línea base**: las 44 pruebas actuales quedan en verde. Ninguna se borra,
   se salta ni se debilita (Principio IV).
2. **Migración de selectores**: solo se tocan las consultas por texto que el
   remarcado rompa, y siempre **hacia** `getByRole`/`getByLabelText`, nunca
   hacia `container.querySelector` ni `data-testid`.
3. **Pruebas nuevas** con Vitest + RTL para lo que esta historia sí introduce:
   shell presente en pantallas públicas y autenticadas, sección activa con
   `aria-current`, cabecera con liga/sin liga, navegación colapsada operable
   con teclado, los tres estados de pantalla, bloqueo de reenvío, sustituto de
   escudo con iniciales y formato de marcador.
4. **Contraste automatizado**: una prueba lee `tokens.css`, extrae los pares
   texto/fondo declarados y calcula el ratio WCAG, fallando por debajo de
   4.5:1. Convierte SC-004 en un gate de CI en lugar de una inspección manual.
5. **Auditoría de tokens automatizada**: una prueba recorre los `*.module.css`
   y falla si encuentra un color literal (`#rgb`, `#rrggbb`, `rgb(`, `hsl(`)
   fuera de `tokens.css`. Es la comprobación directa de SC-009.

**Fuera de alcance**: Playwright. No está instalado, `frontend/e2e/` sigue
vacío por decisión de `specs/001` y añadir la dependencia sería una decisión de
stack que `AGENTS.md` §5 no permite tomar en esta historia. Las verificaciones
visuales a 1280/768/375 px (SC-006) se hacen de forma manual reproducible según
[quickstart.md](./quickstart.md).

**Alternativa descartada**: pruebas de regresión visual por captura (snapshot
de imagen) — requieren navegador real e infraestructura de referencia; coste
desproporcionado para una historia de una sola iteración.

## 10. Piezas transversales menores

- **Formatos (FR-022)**: `src/lib/formato.ts` centraliza fecha, hora, marcador
  ("LOCAL 3 — 1 VISITANTE", FR-009) y diferencia de goles con signo. La
  instancia local de `Intl.DateTimeFormat` que hoy vive en `MatchesPage` se
  mueve ahí y esa pantalla pasa a consumirla.
- **Escudo con sustituto (FR-012)**: componente `EscudoEquipo` que renderiza
  `crest_url` cuando existe y cae al sustituto de iniciales con `onError` —
  cubre el edge case "el enlace existe pero no carga". El sustituto ocupa
  exactamente el mismo cuadro para no romper la alineación de la tabla.
- **Textos largos**: truncado con `text-overflow: ellipsis` conservando el
  texto completo en `title`, según la Assumption "Textos largos".
- **Secciones aún no construidas (FR-006, edge case)**: `Dashboard` y
  `Estadísticas` apuntan a una pantalla `PendienteDeEntrega` que declara
  explícitamente que la sección llegará con `specs/011` y `specs/010`. No es
  una pantalla de negocio nueva: no consulta datos ni introduce reglas.
- **Podio (FR-011)**: distintivo "1.º / 2.º / 3.º" como texto más medalla, con
  fondo propio. Con menos de tres equipos se destacan solo las posiciones
  existentes (Assumption de la spec).

## Riesgos identificados

| Riesgo | Mitigación |
|---|---|
| Las 26 consultas por texto de la suite se rompen al mover textos a componentes compartidos | Migrar a consultas por rol en el mismo PR (FR-033); los textos visibles que las pruebas afirman no cambian de redacción salvo que un FR lo exija |
| Alcance amplio: 8 pantallas de negocio + 7 formularios (FR-031) | Las tareas se ordenan por prioridad de historia (P1 shell → P5 responsive); cada prioridad deja la aplicación entregable |
| Tentación de "mejorar" textos o flujos al restilar | FR-032 lo prohíbe: esta historia no cambia reglas, contratos ni copys de negocio salvo los que un FR nombra explícitamente |
