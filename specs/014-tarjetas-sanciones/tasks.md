# Tasks: Tarjetas y sanciones disciplinarias

**Input**: Design documents from `/specs/014-tarjetas-sanciones/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/cards-sanctions.openapi.yaml`, `quickstart.md`

**Tests**: obligatorios por Acceptance Scenarios, FR-001–FR-008 y Principios II
y IV de la constitución. Se escriben y se comprueba que fallen por
funcionalidad ausente antes de implementar.

**Organization**: tres historias (US1 registrar tarjetas P1, US2 suspensión P1,
US3 ficha pública P2). Setup / Foundational / Polish sin etiqueta de historia.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo (archivos distintos, sin dependencia
  incompleta del mismo grupo).
- **[US1]** / **[US2]** / **[US3]**: mapa a las historias de `spec.md`.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: confirmar que goles (009) y alineaciones (010) —base de eventos y
del puerto `jugadores_alineados`— están operativos antes de ampliar tipos.

- [X] T001 Ejecutar la regresión base con `backend/tests/integration/test_events.py` y `backend/tests/integration/test_lineups_statistics.py`, deteniendo la implementación si falla una prueba existente

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: ampliar el CHECK de tipos y dejar fixtures reproducibles. Sin el
CHECK nuevo, ningún insert de tarjeta pasa en PostgreSQL.

**⚠️ CRITICAL**: US1 no comienza hasta que la migración del CHECK aplique desde
base vacía y el modelo/schemas admitan los tipos nuevos.

- [X] T002 Ampliar en `backend/src/matches/models.py` el `CheckConstraint` `ck_match_events_type_supported` a `type IN ('GOAL', 'YELLOW_CARD', 'RED_CARD')` y documentar que 014 es la dueña de este cambio; no tocar columnas, FKs ni índices ajenos
- [X] T003 Ampliar en `backend/src/matches/schemas.py` el `EventType` / `CreateEventInput.type` a `Literal["GOAL", "YELLOW_CARD", "RED_CARD"]` (type requerido en create, alineado al contrato) y el enum de respuesta `MatchEvent.type`
- [X] T004 Generar la migración con `uv run alembic revision --autogenerate` en `backend/alembic/versions/` que **solo** reemplace el CHECK de tipos; fijar `down_revision` a la cabeza actual de `main` (hoy `919f3bd57721`, re-puntear tras merge de 013 según AGENTS.md); **borrar del diff** cualquier `op.drop_index`/`op.create_index` espurio sobre `ix_leagues_unique_name_season` e `ix_teams_unique_league_name`; verificar `alembic upgrade head` y `downgrade -1` sobre base vacía
- [X] T005 Añadir o extender fixtures en `backend/tests/conftest.py` para: partido `in_progress`/`finished` con jugadores en ambos equipos, partido con alineación registrada, partido sin alineación, partido `scheduled`/`cancelled`, y un segundo partido finalizado de la misma liga (para acumulación de amarillas entre partidos), reutilizando usuarios de prueba sin credenciales literales

**Checkpoint**: baseline en verde, CHECK ampliado, escenarios reproducibles.

---

## Phase 3: User Story 1 - Registrar tarjetas de un partido (Priority: P1) 🎯 MVP

**Goal**: que un operador registre `YELLOW_CARD` / `RED_CARD` como eventos del
partido, con las mismas validaciones de estado, equipo y alineación que los
goles, y que el listado público las muestre.

**Independent Test**: sobre un partido en curso, registrar una amarilla a un
jugador participante y verificar que queda en `GET /matches/{id}/events` con
`type: YELLOW_CARD` y `team_id` derivado.

### Tests for User Story 1 — write first, verify they fail

- [X] T006 [P] [US1] Crear o extender pruebas unitarias en `backend/tests/unit/test_card_rules.py` (o generalizar `test_goal_rules.py`): estados `finished`/`in_progress` aceptados y `scheduled`/`cancelled` rechazados; jugador ajeno → `player_not_in_match`; alineación presente que rechaza a quien no figura y ausente (`None`) que acepta; varias tarjetas del mismo jugador permitidas a nivel de regla de negocio
- [X] T007 [P] [US1] Crear pruebas de contrato en `backend/tests/contract/test_cards_sanctions_contract.py` conforme a `specs/014-tarjetas-sanciones/contracts/cards-sanctions.openapi.yaml` para el path `/matches/{matchId}/events`: enum `GOAL|YELLOW_CARD|RED_CARD` en input/output, `team_id` ausente del body, códigos `401`/`404`/`409` documentados; actualizar `backend/tests/contract/test_events_contract.py` si aún afirma enum solo `GOAL`
- [X] T008 [P] [US1] Crear pruebas de integración en `backend/tests/integration/test_cards_sanctions.py`: registrar amarilla y roja con operador/organizador (AS1–AS2) con `team_id` derivado; rechazo en `scheduled`/`cancelled` (AS3); rechazo fuera de alineación y aceptación sin alineación (AS4–AS5); rechazo jugador ajeno (AS6); varias tarjetas mismo partido (FR-005); `GET` público incluye tarjetas y `consistency` solo cuenta `GOAL`; goles existentes siguen pasando
- [X] T009 [P] [US1] Extender `frontend/src/features/events/__tests__/events.test.tsx` (o añadir `cards.test.tsx`): formulario de tarjeta visible solo para operador/organizador en partidos jugables; envío de amarilla/roja refresca la lista; mensaje legible ante `409 player_not_in_match` / `player_not_in_lineup` / `match_not_playable`

