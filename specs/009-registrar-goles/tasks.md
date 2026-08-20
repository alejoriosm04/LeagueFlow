# Tasks: Registrar goles por jugador

**Input**: Design documents from `/specs/009-registrar-goles/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/events.openapi.yaml`, `quickstart.md`

**Tests**: obligatorios por los cinco Acceptance Scenarios, FR-001–FR-006 y los
Principios II y IV de la constitución. Se escriben y se comprueba que fallen
por la funcionalidad ausente antes de implementar. FR-003 se prueba con un
doble del puerto de alineación; su prueba de integración corresponde a 010
(desviación registrada en `plan.md`).

**Organization**: la spec contiene una única historia P2. Todas las tareas de
producto llevan `[US1]`; Setup, Foundational y cierre no llevan etiqueta.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo porque trabaja en archivos distintos y
  no depende de una tarea incompleta del mismo grupo.
- **[US1]**: Registrar goles por jugador.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: confirmar que los partidos (005), los resultados (006) y las
plantillas (004) —de donde salen partido, marcador y jugador— están operativos
antes de colgarles eventos.

- [X] T001 Ejecutar la regresión base con `backend/tests/integration/test_matches.py`, `backend/tests/integration/test_results.py`, `backend/tests/integration/test_result_corrections.py` y `backend/tests/integration/test_players.py`, deteniendo la implementación si falla una prueba existente

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: crear la tabla nueva y los datos reproducibles. Sin el modelo, la
fixture `base_limpia` de `conftest.py` no puede siquiera crear el esquema, así
que ninguna prueba de US1 arranca.

**⚠️ CRITICAL**: US1 no comienza hasta que `match_events` exista y la migración
se aplique desde una base vacía.

- [X] T002 Definir el modelo `MatchEvent` en `backend/src/matches/models.py` con FKs `RESTRICT` a `matches`, `players`, `teams` y `users`, los CHECK `ck_match_events_minute_nonnegative` y `ck_match_events_type_supported`, y el índice `ix_match_events_match_minute`, sin tocar `Match` ni `ResultCorrectionRequest`
- [X] T003 Generar la migración con `uv run alembic revision --autogenerate` en `backend/alembic/versions/`, fijar `down_revision = "d6e7f8a9b0c1"`, **borrar del diff los `op.drop_index`/`op.create_index` espurios** sobre `ix_leagues_unique_name_season` e `ix_teams_unique_league_name` (AGENTS.md), y verificar `alembic upgrade head` y `downgrade -1` sobre una base vacía
- [X] T004 Añadir a `backend/tests/conftest.py` fixtures de partido finalizado con marcador y jugadores en ambos equipos, jugador de un equipo ajeno al partido, partido `scheduled` y partido `cancelled` de la misma liga, reutilizando los usuarios de prueba existentes sin credenciales literales

**Checkpoint**: baseline en verde, tabla creada y escenarios reproducibles.

---

## Phase 3: User Story 1 - Registrar goles por jugador (Priority: P2) 🎯 MVP

**Goal**: que un operador registre goles atribuidos a jugadores concretos de un
partido con marcador, que el sistema rechace atribuciones imposibles y que
cualquiera pueda consultar los eventos junto a la advertencia de descuadre, sin
que el marcador oficial ni la clasificación cambien nunca.

**Independent Test**: sobre un partido finalizado 3-1, registrar dos goles
atribuidos a jugadores concretos y verificar que quedan listados como eventos
del partido; intentar un gol de un jugador ajeno y verificar el rechazo;
comprobar que la clasificación de la liga no se movió.

### Tests for User Story 1 — write first, verify they fail

- [X] T005 [P] [US1] Crear pruebas unitarias de las funciones puras en `backend/tests/unit/test_goal_rules.py`: jugador de equipo local y de visitante aceptados, jugador ajeno rechazado (AS2, FR-002), alineación ausente (`None`) que acepta y alineación presente que rechaza a quien no figura usando un doble del puerto (AS3, FR-003), estados `finished`/`in_progress` aceptados y `scheduled`/`cancelled` rechazados, y el cálculo de consistencia con marcador que cuadra, que no cuadra y ausente (`matches_official` `true`/`false`/`null`, FR-005)
- [X] T006 [P] [US1] Crear pruebas de contrato en `backend/tests/contract/test_events_contract.py` conforme a `specs/009-registrar-goles/contracts/events.openapi.yaml`: verbos declarados, `GET` con `security: []`, forma `{items, consistency}`, propiedades requeridas de `MatchEvent` y `EventConsistency`, `team_id` ausente del `CreateEventInput`, y los códigos `401 not_authenticated` para el anónimo, `404 match_not_found` y `409` con envelope compartido. **No** intentes ejercitar el `403 insufficient_role`: el endpoint acepta los dos únicos roles que existen, así que ningún usuario autenticado puede recibirlo; el contrato lo declara como forma genérica, igual que hace 006 en `PUT /result`. Afirma en su lugar que operador y organizador son aceptados
- [X] T007 [P] [US1] Crear pruebas de integración extremo a extremo en `backend/tests/integration/test_events.py`: registro con operador y con organizador (AS1) incluida la derivación de `team_id` desde el jugador, rechazo del jugador ajeno (AS2, SC-002), rechazo en partido `scheduled` y `cancelled`, `minute` negativo rechazado, `type` no soportado (`"RED_CARD"`) rechazado con `400 validation_error` (FR-004), `201` pese al descuadre y `consistency.matches_official=false` (AS4), listado público en orden de minuto ascendente, partido sin eventos con `items` vacío y bloque presente, `404` de partido inexistente, y que registrar goles **no altera el marcador oficial** del partido (`home_score`/`away_score` idénticos antes y después, comprobado por `GET /matches/{id}`). No consultes `GET /leagues/{id}/standings`: ese endpoint es de `specs/008-consultar-clasificacion`, que no está mezclada en `main` y por tanto no existe en esta rama. Si 008 se mezcla antes de cerrar esta HU, añade además la aserción sobre la clasificación
- [X] T008 [P] [US1] Crear pruebas de UI en `frontend/src/features/events/__tests__/events.test.tsx`: lista de goles con jugador y minuto visible sin sesión, formulario ausente para visitante y para espectador y presente para operador/organizador (AS5), envío que refresca la lista, advertencia visible cuando `matches_official` es `false` y ausente cuando es `true` o `null`, y mensaje de error legible ante `409 player_not_in_match`

