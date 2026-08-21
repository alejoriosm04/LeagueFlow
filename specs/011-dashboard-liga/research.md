# Research: Dashboard general de la liga

**Feature**: `011-dashboard-liga` · **Date**: 2026-08-20

No quedan `NEEDS CLARIFICATION` en `spec.md`: la spec fija sus tres bloques
(FR-001), el estado vacío (FR-002) y el acceso público (FR-003), y declara
explícitamente que hereda edge cases de `specs/007-*` y `specs/008-*`. Este
documento resuelve las decisiones de diseño que el prompt de planificación
pidió explícitamente.

## 1. Un único endpoint que compone, no reimplementa

**Decision**: `GET /leagues/{leagueId}/dashboard` devuelve un único objeto
`DashboardSummary` con tres listas (`recent_matches`, `upcoming_matches`,
`top_standings`). El endpoint vive en el módulo `statistics` ya existente
(`backend/src/statistics/`), como una tercera clase de servicio
(`DashboardService`) junto a `StandingsService`, siguiendo el mismo patrón que
`specs/010-alineaciones-estadisticas` usó para añadir estadísticas de
jugadores: extiende `router.py`/`schemas.py`/`service.py` existentes en vez de
crear un módulo nuevo.

**Rationale**: la spec no crea entidades ni dominio nuevo (Key Entities:
"Ninguna entidad nueva"); `statistics` es el módulo que la constitución y el
plan de 001 ya reservan para vistas derivadas de solo lectura sobre
`Match`/`Team` ("Standings, PlayerStatistics — specs/008, 010, 011"). Crear un
cuarto módulo `dashboard/` para una sola vista de agregación violaría el
Principio VIII (no introducir fronteras artificiales) sin ganar nada, porque
el dashboard no tiene reglas de negocio propias que aislar.

**Alternatives considered**: (a) tres llamadas separadas desde el frontend a
`/matches?status=finished`, `/matches?status=scheduled` y `/standings` —
descartado porque el prompt pide explícitamente "un único endpoint" y porque
obliga al frontend a orquestar 3 round-trips en vez de 1, empeorando SC-002;
(b) un módulo `backend/src/dashboard/` nuevo — descartado por Principio VIII,
como se explica arriba.

## 2. Reutilizar `MatchService` y `StandingsService` tal cual

**Decision**: `DashboardService.obtener_resumen(league_id)` hace exactamente
tres llamadas a interfaces de dominio ya existentes y probadas, sin
reimplementar filtros, orden ni cálculo:

```python
recientes, _ = await MatchService(db).listar_partidos(
    league_id, page=1, page_size=5, match_status="finished"
)  # 007: status="finished" ya ordena scheduled_at DESC — los últimos 5 jugados
proximos, _ = await MatchService(db).listar_partidos(
    league_id, page=1, page_size=5, match_status="scheduled"
)  # 007: cualquier status != "finished" ordena scheduled_at ASC — los próximos 5
clasificacion = await StandingsService(db).obtener_clasificacion(league_id)
# 008: tabla completa ya ordenada por FR-005/FR-006; el dashboard toma items[:5]
```

`listar_partidos` ya soporta `page`/`page_size`/`status` sin cambios de firma
(spec 007); `obtener_clasificacion` ya deriva la tabla completa ordenada (spec
008). El dashboard no añade una sola cláusula `WHERE` ni `ORDER BY` propia:
solo pide páginas de 5 y recorta la tabla a los primeros 5 elementos.

**Rationale**: es literalmente el requisito 2 del prompt de planificación —
"reutilizar la lógica ya implementada... en vez de duplicar las consultas o
los cálculos". Reimplementar el filtro/orden de partidos o el cálculo de
puntos en el dashboard crearía dos fuentes de verdad para la misma regla, y
una futura corrección en 007/008 (p. ej. un cambio de criterio de desempate)
dejaría de reflejarse aquí — justo lo que el Principio IV prohíbe arriesgar.

**Alternatives considered**: una consulta SQL agregada nueva (`UNION` de
partidos + subconsulta de standings) que traiga los tres bloques en un solo
`SELECT` — descartado: exigiría reimplementar en SQL crudo la regla de
puntuación y desempate de `calcular_clasificacion` (función pura ya probada en
`tests/unit/test_standings_calculator.py`), duplicando exactamente la lógica
que este requisito prohíbe duplicar, a cambio de un ahorro de latencia
irrelevante a esta escala (§4).

**Costo aceptado**: cada una de las tres llamadas valida la existencia de la
liga por su cuenta (`_exigir_liga`, un `SELECT` por PK indexada), así que el
dashboard ejecuta esa validación hasta 4 veces (dos veces en `listar_partidos`,
y dos más dentro de `StandingsService`: una en `TeamService.listar_por_liga` y
otra en `MatchService.listar_finalizados`). No se introduce un
`_exigir_liga` compartido a nivel de `DashboardService` para evitarlo: hacerlo
obligaría a que `MatchService`/`TeamService`/`StandingsService` confiaran en
una validación externa, rompiendo su garantía actual de ser seguros de llamar
de forma independiente. El costo real es una lectura por clave primaria
repetida 4 veces (sub-milisegundo cada una); es barato comparado con el
riesgo de acoplar servicios de dominios distintos por una optimización que
§4 muestra innecesaria.

## 3. Estado vacío: sin sentinelas, listas vacías tal cual las devuelven 007/008

**Decision**: no se introduce ningún campo `is_empty` ni estado especial. Cada
bloque expone directamente lo que su servicio de origen ya produce cuando no
hay datos:

- `recent_matches: []` cuando `listar_partidos(..., "finished")` no encuentra
  partidos finalizados (mismo comportamiento que ya prueba
  `tests/integration/test_calendar.py` para el calendario).
