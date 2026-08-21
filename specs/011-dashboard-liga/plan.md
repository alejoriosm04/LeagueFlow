# Implementation Plan: Dashboard general de la liga

**Branch**: `011-dashboard-liga` | **Date**: 2026-08-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/011-dashboard-liga/spec.md`

**Nota**: esta HU no re-decide stack ni modelo de dominio — hereda ambos de
`specs/001-fundacion-y-autenticacion/plan.md` (`AGENTS.md` §5). Depende
directamente de `specs/007-consultar-calendario` y
`specs/008-consultar-clasificacion`, cuyos servicios reutiliza sin
modificarlos.

## Summary

Un único endpoint público `GET /leagues/{leagueId}/dashboard` que compone, en
una sola respuesta, los últimos 5 partidos finalizados, los próximos 5
partidos programados y los primeros 5 lugares de la clasificación de una
liga. El endpoint vive en el módulo `statistics` ya existente
(`backend/src/statistics/`), junto a `StandingsService`: un nuevo
`DashboardService` orquesta tres llamadas a interfaces de dominio ya
probadas — `MatchService.listar_partidos` (dos veces, con
`status="finished"` y `status="scheduled"`, `page_size=5`) y
`StandingsService.obtener_clasificacion` (recortada a `items[:5]`) — sin
reimplementar filtros, orden ni cálculo de puntos. No se crean entidades ni
persistencia propia: `DashboardSummary` se deriva en cada lectura, igual que
`Standings` en 008. La única adición al esquema es un índice compuesto
aditivo sobre `matches(league_id, status, scheduled_at)` que refuerza tanto a
007/008 como a este dashboard. El detalle de cada decisión está en
`research.md`; el modelo derivado en `data-model.md`; el contrato en
`contracts/dashboard.openapi.yaml`.

## Technical Context

**Language/Version**: Python 3.12 (backend) · TypeScript 5.7 + React 18
(frontend) — fijado en 001, sin cambios.

**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0 async · React,
Vite, React Router 7, React Testing Library — mismas de 007/008, sin
dependencias nuevas.

**Storage**: PostgreSQL 16; solo lectura de `matches` y `teams`, siempre a
través de `MatchService`/`TeamService`/`StandingsService` (Principio VIII).
Sin persistencia propia para `DashboardSummary`.

**Testing**: `pytest` + `httpx.AsyncClient` (contract + integration) ·
`Vitest` + React Testing Library.

**Target Platform**: backend Linux/Railway · SPA Vercel · navegador web.

**Project Type**: aplicación web con backend y frontend separados.

**Performance Goals**: dashboard completo en menos de 2 segundos para una
liga de 20 equipos y 190 partidos (SC-002); un espectador encuentra la
clasificación en 3 interacciones o menos desde el dashboard (SC-001).

**Constraints**: endpoint público, sin autenticación (FR-003); solo `GET`,
sin escritura alguna; cada bloque responde con lista vacía (nunca error)
cuando no hay datos (FR-002); reutiliza `MatchService.listar_partidos` y
`StandingsService.obtener_clasificacion` sin alterar sus firmas ni su
lógica; ninguna entidad nueva; la única migración es un índice aditivo, sin
tocar columnas ni constraints de `Match`.

**Scale/Scope**: un endpoint nuevo, un recurso agregado (3 bloques de hasta 5
elementos cada uno), reutiliza íntegramente los dominios `matches` y
`statistics` ya existentes; hasta 10 ligas simultáneas / 20 equipos / 190
partidos por liga (volumen de referencia de 001).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio / regla | Estado | Cómo se cumple |
|---|---|---|
| I. La Especificación Manda | PASS | Los tres bloques, el estado vacío y el acceso público derivan literalmente de FR-001–FR-003; nada se inventa fuera de la spec |
| II. Toda Regla de Negocio se Prueba | PASS | El dashboard no introduce reglas de negocio nuevas (no hay cálculo propio): pytest de contrato/integración verifica composición, recorte a 5 y estado vacío; Vitest verifica render de los tres bloques |
| III. Contratos de API Explícitos | PASS | `contracts/dashboard.openapi.yaml` documenta el recurso nuevo, reutilizando literalmente los schemas `Match` y `StandingsRow` ya publicados por 007/008 |
| IV. No Romper lo que ya Funciona | PASS | No se modifica ninguna firma de `MatchService` ni `StandingsService`; el índice nuevo es aditivo y no reemplaza ninguno existente; regresión completa de 007/008 antes del PR |
| V. Migraciones Versionadas | PASS | Índice `ix_matches_league_status_scheduled` vía migración Alembic nueva y reversible (`data-model.md` §Migración); no altera filas ni columnas |
| VI. Cero Secretos | PASS | No se añade configuración ni credencial; reutiliza `scripts/seed_calendar_performance.py`, que ya toma el organizador de `SEED_ADMIN_USERNAME` |
| VII. Código de IA con la misma vara | PASS | Mismos pytest, Vitest, ruff, build y auditorías que el resto del proyecto |
| VIII. Entregabilidad Independiente por Dominio | PASS | `DashboardService` vive en `statistics` y consume `MatchService`/`StandingsService` por su interfaz pública, nunca sus modelos; no crea dependencia circular (`statistics -> matches`, igual que 008) |
| Arquitectura: monolito modular | PASS | Un solo backend FastAPI, un solo frontend SPA; ningún servicio nuevo |
| Regla de Derivación de Estadísticas (NO NEGOCIABLE) | PASS | `DashboardSummary` no se persiste: se recalcula en cada `GET`, igual que `Standings`. No existe vía de escritura sobre él |
| Estándares de Seguridad Obligatorios | PASS | `leagueId` validado como UUID por FastAPI, sin SQL concatenado (reutiliza consultas ORM ya parametrizadas de 007/008), envelope de error compartido, sin stack trace al cliente |

Sin violaciones. **Complexity Tracking no aplica** (ver sección al final,
vacía a propósito).

*Re-check post Phase 1*: `data-model.md` confirma que no se introduce ninguna
entidad, campo ni tabla — solo un índice aditivo sobre `matches`, ya
justificado en el punto de Migraciones Versionadas. `contracts/dashboard.openapi.yaml`
reutiliza los schemas `Match` y `StandingsRow` en vez de redefinirlos. **PASS
confirmado, sin desviaciones.**

## Project Structure

### Documentation (this feature)

```text
specs/011-dashboard-liga/
├── spec.md
├── plan.md                          # este archivo
├── research.md                      # Phase 0
├── data-model.md                    # Phase 1
├── contracts/dashboard.openapi.yaml # Phase 1
├── quickstart.md                    # Phase 1
├── checklists/requirements.md       # ya existente
└── tasks.md                         # Phase 2 (/speckit-tasks — aún no generado)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── statistics/
│   │   ├── schemas.py   # + DashboardSummary (reusa Match de matches/schemas.py
│   │   │                #   y StandingsRow ya declarado aquí — sin redefinir campos)
│   │   ├── service.py   # + DashboardService.obtener_resumen(league_id):
│   │   │                #   compone MatchService.listar_partidos x2 + StandingsService
│   │   │                #   .obtener_clasificacion; cero SQL propio
│   │   └── router.py    # + GET /leagues/{liga_id}/dashboard (público, sin Depends de sesión)
│   └── matches/
│       └── models.py    # + Index ix_matches_league_status_scheduled en __table_args__
│                         #   (solo el índice; ninguna columna/constraint cambia)
├── alembic/versions/
│   └── <rev>_indice_matches_liga_status_fecha.py  # migración nueva y aditiva
└── tests/
    ├── contract/test_dashboard_contract.py    # valida contra dashboard.openapi.yaml
    └── integration/test_dashboard.py          # composición, recorte a 5, estado vacío, 404

frontend/src/
├── features/
│   ├── leagues/LeagueDetailPage.tsx   # + enlace "Ver dashboard"
│   └── dashboard/
│       ├── api.ts                     # cliente HTTP de GET .../dashboard
│       ├── DashboardPage.tsx          # tres bloques + enlaces a calendario/standings completos
│       └── __tests__/dashboard.test.tsx
└── routes.tsx                          # + /leagues/:id/dashboard (pública, sin ProtectedRoute)
```

**Structure Decision**: se extiende `backend/src/statistics/`, el mismo
módulo que ya aloja `StandingsService` (008) y las estadísticas de jugadores
(010), en vez de crear `backend/src/dashboard/`. El dashboard no tiene una
regla de negocio propia que justifique un dominio nuevo (Principio VIII):
es una composición de lectura sobre `matches` y `statistics`, y ese es
exactamente el rol que 001 reservó para `statistics`. En el frontend,
`features/dashboard/` sigue la partición por feature ya usada por
`standings/` y `matches/`, con una página propia porque el dashboard es una
ruta y una experiencia de usuario distintas de sus dos vistas de origen,
aunque reutilice sus datos.

## Complexity Tracking

*Sin violaciones que justificar — tabla vacía a propósito.*
