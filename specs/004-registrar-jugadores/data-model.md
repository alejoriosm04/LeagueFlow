# Data Model: Registrar jugadores en un equipo

**Feature**: `004-registrar-jugadores` · **Date**: 2026-08-19

La entidad `Player` ya está definida en
`specs/001-fundacion-y-autenticacion/data-model.md`, el modelo de dominio
compartido. **Este documento no la redefine** (`AGENTS.md` §5): registra solo
lo que esta HU añade.

## Player — lo que aporta esta spec

Campos: ver `specs/001-fundacion-y-autenticacion/data-model.md` §Player
(`id`, `team_id`, `name`, `number`, `position`, `status`, `created_by`,
`created_at`).

Añadidos de esta spec:

| Elemento | Detalle |
|---|---|
| Migración Alembic | Crea la tabla `players` con FK a `teams` |
| Índice único parcial | `UNIQUE (team_id, number) WHERE number IS NOT NULL` — dorsal duplicado solo cuando está informado (FR-003); varios sin dorsal son válidos (`research.md` §1) |
| `number` | Entero 1–99 o `null` (`research.md` §1) |
| `position` | Texto libre ≤ 40 caracteres o `null` (`research.md` §2) |
| `status` | `active` por defecto; `inactive` es borrado lógico (FR-005), con el alcance definido en `research.md` §3 |
| `created_by` | Poblado por el servidor desde la sesión, nunca desde el payload (FR-008 de `specs/001-*`) |
| FK `team_id` | `ON DELETE RESTRICT` — un equipo con jugadores no se borra por accidente; `team_id` inmutable tras creación (Assumption de traspaso) |

## Consultas que esta spec debe soportar

- Jugadores activos de un equipo (plantilla y selectores de alta).
- Jugador por id, incluido si está `inactive` (para el historial, `research.md` §3).

## Lo que NO cambia

Ninguna otra entidad se toca. `Match` / alineaciones / eventos llegan en
specs posteriores y ya referencian `player_id` en el modelo de `001`.
