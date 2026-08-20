# Quickstart: Registrar jugadores en un equipo

Entidad en `data-model.md`, endpoints en `contracts/players.openapi.yaml`,
convenciones compartidas en
`../001-fundacion-y-autenticacion/contracts/conventions.md`.

## Prerrequisitos

`specs/001-fundacion-y-autenticacion`, `specs/002-crear-liga` y
`specs/003-registrar-equipos` mezcladas a `main`: hacen falta la sesión de
organizador y al menos un equipo activo.

## Ejecutar

```bash
cd backend && alembic upgrade head && uvicorn src.main:app --reload
cd frontend && npm run dev
```

## Escenarios de validación (mapean a los Acceptance Scenarios de `spec.md`)

1. **Registrar jugador** (AS1): con sesión de organizador,
   `POST /api/v1/teams/{teamId}/players` con
   `{"name": "Andrés Gómez", "number": 10, "position": "delantero"}` → `201`,
   y aparece en `GET /api/v1/teams/{teamId}/players`.
2. **Dorsal duplicado** (AS2): repetir con el mismo `number` en el mismo
   equipo → `409` con `error.code = "player_number_duplicate"`.
3. **Plantilla aislada por equipo** (AS3): registrar el jugador en el equipo A
   y consultar la plantilla del equipo B de la misma liga → no aparece.
4. **Sin permiso** (AS4): sin cookie → `401`; con sesión de operador → `403`.
5. **Dorsal inválido**: `number: 0` o `number: 100` → `400` con
   `error.field = "number"` (`research.md` §1).
6. **Sin dorsal**: dos jugadores del mismo equipo con `number: null` → ambos
   `201` (la unicidad no aplica a nulos).
7. **Equipo inactivo**: `POST` sobre un equipo `inactive` → `404`
   `team_not_found` (`research.md` §4).
8. **Borrado lógico**: marcar un jugador como `inactive` y verificar que
   desaparece del listado por defecto pero sigue accesible en
   `GET /api/v1/players/{id}` y con `?include_inactive=true`
   (`research.md` §3).

## Pruebas automatizadas

```bash
cd backend && pytest tests/integration/test_players.py tests/contract/test_players_contract.py -v
cd frontend && npx vitest run src/features/players
```
