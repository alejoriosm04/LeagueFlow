# Implementation Plan: Registrar jugadores en un equipo

**Branch**: `004-registrar-jugadores` | **Date**: 2026-08-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-registrar-jugadores/spec.md`

**Hereda de `specs/001-fundacion-y-autenticacion`** (`AGENTS.md` §5): stack,
modelo de dominio y convenciones de API. Este plan **no re-decide** ninguno de
esos aspectos.

## Summary

Alta y consulta de jugadores dentro de un equipo: el organizador registra
jugadores con nombre obligatorio y, opcionalmente, dorsal y posición; el
dorsal es único dentro del equipo cuando está informado. Cualquiera consulta
la plantilla sin autenticarse. Los jugadores con historial no se eliminan: se
marcan inactivos. Decisiones propias en `research.md`, delta de modelo en
`data-model.md`, endpoints en `contracts/players.openapi.yaml`.

## Technical Context

Todo heredado de
[`specs/001-fundacion-y-autenticacion/plan.md`](../001-fundacion-y-autenticacion/plan.md).

**Deltas propios de esta spec**:

- **Storage**: añade la tabla `players`, con FK `ON DELETE RESTRICT` a `teams`.
- **Constraints**: unicidad parcial `(team_id, number)` cuando `number` no es
  nulo; rango y formato de dorsal/posición en `research.md`.
- **Performance Goals**: registrar una plantilla de 20 jugadores en menos de
  10 minutos (SC-001 de `spec.md`).
- **Scale/Scope**: hasta 30 jugadores por equipo (volumen de referencia de
  `001`).

Sin `NEEDS CLARIFICATION`: la spec pasó su checklist 16/16 y las decisiones
abiertas se resolvieron en `research.md`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio / regla | Estado | Cómo se cumple |
|---|---|---|
| I. La Especificación Manda | PASS | Cada endpoint traza a un FR; lo no especificado (rango de dorsal, formato de posición, alcance del borrado lógico) se resolvió en `research.md`, no en el código |
| II. Toda Regla de Negocio se Prueba | PASS | Unicidad de dorsal, pertenencia a un solo equipo, escritura solo organizador y borrado lógico tienen test propio en `tasks.md` |
| III. Contratos de API Explícitos | PASS | `contracts/players.openapi.yaml`, reutilizando envelope y paginación de `001` |
| IV. No Romper lo que ya Funciona | PASS | Solo añade tabla y endpoints; `teams` se toca únicamente con una FK nueva |
| V. Migraciones Versionadas | PASS | La tabla `players` entra como migración Alembic en esta HU |
| VI. Cero Secretos en el Repositorio | PASS | No introduce configuración nueva |
| VII. Código de IA con la Misma Vara | PASS | Regla de revisión de PR |
| VIII. Entregabilidad Independiente por Dominio | PASS | Código en `backend/src/players/` y `frontend/src/features/players/`; accede a `teams` solo por su servicio, no por su modelo interno |
| Arquitectura: monolito modular | PASS | Un módulo más en el backend existente |
| Regla de Derivación de Estadísticas | PASS (indirecto) | El borrado lógico de FR-005 existe para que goles y alineaciones históricas sigan cuadrando; `research.md` §3 fija que un jugador inactivo permanece visible en el historial |
| Estándares de Seguridad Obligatorios | PASS | Validación Pydantic, ORM, escritura por rol organizador |

Sin violaciones. **Complexity Tracking no aplica.**

*Re-check post Phase 1*: el diseño no introdujo elementos fuera de lo aprobado.
**PASS confirmado.**

## Project Structure

### Documentation (this feature)

```text
specs/004-registrar-jugadores/
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── players.openapi.yaml
├── quickstart.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/
├── src/players/
│   ├── models.py         # Player (SQLAlchemy)
│   ├── schemas.py        # CreatePlayerRequest, Player, PaginatedPlayers
│   ├── service.py        # unicidad de dorsal, borrado lógico
│   └── router.py         # POST/GET /teams/{id}/players, GET /players/{id}
├── alembic/versions/     # migración de la tabla players
└── tests/
    ├── contract/test_players_contract.py
    └── integration/test_players.py

frontend/
└── src/features/players/
    ├── PlayersPage.tsx         # plantilla por equipo
    ├── CreatePlayerForm.tsx    # solo organizador
    ├── api.ts
    └── __tests__/
```

**Structure Decision**: misma estructura de
[`001`](../001-fundacion-y-autenticacion/plan.md). Esta HU puebla los
directorios `players/` ya reservados allí; no crea carpetas de primer nivel.

## Complexity Tracking

*Sin violaciones que justificar — tabla vacía a propósito.*
