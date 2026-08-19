# Feature Specification: Programar un partido

**Feature Branch**: `005-programar-partido`

**Created**: 2026-08-18

**Status**: Draft

**Input**: User description: "Como organizador, quiero crear y programar un partido entre dos equipos de la misma liga, para planificar el calendario. Regla: un equipo no puede jugar contra sí mismo (homeTeam != awayTeam)." (HU04, backlog `docs/backlog/backlog.md`).

## Dependencies

Depende de `specs/001-fundacion-y-autenticacion` (auth) y
`specs/003-registrar-equipos` (necesita dos equipos de la misma liga; no
depende de que existan jugadores). No re-decide stack ni modelo — ver
`AGENTS.md` §5.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Programar un partido (Priority: P1)

Como organizador, quiero crear y programar un partido entre dos equipos de la
misma liga para planificar el calendario.

**Why this priority**: El partido es la unidad que produce resultados; sin él
no hay clasificación ni estadísticas.

**Independent Test**: Crear un partido entre dos equipos de una liga con fecha
futura y verificar que aparece en el calendario con estado "programado".

**Acceptance Scenarios**:

1. **Given** una liga con los equipos A y B, **When** el organizador programa
   un partido A vs B con fecha y hora, **Then** el partido queda creado en
   estado programado, sin marcador.
2. **Given** una liga con el equipo A, **When** el organizador intenta
   programar el partido A vs A, **Then** el sistema rechaza la creación
   porque un equipo no puede enfrentarse a sí mismo.
3. **Given** el equipo A en la liga 1 y el equipo C en la liga 2, **When** el
   organizador intenta programar A vs C, **Then** el sistema rechaza la
   creación porque ambos equipos deben pertenecer a la misma liga que el
   partido.
4. **Given** un visitante sin sesión o un usuario con rol operador, **When**
   intenta programar un partido, **Then** el sistema rechaza la operación.

---

### Edge Cases

- ¿Qué ocurre al registrar un resultado de un partido cuya fecha programada
  aún no ha llegado? (relevante para `specs/006-registrar-resultado`)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El organizador MUST poder programar un partido indicando liga,
  equipo local, equipo visitante y fecha/hora programada; el partido MUST
  nacer en estado programado y sin marcador.
- **FR-002**: El sistema MUST rechazar un partido donde el equipo local y el
  visitante sean el mismo equipo.
- **FR-003**: El sistema MUST rechazar un partido cuyos equipos no pertenezcan
  ambos a la liga del partido.
- **FR-004**: El sistema MUST soportar los estados de partido: programado, en
  curso, finalizado y cancelado. Esta spec solo produce el estado programado;
  las demás transiciones las definen `specs/006-registrar-resultado` y
  posteriores.
- **FR-005**: El sistema MUST permitir consultar el detalle de un partido
  (equipos, estado, fecha).
- **FR-006**: Programar un partido MUST requerir sesión con rol organizador.

### Key Entities

- **Match (Partido)**: enfrentamiento entre dos equipos de la misma liga.
  Atributos definidos en esta spec: equipo local, equipo visitante, fecha/hora
  programada, estado. Los atributos de marcador y las relaciones con
  alineación/eventos se amplían en specs posteriores (006, 009, 010).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un organizador programa un partido en menos de 1 minuto.
- **SC-002**: 100% de los intentos de programar un equipo contra sí mismo o
  entre equipos de ligas distintas son rechazados.

## Assumptions

- **Estados de partido**: programado, en curso, finalizado, cancelado. Solo
  los finalizados alimentan la clasificación y las estadísticas (ver
  `specs/008-consultar-clasificacion`).
- **Idioma**: la interfaz está en español.
