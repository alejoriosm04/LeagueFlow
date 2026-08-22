# Tasks: Divisiones (grupos) dentro de una liga

**Input**: Design documents from `/specs/013-grupos-divisiones/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/groups.openapi.yaml`, `quickstart.md`

**Tests**: Incluidas (la constitución exige prueba para toda regla de negocio; Principio II).

**Organization**: Tareas agrupadas por historia de usuario (US1, US2, US3) para implementar y probar cada una de forma independiente.

## Format: `[ID] [P?] [Story] Descripción`

- **[P]**: puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: a qué historia pertenece (US1, US2, US3)
- Incluye rutas exactas de archivo

## Phase 1: Setup

**Purpose**: Estructura inicial del módulo nuevo.

- [ ] T001 Crear el módulo `backend/src/groups/` con `__init__.py` vacío

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Modelos, migración y schemas compartidos por las tres historias.

**⚠️ CRITICAL**: Ninguna historia puede empezar antes de esta fase.

- [ ] T002 Crear los modelos `LeagueGroup` (tabla `groups`) y `GroupTeamMembership` (tabla `group_memberships`) en `backend/src/groups/models.py`, con FKs, `ON DELETE` e índices únicos según `data-model.md` (`ix_groups_unique_league_name`, `uq_group_memberships_team`, `ix_group_memberships_group`)
- [ ] T003 Generar la migración Alembic para `groups` + `group_memberships` en `backend/alembic/versions/` y revisar el diff para NO recrear los índices funcionales de `leagues`/`teams` (AGENTS.md, sección de índices funcionales)
- [ ] T004 [P] Crear los schemas Pydantic en `backend/src/groups/schemas.py`: `CreateGroupRequest`, `RenameGroupRequest`, `AssignTeamRequest`, `Group`, `TeamInGroup`, `GroupWithTeams`, `GroupList`

**Checkpoint**: modelos + migración + schemas listos; las historias ya pueden implementarse en paralelo.

---

## Phase 3: User Story 1 - Crear y gestionar los grupos de una liga (Priority: P1) 🎯 MVP

**Goal**: El organizador crea, renombra y elimina grupos; cada operación valida la unicidad del nombre por liga.

**Independent Test**: crear dos grupos, renombrar uno y eliminar el otro, verificando por las respuestas (`201`, `200`, `204`) y un reintento que devuelva `404`.

### Tests for User Story 1

- [ ] T005 [US1] Test de contrato para `POST /leagues/{leagueId}/groups`, `PATCH /groups/{groupId}` y `DELETE /groups/{groupId}` en `backend/tests/contract/test_groups_contract.py` (códigos 201/200/204/400/401/403/404/409)
- [ ] T006 [US1] Test de integración de crear/renombrar/eliminar grupo (incl. nombre duplicado normalizado) en `backend/tests/integration/test_groups.py`

### Implementation for User Story 1

- [ ] T007 [US1] Implementar `crear_grupo`, `renombrar_grupo` y `eliminar_grupo` en `backend/src/groups/service.py` (unicidad por liga vía `LeagueService.obtener_liga`, errores `league_not_found`/`group_not_found`/`group_name_duplicate`)
- [ ] T008 [US1] Implementar `POST /leagues/{leagueId}/groups`, `PATCH /groups/{groupId}` y `DELETE /groups/{groupId}` en `backend/src/groups/router.py` con `Depends(requiere_rol("organizador"))`
- [ ] T009 [US1] Registrar el router de groups en `backend/src/main.py` (`include_router`)
- [ ] T010 [P] [US1] Frontend: `api.ts` (createGroup, renameGroup, deleteGroup) y `GroupForm.tsx` (crear/renombrar, solo organizador) en `frontend/src/features/groups/`

**Checkpoint**: US1 funcional y testeable por sí sola (crear/renombrar/eliminar grupo).

---

## Phase 4: User Story 2 - Asignar equipos a un grupo (Priority: P1)

**Goal**: El organizador asigna/desasigna equipos; un equipo pertenece a lo sumo a un grupo por liga.

**Independent Test**: asignar un equipo a un grupo y verificar que aparece; desasignarlo y verificar que deja de aparecer.

### Tests for User Story 2

- [ ] T011 [US2] Test de contrato para `POST /groups/{groupId}/teams` y `DELETE /groups/{groupId}/teams` en `backend/tests/contract/test_groups_contract.py` (201/204/401/403/404/409)
- [ ] T012 [US2] Test de integración de asignar/desasignar y los rechazos (`team_not_found_in_league`, `team_already_in_group`, `team_inactive`) en `backend/tests/integration/test_groups.py`

### Implementation for User Story 2

