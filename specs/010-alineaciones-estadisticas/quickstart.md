# Quickstart: Alineaciones y estadisticas de jugadores

Contrato: [`contracts/lineups-statistics.openapi.yaml`](./contracts/lineups-statistics.openapi.yaml).
Modelo y reglas: [`data-model.md`](./data-model.md).

## Prerrequisitos

- `specs/001` a `specs/009` ya integradas.
- Backend y frontend levantados localmente.
- Una liga con partidos finalizados y jugadores registrados en ambos equipos.
- Para escribir alineacion: sesion de operador u organizador.
- Para consultar estadisticas: no se requiere sesion.

## Ejecutar

```bash
cd backend && uv run alembic upgrade head && uv run uvicorn src.main:app --reload
```

```bash
cd frontend && npm run dev
```

## Escenarios de validacion

1. **Registro y modificacion de alineacion (FR-001, FR-005)**
   - `PUT /matches/{id}/lineup` con jugadores home/away validos, autenticado
     como operador.
   - Repetir `PUT` con un cambio de lista y verificar reemplazo completo.

2. **Jugador fuera de equipos del partido (FR-002)**
   - Incluir en `PUT` un jugador de un tercer equipo.
   - Esperado: `409 player_not_in_match`.

3. **Partido finalizado sin alineacion (FR-004 + edge case)**
   - Consultar `GET /matches/{id}/lineup` para un partido `finished` sin carga
     previa.
   - Esperado: `200`, `status: "missing"`, listas vacias.

4. **Coherencia alineacion-eventos al corregir (FR-003)**
   - En partido con gol registrado de jugador X, enviar correccion de alineacion
     que quite a X.
   - Esperado: `409 lineup_conflicts_with_events` y `conflicting_player_ids`.

5. **Cobertura heredada de 009 (FR-003 de 009)**
   - Con alineacion registrada, intentar `POST /matches/{id}/events` para un
     jugador que no figura en la alineacion.
   - Esperado: rechazo `409 player_not_in_lineup` en prueba de integracion E2E.

6. **Ficha individual publica (FR-010, FR-011)**
   - Sin sesion, consultar `GET /players/{playerId}/statistics`.
   - Esperado: `200` con `goals` y `matches_played` correctos, incluyendo ceros
     para jugador sin participaciones.

7. **Tabla de goleadores publica (FR-009, FR-011, SC-002)**
   - Sin sesion, consultar `GET /leagues/{leagueId}/top-scorers`.
   - Esperado: orden por `goals` DESC y bandera `is_top_scorer=true` en el/los
     maximos goleadores para identificacion inmediata en UI.

8. **Recalculo tras eliminar un gol contabilizado (FR-006, SC-001)**
   - Eliminar/anular un evento GOAL en un flujo de correccion auditado.
   - Reconsultar ficha y tabla.
   - Esperado: el gol descontado ya no aparece, porque la derivacion se calcula
     en lectura desde eventos actuales.

9. **Correccion de marcador sin tocar eventos (integracion 006/009)**
   - Aprobar correccion de resultado que cambie `home_score/away_score` sin
     modificar `match_events`.
   - Esperado: standings/cabecera de marcador cambian; goleadores no cambian.

## Verificacion manual de SC-001

Para una liga de prueba:
- Contar manualmente goles por jugador desde `match_events` de tipo `GOAL`.
- Contar manualmente partidos jugados por jugador desde `match_lineups`, solo en
  partidos `finished`.
- Comparar contra API de ficha y tabla de goleadores.
- Esperado: coincidencia total (100%).

## Pruebas previstas

```bash
cd backend && uv run pytest tests/unit/test_lineup_rules.py tests/contract/test_lineups_statistics_contract.py tests/integration/test_lineups_statistics.py -v
```

```bash
cd frontend && npm run test -- src/features/statistics/__tests__/statistics.test.tsx
```

Antes de cerrar la HU: suite completa en verde, lint/build, y metricas de la
HU completadas en `docs/metricas/010-alineaciones-estadisticas.md`.
