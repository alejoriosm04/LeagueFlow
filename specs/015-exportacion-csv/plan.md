# Implementation Plan: Exportacion de clasificacion y calendario a CSV

**Branch**: `015-exportacion-csv` | **Date**: 2026-08-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/015-exportacion-csv/spec.md`

## Summary

Anadir dos descargas publicas CSV que consumen las interfaces existentes de
`statistics`, `matches`, `teams` y `leagues`. Un modulo transversal `exports`
orquesta las lecturas y serializa con la biblioteca estandar de Python, sin
recalcular, persistir ni modificar datos. El frontend anade una accion en cada
vista. Stack y dominio se heredan sin cambios de
[`001/plan.md`](../001-fundacion-y-autenticacion/plan.md) y
[`001/data-model.md`](../001-fundacion-y-autenticacion/data-model.md).

## Technical Context

**Language/Version**: Python 3.12 · TypeScript 5.7 + React 18

**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0 async, modulo
estandar `csv` · React, Vite, React Router 7, React Testing Library

**Storage**: PostgreSQL 16, solo lectura por servicios; sin migracion

**Testing**: pytest + httpx.AsyncClient · Vitest + React Testing Library

**Target Platform**: Linux/Railway · SPA Vercel · navegador · LibreOffice Calc
24.2+ y Microsoft Excel para Microsoft 365 de escritorio

**Project Type**: aplicacion web, backend y frontend separados

**Performance Goals**: exportar hasta 20 equipos/190 partidos sin perder filas;
desde el detalle de liga, iniciar descarga en 2 clics/toques o menos (SC-001)

**Constraints**: publico; solo CSV; UTF-8 con BOM y quoting RFC 4180; orden
identico a vistas fuente; filename seguro; sin escritura, migracion, dependencia
nueva ni calculo alternativo

**Scale/Scope**: dos GET, dos acciones, hasta 20/190 filas

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio / regla | Estado | Como se cumple |
|---|---|---|
| I. Spec manda | PASS | Recursos, anonimato, formato y vacios trazan a FR-001–FR-007 |
| II. Reglas probadas | PASS | pytest cubre equivalencia, orden, vacios, quoting y formato; Vitest, acciones publicas |
| III. Contratos explicitos | PASS | `contracts/exports.openapi.yaml` define binarios, headers y errores |
| IV. No regresiones | PASS | Solo se anaden rutas/controles; 007/008 no cambian |
| V. Migraciones | PASS | No hay esquema ni migracion |
| VI. Cero secretos | PASS | No hay configuracion ni credenciales nuevas |
| VII. Misma vara | PASS | pytest, Vitest, ruff, ESLint, build y auditorias |
| VIII. Dominios independientes | PASS | `exports` consume interfaces publicas; no hay dependencia inversa |
| Estadisticas derivadas | PASS | Se llama `StandingsService`; nunca se calcula ni almacena posiciones |
| Arquitectura/seguridad | PASS | Monolito modular, validacion de UUID/formato y serializacion segura |

*Re-check post Phase 1*: solo hay proyecciones efimeras y dos GET; no hay
persistencia, escritura ni recalculo. **PASS**, sin desviaciones.

## Project Structure

### Documentation (this feature)

```text
specs/015-exportacion-csv/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/exports.openapi.yaml
└── tasks.md                       # posterior: /speckit-tasks
```

### Source Code (repository root)

```text
backend/
├── src/exports/{router.py,service.py,csv_serializer.py}
├── src/main.py
└── tests/{unit/test_csv_serializer.py,contract/test_exports_contract.py,integration/test_exports.py}

frontend/src/features/
├── exports/{api.ts,__tests__/exports.test.tsx}
├── matches/MatchesPage.tsx
└── standings/StandingsPage.tsx
```

**Structure Decision**: `exports` es capacidad transversal de lectura, no un
dominio persistente. Centraliza serializacion y descarga; depende en una sola
direccion de las interfaces de los dominios fuente.

## Complexity Tracking

*Sin violaciones que justificar.*