### Backend implementation for User Story 1

- [X] T010 [P] [US1] Generalizar o duplicar en `backend/src/matches/goal_rules.py` (p. ej. `event_rules.py` / `validar_registro_de_evento`) la validación compartida de estado, pertenencia y alineación para goles y tarjetas, manteniendo `calcular_consistencia` solo sobre `GOAL`
- [X] T011 [US1] Extender `backend/src/matches/service.py` para registrar eventos con `type` `YELLOW_CARD`/`RED_CARD` (método dedicado o generalización de `registrar_gol`), reutilizando `jugadores_alineados` y derivando `team_id` del jugador; `listar_eventos` ya devuelve todos los tipos
- [X] T012 [US1] Ajustar `backend/src/matches/router.py` para aceptar los tipos nuevos en `POST /matches/{partido_id}/events` con `requiere_rol("operador", "organizador")`, sin aceptar `team_id`/`created_by` del cliente

### Frontend implementation for User Story 1

- [X] T013 [P] [US1] Ampliar tipos y cliente en `frontend/src/features/events/api.ts` para `YELLOW_CARD` / `RED_CARD`
- [X] T014 [US1] Añadir UI de registro de tarjeta (selector de tipo amarilla/roja + jugador + minuto) en `frontend/src/features/events/` e integrarla en `frontend/src/features/matches/MatchDetailPage.tsx` solo para operador/organizador y partidos `finished`/`in_progress`; listar tarjetas junto a goles

### Story verification

- [X] T015 [US1] Ejecutar unit/contract/integration/UI de tarjetas (T006–T009) y corregir sin debilitar pruebas

**Checkpoint**: US1 extremo a extremo; goles de 009 no regresionan.

---

## Phase 4: User Story 2 - Derivar la suspensión (Priority: P1)

**Goal**: calcular `suspended` en lectura: 1 roja, o amarillas en ≥ 2 partidos
distintos; nunca persistir bandera.

**Independent Test**: registrar una roja → ficha con `suspended: true`; dos
amarillas en partidos distintos → `suspended: true`; una sola amarilla →
`false`; dos amarillas en el mismo partido → `false`.

### Tests for User Story 2 — write first, verify they fail

- [X] T016 [P] [US2] Crear pruebas unitarias en `backend/tests/unit/test_sanction_rules.py` para la función pura: sin tarjetas / una amarilla → no suspendido; dos amarillas mismo `match_id` → no suspendido; dos amarillas distintos `match_id` → suspendido; una roja → suspendido; conteos de amarillas/rojas correctos
- [X] T017 [P] [US2] Añadir casos de integración en `backend/tests/integration/test_cards_sanctions.py` que cubran AS1–AS4 de US2 vía `GET /players/{id}/discipline` tras registrar las tarjetas correspondientes

### Backend implementation for User Story 2

- [X] T018 [P] [US2] Crear `backend/src/sanctions/rules.py` con la función pura que, dada una lista de eventos de tarjeta (`type`, `match_id`), devuelve `yellow_cards`, `red_cards` y `suspended` según `data-model.md` / FR-007
- [X] T019 [US2] Crear `backend/src/sanctions/schemas.py` con `PlayerDiscipline` (`player_id`, `yellow_cards`, `red_cards`, `suspended`)
- [X] T020 [US2] Crear `backend/src/sanctions/service.py` que resuelve el jugador (`PlayerService`, 404 `player_not_found`), obtiene sus eventos de tarjeta vía interfaz pública de `MatchService` (sin importar el ORM de matches), y aplica `rules.py`
- [X] T021 [US2] Exponer un puerto en `backend/src/matches/service.py` (p. ej. listar eventos de tarjeta por `player_id`) si hace falta para que `sanctions` no importe modelos de `matches`

**Checkpoint**: la regla de suspensión está probada en unitario; integración
depende del endpoint de US3 (puede implementarse en el mismo PR en secuencia).

---

## Phase 5: User Story 3 - Consultar la ficha disciplinaria (Priority: P2)

**Goal**: cualquier visitante consulta `GET /players/{id}/discipline` sin
sesión y ve conteos + `suspended`.

**Independent Test**: sin cookie, abrir la ficha de un jugador con tarjetas y
ver amarillas/rojas y suspensión; jugador sin tarjetas → ceros sin error.

### Tests for User Story 3 — write first, verify they fail

