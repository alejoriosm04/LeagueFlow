---

description: "Task list for feature implementation"
---

# Tasks: Crear una liga

**Input**: Design documents from `/specs/002-crear-liga/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md — todos presentes.

**Tests**: incluidas. El Principio II de la constitución exige prueba automatizada para toda regla de negocio, y esta HU tiene tres (unicidad, normalización, control de rol).

**Organization**: una sola User Story (P1). No hay fase de Setup: la infraestructura la construyó `specs/001-fundacion-y-autenticacion` y esta HU la reutiliza sin repetirla.

**⚠️ Bloqueante**: `specs/001-fundacion-y-autenticacion` debe estar mezclada a `main` antes de empezar — hacen falta `backend/src/core/` (DB, envelope de error, CORS), `backend/src/auth/dependencies.py` (`require_role`) y `frontend/src/services/apiClient.ts`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo (archivo distinto, sin dependencias pendientes)
- **[US1]**: tarea de la User Story 1 (única de esta spec)
- Rutas según `plan.md` → Project Structure

---

## Phase 1: Foundational (Blocking Prerequisites)

**Purpose**: la tabla que todo lo demás de esta HU necesita.

- [X] T001 Crear el modelo SQLAlchemy `League` en `backend/src/leagues/models.py`, usando el `Base` y los mixins de `backend/src/core/models_base.py` (data-model.md; campos según `specs/001-*/data-model.md` §League)
- [X] T002 Generar la migración Alembic de la tabla `leagues` en `backend/alembic/versions/`, incluido el índice único sobre `(lower(trim(name)), lower(trim(season)))` (data-model.md; research.md §1-2; depende de T001)

**Checkpoint**: esquema listo — la User Story puede empezar.

---

## Phase 2: User Story 1 - Crear una liga (Priority: P1) 🎯 MVP

**Goal**: el organizador crea una liga con nombre y temporada únicos; cualquiera puede listarla y verla sin autenticarse.

**Independent Test**: crear una liga con nombre y temporada válidos y verificar que aparece en el listado y que se puede abrir su ficha vacía (`quickstart.md` §Escenarios).

### Tests for User Story 1 ⚠️

> Escribir primero y verificar que fallan antes de implementar.

- [X] T003 [P] [US1] Contract test de `POST /leagues`, `GET /leagues` y `GET /leagues/{id}` contra `contracts/leagues.openapi.yaml`, incluidos los `error.code` de cada 4xx, en `backend/tests/contract/test_leagues_contract.py`
- [X] T004 [P] [US1] Integration test de los 4 Acceptance Scenarios de `spec.md` más la unicidad insensible a mayúsculas (research.md §2) y la autoría automática de `created_by`, en `backend/tests/integration/test_leagues.py`

### Implementation for User Story 1

- [X] T005 [P] [US1] Crear los schemas Pydantic `CreateLeagueRequest`, `League` y `PaginatedLeagues` en `backend/src/leagues/schemas.py` (`contracts/leagues.openapi.yaml`)
- [X] T006 [US1] Implementar `LeagueService` en `backend/src/leagues/service.py`: normalización de `name`/`season` (trim + colapsar espacios), verificación de unicidad insensible a mayúsculas, y captura de la violación de integridad como fallback de carrera traducida al mismo 409 (FR-001, FR-002; research.md §1-2; depende de T001)
- [X] T007 [US1] Implementar el router en `backend/src/leagues/router.py`: `POST /leagues` protegido con `require_role("organizador")` y `created_by` derivado de la sesión, `GET /leagues` paginado y público, `GET /leagues/{id}` público con 404 (FR-003, FR-004, FR-005; depende de T005, T006)
- [X] T008 [US1] Registrar el router de ligas en `backend/src/main.py` (depende de T007)
- [X] T009 [P] [US1] Crear el cliente HTTP de ligas en `frontend/src/features/leagues/api.ts` sobre `services/apiClient.ts` (`contracts/leagues.openapi.yaml`)
- [X] T010 [US1] Crear la página de listado público en `frontend/src/features/leagues/LeaguesPage.tsx`, con estado vacío legible cuando no hay ligas (depende de T009)
- [X] T011 [US1] Crear la ficha de detalle en `frontend/src/features/leagues/LeagueDetailPage.tsx` (depende de T009)
- [X] T012 [US1] Crear el formulario de creación en `frontend/src/features/leagues/CreateLeagueForm.tsx`, visible solo para organizador vía `ProtectedRoute`, mostrando el `error.message` del envelope al recibir 409 o 400 (depende de T009)
- [X] T013 [P] [US1] Tests Vitest del formulario y el listado en `frontend/src/features/leagues/__tests__/leagues.test.tsx` (depende de T010, T012)

**Checkpoint**: User Story 1 funcional y testeable de forma independiente — MVP de esta spec.

---

## Phase 3: Polish & Cross-Cutting Concerns

- [X] T014 [P] Ejecutar los 6 escenarios de `quickstart.md` de punta a punta contra el entorno local
- [X] T015 [P] Registrar las métricas de la HU en `docs/metricas/002-crear-liga.md` a partir de `docs/metricas/_plantilla.md` (`AGENTS.md` §7) — sin inventar el costo de IA ni el tiempo real de trabajo
- [ ] T016 Verificar en el entorno desplegado que crear una liga funciona con la sesión cross-domain (Vercel → Railway), no solo en local (`specs/001-*/tasks.md` T039)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: depende de que `specs/001-*` esté en `main`
- **User Story 1 (Phase 2)**: depende de la Fase 1
- **Polish (Phase 3)**: depende de la User Story 1

### Dentro de la User Story 1

- Tests (T003-T004) primero y deben fallar
- Modelo (T001) → migración (T002) → schemas (T005) → servicio (T006) → router (T007) → registro (T008)
- Frontend: cliente (T009) → páginas (T010-T012) → tests (T013)

### Parallel Opportunities

- T003 y T004 en paralelo entre sí
- T005 en paralelo con el inicio de T006
- T009 puede arrancar apenas exista el contrato, en paralelo con todo el backend; T010, T011 y T012 en paralelo entre sí una vez listo T009
- Backend (T005-T008) y frontend (T009-T013) son dos carriles paralelos si hay dos personas

---

## Implementation Strategy

Al haber una sola User Story, el MVP es la spec completa. Orden: Fase 1 → Fase
2 → Fase 3 → PR. Esta HU desbloquea `specs/003-registrar-equipos` (y por
transitividad todas las demás), así que conviene mezclarla rápido y no
acumularla con otro trabajo.

---

## Notes

- `[P]` = archivos distintos, sin dependencias pendientes entre sí
- Verificar que T003-T004 fallan antes de implementar T005 en adelante
- El envelope de error, la paginación y `require_role` **ya existen**: se
  reutilizan de `specs/001-*`, no se reimplementan
- Commitear por tarea o grupo lógico; el título del PR es lo que queda en `main`
