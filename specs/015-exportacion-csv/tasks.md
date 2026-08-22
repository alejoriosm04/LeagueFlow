# Tasks: Exportacion de clasificacion y calendario a CSV

**Input**: Design documents from `/specs/015-exportacion-csv/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/exports.openapi.yaml`, `quickstart.md`

**Tests**: obligatorios por los acceptance scenarios, FR-003–FR-007 y los
Principios II y IV. Cada grupo de pruebas se escribe primero y se confirma que
falla por la funcionalidad ausente antes de implementar.

**Organization**: las dos historias son P1 y se mantienen como incrementos
independientes sobre una infraestructura CSV compartida.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo porque trabaja en archivos distintos y
  no depende de una tarea incompleta del mismo grupo.
- **[US1]**: descargar la clasificacion en CSV.
- **[US2]**: descargar el calendario en CSV.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: crear la frontera transversal de exportacion sin alterar los
dominios ni agregar dependencias.

- [X] T001 Crear el paquete y el router compuesto vacio de exportaciones en `backend/src/exports/__init__.py` y `backend/src/exports/router.py`
- [X] T002 Registrar el router de exportaciones bajo `/api/v1` en `backend/src/main.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: implementar serializacion y descarga binaria compartidas por las
dos historias.

**CRITICAL**: ninguna historia comienza hasta completar esta fase.

- [X] T003 [P] Escribir primero pruebas fallidas para BOM UTF-8, CRLF, quoting de comas/comillas/saltos, metadatos, vacios, neutralizacion de formulas y filename seguro en `backend/tests/unit/test_csv_serializer.py`
- [X] T004 Implementar `CsvDocument`, reloj inyectable, filename seguro y serializacion con `csv.writer` para satisfacer T003 en `backend/src/exports/csv_serializer.py`
- [X] T005 [P] Escribir primero pruebas fallidas del cliente binario para conservar bytes, `Content-Disposition` y errores JSON en `frontend/src/services/__tests__/apiClient.test.ts`
- [X] T006 Implementar descarga de `Blob` con acceso a headers y propagacion del envelope de error en `frontend/src/services/apiClient.ts`

**Checkpoint**: infraestructura CSV y descarga reutilizable listas; US1 y US2
pueden desarrollarse sin duplicar transformacion ni manejo HTTP.

---

## Phase 3: User Story 1 - Descargar la clasificacion en CSV (Priority: P1) MVP

**Goal**: permitir que cualquier visitante descargue la misma clasificacion,
columnas y orden de 008, con liga y fecha de generacion.

**Independent Test**: desde el detalle de liga, iniciar en <=2 clics/toques la
descarga de una liga con resultados y comparar las diez columnas, filas y orden
contra `GET /standings`; comprobar equipos en cero, liga sin equipos, 404,
anonimato, filename y apertura UTF-8.

### Tests for User Story 1

> Escribir y ejecutar estas pruebas antes de la implementacion; deben fallar
> exclusivamente porque la exportacion aun no existe.

- [X] T007 [P] [US1] Escribir prueba de contrato para GET publico, `format=csv`, headers, media type, 400 y 404 de `/standings/export` en `backend/tests/contract/test_exports_contract.py`
- [X] T008 [P] [US1] Escribir prueba de integracion que compare cada fila/columna/orden con `StandingsService`, cubra equipos en cero, liga vacia, caracteres especiales y acceso anonimo en `backend/tests/integration/test_exports.py`
- [X] T009 [P] [US1] Escribir prueba de interfaz desde el detalle de liga para descarga en <=2 clics/toques, acceso anonimo y presentacion de error en `frontend/src/features/exports/__tests__/exports.test.tsx`

### Implementation for User Story 1

- [X] T010 [US1] Implementar orquestacion de liga + `StandingsService.obtener_clasificacion` y mapeo exacto de columnas sin recalculo en `backend/src/exports/service.py`
- [X] T011 [US1] Implementar GET publico `/leagues/{leagueId}/standings/export`, validacion exclusiva de CSV y respuesta attachment en `backend/src/exports/router.py`
- [X] T012 [US1] Implementar `exportsApi.descargarClasificacion` usando el cliente binario y filename del servidor en `frontend/src/features/exports/api.ts`
- [X] T013 [US1] Incorporar la accion publica `Descargar CSV`, estados accesibles y manejo de error en `frontend/src/features/standings/StandingsPage.tsx`

**Checkpoint**: US1 funciona y se prueba de extremo a extremo sin implementar
la exportacion del calendario.

---

## Phase 4: User Story 2 - Descargar el calendario en CSV (Priority: P1)

**Goal**: permitir que cualquier visitante descargue todos los partidos
programados y jugados con equipos, fecha, estado y marcador.

**Independent Test**: desde el detalle de liga, iniciar en <=2 clics/toques la
descarga de partidos `scheduled` y `finished`, comparar filas/orden contra 007
y comprobar mas de 100 filas, liga sin partidos, 404, anonimato y caracteres
especiales.

### Tests for User Story 2

> Escribir y ejecutar estas pruebas antes de la implementacion; deben fallar
> exclusivamente porque el segundo recurso aun no existe.

- [X] T014 [P] [US2] Extender pruebas de contrato con GET publico, formato, headers, media type, 400 y 404 de `/matches/export` en `backend/tests/contract/test_exports_contract.py`
- [X] T015 [P] [US2] Extender integracion con programados ascendentes, jugados descendentes, marcadores, vacio, caracteres especiales y paginacion completa superior a 100 filas en `backend/tests/integration/test_exports.py`
- [X] T016 [P] [US2] Extender la prueba de interfaz desde el detalle de liga con descarga anonima del calendario en <=2 clics/toques y manejo de error en `frontend/src/features/exports/__tests__/exports.test.tsx`

### Implementation for User Story 2

- [X] T017 [US2] Implementar orquestacion de `MatchService`/`TeamService`, recorrido de todas las paginas `scheduled` y `finished` y mapeo sin alterar orden en `backend/src/exports/service.py`
- [X] T018 [US2] Implementar GET publico `/leagues/{leagueId}/matches/export`, validacion exclusiva de CSV y respuesta attachment en `backend/src/exports/router.py`
- [X] T019 [US2] Implementar `exportsApi.descargarCalendario` usando el cliente binario y filename del servidor en `frontend/src/features/exports/api.ts`
- [X] T020 [US2] Incorporar la accion publica `Descargar CSV`, estados accesibles y manejo de error en `frontend/src/features/matches/MatchesPage.tsx`

**Checkpoint**: ambas historias funcionan de forma independiente y comparten
solo la infraestructura transversal prevista.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: validar contrato, seguridad, regresiones y trazabilidad de cierre.

- [ ] T021 Ejecutar todos los escenarios, incluida la matriz de archivo con datos/vacio/caracteres especiales en LibreOffice Calc 24.2+ y Excel para Microsoft 365 de escritorio, y registrar resultados reproducibles en `specs/015-exportacion-csv/quickstart.md`
- [ ] T022 Ejecutar suites completas, ruff, ESLint, build y auditorias sin omitir ni debilitar pruebas, siguiendo `.github/workflows/ci.yml`
- [X] T023 Copiar la plantilla y registrar tareas, tests, ciclos y reprocesos reales sin inventar tiempo ni tokens en `docs/metricas/015-exportacion-csv.md`

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 Setup
    -> Phase 2 Foundation
         -> Phase 3 US1 (MVP)
         -> Phase 4 US2
US1 + US2 -> Phase 5 Polish
```

