# Implementation Plan: Registrar y corregir el resultado de un partido

**Branch**: `006-registrar-resultado` | **Date**: 2026-08-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/006-registrar-resultado/spec.md`

**Hereda de `specs/001-fundacion-y-autenticacion`** (`AGENTS.md` §5): stack,
modelo de dominio y convenciones de API. Este plan no re-decide esos aspectos.
Requiere que `001` y `005-programar-partido` estén mezcladas en `main` antes de
implementar.

## Summary

Permitir a operador u organizador finalizar un partido programado registrando
un marcador no negativo. Un resultado finalizado queda inmutable por la ruta
directa: cualquier cambio posterior se modela como `ResultCorrectionRequest`,
queda pendiente sin alterar el partido y solo se aplica mediante una decisión
de otro organizador. La historia completa es consultable y cada transición se
protege tanto en servicio como con transacciones y restricciones PostgreSQL.

## Technical Context

Todo el stack se hereda de
[`specs/001-fundacion-y-autenticacion/plan.md`](../001-fundacion-y-autenticacion/plan.md).

**Deltas propios de esta spec**:

- **Storage**: añade checks de coherencia/no negatividad a
  `matches.home_score`/`away_score`, creados en 005, y crea
  `result_correction_requests`, sus FKs y un índice único parcial para una sola
  solicitud `pending` por partido.
- **Primary Dependencies**: reutiliza FastAPI, Pydantic v2, SQLAlchemy 2.0 async
  y Alembic; no incorpora dependencias nuevas.
- **Testing**: pytest para transiciones, autorización, auditoría y carreras;
  Vitest/React Testing Library para formularios y visibilidad por rol.
- **Performance Goals**: completar el registro desde la ficha en menos de 30
  segundos (SC-001); el backend no exige procesamiento asíncrono ni recálculo
  materializado.
- **Constraints**: goles enteros `>= 0`; solo `scheduled` admite resultado
  inicial; `finished` no admite escritura directa; una sola corrección pendiente
  por partido; decisión atómica por un organizador distinto del solicitante.
- **Scale/Scope**: volumen heredado de 001 (hasta 10 ligas, 20 equipos y ~190
  partidos por liga); historial paginado por partido.

Sin `NEEDS CLARIFICATION`: las decisiones de borde están resueltas en
[`research.md`](./research.md).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio / regla | Estado | Cómo se cumple |
|---|---|---|
| I. La Especificación Manda | PASS | Las escrituras, consulta de historial y estados trazan a FR-001–FR-013; las decisiones de borde no añaden capacidades ajenas |
| II. Toda Regla de Negocio se Prueba | PASS | Se planifican pruebas de marcador, transición, roles, inmutabilidad, unicidad pendiente, separación solicitante/decisor y concurrencia |
| III. Contratos de API Explícitos | PASS | `contracts/results.openapi.yaml` extiende el contrato de partidos de 005 y reutiliza las convenciones de 001 |
| IV. No Romper lo que ya Funciona | PASS | Se amplía el módulo `matches`; las rutas de programación/consulta existentes conservan forma y semántica |
| V. Migraciones Versionadas | PASS | La tabla, el índice parcial y los checks nuevos de `matches` entran mediante Alembic; se eliminarán recreaciones espurias de índices funcionales previos |
| VI. Cero Secretos en el Repositorio | PASS | No se introduce configuración ni credencial nueva |
| VII. Código de IA con la Misma Vara | PASS | Backend y frontend quedan sujetos al lint y las suites existentes |
| VIII. Entregabilidad Independiente por Dominio | PASS | Todo reside en `matches`; no accede a modelos internos de `statistics` |
| Arquitectura: monolito modular | PASS | Se extiende el backend y frontend existentes, sin servicio adicional |
| Regla de Derivación de Estadísticas | PASS | Solo cambia el `Match` fuente; no persiste ni edita Standings |
| Estándares de Seguridad Obligatorios | PASS | Pydantic valida, SQLAlchemy parametriza, auth aplica roles y los errores usan el envelope compartido |

Sin violaciones. **Complexity Tracking no aplica.**

*Re-check post Phase 1*: el modelo, contrato y quickstart mantienen el marcador
del partido como única fuente persistida para la futura clasificación; la
solicitud pendiente es solo auditoría/propuesta y nunca una tabla de
estadísticas. No hay rutas de edición directa para un `Match` finalizado.
**PASS confirmado.**

## Project Structure

### Documentation (this feature)

```text
specs/006-registrar-resultado/
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── results.openapi.yaml
├── quickstart.md
└── tasks.md                 # lo generará /speckit-tasks
```

### Source Code (repository root)

```text
backend/
├── src/matches/
│   ├── models.py            # amplía Match + ResultCorrectionRequest
│   ├── schemas.py           # payloads y respuestas de resultado/corrección
│   ├── service.py           # transiciones y decisiones transaccionales
│   └── router.py            # endpoints de results.openapi.yaml
├── alembic/versions/        # migración incremental de correcciones
└── tests/
    ├── contract/test_results_contract.py
    └── integration/test_results.py

frontend/
└── src/features/matches/
    ├── MatchDetailPage.tsx
    ├── ResultForm.tsx
    ├── CorrectionRequestForm.tsx
    ├── CorrectionDecisionForm.tsx
    ├── api.ts
    └── __tests__/
```

**Structure Decision**: se conserva la aplicación web y el monolito modular de
001. La HU amplía `matches` creado en 005; no crea un módulo de estadísticas
ni carpetas de primer nivel.

## Complexity Tracking

*Sin violaciones que justificar — tabla vacía a propósito.*
