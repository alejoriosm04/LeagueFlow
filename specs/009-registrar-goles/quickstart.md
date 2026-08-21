# Quickstart: Registrar goles por jugador

Contrato: [`contracts/events.openapi.yaml`](./contracts/events.openapi.yaml).
Entidad y validaciones: [`data-model.md`](./data-model.md).

## Prerrequisitos

- `specs/004-registrar-jugadores` y `specs/006-registrar-resultado` en `main`.
- Base local levantada y migrada (`docs/flujo-sdd.md` §2.2), incluida la
  migración nueva de esta HU:

```bash
cd backend && uv run alembic upgrade head
```

- Una liga con dos equipos, jugadores en ambos y un partido **finalizado** con
  marcador. Registrar goles exige sesión de operador u organizador; consultarlos
  no exige nada.

## Ejecutar

```bash
cd backend && uv run uvicorn src.main:app --reload
```

```bash
cd frontend && npm run dev
```

## Escenarios de validación

1. **Registrar un gol (AS1)**: como operador, en un partido A vs B, registrar un
   gol del jugador P (plantilla de A) en el minuto 23. El evento queda asociado
   al partido, al jugador y —derivado— al equipo A.
2. **Jugador ajeno al partido (AS2, SC-002)**: intentar un gol de un jugador de
   una liga o equipo distintos: `409 player_not_in_match`.
3. **Alineación (AS3)**: hoy **no es verificable extremo a extremo** — las
   alineaciones las crea `specs/010-alineaciones-estadisticas`. La regla está
   implementada y cubierta por prueba unitaria con un doble del puerto
   `jugadores_alineados`; su prueba de integración corresponde a 010.
   Ver `research.md` §2 y la desviación registrada en `plan.md`.
4. **Descuadre con el marcador (AS4, FR-005)**: en un partido 3-1, registrar
   solo dos goles del local. El `POST` responde `201` igual, y
   `GET /matches/{id}/events` devuelve `consistency.matches_official: false`.
   El marcador oficial **no cambia**: compruébalo con `GET /matches/{id}`
   antes y después. Con 008 ya mezclada en `main`, comprueba también que
   `GET /leagues/{id}/standings` devuelve exactamente la misma tabla antes y
   después de registrar los goles: la clasificación se deriva del marcador,
   no de los eventos.
5. **Sin sesión (AS5, FR-006)**: `POST` sin cookie → `401 not_authenticated`.
   Con sesión de un rol sin permiso → `403 insufficient_role`.
6. **Partido no jugable**: intentar registrar un gol en un partido `scheduled` o
   `cancelled` → `409 match_not_playable`.
7. **Minuto inválido**: `minute: -1` → `400 validation_error` con `field`
   apuntando al campo.
8. **Lectura pública**: cerrar sesión y consultar los eventos: `200`, en orden
   de minuto ascendente.
9. **Partido sin eventos**: `200` con `items: []` y el bloque `consistency`
   presente.
10. **Partido inexistente**: `404 match_not_found` con el envelope compartido.

## Verificación de SC-001

SC-001 ("un operador registra los goles de un partido en menos de 1 minuto")
es una medición de experiencia, no de latencia de API: cronometra el registro
de los 4 goles de un partido 3-1 desde la ficha del partido, sin recargar entre
uno y otro. Registra el número observado; **no lo inventes**.

## Pruebas previstas

```bash
cd backend && uv run pytest tests/unit/test_goal_rules.py tests/contract/test_events_contract.py tests/integration/test_events.py -v
```

```bash
cd frontend && npm run test -- src/features/events
```

Antes de cerrar: suites completas, lint, build, auditorías, `alembic check`
(revisando que solo reporte el falso positivo conocido de los índices
funcionales) y `docs/metricas/009-registrar-goles.md`.
