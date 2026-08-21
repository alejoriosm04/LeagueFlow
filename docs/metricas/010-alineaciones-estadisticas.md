# Métricas — HU 010: Registrar alineaciones y consultar estadísticas de jugadores

**Spec**: `specs/010-alineaciones-estadisticas/spec.md` · **Responsable**: <nombre> · **Cerrada**: 2026-08-20

## Llenado por el agente (al terminar la HU, antes del PR)

| Métrica | Valor |
|---|---|
| Tareas en `tasks.md` (total) | 29 |
| Tareas completadas | 23 (6 bloqueadas por falta de PostgreSQL en el entorno de ejecución; ver Observaciones) |
| Tests escritos (backend) | 44 funciones de prueba (9 unit, 10 contrato, 25 integración) |
| Tests escritos (frontend) | 8 nuevos (`statistics.test.tsx`) + 1 fixture corregida en una suite existente (`events.test.tsx`, sin tests nuevos ahí) |
| Tests en verde al cerrar | Frontend: 52/52 (`npx vitest run`, suite completa). Backend: no ejecutable en este entorno (sin PostgreSQL); revisados manualmente y verificados por lint, `ruff check`/`format`, compilación y generación del schema OpenAPI de la app viva |
| Ciclos de corrección | 4 |
| Archivos de código creados/modificados | 23 (13 modificados + 10 nuevos, sin contar los artefactos de planificación) |

**Ciclos de corrección**: cuántas veces hubo que volver sobre algo ya dado por
terminado (test que falló tras implementar, requisito mal interpretado,
refactor por un choque con otra HU). Cuenta honesta, no aspiracional: `0` es
sospechoso en una HU no trivial.

**Qué se reprocesó y por qué** (una línea por ciclo; es el dato más valioso
para la comparativa SDD vs. prompts sueltos del caso de negocio):

- El gate de checklist (`checklists/alineaciones-estadisticas.md`, 25 ítems) estaba en 0/25 revisado al iniciar `/speckit-implement`. Se revisó honestamente contra `spec.md`, `research.md`, `data-model.md` y `plan.md`: 22/25 quedaron satisfechos; 3 gaps reales se dejaron documentados y sin marcar (SC-002 sin protocolo de prueba de usabilidad; falta un acceptance scenario explícito de "corregir alineación"; falta un escenario de "partido inexistente" en spec.md aunque el contrato sí lo cubre) porque ninguno bloqueaba la implementación.
- `lineup_rules.validar_lado_de_alineacion` se escribió primero con un parámetro `ids_solicitados` que solo servía para mantener la iteración 1:1 con `del id_solicitado` al final del bucle — código muerto disfrazado. Al revisarlo se eliminó el parámetro y hubo que retocar la función, sus dos llamadas en `matches/service.py` y cuatro llamadas en `tests/unit/test_lineup_rules.py`.
- Extender `MatchDetailPage.tsx` para cargar la alineación rompió `events.test.tsx` (spec 009): su `stubFetch` no tenía handler para `GET /matches/m1/lineup`, así que el `Promise.all` de la página fallaba y las 6 pruebas de esa suite mostraban el error genérico de carga. Se corrigió agregando el handler faltante al stub existente, sin tocar sus aserciones.
- `UpsertLineupInput` se escribió primero con `home_player_ids`/`away_player_ids` opcionales (`default_factory=list`), pero el contrato `lineups-statistics.openapi.yaml` los declara `required`. Se corrigió el schema para exigirlos explícitamente y devolver `400 validation_error` si el cliente los omite, en vez de asumir listas vacías.

## Llenado por la persona (dos números, al cerrar)

| Métrica | Valor |
|---|---|
| Tiempo real de trabajo — spec + plan + tasks | <ej. 45 min> |
| Tiempo real de trabajo — implement + tests | <ej. 2 h> |
| Costo IA aproximado de la HU | <del panel de uso de tu herramienta> |

## Observaciones

**Bloqueo de entorno (no es una regresión de esta HU)**: el sandbox de
ejecución no tiene PostgreSQL disponible (ni `docker`, ni `psql`, ni un
servicio Windows de Postgres), y `backend/tests/conftest.py` tiene un fixture
`autouse` (`base_limpia`) que exige una conexión real incluso para pruebas
unitarias puras. Se confirmó que el problema es del entorno y no del código de
esta HU ejecutando primero la suite *preexistente* (`test_players.py`,
`test_goal_rules.py`, `test_standings_calculator.py`, sin relación con esta
HU): falla exactamente igual con `ConnectionRefusedError`. En consecuencia:
T001, T003 (validación real de la migración), T024 (verificación de la
suite backend), T026 y T027 quedaron sin poder ejecutarse en este pase y
están señalados como pendientes en `tasks.md`. Lo que sí se verificó sin base
de datos: `ruff check`/`ruff format --check` en verde, el módulo importa y la
app genera su schema OpenAPI completo (incluye los 3 endpoints nuevos con los
tipos Pydantic correctos), y la migración compila y encadena sobre el head
existente. **Antes de mergear, alguien con Postgres local o el pipeline de CI
debe correr `uv run pytest tests/unit tests/contract tests/integration` y
`alembic upgrade head && alembic downgrade -1 && alembic upgrade head`.**

**Dos contradicciones entre los artefactos de planificación de esta misma HU
—generados antes de este pase de implementación— se resolvieron a favor del
contrato committeado** (Principio III, "Contratos de API Explícitos" es la
fuente de verdad de forma):

- `research.md` (Decisión 4) prometía un campo estructurado
  `conflicting_player_ids` en el 409 de `lineup_conflicts_with_events`, pero
  `contracts/lineups-statistics.openapi.yaml` solo declara el `ErrorEnvelope`
  genérico `{code,message,field}` —el mismo que usa todo el proyecto— sin ese
  campo. Se optó por no romper el envelope compartido: los ids conflictivos
  van en `message`, legible pero no parseable como lista. Documentado en el
  docstring de `detectar_conflicto_con_eventos`.
- `spec.md` (FR-004) pide exponer el estado "con `lineup_status`", pero
  `data-model.md` y el contrato ya convergían en el nombre `status` (anidado
  en `MatchLineupView`). Se implementó `status` por ser lo committeado y
  verificable por contrato; queda anotado por si una revisión humana prefiere
  renombrar el campo para alinear la letra de la spec.

**Tabla de goleadores**: la spec no aclara si debe listar a todos los
jugadores de la liga (incluidos los de cero goles) o solo a quienes anotaron.
Se implementó mostrando solo jugadores con `goals >= 1` —lectura convencional
de "tabla de *goleadores*"— documentado en el propio método
`tabla_goleadores` y enlazado a los gaps CHK015/CHK024 del checklist.

**Deuda heredada de `specs/009` cerrada**: `MatchService.jugadores_alineados`
dejó de devolver siempre `None` y ahora consulta `match_lineups` de verdad;
se agregó la prueba de integración pendiente
(`test_gol_de_jugador_fuera_de_la_alineacion_registrada_es_rechazado`) que
009 había dejado documentada como hueco permanente sin esta HU.
