# Phase 1 — Modelo de la capa de presentación

**Feature**: `012-identidad-visual` | **Fecha**: 2026-08-20 |
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

> **Esta historia no añade entidades de datos, campos ni migraciones**
> (FR-032). El modelo de dominio persistido sigue siendo exactamente el de
> [`specs/001-fundacion-y-autenticacion/data-model.md`](../001-fundacion-y-autenticacion/data-model.md):
> `User`, `Session`, `League`, `Team`, `Player`, `Match`, `MatchEvent`,
> `ResultCorrectionRequest`. Nada de lo que sigue se persiste.
>
> Lo que este documento modela es el **vocabulario de la capa de presentación**
> que `specs/010` y `specs/011` heredan sin volver a decidirlo (SC-010).

## 1. Sistema de valores visuales (tokens)

Fuente única de verdad: `frontend/src/styles/tokens.css`, declarados en
`:root`. Ninguna pantalla define color, tipografía, espaciado, radio o sombra
propios (FR-019, FR-020, SC-009).

### 1.1 Color

| Token | Valor | Uso |
|---|---|---|
| `--lf-color-fondo` | `#eaf1fa` | Fondo de la página (azul muy claro) |
| `--lf-color-superficie` | `#ffffff` | Panel, tarjeta, fila impar de tabla |
| `--lf-color-superficie-alt` | `#e2eaf5` | Encabezado de tabla, fila alterna |
| `--lf-color-texto` | `#14213d` | Texto principal |
| `--lf-color-texto-suave` | `#4a5568` | Texto secundario, ayuda de campo |
| `--lf-color-borde` | `#d3deeb` | Separadores y bordes decorativos |
| `--lf-color-borde-fuerte` | `#6b7684` | Borde de controles de formulario (≥3:1) |
| `--lf-color-primario` | `#0b4fa2` | Botón primario, enlace, acento activo |
| `--lf-color-primario-fuerte` | `#083b7c` | `:hover` / `:active` del primario |
| `--lf-color-primario-tinte` | `#dbe7fb` | Fondo de sección activa y distintivo "Programado" |
| `--lf-color-peligro` | `#a41d1d` | Botón destructivo, texto de error |
| `--lf-color-peligro-tinte` | `#fbe4e4` | Fondo de bloque de error |
| `--lf-color-exito` | `#14532d` | Distintivo "Finalizado" |
| `--lf-color-exito-tinte` | `#d6efdd` | Fondo del distintivo "Finalizado" |
| `--lf-color-aviso` | `#7a4b00` | Distintivo "En curso" |
| `--lf-color-aviso-tinte` | `#fdecc8` | Fondo del distintivo "En curso" |
| `--lf-color-neutro` | `#3f4650` | Distintivo "Cancelado" |
| `--lf-color-neutro-tinte` | `#e6e8eb` | Fondo del distintivo "Cancelado" |
| `--lf-color-podio` | `#fff4d6` | Fondo de las filas 1.ª–3.ª |
| `--lf-color-marca-fondo` | `#33465e` | Extremo claro del degradado de marca; par de contraste de FR-038 |
| `--lf-color-marca-fondo-alto` | `#1e2c40` | Extremo oscuro del degradado de marca |
| `--lf-color-marca-fondo-suave` | `#47607e` | Tercer punto del degradado y superficies de marca planas |
| `--lf-color-marca-texto` | `#d7e2ee` | Texto secundario sobre superficie de marca |
| `--lf-color-acento` | `#a04d0d` | Acento cálido: datos destacados e identidad (FR-037) |
| `--lf-color-acento-tinte` | `#fde8d0` | Fondo suave del acento |
| `--lf-color-acento-claro` | `#f2a65a` | Acento sobre superficie de marca oscura |

El acento **no** es un color de acción ni de error: el azul sigue siendo la
acción (botón primario, enlace, sección activa) y el rojo sigue reservado a
error y acción destructiva (FR-037).

Ratios de contraste medidos de cada par en uso: [research.md §3](./research.md).
Mínimo real del sistema, medido sobre los 30 pares declarados en `tokens.css`:
**4.76:1** (`acento-claro` sobre `marca-fondo`), por encima del 4.5:1 que
exige FR-023. La prueba `styles/__tests__/contraste.test.ts` lo verifica en
cada ejecución.

