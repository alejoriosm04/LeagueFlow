# Tasks: Registrar alineaciones y consultar estadisticas de jugadores

**Input**: Design documents from `/specs/010-alineaciones-estadisticas/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/lineups-statistics.openapi.yaml`, `quickstart.md`

**Tests**: obligatorios por Acceptance Scenarios, FR-001..FR-011, SC-001 y el cierre de deuda heredada de `specs/009-registrar-goles`.

**Organization**: la spec contiene una unica historia (US1, prioridad P2). Todas las tareas de producto llevan `[US1]`; Setup, Foundational y cierre no llevan etiqueta.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo (archivos distintos, sin dependencia de tarea incompleta).
- **[US1]**: Registrar alineaciones y consultar estadisticas de jugadores.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: validar baseline de features dependientes (004, 005, 006, 009) antes de agregar alineaciones y estadisticas derivadas.

- [ ] T001 Ejecutar regresion base de dependencias en `backend/tests/integration/test_players.py`, `backend/tests/integration/test_matches.py`, `backend/tests/integration/test_results.py` y `backend/tests/integration/test_events.py`, deteniendo la implementacion si falla una prueba existente
  - **Bloqueado en este entorno**: no hay PostgreSQL disponible en el sandbox de ejecucion (sin `docker`/`psql`); todo intento de `pytest` -incluidos tests preexistentes sin relacion con esta HU- falla con `ConnectionRefusedError` en el fixture `base_limpia`. No es una regresion introducida por esta HU. Pendiente de ejecutar en CI o localmente con Postgres antes de mergear.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: crear infraestructura compartida que bloquea toda la historia: persistencia de alineaciones, schemas y fixtures reproducibles.

**⚠️ CRITICAL**: ninguna tarea de US1 inicia hasta completar esta fase.

- [X] T002 Definir el modelo `MatchLineup` en `backend/src/matches/models.py` con FKs `RESTRICT`, `uq_match_lineups_match_player`, indices `ix_match_lineups_match_team` y `ix_match_lineups_player`, sin alterar entidades base de specs previas
- [ ] T003 Crear migracion en `backend/alembic/versions/` para `match_lineups` y validar `upgrade head` + `downgrade -1`; eliminar del diff autogenerado cualquier recreacion espuria de `ix_leagues_unique_name_season` o `ix_teams_unique_league_name`
  - Migracion `f3a4b5c6d7e8_crear_tabla_match_lineups.py` escrita a mano (mismo patron que `020b6dc9a54e`), compila y encadena correctamente sobre el head existente. **No pudo ejecutarse `alembic upgrade head`/`downgrade -1` real**: sin Postgres en el sandbox (ver nota de T001).
- [X] T004 [P] Añadir schemas de alineacion en `backend/src/matches/schemas.py` (`UpsertLineupInput`, `LineupPlayer`, `MatchLineupView`) con `status` `registered|missing` segun contrato
- [X] T005 [P] Añadir schemas de estadisticas en `backend/src/statistics/schemas.py` (`PlayerStatistics`, `TopScorerRow`, `TopScorers`) con campos y tipos del contrato
- [X] T006 Ampliar fixtures de prueba en `backend/tests/conftest.py` con partido finalizado sin alineacion, partido con eventos GOAL, jugador de tercer equipo y usuarios por rol para escenarios de FR-002/FR-003/FR-004/FR-011
  - La fixture `partido_con_plantillas` (de la 009) ya cubre los cuatro casos sin modificacion: partido finalizado sin alineacion por defecto, endpoint de eventos disponible para GOAL, `foreign_player_id` de un tercer equipo y `cliente_operador`/`cliente_organizador` para los dos roles. No se duplico (Principio IV).

**Checkpoint**: persistencia y estructuras compartidas listas; escenarios reproducibles.

---

## Phase 3: User Story 1 - Registrar alineaciones y consultar estadisticas de jugadores (Priority: P2) 🎯 MVP

**Goal**: permitir registrar/corregir alineaciones protegidas por rol y exponer estadisticas derivadas publicas (goles y partidos jugados) con tabla de goleadores ordenada.

**Independent Test**: registrar alineacion de dos partidos finalizados, registrar goles de un jugador, consultar su ficha y la tabla de goleadores sin sesion, y verificar conteos/orden; validar rechazo de jugador fuera de partido y rechazo por incoherencia con eventos.

### Tests for User Story 1 — write first, verify they fail

- [X] T007 [P] [US1] Crear pruebas unitarias de reglas de alineacion en `backend/tests/unit/test_lineup_rules.py` para pertenencia a equipos del partido, deteccion de conflicto con eventos y estado `missing` vs `registered`
  - Escritas. **No pudieron ejecutarse** en este sandbox: `tests/conftest.py` tiene un fixture `autouse` (`base_limpia`) que exige Postgres incluso para tests unitarios puros (ver nota de T001); revisadas manualmente linea por linea.
