# Métricas — HU 005: Programar un partido

**Spec**: `specs/005-programar-partido/spec.md` · **Responsable**: Quinnie · **Cerrada**: 2026-08-19

## Llenado por el agente (al terminar la HU, antes del PR)

| Métrica | Valor |
|---|---|
| Tareas en `tasks.md` (total) | 15 |
| Tareas completadas | 14 / 15 (T015 pendiente de verificación post-merge) |
| Tests escritos (backend) | 16 (7 integración + 9 contrato) |
| Tests escritos (frontend) | 5 |
| Tests en verde al cerrar | 21 / 21 (16 backend + 5 frontend) |
| Ciclos de corrección | 1 |
| Archivos de código creados/modificados | ~20 (backend + frontend + migración + spec artifacts) |

**Ciclos de corrección**: cuántas veces hubo que volver sobre algo ya dado por
terminado. Cuenta honesta, no aspiracional: `0` es sospechoso en una HU no trivial.

**Qué se reprocesó y por qué** (una línea por ciclo):

- **ruff format**: 3 archivos del módulo matches/tests reformateados tras la
  primera pasada (mismo patrón mecánico que en 003/004).

## Llenado por la persona (dos números, al cerrar)

| Métrica | Valor |
|---|---|
| Tiempo real de trabajo — spec + plan + tasks | <ej. 45 min> |
| Tiempo real de trabajo — implement + tests | <ej. 2 h> |
| Costo IA aproximado de la HU | <del panel de uso de tu herramienta> |

## Observaciones

La migración se escribió a mano (sin autogenerate) para no tocar índices
funcionales de `teams`/`leagues`. Se incluyó un listado mínimo por liga
(`research.md` §2) para que la UI pueda mostrar partidos antes de la HU de
calendario (007).

T015 (verificación en desplegado Vercel → Railway): **pendiente** hasta el
merge del PR.
