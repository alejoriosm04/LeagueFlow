# Quickstart: Consultar la clasificación

Contrato: [`contracts/standings.openapi.yaml`](./contracts/standings.openapi.yaml).
Derivación y orden: [`data-model.md`](./data-model.md).

## Prerrequisitos

- `specs/006-registrar-resultado` mezclada en `main` y PostgreSQL en `head`.
- Una liga con al menos tres equipos y tres partidos `finished`. Consultar la
  clasificación no requiere sesión; registrar los resultados que la alimentan
  sí (operador u organizador).

## Ejecutar

```bash
cd backend && uv run alembic upgrade head && uv run uvicorn src.main:app --reload
```

```bash
cd frontend && npm run dev
```

## Escenarios de validación

1. **Victoria y derrota (AS1)**: registrar A 2 – 0 B y abrir “Ver clasificación”
   de la liga: A muestra 3 puntos, 1 PJ, 1 G, GF 2, GC 0, GD +2; B muestra 0
   puntos, 1 PJ, 1 P, GD −2.
2. **Empate (AS2)**: registrar C 1 – 1 D: ambos suman 1 punto y 1 E.
3. **Desempate por diferencia de goles (AS3)**: con dos equipos igualados en
   puntos, el de mayor GD aparece primero.
4. **Desempate por goles a favor (AS4)**: con puntos y GD iguales, el de más GF
   aparece primero.
5. **Solo cuentan los finalizados (AS5)**: programar un partido más y dejarlo
   `scheduled`: la tabla no cambia. Marcar un partido como `cancelled` en la
   base de pruebas: tampoco cambia (FR-007).
6. **La tabla no se edita (AS6, FR-002)**: la interfaz no ofrece ningún control
   para cambiar puntos o posición, y la API responde `405` a cualquier verbo
   que no sea `GET`:

   ```bash
   curl -i -X PUT http://localhost:8000/api/v1/leagues/$LIGA/standings
   ```

7. **Reflejo inmediato (SC-002)**: corregir un resultado por
   `PUT /matches/{id}/result` o aprobar una corrección de 006 y volver a
   consultar: la tabla ya refleja el cambio, sin ninguna acción de recálculo.
8. **Equipo sin jugar**: un equipo recién inscrito aparece con todo en cero, al
   final de la tabla.
9. **Liga sin equipos**: `200` con `items: []`; se muestra estado vacío, no
   error.
10. **Liga inexistente**: `404 league_not_found` con el envelope compartido.
11. **Anonimato (FR-008)**: cerrar sesión y abrir la clasificación: no redirige
    al login.

## Verificación manual de SC-001

Tomar los partidos `finished` de la liga de prueba, calcular la tabla a mano y
compararla fila por fila con la que devuelve el sistema, incluidos los
desempates. Deben coincidir en las once columnas y en el orden.

## Rendimiento SC-003

Reutilizar el escenario persistente de 007 (20 equipos, 190 partidos, la mitad
finalizados con marcador):

```bash
cd backend && uv run python -m scripts.seed_admin && uv run python -m scripts.seed_calendar_performance
```

Con el UUID de liga que imprime el script, en sesión anónima y con caché
desactivada, medir desde la navegación a `/leagues/<uuid>/standings` hasta que
las 20 filas estén visibles. Registrar navegador, equipo y tiempo: debe ser
menor de 2 segundos.

## Pruebas previstas

```bash
cd backend && uv run pytest tests/unit/test_standings_calculator.py tests/contract/test_standings_contract.py tests/integration/test_standings.py -v
```

```bash
cd frontend && npm run test -- src/features/standings/__tests__/standings.test.tsx
```

Antes de cerrar la HU: suites completas en verde, lint, build, auditorías de
dependencias y `docs/metricas/008-consultar-clasificacion.md` completado.
