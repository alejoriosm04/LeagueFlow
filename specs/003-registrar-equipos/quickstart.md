# Quickstart: Registrar equipos en una liga

Entidad en `data-model.md`, endpoints en `contracts/teams.openapi.yaml`,
convenciones compartidas en
`../001-fundacion-y-autenticacion/contracts/conventions.md`.

## Prerrequisitos

`specs/001-fundacion-y-autenticacion` y `specs/002-crear-liga` mezcladas a
`main`: hacen falta la sesión de organizador y al menos una liga existente.

## Ejecutar

```bash
cd backend && alembic upgrade head && uvicorn src.main:app --reload
cd frontend && npm run dev
```

## Escenarios de validación (mapean a los Acceptance Scenarios de `spec.md`)

1. **Registrar equipo** (AS1): con sesión de organizador,
   `POST /api/v1/leagues/{ligaId}/teams` con `{"name": "Ingeniería FC"}` →
   `201`, y aparece en `GET /api/v1/leagues/{ligaId}/teams`.
2. **Nombre duplicado en la misma liga** (AS2): repetir la llamada → `409` con
   `error.code = "team_name_duplicate"`. Repetir con `"INGENIERÍA FC"` →
   también `409` (unicidad insensible a mayúsculas).
3. **Mismo nombre en otra liga** (AS3): crear una segunda liga y registrar allí
   "Ingeniería FC" → `201`. Ambos equipos coexisten y son independientes.
4. **Sin permiso** (AS4): sin cookie → `401`; con sesión de operador → `403`.
5. **Escudo inválido**: `crest_url` con `http://` o una cadena que no es URL →
   `400` con `error.field = "crest_url"` (`research.md` §1).
6. **Borrado lógico**: marcar un equipo como `inactive` y verificar que
   desaparece del listado por defecto pero sigue accesible en
   `GET /api/v1/teams/{id}` y con `?include_inactive=true` (`research.md` §3).

## Pruebas automatizadas

```bash
cd backend && pytest tests/integration/test_teams.py tests/contract/test_teams_contract.py -v
cd frontend && npx vitest run src/features/teams
```
