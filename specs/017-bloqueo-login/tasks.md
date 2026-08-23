---

description: "Task list template for feature implementation"
---

# Tasks: Bloqueo tras intentos fallidos de inicio de sesión

**Input**: Design documents from `/specs/017-bloqueo-login/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/)

**Tests**: SÍ se incluyen. No es opcional aquí: el Principio II de la
constitución exige que toda regla de negocio tenga al menos una prueba
automatizada, y `quickstart.md` ya traza cada Acceptance Scenario con la prueba
que debe afirmarlo.

**Organization**: las tareas se agrupan por historia de usuario. US1 (bloquear)
es entregable por sí sola; US2 (desbloquear) se apoya en ella — la propia spec
lo dice: *"depende del bloqueo (Historia 1)"*.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede correr en paralelo (archivo distinto, sin dependencias pendientes)
- **[Story]**: US1 o US2, según la historia de `spec.md`
- Toda tarea lleva la ruta exacta del archivo

## Path Conventions

Aplicación web con backend y frontend separados, heredada de
`specs/001-fundacion-y-autenticacion/plan.md`: `backend/src/`, `backend/tests/`,
`frontend/src/`. Las rutas de abajo son literales del repositorio.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: la configuración que necesitan las dos historias (FR-007)

- [X] T001 [P] Añadir los campos `login_max_failed_attempts` (alias `LOGIN_MAX_FAILED_ATTEMPTS`, default `5`) y `login_lockout_seconds` (alias `LOGIN_LOCKOUT_SECONDS`, default `900`) a la clase `Settings` en `backend/src/core/config.py`, siguiendo el patrón de `session_ttl_seconds`
- [X] T002 [P] Documentar `LOGIN_MAX_FAILED_ATTEMPTS=` y `LOGIN_LOCKOUT_SECONDS=` vacías, con comentario, en una sección nueva de `.env.example` (no son secretos, pero es la convención del proyecto para toda llave de configuración)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: la tabla donde vive el contador. Sin ella ninguna historia puede empezar.

**⚠️ CRITICAL**: ninguna tarea de US1 ni de US2 puede comenzar hasta terminar esta fase

- [X] T003 Crear el modelo `IntentoDeLogin` (tabla `login_attempts`) en `backend/src/auth/models.py` con los campos y restricciones de [data-model.md](./data-model.md) (soporta FR-001): `username_normalizado` `String(60)` NOT NULL **UNIQUE** indexado, `failed_count` `Integer` NOT NULL default `0`, `blocked_until` `DateTime(timezone=True)` nullable, `last_attempt_at` `DateTime(timezone=True)` NOT NULL `server_default=now()`; mixins `Base, UUIDPrimaryKey, TimestampCreated`; **sin clave foránea a `users`** (deliberado: hay que contar identificadores inexistentes — research.md §1). Añadirlo a `__all__`
- [X] T004 Generar la migración con `alembic revision --autogenerate -m "crear tabla login_attempts"` desde `backend/`, y **revisar el diff**: debe contener solo `create_table("login_attempts")` y su índice único. Borrar del archivo cualquier `drop_index`/`create_index` espurio sobre `ix_leagues_unique_name_season` o `ix_teams_unique_league_name` que autogenerate invente (nota de índices funcionales de `AGENTS.md`). Un solo archivo en `backend/alembic/versions/`
- [X] T005 Verificar el archivo generado en `backend/alembic/versions/` contra una base vacía: desde `backend/`, `alembic upgrade head` sobre una BD limpia y `alembic heads` devolviendo **una sola** cabeza (Principio V)

**Checkpoint**: la tabla existe y el esquema es reproducible — puede empezar US1

---

## Phase 3: User Story 1 - Bloquear un identificador tras varios intentos fallidos (Priority: P1) 🎯 MVP

**Goal**: al superar el umbral de fallos consecutivos sobre un identificador
normalizado, ese identificador queda bloqueado y se rechaza todo intento
posterior —incluso con la contraseña correcta— sin revelar si la cuenta existe.

**Independent Test**: fallar 5 veces seguidas con el mismo identificador y
comprobar que el sexto intento responde `429 login_locked`, que responde igual
con la contraseña correcta, que otro usuario entra sin problema, y que un
identificador inventado produce exactamente la misma respuesta.

### Tests for User Story 1 ⚠️

> **Escribir estas pruebas PRIMERO y comprobar que FALLAN antes de implementar**

- [X] T006 [US1] Crear `backend/tests/integration/test_bloqueo_login.py` con los Acceptance Scenarios AS1–AS4 de la Historia 1: AS1 superar el umbral bloquea (5×`401`, el 6.º `429` con `code: login_locked`); AS2 bloqueado rechaza la **contraseña correcta**; AS3 un bloqueo no afecta al login de otro usuario; AS4 un identificador existente y uno inexistente devuelven cuerpos `429` idénticos (FR-006). Importar credenciales de `tests/conftest.py` (`USUARIO_ORGANIZADOR`, `CLAVE_INCORRECTA`, `USUARIO_INEXISTENTE`, fixtures `cliente`/`organizador_creado`/`credenciales_organizador`); definir en el propio archivo un helper local `async def fallar_n_veces(cliente, username, n)` — **no** modificar `conftest.py`
- [X] T007 [US1] Añadir a `backend/tests/integration/test_bloqueo_login.py` los edge cases: que alternar mayúsculas (`Usuario`/`USUARIO`/`usuario`) suma al **mismo** contador y bloquea al superar el umbral; que N peticiones fallidas simultáneas con `asyncio.gather` sobre el mismo identificador no permiten saltarse el bloqueo; y que el bloqueo **no se auto-extiende** al reintentar durante el bloqueo. Mismo archivo que T006, por eso sin `[P]`
- [X] T008 [US1] Añadir a `backend/tests/integration/test_bloqueo_login.py` la prueba de que el umbral **es configurable** (FR-007), que hoy ninguna prueba afirma: con `monkeypatch.setenv("LOGIN_MAX_FAILED_ATTEMPTS", "2")` seguido de `get_settings.cache_clear()` —el patrón que ya usa `backend/tests/contract/test_auth_contract.py:77-88`, con un `cache_clear()` también en el `finally` para no contaminar el resto de la suite— comprobar que el bloqueo salta al **tercer** intento y no al sexto. Cubre además el edge case «si el umbral cambia entre intentos, se aplica en cada comprobación». Mismo archivo que T006/T007, por eso sin `[P]`
- [X] T009 [P] [US1] Añadir a `backend/tests/contract/test_auth_contract.py` un test que afirme el contrato de [contracts/auth-lockout.openapi.yaml](./contracts/auth-lockout.openapi.yaml): la respuesta de bloqueo es `429`, trae cabecera `Retry-After` entera `>= 1`, y su cuerpo sigue el envelope `{error:{code,message,field}}` con `code == "login_locked"`. **Ampliar el archivo, no reescribirlo**: las aserciones existentes quedan intactas (Principio IV)

### Implementation for User Story 1

- [X] T010 [P] [US1] Añadir el parámetro opcional `headers: dict[str, str] | None = None` a `ErrorDeNegocio.__init__` y pasarlo al `JSONResponse` del manejador `_negocio` en `backend/src/core/errors.py`. Estrictamente aditivo: con el default `None` ningún error existente de ninguna spec cambia de comportamiento. Es lo que permite emitir `Retry-After` sin duplicar la construcción del envelope en el router (plan.md §Structure Decision)
- [X] T011 [US1] En `backend/src/auth/service.py`, añadir a `AuthService` la normalización del identificador y la lectura de su fila: un helper que devuelva `username.lower()` —exactamente la misma expresión que ya usa `autenticar` en la línea 75, para que el contador y el lookup coincidan (research.md §2)— y un método que traiga el `IntentoDeLogin` por `username_normalizado`, o `None`
- [X] T012 [US1] En `backend/src/auth/service.py`, implementar el registro del fallo por identificador normalizado (FR-001): UPSERT atómico con `sqlalchemy.dialects.postgresql.insert(...).on_conflict_do_update(...)` sobre `username_normalizado`, con `failed_count = login_attempts.failed_count + 1` y `RETURNING failed_count`, para que dos intentos simultáneos no produzcan un *lost update* (research.md §6). Si el valor devuelto alcanza `settings.login_max_failed_attempts`, fijar `blocked_until = now(UTC) + timedelta(seconds=settings.login_lockout_seconds)` y **reiniciar `failed_count` a 0** (research.md §8). **El `commit` va ANTES del `raise` del error de credenciales**: si se lanza primero, la sesión se descarta, el incremento se pierde y el bloqueo no llega a activarse nunca (research.md §7)
- [X] T013 [US1] En `backend/src/auth/service.py`, insertar el gate al principio de `AuthService.autenticar`, **antes** de la búsqueda del usuario y de `verificar_password`: si la fila tiene `blocked_until` y `blocked_until > now(UTC)`, lanzar `ErrorDeNegocio(code="login_locked", status_code=429, headers={"Retry-After": str(segundos_restantes)})` (FR-002) con `segundos_restantes` redondeado hacia arriba y mínimo `1`. Comprobar antes de verificar la contraseña es lo que hace cumplir FR-003 —si se verificara primero, un acierto se colaría— y evita un `bcrypt` por intento durante un ataque (research.md §5). Depende de T010, T011, T012
- [X] T014 [P] [US1] Añadir la entrada `login_locked` al catálogo `mensajes` de `frontend/src/lib/mensajesDeError.ts`, con un mensaje fijo en español del tipo "Demasiados intentos fallidos. Espera unos minutos antes de volver a intentarlo." — **sin** el número exacto de minutos: el catálogo es estático y `mensajeDeError` nunca renderiza el `message` del servidor (research.md §10). El test existente que recorre `codigosConocidos` lo cubre automáticamente; no hace falta tocar `LoginPage.tsx` ni `AuthContext.tsx`

**Checkpoint**: US1 completa y verificable sola. Un identificador se bloquea, ni la contraseña correcta pasa, nadie más se ve afectado y la respuesta no filtra existencia. Entregable como MVP.

---

## Phase 4: User Story 2 - Desbloquear automáticamente al expirar (Priority: P2)

**Goal**: el bloqueo caduca solo y el usuario legítimo recupera el acceso sin
intervención; un login correcto deja el contador en cero.

**Independent Test**: bloquear un identificador, dejar que expire el periodo y
comprobar que el login vuelve a funcionar; y comprobar que fallar unas cuantas
veces y luego acertar reinicia el conteo.

**Nota sobre el tamaño de esta fase**: FR-004 (desbloqueo automático) **no
lleva código propio**. Por diseño el desbloqueo es implícito — un identificador
está bloqueado si y solo si `blocked_until > now()` en el momento de la
comprobación, que es justo la condición del gate de T013 (research.md §8). No
hay job, ni scheduler, ni estado que caducar. Esta fase, por tanto, implementa
FR-005 (reiniciar el conteo al acertar) y **prueba** FR-004. No falta nada.

### Tests for User Story 2 ⚠️

> **Escribir primero y comprobar que FALLAN**

- [X] T015 [US2] Añadir a `backend/tests/integration/test_bloqueo_login.py` los Acceptance Scenarios AS1–AS3 de la Historia 2: AS1 con el bloqueo expirado el login correcto vuelve a dar `200`; AS2 tres fallos → un acierto → tres fallos más sigue en `401` y **no** en `429` (el contador se reinició); AS3 tras el login correcto posterior al desbloqueo no queda fila en `login_attempts` para ese identificador. Para la expiración **no usar `sleep`**: mover `blocked_until` al pasado con un `UPDATE` sobre la fila (vía `SessionLocal`, como ya hace `test_auth.py`) y volver a llamar al endpoint

### Implementation for User Story 2

- [X] T016 [US2] En `backend/src/auth/service.py`, borrar la fila de `login_attempts` del identificador normalizado cuando la autenticación tiene éxito, antes de devolver el `Usuario` (FR-005). Cubre los dos escenarios: fallar-y-luego-acertar reinicia el conteo, y acertar tras el desbloqueo lo deja en cero

**Checkpoint**: US1 y US2 funcionan. El ciclo completo bloquear → esperar → recuperar acceso queda cerrado.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: quality gates de la constitución y cierre de la HU

- [X] T017 [P] Ejecutar la suite completa del backend con `cd backend && pytest` y dejarla en verde, sin `skip` ni `xfail` nuevos. Prestar atención a `tests/integration/test_auth.py` y `tests/contract/test_auth_contract.py`: deben pasar **sin modificarse** (Principio IV)
- [X] T018 [P] Ejecutar `cd frontend && npm test` y dejarlo en verde, incluido el recorrido de `codigosConocidos` en `frontend/src/lib/__tests__/mensajesDeError.test.ts`
- [X] T019 [P] Pasar los linters que corre el CI, sin excepciones silenciosas ni `noqa`/`eslint-disable` nuevos (Principio VII): desde `backend/`, `uv run ruff check src tests` y `uv run ruff format --check src tests`; desde `frontend/`, `npm run lint`
- [X] T020 Rebasar la rama sobre `main` actualizado y **re-puntear el `down_revision`** del archivo de migración a la cabeza ya mezclada. Orden de merge pactado del bloque paralelo: `013 → 014 → 016 → 017`; esta HU es la **última** de las cuatro que migran. Volver a comprobar que `alembic heads` devuelve una sola cabeza y que `alembic upgrade head` corre desde base vacía (`AGENTS.md`, nota de migraciones en paralelo)
- [X] T021 Recorrer la validación manual de [quickstart.md](./quickstart.md) §Validación manual, incluido el paso 5 con `LOGIN_LOCKOUT_SECONDS=20` (recordar que `get_settings()` está bajo `@lru_cache`: hay que reiniciar el proceso) y el paso 6 en la interfaz
  - Recorrida completa el 2026-08-22, pasos 1-6. El paso 6 se verificó en la
    interfaz real: cinco envíos fallidos desde la pantalla de login devuelven
    `401` y el sexto `429`, y el banner muestra el mensaje del catálogo
    ("Demasiados intentos fallidos. Espera unos minutos…"), no el genérico.
    Sin excepciones en consola. Cubierto además por prueba automatizada en
    `frontend/src/lib/__tests__/mensajesDeError.test.ts`.
- [X] T022 Copiar `docs/metricas/_plantilla.md` a `docs/metricas/017-bloqueo-login.md` y llenar la sección "Llenado por el agente" con datos reales: tareas completadas, pruebas escritas y en verde, ciclos de corrección, y qué se reprocesó y por qué. **No inventar el costo/tokens de IA ni el tiempo real de trabajo** — esos dos campos los llena la persona (`AGENTS.md` §7)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias, puede empezar de inmediato
- **Foundational (Phase 2)**: **sin dependencia de la Phase 1** — las dos variables nuevas tienen valor por defecto, así que tanto la app como Alembic arrancan sin ellas. Puede solaparse con el Setup. **BLOQUEA** a US1 y US2
- **US1 (Phase 3)**: depende de la Phase 2 completa
- **US2 (Phase 4)**: depende de la Phase 2, y en la práctica de US1 — ver abajo
- **Polish (Phase 5)**: depende de las historias que se quieran entregar

### User Story Dependencies

- **US1 (P1)**: solo depende de Foundational. Entregable sola.
- **US2 (P2)**: **no es independiente de US1**, y la spec lo reconoce
  explícitamente (*"depende del bloqueo (Historia 1)"*). Sus escenarios AS1 y
  AS3 necesitan poder bloquear primero, así que sus pruebas no pueden pasar sin
  US1. Se documenta aquí en vez de fingir un paralelismo que no existe: US2 va
  **después** de US1, no en paralelo.
  - Matiz: AS2 (acertar antes del umbral reinicia el conteo) sí es verificable
    con solo el conteo de US1, sin bloqueo de por medio.

### Within Each User Story

- Las pruebas se escriben primero y deben fallar antes de implementar
- Modelo → servicio → contrato/endpoint → frontend
- Dentro de US1: T011 (leer) → T012 (contar) → T013 (bloquear). Es el orden de
  construcción natural: contar tiene que existir para que bloquear signifique algo

### Parallel Opportunities

- **Phase 1**: T001 y T002 en paralelo (archivos distintos)
- **Phase 2**: internamente nada en paralelo — T003 → T004 → T005 es una cadena estricta. La fase entera sí puede solaparse con la Phase 1 (ver arriba)
- **Phase 3**: T009 (contract test, archivo propio) en paralelo con T006/T007/T008.
  En implementación, T010 (`core/errors.py`) y T014 (frontend) corren en
  paralelo con la cadena de `service.py`; T011–T013 son secuenciales entre sí
  por compartir archivo
- **Phase 4**: nada en paralelo (una prueba, una implementación)
- **Phase 5**: T017, T018 y T019 en paralelo; T020–T022 secuenciales al final
- **Entre historias**: ninguna. US2 va después de US1 (ver arriba)

---

## Parallel Example: User Story 1

```bash
# Pruebas: el contract test es el único de archivo propio, va en paralelo
# con la escritura del archivo de integración.
Task: "T009 Contract test del 429 + Retry-After en backend/tests/contract/test_auth_contract.py"

