# Implementation Plan: Registrar equipos en una liga

**Branch**: `003-registrar-equipos` | **Date**: 2026-08-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-registrar-equipos/spec.md`

**Hereda de `specs/001-fundacion-y-autenticacion`** (`AGENTS.md` §5): stack,
modelo de dominio y convenciones de API. Este plan **no re-decide** ninguno de
esos aspectos.

## Summary

Alta y consulta de equipos dentro de una liga: el organizador registra equipos
con nombre único dentro de esa liga (el mismo nombre es válido en ligas
distintas), opcionalmente con escudo y colores; cualquiera los consulta sin
autenticarse. Los equipos con historial no se eliminan: se marcan inactivos.
Decisiones propias en `research.md`, delta de modelo en `data-model.md`,
endpoints en `contracts/teams.openapi.yaml`.

## Technical Context

Todo heredado de
[`specs/001-fundacion-y-autenticacion/plan.md`](../001-fundacion-y-autenticacion/plan.md).

**Deltas propios de esta spec**:

- **Storage**: añade la tabla `teams`, con FK `ON DELETE RESTRICT` a `leagues`.
- **Constraints**: `crest_url` debe ser una URL `https` absoluta; el servidor
  nunca la descarga (evita SSRF y latencia — `research.md` §1).
- **Performance Goals**: registrar 8 equipos en menos de 10 minutos (SC-001 de
  `spec.md`).
- **Scale/Scope**: hasta 20 equipos por liga (volumen de referencia de `001`).

Sin `NEEDS CLARIFICATION`: la spec pasó su checklist 16/16 y las tres
decisiones abiertas se resolvieron en `research.md`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio / regla | Estado | Cómo se cumple |
|---|---|---|
| I. La Especificación Manda | PASS | Cada endpoint traza a un FR; lo no especificado (formato de colores, alcance del borrado lógico) se resolvió en `research.md`, no en el código |
| II. Toda Regla de Negocio se Prueba | PASS | Unicidad por liga, independencia entre ligas, validación de `crest_url` y borrado lógico tienen test propio en `tasks.md` |
| III. Contratos de API Explícitos | PASS | `contracts/teams.openapi.yaml`, reutilizando envelope y paginación de `001` |
| IV. No Romper lo que ya Funciona | PASS | Solo añade tabla y endpoints; `leagues` se toca únicamente con una FK nueva |
| V. Migraciones Versionadas | PASS | La tabla `teams` entra como migración Alembic en esta HU |
| VI. Cero Secretos en el Repositorio | PASS | No introduce configuración nueva |
| VII. Código de IA con la Misma Vara | PASS | Regla de proceso de PR |
| VIII. Entregabilidad Independiente por Dominio | PASS | Código en `backend/src/teams/` y `frontend/src/features/teams/`; accede a `leagues` solo por su servicio, no por su modelo interno |
| Arquitectura: monolito modular | PASS | Un módulo más en el backend existente |
| Regla de Derivación de Estadísticas | PASS (indirecto) | El borrado lógico de FR-005 existe precisamente para que la clasificación histórica siga cuadrando; `research.md` §3 fija que un equipo inactivo permanece visible en el historial |
| Estándares de Seguridad Obligatorios | PASS | Validación Pydantic, ORM, escritura por rol, y el rechazo explícito de descargar `crest_url` evita SSRF |

Sin violaciones. **Complexity Tracking no aplica.**

*Re-check post Phase 1*: el diseño no introdujo elementos fuera de lo aprobado.
La decisión de no descargar el escudo refuerza los Estándares de Seguridad en
vez de tensionarlos. **PASS confirmado.**

## Project Structure

### Documentation (this feature)

```text
specs/003-registrar-equipos/
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── teams.openapi.yaml
├── quickstart.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/
├── src/teams/
│   ├── models.py         # Team (SQLAlchemy)
│   ├── schemas.py        # CreateTeamRequest, Team, PaginatedTeams
│   ├── service.py        # unicidad por liga, normalización, borrado lógico
│   └── router.py         # POST/GET /leagues/{id}/teams, GET /teams/{id}
├── alembic/versions/     # migración de la tabla teams
└── tests/
    ├── contract/test_teams_contract.py
    └── integration/test_teams.py

frontend/
└── src/features/teams/
    ├── TeamsPage.tsx         # listado por liga
    ├── CreateTeamForm.tsx    # solo organizador
    ├── api.ts
    └── __tests__/
```

**Structure Decision**: misma estructura de
[`001`](../001-fundacion-y-autenticacion/plan.md). Esta HU puebla los
directorios `teams/` ya reservados allí; no crea carpetas de primer nivel.

## Complexity Tracking

*Sin violaciones que justificar — tabla vacía a propósito.*
