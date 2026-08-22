# Data Model: Exportacion de clasificacion y calendario a CSV

**Feature**: `015-exportacion-csv` · **Date**: 2026-08-22

No anade entidades persistentes, campos, relaciones, indices ni migraciones.
Consume las proyecciones de 007/008:

```text
League + Standings (008) + Calendar/Match (007) + Team
                         -> ExportService -> CsvDocument (efimero)
```

## CsvDocument

| Campo | Tipo | Regla |
|---|---|---|
| `content` | bytes | UTF-8 BOM, registros CRLF |
| `media_type` | constante | `text/csv; charset=utf-8` |
| `filename` | string | liga segura + recurso + fecha UTC + `.csv` |
| `generated_at` | datetime UTC | inyectable, ISO 8601 |

No tiene id ni ciclo de vida: existe durante un GET.

## Clasificacion

Fuente unica: `StandingsService.obtener_clasificacion`. Mapeo:
`Pos=position`, `Equipo=team_name`, `PJ=played`, `G=won`, `E=drawn`, `P=lost`,
`GF=goals_for`, `GC=goals_against`, `GD=goal_difference`, `Pts=points`.
El orden se conserva. Sin resultados hay filas en cero; sin equipos, cero filas.

## Calendario

Fuentes: colecciones `scheduled` y `finished` de `MatchService` y nombres por
`TeamService`. Columnas: `Local`, `Visitante`, `Fecha` ISO 8601, `Estado`,
`Marcador` (`home_score-away_score` o vacio). Orden: programados ascendente,
luego jugados descendente, ambos con desempate estable. Se recorren todas las
paginas hasta `total`; el limite de 100 nunca recorta la exportacion.

## Metadatos y validaciones

- Registros iniciales: `Liga,<name>` y `Generado en,<ISO UTC>`; luego linea
  vacia, encabezado y filas.
- `csv.writer` delimita comas, comillas y saltos; prefijos de formula se neutralizan.
- Solo `format=csv`; otro valor es `validation_error`.
- Liga inexistente conserva `league_not_found`.
- No hay estados, transiciones ni migracion.
