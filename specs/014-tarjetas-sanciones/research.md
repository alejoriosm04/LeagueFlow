# Research: Tarjetas y sanciones disciplinarias

**Feature**: `014-tarjetas-sanciones` · **Date**: 2026-08-21

Sin `NEEDS CLARIFICATION`: el stack y el modelo vienen fijados por
`specs/001-fundacion-y-autenticacion` (AGENTS.md §5). La spec ya clarificó que
la suspensión es una marca derivada sin expiración. Lo que sigue son las
decisiones propias de esta HU, alineadas con `docs/plan-paralelo-013-017.md`.

## 1. La tarjeta es un `MatchEvent`, no una tabla nueva

**Decision**: ampliar el CHECK `ck_match_events_type_supported` y el
`Literal`/enum de schemas para admitir `YELLOW_CARD` y `RED_CARD`, además de
`GOAL`. Sin tabla `cards` ni entidad ORM nueva.

**Rationale**: FR-004 de `specs/009-registrar-goles` diseñó `type` como
`String(20)` + CHECK precisamente para crecer sin rediseño. El plan paralelo
acordó que esta HU es la dueña exclusiva del dominio `matches/` entre las
cinco del bloque; tocar el CHECK es el cambio mínimo y coherente. Una tabla
aparte duplicaría FKs, minuto, atribución y las mismas validaciones de
alineación/equipo.

**Alternatives considered**: tabla `disciplinary_cards`, descartada por
duplicar el modelo de evento y romper la promesa de FR-004 de 009; enum
PostgreSQL nativo, descartado por el mismo motivo que en 009 (`ALTER TYPE`
bloquea).

## 2. Registro de tarjetas reutiliza el patrón de goles

**Decision**: un método `MatchService.registrar_tarjeta` (o generalizar
`registrar_gol` a `registrar_evento` con tipo discriminado) que aplica las
mismas validaciones de estado, pertenencia al partido y alineación que el
gol. El cuerpo del `POST /matches/{id}/events` admite
`type ∈ {GOAL, YELLOW_CARD, RED_CARD}`; para goles se conserva el bloque
`consistency` del GET (solo cuenta `GOAL`).

**Rationale**: FR-002, FR-003 y FR-004 de esta spec son el mismo criterio que
FR-002/FR-003 de 009 (ya cerrado con alineaciones en 010). Inventar otro
endpoint o otro envelope rompería el Principio III y el contrato que el
frontend de eventos ya conoce. `team_id` sigue derivándose del jugador
(FR-006).

**Alternatives considered**: `POST /matches/{id}/cards` aparte, descartado por
partir el contrato de hechos del partido; exigir `team_id` en el cliente,
descartado por FR-006 y por el precedente de 009.

## 3. Suspensión en módulo `sanctions/`, derivada en lectura

**Decision**: módulo nuevo `backend/src/sanctions/` con reglas puras +
servicio que lee `MatchEvent` vía la interfaz pública de `MatchService` (o
consulta acotada expuesta por matches), sin importar el modelo ORM de
`matches` desde fuera. **Nunca** se persiste una bandera `is_suspended`.

**Rationale**: es el mismo patrón que `statistics/` respecto a partidos y
equipos (Principio VIII + Regla de Derivación). FR-007 exige recalcular en
cada lectura. Meter la derivación dentro de `matches/` mezclaría captura de
hechos con vista disciplinaria del jugador.

**Algoritmo (FR-007 + Assumptions)**:

```text
amarillas_distintos_partidos = |{ match_id | type = YELLOW_CARD }|
rojas = |{ eventos | type = RED_CARD }|
suspendido = (rojas >= 1) OR (amarillas_distintos_partidos >= 2)
```

Dos amarillas en el **mismo** partido cuentan como dos eventos en el conteo
total, pero un solo `match_id` para la acumulación → no disparan suspensión
por amarillas (Assumption de la spec).

**Alternatives considered**: columna `players.suspended`, descartada por
FR-007 y por la regla de no almacenar derivados; disparador SQL, descartado
por opacidad y por salirse del monolito explícito.

## 4. Ficha disciplinaria pública por jugador

**Decision**: `GET /players/{playerId}/discipline` (o `/sanctions`) sin
autenticación, en el router de `sanctions/`, montado desde `main.py`.
Respuesta: conteo de amarillas, conteo de rojas, `suspended: bool`.

**Rationale**: FR-008 y User Story 3. Colgarlo de `players/` mezclaría el
CRUD de plantilla con una vista derivada de eventos; colgarlo de `matches/`
obliga a conocer un partido para preguntar por un jugador. El 404 de jugador
inexistente reutiliza el código ya definido por 003/004.

**Alternatives considered**: embeber la ficha en `GET /players/{id}`,
descartado para no ensanchar el contrato de 004; exigir sesión, descartado
por FR-008 y por la convención de lecturas públicas de 001.

## 5. Migración: solo el CHECK; `down_revision` al merge

**Decision**: una migración que hace `DROP CONSTRAINT` /
`ADD CONSTRAINT` sobre `ck_match_events_type_supported` para incluir
`YELLOW_CARD` y `RED_CARD`. Generada contra `main` actual
(`down_revision` provisional = cabeza actual, hoy `919f3bd57721`). Al
abrir el PR, tras el merge de `013`, re-puntear según AGENTS.md
(orden `013 → 014 → 016 → 017`).

**Rationale**: no hay tabla nueva. El falso positivo de índices funcionales
de ligas/equipos puede aparecer en el autogenerate; hay que borrarlo del
diff (AGENTS.md). No usar `alembic merge heads` salvo último recurso.

**Alternatives considered**: migración que recrea la tabla, descartada por
riesgo e innecesaria; dejar el CHECK en modelo sin migrar, descartado porque
PostgreSQL rechazaría inserts de tarjetas.

## 6. Alcance de escritura y de UI

**Decision**: escritura con rol operador u organizador (mismo que goles).
Frontend: formulario de tarjeta en la ficha del partido (junto a goles) y
página/ruta pública de ficha disciplinaria del jugador. Sin edición ni
borrado de tarjetas (Out of Scope de la spec).

**Rationale**: la spec no pide corrección auditada de tarjetas; inventarla
violaria el Principio I. La suspensión no bloquea alineaciones (Assumption /
Out of Scope): la UI de disciplina informa, no interviene en el flujo de 010.

**Alternatives considered**: bloquear alineación de suspendidos, descartado
explícitamente por la spec; `DELETE` de tarjeta, descartado por fuera de
alcance.
