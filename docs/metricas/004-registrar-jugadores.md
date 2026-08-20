# Métricas — HU 004: Registrar jugadores en un equipo

**Spec**: `specs/004-registrar-jugadores/spec.md` · **Responsable**: Quinnie · **Cerrada**: 2026-08-19

## Llenado por el agente (al terminar la HU, antes del PR)

| Métrica | Valor |
|---|---|
| Tareas en `tasks.md` (total) | 15 |
| Tareas completadas | 14 / 15 (T015 pendiente de verificación post-merge) |
| Tests escritos (backend) | 21 (11 integración + 10 contrato) |
| Tests escritos (frontend) | 5 |
| Tests en verde al cerrar | 26 / 26 (21 backend + 5 frontend) |
| Ciclos de corrección | 1 |
| Archivos de código creados/modificados | 18 (backend + frontend + migración + rutas) |

**Ciclos de corrección**: cuántas veces hubo que volver sobre algo ya dado por
terminado. Cuenta honesta, no aspiracional: `0` es sospechoso en una HU no trivial.

**Qué se reprocesó y por qué** (una línea por ciclo):

- **ruff format**: 4 archivos (router, service, tests contract/integration) necesitaron
  `ruff format` mecánico tras la primera pasada — mismo patrón que en 003.

## Llenado por la persona (dos números, al cerrar)

| Métrica | Valor |
|---|---|
| Tiempo real de trabajo — spec + plan + tasks | <ej. 45 min> |
| Tiempo real de trabajo — implement + tests | <ej. 2 h> |
| Costo IA aproximado de la HU | <del panel de uso de tu herramienta> |

## Observaciones

La migración de `players` se escribió a mano (no autogenerate) para evitar el
gotcha de índices funcionales de `teams` documentado en las métricas de 003.
El índice parcial `UNIQUE (team_id, number) WHERE number IS NOT NULL` quedó
correcto a la primera y los dos jugadores sin dorsal coexisten.

T015 (verificación en desplegado Vercel → Railway): **pendiente** hasta el
merge del PR; la migración se aplicará en el arranque de Railway
(`alembic upgrade head`).
