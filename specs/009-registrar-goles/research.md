# Research: Registrar goles por jugador

**Feature**: `009-registrar-goles` · **Date**: 2026-08-20

Sin `NEEDS CLARIFICATION`: el stack y el modelo vienen fijados por
`specs/001-fundacion-y-autenticacion` (AGENTS.md §5), que **ya define
`MatchEvent`** con sus campos y su validación de alineación. Esta HU no
rediseña esa entidad: la implementa. Lo que sigue son las decisiones propias.

## 1. `MatchEvent` vive en el dominio Match

**Decision**: la tabla, el servicio y los endpoints van en
`backend/src/matches/`, junto a `Match` y `ResultCorrectionRequest`.

**Rationale**: un evento no existe fuera de su partido — `match_id` es
obligatorio y el ciclo de vida es el del partido. Es el mismo criterio con el
que 006 puso `ResultCorrectionRequest` ahí. `statistics/` recibirá en 010 la
*derivación* (goleadores), no el registro.

**Alternatives considered**: un módulo `events/` propio, descartado porque
partiría el dominio Match en dos por una tabla; meterlo en `statistics/`,
descartado porque ese módulo deriva, nunca captura hechos.

## 2. FR-003 sin la tabla de alineaciones: puerto, no tabla especulativa

**Decision**: la regla se implementa **completa y probada** en 009 detrás de un
puerto de lectura, `MatchService.jugadores_alineados(match_id) -> set[UUID] | None`,
donde `None` significa "este partido no tiene alineación registrada". En 009 la
única implementación devuelve `None` siempre, documentado como tal.
`specs/010-alineaciones-estadisticas` la sustituye por la consulta real.

**Rationale**: FR-003 es un MUST de esta spec, pero `MatchLineup` es entidad de
010 y 001 advierte explícitamente contra crear tablas para requisitos que
todavía no existen. El puerto separa **la regla** (de 009, comprobable hoy con
un doble en pruebas unitarias) de **su fuente de datos** (de 010). Así el
Acceptance Scenario 3 no queda sin prueba, que es lo que exige el Principio II.

**Consecuencia que hay que aceptar**: en 009 la regla no tiene cobertura
extremo a extremo, porque no hay forma de crear una alineación. La prueba de
integración correspondiente es responsabilidad de 010 y queda anotada en su
plan. Está registrado como desviación en `plan.md`.

**Alternatives considered**: crear `match_lineups` en 009, descartado por
invadir el alcance de 010 y diseñar una tabla que su spec todavía puede
cambiar; implementar 010 antes que 009, descartado porque altera el orden del
backlog y 010 depende de los eventos de gol que produce 009 (su FR-006);
declarar FR-003 fuera de alcance, descartado porque un MUST no se archiva en
silencio.

## 3. Solo un partido con marcador admite goles

**Decision**: se aceptan eventos en partidos `finished` e `in_progress`; se
rechaza con `409` en `scheduled` y `cancelled`.

**Rationale**: FR-005 obliga a contrastar los goles con el marcador oficial, y
ese marcador solo existe cuando el partido está `finished` (lo garantiza el
`CheckConstraint` `ck_matches_status_scores_coherent` de 006). Registrar goles
de un partido que aún no se juega no tiene sentido de negocio, y de uno
cancelado contradice a FR-007 de 008, que lo excluye de toda derivación.

**Alternatives considered**: aceptar cualquier estado, descartado porque
permite goles en partidos cancelados; exigir estrictamente `finished`,
descartado porque cerraría la puerta al registro en vivo que `in_progress`
existe para habilitar.

## 4. `team_id` se deriva del jugador, no lo envía el cliente

**Decision**: el cuerpo de la petición lleva `player_id` y `minute`. El
servidor resuelve `team_id` desde `Player.team_id` y valida que ese equipo sea
el local o el visitante del partido (FR-002).

**Rationale**: `data-model.md` de 001 exige que `team_id` sea coherente con
`player_id`; si el cliente lo envía, hay que validarlo *y* rechazar la
incoherencia, con lo que el campo solo añade una forma de equivocarse. La
plantilla de un jugador es inmutable tras la creación (Assumption de 004), así
que la derivación es estable.

**Alternatives considered**: aceptar `team_id` y validarlo, descartado por lo
anterior; no persistir `team_id` y resolverlo siempre por join, descartado
porque 001 lo declara como campo de la entidad y 010 lo necesita para agrupar.

## 5. La advertencia de FR-005 es un bloque de consistencia en el listado

**Decision**: `GET /matches/{matchId}/events` devuelve, junto a los eventos, un
bloque `consistency` con los goles registrados por lado, el marcador oficial y
un booleano `matches_official`. El `POST` responde `201` con el evento creado y
**nunca** falla por descuadre.

**Rationale**: FR-005 pide advertir sin bloquear y que el marcador oficial siga
mandando. Un `409` sería bloquear; un campo `warning` en la respuesta del
`POST` describiría el estado en un solo instante y quedaría obsoleto al
registrar el gol siguiente. El bloque en el listado es siempre el estado actual
y sirve igual a la ficha del partido que a una revisión posterior.

**Alternatives considered**: cabecera `Warning` HTTP, descartada por invisible
para el cliente y ajena al contrato del proyecto; endpoint aparte de
consistencia, descartado por partir en dos una lectura que siempre va junta.

## 6. El listado de eventos es público

**Decision**: `POST` exige rol operador u organizador (FR-006); `GET` no exige
sesión.

**Rationale**: es la línea que ya siguen el calendario (007) y la clasificación
(008): en este producto se escribe con sesión y se lee sin ella. Además 010
expondrá los goleadores públicamente derivados de estos mismos eventos; que el
detalle fuera privado y el agregado público sería incoherente.

**Alternatives considered**: exigir sesión para leer, descartado por lo
anterior y porque la spec no lo pide.

## 7. Migración nueva y el falso positivo conocido de Alembic

**Decision**: una migración con `down_revision = "d6e7f8a9b0c1"` que crea
únicamente `match_events` y su índice por `match_id`.

**Rationale**: es la primera tabla nueva desde 006. Al correr
`alembic revision --autogenerate` aparecerán `DROP INDEX`/`CREATE INDEX`
espurios sobre `ix_leagues_unique_name_season` e `ix_teams_unique_league_name`
por la normalización `trim` → `TRIM(BOTH FROM ...)`; hay que borrarlos del
diff a mano (AGENTS.md). Se verificó hoy que `alembic check` los sigue
reportando en `main`, así que no es regresión de esta HU.

**Alternatives considered**: aceptar el diff generado tal cual, descartado
porque recrearía índices ajenos a esta HU y viola el Principio IV.

## 8. Corregir un gol queda fuera de alcance

**Decision**: 009 implementa registrar y listar. No hay edición ni borrado de
eventos.

**Rationale**: la spec no los pide en ningún FR ni Acceptance Scenario. 006 ya
fijó cómo se corrige un dato ya registrado en este producto —solicitud
auditada y aprobación— y replicar ese flujo para eventos sin que ninguna spec
lo describa sería inventar la regla en el código (Principio I).

**Alternatives considered**: un `DELETE` simple, descartado porque
contradiría el criterio de auditoría que 006 estableció para el marcador.
