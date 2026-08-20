# Tasks: Consultar la clasificación

**Input**: Design documents from `/specs/008-consultar-clasificacion/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/standings.openapi.yaml`, `quickstart.md`

**Tests**: obligatorios por los seis Acceptance Scenarios, FR-001–FR-008 y los
Principios II y IV de la constitución. Las pruebas se escriben y se comprueba
que fallen por la funcionalidad ausente antes de implementar. FR-002 es un
requisito negativo: exige prueba propia, no basta con "no implementarlo".

**Organization**: la spec contiene una única historia P1. Todas las tareas de
producto llevan `[US1]`; Setup, Foundational y cierre no llevan etiqueta.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo porque trabaja en archivos distintos y
  no depende de una tarea incompleta del mismo grupo.
- **[US1]**: Consultar la clasificación.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: confirmar que los resultados de 006 —única fuente de la
clasificación— están operativos antes de derivar nada de ellos.

- [X] T001 Ejecutar la regresión base de resultados y calendario con `backend/tests/contract/test_results_contract.py`, `backend/tests/integration/test_results.py`, `backend/tests/integration/test_result_corrections.py` y `backend/tests/integration/test_calendar.py`, deteniendo la implementación si falla una prueba existente

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: disponer de escenarios reproducibles de puntuación y desempate sin
crear infraestructura nueva.

**⚠️ CRITICAL**: US1 no comienza hasta poder construir ligas con marcadores
controlados y con los tres niveles de empate de FR-005/FR-006.

- [X] T002 Añadir a `backend/tests/conftest.py` fixtures reutilizables de liga con equipos y partidos `finished` de marcador controlado, partidos `scheduled`, `in_progress` y `cancelled`, equipo sin partidos, equipo `inactive` con historial y el trío de escenarios de empate (mismos puntos; mismos puntos y GD; mismos puntos, GD y GF), sin escribir credenciales en los fixtures

**Checkpoint**: baseline en verde y escenarios de clasificación reproducibles.

---

## Phase 3: User Story 1 - Consultar la clasificación (Priority: P1) 🎯 MVP

**Goal**: ofrecer a cualquier visitante la tabla de posiciones de una liga,
derivada en lectura de los partidos finalizados, con las ocho estadísticas
por equipo de FR-004, el orden de FR-005/FR-006 y sin ninguna vía de edición
(FR-002).

**Independent Test**: con una liga de al menos tres partidos finalizados,
consultar la clasificación sin sesión y verificar puntos, PJ/G/E/P, GF/GC/GD y
el orden, incluidos los desempates; comprobar que un partido `scheduled` o
`cancelled` no altera la tabla y que no existe forma de editarla.

### Tests for User Story 1 — write first, verify they fail

- [X] T003 [P] [US1] Crear pruebas unitarias de la función pura en `backend/tests/unit/test_standings_calculator.py`: 3/1/0 puntos (AS1, AS2), orden por puntos, por GD y por GF (AS3, AS4), desempate alfabético normalizado y estable ante entrada desordenada (FR-006), exclusión de `scheduled`/`in_progress`/`cancelled` (AS5, FR-007), equipo sin partidos con ceros, equipo `inactive` con historial incluido e `inactive` sin historial excluido, `position` 1..N sin huecos e invariantes `played = won + drawn + lost`, `points = won*3 + drawn`, `goal_difference = goals_for - goals_against` y suma global GF = GC
- [X] T004 [P] [US1] Crear pruebas de contrato en `backend/tests/contract/test_standings_contract.py` conforme a `specs/008-consultar-clasificacion/contracts/standings.openapi.yaml`: forma `{league_id, items}` sin campos de paginación, las once propiedades requeridas de `StandingsRow` con sus tipos, acceso sin cookie de sesión (FR-008), `404 league_not_found` con envelope compartido, y código `405` —solo el status, sin afirmar la forma del cuerpo, que lo produce el router del framework— para `POST`, `PUT`, `PATCH` y `DELETE` sobre `/leagues/{id}/standings` (FR-002, AS6)
- [X] T005 [P] [US1] Crear pruebas de integración extremo a extremo en `backend/tests/integration/test_standings.py`: tabla calculada sobre datos reales, partido `scheduled` que no altera la tabla y `cancelled` que tampoco (AS5, FR-007), corrección de 006 en estado `pending` sobre un partido ya contabilizado que NO altera la tabla, reflejo inmediato tras `PUT /matches/{id}/result` y tras aprobar esa corrección, sin acción de recálculo (SC-002, edge case de correcciones pendientes), mismo orden byte a byte en dos consultas sucesivas (FR-006) y liga sin equipos que devuelve `200` con `items` vacío
- [X] T006 [P] [US1] Crear pruebas de UI en `frontend/src/features/standings/__tests__/standings.test.tsx`: los diez encabezados en español de T015, que cubren las ocho estadísticas de FR-004 más posición y equipo, filas en el orden que entrega la API sin reordenar en cliente, GD negativa con signo, acceso en sesión anónima sin redirección al login, estado vacío, estado de error de liga inexistente, ausencia de cualquier control de edición de puntos o posición (AS6) y enlace “Ver clasificación” desde el detalle de liga