### Backend implementation for User Story 1

- [X] T009 [P] [US1] Añadir a `backend/src/matches/schemas.py` los schemas `CreateEventInput` (solo `player_id`, `minute >= 0` y `type` con default `GOAL`), `MatchEvent`, `EventConsistency` y `MatchEvents`, con el orden de campos del contrato
- [X] T010 [P] [US1] Implementar en `backend/src/matches/goal_rules.py` las funciones puras `validar_registro_de_gol(...)` —estado del partido, pertenencia al partido (FR-002) y alineación recibida como parámetro (FR-003)— y `calcular_consistencia(...)` (FR-005), sin sesión de base de datos y devolviendo `ErrorDeNegocio` con los `code` del contrato
- [X] T011 [US1] Añadir a `backend/src/matches/service.py` el puerto `jugadores_alineados(match_id) -> set[UUID] | None`, documentado como que devuelve siempre `None` hasta que `specs/010-alineaciones-estadisticas` lo implemente, y `registrar_gol(...)` que obtiene el partido, resuelve el jugador vía `PlayerService.obtener_jugador`, deriva `team_id` de su plantilla, delega la validación en `goal_rules` y persiste
- [X] T012 [US1] Añadir a `backend/src/matches/service.py` `listar_eventos(match_id)` que devuelve los eventos en orden `minute ASC, created_at ASC` junto a la consistencia calculada por `goal_rules`, propagando `404 match_not_found`
- [X] T013 [US1] Exponer en `backend/src/matches/router.py` `POST /matches/{partido_id}/events` con `requiere_rol("operador", "organizador")` y `created_by` derivado de la sesión (FR-006), y `GET /matches/{partido_id}/events` público, ambos conforme al contrato

### Frontend implementation for User Story 1

- [X] T014 [P] [US1] Crear tipos `MatchEvent`, `EventConsistency`, `MatchEvents` y el cliente `eventsApi.listar`/`eventsApi.registrar` derivados del contrato en `frontend/src/features/events/api.ts`
- [X] T015 [US1] Implementar `frontend/src/features/events/GoalForm.tsx` con selector de jugador de ambos equipos, campo de minuto, envío, estados de carga y traducción de los `error.code` del contrato a mensajes en español
- [X] T016 [US1] Integrar en `frontend/src/features/matches/MatchDetailPage.tsx` la sección de goles: lista pública con jugador y minuto, la advertencia de descuadre cuando `matches_official` es `false`, y el `GoalForm` solo para operador u organizador y solo si el partido está `finished` o `in_progress`, refrescando con el `cargar()` existente

### Story verification

- [X] T017 [US1] Ejecutar `backend/tests/unit/test_goal_rules.py`, `backend/tests/contract/test_events_contract.py`, `backend/tests/integration/test_events.py` y `frontend/src/features/events/__tests__/events.test.tsx`, corrigiendo la implementación sin borrar, saltar ni debilitar pruebas

**Checkpoint**: AS1, AS2, AS4 y AS5 funcionan extremo a extremo; AS3 queda
cubierto por prueba unitaria, según la desviación aprobada en `plan.md`.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: seguridad, integridad del esquema, guía reproducible, compuertas y
métricas.

