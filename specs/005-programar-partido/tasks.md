---

description: "Task list for feature implementation"
---

# Tasks: Programar un partido

**Input**: Design documents from `/specs/005-programar-partido/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md — todos presentes.

**Tests**: incluidas. Principio II: mismo equipo, equipos de otra liga / inactivos, rol organizador, nacimiento sin marcador.

**Organization**: una sola User Story (P1). Sin fase de Setup: la infraestructura la construyó `specs/001-*`.

**⚠️ Bloqueante**: `specs/001-*`, `specs/002-*` y `specs/003-registrar-equipos` en `main`. No requiere `004`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo (archivo distinto, sin dependencias pendientes)
- **[US1]**: tarea de la User Story 1 (única de esta spec)
- Rutas según `plan.md` → Project Structure

---

## Phase 1: Foundational (Blocking Prerequisites)

- [X] T001 Crear el modelo SQLAlchemy `Match` en `backend/src/matches/models.py`, usando `Base` y los mixins de `backend/src/core/models_base.py` (incl. `TimestampUpdated`; data-model.md; campos según `specs/001-*/data-model.md` §Match)
- [X] T002 Generar la migración Alembic de la tabla `matches` en `backend/alembic/versions/`: FKs `ON DELETE RESTRICT`, columnas de marcador nullable, CHECK `home_team_id <> away_team_id` (data-model.md; research.md §4, §5; depende de T001)

**Checkpoint**: esquema listo.

---

## Phase 2: User Story 1 - Programar un partido (Priority: P1) 🎯 MVP

**Goal**: el organizador programa un partido entre dos equipos distintos de la misma liga; cualquiera consulta listado y detalle.

**Independent Test**: crear un partido A vs B con fecha y verificar que aparece en el listado de la liga con estado `scheduled` (`quickstart.md`; AS1).

### Tests for User Story 1 ⚠️

> Escribir primero y verificar que fallan antes de implementar.

- [X] T003 [P] [US1] Contract test de `POST/GET /leagues/{id}/matches` y `GET /matches/{id}` contra `contracts/matches.openapi.yaml`, incluidos los `error.code` de cada 4xx, en `backend/tests/contract/test_matches_contract.py`
- [X] T004 [P] [US1] Integration test de los 4 Acceptance Scenarios de `spec.md` más: equipo inactivo → 404, detalle público, y marcadores null al crear (research.md §3, §4), en `backend/tests/integration/test_matches.py`

### Implementation for User Story 1

- [X] T005 [P] [US1] Crear los schemas Pydantic `CreateMatchRequest`, `Match` y `PaginatedMatches` en `backend/src/matches/schemas.py` (`contracts/matches.openapi.yaml`)
- [X] T006 [US1] Implementar `MatchService` en `backend/src/matches/service.py`: validar liga, equipos activos de esa liga, `home != away`, crear con `status=scheduled` y scores null (FR-001–FR-003; research.md §3; depende de T001)
- [X] T007 [US1] Implementar el router en `backend/src/matches/router.py`: `POST` con `require_role("organizador")`, `GET` listado y detalle públicos (FR-005, FR-006; depende de T005, T006)
- [X] T008 [US1] Registrar el router de partidos en `backend/src/main.py` y el modelo en `backend/alembic/env.py` (depende de T007)
- [X] T009 [P] [US1] Crear el cliente HTTP de partidos en `frontend/src/features/matches/api.ts` sobre `services/apiClient.ts`
- [X] T010 [US1] Crear el listado en `frontend/src/features/matches/MatchesPage.tsx`, enlace desde `LeagueDetailPage`, rutas en `frontend/src/routes.tsx` (`/leagues/:id/matches`) (depende de T009)
- [X] T011 [US1] Crear el formulario de alta en `frontend/src/features/matches/CreateMatchForm.tsx` (selectores de equipos de la liga + datetime), visible solo para organizador; ruta `/leagues/:id/matches/new` (depende de T009)
- [X] T012 [P] [US1] Tests Vitest del listado y el formulario en `frontend/src/features/matches/__tests__/matches.test.tsx` (depende de T010, T011)

**Checkpoint**: User Story 1 funcional y testeable de forma independiente.

---

## Phase 3: Polish & Cross-Cutting Concerns

- [X] T013 [P] Ejecutar los 6 escenarios de `quickstart.md` de punta a punta contra el entorno local
- [X] T014 [P] Registrar las métricas de la HU en `docs/metricas/005-programar-partido.md` desde `docs/metricas/_plantilla.md` (`AGENTS.md` §7) — sin inventar costo de IA ni tiempo real de trabajo
- [ ] T015 Verificar en el entorno desplegado que programar partidos funciona con la sesión cross-domain (Vercel → Railway)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: depende de `001`–`003` en `main`
- **User Story 1 (Phase 2)**: depende de la Fase 1
- **Polish (Phase 3)**: depende de la User Story 1

### Dentro de la User Story 1

- Tests (T003-T004) primero y deben fallar
- Modelo (T001) → migración (T002) → schemas (T005) → servicio (T006) → router (T007) → registro (T008)
- Frontend: cliente (T009) → vistas (T010-T011) → tests (T012)

### Parallel Opportunities

- T003 y T004 en paralelo
- T005 en paralelo con el inicio de T006
- Backend (T005-T008) y frontend (T009-T012) son carriles paralelos si hay dos personas

---

## Implementation Strategy

MVP = spec completa (una sola User Story). Orden: Fase 1 → 2 → 3 → PR. Esta HU
desbloquea `006` (resultado) y `007` (calendario).

---

## Notes

- `[P]` = archivos distintos, sin dependencias pendientes
- Acceso a ligas/equipos solo por sus servicios (Principio VIII)
- T015 queda pendiente hasta el merge del PR
