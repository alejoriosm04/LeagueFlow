# Data Model: Registrar goles por jugador

**Feature**: `009-registrar-goles` · **Date**: 2026-08-20

Esta HU **implementa** `MatchEvent`, ya declarada en
`specs/001-fundacion-y-autenticacion/data-model.md §MatchEvent`. No redefine
ninguna entidad existente ni añade campos a `Match`, `Player` o `Team`.

```text
Match (existente) ──< MatchEvent >── Player (existente)
                           │
                           └── Team (existente, derivado de Player)
```

## MatchEvent — entidad nueva (persistida)

Tabla `match_events`.

| Campo | Tipo | Reglas |
|---|---|---|
| `id` | UUID | PK |
| `match_id` | UUID (FK → `matches`, RESTRICT) | obligatorio |
| `type` | string(20) | obligatorio; en esta versión solo `GOAL` (FR-004) |
| `player_id` | UUID (FK → `players`, RESTRICT) | obligatorio |
| `team_id` | UUID (FK → `teams`, RESTRICT) | obligatorio; derivado de `Player.team_id` (research.md §4) |
| `minute` | integer | obligatorio, `>= 0` |
| `created_by` | UUID (FK → `users`, RESTRICT) | operador u organizador que lo registró (FR-006) |
| `created_at` | timestamp | |

### Constraints e índices

| Nombre | Tipo | Motivo |
|---|---|---|
| `ck_match_events_minute_nonnegative` | CHECK `minute >= 0` | 001 §MatchEvent |
| `ck_match_events_type_supported` | CHECK `type IN ('GOAL')` | FR-004: hoy solo gol; ampliar el enum es un `ALTER` de una línea, no un rediseño |
| `ix_match_events_match_minute` | índice `(match_id, minute)` | el listado por partido es la consulta caliente y 010 derivará de ella |

**Por qué `type` es `String(20)` con CHECK y no un `ENUM` de PostgreSQL**:
añadir un valor a un tipo `ENUM` exige `ALTER TYPE` y bloquea; sustituir un
CHECK es una migración trivial. FR-004 pide justamente que crecer no duela.

**No se añade unicidad**: dos goles del mismo jugador en el mismo minuto son
legítimos, así que ninguna combinación de campos es única.

## Reglas de validación (dónde vive cada FR)

| Regla | Origen | Dónde se comprueba |
|---|---|---|
| El jugador pertenece a uno de los dos equipos del partido | FR-002 | servicio, antes de insertar; `409 player_not_in_match` |
| Si el partido tiene alineación, el jugador figura en ella | FR-003 | servicio, vía el puerto `jugadores_alineados` (research.md §2); `409 player_not_in_lineup` |
| El partido admite eventos (`finished` o `in_progress`) | research.md §3 | servicio; `409 match_not_playable` |
| `minute >= 0` | 001 §MatchEvent | schema Pydantic **y** CHECK en base |
| Solo operador u organizador registra | FR-006 | dependencia `requiere_rol` del router |
| `type` soportado | FR-004 | schema Pydantic **y** CHECK en base |

## Consistencia con el marcador (FR-005)

No es una columna: se calcula al leer, igual que la clasificación de 008.

```text
home_goals_recorded = count(MatchEvent WHERE type=GOAL AND team_id = match.home_team_id)
away_goals_recorded = count(MatchEvent WHERE type=GOAL AND team_id = match.away_team_id)
matches_official    = (home_goals_recorded, away_goals_recorded)
                      == (match.home_score, match.away_score)
```

`matches_official` es `null` cuando el partido no tiene marcador oficial
(`in_progress`): no hay nada contra qué contrastar. **El marcador oficial nunca
se toca**: sigue siendo la única fuente de la clasificación de 008 (FR-005 y
Assumption de la spec).

## Migración

Una migración nueva, `down_revision = "d6e7f8a9b0c1"`, que crea **solo**
`match_events` con sus dos CHECK y su índice. Al autogenerarla hay que borrar
del diff los `DROP INDEX`/`CREATE INDEX` espurios sobre
`ix_leagues_unique_name_season` e `ix_teams_unique_league_name`
(research.md §7 y AGENTS.md).
