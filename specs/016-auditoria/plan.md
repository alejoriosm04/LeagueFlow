# Implementation Plan: Auditoría de operaciones administrativas

**Branch**: `016-auditoria` | **Date**: 2026-08-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/016-auditoria/spec.md`

**Nota (AGENTS.md §5)**: esta spec no re-decide stack ni remodela el modelo
de dominio. Stack, convenciones de API y `User`/`Session` están fijados en
`specs/001-fundacion-y-autenticacion/plan.md` y `data-model.md`; este plan
solo documenta lo que **añade**: una entidad de auditoría, la captura
transversal que la escribe y el endpoint de solo lectura que la expone.

## Summary

Historia transversal de observabilidad, sin reglas de negocio propias.
Backend: un middleware ASGI genérico (no `Depends`, no toca routers de otros
dominios) intercepta toda petición `POST/PUT/PATCH/DELETE` que termina en
`2xx` y escribe una fila en `audit_logs` (`backend/src/audit/`) con actor,
método, destino, resultado y fecha — nunca el cuerpo de la petición ni de la
respuesta. Un router propio, `GET /admin/audit-log`, expone ese historial en
orden cronológico inverso, protegido por la misma dependencia de rol que ya
usan los endpoints de escritura (`requiere_rol("organizador")`). Frontend:
página `/admin/audit-log`, visible solo a organizador, que reutiliza los
mismos componentes de listado/paginación que el resto de la app.

## Technical Context

**Language/Version**: Python 3.12 (backend) · TypeScript 5.x + React 18
(frontend) — heredado de `specs/001-*`, sin cambios.

**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (async), Alembic — sin
dependencias nuevas. La captura usa el protocolo ASGI puro (`app.add_middleware`
con una clase `__call__(self, scope, receive, send)`), no
`Starlette.BaseHTTPMiddleware` — ver `research.md` §1.

**Storage**: PostgreSQL 16 (heredado). Tabla nueva: `audit_logs`.

**Testing**: `pytest` + `httpx.AsyncClient` (`tests/contract/test_audit_contract.py`,
`tests/integration/test_audit.py`) · `Vitest` + React Testing Library
(`frontend/src/features/audit/__tests__/audit.test.tsx`).

**Target Platform**: sin cambios respecto a `specs/001-*` (Railway / Vercel).

**Project Type**: web (backend + frontend), heredado.

**Performance Goals**: la captura no debe añadir latencia perceptible a las
escrituras existentes — la escritura del registro de auditoría ocurre
después de que la respuesta ya se envió al cliente (`research.md` §4), así
que nunca puede ser la causa de que una escritura exitosa se sienta más
lenta.

**Constraints**: FR-003 — un registro nunca contiene el cuerpo de la
petición ni de la respuesta; el middleware ASGI solo puede inspeccionar
método, ruta y código de estado, nunca leer ni reenviar los bytes del body
(`research.md` §1). El middleware abre su propia sesión de BD
(`SessionLocal()` directo, no `Depends(get_db)`) porque corre fuera del
sistema de inyección de dependencias de FastAPI (`research.md` §2).

**Scale/Scope**: un único endpoint de lectura nuevo, una tabla nueva, un
middleware transversal. Ninguna spec del bloque paralelo (`013-017`) toca
este mecanismo (`spec.md`, Dependencies).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio / regla | Estado | Cómo se cumple |
|---|---|---|
| I. La Especificación Manda | PASS | Cada decisión de este plan traza a un FR de `spec.md` (ver `research.md`) |
| II. Toda Regla de Negocio se Prueba | PASS | La única "regla de negocio" es "solo 2xx en métodos de escritura, sin body" (FR-001/002/003); cubierta en `tests/integration/test_audit.py` |
| III. Contratos de API Explícitos | PASS | `contracts/audit.openapi.yaml` documenta `GET /admin/audit-log`; la captura en sí no es un contrato consumido por el cliente (no se llama directamente) |
| IV. No Romper lo que ya Funciona | PASS | El middleware es aditivo: no modifica ningún router existente; su sesión de BD es independiente de la de cada request, así que un fallo de auditoría no puede tumbar ni revertir la operación que audita (`research.md` §4) |
| V. Migraciones Versionadas | PASS | Una migración nueva para `audit_logs`, `down_revision` apuntando al head confirmado con `uv run alembic heads` (`research.md` §10) |
| VI. Cero Secretos en el Repositorio | PASS | No introduce configuración ni secretos nuevos |
| VII. Código de IA con la Misma Vara | PASS | Regla de proceso, no de plan |
| VIII. Entregabilidad Independiente por Dominio | PASS | `audit` es un módulo nuevo, propio, que solo lee de `users` (vía FK de solo lectura) — no reescribe modelos de `leagues/teams/players/matches/statistics` ni depende de sus internals |
| Arquitectura: monolito modular | PASS | Un middleware más en el mismo backend FastAPI, ninguna pieza nueva desplegable |
| Estándares de Seguridad Obligatorios | PASS | `GET /admin/audit-log` exige rol `organizador` (`requiere_rol`, ya existente); el registro nunca persiste payloads (evita exponer credenciales/datos sensibles vía el propio mecanismo de auditoría) |

Sin violaciones. **Complexity Tracking no aplica** (tabla vacía a propósito).

*Re-check post Phase 1*: `data-model.md` añade una sola entidad
(`AuditLogEntry`), sin tabla editable ni derivación de negocio que tensione
la "Regla de Derivación de Estadísticas" (no aplica a esta historia).
`contracts/audit.openapi.yaml` no introduce convenciones nuevas — reutiliza
el envelope de error y el formato de paginación de
`specs/001-fundacion-y-autenticacion/contracts/conventions.md` sin cambios.
**PASS confirmado.**

## Project Structure

### Documentation (this feature)

```text
specs/016-auditoria/
├── plan.md              # este archivo
├── research.md          # Phase 0 — decisiones de diseño del middleware y el endpoint
├── data-model.md         # Phase 1 — entidad añadida (AuditLogEntry)
├── contracts/
│   └── audit.openapi.yaml  # GET /admin/audit-log
├── quickstart.md         # Phase 1 — validación end-to-end
└── tasks.md              # Phase 2 (/speckit-tasks — aún no generado)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── audit/                  # NUEVO — esta spec
│   │   ├── __init__.py
│   │   ├── models.py            # AuditLogEntry (tabla audit_logs)
│   │   ├── schemas.py           # AuditLogEntry (Pydantic), PaginatedAuditLog
│   │   ├── service.py           # AuditService: registrar() y listar()
│   │   ├── middleware.py        # AuditMiddleware — ASGI puro, ver research.md §1
│   │   └── router.py            # GET /admin/audit-log
│   ├── auth/                    # sin cambios — se REUTILIZA requiere_rol y
│   │                             #   AuthService.obtener_sesion_valida
│   ├── core/                    # sin cambios — se REUTILIZA SessionLocal (no get_db)
│   ├── leagues/ teams/ players/ matches/ statistics/  # sin cambios, ninguno se toca
│   └── main.py                  # MODIFICADO: + app.add_middleware(AuditMiddleware)
│                                 #   junto al CORSMiddleware existente,
│                                 #   + app.include_router(audit_router, prefix="/api/v1")
├── alembic/
│   ├── env.py                    # MODIFICADO: + import src.audit.models para autogenerate
│   └── versions/
│       └── <rev>_crear_tabla_audit_logs.py   # NUEVO, down_revision = head confirmado (research.md §10)
└── tests/
    ├── contract/
    │   └── test_audit_contract.py    # NUEVO — valida contracts/audit.openapi.yaml
    ├── integration/
    │   └── test_audit.py             # NUEVO — FR-001 a FR-007, escenarios de spec.md
    └── unit/                          # sin nuevos casos — no hay cálculo propio que unitear

frontend/
├── src/
│   ├── features/
│   │   └── audit/                # NUEVO — esta spec
│   │       ├── api.ts             # cliente HTTP: auditApi.listar()
│   │       ├── AuditLogPage.tsx   # página /admin/audit-log
│   │       ├── AuditLogPage.module.css
│   │       └── __tests__/
│   │           └── audit.test.tsx
│   └── routes.tsx                # MODIFICADO: + <Route path="/admin/audit-log" ...>
│                                  #   dentro de <ProtectedRoute rol="organizador">
└── tests/                        # (junto a cada componente, Vitest — sin carpeta aparte)
```

**Structure Decision**: se reutiliza literalmente la estructura "Web
application" fijada en `specs/001-*` (`backend/src/<dominio>/` +
`frontend/src/features/<dominio>/`). `audit` se suma como un dominio más de
`backend/src/`, exactamente como pide el enunciado ("tabla propia de
`backend/src/audit/`, sin tocar routers de otros dominios"): ningún archivo
fuera de `backend/src/audit/`, `backend/src/main.py`, `backend/alembic/`,
`frontend/src/features/audit/` y `frontend/src/routes.tsx` se modifica.

## Complexity Tracking

*Sin violaciones que justificar — tabla vacía a propósito.*
