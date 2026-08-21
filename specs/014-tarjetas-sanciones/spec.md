# Feature Specification: Tarjetas y sanciones disciplinarias

**Feature Branch**: `014-tarjetas-sanciones`

**Created**: 2026-08-21

**Status**: Draft

**Input**: User description: "Un operador necesita registrar las tarjetas amarillas y rojas que recibe un jugador durante un partido en curso o finalizado. La tarjeta se registra como un evento del partido. El sistema debe derivar automáticamente, en cada consulta, si un jugador está suspendido (dos amarillas en partidos distintos o una roja). Cualquier visitante, sin iniciar sesión, debe poder consultar la ficha disciplinaria de un jugador: cuántas tarjetas tiene y si está suspendido."

## Dependencies

Historia **aditiva** sobre el modelo ya entregado. No re-decide stack ni modelo
(AGENTS.md §5): su `plan.md` referencia `specs/001-fundacion-y-autenticacion/plan.md`
y `data-model.md`, y solo documenta lo que **añade**.

- **Depende de** `specs/009-registrar-goles` (el evento de partido ya existe y
  está diseñado para admitir tipos nuevos) y `specs/010-alineaciones-estadisticas`
  (para validar si un jugador está en la alineación). También de
  `specs/003-registrar-jugadores` (el jugador a sancionar existe).
- **Extiende** el evento de partido con dos tipos nuevos de tarjeta; esta historia
  es la **dueña exclusiva del dominio de partidos** entre las cinco del bloque
  paralelo (ninguna otra lo toca).
- **Añade** la derivación de la suspensión en un módulo nuevo, leyendo los
  eventos por servicio (patrón de `statistics`), sin tocar sus modelos.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registrar tarjetas de un partido (Priority: P1)

Como operador, quiero registrar la tarjeta amarilla o roja que recibe un jugador
durante un partido, para dejar constancia disciplinaria del encuentro.

**Why this priority**: Sin el registro de tarjetas no hay dato del que derivar la
suspensión ni ficha que consultar; es el punto de entrada de toda la historia.

**Independent Test**: Sobre un partido en curso, registrar una amarilla a un
jugador participante y verificar que queda registrada como evento del partido.

**Acceptance Scenarios**:

1. **Given** un partido en curso o finalizado, **When** el operador registra una
   tarjeta amarilla a un jugador participante, **Then** la tarjeta queda
   registrada como evento del partido.
2. **Given** un partido en curso o finalizado, **When** el operador registra una
   tarjeta roja a un jugador participante, **Then** la tarjeta queda registrada
   como evento del partido.
3. **Given** un partido programado o cancelado, **When** el operador intenta
   registrar una tarjeta, **Then** el sistema rechaza la operación.
4. **Given** un partido con alineación registrada, **When** el operador registra
   una tarjeta a un jugador que no figura en la alineación, **Then** el sistema
   rechaza la operación.
5. **Given** un partido sin alineación registrada, **When** el operador registra
   una tarjeta a un jugador de uno de los dos equipos, **Then** la operación se
   permite.
6. **Given** un partido, **When** el operador registra una tarjeta a un jugador
   que no pertenece a ninguno de los dos equipos, **Then** el sistema rechaza la
   operación.

---

### User Story 2 - Derivar la suspensión de un jugador (Priority: P1)

Como sistema, quiero derivar automáticamente si un jugador está suspendido a
partir de sus tarjetas, para no depender de que alguien lo marque a mano.

**Why this priority**: Es la regla de negocio de la historia; convierte las
tarjetas registradas en una señal accionable sin edición manual.

**Independent Test**: Registrar una roja directa y verificar que el jugador
queda suspendido en su ficha; registrar una segunda amarilla en un partido
distinto y verificar el mismo resultado.

**Acceptance Scenarios**:

1. **Given** un jugador con una tarjeta roja, **When** se consulta su estado,
   **Then** aparece como suspendido.
2. **Given** un jugador con dos tarjetas amarillas en partidos distintos, **When**
   se consulta su estado, **Then** aparece como suspendido.
3. **Given** un jugador con una sola tarjeta amarilla, **When** se consulta su
   estado, **Then** NO aparece como suspendido.
4. **Given** un jugador sin tarjetas, **When** se consulta su estado, **Then** NO
   aparece como suspendido.

---

### User Story 3 - Consultar la ficha disciplinaria (Priority: P2)

Como visitante (sin sesión), quiero consultar la ficha disciplinaria de un
jugador para ver cuántas tarjetas tiene y si está suspendido.

**Why this priority**: Es la parte pública de la historia; depende de que existan
tarjetas registradas, pero aporta valor por sí sola como consulta.

**Independent Test**: Abrir la ficha disciplinaria de un jugador con tarjetas y
verificar que muestra el conteo de amarillas/rojas y su estado de suspensión.

**Acceptance Scenarios**:

