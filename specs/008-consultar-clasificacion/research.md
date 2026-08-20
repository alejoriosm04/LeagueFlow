# Research: Consultar la clasificación

**Feature**: `008-consultar-clasificacion` · **Date**: 2026-08-20

Sin `NEEDS CLARIFICATION` pendientes: el stack y el modelo de dominio vienen
fijados por `specs/001-fundacion-y-autenticacion` (AGENTS.md §5) y las
ambigüedades del dominio quedaron cerradas como *Assumptions* en `spec.md`.
Lo que sigue son las decisiones propias de esta HU.

## 1. Derivar en lectura, no materializar

**Decision**: la clasificación se calcula en cada consulta a partir de los
partidos `finished` de la liga. No hay tabla `standings`, ni columnas de puntos
en `teams`, ni migración.

**Rationale**: cumple FR-001 y FR-002 por construcción — no existe fila que
alguien pueda editar, ni por endpoint, ni por panel, ni por SQL. También
resuelve SC-002 sin trabajo extra: si no hay copia almacenada, no hay copia
que quede desactualizada tras registrar un resultado o aprobar una corrección.
El volumen es trivial (20 equipos, 190 partidos; ver §8).

**Alternatives considered**: tabla materializada actualizada por evento,
descartada porque la constitución la admite solo si es reconstruible y probada,
y aquí ese coste no compra nada al volumen del proyecto; vista materializada de
PostgreSQL, descartada porque exige un `REFRESH` explícito y eso es
exactamente el "recálculo manual" que SC-002 prohíbe.

## 2. Interfaz: recurso público y sin paginación

**Decision**: `GET /api/v1/leagues/{leagueId}/standings`, sin autenticación,
que devuelve la tabla completa en `items` sin `page`/`page_size`/`total`.

**Rationale**: FR-008 la hace pública, como el calendario de 007. La
clasificación es una unidad indivisible: media tabla no es una clasificación, y
las posiciones solo tienen sentido sobre el conjunto ordenado completo. Con 20
equipos por liga el tamaño de respuesta es irrelevante.

**Alternatives considered**: envelope paginado como en 005/007, descartado
porque paginar un ranking obliga al cliente a reensamblarlo para poder leerlo;
calcular la tabla en el navegador desde `GET /leagues/{id}/matches`, descartado
porque duplicaría la regla de negocio en dos lenguajes y dejaría el cálculo
fuera del alcance de los tests de backend (Principio II).

## 3. Qué equipos ocupan una fila

**Decision**: todos los equipos `active` de la liga, más los `inactive` con al
menos un partido `finished`. Un equipo sin partidos jugados aparece con ceros.

**Rationale**: un equipo recién inscrito debe verse en la tabla desde el primer
día. Y omitir un equipo inactivo con historial rompería la aritmética visible:
sus rivales conservan puntos ganados contra un equipo que no aparece.

**Alternatives considered**: solo equipos con partidos jugados, descartado
porque al inicio de temporada la tabla estaría vacía pese a haber liga; todos
los equipos incluidos los inactivos sin historial, descartado porque muestra
como participante a un equipo que nunca jugó y ya fue dado de baja.

## 4. Orden determinista y estable

**Decision**: ordenar por `points DESC`, `goal_difference DESC`,
`goals_for DESC`, `lower(trim(name)) ASC` y, como último recurso, `team_id ASC`.
La posición (`position`) es 1..N según ese orden.

**Rationale**: FR-005 fija los tres primeros criterios y FR-006 exige que un
empate absoluto se resuelva de forma determinista y repetible. El índice único
`ix_teams_unique_league_name` ya garantiza que dos equipos de la misma liga no
comparten nombre normalizado, así que el cuarto criterio siempre desempata; el
`team_id` queda como red de seguridad para que el orden nunca dependa de la
colación ni del plan de ejecución.

