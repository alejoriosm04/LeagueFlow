# Quickstart: Consultar el calendario y los resultados

Contrato: [`contracts/calendar.openapi.yaml`](./contracts/calendar.openapi.yaml).

## Prerrequisitos

- Specs 005 y 006 mezcladas en `main` y PostgreSQL migrado a `head`.
- Una liga con partidos `scheduled` y `finished`; consultar no requiere sesión.

## Ejecutar

```bash
cd backend && uv run alembic upgrade head && uv run uvicorn src.main:app --reload
cd frontend && npm run dev
```

## Escenarios

1. Cerrar sesión y abrir “Ver partidos”: no redirige al login.
2. Dos `scheduled`: aparecen en “Próximos”, fecha más cercana primero.
3. Dos `finished`: aparecen en “Jugados”, con marcador y más reciente primero.
4. Seleccionar cada estado: solo aparecen partidos con ese estado.
5. Liga vacía: muestra estado vacío, no error.
6. Liga inexistente: `404 league_not_found` con envelope compartido.
7. GET sin `status`: conserva paginación y orden ascendente de 005.
8. SC-002: desde la liga se identifica el próximo partido en máximo dos interacciones.

## Rendimiento SC-001

Con el backend detenido, crear o reutilizar el organizador semilla y generar el
escenario persistente e idempotente:

```bash
cd backend
uv run python -m scripts.seed_admin
uv run python -m scripts.seed_calendar_performance
```

El segundo comando debe imprimir el UUID y la ruta de la liga generada con 20
equipos y 190 partidos, sin imprimir contraseñas ni cadenas de conexión. Luego,
en sesión anónima y con caché desactivada, medir desde la navegación a esa ruta
hasta que desaparezca “Cargando partidos…” y estén los 190 elementos. Registrar
navegador, equipo, volumen y tiempo; debe ser menor de 2 segundos.

## Pruebas previstas

```bash
cd backend && uv run pytest tests/contract/test_calendar_contract.py tests/integration/test_calendar.py -v
cd frontend && npm run test -- src/features/matches/__tests__/calendar.test.tsx
```

Antes de cerrar: suites completas, lint, build, auditorías y
`docs/metricas/007-consultar-calendario.md`.
