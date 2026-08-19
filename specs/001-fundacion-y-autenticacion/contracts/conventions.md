# Convenciones de API — LeagueFlow

Válidas para toda spec del proyecto (`specs/002-*` a `specs/011-*`). Ninguna
spec posterior redefine estas convenciones; solo añade sus propios endpoints
siguiendo este contrato (`AGENTS.md` §5, Principio III de la constitución).

## Base

- Base path: `/api/v1`.
- Formato: JSON (`Content-Type: application/json`) en request y response.
- Todas las fechas/horas: ISO 8601 UTC (`2026-08-18T15:30:00Z`).

## Autenticación

- Sesión vía cookie `httpOnly`, `Secure`, `SameSite=None`, nombre `lf_session`.
  `SameSite=None` es obligatorio (no `Lax`) porque frontend y backend viven en
  dominios distintos (Vercel/Railway) — con `Lax` la cookie no viaja en
  peticiones `fetch` cross-site. Ver `research.md` §4 y
  `specs/001-fundacion-y-autenticacion/data-model.md` (entidad `Session`).
- Las rutas de consulta (GET de calendario, clasificación, estadísticas,
  perfiles, búsqueda, dashboard) NUNCA requieren esta cookie.
- Toda ruta de escritura (POST/PUT/PATCH/DELETE) la requiere; sin ella
  responde `401`. Con ella pero rol insuficiente, responde `403`.

## Envelope de error

Toda respuesta de error, cualquier status `4xx`/`5xx`, usa esta forma fija:

```json
{
  "error": {
    "code": "team_name_duplicate",
    "message": "Ya existe un equipo con ese nombre en esta liga.",
    "field": "name"
  }
}
```

- `code`: slug estable en `snake_case`, identifica la regla incumplida
  (mapea 1:1 a un FR de la spec correspondiente). Consumible por el frontend
  sin parsear `message`.
- `message`: texto en español, listo para mostrar al usuario (FR-011/FR-012
  de `specs/001-fundacion-y-autenticacion`).
- `field`: nombre del campo del payload que causó el error, o `null` si no
  aplica (p. ej. conflicto entre dos recursos).

## Códigos de estado HTTP

| Status | Cuándo |
|---|---|
| 200 / 201 | éxito (200 lectura o escritura sin creación; 201 creación de recurso) |
| 400 | payload inválido (falla de validación de schema) |
| 401 | falta sesión en una ruta que la requiere |
| 403 | sesión válida, rol insuficiente |
| 404 | recurso no existe (o pertenece a otra liga — nunca se filtra existencia cruzada) |
| 409 | conflicto de regla de negocio (duplicados, transición de estado inválida) |
| 500 | error inesperado — `message` genérico, nunca stack trace (FR-012, Estándar de Seguridad de la constitución) |

## Paginación (cuando aplique)

Query params `page` (1-indexed, default 1) y `page_size` (default 20, máximo
100). Response envuelve la lista:

```json
{ "items": [...], "page": 1, "page_size": 20, "total": 57 }
```

## Autoría y auditoría

Todo recurso creado o modificado por una escritura expone `created_by` /
`updated_by` (id de `User`) cuando la spec correspondiente lo requiere
(ver FR-008 de esta spec). El cliente nunca envía estos campos; el servidor
los deriva de la sesión.
