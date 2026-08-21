# Feature Specification: Registrar alineaciones y consultar estadísticas de jugadores

**Feature Branch**: `010-alineaciones-estadisticas`

**Created**: 2026-08-18

**Status**: Draft

**Input**: User description: "Como espectador, quiero consultar estadísticas de jugadores (goles anotados, partidos jugados), para conocer su desempeño individual." (HU09, backlog `docs/backlog/backlog.md`). Incluye el registro de alineaciones, añadido en la sesión de clarificación del 2026-08-18 como fuente de "partidos jugados".

## Dependencies

Depende de `specs/001-fundacion-y-autenticacion` (auth para registrar
alineación), `specs/004-registrar-jugadores` y `specs/005-programar-partido`.
Coordina con `specs/009-registrar-goles`: los goles se cuentan a partir de sus
eventos; ver la regla de coherencia alineación-eventos en esa spec (FR-003).
No re-decide stack ni modelo — ver `AGENTS.md` §5.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registrar alineaciones y consultar estadísticas de jugadores (Priority: P2)

Como operador, quiero registrar qué jugadores participaron en cada partido, y
como espectador quiero consultar las estadísticas de jugadores (goles
anotados, partidos jugados) para conocer su desempeño individual.

**Why this priority**: Depende de `specs/009-registrar-goles` y entrega el
segundo bloque analítico del producto. La alineación es el dato que hace
derivable "partidos jugados": sin ella, esa métrica no existe.

**Independent Test**: Registrar la alineación de dos partidos finalizados y
goles de un jugador, y verificar que la ficha del jugador muestra el conteo
correcto de goles y de partidos jugados, y que la tabla de goleadores lo
ordena bien.

**Acceptance Scenarios**:

1. **Given** un partido entre A y B, **When** el operador registra la
   alineación con los jugadores participantes de cada equipo, **Then** la
   alineación queda asociada al partido y visible en su ficha.
2. **Given** un partido entre A y B, **When** el operador intenta incluir en
   la alineación a un jugador que no pertenece a ninguno de los dos equipos,
   **Then** el sistema rechaza la operación.
3. **Given** un jugador que aparece en la alineación de 3 partidos
   finalizados, **When** se consultan sus estadísticas, **Then** se muestran 3
   partidos jugados.
4. **Given** un jugador con 4 goles registrados en la liga, **When** se
   consultan sus estadísticas, **Then** se muestran 4 goles anotados.
5. **Given** varios jugadores con goles, **When** se consulta la tabla de
   goleadores, **Then** aparecen ordenados por goles descendente.
6. **Given** un jugador sin goles y sin participaciones, **When** se consultan
   sus estadísticas, **Then** se muestran cero goles y cero partidos jugados
   en lugar de un error o una ficha vacía.
7. **Given** una corrección de resultado aprobada que elimina un gol, **When**
  se consultan las estadísticas del goleador, **Then** el conteo refleja la
  corrección **solo cuando la corrección elimina o anula el evento GOAL** que
  originaba ese gol; un cambio de marcador oficial sin cambio de eventos no
  altera la tabla de goleadores.
8. **Given** un visitante sin sesión o un espectador, **When** intenta
   registrar una alineación, **Then** el sistema rechaza la operación; **When**
   consulta estadísticas, **Then** accede sin autenticarse.

---

### Edge Cases

- ¿Qué ocurre si nunca se registra la alineación de un partido finalizado?
- ¿Qué ocurre si un gol está atribuido a un jugador y luego una corrección de
  alineación lo excluye del partido?

## Compromiso heredado de la spec 009

`specs/009-registrar-goles` implementó su FR-003 (un gol solo puede atribuirse
a un jugador de la alineación, si el partido tiene una) detrás del puerto
`MatchService.jugadores_alineados`, que hoy devuelve siempre `None` porque
`MatchLineup` es entidad de **esta** spec. La regla está probada con un doble
en `backend/tests/unit/test_goal_rules.py`, pero **no tiene cobertura de
integración**.

El plan de esta HU DEBE, por tanto:

1. Implementar `jugadores_alineados` con la consulta real a `MatchLineup`.
2. Añadir la prueba de integración del Acceptance Scenario 3 de la spec 009:
   partido con alineación registrada + gol atribuido a un jugador que no figura
   en ella → rechazo.

