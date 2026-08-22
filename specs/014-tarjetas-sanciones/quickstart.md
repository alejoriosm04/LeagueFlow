# Quickstart: Tarjetas y sanciones disciplinarias

Contrato: [`contracts/cards-sanctions.openapi.yaml`](./contracts/cards-sanctions.openapi.yaml).
Modelo y reglas: [`data-model.md`](./data-model.md).

## Prerrequisitos

- `specs/009-registrar-goles` y `specs/010-alineaciones-estadisticas` en `main`
  (eventos + alineaciones).
- Base local levantada y migrada, incluida la migración del CHECK de esta HU:

```bash
cd backend && uv run alembic upgrade head
```

- Una liga con dos equipos, jugadores, y un partido **en curso o finalizado**.
- Registrar tarjetas exige sesión de operador u organizador; la ficha
  disciplinaria no exige sesión.

## Ejecutar

```bash
cd backend && uv run uvicorn src.main:app --reload
```

```bash
cd frontend && npm run dev
```

## Escenarios de validación

1. **Amarilla (US1 / AS1)**: como operador, en un partido en curso, registrar
   `YELLOW_CARD` a un jugador participante. `201` con `type: YELLOW_CARD` y
   `team_id` derivado del jugador.
2. **Roja (US1 / AS2)**: registrar `RED_CARD` al mismo patrón. `201`.
3. **Partido no jugable (US1 / AS3, FR-002)**: intentar tarjeta en partido
   `scheduled` o `cancelled` → `409 match_not_playable`.
4. **Alineación (US1 / AS4–AS5, FR-003)**: con alineación registrada, tarjeta a
   jugador fuera de ella → `409 player_not_in_lineup`. Sin alineación, tarjeta
   a jugador de uno de los dos equipos → `201`.
5. **Jugador ajeno (US1 / AS6, FR-004)**: jugador de otro equipo/liga →
   `409 player_not_in_match`.
6. **Varias en el mismo partido (FR-005)**: dos amarillas al mismo jugador en
   el mismo partido → ambos `201`. En la ficha, `yellow_cards: 2` y
   `suspended: false` (mismo `match_id`).
7. **Suspensión por roja (US2 / AS1)**: tras una `RED_CARD`,
   `GET /players/{id}/discipline` → `suspended: true`, `red_cards >= 1`.
8. **Suspensión por acumulación (US2 / AS2)**: una amarilla en el partido A y
   otra en el partido B → `suspended: true`. Una sola amarilla →
   `suspended: false` (US2 / AS3).
9. **Ficha pública (US3 / FR-008)**: sin cookie, `GET /players/{id}/discipline`
   → `200` con conteos. Jugador sin tarjetas → ceros y `suspended: false`.
10. **Jugador inexistente**: `404 player_not_found` con envelope compartido.
11. **Listado de eventos**: `GET /matches/{id}/events` incluye tarjetas;
    `consistency` solo refleja goles.

## Verificación de SC-001 / SC-002

- SC-001: cronometra registrar una tarjeta desde la ficha del partido (meta:
  ≤ 2 interacciones). No inventes el número.
- SC-002: tras el `POST` que dispara la suspensión, el siguiente `GET` de
  ficha debe mostrar `suspended: true` sin paso manual de “recalcular”.

## Pruebas previstas

```bash
cd backend && uv run pytest \
  tests/unit/test_card_rules.py \
  tests/unit/test_sanction_rules.py \
  tests/contract/test_cards_sanctions_contract.py \
  tests/integration/test_cards_sanctions.py -v
```

```bash
cd frontend && npm run test -- src/features/events src/features/sanctions
```

Antes de cerrar: suites completas, lint, build, auditorías, `alembic check`
(revisar falso positivo de índices funcionales), y métricas en
`docs/metricas/014-tarjetas-sanciones.md`.
