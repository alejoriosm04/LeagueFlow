# Métricas — HU 002: Crear una liga

**Spec**: `specs/002-crear-liga/spec.md` · **Responsable**: Alejo · **Cerrada**: 2026-08-19

## Llenado por el agente (al terminar la HU, antes del PR)

| Métrica | Valor |
|---|---|
| Tareas en `tasks.md` (total) | 16 |
| Tareas completadas | 16 / 16 |
| Tests escritos (backend) | 20 (11 integración + 9 contrato) |
| Tests escritos (frontend) | 5 |
| Tests en verde al cerrar | 25 / 25 |
| Ciclos de corrección | 4 |
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
- **Sin punto de entrada en la UI** (detectado tras el despliegue, no por los tests): el formulario `/leagues/new` existía pero la página de listado no enlazaba a él, así que un organizador no podía crear ligas desde la interfaz (SC-001 "sin ayuda externa" roto). Los tests no lo cubrían porque verificaban el formulario aislado, no la navegación desde el listado. Corregido en PR #13 con el enlace "Crear liga" visible solo al organizador + test de visibilidad.

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

T016 (verificación en el entorno desplegado Vercel → Railway) **verificada**:
el endpoint `/api/v1/leagues` en producción responde 200 (listado), 401 sin
sesión y 404 con `league_not_found`; la migración se aplica en cada arranque (el
Dockerfile corre `alembic upgrade head`) y el CORS cross-domain responde
`access-control-allow-origin: https://leagueflow-pdms2.vercel.app` con
`allow-credentials: true`. El flujo completo de crear una liga con la sesión del
organizador desde Vercel quedó confirmado en producción.

**Nota para el caso de negocio**: el PR #8 se mezcló con el título antiguo
"feat(002): plan y tasks de crear liga" (se puso cuando la rama solo tenía
plan/tasks, y la implementación se acumuló en el mismo PR). Por squash merge,
ese título quedó como commit en `main`, así que el commit dice "plan y tasks"
pero contiene toda la implementación. No se corrige sin reescribir historia;
queda como evidencia de que el título del PR debe actualizarse al pasar de
planificar a implementar.