Sin esos dos puntos, FR-003 de la 009 queda sin cobertura extremo a extremo de
forma permanente. La desviación está registrada en
`specs/009-registrar-goles/plan.md` §Complexity Tracking.

## Requirements *(mandatory)*

### Functional Requirements

#### Alineaciones

- **FR-001**: El operador MUST poder registrar la alineación de un partido: el
  conjunto de jugadores que participaron, por cada uno de los dos equipos.
- **FR-002**: El sistema MUST rechazar la inclusión en la alineación de un
  jugador que no pertenezca a ninguno de los dos equipos del partido,
  incluyendo jugadores de terceros equipos aunque pertenezcan a la misma liga.
- **FR-003**: El sistema MUST permitir modificar la alineación de un partido
  mientras se mantenga la coherencia con los eventos ya registrados.
- **FR-004**: La alineación MUST ser opcional: un partido puede finalizarse
  sin ella, y en ese caso el sistema MUST señalarlo en la ficha del partido.
  La señalización MUST exponerse en API con `lineup_status` y valores
  `registered` o `missing`.
- **FR-005**: Registrar una alineación MUST requerir sesión con rol operador u
  organizador.

#### Estadísticas de jugadores

- **FR-006**: El sistema MUST calcular los goles de cada jugador
  exclusivamente a partir de los eventos de gol registrados
  (`specs/009-registrar-goles`).
- **FR-007**: El sistema MUST calcular los partidos jugados de cada jugador
  como el número de partidos finalizados en cuya alineación figura.
- **FR-008**: El sistema MUST NOT permitir editar directamente el conteo de
  goles, los partidos jugados ni ninguna estadística acumulada de un jugador.
  En términos de contrato HTTP, los recursos de estadísticas son solo lectura:
  no existen operaciones `POST`, `PUT`, `PATCH` ni `DELETE` para editar
  estadísticas de jugadores.
- **FR-009**: El espectador MUST poder consultar la tabla de goleadores de una
  liga, ordenada por goles descendente.
- **FR-010**: El espectador MUST poder consultar la ficha estadística de un
  jugador individual.
- **FR-011**: Las consultas de estadísticas MUST ser accesibles sin
  autenticación.

### Key Entities

- **MatchLineup (Alineación)**: conjunto de jugadores que participaron en un
  partido, agrupados por equipo. Pertenece a un partido
  (`specs/005-programar-partido`); es la fuente de los partidos jugados de
  cada jugador. Entidad propia de esta spec.
- **PlayerStatistics (Estadísticas de jugador)**: vista derivada, por jugador,
  con goles anotados y partidos jugados. NUNCA se edita: siempre se recalcula
  desde los eventos (`specs/009-registrar-goles`) y las alineaciones. Entidad
  propia de esta spec.

## Non-Functional Requirements

- **NFR-001 (Auditabilidad)**: Toda alta o corrección de alineación MUST quedar
  auditada con `created_by`/`updated_at` y ser trazable al partido y al actor.
- **NFR-002 (Seguridad en lecturas públicas)**: Las respuestas públicas de
  estadísticas MUST excluir cualquier dato sensible (credenciales, tokens,
  correos u otros identificadores no deportivos).
- **NFR-003 (Determinismo del ranking)**: La tabla de goleadores MUST tener
  orden determinista para empates (desempate estable explícito) para evitar
  variaciones entre consultas idénticas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de las estadísticas de jugador coinciden con el conteo
  manual de goles y partidos jugados a partir de los eventos y alineaciones
  registrados.
- **SC-002**: 90% de los espectadores de una prueba de usabilidad identifican
  correctamente el máximo goleador de la liga en su primer intento.

## Assumptions

- **Alineación opcional**: registrar la alineación no es obligatorio para
  finalizar un partido. Los jugadores de un partido sin alineación no suman
  partidos jugados, y la ficha del partido lo indica explícitamente mediante
  `lineup_status = "missing"`.
- **Coherencia alineación-eventos**: los goles solo pueden atribuirse a
  jugadores de la alineación cuando esta existe; si no existe, basta con que
  el jugador pertenezca a uno de los dos equipos.
- **Semántica de correcciones**: "corrección de resultado" y "corrección de
  eventos" son conceptos distintos. Un cambio de marcador sin cambiar eventos
  no altera goleadores; eliminar/anular un evento GOAL sí altera goleadores.
- **Idioma**: la interfaz está en español.
