# Implementation Plan: Fundación técnica y autenticación

**Branch**: `001-fundacion-y-autenticacion` | **Date**: 2026-08-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-fundacion-y-autenticacion/spec.md`

**Nota**: este plan fija, además de la HU de autenticación, el stack técnico y
el modelo de dominio de **todo el proyecto** — ver el "Scope Note" en
`spec.md` y `AGENTS.md` §5. `specs/002-*` a `specs/011-*` referencian este
archivo y `data-model.md`; no los redefinen.

## Summary

Autenticación por sesión de servidor (cookie `httpOnly` + tabla `sessions`)
con dos roles (`organizador`, `operador`) y acceso público de solo lectura
sin cuenta, sobre un monolito modular: backend FastAPI + PostgreSQL vía
SQLAlchemy/Alembic, frontend React+TypeScript SPA. La aproximación técnica
completa (con alternativas descartadas) está en `research.md`; el modelo de
datos completo del proyecto en `data-model.md`; los endpoints de esta spec y
las convenciones de API compartidas en `contracts/`.

## Technical Context

**Language/Version**: Python 3.12 (backend) · TypeScript 5.x + React 18 (frontend)

**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0 (async),
Alembic, `passlib[bcrypt]` · React, Vite, React Router, React Testing Library

**Storage**: PostgreSQL 16

**Testing**: `pytest` + `httpx.AsyncClient` (backend, foco en reglas de
negocio) · `Vitest` + React Testing Library (frontend) · `Playwright` para el
camino crítico único crear liga → equipo → partido → clasificación

**Target Platform**: contenedor Linux (backend, Railway) · SPA estática servida
por Vercel (frontend) · navegador web (cliente)

**Project Type**: web (frontend + backend separados, consumidos vía HTTPS/JSON)

**Performance Goals**: login completo en menos de 5 segundos (SC-003 de esta
spec); vistas de consulta del resto del proyecto completas en menos de 2
segundos para una liga de 20 equipos / 190 partidos (referencia agregada de
`specs/007-*`, `specs/008-*`, `specs/011-*`, que heredan este backend)

**Constraints**: cookie de sesión `httpOnly` + `Secure` + `SameSite=Lax`; CORS
restringido por variable de entorno, nunca `*`; contraseñas nunca en texto
claro ni recuperables (FR-005); ningún stack trace al cliente (FR-012)

**Scale/Scope**: hasta 10 ligas simultáneas, 20 equipos por liga, 30 jugadores
por equipo (volumen de referencia usado en los Success Criteria de las specs
002-011)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio / regla | Estado | Cómo se cumple |
|---|---|---|
| I. La Especificación Manda | PASS | Este plan deriva de `spec.md`; ningún endpoint o entidad aquí carece de FR que lo respalde |
| II. Toda Regla de Negocio se Prueba | PASS | `pytest`/`Vitest` fijados en Technical Context; `research.md` §5 detalla el foco de pruebas |
| III. Contratos de API Explícitos | PASS | `contracts/auth.openapi.yaml` + `contracts/conventions.md`, versionados en esta carpeta; specs posteriores los extienden sin redefinir |
| IV. No Romper lo que ya Funciona | PASS | Se aplica en CI (`research.md` §8), no en este plan directamente |
| V. Migraciones Versionadas | PASS | Alembic fijado como herramienta de migraciones (`research.md` §3) |
| VI. Cero Secretos en el Repositorio | PASS | `SESSION_SECRET`, `DATABASE_URL`, etc. por variable de entorno; `.env.example` documentará las llaves vacías |
| VII. Código de IA con la Misma Vara | PASS | No aplica una decisión de plan específica; es una regla de proceso de PR |
| VIII. Entregabilidad Independiente por Dominio | PASS | Project Structure (abajo) separa módulos backend por dominio: `auth`, `leagues`, `teams`, `players`, `matches`, `statistics` |
| Arquitectura: monolito modular, no microservicios | PASS | Un solo backend FastAPI, un solo frontend SPA |
| Regla de Derivación de Estadísticas | PASS | `data-model.md`: `Standings` y `PlayerStatistics` documentados como derivados, sin tabla editable |
| Estándares de Seguridad Obligatorios | PASS | Pydantic (validación), SQLAlchemy (sin SQL concatenado), CORS restringido, sin stack traces — todos en `research.md` |

Sin violaciones. **Complexity Tracking no aplica** (ver sección al final,
vacía a propósito).

*Re-check post Phase 1*: el diseño de `data-model.md` y `contracts/` no
introdujo ningún elemento fuera de lo aprobado arriba — Standings y
PlayerStatistics se modelaron explícitamente como no-persistentes/derivados,
reforzando el gate de "Regla de Derivación de Estadísticas" en vez de
tensionarlo. **PASS confirmado.**

## Project Structure

### Documentation (this feature)

```text
specs/001-fundacion-y-autenticacion/
├── plan.md              # este archivo
├── research.md          # Phase 0 — decisiones técnicas de todo el proyecto
├── data-model.md         # Phase 1 — modelo de dominio completo del proyecto
├── contracts/
│   ├── conventions.md    # convenciones de API compartidas por todas las specs
│   └── auth.openapi.yaml # endpoints propios de esta spec
├── quickstart.md         # Phase 1 — validación end-to-end de esta spec
└── tasks.md              # Phase 2 (/speckit-tasks — aún no generado)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── auth/            # User, Session, login/logout — esta spec
│   ├── leagues/         # League — specs/002-crear-liga
│   ├── teams/           # Team — specs/003-registrar-equipos
│   ├── players/         # Player — specs/004-registrar-jugadores
│   ├── matches/         # Match, MatchLineup, MatchEvent, ResultCorrectionRequest
│   │                     #   — specs/005, 006, 009, 010
│   ├── statistics/      # Standings, PlayerStatistics (derivados, solo lectura)
│   │                     #   — specs/008, 010, 011
│   └── core/            # config, sesión de DB, envelope de error, CORS, main.py
├── alembic/              # migraciones versionadas (Principio V)
└── tests/
    ├── contract/         # valida cada módulo contra su contracts/*.yaml
    ├── integration/      # reglas de negocio end-to-end (pytest, foco constitución)
    └── unit/

frontend/
├── src/
│   ├── features/
│   │   ├── auth/         # login, sesión — esta spec
│   │   ├── leagues/ teams/ players/ matches/ standings/ statistics/ dashboard/
│   │   │                 # una carpeta por spec 002-011
│   ├── components/       # UI compartida
│   └── services/         # cliente HTTP, un módulo por recurso de contracts/
└── tests/                # Vitest junto a cada componente

.github/
└── workflows/
    └── ci.yml            # lint -> unit -> integration -> dependency scan -> build
                           #   en cada PR; merge a main dispara deploy (research.md §8)
```

**Structure Decision**: Opción "Web application" del template (`backend/` +
`frontend/` separados), consumidos vía HTTPS/JSON — no hay opción de
"single project" porque el dominio exige frontend y backend independientes
(Arquitectura de Referencia de la constitución). Dentro de `backend/src/`, la
separación por carpeta de dominio (`auth`, `leagues`, `teams`, `players`,
`matches`, `statistics`) es literal a los módulos que exige el Principio VIII
y a los que confirmó el equipo: *"Backend: FastAPI (Python), organizado en
módulos internos por dominio: League, Team, Player, Match, Statistics."* Cada
módulo expone su propio router/schema; ningún módulo importa el modelo interno
de otro — solo su interfaz pública (servicio o schema Pydantic).

## Complexity Tracking

*Sin violaciones que justificar — tabla vacía a propósito.*
