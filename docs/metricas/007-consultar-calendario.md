# Métricas — HU 007: Consultar el calendario y los resultados

**Spec**: `specs/007-consultar-calendario/spec.md` · **Responsable**: <nombre> · **Cerrada**: 2026-08-20

## Llenado por el agente (al terminar la HU, antes del PR)

| Métrica | Valor |
|---|---|
| Tareas en `tasks.md` (total) | 18 |
| Tareas completadas | 18 |
| Tests escritos (backend) | 8 funciones de prueba; 11 casos recolectados |
| Tests escritos (frontend) | 5 |
| Tests en verde al cerrar | 127 backend + 32 frontend |
| Ciclos de corrección | 3 |
| Archivos de código creados/modificados | 11 |

**Ciclos de corrección**: cuántas veces hubo que volver sobre algo ya dado por
terminado (test que falló tras implementar, requisito mal interpretado,
refactor por un choque con otra HU). Cuenta honesta, no aspiracional: `0` es
sospechoso en una HU no trivial.

**Qué se reprocesó y por qué** (una línea por ciclo; es el dato más valioso
para la comparativa SDD vs. prompts sueltos del caso de negocio):

- Se actualizaron tres pruebas de regresión de partidos cuyos mocks conservaban la paginación y el mensaje vacío anteriores al nuevo calendario.
- Se corrigió el orden de imports de dos archivos nuevos después de ejecutar las compuertas Ruff completas.
- Se reutilizó una única instancia de `Intl.DateTimeFormat` porque la primera medición manual superó los 2 segundos al formatear 190 fechas durante el render.

## Llenado por la persona (dos números, al cerrar)

| Métrica | Valor |
|---|---|
| Tiempo real de trabajo — spec + plan + tasks | <ej. 45 min> |
| Tiempo real de trabajo — implement + tests | <ej. 2 h> |
| Costo IA aproximado de la HU | <del panel de uso de tu herramienta> |

## Observaciones

La implementación, el acceso público, los filtros, la paginación de 190 partidos y las suites completas están verificados. El seed persistente produjo 190 partidos en dos ejecuciones consecutivas sin duplicarlos. La primera medición manual de SC-001 superó los 2 segundos; tras optimizar el formateo de fechas, la persona repitió la prueba con 20 equipos/190 partidos y observó aproximadamente 1.4 segundos, por debajo del límite de 2 segundos. SC-002 se verificó en una interacción desde la ficha de la liga mediante la prueba de UI. `alembic check` solo reportó la diferencia conocida de normalización `trim`/`TRIM(BOTH FROM ...)` en dos índices funcionales preexistentes; la HU no añade migraciones ni cambios reales de esquema.
