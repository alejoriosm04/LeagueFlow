# Quickstart: Registrar y corregir el resultado

Modelo en [`data-model.md`](./data-model.md), endpoints en
[`contracts/results.openapi.yaml`](./contracts/results.openapi.yaml) y
convenciones en `../001-fundacion-y-autenticacion/contracts/conventions.md`.

## Prerrequisitos

- Specs 001 y 005 implementadas y mezcladas en `main`.
- PostgreSQL; una liga con dos equipos activos y un partido `scheduled`.
- Dos usuarios distintos: operador solicitante y organizador decisor.

## Ejecutar

```bash
cd backend && alembic upgrade head && uvicorn src.main:app --reload
cd frontend && npm run dev
```

## Escenarios de validación

1. **Registrar 3-1** (AS1): PUT de resultado con operador → `200`, partido
   `finished` y marcador persistido.
2. **Marcador inválido** (AS2): gol negativo o no entero → `400
   validation_error`; partido aún `scheduled`.
3. **Sobrescritura prohibida** (AS3): repetir PUT → `409
   result_already_recorded`; conserva 3-1.
4. **Solicitar corrección** (AS4): POST con 2-1 y motivo → `201 pending`; el
   partido todavía devuelve 3-1.
5. **Aprobar** (AS5): otro organizador decide `approved` → solicitud aprobada
   y partido 2-1.
6. **Rechazar** (AS6): decidir `rejected` con motivo → resultado intacto.
7. **Una pendiente** (AS7): dos altas concurrentes → una `201` y otra `409
   correction_pending_exists`.
8. **Separación de funciones** (AS8): solicitante decide → `409
   correction_self_decision`; operador distinto → `403`.
9. **Historial** (AS9): GET público muestra ambos marcadores, motivos,
   solicitante, decisor y fechas.
10. **Autorización** (AS10): PUT sin cookie → `401`; rol insuficiente → `403`.
11. **Corrección idéntica**: se crea y aprueba con auditoría, sin cambio
    numérico en `Match`.
12. **Decisión concurrente**: una tiene éxito; la otra recibe `409
    correction_already_decided`.
13. **Estados no programados**: registrar sobre `in_progress` o `cancelled` →
    `409 match_not_scheduled`; sobre `finished` → `409
    result_already_recorded` (FR-013).
14. **Tiempo de registro** (SC-001): desde que la ficha termina de cargar hasta
    que se confirma el `200` y se muestra `finished`, un usuario de prueba debe
    completar la captura 3-1 y el envío en menos de 30 segundos. Registrar el
    tiempo observado como evidencia manual reproducible del PR.

## Pruebas automatizadas

```bash
cd backend && pytest tests/integration/test_results.py tests/contract/test_results_contract.py -v
cd frontend && npx vitest run src/features/matches
```

Antes de cerrar la HU se ejecutan las suites completas y se registra
`docs/metricas/006-registrar-resultado.md` con datos reales.
