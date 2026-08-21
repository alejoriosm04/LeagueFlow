# Research: Alineaciones y estadisticas de jugadores

**Feature**: `010-alineaciones-estadisticas` · **Date**: 2026-08-20

## Decision 1: Endpoint unico para registrar/modificar alineacion

- Decision: usar `PUT /matches/{matchId}/lineup` como operacion idempotente de
  reemplazo completo (home + away) y `GET /matches/{matchId}/lineup` como
  lectura publica con estado explicito.
- Rationale: `PUT` evita ambiguedad entre "crear" y "editar" (FR-001, FR-003)
  y encaja con el patron de endpoints operativos ya usado en Match.
- Alternatives considered:
  - `POST` + `PATCH`: mas verbos y mas estados transitorios que no agregan valor.
  - Unicamente extender `GET /matches/{id}`: no deja un contrato aislado para
    validar la regla de alineacion opcional.

## Decision 2: Alineacion opcional y estado explicito en ficha de partido

- Decision: cuando no hay alineacion registrada, la API devolvera
  `lineup.status = "missing"` y listas vacias; esto aplica tambien a partidos
  `finished` que nunca tuvieron alineacion (edge case pedido).
- Rationale: FR-004 exige visibilidad explicita, no inferida por el cliente.
- Alternatives considered:
  - Responder `404` si no hay alineacion: confunde "partido no existe" con
    "alineacion no cargada".
  - Responder `null` sin estado: obliga logica ambigua en cliente.

## Decision 3: Regla de pertenencia jugador-equipo en alineacion

- Decision: rechazar `409 player_not_in_match` si un `player_id` no pertenece a
  `home_team_id` ni `away_team_id` del partido (FR-002).
- Rationale: coherente con la misma regla en eventos de gol de 009.
- Alternatives considered:
  - Reasignar automaticamente de equipo: viola integridad de dominio.

## Decision 4: Coherencia alineacion-eventos al corregir alineaciones

- Decision: una modificacion de alineacion que quite a un jugador con goles ya
  registrados en ese partido se rechaza con
  `409 lineup_conflicts_with_events` + lista `conflicting_player_ids`.
- Rationale: satisface FR-003 y evita dejar eventos invalidos respecto de la
  alineacion vigente.
- Alternatives considered:
  - Borrar automaticamente goles conflictivos: destruye auditabilidad.
  - Permitir incoherencia temporal: rompe la regla derivada de 009/010.

## Decision 5: Derivacion de PlayerStatistics (solo lectura)

- Decision: `PlayerStatistics` se calcula en cada consulta; no existe tabla ni
  columna editable para goles o partidos jugados.
  - `goals`: `COUNT(match_events WHERE type='GOAL' AND player_id = X)`
  - `matches_played`: `COUNT(DISTINCT match_id)` sobre `match_lineups` unido a
    `matches.status = 'finished'`
- Rationale: cumple FR-006, FR-007, FR-008 y la regla constitucional de
  derivacion desde hechos.
- Alternatives considered:
  - Materializar contadores editables: mas rapido en lectura, pero prohibido por
    la constitucion y propenso a drift.

## Decision 6: Recalculo ante correccion de resultado que elimina un gol

- Decision: las estadisticas se recalculan siempre desde estado actual de
  `match_events` + `match_lineups`; por eso cualquier alta/baja/correccion de un
  evento GOAL impacta inmediatamente en la siguiente lectura.
- Rationale: garantiza SC-001 (coincidencia exacta con hechos persistidos).
- Alternatives considered:
  - Recalculo por jobs de sincronizacion: introduce ventanas de inconsistencia.

Nota operativa de integracion con 006/009:
- Si una correccion aprobada modifica solo el marcador oficial y no toca eventos,
  el conteo de goleadores no cambia (porque FR-006 define goles por eventos).
- Si la correccion incluye la eliminacion/anulacion del evento GOAL,
  el conteo baja automaticamente sin mantenimiento adicional.

## Decision 7: Endpoints publicos de estadisticas y "maximo goleador"

- Decision: exponer `GET /leagues/{leagueId}/top-scorers` y
  `GET /players/{playerId}/statistics` sin autenticacion (FR-009, FR-010,
  FR-011). La tabla de goleadores incluye `rank` e `is_top_scorer` para
  identificar de forma inmediata al maximo goleador (SC-002).
- Rationale: separa lectura publica de operaciones protegidas y facilita UX.
- Alternatives considered:
  - Endpoint autenticado: contradice FR-011.
  - Orden sin `rank`: obliga al frontend a recalcular posiciones y empates.

## Decision 8: Cierre de deuda tecnica heredada de 009 (FR-003)

- Decision: implementar `MatchService.jugadores_alineados` con consulta real a
  `MatchLineup` y agregar prueba de integracion pendiente: partido con
  alineacion registrada + gol a jugador fuera de alineacion => rechazo.
- Rationale: cumple compromiso documentado en 009 y evita desviacion permanente.
- Alternatives considered:
  - Mantener doble en unit tests: no cubre flujo extremo a extremo.
