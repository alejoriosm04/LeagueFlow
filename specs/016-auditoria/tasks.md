# Tasks: Auditoría de operaciones administrativas

**Input**: Design documents from `/specs/016-auditoria/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/audit.openapi.yaml`, `quickstart.md`

**Tests**: obligatorias por los Acceptance Scenarios de ambas historias,
FR-001–FR-007 y los Principios I y II de la constitución. La única "regla de
negocio" de esta feature — solo se registran escrituras exitosas, sin body —
es exactamente lo que verifican las pruebas de US1; el orden cronológico
inverso y el rechazo por rol es lo que verifican las de US2.

**Organization**: la spec tiene dos historias — US1 (P1, registrar) y US2
(P2, consultar). Setup, Foundational y Polish no llevan etiqueta de
historia.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo porque trabaja en un archivo distinto
  y no depende de una tarea incompleta del mismo grupo.
- **[US1]**: Registrar automáticamente cada operación de escritura.
- **[US2]**: Consultar el historial de auditoría.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: confirmar que las dos piezas de `specs/001-*` que esta historia
reutiliza tal cual — `AuthService.obtener_sesion_valida` y `requiere_rol` —
siguen en verde, y fijar el head de Alembic sobre el que se va a migrar.

- [X] T001 Ejecutar la regresión base de autenticación con
      `backend/tests/contract/test_auth_contract.py` y
      `backend/tests/integration/test_auth.py`, deteniendo la implementación
      si falla una prueba existente — esta historia no toca `src/auth/`, solo
      lo reutiliza (`research.md` §3, §9)