- [X] T022 [P] [US3] Ampliar contrato en `backend/tests/contract/test_cards_sanctions_contract.py` para `GET /players/{playerId}/discipline`: `security: []`, schema `PlayerDiscipline`, `404 player_not_found`
- [X] T023 [P] [US3] Completar integración pública en `backend/tests/integration/test_cards_sanctions.py`: GET sin cookie 200; jugador sin tarjetas ceros; jugador inexistente 404; consistencia con US2
- [X] T024 [P] [US3] Crear pruebas UI en `frontend/src/features/sanctions/__tests__/discipline.test.tsx`: ficha visible sin sesión; muestra conteos y estado suspendido; estado vacío en cero

### Backend / frontend implementation for User Story 3

- [X] T025 [US3] Crear `backend/src/sanctions/router.py` con `GET /players/{player_id}/discipline` público y montarlo en `backend/src/main.py` con `include_router` (una línea)
- [X] T026 [P] [US3] Crear `frontend/src/features/sanctions/api.ts` y página `DisciplinePage` (o equivalente) que consuma el contrato
- [X] T027 [US3] Registrar la ruta pública en `frontend/src/routes.tsx` y enlazar desde la UI de jugador/partido donde corresponda sin exigir login

### Story verification

- [X] T028 [US3] Ejecutar pruebas de sanctions (T016–T017, T022–T024) y corregir sin debilitar

**Checkpoint**: US1+US2+US3 verificables; SC-002 (suspensión inmediata en el
siguiente GET) cubierto.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: seguridad, migración en paralelo, quickstart, CI, métricas.

- [X] T029 [P] Revisar que no haya SQL concatenado, que el POST no acepte `team_id`/`created_by` del cliente, que el GET de disciplina no exija cookie, y que los errores usen el envelope compartido en `backend/src/matches/` y `backend/src/sanctions/`
- [X] T030 Verificar migración: `alembic upgrade head` desde base vacía, `downgrade -1`, `alembic check` (solo falso positivo conocido de índices funcionales); al abrir PR, rebasear sobre `main` tras 013 y re-puntear `down_revision` (AGENTS.md orden `013 → 014 → 016 → 017`)
- [X] T031 Ejecutar los escenarios de `specs/014-tarjetas-sanciones/quickstart.md` y medir SC-001 (≤ 2 interacciones) con evidencia real, sin inventar tiempos
- [X] T032 Ejecutar suites y quality gates de `.github/workflows/ci.yml` (pytest, Ruff, Vitest, ESLint, build, auditorías); corregir regresiones sin debilitar pruebas
- [X] T033 Crear `docs/metricas/014-tarjetas-sanciones.md` desde `docs/metricas/_plantilla.md` llenando solo la sección del agente (tareas, tests, ciclos, reprocesos); dejar tiempo real y costo de IA para la persona

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (1)**: inmediato; valida 009/010.
- **Foundational (2)**: T002 → T003 → T004 → T005 (modelo/schemas antes de
  migración; fixtures después del CHECK).
- **US1 (3)**: depende de T005; T006–T009 fallan antes de T010–T014.
- **US2 (4)**: puede empezar tras Foundational en unitario (T016/T018); la
  integración necesita persistencia de tarjetas (US1) y el GET (US3).
- **US3 (5)**: depende de T020 (servicio sanctions); T022–T024 fallan antes de
  T025–T027.
- **Polish (6)**: depende de T015 + T028.

### User Story Dependencies

- **US1 (P1)**: MVP — registro + listado. No depende de sanctions.
- **US2 (P1)**: regla pura independiente; datos reales vienen de US1.
- **US3 (P2)**: expone US2 por HTTP/UI; lectura pública.

### Parallel Opportunities

- T006–T009 en paralelo; T013 en paralelo a T010–T012.
- T016 y T018 en paralelo a cierre de UI de US1 si el contrato de disciplina
  ya está claro.
- T022–T024 en paralelo; T026 en paralelo a T025.

---

## Parallel Example: User Story 1

```bash
# Tests en paralelo (deben fallar):
Task: T006 unit card rules
Task: T007 contract events/cards
Task: T008 integration cards
Task: T009 frontend events/cards tests

# Luego implementación backend → frontend → T015
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 + 2  
2. Phase 3 (US1)  
3. **STOP y validar** registro de tarjetas en ficha de partido  
4. Continuar US2 → US3 → Polish en el mismo PR

### `/speckit-implement`

Arrancar en T001 y seguir el orden de fases. No re-decidir stack (AGENTS.md §5).
Al final: métricas + PR con título `feat(014): registrar tarjetas y sanciones de jugadores`.

### Incremental Delivery

1. Setup + Foundational → CHECK listo  
2. US1 → demo de registro  
3. US2+US3 → ficha pública con suspensión  
4. Polish → CI verde y métricas

---

## Notes

- [P] = archivos distintos, sin dependencia incompleta del grupo.
- No inventar edición/borrado de tarjetas ni bloqueo de alineaciones (Out of Scope).
- Commit intermedios libres; el título del PR es el que queda en `main` (squash).
- Ninguna tarea está marcada hecha: listo para `/speckit-implement`.