- `upcoming_matches: []` cuando no hay partidos `scheduled`.
- `top_standings: []` solo si la liga no tiene ningún equipo; si tiene equipos
  activos sin partidos jugados, aparecen con todos los contadores en cero
  (comportamiento ya definido y probado por 008, Assumption "Equipos que
  aparecen en la tabla").

**Rationale**: FR-002 exige un estado vacío "legible", no un contrato nuevo.
Un arreglo JSON vacío es ya distinguible sin ambigüedad de un error (la
respuesta sigue siendo `200` con el envelope de éxito, nunca `4xx`/`5xx`); el
frontend renderiza el mensaje ("Aún no hay partidos jugados", "Aún no hay
próximos partidos", "Aún no hay equipos") por bloque cuando su lista
respectiva llega vacía, igual que ya hace `MatchesPage` de 007 para sus dos
grupos. Introducir un sentinela adicional (`{"empty": true}`) duplicaría una
señal que `items.length === 0` ya da gratis y que el contrato de 007/008 ya
estableció como el idioma del proyecto para "sin datos".

**Alternatives considered**: devolver `null` en vez de `[]` — descartado,
inconsistente con `PaginatedMatches`/`Standings` existentes, que siempre usan
arreglo vacío; añadir un código HTTP distinto (`204`) cuando los tres bloques
están vacíos — descartado, porque la liga sí existe y sí hay una respuesta
válida que mostrar (un dashboard con sus tres estados vacíos es contenido, no
ausencia de contenido), y porque complicaría al cliente distinguir "vacío" de
"error de red".

## 4. Rendimiento: índice compuesto sobre `matches`, sin tocar el modelo

**Decision**: se añade un índice compuesto no único
`ix_matches_league_status_scheduled` sobre `matches(league_id, status,
scheduled_at)`, vía una migración Alembic nueva y aditiva. No se modifica
ninguna columna, constraint ni entidad de `Match` — solo se declara un índice
adicional en `__table_args__`, igual que ya hicieron `009`/`010` con
`ix_match_events_match_minute` e `ix_corrections_match_created` sobre otras
tablas del mismo dominio.

**Rationale — por qué hace falta**: hoy `matches` no tiene ningún índice más
allá de la clave primaria (confirmado en
`backend/alembic/versions/b2c3d4e5f6a7_crear_tabla_matches.py`, que solo
declara `PrimaryKeyConstraint("id")`). Tanto `listar_partidos` (007, que este
dashboard reutiliza dos veces) como `listar_finalizados` (008, reutilizado a
través de `StandingsService`) ejecutan
`WHERE league_id = :id [AND status = :status] ORDER BY scheduled_at`. El
dashboard cuadruplica, en una sola petición, el número de consultas que tocan
`matches` respecto a abrir el calendario o la clasificación por separado
(dos llamadas a `listar_partidos` más una a `listar_finalizados`). El índice
compuesto cubre el filtro completo y el `ORDER BY` sin ordenamiento adicional
en memoria, y es el mismo índice para las tres consultas: no es específico del
dashboard, refuerza directamente los dos métodos que ya existían.

**Por qué no es estrictamente necesario a la escala de referencia**: con 190
partidos por liga (y hasta 10 ligas simultáneas según el `Scale/Scope` de
001, es decir ≤ 1900 filas totales en `matches`), un *sequential scan*
filtrado por `league_id` ya es del orden de milisegundos en PostgreSQL — 007 y
008 alcanzan sus propios SC-001/SC-003 (<2s) hoy sin este índice. El índice no
es la variable que decide si se cumple SC-002; se añade porque es aditivo,
gratuito en riesgo (no reescribe filas, no cambia semántica, se revierte con
un solo `DROP INDEX`) y dejar sentado el plan de consulta correcto antes de
que el volumen crezca es más barato ahora que como migración de emergencia
después.

**Estrategia de consulta**: ninguna otra. Se reutilizan `listar_partidos` y
`obtener_clasificacion` sin paginación adicional, sin `JOIN` nuevo y sin
consulta agregada propia (ver §2). No se ejecutan las tres consultas en
paralelo: las tres comparten la misma `AsyncSession` de SQLAlchemy por
petición (patrón ya establecido en `src/core/db.py`), y una sesión async de
SQLAlchemy no soporta operaciones concurrentes sobre la misma conexión: deben
ejecutarse en secuencia dentro de `DashboardService`. A la escala de
referencia (consultas de sub-10ms cada una sobre datos indexados) esto es
irrelevante para el presupuesto de 2 segundos, que además incluye el
round-trip de red y el render del frontend, no solo el tiempo de base de
datos.

**Alternatives considered**: materializar el dashboard en una tabla/caché —
descartado, viola la Regla de Derivación de Estadísticas de la constitución
(`Standings` y ahora el dashboard SIEMPRE se derivan en lectura, nunca se
persisten); paralelizar las tres consultas con sesiones de BD independientes —
descartado, añade complejidad de pool de conexiones para un ahorro de
milisegundos que el índice ya vuelve innecesario, y las tres consultas de
todas formas dependen de la misma respuesta HTTP.

## 5. Reutilizar el script de datos de rendimiento existente

**Decision**: la validación de SC-002 reutiliza
`backend/scripts/seed_calendar_performance.py` tal cual (mismo script que ya
usan 007/SC-001 y 008/SC-003), sin crear un generador nuevo.

**Rationale**: ya produce exactamente el escenario de referencia — 20 equipos,
190 partidos en round-robin, con una porción `finished` (con marcador) y otra
`scheduled` — que es precisamente lo que necesitan los tres bloques del
dashboard a la vez. Duplicar este script violaría la misma regla de "no
duplicar" que motiva §2.
