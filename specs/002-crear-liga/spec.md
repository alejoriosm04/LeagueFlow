# Feature Specification: Crear una liga

**Feature Branch**: `002-crear-liga`

**Created**: 2026-08-18

**Status**: Draft

**Input**: User description: "Como organizador, quiero crear una liga, para tener un contenedor donde registrar equipos, jugadores y partidos." (HU01, backlog `docs/backlog/backlog.md`).

## Dependencies

Depende de `specs/001-fundacion-y-autenticacion` (debe estar mezclada a `main`
antes de planificar esta spec): usa su modelo de dominio y requiere sesión de
organizador para escribir. No re-decide stack ni modelo — ver `AGENTS.md` §5.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Crear una liga (Priority: P1)

Como organizador, quiero crear una liga para tener un contenedor donde
registrar equipos, jugadores y partidos.

**Why this priority**: La liga es la raíz del modelo de dominio. Sin ella no
existe contexto para ninguna otra entidad, así que ninguna otra HU puede
entregarse antes.

**Independent Test**: Crear una liga con nombre y temporada, y verificar que
aparece en el listado de ligas y que se puede abrir su ficha vacía.

**Acceptance Scenarios**:

1. **Given** que no existe ninguna liga, **When** el organizador crea una liga
   con nombre y temporada válidos, **Then** la liga queda registrada y visible
   en el listado.
2. **Given** que ya existe una liga con el nombre "Interfacultades 2026",
   **When** el organizador intenta crear otra con el mismo nombre y temporada,
   **Then** el sistema rechaza la creación e informa que el nombre ya está en
   uso.
3. **Given** el formulario de creación, **When** el organizador envía el
   nombre vacío, **Then** el sistema rechaza la creación e indica qué campo
   falta.
4. **Given** un visitante sin sesión o un usuario con rol operador, **When**
   intenta crear una liga, **Then** el sistema rechaza la operación (ver
   `specs/001-fundacion-y-autenticacion`).

---

### Edge Cases

- ¿Qué ve un espectador al abrir una liga sin equipos ni partidos?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST permitir al organizador crear una liga con
  nombre y temporada obligatorios, y descripción opcional.
- **FR-002**: El sistema MUST rechazar la creación de una liga cuyo nombre y
  temporada coincidan con los de una liga existente.
- **FR-003**: El sistema MUST permitir listar las ligas y consultar el detalle
  de una liga.
- **FR-004**: El sistema MUST soportar la coexistencia de varias ligas
  independientes, sin que los datos de una afecten a otra.
- **FR-005**: Crear una liga MUST requerir sesión con rol organizador (ver
  `specs/001-fundacion-y-autenticacion`).

### Key Entities

- **League (Liga)**: contenedor raíz de una competición. Atributos: nombre,
  temporada, descripción. Contiene equipos y partidos. Entidad propia de esta
  spec.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un organizador que usa la plataforma por primera vez crea una
  liga en menos de 2 minutos, sin ayuda externa.
- **SC-002**: 100% de los intentos de crear una liga duplicada (mismo nombre y
  temporada) son rechazados con un mensaje que identifica el conflicto.

## Assumptions

- **Fase única**: la liga es una fase regular todos-contra-todos. No hay
  grupos, playoffs, eliminatorias ni ascensos/descensos.
- **Idioma**: la interfaz está en español.
