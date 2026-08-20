# Tasks: Consultar el calendario y los resultados

**Input**: Design documents from `/specs/007-consultar-calendario/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/calendar.openapi.yaml`, `quickstart.md`

**Tests**: obligatorios por los Acceptance Scenarios, FR-001–FR-003 y los
Principios II y IV de la constitución. Las pruebas se escriben y se comprueba
que fallen por la funcionalidad ausente antes de implementar.

**Organization**: la spec contiene una única historia P1. Todas las tareas de
producto están etiquetadas `[US1]`; Setup, Foundational y cierre no llevan
etiqueta de historia.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo porque trabaja en archivos distintos y
  no depende de una tarea incompleta del mismo grupo.
- **[US1]**: Consultar el calendario y los resultados.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: confirmar que el listado de 005 y los resultados de 006 están
operativos antes de cambiar su proyección pública.

- [X] T001 Ejecutar la regresión base de partidos y resultados con `backend/tests/contract/test_matches_contract.py`, `backend/tests/contract/test_results_contract.py`, `backend/tests/integration/test_matches.py`, `backend/tests/integration/test_results.py`, `frontend/src/features/matches/__tests__/matches.test.tsx` y `frontend/src/features/matches/__tests__/results.test.tsx`, deteniendo la implementación si falla una prueba existente

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: disponer de datos reproducibles para orden, filtros, acceso
anónimo y volumen sin crear infraestructura nueva.

**⚠️ CRITICAL**: US1 no comienza hasta tener fixtures capaces de crear
partidos con fechas/estados controlados y un calendario de 190 partidos.

- [X] T002 Añadir fixtures reutilizables de liga vacía, partidos con fechas y estados controlados y carga masiva de 20 equipos/190 partidos en `backend/tests/conftest.py`, y un generador persistente idempotente para la medición manual en `backend/scripts/seed_calendar_performance.py`, usando el organizador configurado por entorno sin imprimir ni guardar secretos

**Checkpoint**: baseline en verde y escenarios del calendario reproducibles.

---

## Phase 3: User Story 1 - Consultar el calendario y los resultados (Priority: P1) 🎯 MVP

**Goal**: ofrecer a cualquier visitante un calendario público con próximos en
orden ascendente, jugados con marcador en orden descendente, estado vacío y
filtro por los cuatro estados, cargando todas las páginas necesarias.

**Independent Test**: sin sesión, abrir una liga con partidos `scheduled` y
`finished`; verificar ambos grupos y sus órdenes, aplicar cada filtro y
comprobar que una liga vacía muestra un mensaje. Con 190 partidos, comprobar
que todos se cargan y el próximo queda visible primero.

### Tests for User Story 1 — write first, verify they fail

- [X] T003 [P] [US1] Crear pruebas de contrato para `status`, enum, paginación, acceso público, orden documentado, respuesta vacía y envelope de `specs/007-consultar-calendario/contracts/calendar.openapi.yaml` en `backend/tests/contract/test_calendar_contract.py`
- [X] T004 [P] [US1] Crear pruebas de integración para próximos ASC, jugados DESC con marcador, desempate por id, cuatro filtros, consulta sin filtro compatible con 005, liga vacía, liga inexistente, ausencia de sesión y 190 filas paginadas en `backend/tests/integration/test_calendar.py`
- [X] T005 [P] [US1] Crear pruebas de UI para grupos, nombres, fechas, marcadores, selector accesible de cuatro estados, estado vacío, sesión anónima, navegación en máximo dos interacciones y carga completa paginada en `frontend/src/features/matches/__tests__/calendar.test.tsx`

### Backend implementation for User Story 1

- [X] T006 [P] [US1] Definir el tipo de estado de partido reutilizable conforme al enum OpenAPI sin alterar el schema de respuesta en `backend/src/matches/schemas.py`
- [X] T007 [US1] Extender `MatchService.listar_partidos` con filtro opcional parametrizado y orden estable `finished: scheduled_at DESC, id DESC`; demás/sin filtro: `scheduled_at ASC, id ASC` en `backend/src/matches/service.py`
- [X] T008 [US1] Exponer y validar el query param opcional `status` en el GET público existente, conservando paginación, `league_not_found`, envelope y compatibilidad de 005 en `backend/src/matches/router.py`

### Frontend implementation for User Story 1

- [X] T009 [P] [US1] Extender los tipos y el cliente de calendario con estado tipado, query param y recorrido de páginas hasta `total` con `page_size=100` en `frontend/src/features/matches/api.ts`
- [X] T010 [US1] Refactorizar la carga de `MatchesPage` para solicitar equipos y colecciones de partidos en paralelo, separar `scheduled`/`finished`, reaccionar al filtro y evitar resultados obsoletos al cambiarlo en `frontend/src/features/matches/MatchesPage.tsx`
- [X] T011 [US1] Implementar en español los grupos “Próximos partidos” y “Partidos jugados”, marcador solo para finalizados, filtros `Todos/Programados/En curso/Finalizados/Cancelados`, estado vacío y enlaces a ficha en `frontend/src/features/matches/MatchesPage.tsx`
- [X] T012 [US1] Asegurar accesibilidad del selector, estados de carga/error y descubrimiento del próximo partido desde `frontend/src/features/leagues/LeagueDetailPage.tsx` y `frontend/src/features/matches/MatchesPage.tsx` sin exigir sesión