### Backend implementation for User Story 1

- [X] T007 [P] [US1] Definir `StandingsRow` y `Standings` en `backend/src/statistics/schemas.py` con las once propiedades del contrato, `position >= 1` y contadores no negativos
- [X] T008 [P] [US1] Implementar `calcular_clasificacion(equipos, partidos) -> list[StandingsRow]` como función pura sin sesión de base de datos en `backend/src/statistics/calculator.py`, aplicando 3/1/0 (FR-003), contando solo partidos `finished` (FR-001, FR-007), incluyendo equipos activos y los inactivos con historial, y ordenando por `points DESC, goal_difference DESC, goals_for DESC, lower(trim(team_name)) ASC, team_id ASC` antes de numerar `position`
- [X] T009 [P] [US1] Añadir `listar_finalizados(league_id) -> list[Match]` a `backend/src/matches/service.py`, sin paginación y reutilizando la validación de liga existente, sin modificar la firma ni el comportamiento de `listar_partidos`
- [X] T010 [P] [US1] Añadir `listar_por_liga(league_id) -> list[Team]` a `backend/src/teams/service.py`, devolviendo activos e inactivos sin paginación, sin modificar la firma ni el comportamiento de `listar_equipos`
- [X] T011 [US1] Implementar `StandingsService.obtener_clasificacion(league_id)` en `backend/src/statistics/service.py` orquestando `MatchService.listar_finalizados` y `TeamService.listar_por_liga` y delegando el cálculo en `calculator.py`, sin importar los modelos `Match` ni `Team` (Principio VIII) y propagando `404 league_not_found`
- [X] T012 [US1] Exponer `GET /leagues/{liga_id}/standings` público, sin dependencia de sesión y sin ningún verbo de escritura, en `backend/src/statistics/router.py`
- [X] T013 [US1] Registrar el router de estadísticas bajo el prefijo `/api/v1` en `backend/src/main.py`

### Frontend implementation for User Story 1

- [X] T014 [P] [US1] Crear tipos `Standings`/`StandingsRow` y el cliente `standingsApi.obtener` derivados del contrato en `frontend/src/features/standings/api.ts`
- [X] T015 [US1] Implementar `frontend/src/features/standings/StandingsPage.tsx` con la tabla en español (Pos, Equipo, PJ, G, E, P, GF, GC, GD, Pts), estados de carga, error y vacío, encabezados accesibles y ningún control de edición
- [X] T016 [US1] Registrar la ruta pública `/leagues/:id/standings` en `frontend/src/routes.tsx` y añadir el enlace “Ver clasificación” junto a los existentes en `frontend/src/features/leagues/LeagueDetailPage.tsx`

### Story verification

- [X] T017 [US1] Ejecutar `backend/tests/unit/test_standings_calculator.py`, `backend/tests/contract/test_standings_contract.py`, `backend/tests/integration/test_standings.py` y `frontend/src/features/standings/__tests__/standings.test.tsx`, corrigiendo la implementación sin borrar, saltar ni debilitar pruebas

**Checkpoint**: los seis Acceptance Scenarios funcionan de forma independiente;
US1 está lista como MVP.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: comprobar seguridad, ausencia de esquema nuevo, rendimiento,
guía reproducible y métricas de cierre.

