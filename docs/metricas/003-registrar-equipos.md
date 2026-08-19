# Métricas — HU 003: Registrar equipos en una liga

**Spec**: `specs/003-registrar-equipos/spec.md` · **Responsable**: Alejo · **Cerrada**: 2026-08-19

## Llenado por el agente (al terminar la HU, antes del PR)

| Métrica | Valor |
|---|---|
| Tareas en `tasks.md` (total) | 15 |
| Tareas completadas | 14 / 15 (T015 es verificación post-merge) |
| Tests escritos (backend) | 21 (11 integración + 10 contrato) |
| Tests escritos (frontend) | 5 |
| Tests en verde al cerrar | 26 / 26 (21 backend + 5 frontend) |
| Ciclos de corrección | 3 |
| Archivos de código creados/modificados | 15 (9 backend + 6 frontend) |

**Ciclos de corrección**: cuántas veces hubo que volver sobre algo ya dado por
terminado. Cuenta honesta, no aspiracional: `0` es sospechoso en una HU no trivial.

**Qué se reprocesó y por qué** (una línea por ciclo):

- **Test de "sin sesión" en falso verde/rojo**: los tests `test_*_sin_sesion_recibe_401` usaban el fixture `cliente_organizador` para crear la liga previa; como ese fixture y `cliente` son el MISMO `AsyncClient`, la cookie de organizador quedaba puesta y el POST devolvía 201 en vez de 401. Corregido probando la ausencia de sesión con un UUID aleatorio y sin crear liga (el control de rol se evalúa antes que la existencia de la liga).
- **Falso positivo de Alembic con índices funcionales**: el autogenerate de la migración de `teams` detectó un "cambio" inexistente en el índice de `leagues` (`lower(trim(name))` vs. `lower(TRIM(BOTH FROM name))`, que es como PostgreSQL normaliza la expresión en el catálogo) e intentó `DROP`/`CREATE` del índice de ligas. Se eliminó ese diff espurio a mano; quedó como gotcha para las specs 004+ (cada autogenerate lo repetirá).
- **ruff**: `E501` en un test (`crest_url` con línea de 102) y 3 archivos por `ruff format`. Mecánico.

## Llenado por la persona (dos números, al cerrar)

| Métrica | Valor |
|---|---|
| Tiempo real de trabajo — spec + plan + tasks | <ej. 45 min> |
| Tiempo real de trabajo — implement + tests | <ej. 2 h> |
| Costo IA aproximado de la HU | <del panel de uso de tu herramienta> |

## Observaciones

Sin defectos de lógica de negocio: los tres ciclos fueron uno de test
(fixture compartido), uno de tooling (autogenerate de índices funcionales) y
uno de formato. La regla de negocio central —unicidad de nombre **por liga**,
insensible a mayúsculas y espacios, permitiendo el mismo nombre en ligas
distintas— quedó fijada por escrito en `research.md` y se implementó en una
sola pasada.

Dos puntos valiosos para el caso de negocio:

1. **El borrado lógico (FR-005) llega antes que su endpoint.** La spec define
   `status=inactive` y su efecto en las consultas (`include_inactive`, detalle
   siempre visible), pero **no** incluye un endpoint para dar de baja un equipo:
   eso llega cuando existan partidos/alineaciones/eventos (specs 005+). Por
   eso el escenario 6 del quickstart y su test de integración "marcan inactive"
   directo en la BD con el ORM. Es un buen ejemplo de diseñar el modelo para el
   futuro sin inventar operaciones que la spec no pide (Principio I).

2. **El gotcha de Alembic con índices funcionales se repetirá en 004+.** El
   autogenerate ve `trim(name)` (lo que declara el modelo) como distinto de
   `TRIM(BOTH FROM name)` (lo que PostgreSQL almacena) y genera un
   `DROP INDEX`/`CREATE INDEX` espurio en cada migración futura que se genere
   con autogenerate. Hay que revisar el diff y borrar esas líneas, como se hizo
   aquí. Vale anotarlo en `AGENTS.md` para que no le cueste a otro integrante.

T015 (verificación en desplegado Vercel → Railway) queda **post-merge**, como
en las HUs anteriores: los endpoints de equipos no existen en producción hasta
que esta rama se mezcle y Railway aplique la migración en el arranque.