### 1.2 Tipografía

| Token | Valor |
|---|---|
| `--lf-fuente-base` | pila del sistema (`system-ui`, `Segoe UI`, `Roboto`, `Helvetica Neue`, `Arial`, `sans-serif`) |
| `--lf-fuente-numerica` | igual que la base con `font-variant-numeric: tabular-nums` |
| `--lf-texto-xs` … `--lf-texto-2xl` | `0.75 / 0.875 / 1 / 1.125 / 1.375 / 1.75 rem` |
| `--lf-texto-3xl` / `--lf-texto-4xl` | `2.5 / 3.25 rem` (titulares de la portada) |
| `--lf-interlineado-titulo` | `1.15` |
| `--lf-espaciado-marca` | `0.14em` (interletraje de la marca tipográfica) |
| `--lf-peso-normal` / `--lf-peso-medio` / `--lf-peso-fuerte` | `400 / 600 / 700` |
| `--lf-interlineado` | `1.5` |

No se alojan fuentes propias en el repositorio (Assumption "Activos alojados").

### 1.3 Espaciado, borde y sombra

| Token | Valor |
|---|---|
| `--lf-espacio-1` … `--lf-espacio-8` | `0.25 / 0.5 / 0.75 / 1 / 1.5 / 2 / 3 / 4 rem` |
| `--lf-radio-sm` / `--lf-radio-md` / `--lf-radio-lg` / `--lf-radio-xl` | `4px / 8px / 12px / 20px` |
| `--lf-radio-pastilla` | `999px` (distintivos y píldoras) |
| `--lf-sombra-1` | sombra sutil de panel |
| `--lf-sombra-2` | sombra de elemento elevado (navegación colapsada abierta) |
| `--lf-sombra-3` | sombra de tarjeta destacada |
| `--lf-sombra-marca` | sombra del bloque principal de la portada |
| `--lf-transicion` | `160ms ease` — foco, `:hover` y apertura de la navegación |
| `--lf-ancho-nav` | `236px` |
| `--lf-ancho-contenido` | `1180px` |
| `--lf-corte-tablet` / `--lf-corte-movil` | `1024px` / `768px` (documentados aquí; las media queries usan el literal, que CSS no admite en `@media`) |

### 1.3b Marco de aplicación (FR-040 a FR-045)