# Implementación: las dos puntas que no tocan service.py van juntas.
Task: "T010 headers opcionales en ErrorDeNegocio en backend/src/core/errors.py"
Task: "T014 código login_locked en frontend/src/lib/mensajesDeError.ts"

# Y en serie, porque los tres tocan el mismo archivo:
# T011 -> T012 -> T013 en backend/src/auth/service.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Setup (T001–T002)
2. Phase 2: Foundational (T003–T005) — CRÍTICA, bloquea todo
3. Phase 3: US1 (T006–T014)
4. **PARAR Y VALIDAR**: los cuatro Acceptance Scenarios de la Historia 1 más
   los edge cases, con `pytest tests/integration/test_bloqueo_login.py -v`
5. En este punto la protección contra fuerza bruta **ya funciona**: es un
   incremento con valor real por sí solo

**Aviso honesto sobre entregar solo el MVP**: sin US2 el contador nunca se
reinicia al acertar. Un usuario legítimo que falle 4 veces a lo largo de días
quedaría bloqueado en su quinto fallo aunque haya entrado bien entremedias. El
bloqueo sí caduca solo (FR-004 no necesita código), así que nadie queda
atrapado más de 15 minutos, pero **US1 sin US2 no debería quedarse en `main`
como estado final**.

### Incremental Delivery

