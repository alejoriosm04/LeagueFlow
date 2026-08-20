# Tasks: Registrar y corregir el resultado de un partido

**Input**: Design documents from `/specs/006-registrar-resultado/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/results.openapi.yaml`, `quickstart.md`

**Tests**: obligatorios por los Acceptance Scenarios, FR-001–FR-013 y los
Principios II y IV de la constitución. Las tareas de prueba de US1 se escriben
y se comprueba que fallen antes de implementar.

**Organization**: la spec contiene una única historia P1. Todas las tareas de
producto están etiquetadas `[US1]`; Setup, Foundational y cierre no llevan
etiqueta de historia.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo porque trabaja en archivos distintos y
  no depende de otra tarea incompleta del mismo grupo.
- **[US1]**: Registrar y corregir el resultado de un partido.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: confirmar que las dependencias 001 y 005 están operativas antes
de ampliar el dominio Match.

- [X] T001 Ejecutar la regresión base de autenticación y partidos con `backend/tests/integration/test_auth.py`, `backend/tests/integration/test_matches.py`, `backend/tests/contract/test_auth_contract.py` y `backend/tests/contract/test_matches_contract.py`, y detener la implementación si alguna prueba existente falla

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: preparar datos de prueba compartidos para todos los escenarios de
registro, corrección y separación solicitante/decisor.

**⚠️ CRITICAL**: US1 no comienza hasta disponer de actores distintos y un
partido programado reproducible.

- [X] T002 Añadir fixtures reutilizables para operador, dos organizadores distintos y partido `scheduled` en `backend/tests/conftest.py`, generando credenciales de prueba dinámicamente para evitar secretos y falsos positivos de GitGuardian

**Checkpoint**: baseline en verde y fixtures disponibles.

---

## Phase 3: User Story 1 - Registrar y corregir el resultado de un partido (Priority: P1) 🎯 MVP

**Goal**: registrar un marcador no negativo que finalice el partido, impedir su
sobrescritura directa y tramitar correcciones pendientes con decisión de un
organizador distinto, historial auditable y seguridad ante concurrencia.

**Independent Test**: registrar 3-1 en un partido programado y comprobar
`finished`; crear una corrección 2-1 y comprobar que el partido conserva 3-1
mientras está pendiente; aprobarla con otro organizador y comprobar 2-1 e
historial completo. Repetir variantes de rechazo, autorización, duplicidad y
concurrencia descritas en `quickstart.md`.

### Tests for User Story 1 — write first, verify they fail

- [X] T003 [P] [US1] Crear pruebas de contrato para los tres paths, schemas, roles, estados HTTP y envelopes de `specs/006-registrar-resultado/contracts/results.openapi.yaml` en `backend/tests/contract/test_results_contract.py`
- [X] T004 [P] [US1] Crear pruebas de integración del resultado inicial: 3-1 finaliza, empate permitido, goles inválidos, partido inexistente, estados `in_progress`/`cancelled` rechazados con `match_not_scheduled`, sobrescritura prohibida, roles y dos registros concurrentes en `backend/tests/integration/test_results.py`
- [X] T005 [P] [US1] Crear pruebas de integración de correcciones: snapshot y pendiente sin alterar Match, aprobación, rechazo con motivo, propuesta idéntica, historial paginado, autoría, autor-decisión prohibida, una pendiente y decisiones concurrentes en `backend/tests/integration/test_result_corrections.py`
- [X] T006 [P] [US1] Crear pruebas de UI para visibilidad por rol, validación, registro, solicitud, decisión e historial en `frontend/src/features/matches/__tests__/results.test.tsx`

### Data model and migration for User Story 1