- [X] T002 Confirmar el head actual de Alembic corriendo `uv run alembic heads`
      desde `backend/` y registrar el resultado (esperado: `919f3bd57721`,
      `research.md` §10); si `013-grupos-divisiones` o
      `014-tarjetas-sanciones` ya se mezclaron a `main`, usar el head real en
      su lugar, no el documentado en `research.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: crear la tabla `audit_logs` — la única entidad de esta feature,
compartida por ambas historias (US1 escribe, US2 lee). Ninguna historia
puede empezar hasta que exista.

**⚠️ CRITICAL**: ningún trabajo de US1 o US2 comienza hasta que este bloque
esté completo.

- [X] T003 Crear `backend/src/audit/__init__.py` y el modelo `AuditLogEntry`
      en `backend/src/audit/models.py` (`__tablename__ = "audit_logs"`) con
      los campos de `data-model.md` — `method`, `path`, `status_code`,
      `actor_id` (FK nullable a `users.id`, `ondelete="SET NULL"`),
      `actor_username` (nullable), `created_at` — y el índice
      `ix_audit_logs_created_at` sobre `created_at`, no único ni funcional
      (`research.md` §11, sin el riesgo de `AGENTS.md` sobre índices
      funcionales)
- [X] T004 Importar `src.audit.models` en `backend/alembic/env.py` junto a
      los demás módulos de dominio, para que `autogenerate` detecte
      `audit_logs` — depende de T003
- [X] T005 Generar la migración con
      `uv run alembic revision --autogenerate -m "crear tabla audit_logs"`
      desde `backend/`, con `down_revision` apuntando al head confirmado en
      T002; revisar el diff y confirmar que **solo** crea `audit_logs` y
      `ix_audit_logs_created_at`, sin tocar
      `ix_leagues_unique_name_season`/`ix_teams_unique_league_name` ni
      ningún índice de specs anteriores (`AGENTS.md`, nota de índices
      funcionales) — depende de T004
- [X] T006 Aplicar la migración con `uv run alembic upgrade head` desde
      `backend/` contra la base de datos local y confirmar que `audit_logs`
      existe — depende de T005

**Checkpoint**: tabla `audit_logs` migrada y disponible. US1 y US2 pueden
empezar, en paralelo si hay capacidad.

---

## Phase 3: User Story 1 - Registrar automáticamente cada operación (Priority: P1) 🎯 MVP

**Goal**: toda petición `POST/PUT/PATCH/DELETE` que termina en `2xx` queda
registrada en `audit_logs` con actor, método, ruta, status y fecha — sin
tocar ningún router existente y sin persistir jamás el body de la petición
ni de la respuesta (FR-001 a FR-004, FR-007).

**Independent Test**: realizar una operación de escritura autenticada (p.
ej. `POST /leagues`) y verificar, consultando `audit_logs` directamente
(vía una sesión de BD en el test — todavía no existe el endpoint de
lectura, que es US2), que quedó una fila con el actor, la acción y la
fecha correctos.

### Tests for User Story 1 — write first, verify they fail

- [X] T007 [US1] Crear pruebas de integración en
      `backend/tests/integration/test_audit.py`, consultando `audit_logs`
      directamente vía una sesión de BD (no vía HTTP — el endpoint de
      lectura es US2, esta historia debe ser verificable sin él): una
      escritura exitosa (`POST /leagues` como organizador) produce una fila
      con `method="POST"`, `path` conteniendo `/leagues`,
      `status_code=201`, `actor_username` igual al del organizador
      autenticado y `created_at` reciente (AC1, FR-001); una lectura (`GET
      /leagues`) no produce ninguna fila nueva (AC2, FR-002); una escritura
      que falla por regla de negocio (repetir la misma liga → `409`) no
      produce ninguna fila nueva (clarificación de `spec.md`); un `POST
      /auth/login` exitoso produce una fila con `actor_id` y
      `actor_username` en `null` — el actor no es determinable porque la
      petición que crea la sesión no trae todavía la cookie (FR-004,
      `research.md` §3); ninguna fila de las anteriores tiene ninguna
      columna con contenido del body enviado o recibido (AC3, FR-003 — por
      inspección de las columnas del modelo, no hay dónde guardarlo)

### Implementation for User Story 1

- [X] T008 [US1] Implementar `AuditService.registrar(method, path,
      status_code, actor)` en `backend/src/audit/service.py`: recibe un
      `Usuario | None` ya resuelto (no reresuelve la sesión), guarda
      `actor_id`/`actor_username` como snapshot cuando `actor` no es `None`
      y ambos en `null` en caso contrario, hace `commit()` sobre la sesión
      que recibe por parámetro (no abre la suya) — depende de T003
- [X] T009 [US1] Implementar `AuditMiddleware` (ASGI puro, no
      `BaseHTTPMiddleware`) en `backend/src/audit/middleware.py`
      (`research.md` §1–§6): si `scope["method"]` no está en
      `{"POST","PUT","PATCH","DELETE"}`, reenvía a `self.app` sin trabajo
      adicional; si lo está, resuelve el actor construyendo
      `starlette.requests.Request(scope)` para leer la cookie
      `lf_session` (`NOMBRE_COOKIE` de `src.auth.dependencies`) y llamando
      `AuthService(db).obtener_sesion_valida(token)` sobre una sesión propia
      abierta con `SessionLocal()` (no `Depends(get_db)`, `research.md`
      §2–§3); envuelve `send` solo para capturar el `status` de
      `http.response.start` en una variable local, sin tocar ningún mensaje
      `http.response.body`; tras que `await self.app(scope, receive,
      send_wrapper)` retorna, si `200 <= status < 300` llama a
      `AuditService.registrar(...)` sobre la misma sesión propia y hace
      `commit`, envuelto en `try/except` con `logger.exception` (nunca
      relanza — un fallo de auditoría no debe afectar una respuesta que el
      cliente ya recibió, `research.md` §4) — depende de T008
- [X] T010 [US1] Registrar `app.add_middleware(AuditMiddleware)` en
      `backend/src/main.py`, inmediatamente después del
      `app.add_middleware(CORSMiddleware, ...)` existente — depende de T009

### Story verification

- [X] T011 [US1] Ejecutar `backend/tests/integration/test_audit.py`,
      corrigiendo la implementación sin borrar, saltar ni debilitar pruebas
      — depende de T007–T010

**Checkpoint**: toda escritura exitosa del sistema queda auditada de forma
transversal, verificable de forma independiente por consulta directa a
`audit_logs`. US1 es el MVP de esta feature.

---

## Phase 4: User Story 2 - Consultar el historial de auditoría (Priority: P2)

**Goal**: un organizador autenticado puede listar `audit_logs` en orden
`created_at` descendente vía `GET /admin/audit-log`; cualquier otro rol o
ausencia de sesión es rechazado (FR-005, FR-006).

**Independent Test**: con filas ya existentes en `audit_logs` (insertadas
directamente en el test, sin depender de que US1 esté conectada al
middleware real), abrir el historial como organizador y verificar que
aparecen en orden cronológico inverso; verificar que un operador y un
visitante sin sesión son rechazados.

### Tests for User Story 2 — write first, verify they fail

- [X] T012 [P] [US2] Crear pruebas de contrato en
      `backend/tests/contract/test_audit_contract.py` conforme a
      `contracts/audit.openapi.yaml`: `GET /admin/audit-log` como
      organizador responde `200` con la forma
      `{items, page, page_size, total}` y cada `item` con `method`, `path`,
      `status_code`, `actor_id`, `actor_username`, `created_at`; sin cookie
      responde `401 not_authenticated`; con sesión de rol `operador`
      responde `403 insufficient_role` — ambos con el envelope de error
      compartido
- [X] T013 [P] [US2] Crear pruebas de integración en
      `backend/tests/integration/test_audit.py` (mismo archivo de T007,
      añadido a continuación): con varias filas de `audit_logs` insertadas
      con `created_at` escalonados, `GET /admin/audit-log` las devuelve en
      orden `created_at` descendente (AC1 de US2, FR-005); con `audit_logs`
      vacía, responde `200` con `items: []` y `total: 0`, sin error (Edge
      Case de `spec.md`)
- [X] T014 [P] [US2] Crear pruebas de UI en
      `frontend/src/features/audit/__tests__/audit.test.tsx`: la página
      renderiza una tabla con las entradas devueltas por
      `auditApi.listar()` (fecha, actor, método, destino, resultado);
      estado de carga, estado de error y estado vacío propios (catálogo de
      `specs/012-identidad-visual`); `ProtectedRoute` bloquea el acceso a
      quien no tiene sesión o no es organizador, igual que en
      `/leagues/new`

### Backend implementation for User Story 2

- [X] T015 [P] [US2] Definir `AuditLogEntry` (Pydantic) y `PaginatedAuditLog`
      en `backend/src/audit/schemas.py`, con los mismos campos y
      nombres de `contracts/audit.openapi.yaml` — depende de T003
- [X] T016 [US2] Implementar `AuditService.listar(page, page_size) ->
      tuple[list[AuditLogEntry], int]` en `backend/src/audit/service.py`
      (mismo archivo de T008): `SELECT` sobre `audit_logs` ordenado por
      `created_at DESC`, con `offset`/`limit` y conteo total, igual patrón
      que `LeagueService.listar_ligas` — depende de T015
- [X] T017 [US2] Exponer `GET /admin/audit-log` en
      `backend/src/audit/router.py`, protegido con
      `Depends(requiere_rol("organizador"))` (la misma dependencia que ya
      usan `POST /leagues` y `POST /users`, sin crear una nueva) y
      parámetros de query `page`/`page_size` (default 1/20, máximo 100,
      convención de `contracts/conventions.md`) — depende de T016
- [X] T018 [US2] Registrar `audit_router` en `backend/src/main.py` con
      `app.include_router(audit_router, prefix="/api/v1")`, junto a los
      demás routers de dominio — depende de T017

### Frontend implementation for User Story 2

- [X] T019 [P] [US2] Crear tipos `AuditLogEntry`/`PaginatedAuditLog` y el
      cliente `auditApi.listar(page, pageSize)` derivados del contrato en
      `frontend/src/features/audit/api.ts`, siguiendo el patrón de
      `frontend/src/features/players/api.ts` — puede empezar en cuanto
      exista `contracts/audit.openapi.yaml`, sin esperar al backend real
- [X] T020 [US2] Implementar `frontend/src/features/audit/AuditLogPage.tsx`:
      tabla con columnas fecha, actor, método, destino y resultado,
      reutilizando `TituloDePantalla`/`TablaDeDatos`/`EstadoCarga`/
      `EstadoError`/`EstadoVacio` del catálogo compartido, con
      `actor_username` mostrado como texto ("Actor no determinable" cuando
      es `null`, FR-004) — depende de T019
- [X] T021 [US2] Registrar la ruta `/admin/audit-log` en
      `frontend/src/routes.tsx` dentro de
      `<ProtectedRoute rol="organizador">`, y añadir un enlace hacia ella
      desde la pantalla `/admin` ya existente (`SoloOrganizador` en el mismo
      archivo) — depende de T020

### Story verification

- [X] T022 [US2] Ejecutar `backend/tests/contract/test_audit_contract.py`,
      `backend/tests/integration/test_audit.py` completo y
      `frontend/src/features/audit/__tests__/audit.test.tsx`, corrigiendo la
      implementación sin borrar, saltar ni debilitar pruebas — depende de
      T012–T021

**Checkpoint**: ambas historias funcionan de forma independiente y juntas —
un organizador puede trazar cualquier escritura reciente del sistema en 3
interacciones o menos (SC-005).

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: cerrar seguridad, alcance real de la migración, validación
end-to-end y métricas de cierre.

- [X] T023 [P] Revisar `backend/src/audit/middleware.py` línea por línea
      contra FR-003: confirmar que ningún mensaje `http.response.body` se
      inspecciona ni se guarda, que `receive` nunca se envuelve, y que
      `logger.exception` (no un `raise`) es lo único que ocurre si
      `AuditService.registrar` falla
- [X] T024 [P] Verificar con `uv run alembic check` desde `backend/` que la
      única migración pendiente de esta HU es la de `audit_logs`, y por
      inspección del archivo generado en T005 confirmar que no reaparecen
      `DROP INDEX`/`CREATE INDEX` espurios sobre índices de specs
      anteriores
- [X] T025 Ejecutar los 5 escenarios de `specs/016-auditoria/quickstart.md`
      manualmente (o vía script), confirmando SC-001 a SC-005 sin inventar
      resultados
- [X] T026 Ejecutar suites completas y quality gates de
      `.github/workflows/ci.yml`: pytest, Ruff check/format, Vitest, ESLint,
      build, `pip-audit` y `npm audit`; corregir regresiones sin modificar
      requisitos ni debilitar pruebas
- [X] T027 Crear `docs/metricas/016-auditoria.md` desde
      `docs/metricas/_plantilla.md` y llenar únicamente tareas, tests,
      ciclos y reprocesos reales, dejando tiempo real y costo de IA para la
      persona

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: inicia de inmediato.
- **Foundational (Phase 2)**: depende de T002 (head de Alembic); bloquea
  US1 y US2.
- **US1 (Phase 3)**: depende de T006; T007 debe fallar por funcionalidad
  ausente antes de T008–T010.
- **US2 (Phase 4)**: depende de T006 (no de US1 completa — sus pruebas
  insertan filas directamente, `research.md`/Independent Test arriba);
  T012–T014 deben fallar antes de T015–T021.
- **Polish (Phase 5)**: depende de T011 y T022; T023–T024 en paralelo,
  luego T025 → T026 → T027.

### User Story Dependencies

- **US1 (P1)**: depende solo de Foundational. No depende de US2.
- **US2 (P2)**: depende solo de Foundational. No depende de que US1 esté
  conectada al middleware real para sus propias pruebas (usa filas
  insertadas directamente) — pero en producción no tiene nada interesante
  que mostrar hasta que US1 esté desplegada, así que se implementa después
  por prioridad, no por bloqueo técnico.

### Within User Story 1

```text
T007 (prueba roja)
  ↓
