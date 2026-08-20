# Implementation Plan: Registrar goles por jugador

**Branch**: `009-registrar-goles` | **Date**: 2026-08-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/009-registrar-goles/spec.md`

## Summary

Implementar `MatchEvent` —ya declarada en el modelo de dominio de 001— como
tabla nueva en el dominio Match, con `POST /matches/{id}/events` para registrar
goles (operador u organizador) y `GET` público que devuelve los eventos junto a
un bloque de consistencia con el marcador oficial. El equipo se deriva del
jugador. El marcador oficial no se toca: sigue siendo la única fuente de la
clasificación de 008. FR-003 (alineaciones) se implementa como regla probada
detrás de un puerto cuya fuente de datos llega con 010 — ver desviación al
final.

## Technical Context

**Language/Version**: Python 3.12 · TypeScript 5.7 + React 18

**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0 async, Alembic ·
React, Vite, React Router 7, React Testing Library

**Storage**: PostgreSQL 16; **una tabla nueva** (`match_events`) y una
migración con `down_revision = "d6e7f8a9b0c1"`

**Testing**: pytest (unit, contract, integration) + httpx.AsyncClient · Vitest +
React Testing Library

**Target Platform**: backend Linux/Railway · SPA Vercel · navegador web

**Project Type**: aplicación web con backend y frontend separados

**Performance Goals**: registrar los goles de un partido en menos de 1 minuto
de interacción (SC-001); ninguna meta de latencia propia

**Constraints**: escritura con rol operador u organizador (FR-006); lectura
pública; el descuadre con el marcador advierte pero nunca bloquea (FR-005); el
enum de tipos debe poder crecer sin rediseño (FR-004)

**Scale/Scope**: una tabla, dos endpoints, una migración, una vista de ficha de
partido ampliada; decenas de eventos por partido

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio / regla | Estado | Cómo se cumple |
|---|---|---|
| I. La Especificación Manda | PASS | Cada endpoint y validación traza a FR-001–FR-006; lo que la spec no fijaba (estados que admiten goles, forma de la advertencia, publicidad del listado, alcance sin edición) queda escrito como decisión en `research.md` y como *Assumption* en `spec.md` |
| II. Toda Regla de Negocio se Prueba | PASS con matiz | Puntuación de reglas, FR-002, FR-004 y FR-005 con pruebas unitarias, de contrato e integración. **FR-003 queda con prueba unitaria pero sin integración** hasta 010 — ver Complexity Tracking |
| III. Contratos de API Explícitos | PASS | `contracts/events.openapi.yaml` define ambos verbos, códigos de error y el bloque de consistencia |
| IV. No Romper lo que ya Funciona | PASS | Solo se añade: tabla, servicio, router y vista. Ninguna firma existente cambia y el marcador oficial no se toca. La migración no altera índices ajenos (research.md §7) |
| V. Migraciones Versionadas | PASS | Una migración versionada crea `match_events`; nada a mano sobre la base |
| VI. Cero Secretos | PASS | No se añade configuración ni credencial |
| VII. Código de IA con la misma vara | PASS | Mismos pytest, Vitest, Ruff, ESLint, build y auditorías |
| VIII. Entregabilidad Independiente | PASS | `MatchEvent` vive en el dominio Match y consume `PlayerService`/`TeamService` por su interfaz pública. `statistics` no se toca: la derivación de goleadores es de 010 |
| Derivación de Estadísticas (NO NEGOCIABLE) | PASS | Los eventos son **hechos capturados**, no estadísticas derivadas. La clasificación sigue derivándose solo del marcador; el bloque `consistency` se calcula al leer y no se almacena |
| Arquitectura y seguridad | PASS | Monolito modular, ORM parametrizado, payload validado por Pydantic y por CHECK en base, `requiere_rol` en la escritura, envelope de error compartido |

*Re-check post Phase 1*: el diseño añade una tabla prevista por 001, ningún
campo a entidades existentes y ninguna dependencia nueva. La única desviación
es la cobertura diferida de FR-003, registrada abajo. **PASS**.

## Project Structure

### Documentation (this feature)

```text
specs/009-registrar-goles/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/events.openapi.yaml
└── tasks.md                 # generado por /speckit-tasks
```

### Source Code (repository root)

```text
backend/
├── alembic/versions/<hash>_crear_tabla_match_events.py   # tabla nueva
├── src/
│   ├── matches/
│   │   ├── models.py        # + MatchEvent
│   │   ├── schemas.py       # + CreateEventInput, MatchEvent, MatchEvents, EventConsistency
│   │   ├── goal_rules.py    # funciones puras: validación de FR-002/FR-003 y consistencia FR-005
│   │   ├── service.py       # + registrar_gol, listar_eventos, jugadores_alineados (puerto)
│   │   └── router.py        # + POST/GET /matches/{id}/events
│   └── players/service.py   # sin cambios: se consume obtener_jugador
└── tests/
    ├── unit/test_goal_rules.py
    ├── contract/test_events_contract.py
    └── integration/test_events.py

frontend/src/features/
├── matches/MatchDetailPage.tsx     # + sección de goles y advertencia
└── events/
    ├── api.ts
    ├── GoalForm.tsx                # solo visible para operador/organizador
    └── __tests__/events.test.tsx
```

**Structure Decision**: los eventos se suman al módulo `matches` existente, como
hizo 006 con las solicitudes de corrección: un evento no existe fuera de su
partido. Las reglas se extraen a `goal_rules.py` como funciones puras —el mismo
patrón que el `StandingsCalculator` de 008— para que FR-002, FR-003 y FR-005 se
prueben sin base de datos; el servicio solo aporta los datos. En el frontend se crea `features/events/` porque el formulario y su
cliente tienen ciclo propio, y se enganchan en la ficha de partido que ya
existe.

## Complexity Tracking

> Desviación que debe aprobarse en la revisión del PR.

| Violación | Por qué es necesaria | Alternativa más simple descartada porque |
|---|---|---|
| FR-003 se implementa con prueba unitaria pero **sin cobertura de integración** en esta HU | `MatchLineup` es entidad de `specs/010-alineaciones-estadisticas`; en 009 no existe forma de crear una alineación contra la que probar. La regla sí queda escrita y probada con un doble del puerto `jugadores_alineados`, de modo que el Acceptance Scenario 3 no se queda sin prueba (Principio II) | Crear `match_lineups` en 009 invadiría el alcance de 010 y fijaría un esquema que su spec aún puede cambiar; implementar 010 antes altera el orden del backlog y 010 depende de los eventos que produce 009 (su FR-006); declarar FR-003 fuera de alcance archivaría un MUST en silencio |

**Compromiso asociado**: el plan de `specs/010-alineaciones-estadisticas` DEBE
incluir la prueba de integración del Acceptance Scenario 3 de esta spec y la
implementación real del puerto. Sin eso, FR-003 queda sin cobertura extremo a
extremo de forma permanente.
