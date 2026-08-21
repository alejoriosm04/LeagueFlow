# Quickstart: Dashboard general de la liga

Contrato: [`contracts/dashboard.openapi.yaml`](./contracts/dashboard.openapi.yaml).

## Prerrequisitos

- Specs 007 y 008 mezcladas en `main` y PostgreSQL migrado a `head` (incluida
  la migración aditiva `ix_matches_league_status_scheduled` de esta HU).
- Una liga con partidos `scheduled` y `finished`, y al menos un equipo;
  consultar el dashboard no requiere sesión.

## Ejecutar

```bash
cd backend && uv run alembic upgrade head && uv run uvicorn src.main:app --reload
cd frontend && npm run dev
```

## Escenarios

1. Cerrar sesión y abrir el dashboard de una liga: no redirige al login
   (FR-003).
2. Liga con ≥ 6 partidos finalizados y ≥ 6 programados: el bloque de
   recientes muestra exactamente 5 (el más reciente primero) y el de próximos
   exactamente 5 (el más cercano primero) — ninguno de los dos excede 5 aunque
   existan más.
3. Liga con ≥ 6 equipos: el bloque de clasificación muestra exactamente los 5
   primeros lugares, en el mismo orden que
   `GET /leagues/{leagueId}/standings`.
4. Liga recién creada sin partidos ni equipos: los tres bloques muestran su
   estado vacío ("Aún no hay partidos jugados", "Aún no hay próximos
   partidos", "Aún no hay equipos"), sin error y con `200`.
5. Liga con equipos ya registrados pero sin ningún partido (AS5): los dos
   bloques de partidos muestran su estado vacío, y el bloque de
   clasificación **no** está vacío — muestra esos equipos con todos los
   contadores en cero.
6. Registrar un resultado y recargar el dashboard: el partido pasa de
   "próximos" a "recientes" y la clasificación del bloque se actualiza sin
   ninguna acción manual de recálculo (hereda SC-002 de 008).
7. Liga inexistente: `404 league_not_found` con el envelope compartido.
8. Desde el dashboard, llegar a la clasificación completa
   (`/leagues/{id}/standings`) en 1 interacción (enlace "Ver clasificación
   completa"); SC-001 pide 3 o menos.

## Rendimiento SC-002

Con el backend detenido, reutilizar el mismo escenario persistente que 007 y
008 ya usan para su propio SC-001/SC-003 (no se genera un escenario nuevo,
`research.md` §5):

```bash
cd backend
uv run python -m scripts.seed_admin
uv run python -m scripts.seed_calendar_performance
```

El segundo comando imprime el UUID y la ruta de la liga generada con 20
equipos y 190 partidos (mitad `finished` con marcador, mitad `scheduled`),
sin imprimir contraseñas ni cadenas de conexión. Luego, en sesión anónima y
con caché desactivada, medir desde la navegación a
`/leagues/{id}/dashboard` hasta que los tres bloques terminen de renderizar.
Registrar navegador, equipo, volumen y tiempo; debe ser menor de 2 segundos.

## Pruebas previstas

```bash
cd backend && uv run pytest tests/contract/test_dashboard_contract.py tests/integration/test_dashboard.py -v
cd frontend && npm run test -- src/features/dashboard/__tests__/dashboard.test.tsx
```

Antes de cerrar: suites completas, lint, build, auditorías y
`docs/metricas/011-dashboard-liga.md`.
