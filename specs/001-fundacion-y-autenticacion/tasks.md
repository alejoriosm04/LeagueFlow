---

description: "Task list for feature implementation"
---

# Tasks: Fundación técnica y autenticación

**Input**: Design documents from `/specs/001-fundacion-y-autenticacion/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md — todos presentes.

**Tests**: incluidas. No son opcionales aquí: el Principio II de la constitución exige prueba automatizada para toda regla de negocio, y `quickstart.md` ya define los comandos `pytest`/`Vitest` como gate mínimo de esta spec.

**Organization**: esta spec tiene una sola User Story (P1, Autenticación y control de acceso por rol), pero además construye el esqueleto de infraestructura compartido por todo el proyecto (Fase 2). `specs/002-*` en adelante reutilizan esa infraestructura sin repetirla.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo (archivo distinto, sin dependencias pendientes)
- **[US1]**: tarea de la User Story 1 (única de esta spec)
- Rutas de archivo según `plan.md` → Project Structure (`backend/src/`, `frontend/src/`)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: inicialización del repositorio backend/frontend y del pipeline de CI.

- [X] T001 Crear el esqueleto `backend/src/{auth,leagues,teams,players,matches,statistics,core}/` y `backend/tests/{contract,integration,unit}/` con `__init__.py`, según `plan.md` → Project Structure
- [X] T002 Inicializar `backend/pyproject.toml` con FastAPI + Pydantic v2 (research.md §1), SQLAlchemy[asyncio] 2.0 + Alembic (research.md §3), `passlib[bcrypt]` (research.md §4), `httpx` + `pytest` + `pytest-asyncio` (research.md §5)
- [X] T003 [P] Inicializar `frontend/` (Vite + React 18 + TypeScript), instalar `react-router-dom`, `vitest`, `@testing-library/react` (research.md §2)
- [X] T004 [P] Configurar lint/format backend (`ruff`) en `backend/pyproject.toml`
- [X] T005 [P] Configurar lint/format frontend (ESLint + Prettier) en `frontend/.eslintrc.cjs` y `frontend/.prettierrc`
- [X] T006 [P] Crear `backend/.env.example` y `frontend/.env.example` con `DATABASE_URL`, `ALLOWED_ORIGINS`, `SESSION_SECRET` vacíos (Principio VI de la constitución)
- [X] T007 [P] Crear `.github/workflows/ci.yml`: lint → tests unitarios → tests de integración → escaneo de dependencias → build, en cada PR (research.md §8)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: infraestructura que bloquea tanto la User Story 1 de esta spec como toda spec `002-011` posterior.

**⚠️ CRITICAL**: ninguna otra spec del proyecto empieza su propio `/speckit-plan` hasta que esta fase (y la User Story 1) estén mezcladas a `main` (`AGENTS.md` §5).

- [X] T008 Configurar conexión a PostgreSQL y `async_sessionmaker` en `backend/src/core/db.py` (data-model.md, research.md §3)
- [X] T009 Inicializar entorno de Alembic en `backend/alembic/` apuntando a `backend/src/core/db.py` (Principio V — migraciones versionadas) (depende de T008)
- [X] T010 [P] Crear `Base` declarativo de SQLAlchemy y mixins comunes (`id` UUID, `created_at`) en `backend/src/core/models_base.py` (convención de `data-model.md`)
- [X] T011 [P] Implementar el envelope de error y los exception handlers de FastAPI en `backend/src/core/errors.py` (`contracts/conventions.md` → Envelope de error, códigos HTTP)
- [X] T012 [P] Configurar `CORSMiddleware` leyendo `ALLOWED_ORIGINS` desde entorno en `backend/src/core/config.py` (Estándares de Seguridad de la constitución)
- [X] T013 Ensamblar la app FastAPI (monta routers, registra exception handlers y CORS) en `backend/src/main.py` (depende de T008, T010, T011, T012)
- [X] T014 [P] Crear el cliente HTTP del frontend (`fetch` base, `credentials: "include"`, parseo del envelope de error) en `frontend/src/services/apiClient.ts` (`contracts/conventions.md`)
- [X] T015 [P] Crear el shell de la app y el router de frontend en `frontend/src/App.tsx` y `frontend/src/routes.tsx`

**Checkpoint**: infraestructura lista — la User Story 1 y, más adelante, `specs/002-*` en adelante pueden empezar.

---

## Phase 3: User Story 1 - Autenticación y control de acceso por rol (Priority: P1) 🎯 MVP

**Goal**: solo un usuario autenticado con el rol adecuado puede ejecutar operaciones de escritura; las consultas siguen siendo públicas.

**Independent Test**: iniciar sesión como operador y verificar que puede registrar pero no aprobar ni crear ligas; iniciar sesión como organizador y verificar que sí puede; navegar sin sesión y verificar que las vistas públicas responden igual (`quickstart.md` §Escenarios de validación).

### Tests for User Story 1 ⚠️

> Escribir estas pruebas primero y verificar que fallan antes de implementar.

- [X] T016 [P] [US1] Contract test de `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`, `POST /users`, `GET /users` contra `contracts/auth.openapi.yaml` en `backend/tests/contract/test_auth_contract.py`
- [X] T017 [P] [US1] Integration test de los 7 Acceptance Scenarios de `spec.md` (login válido/inválido, consulta sin sesión, escritura sin sesión, rol insuficiente, logout revoca, atribución de autoría vía `created_by` en el usuario creado) en `backend/tests/integration/test_auth.py`, incluida una aserción de tiempo sobre el login (`< 5s`, SC-003)

### Implementation for User Story 1

- [X] T018 [US1] Crear los modelos SQLAlchemy `User` (incluye `created_by`, nullable solo para la semilla) y `Session` en `backend/src/auth/models.py` (data-model.md: User, Session; FR-001, FR-004, FR-005, FR-008)
- [X] T019 [US1] Generar y aplicar la migración Alembic de `users` y `sessions` en `backend/alembic/versions/` (depende de T018)
- [X] T020 [P] [US1] Crear los schemas Pydantic (`UserPublic`, `LoginRequest`, `CreateUserRequest`, `PaginatedUsers`) en `backend/src/auth/schemas.py` (`contracts/auth.openapi.yaml`)
- [X] T021 [US1] Implementar utilidades de hash de contraseña con `passlib[bcrypt]` en `backend/src/auth/security.py` (FR-005)
- [X] T022 [US1] Implementar `AuthService` (`create_user`, `authenticate`, `create_session`, `revoke_session`) en `backend/src/auth/service.py` (FR-004, FR-005, FR-006, FR-010; depende de T018, T021)
- [X] T023 [US1] Implementar las dependencias FastAPI `get_current_user` / `require_role` en `backend/src/auth/dependencies.py`, incluida la extensión de `Session.expires_at` en cada validación exitosa — expiración por inactividad, no TTL fijo (FR-003, FR-006, FR-009; depende de T022)
- [X] T024 [US1] Implementar el router de auth (`login`, `logout`, `me`, `POST/GET /users`) en `backend/src/auth/router.py`; `POST /users` MUST poblar `created_by` con el `id` del usuario de la sesión que llama; `GET /users` MUST paginar con `page`/`page_size` y responder el envelope `PaginatedUsers`, no un array plano (FR-007, FR-008; depende de T020, T022, T023)
- [X] T025 [US1] Registrar el router de auth en `backend/src/main.py` (depende de T024, T013)
- [X] T026 [P] [US1] Crear el script de semilla del organizador inicial en `backend/scripts/seed_admin.py` (spec.md → Assumption "Cuentas de usuario")
- [X] T027 [P] [US1] Crear `AuthContext`/hook de sesión (`login`, `logout`, `currentUser`) en `frontend/src/features/auth/AuthContext.tsx` (depende de T014)
- [X] T028 [US1] Crear la página/formulario de login en `frontend/src/features/auth/LoginPage.tsx` (depende de T027)
- [X] T029 [US1] Crear el wrapper `ProtectedRoute` que exige rol en `frontend/src/features/auth/ProtectedRoute.tsx` (FR-003, FR-009; depende de T027)
- [X] T030 [P] [US1] Tests Vitest de `AuthContext` y `LoginPage` en `frontend/src/features/auth/__tests__/auth.test.tsx` (depende de T027, T028)

**Checkpoint**: User Story 1 completamente funcional y testeable de forma independiente — MVP de esta spec.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: cierre de la spec antes de abrir PR.

- [X] T031 [P] Ejecutar los escenarios de `quickstart.md` de punta a punta contra el entorno local
- [X] T032 [P] Documentar los pasos de setup en `backend/README.md` y `frontend/README.md`
- [X] T033 Endurecimiento de seguridad: confirmar que `backend/src/core/errors.py` nunca expone stack traces (FR-012) y que la cookie de `backend/src/auth/service.py` tiene `httpOnly`, `Secure`, `SameSite=None` (research.md §4 — `None`, no `Lax`, por el despliegue cross-domain)
- [X] T034 [P] Configurar el esqueleto de Playwright (`playwright.config.ts`) para el camino crítico único (crear liga → equipo → partido → clasificación) — sin escribir el test todavía: esos pasos viven en specs `002/003/005/008`, aún no implementadas (research.md §5)

---

## Phase 5: Despliegue (Vercel + Railway)

**Purpose**: dejar la aplicación publicada y accesible por URL. Es requisito
explícito del enunciado (`docs/actividad.md` → "Despliegue (DevOps) y Hosting:
Publicación en un entorno totalmente integrado y gratuito"), y habilita el
deploy automático que heredan las specs `002-011` sin volver a configurarlo.

- [X] T035 Crear el proyecto en Railway y provisionar el add-on de PostgreSQL; registrar la `DATABASE_URL` generada como variable de entorno del servicio backend, nunca en el repo (research.md §7, Principio VI)
- [X] T036 Configurar el despliegue del backend en Railway: comando de arranque `uvicorn src.main:app --host 0.0.0.0 --port $PORT` y ejecución de `alembic upgrade head` en el arranque/release, de modo que cada deploy aplique las migraciones pendientes (Principio V)
- [X] T037 [P] Crear el proyecto en Vercel apuntando a `frontend/`, con `VITE_API_URL` = URL pública del backend en Railway como variable de entorno de build
- [X] T038 Configurar `ALLOWED_ORIGINS` en Railway con el dominio real de Vercel y habilitar `allow_credentials=True` en el `CORSMiddleware` de `backend/src/core/config.py` — sin esto la cookie de sesión cross-domain no viaja (depende de T012, T037; research.md §4)
- [X] T039 Verificar en el entorno desplegado que la cookie `lf_session` se emite con `Secure` y `SameSite=None` sobre HTTPS y que el login funciona end-to-end entre el dominio de Vercel y el de Railway — es el escenario que `SameSite=Lax` habría roto y que no se puede validar en local con mismo origen (depende de T036, T037, T038)
- [X] T040 [P] Ejecutar el script de semilla del organizador contra la base de datos de producción, con una credencial inicial entregada fuera del repo (depende de T026, T035)
- [X] T041 Documentar en `README.md` las URLs públicas del frontend y del backend desplegados

**Checkpoint**: aplicación publicada y accesible; specs `002-011` heredan este pipeline sin reconfigurarlo.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias — arranca de inmediato
- **Foundational (Phase 2)**: depende de Setup — bloquea la User Story 1 y toda spec `002-011` posterior
- **User Story 1 (Phase 3)**: depende de Foundational; es la única historia de esta spec, así que no hay paralelismo entre historias
- **Polish (Phase 4)**: depende de que la User Story 1 esté completa
- **Despliegue (Phase 5)**: depende de la User Story 1 (necesita algo funcional que publicar). T035/T037 (crear los proyectos en Railway y Vercel) pueden adelantarse en paralelo desde el inicio, porque no dependen de código; T038/T039 sí requieren la app funcionando

### Dentro de la User Story 1

- Tests (T016-T017) se escriben antes que la implementación y deben fallar primero
- Modelos (T018) → migración (T019) → servicio (T022) → dependencias de rol (T023) → router (T024) → registro en `main.py` (T025)
- Frontend: cliente API (T014, Fase 2) → `AuthContext` (T027) → página de login (T028) y `ProtectedRoute` (T029) → tests (T030)

### Parallel Opportunities

- Setup: T003, T004, T005, T006, T007 en paralelo entre sí (T001-T002 primero, son su prerrequisito de estructura/dependencias)
- Foundational: T010, T011, T012 en paralelo (después de T008-T009); T014, T015 en paralelo (no dependen del backend)
- User Story 1: T016 y T017 en paralelo; T020 en paralelo con T021; T026 en paralelo con el resto una vez existe T022; T027 puede empezar en cuanto T014 esté listo, en paralelo con el trabajo de backend de la historia

---

## Parallel Example: User Story 1

```bash
# Tests, en paralelo:
Task: "Contract test de auth en backend/tests/contract/test_auth_contract.py"
Task: "Integration test de los 7 Acceptance Scenarios en backend/tests/integration/test_auth.py"