- [X] T008 [P] [US1] Crear pruebas de contrato en `backend/tests/contract/test_lineups_statistics_contract.py` para `PUT/GET /matches/{id}/lineup`, `GET /leagues/{id}/top-scorers` y `GET /players/{id}/statistics`, incluyendo `security: []` en GET publicos y errores `401/403/404/409`
  - Escritas; los tests que solo parsean el YAML se verificaron leyendo el contrato manualmente. Los tests contra la app viva no pudieron ejecutarse (sin Postgres).
- [X] T009 [P] [US1] Crear pruebas de integracion en `backend/tests/integration/test_lineups_statistics.py` cubriendo AS1..AS8, edge case de partido finalizado sin alineacion y recalculo tras baja de evento GOAL
  - Escritas; no pudieron ejecutarse (sin Postgres).
- [X] T010 [P] [US1] Crear pruebas UI en `frontend/src/features/statistics/__tests__/statistics.test.tsx` para visibilidad publica, tabla ordenada por goles DESC, indicador de maximo goleador e interfaz de ficha individual con ceros cuando corresponde
  - Escritas y ejecutadas: 8/8 en verde (`npx vitest run`).

### Backend implementation for User Story 1

- [X] T011 [P] [US1] Implementar reglas puras de dominio en `backend/src/matches/lineup_rules.py` para validar FR-002 y FR-003
  - `conflicting_player_ids` como campo estructurado del envelope de error no se implemento: el contrato `lineups-statistics.openapi.yaml` solo declara `ErrorEnvelope {code,message,field}` (el mismo envelope global de `contracts/conventions.md`) para el 409, sin ese campo. Se listan los ids en `message` para no romper el envelope de error compartido por todo el proyecto; ver docstring de `detectar_conflicto_con_eventos`.
- [X] T012 [US1] Implementar en `backend/src/matches/service.py` `guardar_alineacion(match_id, payload, actor_id)` con reemplazo completo idempotente, validacion de pertenencia de jugadores y rechazo `lineup_conflicts_with_events`
- [X] T013 [US1] Implementar en `backend/src/matches/service.py` `obtener_alineacion(match_id)` devolviendo estado `registered|missing` y listas de jugadores por equipo
- [X] T014 [US1] Reemplazar el stub `jugadores_alineados` en `backend/src/matches/service.py` por consulta real a `match_lineups` para cerrar FR-003 heredado de `specs/009`
- [X] T015 [US1] Exponer `PUT /matches/{matchId}/lineup` (protegido con `requiere_rol("operador", "organizador")`) y `GET /matches/{matchId}/lineup` (publico) en `backend/src/matches/router.py`
- [X] T016 [US1] Implementar en `backend/src/statistics/service.py` `obtener_ficha_jugador(player_id)` derivando `goals` desde `match_events` y `matches_played` desde `match_lineups` en partidos `finished`
- [X] T017 [US1] Implementar en `backend/src/statistics/service.py` `tabla_goleadores(league_id)` con orden `goals DESC, player_name ASC, player_id ASC`, `rank` e `is_top_scorer`
  - Solo incluye jugadores con >=1 gol (interpretacion de "tabla de goleadores"; ver nota en el propio metodo y CHK015/CHK024 del checklist).
- [X] T018 [US1] Exponer endpoints publicos `GET /players/{playerId}/statistics` y `GET /leagues/{leagueId}/top-scorers` en `backend/src/statistics/router.py` y registrar rutas en `backend/src/main.py`
  - Ya vivian en el mismo router registrado en `main.py`; no hizo falta tocar `main.py`.

### Frontend implementation for User Story 1

- [X] T019 [P] [US1] Implementar cliente HTTP y tipos de estadisticas en `frontend/src/features/statistics/api.ts` conforme a `contracts/lineups-statistics.openapi.yaml`
- [X] T020 [P] [US1] Implementar cliente HTTP y tipos de alineacion en `frontend/src/features/matches/api.ts` para `PUT/GET /matches/{id}/lineup` con manejo de errores de contrato
- [X] T021 [US1] Extender `frontend/src/features/matches/MatchDetailPage.tsx` para mostrar estado de alineacion `registered|missing` y permitir edicion solo a operador/organizador
  - Se añadio `LineupForm.tsx` (mismo patron que `ResultForm`/`GoalForm`) para la edicion.
- [X] T022 [US1] Implementar `frontend/src/features/statistics/TopScorersPage.tsx` resaltando visualmente el/los `is_top_scorer=true` para cumplir SC-002
- [X] T023 [US1] Implementar `frontend/src/features/statistics/PlayerStatsPage.tsx` y registrar rutas publicas en `frontend/src/routes.tsx`

### Story verification

