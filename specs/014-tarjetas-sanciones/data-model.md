# Data Model: Tarjetas y sanciones disciplinarias

**Feature**: `014-tarjetas-sanciones` · **Date**: 2026-08-21

Esta HU **amplía** `MatchEvent` (ya implementada en
`specs/009-registrar-goles`) y **añade** una vista derivada de ficha
disciplinaria. No redefine `Match`, `Player`, `Team` ni añade tablas nuevas.
Stack y entidades base: `specs/001-fundacion-y-autenticacion/data-model.md`.

```text
Match (existente) ──< MatchEvent >── Player (existente)
     type ∈ {GOAL, YELLOW_CARD, RED_CARD}
                           │
                           └── (lectura) → Ficha disciplinaria (no persistida)
```

## MatchEvent — ampliación de tipo (persistida)

Misma tabla `match_events`. Solo cambia el conjunto admitido en `type`.

| Campo | Cambio en esta HU |
|---|---|
| `type` | Antes: solo `GOAL`. Ahora: `GOAL \| YELLOW_CARD \| RED_CARD` |
| resto | Sin cambios (id, match_id, player_id, team_id, minute, created_by, created_at) |

### Constraints

| Nombre | Cambio |
|---|---|
| `ck_match_events_type_supported` | `type IN ('GOAL', 'YELLOW_CARD', 'RED_CARD')` |
| `ck_match_events_minute_nonnegative` | Sin cambios |
| `ix_match_events_match_minute` | Sin cambios (sigue sirviendo al listado y a consultas por partido) |

**Sin unicidad nueva**: varias tarjetas del mismo jugador en el mismo partido
son legítimas (FR-005), incluido el mismo minuto.

`team_id` sigue derivándose de `Player.team_id` en el servicio; el cliente
nunca lo envía (FR-006).

## Reglas de validación al registrar una tarjeta

| Regla | Origen | Dónde / código de error |
|---|---|---|
| Partido en `in_progress` o `finished` | FR-002 | servicio; `409 match_not_playable` |
| Jugador pertenece a local o visitante | FR-004 | servicio; `409 player_not_in_match` |
| Si hay alineación, el jugador figura en ella | FR-003 | servicio vía `jugadores_alineados` (010); `409 player_not_in_lineup` |
| `type` es `YELLOW_CARD` o `RED_CARD` (o `GOAL` vía el mismo endpoint) | FR-001 | schema Pydantic **y** CHECK en base; `400 validation_error` |
| `minute >= 0` | 001 / 009 | schema + CHECK |
| Escritura con operador u organizador | Assumption roles | `requiere_rol` → `401`/`403` |

Las reglas de pertenencia y alineación son las mismas funciones (o una
generalización compartida) que usa el registro de goles: no se duplica la
lógica en otro módulo.

## Ficha disciplinaria — vista derivada (NO persistida)

No es tabla. Se calcula en cada `GET` a partir de los `MatchEvent` del
jugador con `type ∈ {YELLOW_CARD, RED_CARD}`.

| Campo expuesto | Derivación |
|---|---|
| `player_id` | del path |
| `yellow_cards` | `count` de eventos `YELLOW_CARD` |
| `red_cards` | `count` de eventos `RED_CARD` |
| `suspended` | `red_cards >= 1` **o** número de `match_id` distintos con al menos una `YELLOW_CARD` `>= 2` |

### Regla de suspensión (FR-007)

- **Una roja** → suspendido.
- **Dos amarillas en partidos distintos** → suspendido.
- **Dos amarillas en el mismo partido** → no disparan la acumulación; cuentan
  en `yellow_cards` pero un solo partido para el umbral.
- **Sin expiración** dentro de la temporada: no hay fecha de cumplimiento ni
  flag editable.
- Alcance: eventos del jugador (pertenece a un equipo de una liga; no hay
  traspasos en esta versión — Assumption de 001/004).

## Migración

Una migración que **solo** reemplaza el CHECK de `type`.

- `down_revision` provisional: cabeza actual de `main` (`919f3bd57721` al
  planificar). Al mergear, re-puntear tras `013` según AGENTS.md
  (orden `013 → 014 → 016 → 017`).
- Al autogenerar: borrar del diff cualquier recreación de
  `ix_leagues_unique_name_season` / `ix_teams_unique_league_name`.
- **No** tocar índices ni columnas ajenas (Principio IV).
