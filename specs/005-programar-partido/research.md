# Research: Programar un partido

**Feature**: `005-programar-partido` · **Date**: 2026-08-19

**Sin decisiones de stack.** Todo el stack está fijado en
`specs/001-fundacion-y-autenticacion/research.md` y no se re-decide aquí
(`AGENTS.md` §5). Este documento cubre solo lo específico de esta HU.

## 1. ¿Se permite `scheduled_at` en el pasado?

**Decision**: sí. El servidor acepta cualquier timestamp con zona (ISO 8601);
no exige que sea futuro.

**Rationale**: FR-001 exige fecha/hora programada, no “fecha futura”. El
Independent Test usa una fecha futura como escenario feliz, no como regla.
Rechazar fechas pasadas inventaría alcance y dificultaría cargar partidos
históricos o demos. El edge case de registrar un resultado antes de la fecha
programada queda para `specs/006-registrar-resultado`.

**Alternatives considered**: exigir `scheduled_at > now()` (descartado: no
está en la spec); permitir solo fechas del día o posteriores en zona local
(descartado: complejidad de TZ sin beneficio).

## 2. Listado de partidos por liga en esta HU

**Decision**: exponer `GET /leagues/{leagueId}/matches` (paginado, orden
ascendente por `scheduled_at`) además del detalle `GET /matches/{id}`
(FR-005). La vista rica de calendario (próximos vs jugados, filtros) llega
en `specs/007-consultar-calendario`.

**Rationale**: sin un listado mínimo la UI de esta HU no puede mostrar que el
partido “apareció”, y el organizador no tendría dónde ver lo programado hasta
007. Un GET paginado por liga es el mismo patrón que equipos/jugadores y no
adelanta el alcance de 007 (filtros por estado, agrupación).

**Alternatives considered**: solo GET por id (descartado: UX incompleta);
implementar ya el calendario de 007 (descartado: viola Principio I / alcance
de otra spec).

## 3. Equipos inactivos al programar

**Decision**: ambos equipos MUST existir, pertenecer a la liga del partido y
tener `status = active`. Si alguno falta, está inactivo o es de otra liga →
`404` con `error.code` `team_not_found` (mismo mensaje genérico; no se filtra
cuál falló ni por qué).

**Rationale**: `003` oculta equipos inactivos de los selectores de alta
(`research.md` §3 de esa spec). Programar un partido con un equipo dado de
baja contradice esa semántica. Usar `404` evita filtrar existencia/estado
interno (`conventions.md`). La regla “ambos en la misma liga” (FR-003) se
cubre con la misma respuesta cuando el equipo no pertenece a `league_id`.

**Alternatives considered**: `409 teams_not_in_league` (descartado: filtra
detalle interno y complica el cliente); permitir equipos inactivos
(descartado: incoherente con 003).

## 4. Columnas de marcador en la migración de esta HU

**Decision**: crear `home_score` y `away_score` como `NULL` en la tabla
`matches` desde esta migración. Esta HU **nunca** los escribe; siempre
responden `null`.

**Rationale**: el modelo compartido de `001` ya define esos campos en
`Match`. Incluirlos ahora evita una migración solo-de-columnas en 006 y
cumple “nace sin marcador” (FR-001) de forma explícita. No se exponen
operaciones para setearlos aquí (Principio I).

**Alternatives considered**: omitir columnas hasta 006 (descartado: el modelo
de 001 ya las declara; retrasarlas obliga a alterar la tabla en la siguiente
HU sin ganar claridad).

## 5. Código de error cuando local == visitante

**Decision**: `409` con `error.code = "match_same_team"`, `field = null`
(conflicto entre dos campos del payload).

**Rationale**: es regla de negocio (FR-002), no fallo de schema Pydantic.
`409` es el status de conflicto en `conventions.md`. `field: null` porque el
problema es la relación entre `home_team_id` y `away_team_id`, no un solo
campo inválido.
