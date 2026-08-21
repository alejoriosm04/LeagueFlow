# Feature Specification: Dashboard general de la liga

**Feature Branch**: `011-dashboard-liga`

**Created**: 2026-08-18

**Status**: Draft

**Input**: User description: "Como espectador, quiero un dashboard general con partidos recientes, próximos partidos y los líderes de la clasificación, para tener una vista rápida del estado de la liga." (HU10, backlog `docs/backlog/backlog.md`).

## Dependencies

Depende de `specs/007-consultar-calendario` y `specs/008-consultar-clasificacion`
(agrega datos ya existentes en esas vistas; no introduce cálculos nuevos). Es
de solo lectura: no requiere `specs/001-fundacion-y-autenticacion`. No
re-decide stack ni modelo — ver `AGENTS.md` §5.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Dashboard general de la liga (Priority: P2)

Como espectador, quiero un dashboard con partidos recientes, próximos
partidos y los líderes de la clasificación para tener una vista rápida del
estado de la liga.

**Why this priority**: Agrega datos que ya existen; su valor es de
usabilidad, no de capacidad nueva.

**Independent Test**: Con una liga en curso, abrir el dashboard y verificar
que los tres bloques muestran los mismos partidos/filas, en el mismo orden,
que devuelven por separado `GET /leagues/{id}/matches` y
`GET /leagues/{id}/standings` (las vistas de detalle de 007 y 008).

**Acceptance Scenarios**:

1. **Given** una liga con partidos finalizados y programados, **When** el
   espectador abre el dashboard, **Then** ve los últimos 5 resultados, los
   próximos 5 partidos y los 5 primeros de la clasificación.
2. **Given** una liga recién creada sin partidos ni equipos, **When** el
   espectador abre el dashboard, **Then** cada uno de los tres bloques
   muestra su estado vacío sin errores.
3. **Given** un resultado recién registrado, **When** el espectador recarga el
   dashboard, **Then** el nuevo resultado y la clasificación actualizada se
   reflejan.
4. **Given** cualquier visitante sin sesión, **When** abre el dashboard,
   **Then** accede sin necesidad de autenticarse.
5. **Given** una liga con equipos ya registrados pero sin ningún partido
   programado ni finalizado, **When** el espectador abre el dashboard,
   **Then** los bloques de partidos muestran su estado vacío y el bloque de
   clasificación muestra esos equipos con todos los contadores en cero (no
   vacío) — ver Assumption "Bloque de clasificación 'vacío'".

---

### Edge Cases

Ninguno específico de esta spec — hereda los de `specs/007-consultar-calendario`
y `specs/008-consultar-clasificacion`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST ofrecer un dashboard por liga con los últimos 5
  partidos finalizados (el más reciente primero), los próximos 5 partidos
  programados (el más cercano primero) y los 5 primeros de la clasificación,
  en el mismo orden en que los devuelven `specs/007-consultar-calendario` y
  `specs/008-consultar-clasificacion` respectivamente. Cuando un bloque tenga
  menos de 5 elementos disponibles, MUST mostrar todos los que haya, sin
  rellenar el resto (ver FR-002 para el caso de cero elementos).
- **FR-002**: Cada bloque del dashboard MUST mostrar un estado vacío legible
  cuando no haya datos, respondiendo siempre con éxito — nunca con un código
  de error — para distinguir "sin datos" de "algo falló".
- **FR-003**: El dashboard MUST ser accesible sin autenticación.

### Key Entities

Ninguna entidad nueva. Este dashboard agrega `Match` (`specs/005-*`,
`specs/006-*`) y `Standings` (`specs/008-*`) ya definidas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un espectador que no conoce la plataforma, estando ya en el
  dashboard de una liga, encuentra la clasificación completa de esa liga en 3
  interacciones o menos contadas desde el dashboard.
- **SC-002**: El dashboard, con sus tres bloques ya renderizados, se muestra
  completo en menos de 2 segundos para una liga de 20 equipos y 190 partidos,
  medido desde que el espectador navega a la ruta del dashboard hasta que los
  tres bloques terminan de mostrarse.

## Assumptions

- **Idioma**: la interfaz está en español.
- **Bloque de clasificación "vacío"**: hereda la Assumption de
  `specs/008-consultar-clasificacion` ("Equipos que aparecen en la tabla"):
  un equipo activo sin partidos jugados aparece con todos los contadores en
  cero, no desaparece de la tabla. Por eso el bloque de clasificación llega
  vacío únicamente cuando la liga no tiene ningún equipo — no simplemente
  cuando le faltan partidos. Una liga que ya tiene equipos registrados pero
  aún no tiene partidos (AS5) —el caso más común, dado el orden natural
  crear liga → registrar equipos → programar partidos— muestra los bloques
  de partidos vacíos junto con una clasificación no vacía, con todos los
  equipos en cero. Solo una liga sin equipos NI partidos (AS2) llega a los
  tres bloques realmente vacíos.
- **Usuario autenticado**: un usuario con sesión (organizador u operador) que
  abre el dashboard ve exactamente la misma vista pública descrita en esta
  spec — esta HU no agrega ninguna variante, control o dato adicional para
  roles con sesión.
