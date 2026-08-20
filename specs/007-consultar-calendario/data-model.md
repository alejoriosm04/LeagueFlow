# Data Model: Consultar el calendario y los resultados

**Feature**: `007-consultar-calendario` · **Date**: 2026-08-20

Esta HU es una proyección de lectura. No añade entidades, campos, relaciones,
constraints, índices ni migraciones. Reutiliza `Match` de 005, los marcadores
habilitados por 006 y `Team` para mostrar nombres.

## Match — proyección consultada

| Campo existente | Uso en esta HU |
|---|---|
| `id` | enlace a ficha y desempate estable |
| `league_id` | limita la consulta a una liga |
| `home_team_id` / `away_team_id` | resolución de nombres vía API Team |
| `scheduled_at` | orden ascendente o descendente según estado |
| `status` | filtro: `scheduled`, `in_progress`, `finished`, `cancelled` |
| `home_score` / `away_score` | marcador visible para `finished` |

## Proyecciones no persistentes

```text
Próximos = Match WHERE status = scheduled
           ORDER BY scheduled_at ASC, id ASC

Jugados  = Match WHERE status = finished
           ORDER BY scheduled_at DESC, id DESC
```

`in_progress` y `cancelled` se presentan al seleccionar su filtro.

## Validaciones

- `status` opcional pertenece al enum de `Match`.
- `page >= 1`; `1 <= page_size <= 100`.
- Liga inexistente conserva `404 league_not_found`.
- Sin partidos: `200`, `items=[]`, `total=0`.

## Migración

No aplica: no cambia el esquema.
