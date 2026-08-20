# Quickstart: Programar un partido

Entidad en `data-model.md`, endpoints en `contracts/matches.openapi.yaml`,
convenciones compartidas en
`../001-fundacion-y-autenticacion/contracts/conventions.md`.

## Prerrequisitos

`specs/001-*`, `specs/002-*` y `specs/003-registrar-equipos` en `main`:
sesión de organizador y al menos dos equipos activos en la misma liga.
No requiere `specs/004-registrar-jugadores`.

## Ejecutar

```bash
cd backend && alembic upgrade head && uvicorn src.main:app --reload
cd frontend && npm run dev
```

## Escenarios de validación (mapean a los Acceptance Scenarios de `spec.md`)

1. **Programar partido** (AS1): con sesión de organizador,
   `POST /api/v1/leagues/{ligaId}/matches` con
   `{"home_team_id": "...", "away_team_id": "...", "scheduled_at": "2026-09-01T18:00:00Z"}`
   → `201`, `status = "scheduled"`, `home_score`/`away_score` = `null`, y
   aparece en `GET /api/v1/leagues/{ligaId}/matches`.
2. **Mismo equipo** (AS2): `home_team_id == away_team_id` → `409`
   `match_same_team`.
3. **Equipos de ligas distintas** (AS3): local de liga 1 y visitante de liga 2
   → `404` `team_not_found` (`research.md` §3).
4. **Sin permiso** (AS4): sin cookie → `401`; con sesión de operador → `403`.
5. **Detalle público** (FR-005): `GET /api/v1/matches/{id}` sin sesión → `200`.
6. **Equipo inactivo**: programar con un equipo `inactive` → `404`
   `team_not_found` (`research.md` §3).

## Pruebas automatizadas

```bash
cd backend && pytest tests/integration/test_matches.py tests/contract/test_matches_contract.py -v
cd frontend && npx vitest run src/features/matches
```
