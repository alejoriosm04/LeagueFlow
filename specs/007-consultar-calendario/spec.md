# Feature Specification: Consultar el calendario y los resultados

**Feature Branch**: `007-consultar-calendario`

**Created**: 2026-08-18

**Status**: Draft

**Input**: User description: "Como espectador, quiero consultar los partidos (jugados y próximos) de una liga, para saber el calendario y los resultados." (HU06, backlog `docs/backlog/backlog.md`).

## Dependencies

Depende de `specs/005-programar-partido` y `specs/006-registrar-resultado`
(consulta lo que esas specs producen). Es de solo lectura: no requiere
`specs/001-fundacion-y-autenticacion` porque no escribe. No re-decide stack ni
modelo — ver `AGENTS.md` §5.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar el calendario y los resultados (Priority: P1)

Como espectador, quiero consultar los partidos jugados y próximos de una liga
para saber el calendario y los resultados.

**Why this priority**: Es la vista pública mínima que da valor a los
espectadores y cierra el ciclo "registrar → consultar".

**Independent Test**: Con una liga que tiene partidos finalizados y
programados, consultar la vista de partidos y verificar que ambos grupos se
muestran correctamente ordenados.

**Acceptance Scenarios**:

1. **Given** una liga con partidos finalizados y programados, **When** el
   espectador consulta los partidos, **Then** ve los próximos ordenados por
   fecha ascendente y los jugados con su marcador, ordenados por fecha
   descendente.
2. **Given** una liga sin partidos, **When** el espectador consulta los
   partidos, **Then** ve un mensaje de estado vacío en vez de un error.
3. **Given** una liga con partidos, **When** el espectador filtra por estado,
   **Then** solo se muestran los partidos de ese estado.
4. **Given** cualquier visitante sin sesión, **When** consulta los partidos,
   **Then** accede sin necesidad de autenticarse.

---

### Edge Cases

- ¿Qué ve un espectador al abrir una liga sin equipos ni partidos?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El espectador MUST poder consultar los partidos de una liga
  separados entre próximos (orden ascendente por fecha) y jugados (orden
  descendente por fecha).
- **FR-002**: El sistema MUST permitir filtrar los partidos de una liga por
  estado.
- **FR-003**: Esta consulta MUST ser accesible sin autenticación.

### Key Entities

Ninguna entidad nueva. Esta spec solo consulta `Match` (definida en
`specs/005-programar-partido` y ampliada en `specs/006-registrar-resultado`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: La vista de calendario se muestra completa en menos de 2
  segundos para una liga de 20 equipos y 190 partidos.
- **SC-002**: Un espectador identifica el próximo partido de un equipo en 2
  interacciones o menos.

## Assumptions

- **Idioma**: la interfaz está en español.
- **Semántica de grupos**: “próximos” corresponde a `scheduled` y “jugados” a
  `finished`. `in_progress` y `cancelled` aparecen únicamente bajo su filtro.
- **Estados filtrables**: el filtro admite los cuatro estados del modelo:
  `scheduled`, `in_progress`, `finished` y `cancelled`.
- **Volumen completo**: se conserva la paginación del API y la interfaz recorre
  las páginas necesarias para mostrar los 190 partidos de SC-001.