- [ ] T013 [US2] Implementar `asignar_equipo` y `desasignar_equipo` en `backend/src/groups/service.py` (validaciones FR-005/006/007/008/011 usando `TeamService.obtener_equipo`)
- [ ] T014 [US2] Implementar `POST /groups/{groupId}/teams` y `DELETE /groups/{groupId}/teams` en `backend/src/groups/router.py` con `requiere_rol("organizador")`
- [ ] T015 [P] [US2] Frontend: extender `api.ts` (assignTeam, unassignTeam) y añadir el control de asignar/desasignar en `frontend/src/features/groups/`

**Checkpoint**: US1 y US2 funcionales e independientes (asignar/desasignar equipo).

---

## Phase 5: User Story 3 - Consultar la composición de los grupos (Priority: P2)

**Goal**: Cualquiera, sin sesión, consulta los grupos de una liga con su composición (incluye equipos inactivos que ya son miembros).

**Independent Test**: abrir la vista de grupos y verificar cada grupo con su lista de equipos.

### Tests for User Story 3

- [ ] T016 [US3] Test de contrato para `GET /leagues/{leagueId}/groups` en `backend/tests/contract/test_groups_contract.py` (200 público, 404)
- [ ] T017 [US3] Test de integración de listar la composición (incl. equipo inactivo miembro y liga sin grupos → lista vacía) en `backend/tests/integration/test_groups.py`

### Implementation for User Story 3

- [ ] T018 [US3] Implementar `listar_grupos` (con composición por grupo, incl. inactivos miembros) en `backend/src/groups/service.py`
- [ ] T019 [US3] Implementar `GET /leagues/{leagueId}/groups` público en `backend/src/groups/router.py`
- [ ] T020 [P] [US3] Frontend: `GroupsPage.tsx` (listado público con composición), `api.ts` (listGroups) y su test en `frontend/src/features/groups/__tests__/`

**Checkpoint**: Las tres historias funcionales de forma independiente.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Cierre y validación transversal.

- [ ] T021 [P] Test de frontend para `GroupForm.tsx` en `frontend/src/features/groups/__tests__/`
- [ ] T022 Ejecutar los escenarios de `quickstart.md` (12) y la suite completa en verde (`pytest tests/contract/test_groups_contract.py tests/integration/test_groups.py` y `npx vitest run src/features/groups`)
- [ ] T023 Registrar las métricas de la HU en `docs/metricas/013-grupos-divisiones.md` (AGENTS.md §7, antes del PR)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias.
- **Foundational (Phase 2)**: depende de Setup; BLOQUEA las tres historias.
- **Historias (Phase 3-5)**: dependen de Foundational; luego son independientes entre sí (US1 → US2 → US3 en orden de prioridad, o en paralelo si hay capacidad).
- **Polish (Phase 6)**: depende de las historias deseadas.

### User Story Dependencies

- **US1 (P1)**: tras Foundational. Sin dependencias de otras historias.
- **US2 (P1)**: tras Foundational. Reutiliza el módulo creado en US1, pero es testeable por sí sola (asignar/desasignar).
- **US3 (P2)**: tras Foundational. Reutiliza `listar_grupos` y el listado de US1.

### Within Each User Story

- Tests primero (deben fallar antes de implementar), luego service, luego router, luego frontend.
- Service antes que router; router antes que el registro en `main.py`.

### Parallel Opportunities

- T004 (schemas) puede ir en paralelo con T002/T003.
- T010, T015, T020, T021 tocan archivos frontend distintos y pueden ir en paralelo entre sí.
- Una vez terminada Foundational, las tres historias podrían repartirse entre integrantes.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 + Phase 2 (Setup + Foundational).
2. Phase 3: US1 (crear/renombrar/eliminar grupo).
3. **STOP y VALIDAR**: US1 independiente.
4. Desplegar/demostrar si está listo.

### Incremental Delivery

1. Foundational → US1 → validar (MVP).
2. + US2 (asignar/desasignar) → validar.
3. + US3 (composición pública) → validar.
4. Cada historia suma valor sin romper las anteriores.

### Parallel Team Strategy

- Una persona hace Foundational; luego US1, US2 y US3 se reparten.

---

## Notes

- Los tests de contrato e integración de las tres historias viven en los MISMOS archivos (`test_groups_contract.py`, `test_groups.py`): añadir por historia, no duplicar.
- Respetar los códigos de error de `data-model.md` (`group_name_duplicate`, `team_not_found_in_league`, `team_already_in_group`, `team_inactive`).
- No importar modelos de `teams`/`leagues`: usar sus servicios (Principio VIII).
- Commitear tras cada tarea o grupo lógico.
