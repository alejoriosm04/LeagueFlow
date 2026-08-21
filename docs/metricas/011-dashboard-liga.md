# Métricas — HU 011: Dashboard general de la liga

**Spec**: `specs/011-dashboard-liga/spec.md` · **Responsable**: <nombre> · **Cerrada**: 2026-08-20

## Llenado por el agente (al terminar la HU, antes del PR)

| Métrica | Valor |
|---|---|
| Tareas en `tasks.md` (total) | 19 |
| Tareas completadas | 18 (T017 queda abierta: la medición real de SC-002 con navegador/hardware requiere el entorno de la persona — ver Observaciones) |
| Tests escritos (backend) | 12 funciones de prueba nuevas (4 contrato, 8 integración) + 1 fixture (`dashboard_resumen`) |
| Tests escritos (frontend) | 7 |
| Tests en verde al cerrar | Backend: 217 recolectados, 215 en verde localmente (12 nuevos del dashboard incluidos); 2 fallos preexistentes, ajenos a esta HU (ver Observaciones). Frontend: 51 en verde (7 nuevos) |
| Ciclos de corrección | 7 |
| Archivos de código creados/modificados | 13 (7 modificados, 6 nuevos; no cuenta `specs/011-*` ni este archivo) |

**Ciclos de corrección**: cuántas veces hubo que volver sobre algo ya dado por
terminado (test que falló tras implementar, requisito mal interpretado,
refactor por un choque con otra HU). Cuenta honesta, no aspiracional: `0` es
sospechoso en una HU no trivial.

**Qué se reprocesó y por qué** (una línea por ciclo; es el dato más valioso
para la comparativa SDD vs. prompts sueltos del caso de negocio):

- `/speckit-analyze` detectó que `DashboardPage` no tendría forma de mostrar
  nombres de equipo (`Match` solo trae `home_team_id`/`away_team_id`) y que
  `tasks.md` atribuía mal el tipo `Team` a `matches/api.ts` en vez de
  `teams/api.ts`; se corrigió `tasks.md` antes de escribir código, evitando
  implementar una página que mostraría UUIDs crudos.
- `/speckit-analyze` detectó un conflicto entre AS2 ("cada bloque vacío") y la
  Assumption ya escrita sobre equipos con ceros; se dividió en dos escenarios
  (AS2 sin equipos ni partidos, AS5 con equipos sin partidos) y se propagó a
  `tasks.md` y `quickstart.md`.
- `/speckit-analyze` detectó que `contracts/dashboard.openapi.yaml` no
  declaraba el `400` que `tasks.md` ya exigía probar; se añadió al contrato.
- `/speckit-checklist` (`acceptance.md`, 21 ítems) encontró 10 huecos
  adicionales de especificación tras revisar cada uno a pedido explícito del
  usuario: orden no explícita en FR-001, comportamiento de bloque parcial sin
  definir, "coherente con las vistas de detalle" sin criterio objetivo,
  FR-002 sin distinguir éxito de error, SC-001 con doble ancla de interacción
  ("llega a la plataforma" vs. "desde el dashboard"), SC-002 sin punto de
  medición ni alcance (por bloque vs. combinado), y ningún requisito sobre
  qué ve un usuario autenticado. Los 10 motivaron ediciones reales en
  `spec.md`, `tasks.md` y `quickstart.md` antes de tocar código.
- En la fase roja del frontend, la primera versión de
  `dashboard.test.tsx` afirmaba `getAllByRole('link', { name: /Tigres/ })`
  con longitud 5, pero como el fixture de prueba usaba el mismo par de
  equipos en recientes y próximos, la regex capturaba ambos bloques (10, no
  5); se corrigió acotando la búsqueda con `within()` a cada `<section>`.
- `uv run ruff format` reformateó 3 archivos nuevos (`conftest.py`,
  `test_dashboard_contract.py`, `test_dashboard.py`) antes de que el gate de
  formato pasara.
- Sin PostgreSQL disponible en el entorno de ejecución (sin servicio local,
  sin Docker), hubo que diseñar y validar una estrategia de verificación
  alternativa (SQLite vía `aiosqlite` como sustituto local, con
  `DATABASE_URL` sobrescrito) antes de poder correr un solo test; en el
  camino se diagnosticaron y descartaron como no atribuibles a esta HU tres
  artefactos propios de SQLite (ver Observaciones).

