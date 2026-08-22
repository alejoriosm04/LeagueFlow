# Implementation Plan: Tarjetas y sanciones disciplinarias

**Branch**: `014-tarjetas-sanciones` | **Date**: 2026-08-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/014-tarjetas-sanciones/spec.md`

**Nota (AGENTS.md §5)**: este plan **no** re-decide stack ni modelo de dominio.
Referencia `specs/001-fundacion-y-autenticacion/plan.md` y `data-model.md`.
Solo documenta lo que **añade** esta HU: tipos de tarjeta en `MatchEvent`,
módulo `sanctions/` y consulta pública de ficha disciplinaria. Guía operativa:
`docs/plan-paralelo-013-017.md` §HU 014.

## Summary

Ampliar `MatchEvent` para `YELLOW_CARD` y `RED_CARD` (CHECK + schemas + mismo
`POST /matches/{id}/events` que 009), reutilizando validaciones de estado,
equipo y alineación. Añadir `backend/src/sanctions/` que deriva en lectura si
un jugador está suspendido (1 roja, o 2 amarillas en partidos distintos) y
expone `GET /players/{id}/discipline` público. Frontend: registrar tarjetas en
la ficha del partido y página pública de disciplina. Una migración que solo
toca el CHECK; orden de merge `013 → 014 → 016 → 017`.

## Technical Context

**Language/Version**: Python 3.12 · TypeScript 5.x + React 18 (fijados en 001)

**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0 async, Alembic ·
React, Vite, React Router, React Testing Library (sin dependencias nuevas)

**Storage**: PostgreSQL 16; **sin tabla nueva** — solo `ALTER` del CHECK
`ck_match_events_type_supported` en `match_events`

**Testing**: pytest (unit, contract, integration) + httpx.AsyncClient · Vitest +
React Testing Library

**Target Platform**: backend Linux/Railway · SPA Vercel · navegador web

**Project Type**: aplicación web con backend y frontend separados

**Performance Goals**: registrar una tarjeta en ≤ 2 interacciones (SC-001);
suspensión visible en la siguiente lectura (SC-002); sin meta de latencia propia

**Constraints**: escritura con rol operador u organizador; lectura pública de
ficha (FR-008); suspensión nunca persistida (FR-007); no bloquear alineaciones
de suspendidos (Out of Scope); migración en paralelo re-punta tras 013
(AGENTS.md)

**Scale/Scope**: ampliación de enum/CHECK, un módulo de lectura, un endpoint
GET nuevo, UI de tarjeta + ficha; volumen de referencia de 001 (≤ 20 equipos)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio / regla | Estado | Cómo se cumple |
|---|---|---|
| I. La Especificación Manda | PASS | Endpoints y reglas trazan a FR-001–FR-008; clarificación de suspensión sin expiración ya en `spec.md` |
| II. Toda Regla de Negocio se Prueba | PASS | Unitarias para acumulación/suspensión y validación de tarjeta; contrato OpenAPI; integración de registro + ficha |
| III. Contratos de API Explícitos | PASS | `contracts/cards-sanctions.openapi.yaml` (extiende eventos + ficha) |
| IV. No Romper lo que ya Funciona | PASS | Solo se amplía el CHECK y el enum; goles y `consistency` siguen igual; no se recrean índices ajenos |
| V. Migraciones Versionadas | PASS | Una migración versionada del CHECK; re-puntero de `down_revision` al merge (paralelo) |
| VI. Cero Secretos | PASS | Sin config ni credenciales nuevas |
| VII. Código de IA con la misma vara | PASS | Mismos pytest, Vitest, Ruff, ESLint, build y auditorías |
| VIII. Entregabilidad Independiente | PASS | Captura en `matches/`; derivación en `sanctions/` consumiendo interfaz de matches/players (patrón `statistics/`) |
| Derivación de Estadísticas / derivados | PASS | `suspended` y conteos se calculan en lectura; no hay bandera editable |
| Arquitectura y seguridad | PASS | Monolito modular, Pydantic + CHECK, `requiere_rol` en escritura, lecturas públicas sin cookie |

*Re-check post Phase 1*: el diseño no añade tablas ni campos a Player/Match;
solo amplía el CHECK previsto por FR-004 de 009 y un módulo de lectura.
**PASS**. Complexity Tracking vacío.

## Project Structure

### Documentation (this feature)

```text
specs/014-tarjetas-sanciones/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/cards-sanctions.openapi.yaml
└── tasks.md                 # generado por /speckit-tasks
```

### Source Code (repository root)

```text
backend/
├── alembic/versions/<hash>_ampliar_tipos_match_events_tarjetas.py
├── src/
│   ├── matches/
│   │   ├── models.py          # CHECK type ∈ GOAL|YELLOW_CARD|RED_CARD
│   │   ├── schemas.py         # EventType ampliado; CreateEventInput.type requerido
│   │   ├── goal_rules.py      # o event_rules.py — validación compartida gol/tarjeta
│   │   ├── service.py         # registrar_tarjeta / generalizar registrar_evento
│   │   └── router.py          # mismo POST/GET /matches/{id}/events
│   ├── sanctions/             # NUEVO — patrón statistics/
│   │   ├── rules.py           # puro: conteos + suspended
│   │   ├── schemas.py         # PlayerDiscipline
│   │   ├── service.py         # lee eventos vía MatchService / puerto
│   │   └── router.py          # GET /players/{id}/discipline
│   └── main.py                # include_router(sanctions)
└── tests/
    ├── unit/test_card_rules.py
    ├── unit/test_sanction_rules.py
    ├── contract/test_cards_sanctions_contract.py
    └── integration/test_cards_sanctions.py

frontend/src/
├── routes.tsx                 # + ruta pública de ficha disciplinaria
├── features/events/           # + CardForm / type selector (amarilla/roja)
└── features/sanctions/        # NUEVO — api + DisciplinePage + tests
```

**Structure Decision**: las tarjetas viven en `matches` porque son hechos del
partido (igual que goles). La ficha y la regla de suspensión viven en
`sanctions/` porque son vistas derivadas del jugador, no captura de eventos —
espejo de `statistics/` respecto a partidos. El frontend separa el formulario
(events, ya existente) de la página de consulta (sanctions).

## Complexity Tracking

> Sin violaciones que justificar. Tabla vacía a propósito.
