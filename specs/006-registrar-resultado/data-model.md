# Data Model: Registrar y corregir el resultado

**Feature**: `006-registrar-resultado` · **Date**: 2026-08-19

El modelo central está fijado en 001. Este documento registra solo el delta
que aporta la HU 006.

## Match — delta de esta spec

La tabla y `home_score`/`away_score` existen desde 005. Esta HU habilita su
escritura bajo estas reglas:

| Campo | Tipo | Regla añadida |
|---|---|---|
| `status` | string enum | registro inicial atómico: `scheduled → finished` |
| `home_score` | integer nullable | al finalizar pasa a no nulo y `>= 0` |
| `away_score` | integer nullable | al finalizar pasa a no nulo y `>= 0` |
| `updated_at` | timestamptz | cambia al registrar o aprobar una corrección |

Invariantes:

- `finished` implica ambos marcadores no nulos y no negativos.
- La ruta de resultado nunca escribe un partido `finished`.
- Aprobar cambia ambos marcadores y `updated_at`; el estado sigue `finished`.
- Una corrección pendiente o rechazada nunca cambia `Match`.

Constraints de base de datos añadidos por esta HU:

- Cada marcador es nulo o `>= 0`.
- `status = 'finished'` exige ambos marcadores no nulos.
- Los estados distintos de `finished` exigen ambos marcadores nulos.

```text
scheduled --registrar resultado--> finished
finished  --aprobar corrección----> finished (cambia marcador)
```

## ResultCorrectionRequest — entidad nueva

| Campo | Tipo | Reglas |
|---|---|---|
| `id` | UUID | PK |
| `match_id` | UUID FK → Match | obligatorio, `ON DELETE RESTRICT`; partido `finished` al solicitar |
| `proposed_home_score` | integer | obligatorio, `>= 0` |
| `proposed_away_score` | integer | obligatorio, `>= 0` |
| `previous_home_score` | integer | snapshot obligatorio, `>= 0`; inmutable |
| `previous_away_score` | integer | snapshot obligatorio, `>= 0`; inmutable |
| `reason` | text | obligatorio; tras trim no vacío |
| `status` | string enum | `pending` por defecto; luego `approved` o `rejected` |
| `requested_by` | UUID FK → User | obligatorio; derivado de sesión |
| `decided_by` | UUID nullable FK → User | organizador distinto de `requested_by` al cerrar |
| `decision_reason` | text nullable | obligatorio/no vacío en `rejected`; nulo en los demás estados |
| `created_at` | timestamptz | obligatorio |
| `decided_at` | timestamptz nullable | nulo en `pending`; obligatorio al cerrar |

Restricciones e índices:

- Checks para los cuatro campos de marcador `>= 0`.
- Índice por `(match_id, created_at)` para el historial.
- Índice único parcial sobre `match_id` cuando `status = 'pending'` (FR-011).
- Coherencia: `pending` no tiene decisión; `approved` tiene decisor/fecha sin
  motivo de rechazo; `rejected` tiene decisor, fecha y motivo.
- `decided_by != requested_by` cuando existe decisión.

### Transiciones

```text
pending --decisión approved--> approved  [actualiza Match en la transacción]
pending --decisión rejected--> rejected  [Match permanece intacto]
```

`approved` y `rejected` son terminales. Una decisión repetida es conflicto.

## Relaciones y consultas

- `Match 1 ── * ResultCorrectionRequest`.
- Historial paginado por `created_at DESC`, con desempate por `id`.
- La clasificación de 008 lee únicamente `Match` finalizados; nunca lee esta
  solicitud ni persiste acumulados.

## Migración

Alembic crea `result_correction_requests`, sus constraints e índices, y añade
los checks de marcador/estado a `matches`. Se elimina del autogenerate cualquier
recreación espuria de
`ix_leagues_unique_name_season` o `ix_teams_unique_league_name`, según
`AGENTS.md`.
