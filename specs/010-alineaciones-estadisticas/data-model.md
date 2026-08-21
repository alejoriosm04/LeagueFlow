# Data Model: Alineaciones y estadisticas de jugadores

**Feature**: `010-alineaciones-estadisticas` · **Date**: 2026-08-20

Esta HU agrega `MatchLineup` como persistencia nueva y define
`PlayerStatistics` como vista derivada de solo lectura.

```text
Match (existente) ──< MatchLineup >── Player (existente)
Match (existente) ──< MatchEvent (existente desde 009) >── Player

PlayerStatistics = derivacion en lectura de MatchLineup + MatchEvent
```

## MatchLineup — entidad nueva (persistida)

Tabla `match_lineups` (grano: una fila por jugador participante en un partido).

| Campo | Tipo | Reglas |
|---|---|---|
| `id` | UUID | PK |
| `match_id` | UUID (FK -> `matches`, RESTRICT) | obligatorio |
| `team_id` | UUID (FK -> `teams`, RESTRICT) | obligatorio; debe ser home o away del partido |
| `player_id` | UUID (FK -> `players`, RESTRICT) | obligatorio; debe pertenecer a `team_id` |
| `created_by` | UUID (FK -> `users`, RESTRICT) | operador/organizador que registro o corrigio |
| `created_at` | timestamp | obligatorio |
| `updated_at` | timestamp | obligatorio |

### Constraints e indices

| Nombre | Tipo | Motivo |
|---|---|---|
| `uq_match_lineups_match_player` | UNIQUE (`match_id`, `player_id`) | evita duplicar un jugador en la misma alineacion |
| `ix_match_lineups_match_team` | indice (`match_id`, `team_id`) | lectura por equipo local/visitante |
| `ix_match_lineups_player` | indice (`player_id`) | calculo de partidos jugados por jugador |

Validaciones de negocio (en servicio):
- `player.team_id == team_id`
- `team_id in {match.home_team_id, match.away_team_id}`
- si se corrige alineacion y se excluye un jugador con goles ya registrados en
  ese partido, rechazar `409 lineup_conflicts_with_events` (FR-003)

## PlayerStatistics — vista derivada (no persistida)

Objeto de lectura por jugador.

| Campo | Tipo | Regla de calculo |
|---|---|---|
| `player_id` | UUID | identificador del jugador consultado |
| `player_name` | string | `Player.name` |
| `team_id` | UUID | `Player.team_id` |
| `team_name` | string | `Team.name` |
| `goals` | integer >= 0 | `COUNT(match_events)` donde `type='GOAL'` y `player_id` |
| `matches_played` | integer >= 0 | `COUNT(DISTINCT match_id)` en `match_lineups` del jugador, filtrando `matches.status='finished'` |

Propiedades importantes:
- Nunca editable por endpoint (FR-008).
- Recalculo en cada lectura: refleja altas/bajas de eventos y correcciones de
  alineacion sin tareas de sincronizacion.

## Tabla de goleadores — proyeccion derivada

Consulta por liga con orden determinista:
1. `goals` DESC
2. `player_name` ASC (desempate estable)
3. `player_id` ASC (desempate tecnico final)

Campos de salida por fila: `rank`, `player_id`, `player_name`, `team_name`,
`goals`, `matches_played`, `is_top_scorer`.

`is_top_scorer = true` cuando `goals == max(goals)` en la liga; permite
identificacion inmediata en UI (SC-002).

## Estado explicito de alineacion en ficha de partido

Campo derivado en lectura:
- `lineup_status = "registered"` si existe al menos una fila en `match_lineups`
  para el partido.
- `lineup_status = "missing"` si no existe ninguna fila, incluso con
  `match.status = 'finished'` (edge case obligatorio).

## Migracion

Una migracion nueva crea solo `match_lineups` con sus FKs, indices y
unicidad. Mantener la regla de AGENTS.md: eliminar del autogenerado cualquier
`drop/create` espurio de indices funcionales heredados de `leagues` o `teams`.
