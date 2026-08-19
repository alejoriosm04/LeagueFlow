# Feature Specification: Registrar goles por jugador

**Feature Branch**: `009-registrar-goles`

**Created**: 2026-08-18

**Status**: Draft

**Input**: User description: "Como operador, quiero registrar los goles anotados por jugadores específicos dentro de un partido (como MatchEvent de tipo GOAL), para poder calcular goleadores." (HU08, backlog `docs/backlog/backlog.md`).

## Dependencies

Depende de `specs/001-fundacion-y-autenticacion` (auth), `specs/004-registrar-jugadores`
(jugadores existentes) y `specs/006-registrar-resultado` (partido con
marcador). Coordina con `specs/010-alineaciones-estadisticas`: si un partido
tiene alineación registrada, un gol solo puede atribuirse a un jugador de esa
alineación (FR-003 de esta spec). No re-decide stack ni modelo — ver
`AGENTS.md` §5.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registrar goles por jugador (Priority: P2)

Como operador, quiero registrar los goles anotados por jugadores específicos
dentro de un partido para poder calcular goleadores.

**Why this priority**: Añade granularidad analítica sobre lo ya construido,
pero la liga funciona sin ella: la clasificación solo necesita el marcador.

**Independent Test**: Sobre un partido finalizado, registrar dos goles
atribuidos a jugadores concretos y verificar que quedan listados como eventos
del partido.

**Acceptance Scenarios**:

1. **Given** un partido entre los equipos A y B, **When** el operador registra
   un gol del jugador P (plantilla de A) en el minuto 23, **Then** el evento
   queda asociado al partido, al jugador y a su equipo.
2. **Given** un partido entre A y B, **When** el operador intenta registrar un
   gol de un jugador que no pertenece ni a A ni a B, **Then** el sistema
   rechaza el registro.
3. **Given** un partido con alineación registrada, **When** el operador
   intenta atribuir un gol a un jugador que no aparece en ella, **Then** el
   sistema rechaza el registro.
4. **Given** un partido con marcador 3-1, **When** los goles atribuidos a
   jugadores no suman ese marcador, **Then** el sistema muestra una
   advertencia de inconsistencia sin bloquear el registro.
5. **Given** un visitante sin sesión o un espectador, **When** intenta
   registrar un gol, **Then** el sistema rechaza la operación.

---

### Edge Cases

- ¿Qué ocurre si se registran más goles por jugador que los del marcador
  oficial?
- ¿Qué ocurre si un gol está atribuido a un jugador y luego una corrección de
  alineación lo excluye del partido?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El operador MUST poder registrar un gol como evento de partido,
  indicando el jugador anotador y el minuto.
- **FR-002**: El sistema MUST rechazar un evento de gol cuyo jugador no
  pertenezca a ninguno de los dos equipos del partido.
- **FR-003**: Cuando un partido tenga alineación registrada
  (`specs/010-alineaciones-estadisticas`), el sistema MUST rechazar eventos de
  gol atribuidos a jugadores que no figuren en ella.
- **FR-004**: El modelo de eventos MUST admitir tipos adicionales en el futuro
  (por ejemplo tarjeta amarilla, tarjeta roja, sustitución) sin rediseñar el
  modelo; en esta versión solo se implementa el tipo gol.
- **FR-005**: Cuando la suma de goles atribuidos a jugadores no coincida con
  el marcador oficial del partido, el sistema MUST advertirlo sin bloquear el
  registro, y el marcador oficial MUST seguir siendo la fuente de verdad para
  la clasificación.
- **FR-006**: Registrar un gol MUST requerir sesión con rol operador u
  organizador.

### Key Entities

- **MatchEvent (Evento de partido)**: hecho ocurrido durante un partido.
  Atributos: tipo (gol en esta versión; extensible), jugador, equipo, minuto.
  Pertenece a un partido (`specs/005-programar-partido`). Entidad propia de
  esta spec.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un operador registra los goles de un partido en menos de 1
  minuto.
- **SC-002**: 100% de los intentos de atribuir un gol a un jugador ajeno a los
  dos equipos del partido son rechazados.

## Assumptions

- **Marcador oficial como fuente de verdad**: la clasificación se calcula
  desde el marcador del partido, no desde la suma de eventos de gol; los
  eventos alimentan solo las estadísticas individuales
  (`specs/010-alineaciones-estadisticas`).
- **Idioma**: la interfaz está en español.