**Alternatives considered**: dejar el empate sin resolver y aceptar el orden
que devuelva la base, descartado porque viola FR-006; enfrentamiento directo
como primer desempate, descartado porque la spec no lo pide y añadiría una
regla que nadie escribió.

## 5. Cálculo como función pura

**Decision**: `StandingsCalculator` es una función pura
`calcular_clasificacion(equipos, partidos) -> list[StandingsRow]`, sin sesión de
base de datos. El servicio obtiene los datos y delega el cálculo.

**Rationale**: es literalmente el flujo que la constitución exige
(`MatchResult -> StandingsCalculator -> Standings`) y permite cubrir los seis
acceptance scenarios y los desempates con tests unitarios rápidos, sin montar
PostgreSQL. `backend/tests/unit/` existe y está vacío: esta es su HU.

**Alternatives considered**: agregar todo en una sola sentencia SQL con
`GROUP BY`, descartado porque alcanzaría la tabla `matches` de otro dominio
(§6) y porque probar reglas de puntuación contra SQL es mucho más caro que
contra una función.

## 6. Cruce entre dominios por la interfaz del servicio

**Decision**: `statistics` no importa los modelos `Match` ni `Team`. Consume
`MatchService.listar_finalizados(league_id)` y
`TeamService.listar_por_liga(league_id)`, dos métodos nuevos que amplían la
interfaz pública de esos dominios sin cambiar ninguno existente.

**Rationale**: Principio VIII prohíbe alcanzar tablas o modelos internos de
otro dominio, y es el patrón que ya siguen `MatchService -> TeamService` y
`MatchService -> LeagueService` en el código actual. Los métodos existentes
(`listar_partidos`, `listar_equipos`) están paginados y forzarlos con un
`page_size` enorme sería un abuso de su contrato.

**Alternatives considered**: reutilizar los métodos paginados, descartado por
lo anterior; que `statistics` consulte directamente los modelos, descartado por
Principio VIII.

## 7. Cómo se prueba que la tabla no se puede editar (FR-002)

**Decision**: además de no implementar escrituras, un test de contrato afirma
que `POST`, `PUT`, `PATCH` y `DELETE` sobre `/leagues/{id}/standings` responden
`405`, y un test de integración verifica que corregir el marcador de un partido
es la única vía por la que cambia la tabla.

**Rationale**: FR-002 y el Acceptance Scenario 6 son requisitos negativos, y un
requisito negativo sin prueba es una promesa. El `405` es la evidencia de que
el router no expone verbo de escritura alguno.

**Alternatives considered**: dar FR-002 por cumplido "porque no hay código que
lo permita", descartado por Principio II — una regresión futura que añadiera un
endpoint no sería detectada por ninguna prueba.

## 8. Estados que no suman y criterios medibles

**Decision**: solo `finished` contribuye; `scheduled`, `in_progress` y
`cancelled` se ignoran (FR-001, FR-007). SC-001 se verifica con casos
unitarios calculados a mano, incluidos los tres niveles de desempate. SC-003 se
mide sobre la liga de 20 equipos y 190 partidos que ya genera
`backend/scripts/seed_calendar_performance.py`, reutilizándola tal cual.

**Rationale**: `cancelled` está en el enum de `Match` desde 005 aunque ningún
endpoint lo produzca todavía; el test lo fija por fixture para que la regla
quede cubierta antes de que exista quien la dispare. Reutilizar el script de
007 evita un segundo generador de datos que mantener: ya produce round robin
completo de 20 equipos con la mitad de los partidos `finished` y con marcador,
es decir 20 filas alimentadas por unos 95 resultados y 95 partidos que la
consulta debe descartar — justo el escenario de FR-001 a escala de SC-003.

**Alternatives considered**: un script nuevo de datos para esta HU, descartado
por duplicación; medir solo el tiempo del endpoint, descartado porque SC-003
habla de la vista mostrada, no de la respuesta HTTP.
