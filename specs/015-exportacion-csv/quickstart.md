# Quickstart: Exportacion de clasificacion y calendario a CSV

Contrato: [`contracts/exports.openapi.yaml`](./contracts/exports.openapi.yaml).
Columnas: [`data-model.md`](./data-model.md).

## Prerrequisitos y ejecucion

- Specs 007/008 mezcladas, PostgreSQL en `head`, liga con equipos y partidos.
- Ninguna descarga requiere sesion.

```bash
cd backend && uv run alembic upgrade head && uv run uvicorn src.main:app --reload
cd frontend && npm run dev
```

## Validacion

1. Sin sesion y desde el detalle de liga, iniciar cada descarga en <=2 clics o
   toques, contando navegacion y activacion de descarga; no hay login.
2. Comparar columnas, filas y orden de clasificacion; incluye liga/fecha.
3. Sin resultados, cada equipo aparece en cero; sin equipos, solo encabezados.
4. Calendario contiene programados y jugados con equipos, fecha, estado/marcador.
5. Sin partidos: metadatos/encabezados, sin filas ni error.
6. Liga inexistente: `404 league_not_found`; `?format=pdf`: `400 validation_error`.
7. Abrir en LibreOffice Calc 24.2+ y Microsoft Excel para Microsoft 365 de
   escritorio los casos con datos, vacio y nombres con coma, comillas, tildes,
   salto o `=`; ninguno se corrompe ni ejecuta formulas.
8. Verificar Content-Type, attachment, `.csv`, fecha y BOM UTF-8.

```bash
curl -OJ "http://localhost:8000/api/v1/leagues/$LIGA/standings/export?format=csv"
curl -OJ "http://localhost:8000/api/v1/leagues/$LIGA/matches/export?format=csv"
```

## Pruebas previstas

```bash
cd backend && uv run pytest tests/unit/test_csv_serializer.py tests/contract/test_exports_contract.py tests/integration/test_exports.py -v
cd frontend && npm run test -- src/features/exports/__tests__/exports.test.tsx
```

Antes de cerrar: suites completas, lint, build, auditorias y
`docs/metricas/015-exportacion-csv.md` con datos reales.
