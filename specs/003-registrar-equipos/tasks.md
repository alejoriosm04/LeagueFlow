---

description: "Task list for feature implementation"
---

# Tasks: Registrar equipos en una liga

**Input**: Design documents from `/specs/003-registrar-equipos/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md — todos presentes.

**Tests**: incluidas. Principio II de la constitución: esta HU tiene cuatro reglas de negocio (unicidad por liga, independencia entre ligas, validación de escudo, borrado lógico).

**Organization**: una sola User Story (P1). Sin fase de Setup: la infraestructura la construyó `specs/001-fundacion-y-autenticacion`.

**⚠️ Bloqueante**: `specs/001-fundacion-y-autenticacion` y `specs/002-crear-liga` deben estar en `main` — hacen falta `require_role`, el envelope de error, `apiClient.ts` y la tabla `leagues` con su servicio.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo (archivo distinto, sin dependencias pendientes)
- **[US1]**: tarea de la User Story 1 (única de esta spec)
- Rutas según `plan.md` → Project Structure

---

## Phase 1: Foundational (Blocking Prerequisites)

- [X] T001 Crear el modelo SQLAlchemy `Team` en `backend/src/teams/models.py`, usando `Base` y los mixins de `backend/src/core/models_base.py` (data-model.md; campos según `specs/001-*/data-model.md` §Team)
- [X] T002 Generar la migración Alembic de la tabla `teams` en `backend/alembic/versions/`: FK `league_id` con `ON DELETE RESTRICT` e índice único `(league_id, lower(trim(name)))` (data-model.md; depende de T001)

**Checkpoint**: esquema listo.

---

## Phase 2: User Story 1 - Registrar equipos en una liga (Priority: P1) 🎯 MVP

**Goal**: el organizador registra equipos en una liga con nombre único dentro de ella; cualquiera los consulta sin autenticarse.

**Independent Test**: registrar dos equipos en una liga y verificar que ambos aparecen en su listado y no en el de otra liga (`quickstart.md` §Escenarios).

### Tests for User Story 1 ⚠️

> Escribir primero y verificar que fallan antes de implementar.

- [X] T003 [P] [US1] Contract test de `POST/GET /leagues/{id}/teams` y `GET /teams/{id}` contra `contracts/teams.openapi.yaml`, incluidos los `error.code` de cada 4xx, en `backend/tests/contract/test_teams_contract.py`
- [X] T004 [P] [US1] Integration test de los 4 Acceptance Scenarios de `spec.md` más: unicidad insensible a mayúsculas, rechazo de `crest_url` no-https, y que un equipo `inactive` desaparece del listado por defecto pero sigue accesible por id (research.md §1, §3), en `backend/tests/integration/test_teams.py`

### Implementation for User Story 1

- [X] T005 [P] [US1] Crear los schemas Pydantic `CreateTeamRequest`, `Team` y `PaginatedTeams` en `backend/src/teams/schemas.py`, con la validación de `crest_url` como URL https absoluta (`contracts/teams.openapi.yaml`; research.md §1)
- [X] T006 [US1] Implementar `TeamService` en `backend/src/teams/service.py`: normalización del nombre, unicidad por `(league_id, name)` insensible a mayúsculas con captura de la violación de integridad como fallback, y filtrado por `status` según `include_inactive` (FR-001, FR-002, FR-003, FR-005; research.md §3; depende de T001)
- [X] T007 [US1] Implementar el router en `backend/src/teams/router.py`: `POST` protegido con `require_role("organizador")` y `created_by` derivado de la sesión, `GET` de listado y de detalle públicos, con 404 cuando la liga no existe (FR-004; depende de T005, T006)
- [X] T008 [US1] Registrar el router de equipos en `backend/src/main.py` (depende de T007)
- [X] T009 [P] [US1] Crear el cliente HTTP de equipos en `frontend/src/features/teams/api.ts` sobre `services/apiClient.ts`
- [X] T010 [US1] Crear el listado de equipos de una liga en `frontend/src/features/teams/TeamsPage.tsx`, con escudo por defecto cuando `crest_url` es nulo o la imagen falla al cargar (research.md §1; depende de T009)
- [X] T011 [US1] Crear el formulario de alta en `frontend/src/features/teams/CreateTeamForm.tsx`, visible solo para organizador, mostrando el `error.message` del envelope en 409 y 400 (depende de T009)
- [X] T012 [P] [US1] Tests Vitest del listado y el formulario en `frontend/src/features/teams/__tests__/teams.test.tsx` (depende de T010, T011)

**Checkpoint**: User Story 1 funcional y testeable de forma independiente.

---

## Phase 3: Polish & Cross-Cutting Concerns

- [X] T013 [P] Ejecutar los 6 escenarios de `quickstart.md` de punta a punta contra el entorno local
- [X] T014 [P] Registrar las métricas de la HU en `docs/metricas/003-registrar-equipos.md` desde `docs/metricas/_plantilla.md` (`AGENTS.md` §7) — sin inventar costo de IA ni tiempo real de trabajo
- [ ] T015 Verificar en el entorno desplegado que el alta de equipos funciona con la sesión cross-domain (Vercel → Railway)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: depende de `specs/001-*` y `specs/002-*` en `main`
- **User Story 1 (Phase 2)**: depende de la Fase 1
- **Polish (Phase 3)**: depende de la User Story 1

### Dentro de la User Story 1

- Tests (T003-T004) primero y deben fallar
- Modelo (T001) → migración (T002) → schemas (T005) → servicio (T006) → router (T007) → registro (T008)
- Frontend: cliente (T009) → vistas (T010-T011) → tests (T012)

### Parallel Opportunities

- T003 y T004 en paralelo
- T005 en paralelo con el inicio de T006
- T009 puede arrancar apenas exista el contrato; T010 y T011 en paralelo tras T009
- Backend (T005-T008) y frontend (T009-T012) son carriles paralelos si hay dos personas

---

## Implementation Strategy

MVP = spec completa (una sola User Story). Orden: Fase 1 → 2 → 3 → PR. Esta HU
desbloquea `specs/004-registrar-jugadores` y `specs/005-programar-partido`, que
son de otras personas: conviene mezclarla rápido para no dejarlas esperando.

---

## Notes

- `[P]` = archivos distintos, sin dependencias pendientes
- Verificar que T003-T004 fallan antes de implementar
- `require_role`, el envelope de error y la paginación **ya existen** en
  `specs/001-*`: se reutilizan, no se reimplementan
- El módulo accede a ligas por el servicio de `backend/src/leagues/`, nunca
  importando su modelo interno (Principio VIII)
