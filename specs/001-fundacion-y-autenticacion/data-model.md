# Data Model: LeagueFlow (modelo de dominio compartido)

**Feature**: `001-fundacion-y-autenticacion` · **Date**: 2026-08-18

Este es el modelo de dominio **completo del proyecto**, no solo de esta HU —
ver el "Scope Note" en `specs/001-fundacion-y-autenticacion/spec.md`. Las
specs `002` a `011` referencian este archivo y solo documentan ampliaciones;
no lo redefinen (`AGENTS.md` §5).

Convenciones: todo id es UUID. Todo registro tiene `created_at`; los que
admiten edición tienen también `updated_at`. Los campos marcados **derivado**
nunca se escriben directamente — se recalculan.

## Diagrama de relaciones

```text
User (org./operador)
  │ atribuye autoría de
  ▼
League ──< Team ──< Player
  │
  └──< Match >── (home_team, away_team → Team)
         │
         ├──< MatchLineup >── Player   (qué jugadores participaron)
         ├──< MatchEvent >── Player    (goles; extensible a más tipos)
         └──< ResultCorrectionRequest  (solicitudes de corrección de marcador)

Standings          = derivado de Match (finished)               [specs/008]
PlayerStatistics   = derivado de MatchEvent + MatchLineup        [specs/010]
```

---

## User

Persona autenticada que opera el sistema. Definida en esta spec.

| Campo | Tipo | Reglas |
|---|---|---|
| id | UUID | PK |
| username | string, único | obligatorio (FR-004) |
| password_hash | string | nunca se expone; ver `passlib[bcrypt]` en `research.md` §4 (FR-005) |
| role | enum: `organizador`, `operador` | obligatorio, exactamente uno (FR-001, FR-004) |
| status | enum: `active`, `inactive` | por defecto `active` |
| created_by | UUID nullable (FK → User) | organizador que creó la cuenta (FR-007, FR-008); `null` únicamente en el usuario semilla, creado por script de despliegue y no por otro usuario |
| created_at | timestamp | |

**Validaciones**: `username` único (case-insensitive). Un usuario `inactive`
no puede iniciar sesión (mensaje genérico, FR-010).

**Semilla inicial**: al desplegar, se crea un usuario `organizador` semilla
(ver Assumption "Cuentas de usuario" en `spec.md`) — no hay autorregistro
(FR-007).

## Session

Entidad de infraestructura (no aparece como Key Entity de negocio en
`spec.md`, pero sostiene FR-006 y FR-008 — ver `research.md` §4).

| Campo | Tipo | Reglas |
|---|---|---|
| id / token | UUID opaco | valor de la cookie `httpOnly` |
| user_id | UUID (FK → User) | |
| created_at | timestamp | |
| expires_at | timestamp | se extiende en cada request válido (expiración por inactividad, FR-006) |
| revoked_at | timestamp nullable | se setea al cerrar sesión; una sesión revocada no autentica |

**Validaciones**: toda ruta de escritura exige una sesión con `revoked_at IS
NULL AND expires_at > now()` (FR-003). El rol del `User`
asociado determina si la operación está permitida (FR-009). `get_current_user`
MUST extender `expires_at` en cada validación exitosa — es lo que hace la
expiración "por inactividad" y no un TTL fijo (FR-006).

**Sin `created_by`, a propósito**: una sesión pertenece al usuario que se
autenticó, no la crea otro usuario en su nombre — no aplica el patrón de
atribución de autoría de las demás entidades (ver nota en §User sobre FR-008).

---

## League

Contenedor raíz de una competición. Definida en `specs/002-crear-liga`.

| Campo | Tipo | Reglas |
|---|---|---|
| id | UUID | PK |
| name | string | obligatorio |
| season | string | obligatorio |
| description | string nullable | opcional |
| created_by | UUID (FK → User) | organizador que la creó |
| created_at | timestamp | |