- [X] T018 [P] Revisar que la consulta use exclusivamente SQLAlchemy parametrizado, que `leagueId` inválido produzca `400 validation_error`, que no se exija cookie y que ningún mensaje exponga stack traces, en `backend/src/statistics/service.py`, `backend/src/statistics/router.py` y `backend/src/core/errors.py`
- [X] T019 [P] Verificar que no existe delta de esquema ejecutando `uv run alembic check` desde `backend/` y confirmando que la HU 008 no añade archivos a `backend/alembic/versions/`
- [X] T020 Ejecutar los once escenarios de `specs/008-consultar-clasificacion/quickstart.md`, verificar SC-001 comparando la tabla del sistema con el cálculo manual fila a fila, y medir SC-003 sobre la liga de 20 equipos generada por `backend/scripts/seed_calendar_performance.py`, registrando navegador, equipo y tiempo observado sin inventar cifras
- [X] T021 Ejecutar suites completas y quality gates de `.github/workflows/ci.yml`: pytest, Ruff check/format, Vitest, ESLint, build, `pip-audit` y `npm audit`; corregir regresiones sin modificar requisitos ni debilitar pruebas
- [X] T022 Crear `docs/metricas/008-consultar-clasificacion.md` desde `docs/metricas/_plantilla.md` y llenar únicamente tareas, tests, ciclos y reprocesos reales, dejando tiempo real y costo de IA para la persona

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: inicia de inmediato y valida 006.
- **Foundational (Phase 2)**: depende de T001 y bloquea US1.
- **US1 (Phase 3)**: depende de T002; T003–T006 deben fallar por funcionalidad
  ausente antes de T007–T016.
- **Polish (Phase 4)**: depende de T017; T018 y T019 pueden correr en paralelo,
  luego T020 → T021 → T022.

### User Story Dependencies

- **US1 (P1)**: única historia. Depende de `specs/006-registrar-resultado` ya
  mezclada en `main`, no de otra historia de esta feature.

### Within User Story 1

```text
T003–T006 (pruebas rojas)
       ↓
T007  T008  T009  T010
   \    \    /    /
        T011 → T012 → T013
T014 → T015 → T016
                    ↓
                   T017
```

- T003–T006 trabajan en cuatro suites distintas y son paralelizables.
- T007–T010 tocan cuatro archivos distintos y no dependen entre sí.
- T011 necesita el calculador y los dos métodos de servicio; T012 necesita
  T011; T013 cierra el cableado.
- T014 deriva del contrato y no espera al backend; T015 y T016 comparten la
  feature y se ejecutan en orden.

### Parallel Opportunities

- T003–T006: unitarias, contrato, integración y UI en archivos independientes.
- T007–T010: schemas, calculador y los dos métodos de dominio en paralelo.
- T014 puede empezar en cuanto exista el contrato, antes de que T012 esté listo.
- T018 y T019 son revisiones independientes durante el cierre.

## Parallel Example: User Story 1

```text
Task: "T003 reglas de puntuación y desempate en backend/tests/unit/test_standings_calculator.py"
Task: "T004 contrato y 405 de FR-002 en backend/tests/contract/test_standings_contract.py"
Task: "T005 derivación y SC-002 en backend/tests/integration/test_standings.py"
Task: "T006 tabla pública sin edición en frontend/src/features/standings/__tests__/standings.test.tsx"
```

## Implementation Strategy

### MVP First (US1)

1. Completar T001–T002.
2. Escribir T003–T006 y comprobar el fallo esperado.
3. Implementar backend T007–T013.
4. Implementar frontend T014–T016.
5. Ejecutar T017 y validar la clasificación anónima de forma independiente.

### Incremental Delivery Within US1

1. Regla de puntuación y orden probados como función pura.
2. Endpoint público derivado, con `404` y sin verbos de escritura.
3. Tabla en la SPA, accesible y sin controles de edición.
4. Seguridad, ausencia de migración, rendimiento, auditorías y métricas.

### Parallel Team Strategy

- Persona A: unitarias, contrato e integración + backend (T003–T005,
  T007–T013).
- Persona B: pruebas UI y frontend (T006, T014–T016).
- Ambas convergen en T017; el cierre T018–T022 es compartido.

## Notes

- No se añaden entidades, dependencias, variables de entorno ni migraciones:
  `Standings` se deriva en lectura y no se persiste.
- `statistics` nunca importa los modelos `Match` ni `Team`; solo sus servicios.
- FR-002 no se da por cumplido "porque no hay código que lo permita": el `405`
  y la ausencia de controles en UI son la prueba.
- El escenario de rendimiento reutiliza el script de 007; no se crea otro
  generador de datos.
- SC-001 y SC-003 requieren evidencia observada; nunca se inventan cifras.
