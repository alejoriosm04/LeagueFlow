---

description: "Task list for 012-identidad-visual"
---

# Tasks: Identidad visual y experiencia de usuario consistente

**Input**: Design documents from `/specs/012-identidad-visual/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md),
[research.md](./research.md), [data-model.md](./data-model.md),
[contracts/ui-contracts.md](./contracts/ui-contracts.md),
[quickstart.md](./quickstart.md)

**Tests**: SÍ se incluyen. No es una elección de estilo: la spec lo exige
(FR-033, SC-008) y el Principio IV de la constitución convierte la suite
existente en un gate de merge. Las pruebas nuevas cubren **solo lo que esta
historia introduce** (shell, estados, catálogo, contraste, auditoría de
tokens); no se añaden pruebas de reglas de negocio porque esta historia no
introduce ninguna (FR-032).

**Organización**: por historia de usuario, en el orden de prioridad de la spec
(P1 → P5), que es el mismo orden de entrega de [plan.md](./plan.md) §Orden de
entrega. Cada fase deja la aplicación entregable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: US1…US5, según las historias de [spec.md](./spec.md)
- Todas las rutas son relativas a la raíz del repositorio

## Path Conventions

Proyecto **web** (`backend/` + `frontend/`), heredado de `specs/001`. **Esta
historia solo toca `frontend/`**: el diff sobre `backend/` debe quedar vacío
(FR-032, verificable en [quickstart.md](./quickstart.md) §Comprobación de
FR-032).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: fijar la línea base de no regresión y crear las carpetas que
`specs/001` había reservado y dejado vacías.

- [X] T001 Ejecutar `npx vitest run` en `frontend/` y confirmar la línea base de FR-033: 9 archivos y 44 pruebas en verde. Si el conteo no coincide, detenerse y actualizar la cifra en `specs/012-identidad-visual/quickstart.md` antes de continuar
- [X] T002 [P] Crear las carpetas `frontend/src/styles/`, `frontend/src/lib/` y `frontend/src/components/` con sus subcarpetas `layout/`, `datos/`, `formulario/`, `estado/` y `__tests__/`
- [X] T003 [P] Crear el barril vacío `frontend/src/components/index.ts` que reexportará el catálogo (contrato en `specs/012-identidad-visual/contracts/ui-contracts.md` §2)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: la fuente única de valores visuales. Todo componente de las cinco
historias la consume; nada puede estilarse antes.

**⚠️ CRITICAL**: ninguna historia puede empezar hasta que esta fase esté
completa.

- [X] T004 Crear `frontend/src/styles/tokens.css` declarando en `:root` los 18 tokens de color, la tipografía, los tamaños de texto, los pesos, la escala de espaciado, los radios, las sombras y los anchos de `data-model.md` §1, con los valores exactos ahí tabulados (FR-019)
- [X] T005 Crear `frontend/src/styles/global.css` con el reset mínimo, la tipografía base, el `:focus-visible` compartido (FR-024) y `html/body` sin desplazamiento horizontal (FR-030), consumiendo únicamente `var(--lf-…)` (FR-020)
- [X] T006 Importar `./styles/tokens.css` y `./styles/global.css` una sola vez en `frontend/src/main.tsx`, antes del render (research.md §2)

**Checkpoint**: los tokens están disponibles en toda la aplicación. Las cinco
historias pueden empezar.

---

## Phase 3: User Story 1 - Reconocer la aplicación como un producto (Priority: P1) 🎯 MVP

**Goal**: toda pantalla, pública o autenticada, comparte cabecera de marca,
indicador de liga en contexto, estado de sesión y navegación de seis secciones
con la sección actual resaltada. Cubre FR-001 a FR-006, FR-027 y SC-001, más
FR-021 en los textos del propio shell; su verificación en las 16 pantallas del
alcance es T082.

**Independent Test**: recorrer las nueve pantallas ya entregadas y verificar la
misma cabecera y la misma navegación, con la sección actual marcada por
`aria-current="page"` y por un distintivo no cromático
([quickstart.md](./quickstart.md) escenarios 1-6).

### Implementación

- [X] T007 [P] [US1] Declarar las seis secciones (Dashboard, Equipos, Jugadores, Partidos, Tabla, Estadísticas) en el orden del mockup de `docs/enunciado.md` §2 en `frontend/src/components/layout/secciones.ts`, con el tipo `Seccion` del contrato —incluidos `ruta` y `coincide` como campos separados— y la marca `pendiente` en Dashboard y Estadísticas (FR-003, data-model.md §2.1)
- [X] T008 [P] [US1] Implementar `useLigaEnContexto()` en `frontend/src/components/layout/useLigaEnContexto.ts`: deriva el `:id` de la ruta `/leagues/:id/*`, acepta un `league_id` explícito para `/matches/:matchId`, resuelve el nombre con `leaguesApi` y cachea en memoria por `id`. Sin `localStorage` (FR-002, FR-006, research.md §5)
- [X] T009 [P] [US1] Implementar `EstadoDeSesion.tsx` y su `EstadoDeSesion.module.css` en `frontend/src/components/layout/`: usuario y rol con acceso a cerrar sesión, o enlace "Iniciar sesión" sin sesión (FR-002)
- [X] T010 [P] [US1] Implementar `PendienteDeEntrega.tsx` y su hoja en `frontend/src/components/layout/`: pantalla que declara que la sección llega con `specs/010` o `specs/011`, sin consultar datos (research.md §10)
- [X] T011 [US1] Implementar `IndicadorDeLiga.tsx` y su hoja en `frontend/src/components/layout/`, consumiendo `useLigaEnContexto()`; muestra "Sin liga seleccionada" en el estado `sin-liga` (FR-002, FR-006) — depende de T008
- [X] T012 [US1] Implementar `AppShell.tsx` y `AppShell.module.css` en `frontend/src/components/layout/` con `<header role="banner">` (marca tipográfica "LEAGUEFLOW" + `IndicadorDeLiga` + `EstadoDeSesion`), `<nav aria-label="Secciones">` y `<main>`. `aria-current="page"` se calcula contra `coincide`, **nunca** contra `ruta`, para que Equipos y Jugadores no queden activas a la vez en `/leagues/:id/teams` (FR-001, FR-004, FR-027) — depende de T007, T009, T011
- [X] T013 [US1] Deshabilitar en `frontend/src/components/layout/AppShell.tsx` las secciones que requieren liga cuando el estado es `sin-liga`, indicando "Selecciona una liga" con enlace al listado, sin destinos rotos (FR-006)
- [X] T014 [US1] Marcar la sección activa en `frontend/src/components/layout/AppShell.module.css` con barra lateral y peso tipográfico además del color, nunca solo con color (FR-004, FR-028)
- [X] T015 [US1] Añadir en `frontend/src/routes.tsx` las rutas `/leagues/:id/dashboard` y `/leagues/:id/statistics` apuntando a `PendienteDeEntrega`, sin tocar las rutas ya existentes — depende de T010
- [X] T016 [US1] Reemplazar en `frontend/src/App.tsx` la cabecera con estilos en línea por `<AppShell><AppRoutes /></AppShell>`, eliminando todos los `style={{…}}` del archivo (FR-001, FR-020) — depende de T012
- [X] T017 [US1] Reexportar `AppShell`, `secciones`, `useLigaEnContexto` y `PendienteDeEntrega` desde `frontend/src/components/index.ts`

### Pruebas de la Historia 1

- [X] T018 [P] [US1] Crear `frontend/src/components/__tests__/appShell.test.tsx`: el shell aparece en una ruta pública y en una autenticada; **en cualquier ruta hay como máximo un `aria-current="page"`**, y en `/leagues/:id/teams` es Equipos y no Jugadores; en `/teams/:teamId/players` es Jugadores; en `/login` no hay ninguna activa; y la cabecera muestra usuario+rol con sesión y "Iniciar sesión" sin ella (FR-004, SC-001)
- [X] T019 [P] [US1] Crear `frontend/src/components/__tests__/ligaEnContexto.test.tsx`: dentro de `/leagues/:id/*` la cabecera muestra el nombre de la liga; en `/`, `/login`, `/leagues` y `/leagues/new` muestra "Sin liga seleccionada" y las secciones que requieren liga quedan deshabilitadas (FR-006)
- [X] T020 [US1] Ejecutar `npx vitest run` en `frontend/` y migrar los selectores que el nuevo marcado rompa **hacia** `getByRole`/`getByLabelText`, nunca hacia `querySelector` ni `data-testid`. Prohibido borrar, saltar o debilitar una prueba (FR-033, Principio IV)

**Checkpoint**: la aplicación ya se lee como un producto. US1 es entregable por
sí sola (MVP).

---

## Phase 4: User Story 2 - Leer el estado de la liga de un vistazo (Priority: P2)

**Goal**: marcadores, estados de partido, tablas, escudos, podio y fechas usan
el mismo lenguaje visual en todas las vistas. Cubre FR-007 a FR-012 y FR-022.

**Independent Test**: abrir el listado de partidos y la clasificación de una
liga con datos en los cuatro estados y verificar formato de marcador,
distintivos por texto, alineación numérica, sustituto de escudo y destacado del
podio ([quickstart.md](./quickstart.md) escenarios 7-11).

### Implementación

- [X] T021 [P] [US2] Crear `frontend/src/lib/formato.ts` con `formatearFecha`, `formatearFechaHora`, `formatearMarcador`, `formatearDiferencia` e `inicialesDeEquipo`, según `contracts/ui-contracts.md` §5 y `data-model.md` §6 (FR-009, FR-022)
- [X] T022 [P] [US2] Implementar `Panel.tsx` y `Panel.module.css` en `frontend/src/components/datos/`: contenedor con título opcional como `<h2>` y área de acciones (FR-007)
- [X] T023 [P] [US2] Implementar `TablaDeDatos.tsx` y `TablaDeDatos.module.css` en `frontend/src/components/datos/`: encabezado diferenciado, filas alternas, columnas `numerica` alineadas a la derecha con `tabular-nums`, `<caption>` y envoltorio `role="region"` con `tabIndex={0}` y `overflow-x: auto` (FR-008, FR-030)
- [X] T024 [P] [US2] Implementar `DistintivoDeEstado.tsx` y su hoja en `frontend/src/components/datos/` con las etiquetas fijas Programado, En curso, Finalizado y Cancelado; el texto es obligatorio y el color redundante (FR-010, FR-028)
- [X] T025 [P] [US2] Implementar `EscudoEquipo.tsx` y su hoja en `frontend/src/components/datos/`: renderiza `crest_url` y cae al sustituto de iniciales con `onError`, ocupando el mismo cuadro (FR-012)
- [X] T026 [P] [US2] Implementar `DestacadoDePodio.tsx` y su hoja en `frontend/src/components/datos/`: texto "1.º/2.º/3.º" más medalla; con menos de tres equipos destaca solo las posiciones existentes (FR-011, FR-028)
- [X] T027 [US2] Implementar `FilaDeMarcador.tsx` y su hoja en `frontend/src/components/datos/` con el formato "LOCAL 3 — 1 VISITANTE" y "vs" cuando no hay resultado (FR-009) — depende de T021, T024, T025
- [X] T028 [US2] Reexportar los seis componentes de datos desde `frontend/src/components/index.ts`
- [X] T029 [US2] Aplicar `Panel`, `TablaDeDatos` y `DestacadoDePodio` en `frontend/src/features/standings/StandingsPage.tsx`, con puntos y diferencia de goles como columnas numéricas (FR-008, FR-011)
- [X] T030 [US2] Aplicar `FilaDeMarcador`, `DistintivoDeEstado` y `formatearFechaHora` en `frontend/src/features/matches/MatchesPage.tsx`, retirando el `Intl.DateTimeFormat` local del archivo a favor de `lib/formato.ts` (FR-009, FR-010, FR-022, research.md §10)
- [X] T031 [P] [US2] Aplicar `Panel`, `FilaDeMarcador` y `DistintivoDeEstado` en `frontend/src/features/matches/MatchDetailPage.tsx`, informando el `league_id` a `useLigaEnContexto()` (FR-002, FR-009)
- [X] T032 [P] [US2] Aplicar `Panel`, `TablaDeDatos` y `EscudoEquipo` en `frontend/src/features/teams/TeamsPage.tsx` (FR-008, FR-012)
- [X] T033 [P] [US2] Aplicar `Panel` y `TablaDeDatos` en `frontend/src/features/leagues/LeaguesPage.tsx` y `frontend/src/features/leagues/LeagueDetailPage.tsx` (FR-007, FR-008)
- [X] T034 [P] [US2] Aplicar `Panel` y `TablaDeDatos` en `frontend/src/features/players/PlayersPage.tsx` (FR-007, FR-008)

### Pruebas de la Historia 2

- [X] T035 [P] [US2] Crear `frontend/src/lib/__tests__/formato.test.ts`: fecha y fecha-hora en español, marcador "LOCAL 3 — 1 VISITANTE", diferencia con signo explícito (`+4`, `0`, `-2`) e iniciales de hasta 3 caracteres (FR-009, FR-022)
- [X] T036 [P] [US2] Crear `frontend/src/components/__tests__/catalogoDatos.test.tsx`: los cuatro estados de partido se leen por texto, el equipo sin `crest_url` y el de URL rota muestran iniciales, y el podio marca 1.º/2.º/3.º por texto (FR-010, FR-011, FR-012, FR-028)
- [X] T037 [US2] Ejecutar `npx vitest run` en `frontend/` y migrar hacia consultas por rol y etiqueta los selectores por texto que rompan el marcador y los distintivos, sin borrar ni debilitar ninguna prueba (FR-033)

**Checkpoint**: US1 y US2 funcionan de forma independiente.

---

## Phase 5: User Story 3 - Entender qué pasa cuando no hay datos o algo falla (Priority: P3)

**Goal**: las tres pantallas de estado y los formularios del catálogo,
aplicados a todo el alcance de FR-031. Cubre FR-013 a FR-018, SC-002 y SC-003.

**Independent Test**: forzar carga, vacío y error en una pantalla de consulta y
un error de campo más un doble envío en un formulario
([quickstart.md](./quickstart.md) escenarios 12-16).

### Implementación

- [X] T038 [P] [US3] Crear `frontend/src/lib/mensajesDeError.ts` con `mensajeDeError(error: unknown): string`, que traduce el `code` del envelope de `specs/001/contracts/conventions.md` a español y usa un genérico para códigos desconocidos y fallos de red. Nunca devuelve el `message` del servidor ni el `code` crudo (FR-015, SC-003)
- [X] T039 [P] [US3] Implementar `EstadoCarga.tsx` y su hoja en `frontend/src/components/estado/` con `role="status"` y `aria-live="polite"` (FR-013)
- [X] T040 [P] [US3] Implementar `EstadoVacio.tsx` y su hoja en `frontend/src/components/estado/` con título, qué hacer a continuación y acción **opcional**, que solo se pasa si el rol actual puede ejecutarla (FR-014)
- [X] T041 [P] [US3] Implementar `EstadoError.tsx` y su hoja en `frontend/src/components/estado/` con `role="alert"`, mensaje ya traducido y "Reintentar"; se renderiza dentro de `<main>` para que el shell sobreviva (FR-015, FR-016)
- [X] T042 [P] [US3] Implementar `Boton.tsx` y `Boton.module.css` en `frontend/src/components/formulario/` con variantes `primario`/`secundario`/`destructivo` y la prop `enviando` que deshabilita, pone `aria-busy` y el texto "Enviando…" (FR-007, FR-018)
- [X] T043 [P] [US3] Implementar `CampoDeFormulario.tsx` y su hoja en `frontend/src/components/formulario/` con `<label for>` obligatoria, ayuda y error ligados por `aria-describedby` y `aria-invalid` (FR-017, FR-026)
- [X] T044 [US3] Reexportar los tres estados y los dos componentes de formulario desde `frontend/src/components/index.ts`
- [X] T045 [P] [US3] Aplicar los tres estados en `frontend/src/features/standings/StandingsPage.tsx`, con el vacío explicando que la tabla se llena al finalizar partidos (FR-013, FR-014)
- [X] T046 [P] [US3] Aplicar los tres estados en `frontend/src/features/matches/MatchesPage.tsx` y `frontend/src/features/matches/MatchDetailPage.tsx` (FR-013)
- [X] T047 [P] [US3] Aplicar los tres estados en `frontend/src/features/teams/TeamsPage.tsx`, con la acción "Registrar el primer equipo" solo para el rol que puede crearla (FR-014, Assumption "Estados vacíos según permisos")
- [X] T048 [P] [US3] Aplicar los tres estados en `frontend/src/features/players/PlayersPage.tsx` (FR-013, FR-014)
- [X] T049 [P] [US3] Aplicar los tres estados en `frontend/src/features/leagues/LeaguesPage.tsx` y `frontend/src/features/leagues/LeagueDetailPage.tsx` (FR-013, FR-014)
- [X] T050 [P] [US3] Migrar a `CampoDeFormulario`, `Boton` y `mensajeDeError` el formulario de `frontend/src/features/auth/LoginPage.tsx`, con bloqueo de reenvío (FR-017, FR-018)
- [X] T051 [P] [US3] Migrar al catálogo de formulario `frontend/src/features/leagues/CreateLeagueForm.tsx` (FR-017, FR-018)
- [X] T052 [P] [US3] Migrar al catálogo de formulario `frontend/src/features/teams/CreateTeamForm.tsx`, mostrando el error de nombre duplicado junto al campo (FR-017)
- [X] T053 [P] [US3] Migrar al catálogo de formulario `frontend/src/features/players/CreatePlayerForm.tsx` (FR-017, FR-018)
- [X] T054 [P] [US3] Migrar al catálogo de formulario `frontend/src/features/matches/CreateMatchForm.tsx` (FR-017, FR-018)
- [X] T055 [P] [US3] Migrar al catálogo de formulario `frontend/src/features/matches/ResultForm.tsx` (FR-017, FR-018)
- [X] T056 [P] [US3] Migrar al catálogo de formulario `frontend/src/features/matches/CorrectionRequestForm.tsx` y `frontend/src/features/matches/CorrectionDecisionForm.tsx`, usando la variante `destructivo` donde corresponda (FR-007, FR-017)
- [X] T057 [P] [US3] Migrar al catálogo de formulario `frontend/src/features/events/GoalForm.tsx`, con bloqueo de reenvío (FR-017, FR-018)
- [X] T058 [US3] Verificar en los nueve formularios migrados que tras un error el formulario vuelve al estado `inactivo` y el usuario puede reintentar, sin quedar atrapado (FR-018, `data-model.md` §5, edge case de la spec)

### Pruebas de la Historia 3

- [X] T059 [P] [US3] Crear `frontend/src/components/__tests__/estadosDePantalla.test.tsx`: el estado de carga expone `role="status"`, el vacío muestra la acción solo cuando se le pasa, y el de error expone `role="alert"` con el shell intacto (SC-002, FR-016)
- [X] T060 [P] [US3] Crear `frontend/src/lib/__tests__/mensajesDeError.test.ts`: un `code` conocido se traduce, un `code` desconocido y un fallo de red caen en el genérico, y en ningún caso se devuelve el `message` del servidor ni el `code` crudo (FR-015, SC-003)
- [X] T061 [P] [US3] Crear `frontend/src/components/__tests__/formulario.test.tsx`: el error de campo queda ligado por `aria-describedby` con `aria-invalid="true"`, y con `enviando` el botón queda deshabilitado con `aria-busy`, bloqueando el segundo envío (FR-017, FR-018)
- [X] T062 [US3] Ejecutar `npx vitest run` en `frontend/` y migrar hacia consultas por rol y etiqueta las consultas por texto que rompan los mensajes unificados de carga, vacío y error, sin borrar ni debilitar ninguna prueba (FR-033)

**Checkpoint**: US1, US2 y US3 funcionan de forma independiente.

---

## Phase 6: User Story 4 - Usar la aplicación solo con teclado y con buen contraste (Priority: P4)

**Goal**: convertir la accesibilidad en un gate automatizado donde se puede y
en una verificación reproducible donde no. Cubre FR-023 a FR-028, SC-004,
SC-005 y SC-009.

**Independent Test**: recorrer con teclado una pantalla con formulario y un
listado, y ejecutar las dos pruebas de sistema
([quickstart.md](./quickstart.md) §Verificación manual de SC-005).

- [X] T063 [P] [US4] Crear `frontend/src/styles/__tests__/contraste.test.ts`: lee `frontend/src/styles/tokens.css`, calcula el ratio WCAG de cada par texto/fondo declarado en `data-model.md` §1.1 y falla por debajo de 4.5:1 (FR-023, SC-004)
- [X] T064 [P] [US4] Crear `frontend/src/styles/__tests__/auditoriaDeTokens.test.ts`: recorre todos los `*.module.css` de `frontend/src/` y falla si alguno declara un color literal (`#rgb`, `#rrggbb`, `rgb(`, `hsl(`) fuera de `tokens.css` (FR-020, SC-009)
- [X] T065 [US4] Corregir las violaciones que reporten T063 y T064 en los `*.module.css` afectados, sustituyendo literales por `var(--lf-…)` o ajustando el token en `frontend/src/styles/tokens.css` (FR-019, FR-020)
- [X] T066 [US4] Auditar que ninguna hoja de `frontend/src/components/` anula el foco con `outline: none` y que todo elemento interactivo hereda el `:focus-visible` de `frontend/src/styles/global.css` (FR-024, `contracts/ui-contracts.md` §6)
- [X] T067 [US4] Verificar que cada pantalla tiene un único `<h1>` y que la jerarquía de encabezados no salta niveles bajo el `<main>` del shell, en `frontend/src/features/auth/LoginPage.tsx`, `leagues/LeaguesPage.tsx`, `leagues/LeagueDetailPage.tsx`, `teams/TeamsPage.tsx`, `players/PlayersPage.tsx`, `matches/MatchesPage.tsx`, `matches/MatchDetailPage.tsx` y `standings/StandingsPage.tsx` (FR-027)
- [X] T068 [US4] Revisar que ninguna información dependa solo del color en `frontend/src/components/datos/DistintivoDeEstado.tsx`, `datos/DestacadoDePodio.tsx`, `estado/EstadoError.tsx` y el ítem activo de `layout/AppShell.tsx`, y corregir sus `.module.css` donde falte texto o forma (FR-028)
- [X] T069 [P] [US4] Crear `frontend/src/components/__tests__/accesibilidad.test.tsx`: todo control de un formulario del catálogo es alcanzable por `Tab` en orden y activable con teclado, y cada campo tiene su etiqueta asociada (FR-025, FR-026)
- [ ] T070 [US4] Ejecutar el recorrido manual solo con teclado de `specs/012-identidad-visual/quickstart.md` (iniciar sesión → crear equipo → registrar resultado) y anotar el resultado en `docs/metricas/012-identidad-visual.md` (SC-005)

**Checkpoint**: contraste y ausencia de literales son gates de CI, no
inspecciones a ojo.

---

## Phase 7: User Story 5 - Usar la aplicación desde tablet o móvil (Priority: P5)

**Goal**: 1280, 768 y 375 px usables sin desplazamiento horizontal de página.
Cubre FR-029, FR-030 y SC-006.

**Independent Test**: recorrer cada pantalla del alcance en los tres anchos y
comprobar que `document.body.scrollWidth` no supera el ancho de la ventana
([quickstart.md](./quickstart.md) §Verificación manual de SC-006).

- [X] T071 [US5] Añadir en `frontend/src/components/layout/AppShell.module.css` los tres cortes de research.md §6: ≥1024 px navegación lateral fija, 768–1023 px lateral estrecha, <768 px colapsada (FR-005, FR-029)
- [X] T072 [US5] Añadir en `frontend/src/components/layout/AppShell.tsx` el `<button>` "Menú" visible solo por debajo de 768 px, con `aria-expanded` y `aria-controls` apuntando al `<nav>`, sin `matchMedia` en el render (FR-005) — depende de T071
- [X] T073 [P] [US5] Verificar y ajustar en `frontend/src/components/datos/TablaDeDatos.module.css` que el envoltorio con desplazamiento propio funciona a 375 px y que la página no desplaza en horizontal (FR-030)
- [X] T074 [P] [US5] Revisar que ningún componente fuerza un ancho mínimo que desborde a 375 px en `frontend/src/components/datos/Panel.module.css`, `datos/FilaDeMarcador.module.css`, `datos/DistintivoDeEstado.module.css` y `formulario/CampoDeFormulario.module.css`, y aplicar el truncado con `title` de la Assumption "Textos largos" donde haga falta (FR-029, FR-030)
- [X] T075 [P] [US5] Crear `frontend/src/components/__tests__/navegacionColapsada.test.tsx`: el botón "Menú" alterna `aria-expanded`, el `<nav>` sigue alcanzable con teclado y los seis ítems siguen presentes al abrirlo (FR-005)
- [ ] T076 [US5] Ejecutar la verificación manual de los tres anchos sobre las pantallas de FR-031 según `specs/012-identidad-visual/quickstart.md` y anotar el resultado en `docs/metricas/012-identidad-visual.md` (SC-006)

**Checkpoint**: las cinco historias están completas y son independientemente
verificables.

---

## Phase 8: Polish & Cross-Cutting Concerns

- [X] T077 Ejecutar `npx vitest run` en `frontend/` y confirmar que las 44 pruebas originales siguen en verde junto a las nuevas, sin ninguna borrada, saltada ni debilitada (FR-033, SC-008, Principio IV)
- [X] T078 [P] Ejecutar `npm run lint` y `npm run build` en `frontend/` y dejar ambos en verde (Principio VII)
- [X] T079 [P] Verificar FR-032 con `git diff --stat main...012-identidad-visual -- backend/` y confirmar que el diff sobre `backend/` es vacío: sin esquema, sin migraciones, sin contratos modificados
- [ ] T080 Recorrer los 16 escenarios de validación de `specs/012-identidad-visual/quickstart.md` sobre la aplicación en ejecución y registrar las desviaciones encontradas
- [X] T081 [P] Copiar `docs/metricas/_plantilla.md` a `docs/metricas/012-identidad-visual.md` y llenar la sección "Llenado por el agente" con datos reales: tareas completadas, pruebas escritas y en verde, ciclos de corrección y qué se reprocesó. **No inventar el costo/tokens de IA ni el tiempo real de trabajo** — esos dos campos los llena la persona (`AGENTS.md` §7)
- [X] T082 [P] Verificar que el 100% del texto visible está en español en las 16 pantallas de FR-031, incluidas las etiquetas del catálogo (`DistintivoDeEstado`, `Boton`, los tres estados) y los mensajes de `frontend/src/lib/mensajesDeError.ts`; corregir cualquier texto en otro idioma (FR-021)

---

## Phase 9: User Story 6 - Portada y expresividad visual (Priority: P6)

**Ampliación posterior a la primera pasada de la historia.** Nace de la
revisión visual con el equipo: la primera entrega cumplía la estructura del
mockup pero se leía plana, y la pantalla de inicio mostraba seis secciones
deshabilitadas. Enmienda FR-006 y añade FR-034 a FR-039, SC-011 y SC-012.

### Sistema de valores

- [X] T083 Ampliar `frontend/src/styles/tokens.css`: fondo azul claro, superficies de marca (`marca-fondo`, `marca-fondo-alto`, `marca-fondo-suave`, `marca-texto`), acento cálido (`acento`, `acento-tinte`, `acento-claro`), escala tipográfica de portada, radios `xl`/pastilla, elevaciones `sombra-3`/`sombra-marca` y los cuatro degradados, con sus pares de contraste declarados (FR-036, FR-037, FR-038)
- [X] T084 [P] Actualizar `specs/012-identidad-visual/data-model.md` §1.1, §1.3, §1.4 y §2.3 con los valores y la estructura de la portada

### Implementación

- [X] T085 `frontend/src/components/layout/AppShell.tsx`: sin liga en contexto dejar de pintar la lista de secciones y ofrecer un único acceso al listado de ligas; conservar el hueco mientras la liga se resuelve (FR-006)
- [X] T086 `frontend/src/components/layout/AppShell.module.css`: acabado de la cabecera con degradado de marca, navegación como tarjeta elevada e ítem activo en pastilla (FR-039)
- [X] T087 Crear `frontend/src/features/inicio/Portada.tsx` y su `.module.css`: bloque principal con marca, propuesta de valor y acción principal según sesión, píldoras de capacidades y tarjetas de sección generadas desde `secciones.ts` (FR-034, FR-035)
- [X] T088 `frontend/src/routes.tsx`: servir la portada en `/` en lugar del bloque de texto actual
- [X] T089 [P] Elevar el acabado compartido de `Panel`, `TablaDeDatos`, `DestacadoDePodio` y `DistintivoDeEstado` al nuevo tratamiento de superficie (FR-039)

### Pruebas de la Historia 6

- [X] T090 Actualizar `frontend/src/components/__tests__/ligaEnContexto.test.tsx` a la conducta de FR-006 enmendado y afirmar que sin liga no queda ningún elemento de navegación deshabilitado (SC-011)
- [X] T091 Crear `frontend/src/features/inicio/__tests__/portada.test.tsx`: acción principal correcta con y sin sesión, presencia de la marca y de las tarjetas de sección (FR-034)
- [X] T092 Ejecutar la suite completa, `npm run lint` y `npm run build`; confirmar que contraste y auditoría de tokens siguen en verde con la paleta nueva (SC-004, SC-009, SC-012, FR-033)
- [X] T093 Verificar la portada y dos pantallas internas en navegador a 1280 / 768 / 375 px, sin desbordamiento horizontal (SC-006, SC-011)

---

## Phase 10: Marco de aplicación sobre la maqueta de referencia (P6, ampliación)

**Segunda ampliación**, a partir de una maqueta navegable (`LeagueFlow Wow`,
hecha con Claude Design) que el equipo aportó como referencia de disposición y
color. Enmienda FR-040 a FR-046, SC-013 y SC-014. Ver spec.md, Assumption
"Maqueta de referencia del marco" para qué de la maqueta se implementa y qué
no (buscador, notificaciones, tarjetas de dashboard con datos agregados).

### Sistema de valores

- [X] T094 Ampliar `tokens.css`: `marca-superficie`, `marca-borde`, `fondo-alto`, superposiciones translúcidas de marca, `radio-tarjeta`, `ancho-marco`, `degradado-lienzo`, `degradado-velo`, `patron-franjas`, con sus pares de contraste nuevos declarados (FR-040, FR-044, FR-045, SC-013)
- [X] T095 [P] Actualizar `data-model.md` §1.3b, §1.4 y §2 con los tokens y la estructura de marco nuevos

### Implementación

- [X] T096 `AppShell.tsx`/`.module.css`: marco único (`.lienzo` → `.marco` → `.aside` + `.columna`) que llena el alto del lienzo (FR-040); la marca pasa a la barra lateral en dos tramos de color con nombre accesible explícito
- [X] T097 Crear `IconoSeccion.tsx`/`.module.css`: marca visual propia por sección, coloreada con `currentColor` para heredar el estado activo sin reglas duplicadas (FR-041)
- [X] T098 `.contenido` como superficie clara elevada sobre la marca (FR-043): las pantallas existentes no cambian una sola línea para vivir dentro del marco nuevo
- [X] T099 `IndicadorDeLiga`/`EstadoDeSesion`: restilizados para la cabecera sobre la superficie de marca — chip translúcido y píldora blanca propia — sin usar nunca los colores de texto de superficie clara sobre la marca (FR-044, FR-045)
- [X] T100 Añadir `inicialesDe` en `formato.ts` (alias de `inicialesDeEquipo`) para la sigla del chip de liga y del selector de la portada
- [X] T101 `Portada.tsx`/`.module.css`: selector de ligas real (`SelectorDeLigas`) con sus tres estados de pantalla —carga, vacío, error— que navega a la liga elegida en una interacción (FR-046, SC-014)

### Pruebas de la Historia 6 (marco)

- [X] T102 Actualizar `appShell.test.tsx`, `ligaEnContexto.test.tsx`, `navegacionColapsada.test.tsx`, `accesibilidad.test.tsx` a la estructura de marco nueva
- [X] T103 Ampliar `portada.test.tsx`: el selector lista ligas reales y navega en una interacción; estado vacío sin ligas; estado de error con reintento (FR-046, SC-014)
- [X] T104 Ejecutar la suite completa, `npm run lint` y `npm run build`; confirmar que contraste (39 pares) y auditoría de tokens siguen en verde con los tokens de marco nuevos (SC-004, SC-009, SC-013)
- [X] T105 Verificar en navegador, a 1280 / 768 / 375 px: el marco llena el alto del viewport en pantallas con poco contenido, la navegación móvil no deja una franja oscura vacía entre la marca y la cabecera, y `document.body.scrollWidth === window.innerWidth` en los tres anchos (SC-006)

---

## Estado de las tareas de verificación manual

**T070, T076 y T080 quedan sin marcar a propósito.** Requieren la aplicación
con datos, y en el entorno de implementación **no hay PostgreSQL levantado**,
así que el backend no sirve nada.

Lo que **sí** se verificó en navegador real (Chrome, 1280 / 768 / 375 px):

- Shell, cabecera de marca, indicador de liga y navegación de seis secciones.
- Navegación inerte y con su aviso cuando no hay liga en contexto (FR-006).
- Estado de error en español, con rótulo "Error", sin detalle técnico, y la
  aplicación navegable (FR-015, FR-016, SC-003).
- `:focus-visible` con contorno sólido de 3 px y desplazamiento de 2 px, sobre
  una pulsación real de `Tab` (FR-024).
- Los 8 elementos enfocables de la pantalla de login, todos con nombre
  accesible; el botón "Menú", oculto a 1280 px, correctamente **fuera** del
  orden de tabulación (FR-025, FR-026).
- Botón "Menú" alternando `aria-expanded` y desplegando la navegación a 375 px
  (FR-005).
- `document.body.scrollWidth === window.innerWidth` en los tres anchos: cero
  desbordamiento horizontal (FR-030, SC-006).

**Actualización tras la ampliación visual (Historia 6).** Con el backend ya
sirviendo datos se recorrieron en navegador real portada, listado y detalle de
liga, partidos, clasificación e inicio de sesión a 1280 / 768 / 375 px: podio y
marcador sobre datos reales, sección activa con marcador no cromático, cero
desbordamiento horizontal a 375 px (T093). **T070 sigue sin marcar**: el
recorrido de teclado de SC-005 exige iniciar sesión con credenciales reales.

Lo que **falta** y necesita backend en marcha: el recorrido de teclado de las
tres tareas de SC-005 (iniciar sesión → crear equipo → registrar resultado), y
los escenarios de `quickstart.md` que dependen de datos — tabla de posiciones
con podio, marcadores en los cuatro estados, escudos ausentes y rotos, y
desplazamiento de tablas anchas dentro de su contenedor.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias
- **Foundational (Phase 2)**: depende del Setup — **bloquea las cinco historias**
- **US1 (Phase 3)**: depende de Phase 2. Sin dependencias de otras historias
- **US2 (Phase 4)**: depende de Phase 2. Sus componentes se muestran dentro del
  shell de US1, pero se prueban por separado y no requieren US1 completa
- **US3 (Phase 5)**: depende de Phase 2. Toca las mismas pantallas que US2, por
  lo que en un único desarrollador conviene ejecutarla **después** de US2 para
  evitar dos remarcados sobre los mismos archivos
- **US4 (Phase 6)**: depende de Phase 2; T065 solo tiene sentido cuando existen
  hojas de componente, es decir, tras US1-US3
- **US5 (Phase 7)**: depende de US1 (el shell que se colapsa) y de US2 (la tabla
  que se desplaza)
- **Polish (Phase 8)**: depende de las historias que se decidan entregar

### Within Each User Story

- Los archivos de un mismo componente (`.tsx` + `.module.css`) son una sola
  tarea: separarlos crearía dos tareas que se bloquean entre sí
- Componentes antes que su aplicación a pantallas
- `lib/` antes que los componentes que lo consumen (T021 antes de T027)
- La migración de selectores cierra cada historia (T020, T037, T062), nunca se
  aplaza a la fase de Polish

### Parallel Opportunities

- **Setup**: T002 y T003 en paralelo
- **US1**: T007, T008, T009 y T010 en paralelo (cuatro archivos distintos);
  después T018 y T019 en paralelo
- **US2**: T021 a T026 en paralelo (seis archivos distintos); T031 a T034 en
  paralelo (cuatro pantallas distintas); T035 y T036 en paralelo
- **US3**: T038 a T043 en paralelo; T045 a T049 en paralelo (pantallas de
  consulta); T050 a T057 en paralelo (formularios, un archivo cada uno);
  T059 a T061 en paralelo
- **US4**: T063, T064 y T069 en paralelo
- **US5**: T073, T074 y T075 en paralelo
- Con varios desarrolladores, US2 y US3 se reparten por pantalla; el conflicto
  real es que ambas tocan los mismos archivos de `features/`

---

## Parallel Example: User Story 2

```bash
# Catálogo de datos: seis archivos independientes, a la vez
Task: "Crear frontend/src/lib/formato.ts"
Task: "Implementar Panel.tsx en frontend/src/components/datos/"
Task: "Implementar TablaDeDatos.tsx en frontend/src/components/datos/"
Task: "Implementar DistintivoDeEstado.tsx en frontend/src/components/datos/"
Task: "Implementar EscudoEquipo.tsx en frontend/src/components/datos/"
Task: "Implementar DestacadoDePodio.tsx en frontend/src/components/datos/"

# Aplicación a pantallas: cuatro archivos distintos, a la vez
Task: "Aplicar el catálogo en features/matches/MatchDetailPage.tsx"
Task: "Aplicar el catálogo en features/teams/TeamsPage.tsx"
Task: "Aplicar el catálogo en features/leagues/LeaguesPage.tsx"
Task: "Aplicar el catálogo en features/players/PlayersPage.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Phase 1: Setup
2. Phase 2: Foundational (bloquea todo)
3. Phase 3: US1 — shell, marca, liga en contexto, sección activa
4. **PARAR Y VALIDAR**: escenarios 1-6 de `quickstart.md` y suite en verde
5. Ya es demostrable: la aplicación deja de parecer un prototipo sin estilos

### Incremental Delivery

1. Setup + Foundational → tokens disponibles
2. US1 → shell en todas las pantallas → demo (MVP)
3. US2 → los datos se leen de un vistazo → demo
4. US3 → carga, vacío y error explícitos → demo
5. US4 → contraste y teclado como gate → demo
6. US5 → 1280 / 768 / 375 px → demo
7. Cada historia añade valor sin romper la anterior: la suite lo verifica al
   cierre de cada fase

### Nota sobre el orden de US4

[plan.md](./plan.md) §Orden de entrega sitúa la prueba de contraste y la
auditoría de tokens en P4, no en la fase Foundational. La consecuencia es que
las hojas escritas en US1-US3 pueden acumular literales que T065 tenga que
corregir después. Es aceptable porque los tokens (T004) existen desde el
principio y el contrato de estilo
([contracts/ui-contracts.md](./contracts/ui-contracts.md) §6) obliga a usarlos
desde la primera hoja. Si se prefiere el gate desde el minuto uno, T063 y T064
pueden adelantarse a la Phase 2 sin cambiar ninguna otra dependencia.

---

## Notes

- `[P]` = archivos distintos, sin dependencias entre sí
- Cada componente se entrega con su `.module.css`: son una unidad, no dos tareas
- Ninguna tarea toca `backend/`, `alembic/` ni un contrato de API (FR-032)
- Ninguna tarea borra, salta ni debilita una prueba existente (Principio IV)
- Commit por tarea o por grupo lógico, con `feat(012): …` (`AGENTS.md`)
- Parar en cualquier checkpoint para validar la historia por separado

---

## Post-cierre: integración con specs/010 y specs/011 (2026-08-21)

T007, T010, T015 y T017 se ejecutaron cuando `specs/010-alineaciones-estadisticas`
y `specs/011-dashboard-liga` seguían sin entregar: Dashboard y Estadísticas
apuntaban a `PendienteDeEntrega`. Ambas specs se entregaron y se mezclaron a
`main` después; al traer `main` de vuelta a esta rama, la resolución de
conflictos en `frontend/src/routes.tsx` dejó **dos** rutas para
`/leagues/:id/dashboard` (la real y la de `PendienteDeEntrega`, ganando la
primera por orden mas dejando la segunda como código muerto) y ninguna ruta
real para Estadísticas, y además revirtió `/` de `Portada` a un `Inicio`
inline previo a esta historia. No son tareas nuevas del catálogo original;
se registran aquí como corrección post-cierre:

- [X] Restaurar `/` → `Portada` en `routes.tsx` (regresión de merge).
- [X] Eliminar las rutas muertas de `PendienteDeEntrega` para Dashboard y
  Estadísticas; ambas secciones navegan ya a sus pantallas reales
  (`DashboardPage`, `specs/011`; `TopScorersPage` vía `/leagues/:id/top-scorers`,
  `specs/010`).
- [X] Quitar el campo `pendiente` de `Seccion` (`secciones.ts`,
  `contracts/ui-contracts.md`) y el componente `PendienteDeEntrega`: sin
  secciones pendientes, era código sin ningún llamador.
- [X] Actualizar `spec.md` (Assumptions, Edge Cases) y `data-model.md` §2.1
  para reflejar que las seis secciones están entregadas.
- [X] Ajustar `frontend/src/features/inicio/__tests__/portada.test.tsx` (ya
  no hay `pendiente` que filtrar) — suite en verde.
- [X] Extender `useLigaEnContexto` para resolver `/players/:playerId/*` (vía
  el equipo del jugador): al apuntar Estadísticas a la ficha individual, esa
  ruta pasó a formar parte de un `coincide`, y sin resolución de liga el
  shell no pintaba ninguna sección en ella (FR-004, FR-006).
- [X] Restilizar `DashboardPage.tsx`, `TopScorersPage.tsx` y
  `PlayerStatsPage.tsx` con el catálogo de `specs/012` (`Panel`,
  `TablaDeDatos`, `FilaDeMarcador`, `DestacadoDePodio`, los tres estados de
  pantalla y `mensajeDeError`): specs/010 y specs/011 se construyeron antes
  de que este catálogo existiera formalmente, con HTML sin estilo propio —
  el mismo estado que tenían specs/001 a 009 antes de esta historia
  (FR-031 ahora también cubre estas dos pantallas).
- [X] Diagnóstico de la "ficha del partido" rota reportada tras el `pull`:
  no era una regresión de código sino la base de datos local, detenida en
  la rama de migración `020b6dc9a54e` en vez de la cabeza fusionada
  `919f3bd57721` (`alembic heads`/`alembic current` lo confirman). Un
  `alembic upgrade head` local lo resuelve; no aplica ningún cambio de
  código ni de migración nueva.

## Post-cierre: paridad con la maqueta de referencia en Dashboard y ficha del partido (2026-08-21)

Con Dashboard y Estadísticas ya integradas, se pidió acercar su acabado al de
la maqueta `LeagueFlow Wow` (ver spec.md, Assumptions) en vez de quedarse en
la versión mínima de la primera integración. FR-032/FR-035 siguen intactos:
0 contratos de API nuevos, todo compuesto en el cliente a partir de
`specs/003`, `specs/005`, `specs/008`, `specs/010` y `specs/011`.

- [X] `DashboardPage.tsx`: tarjetas "Próximo partido", "Estado de la
  temporada" (jugados/programados/cancelados — adaptación honesta de
  "ganados/empates/perdidos", que es una estadística por equipo, no de
  liga), "Goles por fecha" (adaptación de "por jornada": `Match` no tiene
  ese campo), contadores "Equipos"/"Jugadores" y "Temporada completada"
  (anillo `conic-gradient`, sin librería de gráficos — decisión de stack que
  esta historia no puede tomar, `AGENTS.md` §5).
- [X] Nuevo componente de catálogo `GraficoDeBarras` (`components/datos/`):
  gráfico de barras con el valor siempre visible como texto (FR-028).
  Documentado en `contracts/ui-contracts.md` §2.
- [X] `MatchDetailPage.tsx`: dos bugs reales de la resolución de conflictos
  de merge, no solo estilo — `ResultForm` y `CorrectionRequestForm` se
  renderizaban **dos veces** cada uno. Se corrige y se añade una prueba de
  regresión (`events.test.tsx`). Se retiran además las líneas de texto
  plano "Estado: finished" / "Marcador vigente: …" (raw enum sin traducir,
  redundante con `FilaDeMarcador`+`DistintivoDeEstado` ya mostrados
  arriba), y "Alineación"/"Goles" pasan a vivir en `Panel` con
  `EscudoEquipo` por fila (los goles de visitante se leen en espejo:
  la posición, no solo el color, distingue el equipo — FR-028).
- [X] `LineupForm.tsx`: no tenía ningún estilo del catálogo (checkboxes sin
  marcado, sin `Boton`, sin `.lf-formulario`) — mismo estado en el que
  estaban Dashboard/Estadísticas antes de esta historia. Se alinea con el
  resto de formularios de la aplicación.
- [X] Rejilla del Dashboard: la primera versión de las tarjetas usaba dos
  columnas iguales (`1fr 1fr`) más bloques a ancho completo apilados. Con
  contenido de alto muy distinto entre tarjetas de la misma fila (p. ej.
  "Goles por fecha" corta junto a "Tabla de posiciones" larga), eso dejaba
  huecos vacíos irregulares al pie de las tarjetas cortas. Se midió el DOM
  real de la maqueta `LeagueFlow Wow` (`getComputedStyle`/`getBoundingClientRect`
  sobre el HTML exportado) y resultó ser una rejilla de **12 columnas**:
  fila 1 en 5/7 (Próximo partido / Estado de la temporada), fila de tabla en
  7/5 (Tabla de posiciones / columna con Goles por fecha + Equipos +
  Jugadores). Se adoptó esa proporción con `grid-column: span N` y
  `align-items: stretch` propagado a la tarjeta interior (`Panel` o
  `.columnaSecundaria`), así que la tarjeta corta se estira a la altura de
  la larga en vez de dejar un hueco fuera de cualquier tarjeta. Por debajo de
  1024px cada tarjeta vuelve a ocupar las 12 columnas (una por fila).
- [X] Paridad final de tarjetas con la maqueta: aun con la rejilla correcta,
  el panel seguía mostrando **nueve** tarjetas frente a las **siete** de la
  maqueta, porque `specs/011` publicaba dos listas propias ("Últimos
  resultados" y "Próximos partidos") que la maqueta no dibuja. "Próximos
  partidos" era además el **mismo dato** que "Próximo partido" —ambos leen
  `upcoming_matches`—, así que el panel enseñaba el próximo encuentro dos
  veces seguidas. Se retiran ambas listas; el calendario completo sigue a un
  clic desde el enlace "Ver calendario" de la propia tarjeta. Se añaden los
  enlaces de cabecera que la maqueta sí dibuja, vía la prop `acciones` de
  `Panel` (ya en el catálogo, sin componente nuevo): "Ver calendario", "Ver
  estadísticas" y "Ver tabla completa", en lugar de los dos enlaces sueltos
  que colgaban bajo el `<h1>`. Los números de "Estado de la temporada" pasan
  al color de su segmento en la barra, como en la maqueta; eso suma dos
  pares a la auditoría de contraste (`exito sobre superficie`, `aviso sobre
  superficie`), ambos verificados por `contraste.test.ts`.
- [X] Refactor final a la disposición de la maqueta, pieza por pieza:
  - **Cabecera** (`AppShell`): el **título de la pantalla** a la izquierda a
    tamaño de titular ("Dashboard de la liga", "Equipos", "Ficha del
    partido"…), píldora de sesión a la derecha, y el selector de liga movido
    de la esquina a una fila propia bajo la cabecera, con el badge de
    iniciales y un botón secundario "Cambiar liga" → `/leagues`. El buscador
    global y la campana **no** se dibujan: no hay endpoint que los sirva
    (FR-032/FR-035); dibujar controles inertes es peor que omitirlos.
  - **`TituloDePantalla`** (componente nuevo del catálogo): mueve el `<h1>`
    de cada pantalla a la cabecera del marco mediante un portal. Se probó
    primero con un saludo fijo ("Hola, {usuario} · {rol}") en ese hueco,
    pero el título de la pantalla es lo que de verdad orienta al usuario y
    el nombre de usuario ya está en la píldora de sesión, al lado. Las 16
    pantallas pasan de `<h1>…</h1>` a `<TituloDePantalla>…</TituloDePantalla>`;
    sigue habiendo exactamente un `<h1>` por pantalla (FR-027) y las pruebas
    que renderizan una pantalla suelta lo siguen encontrando, porque sin
    shell el portal no tiene destino y el `<h1>` cae en su sitio natural.
    La portada (`/`) es la excepción: su `<h1>LeagueFlow</h1>` es el titular
    del bloque principal, no una etiqueta de sección, y se queda ahí.
  - **Próximo partido**: deja de ser una fila de marcador y pasa a ser el
    bloque de la maqueta — fecha arriba, dos badges circulares grandes
    enfrentados con "VS" al centro y el nombre de cada equipo debajo, todo
    dentro de un único enlace al partido. Sin "Jornada N" ni sede: `Match`
    (`specs/005`) no tiene esos campos.
  - **Rendimiento de la temporada**: barra segmentada de tres colores +
    grid de 4 métricas, con las etiquetas corregidas a Jugados / Gana local
    / Empates / Gana visitante (ver spec.md — "ganados/perdidos" a nivel de
    liga es siempre el mismo número).
  - **Tabla de posiciones**: columna EQUIPO con badge circular + nombre,
    columna DG (antes GD) y más alto vertical al ocupar 7/12.
  - **Goles por fecha**: hasta 12 barras (antes 8), la última destacada en
    acento —nueva prop `destacarUltima` de `GraficoDeBarras`— y ancho de
    barra acotado para que una liga con una sola fecha no pinte un bloque
    del ancho de la tarjeta.
  - **Equipos / Jugadores**: dos tarjetas compactas con la etiqueta encima
    del número, como la maqueta.
  - **Temporada completada**: banner con degradado de acento, porcentaje en
    texto gigante a la izquierda y anillo tipo *donut* a la derecha
    (`conic-gradient` + `mask`, sin librería de gráficos).
  - `EscudoEquipo` gana `tamano: 'lg'` y `circular` para los badges
    redondos de la maqueta, en el catálogo y no como CSS suelto de pantalla.
