# Implementation Plan: Divisiones (grupos) dentro de una liga

**Branch**: `013-grupos-divisiones` | **Date**: 2026-08-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/013-grupos-divisiones/spec.md`

**Hereda de `specs/001-fundacion-y-autenticacion`** (`AGENTS.md` §5): stack,
modelo de dominio y convenciones de API. Este plan **no re-decide** ninguno de
esos aspectos.

## Summary

Alta, gestión y consulta de grupos (divisiones) dentro de una liga: el
organizador crea, renombra y elimina grupos, y asigna/desasigna equipos (a lo
sumo un grupo por liga); cualquiera consulta la composición sin autenticarse.
Nuevo módulo `backend/src/groups/` con sus propias tablas (`groups`,
`group_memberships`), sin tocar `teams` ni `leagues` — los lee por su interfaz
pública de servicio (Principio VIII). Decisiones propias en `research.md`,
delta de modelo en `data-model.md`, endpoints en `contracts/groups.openapi.yaml`.

## Technical Context

Todo heredado de
[`specs/001-fundacion-y-autenticacion/plan.md`](../001-fundacion-y-autenticacion/plan.md).

**Deltas propios de esta spec**:

- **Storage**: añade dos tablas: `groups` (FK `ON DELETE RESTRICT` a `leagues`)
  y `group_memberships` (FK `ON DELETE CASCADE` a `groups`, `ON DELETE RESTRICT`
  a `teams`).
- **Constraints**: nombre de grupo único por liga (`lower(trim(name))`); un
  equipo en a lo sumo un grupo (`UNIQUE (team_id)` en membresías).
- **Performance Goals**: crear un grupo y asignarle un equipo en 3
  interacciones (SC-001 de `spec.md`).
- **Scale/Scope**: hasta 20 equipos por liga (volumen de referencia de `001`);
  sin límite duro de grupos por liga.

Sin `NEEDS CLARIFICATION`: la spec pasó su checklist 16/16 y la clarificación
de equipos inactivos quedó resuelta en `spec.md` (§Clarifications).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio / regla | Estado | Cómo se cumple |
|---|---|---|
| I. La Especificación Manda | PASS | Cada endpoint traza a un FR; la decisión de equipos inactivos está en `spec.md` §Clarifications, no inventada en código |
| II. Toda Regla de Negocio se Prueba | PASS | Unicidad por liga, "a lo sumo un grupo", rechazo de equipo ajeno/inactivo y el borrado de grupo tienen test propio en `tasks.md` |
| III. Contratos de API Explícitos | PASS | `contracts/groups.openapi.yaml`, reutilizando envelope y cookie de sesión de `001` |
| IV. No Romper lo que ya Funciona | PASS | Solo añade tablas y endpoints; `teams`/`leagues` no se modifican (solo se leen por servicio) |
| V. Migraciones Versionadas | PASS | `groups` y `group_memberships` entran como migración Alembic en esta HU |
| VI. Cero Secretos en el Repositorio | PASS | No introduce configuración nueva |
| VII. Código de IA con la Misma Vara | PASS | Regla de proceso de PR |
| VIII. Entregabilidad Independiente por Dominio | PASS | Código en `backend/src/groups/`; accede a `teams`/`leagues` solo por servicio, no por modelo interno |
| Arquitectura: monolito modular | PASS | Un módulo más en el backend existente |
| Regla de Derivación de Estadísticas | PASS (indirecto) | Los grupos no alimentan la clasificación; `spec.md` FR-010 lo fija explícitamente |
| Estándares de Seguridad Obligatorios | PASS | Validación Pydantic, ORM, escritura por rol (`organizador`), consulta pública sin secretos |

Sin violaciones. **Complexity Tracking no aplica.**

*Re-check post Phase 1*: el diseño (tabla puente + servicio de lectura) refuerza
el Principio VIII en vez de tensionarlo. **PASS confirmado.**

## Project Structure

### Documentation (this feature)

```text
specs/013-grupos-divisiones/
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── groups.openapi.yaml
├── quickstart.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/
├── src/groups/
│   ├── models.py         # LeagueGroup, GroupTeamMembership (SQLAlchemy)
│   ├── schemas.py        # CreateGroupRequest, Group, GroupWithTeams, AssignTeamRequest
│   ├── service.py        # unicidad por liga, "a lo sumo un grupo", inactivos
│   └── router.py         # POST/GET /leagues/{id}/groups, PATCH/DELETE /groups/{id}, asignar/desasignar
├── alembic/versions/     # migración de las tablas groups + group_memberships
└── tests/
    ├── contract/test_groups_contract.py
    └── integration/test_groups.py

frontend/
└── src/features/groups/
    ├── GroupsPage.tsx         # composición por liga (pública)
    ├── GroupForm.tsx          # crear/renombrar (solo organizador)
    ├── api.ts
    └── __tests__/
```

**Structure Decision**: misma estructura de
[`001`](../001-fundacion-y-autenticacion/plan.md). Esta HU crea el módulo nuevo
`backend/src/groups/` y `frontend/src/features/groups/`; no toca carpetas de
otros dominios.

## Complexity Tracking

*Sin violaciones que justificar — tabla vacía a propósito.*
