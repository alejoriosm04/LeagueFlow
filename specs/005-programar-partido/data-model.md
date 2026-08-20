# Data Model: Programar un partido

**Feature**: `005-programar-partido` · **Date**: 2026-08-19

La entidad `Match` ya está definida en
`specs/001-fundacion-y-autenticacion/data-model.md`, el modelo de dominio
compartido. **Este documento no la redefine** (`AGENTS.md` §5): registra solo
lo que esta HU añade.

## Match — lo que aporta esta spec

Campos: ver `specs/001-fundacion-y-autenticacion/data-model.md` §Match
(`id`, `league_id`, `home_team_id`, `away_team_id`, `scheduled_at`, `status`,
`home_score`, `away_score`, `created_by`, `created_at`, `updated_at`).

Añadidos de esta spec:

| Elemento | Detalle |
|---|---|
| Migración Alembic | Crea la tabla `matches` con FKs a `leagues` y `teams` |
| `status` | Default `scheduled`; el enum admite `in_progress`, `finished`, `cancelled` (FR-004), pero esta HU solo produce `scheduled` |
| `home_score` / `away_score` | Columnas nullable; siempre `null` al crear (`research.md` §4) |
| `scheduled_at` | `timestamptz` obligatorio; pasado permitido (`research.md` §1) |
| Check de negocio | `home_team_id != away_team_id` (FR-002); validado en servicio (+ IntegrityError si se añade CHECK en BD) |
| `created_by` | Poblado por el servidor desde la sesión (FR-008 de `specs/001-*`) |
| FKs | `ON DELETE RESTRICT` en `league_id`, `home_team_id`, `away_team_id` |

## Consultas que esta spec debe soportar

- Partidos de una liga ordenados por `scheduled_at` ascendente (listado,
  `research.md` §2).
- Partido por id (FR-005).

## Lo que NO cambia

Ninguna otra entidad se toca. Resultados, correcciones, alineaciones y eventos
llegan en specs posteriores.
