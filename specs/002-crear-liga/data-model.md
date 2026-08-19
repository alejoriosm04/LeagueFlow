# Data Model: Crear una liga

**Feature**: `002-crear-liga` · **Date**: 2026-08-19

La entidad `League` ya está definida en
`specs/001-fundacion-y-autenticacion/data-model.md`, que es el modelo de
dominio compartido del proyecto. **Este documento no la redefine**
(`AGENTS.md` §5): registra únicamente lo que esta HU añade al implementarla.

## League — lo que aporta esta spec

Campos: ver `specs/001-fundacion-y-autenticacion/data-model.md` §League
(`id`, `name`, `season`, `description`, `created_by`, `created_at`).

Añadidos de esta spec:

| Elemento | Detalle |
|---|---|
| Migración Alembic | Crea la tabla `leagues`. Es la primera migración después de `users`/`sessions` (`specs/001-*`) |
| Índice único | `UNIQUE (lower(trim(name)), lower(trim(season)))` — unicidad insensible a mayúsculas y espacios (`research.md` §2) |
| Normalización | `name` y `season` se guardan con espacios recortados y colapsados; se preserva la capitalización original para mostrar |
| `created_by` | Poblado por el servidor desde la sesión activa, nunca desde el payload (FR-008 de `specs/001-*`) |

## Lo que NO cambia

Ninguna otra entidad del modelo compartido se toca. `Team`, `Player`, `Match`
y las demás llegan en sus propias specs (`003` en adelante) y ya tienen su
`league_id` previsto en el modelo de `001`.