- [X] T007 [P] [US1] Añadir a `Match` checks de marcador no negativo y coherencia entre estado/marcadores, y definir `ResultCorrectionRequest` con relaciones, checks, estados, snapshots, auditoría e índice único parcial pendiente en `backend/src/matches/models.py`
- [X] T008 [P] [US1] Definir schemas Pydantic para marcador, alta de corrección, decisión condicional, respuesta e historial paginado conforme al OpenAPI en `backend/src/matches/schemas.py`
- [X] T009 [US1] Generar en `backend/alembic/versions/` la migración Alembic de `result_correction_requests` y de los checks nuevos sobre `matches`, probar upgrade desde el head de 005 y downgrade, y eliminar cualquier recreación espuria de `ix_leagues_unique_name_season` o `ix_teams_unique_league_name`

### Backend implementation for User Story 1

- [X] T010 [US1] Implementar en `backend/src/matches/service.py` el registro transaccional `scheduled → finished`, validación de marcador/estado y errores `match_not_found`, `match_not_scheduled` y `result_already_recorded`
- [X] T011 [US1] Implementar en `backend/src/matches/service.py` la creación y consulta paginada de correcciones con trim de motivo, snapshot, índice pendiente traducido a `correction_pending_exists` y orden estable `created_at DESC, id`
- [X] T012 [US1] Implementar en `backend/src/matches/service.py` aprobación/rechazo atómicos, autorización de decisor distinto, motivo obligatorio al rechazar, actualización de Match solo al aprobar y conflictos por decisión repetida/concurrente
- [X] T013 [US1] Exponer PUT de resultado, POST/GET de correcciones y POST de decisión con roles, sesión y envelope compartido en `backend/src/matches/router.py`, manteniendo intactas las rutas de 005

### Frontend implementation for User Story 1

- [X] T014 [US1] Extender tipos y cliente HTTP para resultado, correcciones, historial y decisión desde el contrato en `frontend/src/features/matches/api.ts`
- [X] T015 [P] [US1] Implementar el formulario accesible de marcador no negativo para operador/organizador y manejo de errores en español en `frontend/src/features/matches/ResultForm.tsx`
- [X] T016 [P] [US1] Implementar el formulario de solicitud con marcador propuesto y motivo obligatorio en `frontend/src/features/matches/CorrectionRequestForm.tsx`
- [X] T017 [P] [US1] Implementar controles de aprobación/rechazo solo para organizador, exigiendo motivo al rechazar, en `frontend/src/features/matches/CorrectionDecisionForm.tsx`
- [X] T018 [US1] Construir la ficha pública con marcador vigente, historial auditado y composición de formularios según sesión/rol en `frontend/src/features/matches/MatchDetailPage.tsx`
- [X] T019 [US1] Enlazar cada partido a su ficha y registrar la ruta de detalle sin romper creación/listado en `frontend/src/features/matches/MatchesPage.tsx` y `frontend/src/routes.tsx`

### Story verification

- [X] T020 [US1] Ejecutar `backend/tests/contract/test_results_contract.py`, `backend/tests/integration/test_results.py`, `backend/tests/integration/test_result_corrections.py` y `frontend/src/features/matches/__tests__/results.test.tsx`, corrigiendo la implementación sin borrar, saltar ni debilitar pruebas

**Checkpoint**: los diez Acceptance Scenarios y los tres edge cases funcionan
de forma independiente; US1 está lista como MVP.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: verificar regresión, seguridad, contrato, guía reproducible y
métricas de cierre.

- [X] T021 [P] Revisar sanitización de motivos, ausencia de stack traces y coherencia de todos los códigos/mensajes seguros con `specs/006-registrar-resultado/contracts/results.openapi.yaml` en `backend/src/matches/schemas.py`, `backend/src/matches/service.py` y `backend/src/matches/router.py`
- [X] T022 Ejecutar el flujo completo de `specs/006-registrar-resultado/quickstart.md`, incluyendo concurrencia, historial público, autorización, migración desde una base vacía y medición manual reproducible de SC-001 desde ficha cargada hasta confirmación visible, verificando menos de 30 segundos
- [X] T023 Ejecutar suites completas y quality gates con `backend/pyproject.toml`, `frontend/package.json` y `.github/workflows/ci.yml`: pytest, lint backend, Vitest, lint/build frontend y escaneo de dependencias; corregir regresiones sin modificar requisitos ni debilitar pruebas
- [X] T024 Crear `docs/metricas/006-registrar-resultado.md` desde `docs/metricas/_plantilla.md` y llenar únicamente tareas, tests, ciclos y reprocesos reales, dejando costo/tokens de IA y tiempo real para la persona

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: inicia de inmediato y valida 001/005.
- **Foundational (Phase 2)**: depende de T001 y bloquea US1.
- **US1 (Phase 3)**: depende de T002. Sus pruebas T003–T006 se escriben y
  fallan antes de T007–T019.
