# Métricas — HU 006: Registrar y corregir el resultado de un partido

**Spec**: `specs/006-registrar-resultado/spec.md` · **Responsable**: <nombre> · **Cerrada**: 2026-08-20

## Llenado por el agente (al terminar la HU, antes del PR)

| Métrica | Valor |
|---|---|
| Tareas en `tasks.md` (total) | 24 |
| Tareas completadas | 24 |
| Tests escritos (backend) | 18 funciones de prueba; 21 casos recolectados |
| Tests escritos (frontend) | 3 |
| Tests en verde al cerrar | 116 backend + 27 frontend |
| Ciclos de corrección | 3 |
| Archivos de código creados/modificados | 18 |

**Ciclos de corrección**: cuántas veces hubo que volver sobre algo ya dado por
terminado (test que falló tras implementar, requisito mal interpretado,
refactor por un choque con otra HU). Cuenta honesta, no aspiracional: `0` es
sospechoso en una HU no trivial.

**Qué se reprocesó y por qué** (una línea por ciclo; es el dato más valioso
para la comparativa SDD vs. prompts sueltos del caso de negocio):

- Se ajustó la validación del formulario de corrección porque la validación nativa del navegador impedía mostrar el mensaje español exigido por la prueba.
- Se restauró y comprobó el estado de Alembic porque la limpieza de tablas de pytest dejó obsoleta la tabla de versión antes del ciclo downgrade/upgrade.
- Se reformatearon modelos, servicio y pruebas nuevas para satisfacer exactamente las compuertas Ruff de CI.

## Llenado por la persona (dos números, al cerrar)

| Métrica | Valor |
|---|---|
| Tiempo real de trabajo — spec + plan + tasks | <ej. 45 min> |
| Tiempo real de trabajo — implement + tests | <ej. 2 h> |
| Costo IA aproximado de la HU | <del panel de uso de tu herramienta> |

## Observaciones

La implementación, migraciones, concurrencia, autorización, auditoría y suites completas están verificadas. La persona ejecutó SC-001 manualmente desde la ficha cargada hasta la confirmación visible y reportó un tiempo menor de 1 segundo, por debajo del límite de 30 segundos.