1. Setup + Foundational → la tabla existe, sin cambio de comportamiento visible
2. US1 → bloqueo operativo → validar → demo
3. US2 → reinicio del conteo y ciclo de recuperación completo → validar → demo
4. Polish → quality gates, migración re-punteada y métricas → PR

### Parallel Team Strategy

Esta HU es de **un solo integrante**, por diseño: es la única del bloque
paralelo que toca `auth/`, precisamente para que nadie compita por esos
archivos (`spec.md` §Dependencies). Dentro de la HU, US1 y US2 son
secuenciales, así que no hay reparto que hacer. El paralelismo aprovechable es
el de archivos dentro de una misma fase, listado arriba.

---

## Notes

- `[P]` = archivos distintos, sin dependencias pendientes
- `conftest.py` **no se toca**: los helpers de prueba viven en el propio
  `test_bloqueo_login.py`, para no arriesgar las suites de otras specs
- La fixture `base_limpia` recrea el esquema en cada test, así que ningún
  contador se arrastra entre pruebas
- Ninguna prueba existente se borra, salta ni debilita (Principio IV)
- Commit por tarea o por grupo lógico; los commits intermedios de la rama
  pueden ser informales porque el merge es squash
- Título del PR: `feat(017): bloquear el login tras intentos fallidos`
