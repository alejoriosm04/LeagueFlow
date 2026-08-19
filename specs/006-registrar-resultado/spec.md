# Feature Specification: Registrar y corregir el resultado de un partido

**Feature Branch**: `006-registrar-resultado`

**Created**: 2026-08-18

**Status**: Draft

**Input**: User description: "Como operador, quiero registrar el resultado de un partido (goles de cada equipo), para que se refleje en la clasificación. Reglas: homeScore >= 0, awayScore >= 0; un partido en estado FINISHED no puede modificar su resultado directamente (requiere un flujo explícito de corrección)." (HU05, backlog `docs/backlog/backlog.md`).

## Dependencies

Depende de `specs/001-fundacion-y-autenticacion` (auth — distingue operador de
organizador para el flujo de corrección) y `specs/005-programar-partido`
(necesita un partido programado). No re-decide stack ni modelo — ver
`AGENTS.md` §5.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registrar y corregir el resultado de un partido (Priority: P1)

Como operador, quiero registrar el resultado de un partido (goles de cada
equipo) para que se refleje en la clasificación, y quiero poder proponer una
corrección cuando el resultado registrado sea erróneo.

**Why this priority**: Es el evento que alimenta toda la analítica del
sistema. Sin resultados, la clasificación y las estadísticas están vacías.

**Independent Test**: Registrar el marcador de un partido programado y
verificar que el partido queda finalizado con ese marcador; después, proponer
una corrección y verificar que solo se aplica tras la aprobación del
organizador.

**Acceptance Scenarios**:

1. **Given** un partido programado, **When** el operador registra 3-1,
   **Then** el partido pasa a estado finalizado con ese marcador.
2. **Given** un partido programado, **When** el operador intenta registrar un
   marcador negativo, **Then** el sistema rechaza el registro porque los goles
   deben ser enteros mayores o iguales a cero.
3. **Given** un partido ya finalizado con marcador 3-1, **When** el operador
   intenta sobrescribir el marcador directamente, **Then** el sistema rechaza
   la operación e indica que debe crear una solicitud de corrección.
4. **Given** un partido finalizado con marcador 3-1, **When** el operador crea
   una solicitud de corrección a 2-1 con motivo, **Then** la solicitud queda
   pendiente y el partido conserva el marcador 3-1.
5. **Given** una solicitud de corrección pendiente, **When** el organizador la
   aprueba, **Then** el partido pasa a tener el marcador corregido.
6. **Given** una solicitud de corrección pendiente, **When** el organizador la
   rechaza indicando el motivo, **Then** el resultado original se mantiene
   intacto y la solicitud queda cerrada como rechazada.
7. **Given** una solicitud de corrección pendiente sobre un partido, **When**
   se intenta crear una segunda solicitud sobre el mismo partido, **Then** el
   sistema la rechaza porque solo puede haber una solicitud pendiente por
   partido.
8. **Given** una solicitud creada por un operador, **When** ese mismo usuario
   intenta aprobarla, **Then** el sistema rechaza la operación: aprobar es
   competencia del organizador.
9. **Given** un partido con correcciones aplicadas, **When** se consulta su
   historial, **Then** se ven el marcador anterior, el nuevo, el motivo, quién
   solicitó, quién decidió y las fechas.
10. **Given** un visitante sin sesión o un espectador, **When** intenta
    registrar un resultado, **Then** el sistema rechaza la operación.

---

### Edge Cases

- ¿Qué ocurre si el organizador aprueba una corrección que deja el marcador
  idéntico al actual?
- ¿Qué pasa si dos operadores registran el resultado del mismo partido al
  mismo tiempo?
- ¿Qué se muestra en la clasificación mientras hay una solicitud de corrección
  pendiente sobre un partido ya contabilizado? (ver `specs/008-consultar-clasificacion`)

## Requirements *(mandatory)*

### Functional Requirements

#### Resultados

- **FR-001**: El operador MUST poder registrar el resultado de un partido con
  goles del local y del visitante como enteros mayores o iguales a cero.
- **FR-002**: El registro del resultado MUST transicionar el partido a estado
  finalizado.
- **FR-003**: El sistema MUST rechazar cualquier modificación directa del
  marcador de un partido en estado finalizado.
- **FR-004**: Registrar un resultado MUST requerir sesión con rol operador u
  organizador.

#### Corrección de resultados

- **FR-005**: El operador MUST poder crear una solicitud de corrección sobre
  un partido finalizado, indicando el nuevo marcador propuesto y un motivo
  obligatorio.
- **FR-006**: Una solicitud de corrección MUST nacer en estado pendiente y
  MUST NOT alterar el marcador del partido mientras siga pendiente.
- **FR-007**: El organizador MUST poder aprobar o rechazar una solicitud de
  corrección pendiente.
- **FR-008**: Al aprobarse una solicitud, el sistema MUST sustituir el
  marcador del partido por el propuesto.
- **FR-009**: Al rechazarse una solicitud, el sistema MUST conservar el
  resultado original y MUST registrar el motivo del rechazo.
- **FR-010**: El sistema MUST conservar y permitir consultar el historial de
  correcciones de cada partido: marcador anterior, marcador nuevo, motivo,
  autor de la solicitud, autor de la decisión y fechas.
- **FR-011**: El sistema MUST permitir como máximo una solicitud de corrección
  pendiente por partido.
- **FR-012**: El sistema MUST impedir que el usuario que creó una solicitud de
  corrección sea quien la apruebe.

### Key Entities

- **ResultCorrectionRequest (Solicitud de corrección)**: propuesta de nuevo
  marcador para un partido finalizado. Atributos: marcador propuesto, motivo,
  estado (pendiente/aprobada/rechazada), solicitante, decisor, fechas,
  marcador anterior. Pertenece a un partido (`specs/005-programar-partido`).
  Entidad propia de esta spec.
- **Match (Partido)**: esta spec amplía la entidad definida en
  `specs/005-programar-partido` con los atributos `homeScore`, `awayScore` y
  el historial de correcciones.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un operador registra el resultado de un partido en menos de 30
  segundos desde que abre la ficha del partido.
- **SC-002**: 100% de los cambios de resultado sobre partidos finalizados
  quedan registrados con solicitante, aprobador, motivo y marcador anterior,
  sin excepción.
- **SC-003**: 100% de los intentos de modificación directa de un marcador
  finalizado son rechazados.

## Assumptions

- **Empates permitidos**: no existen prórrogas ni penaltis; un partido puede
  terminar en empate.
- **Idioma**: la interfaz está en español.
