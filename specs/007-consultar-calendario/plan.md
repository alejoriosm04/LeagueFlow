# Implementation Plan: Consultar el calendario y los resultados

**Branch**: `007-consultar-calendario` | **Date**: 2026-08-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/007-consultar-calendario/spec.md`

## Summary

Convertir el listado público existente en un calendario que separe próximos
(`scheduled`, fecha ascendente) y jugados (`finished`, fecha descendente),
muestre marcadores y filtre por los cuatro estados de `Match`. Se extiende de
forma compatible `GET /leagues/{leagueId}/matches` con `status` opcional; el
frontend recorre la paginación para cubrir hasta 190 partidos. No se añaden
entidades, dependencias ni migraciones.

## Technical Context

**Language/Version**: Python 3.12 · TypeScript 5.7 + React 18

**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0 async · React,
Vite, React Router 7, React Testing Library

**Storage**: PostgreSQL 16; solo lectura de `matches`, `teams` y `leagues`

**Testing**: pytest + httpx.AsyncClient · Vitest + React Testing Library

**Target Platform**: backend Linux/Railway · SPA Vercel · navegador web

**Project Type**: aplicación web con backend y frontend separados

**Performance Goals**: vista completa en menos de 2 segundos con 20 equipos y
190 partidos (SC-001)

**Constraints**: endpoint público; `page_size <= 100` por compatibilidad;
orden estable con desempate por `id`; ninguna escritura ni migración

**Scale/Scope**: una vista pública, un endpoint ampliado, cuatro estados
filtrables y hasta 190 partidos por liga

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio / regla | Estado | Cómo se cumple |
|---|---|---|
| I. La Especificación Manda | PASS | Filtro, agrupación y acceso público derivan de FR-001–FR-003; la semántica de estados queda en Assumptions |
| II. Toda Regla de Negocio se Prueba | PASS | pytest cubre filtro/orden y Vitest agrupación, marcador, vacío y anonimato |
| III. Contratos de API Explícitos | PASS | `contracts/calendar.openapi.yaml` documenta la extensión compatible |
| IV. No Romper lo existente | PASS | `status` es opcional y sin él se conserva el orden de 005; habrá regresión completa |
| V. Migraciones Versionadas | PASS | No hay cambio de esquema |
| VI. Cero Secretos | PASS | No se añaden configuración ni credenciales |
| VII. Código de IA con la misma vara | PASS | Se mantienen pytest, Vitest, lint, build y auditorías |
| VIII. Entregabilidad Independiente | PASS | El cambio permanece en `matches` y consume la API pública de equipos |
| Arquitectura y seguridad | PASS | Monolito modular, ORM parametrizado, enum validado y errores compartidos |

*Re-check post Phase 1*: no existe delta de persistencia y el contrato solo
añade un parámetro opcional. No hay desviaciones. **PASS**.

## Project Structure

### Documentation (this feature)

```text
specs/007-consultar-calendario/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/calendar.openapi.yaml
└── tasks.md                 # generado por /speckit-tasks
```

### Source Code (repository root)

```text
backend/
├── src/matches/{router.py,schemas.py,service.py}
├── scripts/seed_calendar_performance.py
└── tests/{contract/test_calendar_contract.py,integration/test_calendar.py}

frontend/src/features/
├── leagues/LeagueDetailPage.tsx
└── matches/
    ├── api.ts
    ├── MatchesPage.tsx
    └── __tests__/calendar.test.tsx
```

**Structure Decision**: se reutiliza el módulo `matches` establecido en 001.
El calendario es una proyección de lectura de `Match`; crear otro módulo
introduciría una frontera artificial en el mismo dominio.

## Complexity Tracking

*Sin violaciones que justificar.*
