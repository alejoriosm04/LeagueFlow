# Feature Specification: Exportación de clasificación y calendario a CSV

**Feature Branch**: `015-exportacion-csv`

**Created**: 2026-08-21

**Status**: Draft

**Input**: User description: "Un visitante o un organizador necesita poder descargar, como archivo CSV, la tabla de posiciones de una liga y su calendario de partidos, para compartirlos o abrirlos en una hoja de cálculo. La información exportada debe ser exactamente la misma que ya se puede consultar en la aplicación — esta funcionalidad no recalcula nada, solo la empaqueta como archivo descargable. No requiere iniciar sesión, igual que las consultas de las que parte."

## Dependencies

Historia **de solo lectura y transformación**: no persiste nada, no introduce
entidades, contratos de escritura ni migraciones. No re-decide stack ni modelo
(AGENTS.md §5): su `plan.md` referencia `specs/001-fundacion-y-autenticacion/plan.md`
y `data-model.md`, y solo documenta lo que **añade**.

- **Depende de** `specs/008-consultar-clasificacion` (la tabla de posiciones) y
  `specs/007-consultar-calendario` (el calendario de partidos). Reutiliza esos
  mismos datos, sin recalcularlos.
- **No modifica** entidades ni contratos existentes: reempaqueta lo que ya
  exponen `standings` y `matches` por sus interfaces públicas de servicio.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Descargar la clasificación en CSV (Priority: P1)

Como visitante u organizador, quiero descargar la tabla de posiciones de una
liga como archivo CSV, para compartirla o abrirla en una hoja de cálculo.

**Why this priority**: Es el dato de mayor valor de distribución (la clasificación)
y la mitad del alcance de la historia.

**Independent Test**: Descargar la clasificación de una liga con partidos jugados
y verificar que el CSV contiene las mismas filas y columnas que la vista.

**Acceptance Scenarios**:

1. **Given** una liga con partidos finalizados, **When** el usuario descarga la
   clasificación, **Then** el CSV contiene las mismas filas, columnas y orden que
   la vista, e incluye el nombre de la liga y la fecha de generación.
2. **Given** una liga sin partidos finalizados, **When** el usuario descarga la
   clasificación, **Then** obtiene un CSV válido con todos los equipos en cero.
3. **Given** una liga inexistente, **When** el usuario intenta descargar, **Then**
   recibe el error de "liga no encontrada" ya definido por `specs/008`.

---

### User Story 2 - Descargar el calendario en CSV (Priority: P1)

Como visitante u organizador, quiero descargar el calendario de partidos de una
liga como archivo CSV, para compartirlo o abrirlo en una hoja de cálculo.

**Why this priority**: Es la otra mitad del alcance; la misma mecánica que la
clasificación, sobre el calendario.

**Independent Test**: Descargar el calendario de una liga con partidos y verificar
que el CSV lista los partidos con sus equipos, fecha y estado.

**Acceptance Scenarios**:

1. **Given** una liga con partidos programados y jugados, **When** el usuario
   descarga el calendario, **Then** el CSV contiene todos los partidos con sus
   equipos, fecha y estado.
2. **Given** una liga sin partidos, **When** el usuario descarga el calendario,
   **Then** obtiene un CSV con solo los encabezados, sin errores.
3. **Given** una liga inexistente, **When** el usuario intenta descargar, **Then**
   recibe el error de "liga no encontrada" ya definido por `specs/007`.

---

### Edge Cases

- ¿Qué ocurre al exportar una liga sin datos? Se devuelve un CSV con solo los
  encabezados, nunca un error.
- ¿Qué ocurre al pedir un formato distinto de CSV? Se rechaza indicando que solo
  se soporta CSV.
- ¿Qué ocurre al exportar una liga inexistente? Se responde con "liga no
  encontrada".
- ¿Qué ocurre con nombres de liga o equipos que contienen comas o caracteres
  especiales? El CSV los delimita correctamente para no romper la estructura.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Cualquier usuario, sin autenticación, MUST poder descargar la
  clasificación de una liga en formato CSV.
- **FR-002**: Cualquier usuario, sin autenticación, MUST poder descargar el
  calendario de partidos de una liga en formato CSV.
- **FR-003**: El CSV de clasificación MUST contener las mismas filas, columnas y
  orden que la vista, e incluir el nombre de la liga y la fecha de generación.
- **FR-004**: El CSV de calendario MUST contener todos los partidos de la liga
  (programados y jugados) con sus equipos, fecha y estado.
- **FR-005**: El sistema MUST devolver un CSV con solo los encabezados cuando no
  haya datos, y NUNCA un error por ausencia de datos.
- **FR-006**: El sistema MUST rechazar la solicitud de un formato distinto de CSV.
- **FR-007**: La exportación MUST empaquetar los mismos datos que ya exponen la
  clasificación y el calendario, sin recalcularlos ni alterarlos.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un usuario descarga la clasificación o el calendario en 2
  interacciones o menos.
- **SC-002**: El 100% de las filas, columnas y el orden del CSV coinciden con la
  vista de la que parten.
- **SC-003**: El 100% de las exportaciones de una liga sin datos devuelven un CSV
  con encabezados (0 errores por ausencia de datos).
- **SC-004**: Un visitante sin sesión descarga ambos archivos sin ningún paso de
  autenticación.
- **SC-005**: El 100% de los archivos descargados se abren en una hoja de cálculo
  sin corrupción, incluyendo nombres con caracteres especiales.

## Assumptions

- **Formato**: solo CSV; otros formatos quedan fuera de alcance y se rechazan.
- **Alcance del calendario**: incluye todos los partidos de la liga (programados y
  jugados), igual que la vista de calendario existente.
- **Nombre de archivo**: se genera con el nombre de la liga y la fecha de
  generación (para que el archivo descargado sea autoexplicativo).
- **Sin autenticación**: la descarga es pública, igual que las consultas de
  clasificación y calendario de las que parte.

## Out of Scope

- Exportación en PDF o en otros formatos.
- Personalización de columnas o filtros en la exportación.
- Exportación de otros datos (estadísticas de jugadores, eventos, grupos).
- Programación de exportaciones periódicas o envío por correo.