- [X] T018 [P] Revisar que las consultas usen exclusivamente SQLAlchemy parametrizado, que un `matchId` inválido produzca `400 validation_error`, que el `GET` no exija cookie, que el `POST` no acepte `team_id` ni `created_by` del cliente y que ningún mensaje exponga stack traces, en `backend/src/matches/service.py`, `backend/src/matches/router.py` y `backend/src/core/errors.py`
- [X] T019 Verificar la migración de forma independiente: `alembic upgrade head` desde una base vacía, `downgrade -1`, y `alembic check` comprobando que **solo** reporta el falso positivo conocido de `ix_leagues_unique_name_season` e `ix_teams_unique_league_name`, sin diferencias sobre `match_events`
- [X] T020 Ejecutar los diez escenarios de `specs/009-registrar-goles/quickstart.md`, medir SC-001 cronometrando el registro de los cuatro goles de un partido 3-1 y registrar la evidencia observada sin inventar tiempos
- [X] T021 Ejecutar suites completas y quality gates de `.github/workflows/ci.yml`: pytest, Ruff check/format, Vitest, ESLint, build, `pip-audit` y `npm audit`; corregir regresiones sin modificar requisitos ni debilitar pruebas
- [X] T022 Crear `docs/metricas/009-registrar-goles.md` desde `docs/metricas/_plantilla.md` y llenar únicamente tareas, tests, ciclos y reprocesos reales, dejando tiempo real y costo de IA para la persona
- [X] T023 Anotar en `specs/010-alineaciones-estadisticas/spec.md` el compromiso heredado: su plan DEBE implementar el puerto `jugadores_alineados` y añadir la prueba de integración del Acceptance Scenario 3 de esta spec

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: inicia de inmediato y valida 004, 005 y 006.
- **Foundational (Phase 2)**: depende de T001. T002 → T003 → T004 en orden: la
  migración se autogenera desde el modelo y las fixtures necesitan la tabla.
- **US1 (Phase 3)**: depende de T004; T005–T008 deben fallar por funcionalidad
  ausente antes de T009–T016.
- **Polish (Phase 4)**: depende de T017; T018 y T019 pueden correr en paralelo,
  luego T020 → T021 → T022 → T023.

### User Story Dependencies

- **US1 (P2)**: única historia. Depende de las specs 004, 005 y 006 ya
  mezcladas, no de otra historia de esta feature. **No** depende de 008.

### Within User Story 1

```text
T005–T008 (pruebas rojas)
       ↓
T009  T010
   \   /
    T011 → T012 → T013
T014 → T015 → T016
                    ↓
                   T017
```

- T005–T008 trabajan en cuatro suites distintas y son paralelizables.
- T009 y T010 tocan archivos distintos y no dependen entre sí.
- T011 necesita schemas y reglas; T012 reutiliza la consistencia de T010; T013
  cierra el cableado HTTP.
- T014 deriva del contrato y no espera al backend; T015 y T016 comparten la
  ficha de partido y van en orden.

### Parallel Opportunities

- T005–T008: unitarias, contrato, integración y UI en archivos independientes.
- T009 y T010: schemas y funciones puras en paralelo.
- T014 puede empezar en cuanto exista el contrato.
- T018 y T019 son revisiones independientes durante el cierre.

## Parallel Example: User Story 1

```text
Task: "T005 reglas de gol y consistencia en backend/tests/unit/test_goal_rules.py"
Task: "T006 contrato y códigos de error en backend/tests/contract/test_events_contract.py"
Task: "T007 registro, rechazos y no-efecto en la clasificación en backend/tests/integration/test_events.py"
Task: "T008 lista pública, formulario por rol y advertencia en frontend/src/features/events/__tests__/events.test.tsx"
```

## Implementation Strategy

### MVP First (US1)

1. Completar T001–T004: baseline, tabla y fixtures.
2. Escribir T005–T008 y comprobar el fallo esperado.
3. Implementar backend T009–T013.
4. Implementar frontend T014–T016.
5. Ejecutar T017 y validar el registro de goles de forma independiente.

### Incremental Delivery Within US1

1. Reglas de atribución y consistencia probadas como funciones puras.
2. Endpoints con sus rechazos y el listado público.
3. Ficha de partido con goles, advertencia y formulario por rol.
4. Seguridad, migración, rendimiento, auditorías y métricas.

### Parallel Team Strategy

- Persona A: unitarias, contrato e integración + backend (T005–T007,
  T009–T013).
- Persona B: pruebas UI y frontend (T008, T014–T016).
- Ambas convergen en T017; el cierre T018–T023 es compartido.

## Notes

- `MatchEvent` ya estaba declarada en `specs/001-fundacion-y-autenticacion/data-model.md`:
  esta HU la implementa, no la rediseña.
- El marcador oficial nunca se modifica desde aquí, y T007 lo comprueba sobre
  el propio partido. La clasificación de 008 se deriva solo de ese marcador,
  así que queda protegida por transitividad; su aserción directa solo es
  posible si 008 se mezcla a `main` antes de cerrar esta HU.
- FR-005 advierte, nunca bloquea: un `409` por descuadre sería un defecto.
- El `type` se valida contra `GOAL` en schema y en CHECK; ampliarlo en el
  futuro es una migración de una línea (FR-004).
- La migración es la primera desde 006: hay que limpiar a mano el diff de
  Alembic (T003).
- AS3 no tiene cobertura de integración en esta HU por decisión registrada en
  `plan.md`; T023 deja el compromiso escrito en la spec de 010.
