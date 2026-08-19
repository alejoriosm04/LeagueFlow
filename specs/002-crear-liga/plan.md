# Implementation Plan: Crear una liga

**Branch**: `002-crear-liga` | **Date**: 2026-08-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-crear-liga/spec.md`

**Hereda de `specs/001-fundacion-y-autenticacion`** (`AGENTS.md` §5): stack,
modelo de dominio y convenciones de API. Este plan **no re-decide** ninguno de
esos aspectos; solo documenta lo que esta HU añade.

## Summary

Alta y consulta de ligas: el organizador crea una liga con nombre y temporada
únicos; cualquiera puede listarlas y ver su detalle sin autenticarse. Es la HU
raíz del dominio — sin liga no hay equipos, jugadores ni partidos. Las
decisiones propias de esta HU (dónde vive la unicidad, comparación
insensible a mayúsculas, formato libre de temporada) están en `research.md`;
lo que añade al modelo, en `data-model.md`; los endpoints, en
`contracts/leagues.openapi.yaml`.

## Technical Context

Todo heredado de
[`specs/001-fundacion-y-autenticacion/plan.md`](../001-fundacion-y-autenticacion/plan.md):
Python 3.12 + FastAPI + Pydantic v2, PostgreSQL 16 + SQLAlchemy 2.0 async +
Alembic, React 18 + TypeScript + Vite, `pytest`/`Vitest`, sesión por cookie
`httpOnly`+`Secure`+`SameSite=None`, CORS restringido, despliegue Vercel +
Railway, CI en GitHub Actions.

**Deltas propios de esta spec**:

- **Storage**: añade la tabla `leagues` (primera migración tras `users`/`sessions`).
- **Performance Goals**: crear una liga en menos de 2 minutos para un
  organizador que usa la plataforma por primera vez (SC-001 de `spec.md`).
- **Scale/Scope**: hasta 10 ligas simultáneas (volumen de referencia de `001`).

Sin `NEEDS CLARIFICATION`: la spec pasó su checklist de calidad 16/16 y las
tres decisiones abiertas se resolvieron en `research.md`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio / regla | Estado | Cómo se cumple |
|---|---|---|
| I. La Especificación Manda | PASS | Cada endpoint de `contracts/` traza a un FR de `spec.md`; las decisiones no especificadas se documentaron en `research.md` en vez de inventarse en el código |
| II. Toda Regla de Negocio se Prueba | PASS | Unicidad `(name, season)`, normalización y control de rol tienen tarea de test propia en `tasks.md` |
| III. Contratos de API Explícitos | PASS | `contracts/leagues.openapi.yaml`, reutilizando el envelope de error y la paginación de `001` |
| IV. No Romper lo que ya Funciona | PASS | Solo añade tabla y endpoints nuevos; no toca `users`/`sessions` ni sus pruebas |
| V. Migraciones Versionadas | PASS | La tabla `leagues` entra como migración Alembic en esta misma HU |
| VI. Cero Secretos en el Repositorio | PASS | No introduce configuración nueva; usa las variables ya definidas en `001` |
| VII. Código de IA con la Misma Vara | PASS | Regla de proceso de PR; sin decisión de plan asociada |
| VIII. Entregabilidad Independiente por Dominio | PASS | Todo el código vive en `backend/src/leagues/` y `frontend/src/features/leagues/`; no importa modelos internos de otro módulo |
| Arquitectura: monolito modular | PASS | Un módulo más dentro del backend existente |
| Regla de Derivación de Estadísticas | N/A | Esta HU no toca clasificación ni estadísticas |
| Estándares de Seguridad Obligatorios | PASS | Validación por Pydantic, SQL vía ORM, escritura restringida por rol, errores sin stack trace (heredado de `001`) |

Sin violaciones. **Complexity Tracking no aplica.**

*Re-check post Phase 1*: el diseño no introdujo nada fuera de lo aprobado. La
única decisión con peso —duplicar la unicidad en servicio + constraint de base
de datos— refuerza el Principio II (regla de negocio verificable y a prueba de
carreras) en vez de tensionar ningún gate. **PASS confirmado.**

## Project Structure

### Documentation (this feature)

```text
specs/002-crear-liga/
├── plan.md              # este archivo
├── research.md          # Phase 0 — decisiones propias de esta HU
├── data-model.md        # Phase 1 — delta sobre el modelo compartido de 001
├── contracts/
│   └── leagues.openapi.yaml
├── quickstart.md        # Phase 1 — validación end-to-end
├── checklists/
│   └── requirements.md  # calidad de la spec (16/16)
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
backend/
├── src/leagues/          # módulo de esta HU
│   ├── models.py         # League (SQLAlchemy)
│   ├── schemas.py        # CreateLeagueRequest, League, PaginatedLeagues
│   ├── service.py        # unicidad, normalización, autoría
│   └── router.py         # POST /leagues, GET /leagues, GET /leagues/{id}
├── alembic/versions/     # migración de la tabla leagues
└── tests/
    ├── contract/test_leagues_contract.py
    └── integration/test_leagues.py

frontend/
└── src/features/leagues/
    ├── LeaguesPage.tsx       # listado público
    ├── LeagueDetailPage.tsx  # detalle público
    ├── CreateLeagueForm.tsx  # solo organizador
    ├── api.ts                # cliente sobre services/apiClient.ts
    └── __tests__/
```

**Structure Decision**: se mantiene la estructura de
[`001`](../001-fundacion-y-autenticacion/plan.md) (`backend/` + `frontend/`
separados, módulos backend por dominio). Esta HU solo puebla los directorios
`leagues/` que aquel plan ya había reservado; no introduce carpetas de primer
nivel nuevas.

## Complexity Tracking

*Sin violaciones que justificar — tabla vacía a propósito.*
