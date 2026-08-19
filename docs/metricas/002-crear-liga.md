# Métricas — HU 002: Crear una liga

**Spec**: `specs/002-crear-liga/spec.md` · **Responsable**: Alejo · **Cerrada**: 2026-08-19

## Llenado por el agente (al terminar la HU, antes del PR)

| Métrica | Valor |
|---|---|
| Tareas en `tasks.md` (total) | 16 |
| Tareas completadas | 15 / 16 (T016 es verificación post-merge) |
| Tests escritos (backend) | 20 (11 integración + 9 contrato) |
| Tests escritos (frontend) | 4 |
| Tests en verde al cerrar | 24 / 24 (20 backend + 4 frontend) |
| Ciclos de corrección | 3 |
| Archivos de código creados/modificados | 16 (9 backend + 7 frontend) |

**Ciclos de corrección**: cuántas veces hubo que volver sobre algo ya dado por
terminado (test que falló tras implementar, requisito mal interpretado,
refactor por un choque con otra HU). Cuenta honesta, no aspiracional: `0` es
sospechoso en una HU no trivial.

**Qué se reprocesó y por qué** (una línea por ciclo; es el dato más valioso
para la comparativa SDD vs. prompts sueltos del caso de negocio):

- `ruff check` sobre `tests/integration/test_leagues.py`: importaba `select`/`SessionLocal`/`League` sin usarlos (quedaron de un test de BD que se descartó), variable ambigua `l` en una comprensión y una línea de 101 chars. Todo detectado por el linter, no en ejecución.
- `ruff format --check`: dos archivos de test tenían líneas que cabían en una sola (`test_leagues_contract.py`, `test_leagues.py`). Corregido con `ruff format`.
- `eslint` + `tsc` sobre el helper de mock de Vitest: el parámetro `init` quedó sin usar al simplificar la respuesta; marcado por `@typescript-eslint/no-unused-vars` y `TS6133`. Resuelto con `void init`.

## Llenado por la persona (dos números, al cerrar)

| Métrica | Valor |
|---|---|
| Tiempo real de trabajo — spec + plan + tasks | <ej. 45 min> |
| Tiempo real de trabajo — implement + tests | <ej. 2 h> |
| Costo IA aproximado de la HU | <del panel de uso de tu herramienta> |

## Observaciones

No hubo defectos de lógica: los tres ciclos de corrección fueron mecánicos de
lint/formato, no de comportamiento. Escribir los tests primero (T003/T004, que
fallaron en rojo por rutas no registradas) y tener la spec con su checklist
16/16 más `research.md` cerrado dejó poco margen de ambigüedad: la única regla
de negocio real (unicidad `(name, season)` insensible a mayúsculas y espacios)
ya estaba decidida por escrito y se implementó en una sola pasada.

El punto que merece atención para el caso de negocio es la **duplicación
deliberada de la regla de unicidad** (servicio + índice único funcional): sin
ella, o se deja una ventana de carrera entre dos organizadores, o el error de
colisión llega como un 500 genérico en vez del 409 legible del envelope. El
índice `lower(trim(name)), lower(trim(season))` se autogeneró correctamente
con Alembic (aunque los índices funcionales no siempre se detectan; aquí sí,
por estar declarados en el modelo con `Index(...)`).

T016 (verificación en el entorno desplegado Vercel → Railway) queda **pendiente
de hacer tras el merge**, igual que en la 001: el endpoint `/api/v1/leagues` en
el entorno de producción hoy devuelve 404 porque el código de esta HU aún no
está desplegado. Es una tarea post-merge, no parte del implement.
