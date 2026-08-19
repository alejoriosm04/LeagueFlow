# Data Model: Registrar equipos en una liga

**Feature**: `003-registrar-equipos` · **Date**: 2026-08-19

La entidad `Team` ya está definida en
`specs/001-fundacion-y-autenticacion/data-model.md`, el modelo de dominio
compartido. **Este documento no la redefine** (`AGENTS.md` §5): registra solo
lo que esta HU añade.

## Team — lo que aporta esta spec

Campos: ver `specs/001-fundacion-y-autenticacion/data-model.md` §Team
(`id`, `league_id`, `name`, `crest_url`, `colors`, `status`, `created_by`,
`created_at`).

Añadidos de esta spec:

| Elemento | Detalle |
|---|---|
| Migración Alembic | Crea la tabla `teams` con FK a `leagues` |
| Índice único | `UNIQUE (league_id, lower(trim(name)))` — el mismo nombre es válido en ligas distintas (FR-002) |
| `status` | `active` por defecto; `inactive` es borrado lógico (FR-005), con el alcance definido en `research.md` §3 |
| `crest_url` | URL `https` absoluta, validada por formato; el recurso no se descarga (`research.md` §1) |
| `created_by` | Poblado por el servidor desde la sesión, nunca desde el payload (FR-008 de `specs/001-*`) |
| FK `league_id` | `ON DELETE RESTRICT` — una liga con equipos no se borra por accidente |

## Consultas que esta spec debe soportar

- Equipos activos de una liga (listado y selector de alta).
- Equipo por id, incluido si está `inactive` (para el historial, `research.md` §3).

## Lo que NO cambia

Ninguna otra entidad se toca. `Player` llega en `specs/004-*` y ya tiene su
`team_id` previsto en el modelo de `001`.
