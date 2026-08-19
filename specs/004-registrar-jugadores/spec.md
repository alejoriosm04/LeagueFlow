# Feature Specification: Registrar jugadores en un equipo

**Feature Branch**: `004-registrar-jugadores`

**Created**: 2026-08-18

**Status**: Draft

**Input**: User description: "Como organizador, quiero registrar jugadores dentro de un equipo, para llevar el registro de la plantilla." (HU03, backlog `docs/backlog/backlog.md`).

## Dependencies

Depende de `specs/001-fundacion-y-autenticacion` (auth) y
`specs/003-registrar-equipos` (debe existir un equipo). No re-decide stack ni
modelo — ver `AGENTS.md` §5.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registrar jugadores en un equipo (Priority: P1)

Como organizador, quiero registrar jugadores dentro de un equipo para llevar
el registro de la plantilla.

**Why this priority**: La plantilla es requisito para las estadísticas
individuales y para el registro de goles por jugador (specs 009 y 010).

**Independent Test**: Sobre un equipo existente, registrar tres jugadores y
verificar que la plantilla del equipo los lista.

**Acceptance Scenarios**:

1. **Given** un equipo existente, **When** el organizador registra un jugador
   con nombre válido, **Then** el jugador queda asociado a ese equipo y
   aparece en su plantilla.
2. **Given** un equipo donde ya existe un jugador con dorsal 10, **When** el
   organizador registra otro jugador con dorsal 10 en el mismo equipo,
   **Then** el sistema rechaza el registro por dorsal duplicado.
3. **Given** un jugador registrado en el equipo A, **When** se consulta la
   plantilla del equipo B de la misma liga, **Then** ese jugador no aparece.
4. **Given** un visitante sin sesión o un usuario con rol operador, **When**
   intenta registrar un jugador, **Then** el sistema rechaza la operación.

---

### Edge Cases

- ¿Qué ocurre si se elimina un jugador que tiene goles registrados o aparece
  en alineaciones ya guardadas?
- ¿Qué pasa si un jugador cambia de equipo a mitad de temporada?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El organizador MUST poder registrar un jugador dentro de un
  equipo con nombre obligatorio y, opcionalmente, dorsal y posición.
- **FR-002**: Cada jugador MUST pertenecer exactamente a un equipo.
- **FR-003**: El sistema MUST rechazar dos jugadores con el mismo dorsal
  dentro del mismo equipo cuando el dorsal esté informado.
- **FR-004**: Registrar un jugador MUST requerir sesión con rol organizador.
- **FR-005**: Un jugador con goles, alineaciones o eventos asociados MUST NOT
  eliminarse; se marca como inactivo.

### Key Entities

- **Player (Jugador)**: integrante de la plantilla de un equipo. Atributos:
  nombre, dorsal, posición, estado (activo/inactivo). Pertenece a un equipo
  (`specs/003-registrar-equipos`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un organizador registra una plantilla de 20 jugadores en menos
  de 10 minutos.
- **SC-002**: 100% de los intentos de registrar un dorsal duplicado dentro del
  mismo equipo son rechazados.

## Assumptions

- **Jugador en un solo equipo**: un jugador pertenece a un único equipo dentro
  de una liga; el traspaso a mitad de temporada no está soportado en esta
  versión.
- **Idioma**: la interfaz está en español.