# Backend y frontend pueden avanzar en paralelo una vez lista la Fase 2:
Task: "AuthService en backend/src/auth/service.py"
Task: "AuthContext en frontend/src/features/auth/AuthContext.tsx"
```

---

## Implementation Strategy

### MVP = esta spec completa

Al no haber más de una User Story, el MVP de `001-fundacion-y-autenticacion`
es la spec entera: Setup → Foundational → User Story 1 → Polish. No hay un
recorte más pequeño que siga siendo útil, porque sin autenticación ninguna
otra spec puede completar sus propias pruebas de escritura.

### Entrega

1. Completar Fase 1 + Fase 2 (infraestructura) — habilita en paralelo el
   trabajo de `specs/002-*` en adelante aunque su propio `/speckit-plan`
   todavía no se haya corrido, porque ya existe `backend/src/core/` y
   `frontend/src/services/apiClient.ts` para que referencien.
2. Completar Fase 3 (User Story 1) — habilita las reglas de rol que
   `specs/006-registrar-resultado` y las demás specs de escritura necesitan.
3. Completar Fase 4 (Polish) y Fase 5 (Despliegue) → PR → mezclar a `main`
   antes de que cualquier otra spec empiece su `/speckit-plan` (`AGENTS.md`
   §5). Desplegar aquí y no al final significa que cada HU posterior se
   publica sola al mezclarse, en vez de acumular un despliegue grande y
   arriesgado el último día.

### Estrategia de equipo

Con una sola persona (recomendado para esta spec, ver conversación previa):
Fases 1-4 en el orden dado. Si se reparte entre dos personas: una toma
backend (T008-T026), otra frontend (T014-T015, T027-T030) en paralelo desde
que termina la Fase 2 backend compartida (T008-T013).

---

## Notes

- `[P]` = archivos distintos, sin dependencias pendientes entre sí
- `[US1]` traza cada tarea a la única User Story de esta spec
- Verificar que T016-T017 fallan antes de implementar T018 en adelante
- Commitear por tarea o por grupo lógico, no todo de una vez
- Al terminar la Fase 2, correr `quickstart.md` §Escenarios como humo antes de seguir con la Fase 3
- **SC-001/SC-002 son afirmaciones de todo el proyecto** ("sobre el catálogo
  completo de operaciones de todas las specs"). T017 solo verifica la porción
  que esta spec posee (`POST /users`) — se cierran incrementalmente conforme
  `specs/002-011` añaden sus propias pruebas de escritura con sesión/rol. No
  tratar "001 completa" como "SC-001/SC-002 cumplidos" todavía.
- `data-model.md` aplica `created_by` de forma consistente en toda entidad
  mutable (`User`, `League`, `Team`, `Player`, `Match`, `MatchLineup`,
  `MatchEvent`; `ResultCorrectionRequest` vía `requested_by`/`decided_by`) —
  decisión tomada en `/speckit-analyze` (hallazgo I1) para que FR-008 se
  cumpla igual en todas partes en vez de solo donde se implementó primero.
  `Session` es la única excepción documentada (no aplica el patrón).
