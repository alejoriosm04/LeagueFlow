# Quickstart: Auditoría de operaciones administrativas

**Feature**: `016-auditoria` · **Date**: 2026-08-21

Valida de punta a punta los escenarios de aceptación de `spec.md` (User
Story 1 y 2). Requiere el backend corriendo con la migración de esta spec
aplicada y un usuario `organizador` (y, para el escenario 5, uno `operador`)
— ver `specs/001-fundacion-y-autenticacion/quickstart.md` para cómo sembrar
esas cuentas si el entorno no las tiene todavía.

## Prerrequisitos

```bash
cd backend
uv run alembic upgrade head       # aplica la migración de audit_logs de esta spec
uv run uvicorn src.main:app --reload
```

Un cliente HTTP con soporte de cookies (`httpx.AsyncClient` en los tests,
o `curl -c/-b cookies.txt` manualmente).

## Escenario 1 — Una escritura exitosa queda registrada (US1, AC1)

```bash
# 1. Login como organizador (guarda la cookie de sesión)
curl -c cookies.txt -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "<seed_admin_username>", "password": "<seed_admin_password>"}'

# 2. Una escritura cualquiera — crear una liga
curl -b cookies.txt -X POST http://localhost:8000/api/v1/leagues \
  -H "Content-Type: application/json" \
  -d '{"name": "Liga Quickstart", "season": "2026"}'

# 3. Consultar el historial
curl -b cookies.txt http://localhost:8000/api/v1/admin/audit-log
```

**Esperado**: el `items[0]` de la respuesta del paso 3 tiene
`method: "POST"`, `path` conteniendo `/leagues`, `status_code: 201`,
`actor_username` con el username del organizador que hizo login, y
`created_at` reciente. Es la entrada más reciente porque el orden es
`created_at DESC` (FR-005).

## Escenario 2 — Una lectura NO se registra (US1, AC2)

```bash
curl -b cookies.txt http://localhost:8000/api/v1/leagues   # GET, lectura
curl -b cookies.txt http://localhost:8000/api/v1/admin/audit-log
```

**Esperado**: el `total` del historial no cambia entre el estado anterior y
posterior a la petición `GET /leagues` — ninguna entrada nueva con
`method: "GET"` aparece jamás en el historial (FR-002).

## Escenario 3 — Una escritura que falla NO se registra

```bash
# Repetir la MISMA liga del escenario 1 → 409 por nombre duplicado
curl -b cookies.txt -X POST http://localhost:8000/api/v1/leagues \
  -H "Content-Type: application/json" \
  -d '{"name": "Liga Quickstart", "season": "2026"}'

curl -b cookies.txt http://localhost:8000/api/v1/admin/audit-log
```

**Esperado**: la petición anterior responde `409`; el `total` del historial
sigue igual al del escenario 1 — no se agregó una entrada para el intento
fallido (clarificación de `spec.md`: solo escrituras exitosas).

## Escenario 4 — El registro nunca contiene el body (US1, AC3)

Inspección de schema, no de una petición puntual: `AuditLogEntry`
(`data-model.md`) no tiene ninguna columna capaz de contener el body de una
petición o respuesta — no hay `payload`, `request_body`, `response_body` ni
similar. Verificable revisando la migración
(`backend/alembic/versions/<rev>_crear_tabla_audit_logs.py`) y confirmando
que las únicas columnas de texto libre son `path` (una ruta, acotada por
`String(255)`) y `actor_username` (un username existente, no contenido
arbitrario del cliente).

## Escenario 5 — Consultar el historial (US2, AC1/AC2/AC3)

```bash
# Como organizador (cookie del escenario 1): 200, orden created_at DESC
curl -b cookies.txt http://localhost:8000/api/v1/admin/audit-log

# Como operador (otra sesión, rol distinto): 403
curl -c cookies_operador.txt -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" -d '{"username": "<operador>", "password": "<pwd>"}'
curl -b cookies_operador.txt http://localhost:8000/api/v1/admin/audit-log

# Sin sesión: 401
curl http://localhost:8000/api/v1/admin/audit-log
```

**Esperado**: `200` con `items` ordenados por `created_at` descendente para
el organizador; `403` (`insufficient_role`) para el operador; `401`
(`not_authenticated`) sin cookie — FR-006, AC2/AC3 de US2.

## Frontend

```bash
cd frontend
npm run dev
```

Navegar a `/admin/audit-log` autenticado como organizador: la página lista
el historial (reutilizando `TituloDePantalla`, `TablaDeDatos`,
`EstadoCarga`/`EstadoError`/`EstadoVacio` del catálogo de
`specs/012-identidad-visual`, ver `plan.md`). Sin sesión o con rol
`operador`, `ProtectedRoute` bloquea el acceso igual que en `/leagues/new`
(guarda de usabilidad — la autorización real la impone el 401/403 del
backend, `frontend/src/features/auth/ProtectedRoute.tsx`).

## Pruebas automatizadas equivalentes

- `backend/tests/contract/test_audit_contract.py` — valida
  `contracts/audit.openapi.yaml` (schema de `GET /admin/audit-log`, 401/403).
- `backend/tests/integration/test_audit.py` — los 5 escenarios de arriba,
  más el caso de actor no determinable (FR-004: `POST /auth/login` exitoso
  produce una entrada con `actor_id: null`).
- `frontend/src/features/audit/__tests__/audit.test.tsx` — render de la
  página en sus tres estados (cargando/error/datos) y el bloqueo de
  `ProtectedRoute` para quien no es organizador.
