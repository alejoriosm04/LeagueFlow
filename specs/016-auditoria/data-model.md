# Data Model: Auditoría de operaciones administrativas

**Feature**: `016-auditoria` · **Date**: 2026-08-21

Esta spec **añade** una entidad sobre el modelo de dominio compartido de
`specs/001-fundacion-y-autenticacion/data-model.md`; no lo redefine
(`AGENTS.md` §5). Convenciones heredadas: todo id es UUID; todo registro
tiene `created_at`.

## Diagrama de relaciones (incremento sobre el modelo compartido)

```text
User (organizador/operador)          [specs/001-*, sin cambios]
  │ referenciado como actor de (opcional)
  ▼
AuditLogEntry                        [NUEVO — esta spec]
```

`AuditLogEntry` no participa de `League/Team/Player/Match/MatchEvent`: no
tiene FK hacia ellos. Su único vínculo con el modelo existente es la
referencia opcional a `User` (ver `research.md` §7 sobre por qué es
opcional y por qué se snapshotea el username).

---

## AuditLogEntry

Entrada que documenta una operación de escritura exitosa, escrita de forma
automática por `AuditMiddleware` (nunca por un router de negocio). Es la
única entidad de la spec — corresponde 1:1 a la Key Entity "Registro de
auditoría" de `spec.md`.

| Campo | Tipo | Reglas |
|---|---|---|
| id | UUID | PK |
| method | string(10) | obligatorio; uno de `POST`, `PUT`, `PATCH`, `DELETE` (FR-001, FR-002) — es la "acción" de la spec |
| path | string(255) | obligatorio; ruta exacta de la petición, sin query string (FR-003) — es el "destino" de la spec |
| status_code | integer | obligatorio; `200 <= status_code < 300` siempre (solo se escribe en éxito — clarificación de `spec.md`) — es el "resultado" de la spec |
| actor_id | UUID nullable (FK → `users.id`, `ON DELETE SET NULL`) | `null` únicamente cuando el actor no es determinable (p. ej. `POST /auth/login`, FR-004) |
| actor_username | string nullable | snapshot de `Usuario.username` en el momento del registro, no un join en lectura (`research.md` §7); `null` en el mismo caso que `actor_id` |
| created_at | timestamp (UTC) | obligatorio, `server_default=now()` — es la "fecha" de la spec; nunca se actualiza (la entidad es inmutable, sin `updated_at`) |

**Validaciones**:
- Ninguna regla de negocio adicional a nivel de fila — el dato ya viene
  saneado por lo que el propio middleware puede observar (método real de la
  petición, status real de la respuesta). No hay input de usuario que
  validar (FR-003 excluye justamente el único campo con contenido libre: el
  body).
- La tabla nunca se actualiza ni se borra vía API — es un log de solo
  inserción y lectura. No hay endpoint de edición ni de borrado (fuera de
  alcance, ver `spec.md` §Out of Scope: purga/rotación).

**Índices**:
- `ix_audit_logs_created_at` sobre `created_at`, no único, no funcional
  (`research.md` §11) — soporta el orden "más reciente primero" de FR-005 a
  medida que la tabla crece.

**Sin state transitions**: `AuditLogEntry` es un hecho inmutable una vez
escrito; no tiene estados ni transiciones.

**Nota sobre `actor_id` y borrado de usuarios**: hoy no existe ningún
endpoint que borre un `User` (`specs/001-*/data-model.md` solo define
`status: active/inactive`), así que `ON DELETE SET NULL` no se ejerce en la
práctica todavía; se declara de todos modos como la política correcta si
esa capacidad se añade en el futuro, en vez de dejar la FK sin política
explícita.
