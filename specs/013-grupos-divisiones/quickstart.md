# Quickstart: Divisiones (grupos) dentro de una liga

Entidades en `data-model.md`, endpoints en `contracts/groups.openapi.yaml`,
convenciones compartidas en
`../001-fundacion-y-autenticacion/contracts/conventions.md`.

## Prerrequisitos

`specs/001-fundacion-y-autenticacion`, `specs/002-crear-liga` y
`specs/003-registrar-equipos` mezcladas a `main`: hacen falta la sesión de
organizador, una liga existente y equipos registrados en esa liga.

## Ejecutar

```bash
cd backend && alembic upgrade head && uvicorn src.main:app --reload
cd frontend && npm run dev
```

## Escenarios de validación (mapean a los Acceptance Scenarios de `spec.md`)

1. **Crear grupo** (AS1): con sesión de organizador,
   `POST /api/v1/leagues/{ligaId}/groups` con `{"name": "Grupo A"}` → `201`, y
   aparece en `GET /api/v1/leagues/{ligaId}/groups`.
2. **Nombre duplicado en la misma liga** (AS2): repetir la llamada con
   `"GRUPO A"` → `409` con `error.code = "group_name_duplicate"` (unicidad
   insensible a mayúsculas).
3. **Mismo nombre en otra liga** (AS3): en una segunda liga, crear "Grupo A" →
   `201`. Ambos grupos coexisten.
4. **Renombrar** (AS4): `PATCH /api/v1/groups/{groupId}` con `{"name": "Grupo B"}`
   → `200` con el nuevo nombre.
5. **Eliminar grupo** (AS5): `DELETE /api/v1/groups/{groupId}` → `204`; el grupo
   desaparece del listado y sus equipos siguen existiendo (no se eliminan).
6. **Asignar equipo** (AS1-US2): `POST /api/v1/groups/{groupId}/teams` con
   `{"team_id": "..."}` → `201`; el equipo aparece en `GET /api/v1/leagues/{ligaId}/groups`.
7. **Equipo en otro grupo** (AS2-US2): intentar asignar ese mismo equipo a otro
   grupo → `409` con `error.code = "team_already_in_group"`.
8. **Equipo de otra liga** (AS3-US2): intentar asignar un equipo de otra liga →
   `404` con `error.code = "team_not_found_in_league"`.
9. **Equipo inactivo** (FR-011): intentar asignar un equipo `inactive` →
   `409` con `error.code = "team_inactive"`.
10. **Desasignar** (AS4-US2): `DELETE /api/v1/groups/{groupId}/teams?teamId={teamId}`
    → `204`; el equipo deja de aparecer en la composición.
11. **Consulta pública** (US3): sin cookie, `GET /api/v1/leagues/{ligaId}/groups`
    → `200` con cada grupo y su lista de equipos; con una liga sin grupos →
    `200` con lista vacía.
12. **Sin permiso**: crear grupo sin cookie → `401`; con sesión de operador → `403`.

## Pruebas automatizadas

```bash
cd backend && pytest tests/integration/test_groups.py tests/contract/test_groups_contract.py -v
cd frontend && npx vitest run src/features/groups
```
