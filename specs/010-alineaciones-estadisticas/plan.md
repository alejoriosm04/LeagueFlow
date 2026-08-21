# Implementation Plan: Registrar alineaciones y consultar estadisticas de jugadores

**Branch**: `010-alineaciones-estadisticas` | **Date**: 2026-08-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/010-alineaciones-estadisticas/spec.md`

## Summary

Extender el dominio Match con `MatchLineup` para registrar y corregir la
alineacion de un partido con `PUT /matches/{id}/lineup` (solo operador u
organizador), respetando la coherencia con eventos ya registrados. Extender el
dominio Statistics con consultas derivadas y de solo lectura para tabla de
goleadores y ficha individual de jugador, ambas publicas. No se redefine stack,
arquitectura, auth, hosting ni modelo base de `specs/001-fundacion-y-autenticacion`:
esta HU solo agrega `MatchLineup` y `PlayerStatistics` derivada.

## Technical Context

**Language/Version**: Python 3.12 · TypeScript 5.7 + React 18

**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0 async, Alembic ·
React, Vite, React Router 7, React Testing Library

**Storage**: PostgreSQL 16; una tabla nueva para alineaciones (`match_lineups`);
`PlayerStatistics` es consulta derivada (sin tabla persistida)

**Testing**: pytest (unit, contract, integration) + httpx.AsyncClient · Vitest +
React Testing Library

**Target Platform**: backend Linux/Railway · SPA Vercel · navegador web

**Project Type**: aplicacion web con backend y frontend separados

**Performance Goals**: mantener SC-001 (100% coincidencia con conteo real de
eventos + alineaciones); top scorer identificable de inmediato en la interfaz
(SC-002)

**Constraints**:
- Escritura de alineacion protegida para operador u organizador (FR-005)
- Lecturas estadisticas publicas, sin autenticacion (FR-011)
- Alineacion opcional: un partido puede estar `finished` sin alineacion y la API
  debe indicarlo explicitamente (FR-004)
- Estadisticas siempre derivadas, nunca editables (FR-006, FR-007, FR-008)
- Comportamiento de correccion cuando se excluye un goleador de la alineacion:
  **NEEDS CLARIFICATION**
- Recalculo cuando una correccion de resultado elimina un gol contabilizado:
  **NEEDS CLARIFICATION**

**Scale/Scope**: 1 tabla nueva, 3 endpoints principales, extension del detalle
de partido, y cobertura de integracion faltante de FR-003 heredada de 009

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio / regla | Estado | Como se cumple |
|---|---|---|
| I. La Especificacion Manda | PASS | Todo el diseno traza a FR-001..FR-011 y al compromiso heredado de 009; los puntos abiertos se resuelven en `research.md` |
| II. Toda Regla de Negocio se Prueba | PASS | Se planifican pruebas unitarias/integracion/contrato para validacion de pertenencia de jugador, coherencia lineup-eventos y derivacion de estadisticas |
| III. Contratos de API Explicitos | PASS | Se define `contracts/lineups-statistics.openapi.yaml` con endpoints protegidos/publicos y codigos de error |
| IV. No Romper lo que ya Funciona | PASS | Cambios aditivos; no se altera el stack ni se reemplazan contratos existentes |
| V. Migraciones Versionadas | PASS | Una migracion versionada crea `match_lineups`; sin cambios manuales en BD |
| VI. Cero Secretos | PASS | No se agregan credenciales ni secretos |
| VII. Codigo de IA con la misma vara | PASS | Misma suite y quality gates del proyecto |
| VIII. Entregabilidad Independiente | PASS | `MatchLineup` vive en Match; `PlayerStatistics` vive en Statistics y consume interfaces de Match/Player |
| Derivacion de Estadisticas (NO NEGOCIABLE) | PASS | Goles y partidos jugados se calculan en lectura desde `MatchEvent` y `MatchLineup`, sin columnas editables |
| Arquitectura y seguridad | PASS | Monolito modular, validacion de payload, ORM parametrizado, `requiere_rol` en escrituras, GET publicos |

*Re-check post Phase 1*: con las decisiones de `research.md` el diseno conserva
derivacion estricta desde hechos (`MatchEvent` + `MatchLineup`), y define que la
coherencia lineup-eventos se protege al corregir alineaciones. **PASS**.

## Project Structure

### Documentation (this feature)

```text
specs/010-alineaciones-estadisticas/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/lineups-statistics.openapi.yaml
└── tasks.md                 # generado por /speckit-tasks
```

### Source Code (repository root)

```text
backend/
├── alembic/versions/<hash>_crear_tabla_match_lineups.py
├── src/
│   ├── matches/
│   │   ├── models.py        # + MatchLineup
│   │   ├── schemas.py       # + MatchLineupInput/MatchLineupView
│   │   ├── service.py       # + guardar_alineacion, obtener_alineacion, jugadores_alineados real
│   │   └── router.py        # + PUT/GET /matches/{id}/lineup y bandera en ficha
│   └── statistics/
│       ├── schemas.py       # + PlayerStatistics, TopScorerRow
│       ├── service.py       # + obtener_ficha_jugador, tabla_goleadores
│       └── router.py        # + GET /players/{id}/statistics, /leagues/{id}/top-scorers
└── tests/
    ├── unit/test_lineup_rules.py
    ├── contract/test_lineups_statistics_contract.py
    └── integration/test_lineups_statistics.py

frontend/src/features/
├── matches/MatchDetailPage.tsx      # estado explicito de alineacion (registrada/faltante)
└── statistics/
    ├── api.ts
    ├── TopScorersPage.tsx           # resalta maximo goleador
    ├── PlayerStatsPage.tsx
    └── __tests__/statistics.test.tsx
```

**Structure Decision**: mantener el patron existente: reglas de dominio puras en
`matches`/`statistics`, autorizacion en router con `requiere_rol`, y derivacion en
lectura (sin tabla acumulada de estadisticas).

## Phase 0 Research Focus

1. Definir semantica de correccion de alineacion si excluye jugador con goles
   ya registrados.
2. Definir semantica de recalculo ante correcciones de resultado con impacto en
   eventos.
3. Definir forma de exponer "alineacion faltante" en la API de ficha de partido.

Resultado: ver decisiones cerradas en `research.md`.

## Complexity Tracking

*Sin violaciones que justificar.*
