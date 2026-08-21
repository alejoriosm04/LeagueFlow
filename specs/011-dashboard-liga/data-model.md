# Data Model: Dashboard general de la liga

**Feature**: `011-dashboard-liga` · **Date**: 2026-08-20

Esta HU **no añade entidades persistentes ni campos nuevos**. `DashboardSummary`
es una vista derivada compuesta en cada consulta a partir de dos entidades ya
existentes — `Match` (`specs/005-*`, `specs/006-*`) y `Standings`
(`specs/008-*`, ella misma derivada de `Match` y `Team`) — sin introducir un
tercer origen de datos:

```text
Match (existente) ──> MatchService.listar_partidos (007, sin cambios) ──┐
                                                                          ├─> DashboardSummary (en memoria)
Team (existente) ──┐                                                    │
                    ├─> StandingsService.obtener_clasificacion (008) ────┘
Match (existente) ──┘
```

Sobre el modelo de `001-fundacion-y-autenticacion` esta HU solo añade un
índice sobre una tabla existente (§Migración); ninguna columna, constraint ni
entidad cambia de forma.

## DashboardSummary — entidad derivada (no persistente)

Igual que `Standings` en 008, no tiene identificador propio ni marca de
tiempo: es una función pura de sus tres entradas, recalculada en cada
`GET`.

| Campo             | Tipo                    | Derivación                                                                 |
| ------------------ | ----------------------- | --------------------------------------------------------------------------- |
| `league_id`        | uuid                    | parámetro de ruta                                                          |
| `recent_matches`   | `Match[]` (≤ 5)         | `MatchService.listar_partidos(league_id, page=1, page_size=5, status="finished")`, items — ya viene ordenado `scheduled_at DESC` (007) |
| `upcoming_matches` | `Match[]` (≤ 5)         | `MatchService.listar_partidos(league_id, page=1, page_size=5, status="scheduled")`, items — ya viene ordenado `scheduled_at ASC` (007) |
| `top_standings`    | `StandingsRow[]` (≤ 5)  | `StandingsService.obtener_clasificacion(league_id).items[:5]` — ya viene ordenado por FR-005/FR-006 (008) |

`Match` y `StandingsRow` son los schemas Pydantic **ya existentes** en
`src/matches/schemas.py` y `src/statistics/schemas.py` respectivamente; el
dashboard los reutiliza como tipos de campo — no redeclara sus propiedades.

### Invariantes verificables en test

- `len(recent_matches) <= 5`, `len(upcoming_matches) <= 5`,
  `len(top_standings) <= 5` — siempre, incluida una liga con más de 5
  partidos/equipos.
- Todo elemento de `recent_matches` tiene `status == "finished"`; todo
  elemento de `upcoming_matches` tiene `status == "scheduled"` (heredado de la
  garantía de filtro de 007, no reimplementado aquí).
- `recent_matches` viene ordenado por `scheduled_at` descendente;
  `upcoming_matches`, ascendente (heredado de 007).
- `top_standings[i].position == i + 1` para `i` en `0..len(top_standings)-1`
  (heredado de 008; el recorte a 5 no reordena).
- Una liga sin partidos: `recent_matches == []` y `upcoming_matches == []`.
  Una liga sin equipos: `top_standings == []`. Ninguno de los tres casos
  produce error — la respuesta sigue siendo `200`.

## Estados y transiciones

Ninguna. Igual que `Standings`, `DashboardSummary` no se crea, actualiza ni
borra: cambia únicamente porque cambian los partidos de origen (nuevo
partido programado, resultado registrado, corrección aprobada), y el cambio
se refleja en la siguiente consulta sin acción manual — hereda esta garantía
de 007/008 sin añadir lógica propia.

## Migración

Una migración aditiva, sin tocar filas existentes ni el modelo `Match`:

```text
CREATE INDEX ix_matches_league_status_scheduled
    ON matches (league_id, status, scheduled_at);
```

- **Reversible**: `DROP INDEX ix_matches_league_status_scheduled`.
- **No afecta** ningún índice ni constraint de `001`–`010` (no toca
  `ix_teams_unique_league_name`, `ix_leagues_unique_name_season`,
  `ix_match_events_match_minute` ni los índices de
  `result_correction_requests`).
- Justificación completa de por qué se añade (y por qué no es indispensable a
  la escala de referencia) en `research.md` §4.
- Se declara también en `Match.__table_args__`
  (`backend/src/matches/models.py`) para que `alembic revision --autogenerate`
  futuro no la vuelva a proponer como faltante.