**Validaciones**: `(name, season)` único (FR-002 de `specs/002-*`).

## Team

Participante de una liga. Definida en `specs/003-registrar-equipos`.

| Campo | Tipo | Reglas |
|---|---|---|
| id | UUID | PK |
| league_id | UUID (FK → League) | obligatorio, inmutable tras creación |
| name | string | obligatorio |
| crest_url | string nullable | enlace externo, no se aloja el archivo |
| colors | string nullable | libre (ej. "azul/blanco") |
| status | enum: `active`, `inactive` | por defecto `active` (FR-005 de `specs/003-*`: borrado lógico) |
| created_by | UUID (FK → User) | organizador que lo registró (FR-008) |
| created_at | timestamp | |

**Validaciones**: `(league_id, name)` único (FR-002 de `specs/003-*`).

## Player

Integrante de la plantilla de un equipo. Definida en `specs/004-registrar-jugadores`.

| Campo | Tipo | Reglas |
|---|---|---|
| id | UUID | PK |
| team_id | UUID (FK → Team) | obligatorio, inmutable tras creación (ver Assumption "jugador en un solo equipo") |
| name | string | obligatorio |
| number | integer nullable | dorsal, opcional |
| position | string nullable | opcional |
| status | enum: `active`, `inactive` | por defecto `active` (FR-005 de `specs/004-*`) |
| created_by | UUID (FK → User) | organizador que lo registró (FR-008) |
| created_at | timestamp | |

**Validaciones**: `(team_id, number)` único cuando `number` no es nulo
(FR-003 de `specs/004-*`).

## Match

Enfrentamiento entre dos equipos de la misma liga. Definida en
`specs/005-programar-partido`, ampliada en `specs/006-registrar-resultado`.

| Campo | Tipo | Reglas |
|---|---|---|
| id | UUID | PK |
| league_id | UUID (FK → League) | obligatorio |
| home_team_id | UUID (FK → Team) | obligatorio |
| away_team_id | UUID (FK → Team) | obligatorio, `!= home_team_id` (FR-002 de `specs/005-*`) |
| scheduled_at | timestamp | obligatorio |
| status | enum: `scheduled`, `in_progress`, `finished`, `cancelled` | por defecto `scheduled` |
| home_score | integer nullable | `>= 0`; solo se escribe vía el flujo de resultado (FR-001/FR-003 de `specs/006-*`) |
| away_score | integer nullable | ídem |
| created_by | UUID (FK → User) | organizador que lo programó (FR-008) |
| created_at, updated_at | timestamp | |

**Validaciones**: `home_team_id` y `away_team_id` MUST pertenecer a `league_id`
(FR-003 de `specs/005-*`). `home_score`/`away_score` solo son no-nulos cuando
`status = finished`.

**State transitions** (`status`):

```text
scheduled ──(registrar resultado, specs/006)──> finished
scheduled ──(cancelar, fuera de alcance de la línea base)──> cancelled
finished  ──(aprobar ResultCorrectionRequest)──> finished   [homeScore/awayScore cambian, status no]
```

No hay transición directa que reabra `finished` a `scheduled`. `in_progress`
queda reservado en el enum para uso futuro (constitución exige el modelo
abierto a extensión); ninguna spec de la línea base lo produce todavía.

**Nota de alcance**: `video_url` (highlights de partido, HU11 del backlog)
NO se incluye en este modelo — HU11 no tiene spec propia en `specs/` todavía
(quedó fuera de la línea base de 10 HU, ver `docs/backlog/backlog.md`). Se
añade como migración incremental cuando esa spec exista (Principio V);
agregarlo ahora violaría la regla de no diseñar para requisitos hipotéticos.

## MatchLineup

Conjunto de jugadores que participaron en un partido, por equipo. Definida en
`specs/010-alineaciones-estadisticas`.