Tokens añadidos al ampliar el marco sobre una maqueta de referencia aportada
por el equipo (`LeagueFlow Wow`, Claude Design — spec.md, Assumption "Maqueta
de referencia del marco").

| Token | Valor | Uso |
|---|---|---|
| `--lf-color-marca-superficie` | `#3d5470` | Sólido equivalente de una tarjeta translúcida sobre la marca; par de contraste de FR-038 |
| `--lf-color-marca-borde` | `#94abc4` | Borde de control sobre superficie de marca (≥3:1) |
| `--lf-color-fondo-alto` | `#dbe4f1` | Extremo exterior del lienzo que enmarca el marco |
| `--lf-color-marca-superponer-sutil` / `-fuerte` | blanco 8% / 16% | `:hover` e ítem activo de la navegación sobre la marca |
| `--lf-color-marca-superponer` | blanco 12% | Chips de la cabecera (liga en contexto) |
| `--lf-color-marca-borde-sutil` / `-medio` | blanco 12% / 16% | Borde de chips y tarjetas translúcidas sobre la marca |
| `--lf-radio-tarjeta` | `18px` | Tarjetas de datos sobre la marca |
| `--lf-ancho-marco` | `1420px` | Ancho máximo del marco completo |

FR-045: `acento-claro` escribe como texto solo sobre `marca-fondo` (4.76:1) y
`marca-fondo-alto` (6.97:1); sobre `marca-superficie` se queda en 3.84:1, así
que ahí es solo relleno, filete o marca decorativa — nunca texto.

### 1.4 Degradados (FR-036)

Se componen exclusivamente a partir de los colores de §1.1; ninguna hoja de
componente declara un degradado propio.

| Token | Composición | Uso |
|---|---|---|
| `--lf-degradado-marca` | `marca-fondo-alto` → `marca-fondo` → `marca-fondo-suave`, 135° | Bloque principal de la portada, cabecera de marca |
| `--lf-degradado-fondo` | `superficie-alt` → `fondo`, 180° | Fondo de la aplicación |
| `--lf-degradado-superficie` | `superficie` → `superficie-alt`, 160° | Tarjetas destacadas |
| `--lf-degradado-acento` | `acento` → `acento-claro`, 120° | Barras de dato y realces de identidad |
| `--lf-degradado-lienzo` | radial, `superficie` → `fondo` → `fondo-alto` | Lienzo que enmarca el marco de aplicación (FR-040) |
| `--lf-degradado-velo` | `marca-fondo-alto` transparente → opaco, 180° | Legibilidad del texto sobre el patrón del bloque principal |
| `--lf-patron-franjas` | franjas repetidas `marca-fondo-suave`/`marca-superficie`, 35° | Sustituye la fotografía que la maqueta deja como hueco |

**FR-038**: el texto sobre un degradado declara su par de contraste contra el
extremo **más claro**, que es el caso peor. Por eso `superficie sobre
marca-fondo` y `marca-texto sobre marca-fondo` están en el bloque
`pares-de-contraste` aunque el fondo real no sea plano.

## 2. Estructura de aplicación (shell)

```text
AppShell
└── .lienzo                        lienzo claro, min-height 100vh (FR-040)
    └── .marco                     superficie de marca única, alto = lienzo
        ├── aside (.aside)
        │   ├── MarcaLeagueFlow    "LEAGUEFLOW" en dos tramos de color
        │   └── nav (role: navigation, aria-label "Secciones")
        │       └── ItemDeSeccion[]   6 ítems, icono propio (FR-041) + aria-current="page"
        └── .columna
            ├── header (role: banner)
            │   ├── IndicadorDeLiga    chip translúcido sobre la marca
            │   └── EstadoDeSesion     píldora blanca propia (FR-044)
            └── main (role: main, .contenido)   superficie clara elevada (FR-043)
                                        <AppRoutes />, con un único <h1> por pantalla
```

El `<header role="banner">` vive dentro de `.columna`, no envolviendo todo el
`AppShell`: sigue siendo el único `<header>` de la página (no hay `<article>`
ni `<section>` sectioning entre él y el `<body>` salvo divs sin rol), así que
el rol `banner` se calcula igual. Lo que cambia respecto a la versión anterior
de esta historia es dónde vive visualmente la marca (ahora en `.aside`, no en
la cabecera), no la semántica de landmarks de FR-027.

### 2.1 Secciones de navegación (FR-003)

Declaradas una sola vez en `src/components/layout/secciones.ts`, en el orden
del mockup de `docs/enunciado.md` §2:

| Sección | Destino (a dónde navega) | Activa en (qué la resalta) | Estado |
|---|---|---|---|
| Dashboard | `/leagues/:id/dashboard` | `/leagues/:id/dashboard` | Entregada (`specs/011`) |
| Equipos | `/leagues/:id/teams` | `/leagues/:id/teams`, `/leagues/:id/teams/new` | Entregada (`specs/003`) |
| Jugadores | `/leagues/:id/teams` (elegir equipo) | `/teams/:teamId/players`, `/teams/:teamId/players/new` | Entregada (`specs/004`) |
| Partidos | `/leagues/:id/matches` | `/leagues/:id/matches`, `/leagues/:id/matches/new`, `/matches/:matchId` | Entregada (`specs/005`–`007`, `009`) |
| Tabla | `/leagues/:id/standings` | `/leagues/:id/standings` | Entregada (`specs/008`) |
| Estadísticas | `/leagues/:id/top-scorers` (tabla de goleadores) | `/leagues/:id/top-scorers`, `/players/:playerId/statistics` | Entregada (`specs/010`) |

Las seis secciones requieren liga en contexto.

**Destino y activación son dos campos distintos, a propósito.** Los jugadores
se consultan por equipo (`specs/004`), así que la sección Jugadores **navega**
al listado de equipos para elegir uno, igual que Equipos, pero **se resalta**
solo en las rutas de jugadores. Si la sección activa se dedujera de la ruta de
destino, en `/leagues/:id/teams` quedarían dos ítems con `aria-current="page"`
a la vez, incumpliendo FR-004 y el escenario AS4 de la Historia 1. La
activación se calcula contra `coincide`, nunca contra `ruta`
([contracts/ui-contracts.md](./contracts/ui-contracts.md) §1). Estadísticas
comparte el mismo patrón: **navega** a la tabla de goleadores de la liga
(`specs/010`), pero también **se resalta** al llegar a la ficha individual de
un jugador (`/players/:playerId/statistics`), a la que se llega desde un
enlace de jugador en cualquier otra pantalla — sin ese `coincide` adicional,
esa ficha quedaría sin ninguna sección activa.

Sin liga en contexto, el shell **no** pinta la lista de secciones (FR-006
enmendado): en su lugar muestra un único acceso al listado de ligas. Seis
ítems deshabilitados serían ruido — una lista gris que ocupa el sitio de la
navegación real sin poder usarse — y ninguno conduciría a una pantalla rota
de todas formas, pero ese no es el motivo: el motivo es que esa lista no
sirve para nada sin liga (ver §2.2).

### 2.2 Liga en contexto (derivada, no persistida)

| Campo | Origen | Notas |
|---|---|---|
| `leagueId` | `:id` de la ruta `/leagues/:id/*`; el `league_id` del equipo en `/teams/:teamId/*`; el `league_id` del partido en `/matches/:matchId`; el `league_id` del equipo del jugador en `/players/:playerId/*` | Nunca de `localStorage`. Lo resuelve el shell; ninguna pantalla lo informa |
| `nombre` | `GET /leagues/{id}` (contrato de `specs/002`) | Cacheado en memoria por `id` durante la navegación |
| `estado` | `sin-liga` \| `cargando` \| `resuelta` \| `no-encontrada` | `sin-liga` en `/`, `/login`, `/leagues`, `/leagues/new` |

Resolver la liga también fuera de `/leagues/:id` es lo que mantiene viva la
navegación en las pantallas de jugadores, de detalle de partido y de ficha
individual de estadísticas. Sin ello, en `/teams/:teamId/players` o en
`/players/:playerId/statistics` no habría liga en contexto, la navegación de
secciones desaparecería por FR-006 y las secciones Jugadores y Estadísticas
nunca podrían resaltarse.

Con `estado === 'sin-liga'` el shell **no** pinta la lista de secciones: en su
lugar muestra un único acceso al listado de ligas (FR-006). Seis ítems
deshabilitados eran ruido —una lista gris que ocupa el mismo espacio que la
navegación real sin poder usarse— y dejaban a la portada compitiendo con una
columna vacía. Con `estado === 'cargando'` se conserva el hueco de la
navegación para que el contenido no salte al resolverse.

### 2.3 Portada (FR-034)

Pantalla de inicio, ruta `/`. No consume contratos nuevos (FR-035).

```text
Portada
├── bloque principal (degradado de marca)
│   ├── marca + propuesta de valor
│   ├── acción principal      sesión ? "Ver mis ligas" : "Iniciar sesión"
│   └── píldoras de capacidades   Programa · Registra · Clasifica · Analiza
├── tarjetas de sección        una por sección del producto (§2.1)
└── panel de cierre            qué hace falta para empezar
```

| Estado | Acción principal | Fuente |
|---|---|---|
| Sin sesión | "Iniciar sesión" → `/login` | sesión en memoria (`specs/001`) |
| Con sesión | "Ver mis ligas" → `/leagues` | sesión en memoria (`specs/001`) |

Las tarjetas de sección se generan desde `secciones.ts` (§2.1): añadir una
sección al producto no obliga a tocar el marcado de la portada.

## 3. Catálogo de componentes (FR-007)

Definidos una sola vez en `frontend/src/components/`, reutilizados por todas
las pantallas. El contrato de propiedades de cada uno está en
[contracts/ui-contracts.md](./contracts/ui-contracts.md).

| Componente | Responsabilidad | FR |
|---|---|---|
| `Panel` | Contenedor con título opcional y área de acciones | FR-007 |
| `TablaDeDatos` | Tabla con encabezado diferenciado, filas alternas, numéricos a la derecha y envoltorio con desplazamiento propio | FR-008, FR-030 |
| `FilaDeMarcador` | "LOCAL 3 — 1 VISITANTE", idéntica en toda la aplicación | FR-009 |
| `DistintivoDeEstado` | Estado del partido por texto + color (nunca solo color) | FR-010, FR-028 |
| `Boton` | Jerarquía `primario` \| `secundario` \| `destructivo`, con estado de envío en curso | FR-007, FR-018 |
| `CampoDeFormulario` | Etiqueta asociada + ayuda + error, ligados con `aria-describedby`/`aria-invalid` | FR-017, FR-026 |
| `DestacadoDePodio` | Distintivo "1.º/2.º/3.º" con medalla y fondo propio | FR-011 |
| `EscudoEquipo` | `crest_url` con sustituto de iniciales del mismo tamaño | FR-012 |
| `EstadoCarga` / `EstadoVacio` / `EstadoError` | Los tres estados de pantalla | FR-013 a FR-016 |

## 4. Estados de pantalla (FR-013)

Máquina de estados que toda pantalla que consulta datos debe recorrer:

```text
              ┌──────────┐
   montaje ──▶│ cargando │
              └────┬─────┘
        éxito con  │  éxito sin        fallo
        datos      │  datos              │
        ┌──────────┼──────────┐          │
        ▼          ▼          ▼          ▼
   ┌────────┐ ┌────────┐            ┌───────┐
   │  datos │ │  vacío │            │ error │──▶ reintentar ──▶ cargando
   └────────┘ └────────┘            └───────┘
```

| Estado | Semántica | Contenido |
|---|---|---|
| `cargando` | `role="status"`, `aria-live="polite"` | "Cargando <recurso>…" |
| `vacío` | Contenido normal | Título + qué hacer a continuación; la acción solo si el rol actual puede ejecutarla (FR-014) |
| `error` | `role="alert"` | Mensaje del catálogo en español + "Reintentar"; el shell sigue disponible (FR-016) |

## 5. Estados de formulario (FR-017, FR-018)

| Estado | Efecto |
|---|---|
| `inactivo` | Controles habilitados |
| `enviando` | Botón de envío deshabilitado con texto "Enviando…" y `aria-busy="true"`; el reenvío queda bloqueado |
| `error-de-campo` | Mensaje junto al campo, `aria-invalid="true"` + `aria-describedby`; el formulario vuelve a `inactivo` (nunca queda atrapado) |
| `error-general` | `EstadoError` sobre el formulario; el formulario vuelve a `inactivo` |
| `éxito` | Navegación o mensaje de confirmación, según ya definió la spec de origen de cada pantalla |

## 6. Reglas de formato compartidas (FR-009, FR-022)

Centralizadas en `frontend/src/lib/formato.ts`:

| Regla | Formato | Ejemplo |
|---|---|---|
| Fecha | `Intl.DateTimeFormat('es', { dateStyle: 'medium' })` | 20 ago 2026 |
| Fecha y hora | `dateStyle: 'medium'` + `timeStyle: 'short'` | 20 ago 2026, 19:30 |
| Marcador | `LOCAL <n> — <n> VISITANTE` | EAFIT 3 — 1 CES |
| Diferencia de goles | Signo explícito en positivos | `+4`, `0`, `-2` |
| Iniciales de equipo | Hasta 3 caracteres en mayúscula | "Deportivo Cali" → DC |
| Texto largo | Truncado visual con el texto íntegro en `title` | — |

## 7. Trazabilidad

| Requisito | Dónde se modela |
|---|---|
| FR-001 a FR-006 | §2 Estructura de aplicación |
| FR-007 a FR-012 | §3 Catálogo de componentes |
| FR-013 a FR-016 | §4 Estados de pantalla |
| FR-017, FR-018 | §5 Estados de formulario |
| FR-019 a FR-022 | §1 Tokens y §6 Reglas de formato |
| FR-023 a FR-028 | §1.1 (contraste), §2 (semántica), §3 (`CampoDeFormulario`, `DistintivoDeEstado`) |
| FR-029 a FR-030 | §1.3 (cortes) y §3 (`TablaDeDatos`) |
| FR-031 a FR-033 | [plan.md](./plan.md) §Alcance por pantalla |