### Story verification

- [X] T013 [US1] Ejecutar `backend/tests/contract/test_calendar_contract.py`, `backend/tests/integration/test_calendar.py` y `frontend/src/features/matches/__tests__/calendar.test.tsx`, corrigiendo la implementación sin borrar, saltar ni debilitar pruebas

**Checkpoint**: los cuatro Acceptance Scenarios y el edge case funcionan de
forma independiente; US1 está lista como MVP.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: comprobar rendimiento, compatibilidad, seguridad, guía
reproducible y métricas de cierre.

- [X] T014 [P] Revisar que la consulta use exclusivamente SQLAlchemy parametrizado, que el enum inválido produzca `400 validation_error`, que no se exijan cookies y que los mensajes no expongan stack traces en `backend/src/matches/service.py`, `backend/src/matches/router.py` y `backend/src/core/errors.py`
- [X] T015 Verificar que no existe delta de esquema ejecutando `uv run alembic check` y confirmando que la HU 007 no añade migraciones en `backend/alembic/versions/`
- [X] T016 Ejecutar todos los escenarios de `specs/007-consultar-calendario/quickstart.md`, generar el escenario persistente con `backend/scripts/seed_calendar_performance.py`, medir SC-001 con 20 equipos/190 partidos en menos de 2 segundos y SC-002 en máximo dos interacciones, registrando la evidencia observada sin inventar tiempos
- [X] T017 Ejecutar suites completas y quality gates de `.github/workflows/ci.yml`: pytest, Ruff check/format, Vitest, ESLint, build, `pip-audit` y `npm audit`; corregir regresiones sin modificar requisitos ni debilitar pruebas
- [X] T018 Crear `docs/metricas/007-consultar-calendario.md` desde `docs/metricas/_plantilla.md` y llenar únicamente tareas, tests, ciclos y reprocesos reales, dejando tiempo real y costo de IA para la persona

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: inicia de inmediato y valida 005/006.
- **Foundational (Phase 2)**: depende de T001 y bloquea US1.
- **US1 (Phase 3)**: depende de T002; T003–T005 deben fallar por funcionalidad
  ausente antes de T006–T012.
- **Polish (Phase 4)**: depende de T013 y cierra en orden T014 → T015 → T016
  → T017 → T018, salvo T014 que puede revisarse mientras se documenta.

### User Story Dependencies

- **US1 (P1)**: única historia; comienza tras Foundational y depende de las
  specs 005/006 ya mezcladas, no de otra historia de esta feature.

### Within User Story 1

```text
T003–T005 (pruebas rojas)
       ↓
T006 → T007 → T008
T009 → T010 → T011 → T012
                              ↓
                             T013
```

- T003, T004 y T005 trabajan en suites distintas y son paralelizables.
- T006 fija el tipo backend antes del service/router; T009 deriva en paralelo
  el tipo frontend directamente del contrato.
- T007 precede T008; T006 y T009 no dependen entre sí porque ambos derivan del
  contrato y trabajan en capas distintas.
- T010–T012 comparten componentes y se ejecutan en orden.

### Parallel Opportunities

- T003–T005: contrato, integración y UI en archivos independientes.
- T006 y T009 pueden implementarse en paralelo porque derivan del contrato y
  trabajan en capas y archivos distintos.
- T014 puede revisarse en paralelo con documentación de cierre; T018 espera las
  métricas reales de todas las compuertas.

## Parallel Example: User Story 1

```text
Task: "T003 contrato del calendario en backend/tests/contract/test_calendar_contract.py"
Task: "T004 integración de filtros/orden en backend/tests/integration/test_calendar.py"
Task: "T005 experiencia pública en frontend/src/features/matches/__tests__/calendar.test.tsx"
```

## Implementation Strategy

### MVP First (US1)

1. Completar T001–T002.
2. Escribir T003–T005 y comprobar el fallo esperado.
3. Implementar backend T006–T008.
4. Implementar frontend T009–T012.
5. Ejecutar T013 y validar el calendario anónimo de forma independiente.

### Incremental Delivery Within US1

1. Filtro y orden compatibles en API.
2. Cliente que recorre paginación completa.
3. Grupos, filtros y estados accesibles en UI.
4. Rendimiento, regresión, auditorías y métricas.

### Parallel Team Strategy

- Persona A: contrato, integración y backend (T003–T004, T006–T008).
- Persona B: pruebas UI y frontend (T005, T009–T012).
- Ambas convergen en T013; el cierre T014–T018 es compartido.

## Notes

- Todas las reglas de consulta tienen prueba automatizada antes de cerrar US1.
- No se añaden dependencias, variables de entorno, entidades ni migraciones.
- El GET sin `status` mantiene el contrato y orden de 005.
- Los filtros intermedios no clasifican cancelados/en curso como próximos o jugados.
- SC-001 requiere evidencia medida; nunca se inventa el tiempo.