- **Setup** no tiene dependencias.
- **Foundation** depende de Setup y bloquea ambas historias.
- **US1** y **US2** dependen de Foundation. Pueden desarrollarse en paralelo
  por personas distintas si coordinan los archivos compartidos; la secuencia
  recomendada para una persona es US1 y luego US2.
- **Polish** depende de ambas historias.

### User Story Dependencies

- **US1 (P1/MVP)**: no depende de US2; usa solo Foundation y 008.
- **US2 (P1)**: no depende funcionalmente de US1; usa solo Foundation y 007.
- Los cambios compartidos en `service.py`, `router.py`, `api.ts` y sus archivos
  de prueba deben integrarse sin sobrescribir la historia ya completada.

### Within Each User Story

- Tests T007–T009 antes de T010–T013; tests T014–T016 antes de T017–T020.
- Servicio antes de endpoint; cliente API antes de accion de interfaz.
- Confirmar pruebas de la historia en verde en cada checkpoint.

### Parallel Opportunities

- T003 y T005 pueden escribirse en paralelo; T004 sigue a T003 y T006 a T005.
- T007, T008 y T009 pueden escribirse en paralelo.
- T014, T015 y T016 pueden escribirse en paralelo.
- Tras Foundation, US1 y US2 pueden avanzar en paralelo con coordinacion de
  archivos compartidos.

---

## Parallel Example: User Story 1

```text
Task T007: contrato backend en backend/tests/contract/test_exports_contract.py
Task T008: integracion backend en backend/tests/integration/test_exports.py
Task T009: interfaz frontend en frontend/src/features/exports/__tests__/exports.test.tsx
```

## Parallel Example: User Story 2

```text
Task T014: contrato del calendario en backend/tests/contract/test_exports_contract.py
Task T015: integracion/paginacion en backend/tests/integration/test_exports.py
Task T016: interfaz del calendario en frontend/src/features/exports/__tests__/exports.test.tsx
```

---

## Implementation Strategy

### MVP First (US1)

1. Completar Setup y Foundation.
2. Escribir T007–T009 y confirmar rojo.
3. Implementar T010–T013 y confirmar verde.
4. Detenerse y validar US1 de forma independiente con `quickstart.md`.

### Incremental Delivery

1. Foundation compartida lista.
2. US1: clasificacion descargable y demostrable como MVP.
3. US2: calendario descargable sin modificar el comportamiento de US1.
4. Polish: regresion completa, validacion manual y metricas.

## Notes

- `[P]` solo aparece cuando no hay dependencia ni conflicto inmediato.
- No se crean modelos ORM, dependencias externas ni migraciones.
- No se calcula standings ni se consulta SQL desde `exports`.
- Cada tarea de historia incluye `[US1]` o `[US2]` y una ruta exacta.
- Commits intermedios pueden agrupar una prueba y su implementacion; el PR debe
  usar el formato definido para la HU 015.
