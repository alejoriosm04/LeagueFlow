# Métricas — HU 013: Divisiones (grupos) dentro de una liga

**Spec**: `specs/013-grupos-divisiones/spec.md` · **Responsable**: <nombre> · **Cerrada**: 2026-08-22

## Llenado por el agente (al terminar la HU, antes del PR)

| Métrica | Valor |
|---|---|
| Tareas en `tasks.md` (total) | 23 |
| Tareas completadas | 23 |
| Tests escritos (backend) | 20 funciones de prueba (9 de contrato + 11 de integración) |
| Tests escritos (frontend) | 3 (GroupsPage: vacío, acción solo organizador, composición) |
| Tests en verde al cerrar | Backend: 282 en verde (suite completa; 20 nuevos incluidos). Frontend: 226 en verde (suite completa; 3 nuevos incluidos) |
| Ciclos de corrección | 1 |
| Archivos de código creados/modificados | 17 (11 creados, 6 modificados; no cuenta `specs/013-*` ni este archivo) |

**Ciclos de corrección**: cuántas veces hubo que volver sobre algo ya dado por
terminado. Cuenta honesta, no aspiracional: `0` es sospechoso en una HU no trivial.

**Qué se reprocesó y por qué** (una línea por ciclo; es el dato más valioso
para la comparativa SDD vs. prompts sueltos del caso de negocio):

- Corrección de lint/tipos al validar antes de dar por terminada: `ruff format`
  (líneas >100 en `service.py`/`router.py`/tests) y un parámetro sin usar en el
  test de frontend (`tsc -b`). Sin re-diseño: la especificación y el plan no
  cambiaron.

## Llenado por la persona (dos números, al cerrar)

| Métrica | Valor |
|---|---|
| Tiempo real de trabajo — spec + plan + tasks | <ej. 45 min> |
| Tiempo real de trabajo — implement + tests | <ej. 2 h> |
| Costo IA aproximado de la HU | <del panel de uso de tu herramienta> |

## Observaciones

- La decisión de modelar la pertenencia como **tabla puente** (`group_memberships`)
  en vez de un `group_id` en `teams` evitó tocar el dominio de equipos (Principio
  VIII): la implementación no modificó ningún archivo de `teams`/`leagues`, solo
  los leyó por servicio.
- La regla "a lo sumo un grupo por liga" quedó garantizada por `UNIQUE (team_id)`
  en la base y por un chequeo en el servicio; la migración se revisó para no
  recrear los índices funcionales de `leagues`/`teams` (AGENTS.md).
- El backend y el frontend se implementaron en una sola pasada; la única
  corrección fue de estilo/tipos, no de lógica.