## Llenado por la persona (dos números, al cerrar)

| Métrica | Valor |
|---|---|
| Tiempo real de trabajo — spec + plan + tasks | <ej. 45 min> |
| Tiempo real de trabajo — implement + tests | <ej. 2 h> |
| Costo IA aproximado de la HU | <del panel de uso de tu herramienta> |

## Observaciones

**Sin PostgreSQL en el entorno de esta sesión.** No había servicio local, ni
Docker, ni `DATABASE_URL` alcanzable. Con autorización explícita del usuario,
la verificación se hizo contra SQLite (`aiosqlite`) como sustituto local,
sobrescribiendo `DATABASE_URL` solo para estos comandos (nunca commiteado).
Esto expuso tres diferencias de dialecto **preexistentes, ajenas a esta HU**:

1. `DateTime(timezone=True)` pierde el `tzinfo` al volver de SQLite, y
   `auth/service.py:108` compara eso contra un `datetime.now(UTC)` con
   tzinfo — revienta en cualquier request autenticado. Se aplicó un parche de
   una línea *solo para verificar localmente* y se revirtió con
   `git checkout` antes de cerrar (no queda en el diff). En Postgres real
   (asyncpg) esto no ocurre: la columna vuelve tz-aware.
2. `ix_corrections_one_pending_per_match` usa `postgresql_where=...` (índice
   parcial); SQLAlchemy ignora ese argumento fuera de Postgres, así que en
   SQLite se vuelve un índice único total y rechaza una segunda solicitud de
   corrección aunque la primera ya esté decidida. Rompe
   `test_result_corrections.py::test_aprobar_aplica_y_rechazar_conserva`
   (archivo que esta HU no toca).
3. `with_for_update()` no tiene el mismo bloqueo por fila en SQLite que en
   Postgres; el test de dos registros de resultado concurrentes
   (`test_results.py::test_dos_registros_concurrentes_solo_aplican_uno`)
   espera un `200`/`409` y obtiene `200`/`200` bajo SQLite.

Ninguno de los tres toca archivos de esta HU ni su lógica; los 12 tests
nuevos del dashboard, y los 33 de la regresión base de 007/008 (T001), pasan
limpio. Se recomienda que la persona responsable corra
`uv run pytest` completo contra Postgres real antes de mezclar, para
confirmar que estos dos fallos no aparecen ahí (la expectativa, justificada
arriba, es que no aparezcan).

**Migración**: `5532b23cfb95_indice_matches_liga_status_fecha.py` se escribió
a mano (no vía `alembic revision --autogenerate`, que necesita una BD real
para diffear) siguiendo el patrón exacto de las dos migraciones de índice ya
existentes en el proyecto. Se verificó que la cadena de revisiones resuelve
sin bifurcaciones (`alembic history`/`heads`, un solo head) y que el archivo
generado no toca ningún índice de specs anteriores — por construcción, al
haberse escrito a mano en vez de generado, no hay riesgo del gotcha de
índices funcionales de `AGENTS.md`. No se pudo reproducir el `alembic upgrade
head` completo contra una BD real en este entorno (la migración anterior,
`d6e7f8a9b0c1`, usa `ALTER` de constraints que SQLite no soporta — limitación
preexistente del sustituto local, no de esta HU).

**T017 (quickstart + SC-002) queda abierta.** Los siete escenarios
funcionales de `quickstart.md` están cubiertos por los tests automatizados
(T003–T005), pero la medición cronometrada de SC-002 ("menos de 2 segundos
para 20 equipos y 190 partidos", con navegador real y
`scripts/seed_calendar_performance.py` contra Postgres) exige el entorno de
quien cierre la HU — `AGENTS.md` y las Notes de `tasks.md` son explícitas en
que SC-001/SC-002 "requieren evidencia observada; nunca se inventan cifras".
El índice `ix_matches_league_status_scheduled` (T006/T007) queda listo para
esa medición.

**Reutilización de 007/008 verificada, no solo declarada.**
`test_top_standings_son_las_5_primeras_filas_en_orden` y las dos pruebas
equivalentes de calendario comparan la respuesta del dashboard contra
`GET /matches`/`GET /standings` reales en la misma prueba, no contra valores
fijos — si `DashboardService` reimplementara el filtro/orden/cálculo en vez
de llamar a `MatchService`/`StandingsService`, esas tres pruebas fallarían
aunque los números "parecieran" correctos.