- [ ] T024 [US1] Ejecutar `backend/tests/unit/test_lineup_rules.py`, `backend/tests/contract/test_lineups_statistics_contract.py`, `backend/tests/integration/test_lineups_statistics.py` y `frontend/src/features/statistics/__tests__/statistics.test.tsx`, corrigiendo sin debilitar pruebas
  - Frontend: 8/8 en verde. Backend: no ejecutable en este sandbox (sin Postgres); pendiente antes de mergear.

**Checkpoint**: US1 completamente funcional e independientemente verificable.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: cierre de seguridad, consistencia de derivacion y evidencia de calidad.

- [X] T025 [P] Revisar en `backend/src/matches/router.py`, `backend/src/statistics/router.py` y `backend/src/core/errors.py` que escrituras exijan rol, lecturas sean anonimas y no se filtren stack traces ni campos sensibles
  - `PUT /matches/{id}/lineup` exige `requiere_rol("operador","organizador")`; `GET` de lineup y ambos endpoints de estadisticas no tienen dependencia de rol (publicos). `errors.py` no se toco: sigue sin exponer stack traces. `PlayerStatistics`/`TopScorerRow` no incluyen campos sensibles.
- [ ] T026 [P] Ejecutar validacion de migraciones en `backend/`: `alembic upgrade head`, `alembic downgrade -1`, `alembic upgrade head` y `alembic check`, verificando que no haya cambios de esquema fuera de `match_lineups`
  - Bloqueado: sin Postgres en el sandbox (ver T001/T003).
- [ ] T027 Ejecutar escenarios de `specs/010-alineaciones-estadisticas/quickstart.md`, documentar evidencia de SC-001 (coincidencia 100% conteo manual vs API) y SC-002 (identificacion inmediata del maximo goleador)
  - Bloqueado: requiere backend corriendo contra Postgres real; no disponible en el sandbox.
- [ ] T028 Ejecutar quality gates completos de CI (pytest, Ruff, Vitest, ESLint, build, auditorias) y corregir regresiones sin modificar requisitos
  - Parcial: `ruff check`/`ruff format --check` (backend) y `npm run lint`/`npx vitest run`/`npm run build` (frontend) en verde. `pytest`, `pip-audit` y `npm audit` no se ejecutaron (sin Postgres / fuera de alcance de este pase).
- [X] T029 Crear `docs/metricas/010-alineaciones-estadisticas.md` desde `docs/metricas/_plantilla.md` y completar solo datos reales de tareas/tests/ciclos/reprocesos

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: inicia de inmediato.
- **Foundational (Phase 2)**: depende de T001.
- **US1 (Phase 3)**: depende de T002..T006; pruebas T007..T010 deben existir antes de implementar T011..T023.
- **Polish (Phase 4)**: depende de T024.

### User Story Dependencies

- **US1 (P2)**: unica historia de la feature; depende de specs previas 004/005/006/009 ya operativas.

### Within User Story 1

```text
T007-T010 (pruebas rojas)
      ↓
T011 + T012 + T013 + T014
      ↓
T015
      ↓
T016 + T017
      ↓
T018
      ↓
T019 + T020 + T021 + T022 + T023
      ↓
T024
```

### Parallel Opportunities

- T004 y T005 en paralelo (schemas de modulos distintos).
- T007, T008, T009 y T010 en paralelo (suites separadas).
- T011 y T019/T020 en paralelo (reglas backend vs clientes frontend).
- T016 y T017 en paralelo tras resolver alineaciones en Match.
- T025 y T026 en paralelo durante cierre.

## Parallel Example: User Story 1

```text
Task: "T007 [US1] Reglas unitarias en backend/tests/unit/test_lineup_rules.py"
Task: "T008 [US1] Contrato en backend/tests/contract/test_lineups_statistics_contract.py"
Task: "T009 [US1] Integracion en backend/tests/integration/test_lineups_statistics.py"
Task: "T010 [US1] UI en frontend/src/features/statistics/__tests__/statistics.test.tsx"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1 y Phase 2.
2. Escribir y validar pruebas rojas T007..T010.
3. Implementar backend T011..T018.
4. Implementar frontend T019..T023.
5. Ejecutar T024 y validar historia en forma independiente.

### Incremental Delivery

1. Alineaciones protegidas y visibles en ficha de partido.
2. Estadisticas individuales derivadas y publicas.
3. Tabla de goleadores publica con maximo goleador destacado.
4. Cierre de calidad, seguridad y metricas.

### Parallel Team Strategy

- Persona A: backend + pruebas unit/contrato/integracion (T007..T018).
- Persona B: frontend + pruebas UI (T010, T019..T023).
- Convergencia en T024 y cierre T025..T029.

## Notes

- Las estadisticas de jugador se derivan siempre en lectura de `match_events` y `match_lineups`; no se crea tabla de acumulados.
- El caso borde de partido finalizado sin alineacion se representa explicitamente como `status: missing`.
- La deuda de FR-003 de `specs/009` se cierra implementando `jugadores_alineados` real y su prueba de integracion en esta HU.