| Campo | Tipo | Reglas |
|---|---|---|
| id | UUID | PK |
| match_id | UUID (FK → Match) | obligatorio |
| team_id | UUID (FK → Team) | obligatorio, uno de los dos equipos del partido |
| player_id | UUID (FK → Player) | obligatorio, `player.team_id == team_id` (FR-002 de `specs/010-*`) |
| created_by | UUID (FK → User) | operador/organizador que registró la alineación (FR-008) |

**Validaciones**: `(match_id, player_id)` único. Opcional a nivel de partido
(FR-004 de `specs/010-*`): un `Match` puede no tener ninguna fila aquí.

## MatchEvent

Hecho ocurrido durante un partido. Definida en `specs/009-registrar-goles`.

| Campo | Tipo | Reglas |
|---|---|---|
| id | UUID | PK |
| match_id | UUID (FK → Match) | obligatorio |
| type | enum: `GOAL` (extensible) | solo `GOAL` implementado en esta versión (FR-004 de `specs/009-*`) |
| player_id | UUID (FK → Player) | obligatorio, pertenece a uno de los dos equipos del partido (FR-002) |
| team_id | UUID (FK → Team) | obligatorio, coherente con `player_id` |
| minute | integer | obligatorio, `>= 0` |
| created_by | UUID (FK → User) | operador/organizador que lo registró |
| created_at | timestamp | |

**Validaciones**: si `match_id` tiene filas en `MatchLineup`, `player_id` MUST
existir en esa alineación para ese partido (FR-003 de `specs/009-*`). El enum
`type` está diseñado para crecer (`YELLOW_CARD`, `RED_CARD`, `SUBSTITUTION`)
sin romper esta tabla — ver constitución, Modelo de Dominio Central.

## ResultCorrectionRequest

Propuesta de nuevo marcador para un partido finalizado. Definida en
`specs/006-registrar-resultado`.

| Campo | Tipo | Reglas |
|---|---|---|
| id | UUID | PK |
| match_id | UUID (FK → Match) | obligatorio, `match.status == finished` |
| proposed_home_score | integer | `>= 0` |
| proposed_away_score | integer | `>= 0` |
| previous_home_score | integer | snapshot del marcador al momento de la solicitud |
| previous_away_score | integer | ídem |
| reason | string | obligatorio (FR-005) |
| status | enum: `pending`, `approved`, `rejected` | por defecto `pending` |
| requested_by | UUID (FK → User) | operador u organizador que solicita |
| decided_by | UUID nullable (FK → User) | organizador que decide; `!= requested_by` (FR-012) |
| decision_reason | string nullable | motivo si se rechaza (FR-009) |
| created_at, decided_at | timestamp | `decided_at` nullable hasta resolver |

**Validaciones**: máximo una fila `status = pending` por `match_id` (FR-011).

**State transitions**:

```text
pending ──(organizador aprueba)──> approved   [Match.home_score/away_score se sustituyen]
pending ──(organizador rechaza)──> rejected   [Match no cambia]
```

---

## Standings (derivado — sin tabla propia)

**Nunca se persiste como tabla editable.** Se calcula on-demand (o se
materializa con recálculo completo garantizado — constitución, Regla de
Derivación de Estadísticas) a partir de `Match` donde `status = finished`,
agrupado por `league_id`. Definido en `specs/008-consultar-clasificacion`.

Campos por fila (equipo): `played, won, drawn, lost, goals_for, goals_against,
goal_diff, points, position`. Orden: `points DESC, goal_diff DESC, goals_for
DESC, team.name ASC` (FR-005/FR-006 de `specs/008-*`).

## PlayerStatistics (derivado — sin tabla propia)

**Nunca se persiste como tabla editable.** `goals` = conteo de `MatchEvent`
tipo `GOAL` por `player_id`. `matches_played` = conteo de `MatchLineup` por
`player_id` sobre partidos `finished`. Definido en
`specs/010-alineaciones-estadisticas`.
