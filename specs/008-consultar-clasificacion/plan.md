# Implementation Plan: Consultar la clasificación

**Branch**: `008-consultar-clasificacion` | **Date**: 2026-08-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/008-consultar-clasificacion/spec.md`

## Summary

Estrenar el dominio **Statistics** con la tabla de posiciones: un endpoint
público `GET /leagues/{leagueId}/standings` que deriva la clasificación en cada
consulta desde los partidos `finished` de la liga, y una vista de solo lectura
que la muestra. El cálculo vive en una función pura
(`MatchResult -> StandingsCalculator -> Standings`, constitución) que
`statistics` alimenta llamando a `MatchService` y `TeamService`, nunca a sus
modelos. No hay tabla de standings, ni escritura, ni migración: FR-002 se
cumple por construcción y SC-002 sale gratis.

## Technical Context

**Language/Version**: Python 3.12 · TypeScript 5.7 + React 18

**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0 async · React,
Vite, React Router 7, React Testing Library

**Storage**: PostgreSQL 16; solo lectura de `matches`, `teams` y `leagues` a
través de los servicios de esos dominios. Sin persistencia propia.

**Testing**: pytest (unit, contract, integration) + httpx.AsyncClient · Vitest +
React Testing Library

**Target Platform**: backend Linux/Railway · SPA Vercel · navegador web

**Project Type**: aplicación web con backend y frontend separados

**Performance Goals**: tabla completa de 20 equipos visible en menos de 2
segundos (SC-003), sobre una liga de 190 partidos

**Constraints**: endpoint público sin autenticación (FR-008); recurso de solo
lectura, sin verbo de escritura alguno (FR-002); orden total y estable entre
consultas sucesivas (FR-006); ninguna migración

**Scale/Scope**: una vista pública nueva, un endpoint nuevo, dos métodos
añadidos a interfaces de dominio existentes, hasta 20 filas por liga

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio / regla | Estado | Cómo se cumple |
|---|---|---|
| I. La Especificación Manda | PASS | Cada decisión traza a FR-001–FR-008; lo que la spec no fijaba (equipos con fila, correcciones pendientes, `in_progress`, empate absoluto) quedó escrito como *Assumption* en `spec.md`, no inventado en el código |
| II. Toda Regla de Negocio se Prueba | PASS | Puntuación, desempates y exclusión de no finalizados en unit tests sobre la función pura; FR-002 y FR-008 en tests de contrato; SC-002 en integración; la vista en Vitest |
| III. Contratos de API Explícitos | PASS | `contracts/standings.openapi.yaml` define recurso, orden, envelope de error y el `405` de FR-002 |
| IV. No Romper lo que ya Funciona | PASS | Solo se añade: router nuevo, dos métodos nuevos de servicio, ninguna firma existente cambia. Regresión completa antes del PR |
| V. Migraciones Versionadas | PASS | No hay cambio de esquema (data-model.md §Migración) |
| VI. Cero Secretos | PASS | No se añade configuración ni credencial; se reutiliza el script de datos de 007, que ya toma el organizador de `SEED_ADMIN_USERNAME` |
| VII. Código de IA con la misma vara | PASS | Mismos pytest, Vitest, ruff, build y auditorías que el resto |
| VIII. Entregabilidad Independiente | PASS | `statistics` no importa `Match` ni `Team`: consume `MatchService.listar_finalizados` y `TeamService.listar_por_liga`. Sin dependencia circular: `statistics -> matches/teams`, nunca al revés |
| Derivación de Estadísticas (NO NEGOCIABLE) | PASS | Standings no se almacena: se recalcula en cada lectura. No existe endpoint, panel ni script que la edite, y el `405` lo prueba |
| Arquitectura y seguridad | PASS | Monolito modular, ORM parametrizado, `leagueId` validado como UUID por FastAPI, errores por el envelope compartido sin stack trace |

*Re-check post Phase 1*: el diseño no introduce persistencia, ni entidad nueva,
ni dependencia nueva, ni ruta de escritura. El contrato solo añade un recurso
`GET`. **PASS**, sin desviaciones que justificar.

## Project Structure

### Documentation (this feature)

```text
specs/008-consultar-clasificacion/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/standings.openapi.yaml
└── tasks.md                 # generado por /speckit-tasks
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── statistics/          # módulo ya reservado, hoy vacío
│   │   ├── calculator.py    # función pura: equipos + partidos -> filas ordenadas
│   │   ├── schemas.py       # Standings, StandingsRow
│   │   ├── service.py       # orquesta MatchService + TeamService + calculator
│   │   └── router.py        # GET /leagues/{liga_id}/standings
│   ├── matches/service.py   # + listar_finalizados(league_id)
│   ├── teams/service.py     # + listar_por_liga(league_id)
│   └── main.py              # + include_router(statistics_router)
└── tests/
    ├── unit/test_standings_calculator.py
    ├── contract/test_standings_contract.py
    └── integration/test_standings.py

frontend/src/
├── features/
│   ├── leagues/LeagueDetailPage.tsx      # + enlace "Ver clasificación"
│   └── standings/
│       ├── api.ts
│       ├── StandingsPage.tsx
│       └── __tests__/standings.test.tsx
└── routes.tsx                            # + /leagues/:id/standings (pública)
```

**Structure Decision**: se estrena `backend/src/statistics/`, el módulo que la
constitución reserva para el dominio Statistics y que hoy solo contiene
`__init__.py`. La clasificación no pertenece a `matches`: consume partidos pero
su regla de negocio es la puntuación y el orden, y de ahí colgarán las
estadísticas de 009–011. En el frontend, `features/standings/` sigue la misma
partición por feature que el resto de la SPA.

## Complexity Tracking

*Sin violaciones que justificar.*