T008 → T009 → T010
  ↓
T011
```

### Within User Story 2

```text
T012  T013  T014        (pruebas rojas, en paralelo — 3 archivos distintos)
  ↓
T015 → T016 → T017 → T018
T019 → T020 → T021
  ↓
T022
```

- T015 y T019 pueden arrancar en paralelo entre sí (schemas backend vs.
  tipos frontend), ambos apoyados solo en el contrato ya publicado.
- T016 comparte archivo con T008 (`service.py`): dentro de la misma
  feature, T016 se escribe después de que T008 exista, no en paralelo con
  él.

### Parallel Opportunities

- T012–T014: contrato, integración y UI en archivos independientes.
- T015 y T019: schema backend y tipos frontend, en paralelo.
- T023 y T024: revisiones de cierre independientes.

## Parallel Example: User Story 2

```text
Task: "T012 contrato, 401/403 en backend/tests/contract/test_audit_contract.py"
Task: "T013 orden created_at DESC y lista vacía en backend/tests/integration/test_audit.py"
Task: "T014 tabla, tres estados y bloqueo de ProtectedRoute en frontend/src/features/audit/__tests__/audit.test.tsx"
```

## Implementation Strategy

### MVP First (US1)

1. Completar T001–T002 (Setup).
2. Completar T003–T006 (Foundational: tabla `audit_logs`).
3. Escribir T007 y comprobar el fallo esperado.
4. Implementar T008–T010 (`AuditService.registrar` + `AuditMiddleware` +
   registro en `main.py`).
5. Ejecutar T011 y validar por consulta directa a `audit_logs` que toda
   escritura exitosa queda registrada.

### Incremental Delivery

1. Setup + Foundational → tabla lista.
2. US1 → captura transversal activa → validar de forma independiente.
3. US2 → endpoint de lectura + página → validar de forma independiente y en
   conjunto con US1.
4. Polish → seguridad, migración, quickstart, CI, métricas.

### Parallel Team Strategy

- Persona A: US1 completa (T007–T011).
- Persona B: contrato/schemas/frontend de US2 (T012, T015, T019) mientras
  A termina Foundational — el resto de US2 (T016–T018, T020–T022) depende
  de que la tabla exista (Foundational) pero no de que US1 esté terminada.
- Ambas convergen en el cierre T023–T027.

## Notes

- Una sola entidad nueva (`AuditLogEntry`); ninguna spec del bloque
  paralelo (`013-017`) toca `backend/src/audit/` (`spec.md`, Dependencies).
- El middleware nunca reimplementa la validación de sesión: llama
  `AuthService.obtener_sesion_valida` tal cual (`research.md` §3).
- El endpoint de lectura nunca reimplementa la autorización por rol: usa
  `requiere_rol("organizador")` tal cual (`research.md` §9).
- FR-003 no se da por cumplido "porque nadie lo hizo a propósito": T007 y
  T023 son la prueba y la revisión de que estructuralmente no hay dónde
  guardar un body.
- Antes de abrir el PR, re-confirmar `uv run alembic heads` contra el `main`
  vigente en ese momento (T002 documenta el head al planear, no al
  mezclar) — ver `AGENTS.md`, nota de migraciones en paralelo.
