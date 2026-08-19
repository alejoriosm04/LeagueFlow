# Feature Specification: Registrar equipos en una liga

**Feature Branch**: `003-registrar-equipos`

**Created**: 2026-08-18

**Status**: Draft

**Input**: User description: "Como organizador, quiero registrar equipos dentro de una liga, para que puedan participar en partidos." (HU02, backlog `docs/backlog/backlog.md`).

## Dependencies

Depende de `specs/001-fundacion-y-autenticacion` (auth) y
`specs/002-crear-liga` (debe existir una liga). No re-decide stack ni modelo —
ver `AGENTS.md` §5.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registrar equipos en una liga (Priority: P1)

Como organizador, quiero registrar equipos dentro de una liga para que puedan
participar en partidos.

**Why this priority**: Sin equipos no hay partidos ni clasificación. Es el
segundo eslabón obligatorio de la cadena de valor.

**Independent Test**: Sobre una liga existente, registrar dos equipos y
verificar que ambos aparecen en la lista de equipos de esa liga y no en la de
otra liga.

**Acceptance Scenarios**:

1. **Given** una liga existente, **When** el organizador registra un equipo
   con nombre válido, **Then** el equipo queda asociado a esa liga y aparece
   en su listado.
2. **Given** una liga con el equipo "Ingeniería FC", **When** el organizador
   intenta registrar otro equipo con el mismo nombre en esa liga, **Then** el
   sistema rechaza el registro por nombre duplicado.
3. **Given** dos ligas distintas, **When** existe un equipo llamado
   "Ingeniería FC" en cada una, **Then** ambos son válidos y se mantienen
   independientes.
4. **Given** un visitante sin sesión o un usuario con rol operador, **When**
   intenta registrar un equipo, **Then** el sistema rechaza la operación.

---

### Edge Cases

- ¿Qué ocurre si se elimina un equipo que ya tiene partidos finalizados? La
  clasificación histórica no puede quedar inconsistente.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El organizador MUST poder registrar un equipo dentro de una liga
  con nombre obligatorio y, opcionalmente, escudo y colores.
- **FR-002**: El sistema MUST rechazar dos equipos con el mismo nombre dentro
  de la misma liga, y MUST permitirlos en ligas distintas.
- **FR-003**: Cada equipo MUST pertenecer exactamente a una liga.
- **FR-004**: Registrar un equipo MUST requerir sesión con rol organizador.
- **FR-005**: Un equipo con partidos, alineaciones o eventos asociados MUST NOT
  eliminarse; se marca como inactivo para preservar la integridad histórica de
  la clasificación.

### Key Entities

- **Team (Equipo)**: participante de una liga. Atributos: nombre, escudo,
  colores, estado (activo/inactivo). Pertenece a una liga (`specs/002-crear-liga`);
  contendrá jugadores (`specs/004-registrar-jugadores`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un organizador registra 8 equipos en una liga en menos de 10
  minutos.
- **SC-002**: 100% de los intentos de registrar un equipo con nombre duplicado
  en la misma liga son rechazados.

## Assumptions

- **Escudo del equipo**: se almacena como enlace externo. La plataforma no
  aloja archivos multimedia.
- **Idioma**: la interfaz está en español.
