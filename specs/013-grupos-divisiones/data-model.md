# Data Model: Divisiones (grupos) dentro de una liga

**Feature**: `013-grupos-divisiones` · **Date**: 2026-08-22

Este documento **no redefine** el modelo compartido de
`specs/001-fundacion-y-autenticacion/data-model.md` (`AGENTS.md` §5): registra
solo lo que esta HU añade. `League`, `Team`, `User` y el resto no se modifican.

## LeagueGroup — entidad nueva

Tabla `groups`. Una división de una liga.

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID PK | hereda `UUIDPrimaryKey` de `core/models_base.py` |
| `league_id` | UUID FK → `leagues.id` | `ON DELETE RESTRICT`; una liga con grupos no se borra por accidente |
| `name` | String(120) NOT NULL | FR-001 |
| `position` | Integer NULL | orden de presentación; sin regla de negocio (`research.md` §5) |
| `created_by` | UUID FK → `users.id` | poblado por el servidor desde la sesión (patrón `001`) |
| `created_at` / `updated_at` | timestamps | hereda `TimestampCreated`/`TimestampUpdated` |

Índice único (FR-002):

```text
ix_groups_unique_league_name = UNIQUE (league_id, lower(trim(name)))
```

## GroupTeamMembership — entidad nueva

Tabla `group_memberships`. Pertenencia de un equipo a un grupo.

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID PK | |
| `group_id` | UUID FK → `groups.id` | `ON DELETE CASCADE`: al borrar el grupo se borran sus membresías (FR-004) |
| `team_id` | UUID FK → `teams.id` | `ON DELETE RESTRICT`: no se borra un equipo que está en un grupo |
| `created_by` | UUID FK → `users.id` | patrón `001` |
| `created_at` | timestamp | |

Índices:

```text
uq_group_memberships_team = UNIQUE (team_id)   # "a lo sumo un grupo por liga" (FR-007, research.md §2)
ix_group_memberships_group = INDEX (group_id)  # listar los equipos de un grupo
```

## Relaciones

- `League 1 ── * LeagueGroup` (una liga tiene cero o más grupos).
- `LeagueGroup 1 ── * GroupTeamMembership ── * Team` (la composición).
- `Team * ── 1 GroupTeamMembership` como máximo (un equipo, a lo sumo un grupo).

## Reglas de validación (servicio)

| Regla | FR | Error |
|---|---|---|
| La liga debe existir | FR-001/FR-009 | `404 league_not_found` |
| Nombre normalizado único por liga | FR-002 | `409 group_name_duplicate` (field `name`) |
| El grupo debe existir | FR-003/FR-004/FR-005 | `404 group_not_found` |
| El equipo debe existir | FR-005 | `404 team_not_found` |
| El equipo debe ser de la liga del grupo | FR-008 | `404 team_not_found_in_league` |
| El equipo no debe estar ya en un grupo | FR-007 | `409 team_already_in_group` |
| El equipo debe estar activo | FR-011 | `409 team_inactive` |

## Consultas que esta spec debe soportar

- Listar los grupos de una liga con su composición (incluye equipos inactivos
  que ya son miembros — FR-012).
- Obtener un grupo por id (para renombrar/eliminar/asignar).

## Lo que NO cambia

Ninguna entidad existente se toca. `teams` y `leagues` se leen únicamente por
sus servicios (`TeamService.obtener_equipo`, `TeamService.listar_por_liga`,
`LeagueService.obtener_liga`), nunca importando sus modelos (Principio VIII).
