# Métricas — HU 008: Consultar la clasificación

**Spec**: `specs/008-consultar-clasificacion/spec.md` · **Responsable**: <nombre> · **Cerrada**: 2026-08-20

## Llenado por el agente (al terminar la HU, antes del PR)

| Métrica | Valor |
|---|---|
| Tareas en `tasks.md` (total) | 22 |
| Tareas completadas | 22 |
| Tests escritos (backend) | 31 funciones de prueba; 36 casos recolectados (14 unit, 10 contrato, 12 integración) |
| Tests escritos (frontend) | 6 |
| Tests en verde al cerrar | 163 backend (74 unit+contrato, 89 integración) + 38 frontend |
| Ciclos de corrección | 6 |
| Archivos de código creados/modificados | 16 |

**Ciclos de corrección**: cuántas veces hubo que volver sobre algo ya dado por
terminado (test que falló tras implementar, requisito mal interpretado,
refactor por un choque con otra HU). Cuenta honesta, no aspiracional: `0` es
sospechoso en una HU no trivial.

**Qué se reprocesó y por qué** (una línea por ciclo; es el dato más valioso
para la comparativa SDD vs. prompts sueltos del caso de negocio):

- `research.md` §8 afirmaba que el generador de datos de 007 solo creaba partidos `scheduled`; al leer el script se vio que la mitad son `finished` con marcador, y hubo que reescribir la justificación de por qué sirve para medir SC-003.
- `/speckit-analyze` detectó que el contrato prometía el envelope compartido en el `405`, pero ese status lo emite el router del framework y `core/errors.py` no lo traduce: se corrigió el contrato y la tarea T004 antes de escribir el test, que si no habría afirmado un cuerpo inexistente.
- `/speckit-analyze` detectó una contradicción de conteo de columnas dentro de `tasks.md` (8 estadísticas de FR-004 vs. 11 propiedades del contrato vs. 10 encabezados de la tabla); se separaron los tres conceptos.
- `/speckit-analyze` detectó que el edge case de correcciones pendientes tenía Assumption escrita pero ninguna aserción: se amplió T005 con el caso `pending`.
- En la fase roja, `test_consultas_sucesivas_devuelven_el_mismo_orden` pasaba en vacío porque comparaba dos respuestas `404` idénticas; se reforzó exigiendo `200` y filas no vacías antes de comparar.
- Limpiezas menores tras las compuertas: campo muerto `puntos` en el dataclass `_Acumulado` y una línea de 101 caracteres que rompía Ruff E501 en las pruebas unitarias.

## Llenado por la persona (dos números, al cerrar)

| Métrica | Valor |
|---|---|
| Tiempo real de trabajo — spec + plan + tasks | <ej. 45 min> |
| Tiempo real de trabajo — implement + tests | <ej. 2 h> |
| Costo IA aproximado de la HU | <del panel de uso de tu herramienta> |

## Observaciones

La HU no añade entidades, dependencias ni migraciones: `Standings` se deriva en
cada lectura desde los partidos `finished`, de modo que FR-002 (nadie puede
editar la tabla) se cumple por construcción y SC-002 (reflejo inmediato) no
necesita ningún mecanismo de invalidación. Estrena el módulo `backend/src/statistics/`,
reservado por la constitución y hasta ahora vacío, y también `backend/tests/unit/`,
que llevaba siete HU sin un solo archivo: toda la regla de puntuación y
desempate se prueba contra una función pura, sin base de datos.

SC-001 se verifica comparando la tabla del sistema con la tabla calculada a mano
que documenta la fixture `clasificacion_liga`; el escenario incluye un caso que
no era obvio al redactar la spec: un equipo sin partidos jugados (GD 0) queda
por delante de equipos con 0 puntos y GD negativa, no al final de la tabla.

SC-003 se midió sobre la liga de 20 equipos y 190 partidos (95 finalizados) que
genera `scripts/seed_calendar_performance.py`, con el frontend en modo desarrollo
(Vite) y PostgreSQL 16 en Docker local, instrumentando la propia página: la
navegación desde la ficha de la liga hasta tener las 20 filas en el DOM tardó
**39 ms** (MutationObserver), y en recarga en frío la respuesta de `/standings`
terminó a los **43 ms** y `loadEventEnd` a los **53 ms** desde el inicio de la
navegación, con las 20 filas presentes. Muy por debajo del límite de 2 segundos;
conviene repetir la medición sobre un build de producción antes de darla por
definitiva.

`alembic check` vuelve a reportar únicamente la diferencia conocida de
normalización `trim` / `TRIM(BOTH FROM ...)` en `ix_leagues_unique_name_season`
e `ix_teams_unique_league_name`, dos índices funcionales preexistentes de las
specs 002 y 003. La HU 008 no añade ningún archivo a `alembic/versions/` ni
define modelos: el módulo `statistics` no tiene `models.py`.

FR-002 no se dio por cumplido "porque no hay código que lo permita": un test de
contrato parametrizado comprueba que `POST`, `PUT`, `PATCH` y `DELETE` sobre
`/leagues/{id}/standings` responden `405` incluso con sesión de organizador, y
la prueba de UI comprueba que la vista no expone botones ni campos de entrada.
