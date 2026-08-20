---

description: "Task list for feature implementation"
---

# Tasks: Registrar jugadores en un equipo

**Input**: Design documents from `/specs/004-registrar-jugadores/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md — todos presentes.

**Tests**: incluidas. Principio II de la constitución: esta HU tiene reglas de negocio (unicidad de dorsal, pertenencia a un solo equipo, escritura solo organizador, borrado lógico, rechazo sobre equipo inactivo).

**Organization**: una sola User Story (P1). Sin fase de Setup: la infraestructura la construyó `specs/001-fundacion-y-autenticacion`.

**⚠️ Bloqueante**: `specs/001-*`, `specs/002-*` y `specs/003-registrar-equipos` deben estar en `main` — hacen falta `require_role`, el envelope de error, `apiClient.ts` y la tabla `teams` con su servicio.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo (archivo distinto, sin dependencias pendientes)
- **[US1]**: tarea de la User Story 1 (única de esta spec)
- Rutas según `plan.md` → Project Structure

---

## Phase 1: Foundational (Blocking Prerequisites)

- [X] T001 Crear el modelo SQLAlchemy `Player` en `backend/src/players/models.py`, usando `Base` y los mixins de `backend/src/core/models_base.py` (data-model.md; campos según `specs/001-*/data-model.md` §Player)
- [X] T002 Generar la migración Alembic de la tabla `players` en `backend/alembic/versions/`: FK `team_id` con `ON DELETE RESTRICT` e índice único parcial `(team_id, number) WHERE number IS NOT NULL` (data-model.md; research.md §1; depende de T001)

**Checkpoint**: esquema listo.

---

## Phase 2: User Story 1 - Registrar jugadores en un equipo (Priority: P1) 🎯 MVP

**Goal**: el organizador registra jugadores en un equipo con dorsal único cuando está informado; cualquiera consulta la plantilla sin autenticarse.

**Independent Test**: sobre un equipo existente, registrar tres jugadores y verificar que la plantilla del equipo los lista (`quickstart.md` §Escenarios; AS1 de `spec.md`).

### Tests for User Story 1 ⚠️

> Escribir primero y verificar que fallan antes de implementar.

- [X] T003 [P] [US1] Contract test de `POST/GET /teams/{id}/players` y `GET /players/{id}` contra `contracts/players.openapi.yaml`, incluidos los `error.code` de cada 4xx, en `backend/tests/contract/test_players_contract.py`
- [X] T004 [P] [US1] Integration test de los 4 Acceptance Scenarios de `spec.md` más: rechazo de `number` fuera de 1–99, dos jugadores sin dorsal en el mismo equipo, rechazo de alta sobre equipo `inactive`, y que un jugador `inactive` desaparece del listado por defecto pero sigue accesible por id (research.md §1, §3, §4), en `backend/tests/integration/test_players.py`

### Implementation for User Story 1

- [X] T005 [P] [US1] Crear los schemas Pydantic `CreatePlayerRequest`, `Player` y `PaginatedPlayers` en `backend/src/players/schemas.py`, con `number` en 1–99 o null y `position` ≤ 40 (`contracts/players.openapi.yaml`; research.md §1, §2)
- [X] T006 [US1] Implementar `PlayerService` en `backend/src/players/service.py`: validar equipo activo vía servicio de `teams` (no importar su modelo), unicidad de dorsal con captura de violación de integridad como fallback, y filtrado por `status` según `include_inactive` (FR-001, FR-002, FR-003, FR-005; research.md §3, §4; depende de T001)
- [X] T007 [US1] Implementar el router en `backend/src/players/router.py`: `POST` protegido con `require_role("organizador")` y `created_by` derivado de la sesión, `GET` de listado y de detalle públicos, con 404 cuando el equipo no existe o está inactivo en el alta (FR-004; depende de T005, T006)
- [X] T008 [US1] Registrar el router de jugadores en `backend/src/main.py` (depende de T007)
- [X] T009 [P] [US1] Crear el cliente HTTP de jugadores en `frontend/src/features/players/api.ts` sobre `services/apiClient.ts`
- [X] T010 [US1] Crear el listado de plantilla en `frontend/src/features/players/PlayersPage.tsx` y enlazarlo desde `frontend/src/features/teams/TeamsPage.tsx` / `frontend/src/routes.tsx` en `/teams/:teamId/players` (depende de T009)
- [X] T011 [US1] Crear el formulario de alta en `frontend/src/features/players/CreatePlayerForm.tsx`, visible solo para organizador, mostrando el `error.message` del envelope en 409 y 400; ruta `/teams/:teamId/players/new` en `frontend/src/routes.tsx` (depende de T009)
- [X] T012 [P] [US1] Tests Vitest del listado y el formulario en `frontend/src/features/players/__tests__/players.test.tsx` (depende de T010, T011)

**Checkpoint**: User Story 1 funcional y testeable de forma independiente.

---

## Phase 3: Polish & Cross-Cutting Concerns

- [X] T013 [P] Ejecutar los 8 escenarios de `quickstart.md` de punta a punta contra el entorno local
- [X] T014 [P] Registrar las métricas de la HU en `docs/metricas/004-registrar-jugadores.md` desde `docs/metricas/_plantilla.md` (`AGENTS.md` §7) — sin inventar costo de IA ni tiempo real de trabajo
- [ ] T015 Verificar en el entorno desplegado que el alta de jugadores funciona con la sesión cross-domain (Vercel → Railway)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: depende de `specs/001-*`, `specs/002-*` y `specs/003-*` en `main`
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
desbloquea `specs/009-registrar-goles` y `specs/010-alineaciones-estadisticas`
(dependen de jugadores); conviene mezclarla antes de esas.

---

## Notes

- `[P]` = archivos distintos, sin dependencias pendientes
- Verificar que T003-T004 fallan antes de implementar
- `require_role`, el envelope de error y la paginación **ya existen** en
  `specs/001-*`: se reutilizan, no se reimplementan
- El módulo accede a equipos por el servicio de `backend/src/teams/`, nunca
  importando su modelo interno (Principio VIII)
- No hay endpoint público de baja en esta HU (igual que `003`): el borrado
  lógico se cubre en servicio/tests vía `status = inactive` (FR-005)
- T015 queda pendiente hasta el merge del PR (mismo patrón que 003)
