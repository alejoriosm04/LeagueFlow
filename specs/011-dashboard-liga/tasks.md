# Tasks: Dashboard general de la liga

**Input**: Design documents from `/specs/011-dashboard-liga/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/dashboard.openapi.yaml`, `quickstart.md`

**Tests**: obligatorias por los cuatro Acceptance Scenarios, FR-001–FR-003 y
los Principios I y II de la constitución ("cada acceptance criterion se
traduce a una prueba automatizada"). El dashboard no añade reglas de negocio
propias — compone 007 y 008 — pero la composición (exactamente 5+5+5, el
orden heredado, el estado vacío) sí es un comportamiento verificable y exige
prueba propia, igual que hizo 008 con FR-002.

**Organization**: la spec contiene una única historia (Priority: P2 en el
backlog). Todas las tareas de producto llevan `[US1]`; Setup, Foundational y
cierre no llevan etiqueta.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo porque trabaja en archivos distintos y
  no depende de una tarea incompleta del mismo grupo.
- **[US1]**: Dashboard general de la liga.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: confirmar que el calendario (007) y la clasificación (008) —las
dos únicas fuentes de este dashboard— están operativos antes de componerlos.

- [X] T001 Ejecutar la regresión base de calendario y clasificación con
      `backend/tests/contract/test_calendar_contract.py`,
      `backend/tests/integration/test_calendar.py`,
      `backend/tests/contract/test_standings_contract.py` y
      `backend/tests/integration/test_standings.py`, deteniendo la
      implementación si falla una prueba existente

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: disponer de un escenario reproducible con más de 5 partidos
finalizados, más de 5 programados y más de 5 equipos, para poder probar el
recorte a 5 y el orden heredado sin ambigüedad.

**⚠️ CRITICAL**: ninguna fixture existente (`calendario_mixto` tiene solo 2+2,
`calendario_190` no tiene partidos `finished`, `clasificacion_liga` tiene 5
filas) cubre los tres bloques a la vez con más de 5 elementos cada uno. US1 no
comienza hasta tener esa fixture.

- [X] T002 Añadir a `backend/tests/conftest.py` la fixture
      `dashboard_resumen(organizador_creado)`: una liga con 7 equipos, 7
      partidos `finished` (marcadores y fechas escalonadas para que el orden
      esperado de "últimos 5" no coincida con el orden de inserción) y 7
      partidos `scheduled` (fechas futuras escalonadas, ídem para "próximos
      5"), devolviendo `league_id` y los IDs/orden esperado de cada bloque
      recortado a 5, siguiendo el patrón de `clasificacion_liga` (equipos
      nombrados y `orden_esperado` explícito)

**Checkpoint**: baseline en verde y escenario de dashboard reproducible con
más de 5 elementos por bloque.

---

## Phase 3: User Story 1 - Dashboard general de la liga (Priority: P2) 🎯 MVP

**Goal**: ofrecer a cualquier visitante, en una sola respuesta pública, los
últimos 5 partidos finalizados, los próximos 5 programados y los primeros 5
lugares de la clasificación de una liga, componiendo `MatchService` (007) y
`StandingsService` (008) sin reimplementar su filtro, orden o cálculo, y sin
error cuando la liga aún no tiene datos (FR-002).

**Independent Test**: con una liga en curso, abrir el dashboard y verificar
que los tres bloques muestran datos coherentes con las vistas de detalle
(`GET /leagues/{id}/matches` y `GET /leagues/{id}/standings`).

### Tests for User Story 1 — write first, verify they fail

- [X] T003 [P] [US1] Crear pruebas de contrato en
      `backend/tests/contract/test_dashboard_contract.py` conforme a
      `specs/011-dashboard-liga/contracts/dashboard.openapi.yaml`: forma
      `{league_id, recent_matches, upcoming_matches, top_standings}`, cada
      lista con `maxItems: 5` y los campos de `Match`/`StandingsRow`
      reutilizados tal cual, acceso sin cookie de sesión (FR-003),
      `404 league_not_found` con envelope compartido para liga inexistente, y
      `400 validation_error` para un `leagueId` que no es UUID
- [X] T004 [P] [US1] Crear pruebas de integración en
      `backend/tests/integration/test_dashboard.py` usando la fixture
      `dashboard_resumen`: `recent_matches` son exactamente los 5 `finished`
      más recientes en el mismo orden que
      `GET /leagues/{id}/matches?status=finished`, `upcoming_matches` son
      exactamente los 5 `scheduled` más próximos en el mismo orden que
      `status=scheduled`, `top_standings` son exactamente las 5 primeras filas
      de `GET /leagues/{id}/standings` en el mismo orden (comparación directa
      contra esos dos endpoints, no contra valores fijos, para probar
      composición sin reimplementación); liga sin equipos ni partidos
      devuelve `200` con las tres listas vacías (FR-002, AS2); liga con
      equipos registrados pero sin partidos (AS5) devuelve
      `recent_matches`/`upcoming_matches` vacíos y `top_standings` **no**
      vacío, con todos los equipos en cero (Assumption "Bloque de
      clasificación vacío" de `spec.md`); tras
      `PUT /matches/{id}/result` sobre un partido antes `scheduled`, el
      dashboard recargado lo refleja en `recent_matches` y ya no en
      `upcoming_matches`, y la clasificación del bloque cambia sin recálculo
      manual (AS3); liga inexistente devuelve `404 league_not_found` (AS
      heredado de 007/008)
- [X] T005 [P] [US1] Crear pruebas de UI en
      `frontend/src/features/dashboard/__tests__/dashboard.test.tsx`: los
      tres bloques con encabezado en español, máximo 5 filas visibles por
      bloque con los datos de `dashboard_resumen`, mensaje de estado vacío
      propio por bloque cuando su lista llega vacía, acceso en sesión anónima
      sin redirección al login, y presencia de un enlace "Ver clasificación
      completa" hacia `/leagues/:id/standings` (soporte de SC-001: 1
      interacción desde el dashboard)

### Backend implementation for User Story 1

- [X] T006 [P] [US1] Añadir `Index("ix_matches_league_status_scheduled",
      "league_id", "status", "scheduled_at")` a `__table_args__` de `Match`
      en `backend/src/matches/models.py` — solo el índice; ninguna columna ni
      constraint cambia (`research.md` §4, `data-model.md` §Migración)
- [X] T007 [US1] Generar la migración Alembic aditiva con
      `uv run alembic revision --autogenerate -m "indice matches liga status fecha"`
      desde `backend/` (down_revision `020b6dc9a54e`, la cabeza actual),
      revisar el diff y confirmar que **solo** crea
      `ix_matches_league_status_scheduled`, sin tocar
      `ix_teams_unique_league_name`, `ix_leagues_unique_name_season` ni
      ningún índice de `result_correction_requests`/`match_events`
      (gotcha de índices funcionales, `AGENTS.md`) — depende de T006
- [X] T008 [P] [US1] Definir `DashboardSummary` en
      `backend/src/statistics/schemas.py`, con `league_id`,
      `recent_matches: list[Match]`, `upcoming_matches: list[Match]` y
      `top_standings: list[StandingsRow]`, importando `Match` desde
      `src.matches.schemas` y reutilizando `StandingsRow` ya declarado en
      este archivo — sin redeclarar sus propiedades
- [X] T009 [US1] Implementar `DashboardService.obtener_resumen(league_id) ->
      DashboardSummary` en `backend/src/statistics/service.py`: llama dos
      veces a `MatchService.listar_partidos(league_id, page=1, page_size=5,
      match_status=...)` (`"finished"` y `"scheduled"`) y una vez a
      `StandingsService.obtener_clasificacion(league_id).items[:5]`, sin
      construir ninguna consulta SQL ni cálculo propio — depende de T008
- [X] T010 [US1] Exponer `GET /leagues/{liga_id}/dashboard` público, sin
      dependencia de sesión, en `backend/src/statistics/router.py` (mismo
      router ya registrado en `main.py` para `/standings`: no hace falta
      tocar `backend/src/main.py`) — depende de T009

### Frontend implementation for User Story 1

- [X] T011 [P] [US1] Crear tipos `DashboardSummary` y el cliente
      `dashboardApi.obtener` derivados del contrato en
      `frontend/src/features/dashboard/api.ts`, reutilizando el tipo `Match`
      ya exportado por `features/matches/api.ts`, `StandingsRow` por
      `features/standings/api.ts` y `Team`/`teamsApi` por
      `features/teams/api.ts` (no por `matches/api.ts`) en vez de
      redeclararlos — `Team` hace falta porque `Match` solo trae
      `home_team_id`/`away_team_id` (UUIDs), sin nombre de equipo
- [X] T012 [US1] Implementar `frontend/src/features/dashboard/DashboardPage.tsx`
      con los tres bloques ("Últimos resultados", "Próximos partidos", "Tabla
      de posiciones"), estado vacío propio por bloque en español, estados de
      carga/error, y enlaces "Ver calendario completo" y "Ver clasificación
      completa" hacia las rutas ya existentes; para pintar "Equipo A vs
      Equipo B" en los dos bloques de partidos, pedir `teamsApi.listar(id)`
      en paralelo a `dashboardApi.obtener(id)` y construir el mapa
      `id → nombre`, igual que ya hace `MatchesPage.tsx` — depende de T011
- [X] T013 [US1] Registrar la ruta pública `/leagues/:id/dashboard` en
      `frontend/src/routes.tsx` (sin `ProtectedRoute`) y añadir el enlace "Ver
      dashboard" junto a los existentes en
      `frontend/src/features/leagues/LeagueDetailPage.tsx` — depende de T012

### Story verification

- [X] T014 [US1] Ejecutar
      `backend/tests/contract/test_dashboard_contract.py`,
      `backend/tests/integration/test_dashboard.py` y
      `frontend/src/features/dashboard/__tests__/dashboard.test.tsx`,
      corrigiendo la implementación sin borrar, saltar ni debilitar pruebas
      — depende de T003–T013

**Checkpoint**: los cuatro Acceptance Scenarios funcionan de forma
independiente; US1 está lista como MVP de esta feature.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: comprobar seguridad, alcance real de la migración, rendimiento,
guía reproducible y métricas de cierre.

- [X] T015 [P] Revisar que `DashboardService` use exclusivamente los métodos
      ya parametrizados de `MatchService`/`StandingsService` (sin SQL propio),
      que un `leagueId` inválido produzca `400 validation_error`, que no se
      exija cookie de sesión y que ningún mensaje exponga stack traces, en
      `backend/src/statistics/service.py`, `backend/src/statistics/router.py`
      y `backend/src/core/errors.py`
- [X] T016 [P] Verificar con `uv run alembic check` desde `backend/` que la
      única migración pendiente de esta HU es
      `ix_matches_league_status_scheduled`, y confirmar por inspección del
      archivo generado en T007 que no reaparecen `DROP INDEX`/`CREATE INDEX`
      espurios sobre índices de specs anteriores
- [ ] T017 Ejecutar los siete escenarios de
      `specs/011-dashboard-liga/quickstart.md`, medir SC-002 sobre la liga de
      20 equipos/190 partidos generada por
      `backend/scripts/seed_calendar_performance.py` (reutilizado, sin
      generador nuevo) y verificar manualmente SC-001 (clasificación
      alcanzable en 3 interacciones o menos desde el dashboard), registrando
      navegador, equipo y tiempo observado sin inventar cifras
- [X] T018 Ejecutar suites completas y quality gates de
      `.github/workflows/ci.yml`: pytest, Ruff check/format, Vitest, ESLint,
      build, `pip-audit` y `npm audit`; corregir regresiones sin modificar
      requisitos ni debilitar pruebas
- [X] T019 Crear `docs/metricas/011-dashboard-liga.md` desde
      `docs/metricas/_plantilla.md` y llenar únicamente tareas, tests, ciclos
      y reprocesos reales, dejando tiempo real y costo de IA para la persona

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: inicia de inmediato y valida 007/008.
- **Foundational (Phase 2)**: depende de T001 y bloquea US1.
- **US1 (Phase 3)**: depende de T002; T003–T005 deben fallar por
  funcionalidad ausente antes de T006–T013.
- **Polish (Phase 4)**: depende de T014; T015 y T016 pueden correr en
  paralelo, luego T017 → T018 → T019.

### User Story Dependencies

- **US1 (única historia)**: depende de `specs/007-consultar-calendario` y
  `specs/008-consultar-clasificacion` ya mezcladas en `main`, no de otra
  historia de esta feature.

### Within User Story 1

```text
T003  T004  T005   (pruebas rojas, en paralelo)
       ↓
T006 → T007                    T008
                                 ↓
                                T009 → T010
T011 → T012 → T013
                    ↓
                   T014
```

- T003–T005 trabajan en tres suites distintas y son paralelizables.
- T006→T007 (índice + migración) y T008 (schema) son independientes entre sí;
  T009 necesita T008; T010 necesita T009.
- T011 deriva del contrato y no espera al backend; T012 y T013 comparten la
  feature y se ejecutan en orden.

### Parallel Opportunities

- T003–T005: contrato, integración y UI en archivos independientes.
- T006 y T008: modelo/migración y schema en archivos distintos, en paralelo.
- T011 puede empezar en cuanto exista el contrato, antes de que T010 esté
  listo.
- T015 y T016 son revisiones independientes durante el cierre.

## Parallel Example: User Story 1

```text
Task: "T003 contrato y 400/404 en backend/tests/contract/test_dashboard_contract.py"
Task: "T004 composición, recorte a 5 y FR-002 en backend/tests/integration/test_dashboard.py"
Task: "T005 tres bloques y estado vacío en frontend/src/features/dashboard/__tests__/dashboard.test.tsx"
```

## Implementation Strategy

### MVP First (US1)

1. Completar T001–T002.
2. Escribir T003–T005 y comprobar el fallo esperado.
3. Implementar backend T006–T010.
4. Implementar frontend T011–T013.
5. Ejecutar T014 y validar el dashboard anónimo de forma independiente.

### Incremental Delivery Within US1

1. Índice aditivo y `DashboardSummary` como composición pura de 007/008.
2. Endpoint público derivado, con `404`/`400` y sin escritura.
3. Página en la SPA con los tres bloques y sus estados vacíos.
4. Seguridad, alcance real de la migración, rendimiento, auditorías y
   métricas.

### Parallel Team Strategy

- Persona A: contrato e integración + backend (T003–T004, T006–T010).
- Persona B: prueba UI y frontend (T005, T011–T013).
- Ambas convergen en T014; el cierre T015–T019 es compartido.

## Notes

- No se añaden entidades, dependencias ni variables de entorno: la única
  migración es un índice aditivo sobre `matches`, ya usada por 007/008.
- `DashboardService` nunca reimplementa el filtro/orden de `MatchService` ni
  el cálculo de `StandingsService`: los llama tal cual (research.md §2).
- FR-002 no se da por cumplido "porque no hay código que lo permita": las
  tres listas vacías con `200` en T004 son la prueba.
- El escenario de rendimiento reutiliza el script de 007/008; no se crea otro
  generador de datos.
- SC-001 y SC-002 requieren evidencia observada; nunca se inventan cifras.
