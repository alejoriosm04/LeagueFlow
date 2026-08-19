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
que los tres bloques muestran datos coherentes con las vistas de detalle.

**Acceptance Scenarios**:

1. **Given** una liga con partidos finalizados y programados, **When** el
   espectador abre el dashboard, **Then** ve los últimos 5 resultados, los
   próximos 5 partidos y los 5 primeros de la clasificación.
2. **Given** una liga recién creada sin partidos, **When** el espectador abre
   el dashboard, **Then** cada bloque muestra su estado vacío sin errores.
3. **Given** un resultado recién registrado, **When** el espectador recarga el
   dashboard, **Then** el nuevo resultado y la clasificación actualizada se
   reflejan.
4. **Given** cualquier visitante sin sesión, **When** abre el dashboard,
   **Then** accede sin necesidad de autenticarse.

---

### Edge Cases

Ninguno específico de esta spec — hereda los de `specs/007-consultar-calendario`
y `specs/008-consultar-clasificacion`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST ofrecer un dashboard por liga con los últimos 5
  partidos finalizados, los próximos 5 partidos programados y los 5 primeros
  de la clasificación.
- **FR-002**: Cada bloque del dashboard MUST mostrar un estado vacío legible
  cuando no haya datos.
- **FR-003**: El dashboard MUST ser accesible sin autenticación.

### Key Entities

Ninguna entidad nueva. Este dashboard agrega `Match` (`specs/005-*`,
`specs/006-*`) y `Standings` (`specs/008-*`) ya definidas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un espectador que llega a la plataforma sin conocerla encuentra
  la clasificación de una liga en 3 interacciones o menos desde el dashboard.
- **SC-002**: El dashboard se muestra completo en menos de 2 segundos para una
  liga de 20 equipos y 190 partidos.

## Assumptions

- **Idioma**: la interfaz está en español.
