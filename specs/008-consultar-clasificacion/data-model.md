# Data Model: Consultar la clasificación

**Feature**: `008-consultar-clasificacion` · **Date**: 2026-08-20

Esta HU **no añade entidades persistentes, campos, relaciones, constraints,
índices ni migraciones**. `Standings` es una vista derivada que se calcula en
cada consulta desde los partidos `finished` de la liga (research.md §1).

Sobre el modelo de 001 solo se añade lo siguiente, y nada de ello toca el
esquema:

```text
Team (existente) ─┐
                  ├─> StandingsCalculator ──> Standings  (en memoria)
Match (existente) ┘
```

## Standings — entidad derivada (no persistente)

Una `Standings` es la lista ordenada de filas de una liga. No tiene
identificador propio ni fecha de creación: es una función de sus entradas.

### StandingsRow

| Campo | Tipo | Derivación |
|---|---|---|
| `position` | int ≥ 1 | índice 1..N en el orden de §Orden |
| `team_id` | uuid | `Team.id` |
| `team_name` | str | `Team.name` |
| `played` | int ≥ 0 | partidos `finished` del equipo en la liga |
| `won` | int ≥ 0 | partidos con más goles a favor que en contra |
| `drawn` | int ≥ 0 | partidos con la misma cantidad de goles |
| `lost` | int ≥ 0 | partidos con menos goles a favor que en contra |
| `goals_for` | int ≥ 0 | suma de goles anotados |
| `goals_against` | int ≥ 0 | suma de goles recibidos |
| `goal_difference` | int | `goals_for - goals_against` |
| `points` | int ≥ 0 | `won * 3 + drawn * 1` (FR-003) |

Invariantes verificables en test: `played == won + drawn + lost`,
`points == won * 3 + drawn`, `goal_difference == goals_for - goals_against`, y
la suma de `goals_for` de toda la tabla es igual a la suma de `goals_against`.

## Entradas del cálculo

**Partidos** (`MatchService.listar_finalizados`): partidos de la liga con
`status = 'finished'`. Por el `CheckConstraint`
`ck_matches_status_scores_coherent` de 006, un partido `finished` siempre tiene
`home_score` y `away_score` no nulos, así que el cálculo no necesita defensa
contra marcadores nulos. `scheduled`, `in_progress` y `cancelled` se descartan
(FR-001, FR-007).

**Equipos** (`TeamService.listar_por_liga`): todos los equipos de la liga.
Ocupan fila los `active` y los `inactive` con al menos un partido `finished`
(research.md §3, Assumption de la spec).

## Reglas de puntuación (FR-003)

Para cada partido `finished`, con el equipo actuando de local o de visitante:

```text
goles_propios > goles_rivales  -> won++,   points += 3
goles_propios = goles_rivales  -> drawn++, points += 1
goles_propios < goles_rivales  -> lost++,  points += 0
```

## Orden (FR-005, FR-006)

```text
ORDER BY points DESC,
         goal_difference DESC,
         goals_for DESC,
         lower(trim(team_name)) ASC,
         team_id ASC
```

Los tres primeros criterios son FR-005. El cuarto es el desempate determinista
de FR-006, y `ix_teams_unique_league_name` garantiza que basta. `team_id`
cierra el orden para que sea total y reproducible en cualquier motor o
colación.

## Estados y transiciones

Ninguna. `Standings` no tiene ciclo de vida: no se crea, no se actualiza y no
se borra. La única forma de que cambie es que cambien los partidos de origen —
registrar un resultado (006) o aprobar una corrección (006) — y el cambio se
observa en la siguiente consulta sin acción intermedia (SC-002, FR-002).

## Migración

No aplica. Ningún cambio de esquema en esta HU.
