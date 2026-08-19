# Quickstart: Crear una liga

Valida esta spec end-to-end. Entidad en `data-model.md`, endpoints en
`contracts/leagues.openapi.yaml`, convenciones compartidas en
`../001-fundacion-y-autenticacion/contracts/conventions.md`.

## Prerrequisitos

`specs/001-fundacion-y-autenticacion` implementada y mezclada a `main`: hacen
falta el backend en marcha, la base de datos migrada y el usuario organizador
semilla. Ver `../001-fundacion-y-autenticacion/quickstart.md` §Setup.

## Ejecutar

```bash
cd backend && alembic upgrade head && uvicorn src.main:app --reload
cd frontend && npm run dev
```

## Escenarios de validación (mapean a los Acceptance Scenarios de `spec.md`)

1. **Crear liga** (AS1): con sesión de organizador, `POST /api/v1/leagues` con
   `{"name": "Interfacultades", "season": "2026-1"}` → `201`, y la liga aparece
   en `GET /api/v1/leagues`.
2. **Nombre duplicado** (AS2): repetir la misma llamada → `409` con
   `error.code = "league_already_exists"`. Repetirla con
   `{"name": "INTERFACULTADES", "season": "2026-1"}` → también `409`, porque la
   unicidad es insensible a mayúsculas (`research.md` §2).
3. **Nombre vacío** (AS3): `POST` con `{"name": "", "season": "2026-1"}` →
   `400`, y `error.field = "name"`.
4. **Sin permiso** (AS4): sin cookie de sesión → `401`. Con sesión de operador
   → `403`.
5. **Consulta pública**: `GET /api/v1/leagues` y `GET /api/v1/leagues/{id}` sin
   cookie → `200` en ambos.
6. **Autoría**: la liga creada en el paso 1 tiene `created_by` igual al `id`
   del organizador de la sesión, sin haberlo enviado en el payload.

## Pruebas automatizadas

```bash
cd backend && pytest tests/integration/test_leagues.py tests/contract/test_leagues_contract.py -v
cd frontend && npx vitest run src/features/leagues
```
