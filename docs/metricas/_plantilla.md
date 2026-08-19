# Métricas — HU NNN: <título de la HU>

**Spec**: `specs/NNN-slug/spec.md` · **Responsable**: <nombre> · **Cerrada**: AAAA-MM-DD

## Llenado por el agente (al terminar la HU, antes del PR)

| Métrica | Valor |
|---|---|
| Tareas en `tasks.md` (total) | |
| Tareas completadas | |
| Tests escritos (backend) | |
| Tests escritos (frontend) | |
| Tests en verde al cerrar | |
| Ciclos de corrección | |
| Archivos de código creados/modificados | |

**Ciclos de corrección**: cuántas veces hubo que volver sobre algo ya dado por
terminado (test que falló tras implementar, requisito mal interpretado,
refactor por un choque con otra HU). Cuenta honesta, no aspiracional: `0` es
sospechoso en una HU no trivial.

**Qué se reprocesó y por qué** (una línea por ciclo; es el dato más valioso
para la comparativa SDD vs. prompts sueltos del caso de negocio):

-

## Llenado por la persona (dos números, al cerrar)

| Métrica | Valor |
|---|---|
| Tiempo real de trabajo — spec + plan + tasks | <ej. 45 min> |
| Tiempo real de trabajo — implement + tests | <ej. 2 h> |
| Costo IA aproximado de la HU | <del panel de uso de tu herramienta> |

## Observaciones

<Qué salió mejor o peor de lo esperado. Si algo del spec estaba mal y se
descubrió implementando, anótalo aquí: es evidencia directa del valor —o del
costo— de SDD.>