1. **Given** un jugador con tarjetas registradas, **When** un visitante sin
   sesión consulta su ficha, **Then** ve cuántas amarillas y rojas tiene.
2. **Given** un jugador suspendido, **When** un visitante consulta su ficha,
   **Then** ve que está suspendido.
3. **Given** un jugador sin tarjetas, **When** un visitante consulta su ficha,
   **Then** ve la ficha en cero, sin errores.

---

### Edge Cases

- ¿Qué ocurre al registrar una tarjeta a un jugador que no es de los dos equipos
  del partido? Se rechaza.
- ¿Qué ocurre al registrar una tarjeta a un jugador que no está en la alineación
  (cuando la alineación existe)? Se rechaza; si no hay alineación, se permite.
- ¿Qué ocurre al registrar tarjetas en un partido programado o cancelado? Se
  rechaza.
- ¿Qué ocurre con dos amarillas del mismo jugador en el mismo partido? Se
  registran como dos eventos, pero no disparan la suspensión por acumulación
  (esa regla exige partidos distintos).
- ¿Qué ocurre si un jugador suspendido aparece en una alineación posterior? El
  sistema informa la suspensión pero no bloquea la alineación (fuera de alcance).
- ¿Qué ocurre al consultar la ficha de un jugador inexistente? Se responde con el
  error de "jugador no encontrado" ya definido por `specs/003`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El operador MUST poder registrar una tarjeta amarilla o roja de un
  partido como evento, indicando el jugador y el minuto.
- **FR-002**: El sistema MUST permitir el registro de tarjetas únicamente en
  partidos en curso o finalizados; MUST rechazarlo en programado o cancelado.
- **FR-003**: Si el partido tiene alineación registrada, el sistema MUST rechazar
  una tarjeta a un jugador que no figure en ella; si no hay alineación, MUST
  permitirlo igual.
- **FR-004**: El sistema MUST rechazar una tarjeta a un jugador que no pertenezca
  a ninguno de los dos equipos del partido.
- **FR-005**: El sistema MUST permitir varias tarjetas del mismo jugador en el
  mismo partido.
- **FR-006**: El equipo de la tarjeta MUST derivarse del jugador, NUNCA ser
  proporcionado por el cliente.
- **FR-007**: El sistema MUST derivar la suspensión de un jugador en cada lectura
  (una roja, o dos amarillas en partidos distintos), y MUST NOT almacenarla como
  una bandera editable.
- **FR-008**: Cualquier visitante, sin autenticación, MUST poder consultar la
  ficha disciplinaria de un jugador (conteo de amarillas y rojas, y estado de
  suspensión).

### Key Entities

- **Evento de partido (tarjeta)**: hecho ocurrido durante un partido. Se amplía el
  tipo de evento para admitir tarjeta amarilla y roja, además del gol existente.
  Atributos: tipo, jugador, equipo y minuto.
- **Ficha disciplinaria**: vista derivada por jugador con el conteo de tarjetas
  (amarillas y rojas) y el estado de suspensión. NUNCA se edita: se recalcula a
  partir de los eventos de tarjeta.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un operador registra una tarjeta en 2 interacciones o menos.
- **SC-002**: La suspensión se refleja en la ficha inmediatamente después de
  registrar la tarjeta que la dispara, sin recálculo manual.
- **SC-003**: El 100% de las tarjetas atribuidas a un jugador que no es de los
  dos equipos del partido se rechazan.
- **SC-004**: Un visitante sin sesión consulta la ficha disciplinaria de un
  jugador sin ningún paso de autenticación.
- **SC-005**: El estado de suspensión es consistente en todas las consultas (0
  casos donde la ficha contradiga las tarjetas registradas).

## Assumptions

- **Acumulación por temporada**: la cuenta de amarillas es por toda la temporada
  (no se reinicia por jornada ni por fase).
- **Dos amarillas en el mismo partido** no disparan la suspensión por acumulación;
  solo cuentan amarillas en partidos distintos. Una expulsión por doble amarilla
  en el mismo partido se reflejaría registrando una tarjeta roja aparte.
- **Roles de escritura**: el registro de tarjetas lo hace el operador (y el
  organizador), igual que el resto de eventos del partido. La consulta es pública.
- **La suspensión no bloquea alineaciones**: informar la suspensión no impide
  registrar al jugador en una alineación posterior (fuera de alcance).
- **El jugador existe**: la tarjeta siempre referencia a un jugador ya registrado
  (el alta de jugadores es de `specs/003`).

## Out of Scope

- Expulsión automática por doble amarilla en el mismo partido (solo se registran
  eventos; el árbitro decide la roja y el operador la registra).
- Cumplimiento automático de suspensiones (bloquear la inclusión de un suspendido
  en una alineación).
- Historial de cumplimiento o edición de tarjetas una vez registradas.
- Apelaciones o revisión de sanciones.