- **Polish (Phase 4)**: depende de T020 y cierra la HU en orden
  T021 → T022 → T023 → T024, salvo T021 que puede comenzar en paralelo con la
  revisión de frontend posterior a T020.

### User Story Dependencies

- **US1 (P1)**: única historia; no depende de otras historias. Sí depende de
  las specs ya implementadas 001 y 005.

### Within User Story 1

```text
T003–T006 (tests fallan)
       ↓
T007 ──→ T009
T008 ──┐
       ├→ T010 → T011 → T012 → T013
       └→ T014 → T015/T016/T017 → T018 → T019
                                      ↓
                                     T020
```

- T007 y T008 pueden avanzar en paralelo después de las pruebas.
- T009 depende de T007.
- T010–T013 comparten `service.py`/`router.py` y se ejecutan en orden.
- T014 debe preceder los formularios; T015–T017 son paralelizables.
- T018 integra los formularios; T019 integra navegación; T020 verifica todo.

### Parallel Opportunities

- T003, T004, T005 y T006: contrato, dos suites backend y UI en archivos
  independientes.
- T007 y T008: modelo SQLAlchemy y schemas Pydantic en archivos distintos.
- Después de T014, T015, T016 y T017: tres componentes independientes.
- T021 puede revisarse en paralelo con tareas de documentación de cierre que
  no alteren los mismos archivos, pero T024 solo se llena tras tener métricas.

---

## Parallel Example: User Story 1

```text
Task: "T003 contrato API en backend/tests/contract/test_results_contract.py"
Task: "T004 resultado inicial en backend/tests/integration/test_results.py"
Task: "T005 correcciones en backend/tests/integration/test_result_corrections.py"
Task: "T006 UI en frontend/src/features/matches/__tests__/results.test.tsx"

Después de T014:
Task: "T015 formulario de resultado en ResultForm.tsx"
Task: "T016 formulario de solicitud en CorrectionRequestForm.tsx"
Task: "T017 decisión en CorrectionDecisionForm.tsx"
```

---

## Implementation Strategy

### MVP First (US1)

1. Completar T001–T002.
2. Escribir T003–T006 y confirmar que fallan por funcionalidad ausente.
3. Implementar backend T007–T013 y validar contrato/reglas.
4. Implementar frontend T014–T019.
5. Ejecutar T020 y detenerse para validar el MVP independiente.

### Incremental Delivery Within US1

1. Resultado inicial seguro y atómico: T003/T004 + T007–T010 + ruta de T013.
2. Flujo auditado de correcciones: T005 + T009/T011/T012 + rutas de T013.
3. Experiencia web completa: T006 + T014–T019.
4. Quality gates y métricas: T021–T024.

### Parallel Team Strategy

Tras T002 y con coordinación sobre el contrato:

- Persona A: pruebas y backend (`T003–T005`, `T007–T013`).
- Persona B: pruebas y cliente frontend (`T006`, `T014–T019`).
- La migración T009 se integra antes de ejecutar pruebas backend contra
  PostgreSQL; ambas capas convergen en T020.

---

## Notes

- Todas las reglas de negocio tienen prueba automatizada antes de cerrar US1.
- No se añaden dependencias ni variables de entorno nuevas.
- La migración no toca índices funcionales de ligas/equipos.
- No se implementa clasificación: 008 la deriva después desde `Match`.
- El spec, plan, tareas, código, migración y métricas entran en el mismo PR.
