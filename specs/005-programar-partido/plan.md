# Implementation Plan: Programar un partido

**Branch**: `005-programar-partido` | **Date**: 2026-08-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-programar-partido/spec.md`

**Hereda de `specs/001-fundacion-y-autenticacion`** (`AGENTS.md` §5): stack,
modelo de dominio y convenciones de API. Este plan **no re-decide** ninguno de
esos aspectos.

## Summary

Alta y consulta de partidos: el organizador programa un enfrentamiento entre
dos equipos distintos de la misma liga con fecha/hora; el partido nace en
estado `scheduled` y sin marcador. Cualquiera consulta el detalle (y el
listado por liga) sin autenticarse. Decisiones propias en `research.md`,
delta de modelo en `data-model.md`, endpoints en `contracts/matches.openapi.yaml`.

## Technical Context

Todo heredado de
[`specs/001-fundacion-y-autenticacion/plan.md`](../001-fundacion-y-autenticacion/plan.md).

**Deltas propios de esta spec**:

- **Storage**: añade la tabla `matches`, con FKs `ON DELETE RESTRICT` a
  `leagues` y `teams`.
- **Constraints**: `home_team_id != away_team_id`; ambos equipos deben
  pertenecer a `league_id` y estar activos (`research.md`).
- **Performance Goals**: programar un partido en menos de 1 minuto (SC-001).
- **Scale/Scope**: ligas de hasta 20 equipos / ~190 partidos (volumen de `001`).

Sin `NEEDS CLARIFICATION`: la spec pasó su checklist 16/16 y las decisiones
abiertas se resolvieron en `research.md`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio / regla | Estado | Cómo se cumple |
|---|---|---|
| I. La Especificación Manda | PASS | Cada endpoint traza a un FR; fechas pasadas, listado por liga y equipos inactivos se resolvieron en `research.md` |
| II. Toda Regla de Negocio se Prueba | PASS | Mismo equipo, equipos de otra liga, rol organizador y equipos inactivos tienen test propio |
| III. Contratos de API Explícitos | PASS | `contracts/matches.openapi.yaml`, reutilizando envelope y paginación de `001` |
| IV. No Romper lo que ya Funciona | PASS | Solo añade tabla y endpoints; no altera ligas/equipos/jugadores existentes |
| V. Migraciones Versionadas | PASS | La tabla `matches` entra como migración Alembic en esta HU |
| VI. Cero Secretos en el Repositorio | PASS | No introduce configuración nueva |
| VII. Código de IA con la Misma Vara | PASS | Regla de revisión de PR |
| VIII. Entregabilidad Independiente por Dominio | PASS | Código en `backend/src/matches/` y `frontend/src/features/matches/`; accede a ligas/equipos solo por sus servicios |
| Arquitectura: monolito modular | PASS | Un módulo más en el backend existente |
| Regla de Derivación de Estadísticas | PASS | Esta HU no escribe marcadores; `home_score`/`away_score` nacen `null` |
| Estándares de Seguridad Obligatorios | PASS | Validación Pydantic, ORM, escritura por rol organizador |

Sin violaciones. **Complexity Tracking no aplica.**

*Re-check post Phase 1*: el diseño no introdujo elementos fuera de lo aprobado.
**PASS confirmado.**

## Project Structure

### Documentation (this feature)

```text
specs/005-programar-partido/
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── matches.openapi.yaml
├── quickstart.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/
├── src/matches/
│   ├── models.py         # Match (SQLAlchemy)
│   ├── schemas.py        # CreateMatchRequest, Match, PaginatedMatches
│   ├── service.py        # validaciones de equipos y liga
│   └── router.py         # POST/GET /leagues/{id}/matches, GET /matches/{id}
├── alembic/versions/     # migración de la tabla matches
└── tests/
    ├── contract/test_matches_contract.py
    └── integration/test_matches.py

frontend/
└── src/features/matches/
    ├── MatchesPage.tsx         # listado por liga
    ├── CreateMatchForm.tsx     # solo organizador
    ├── api.ts
    └── __tests__/
```

**Structure Decision**: misma estructura de
[`001`](../001-fundacion-y-autenticacion/plan.md). Esta HU puebla los
directorios `matches/` ya reservados allí; no crea carpetas de primer nivel.

## Complexity Tracking

*Sin violaciones que justificar — tabla vacía a propósito.*
