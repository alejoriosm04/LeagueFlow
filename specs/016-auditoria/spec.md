# Feature Specification: Auditoría de operaciones administrativas

**Feature Branch**: `016-auditoria`

**Created**: 2026-08-21

**Status**: Draft

**Input**: User description: "El equipo necesita poder ver un historial de qué operación administrativa se hizo, quién la hizo y cuándo (crear una liga, registrar un resultado, etc.), para poder investigar un dato incorrecto o un incidente sin tener que revisar la base de datos manualmente. Solo un organizador autenticado puede consultar ese historial; las consultas públicas (lecturas) no se registran, solo las operaciones que modifican datos."

## Clarifications

### Session 2026-08-21

- Q: ¿El registro de auditoría debe incluir también las operaciones de escritura que fallan (por validación o permisos insuficientes), o solo las que terminan con éxito? → A: Solo escrituras exitosas; los fallos por validación o permisos no se registran.

## Dependencies

Historia **transversal de observabilidad**. No introduce reglas de negocio ni
modifica los endpoints existentes: captura las escrituras de forma genérica. No
re-decide stack ni modelo (AGENTS.md §5): su `plan.md` referencia
`specs/001-fundacion-y-autenticacion/plan.md` y `data-model.md`, y solo documenta
lo que **añade**.

- **Depende de** `specs/001-fundacion-y-autenticacion` (sesión y roles, para
  determinar quién actuó y quién puede consultar el historial).
- **Añade** una tabla de registros y una consulta de solo lectura, sin
  instrumentar endpoint por endpoint: la captura es automática y transversal.
- **No compite** con ninguna otra spec del bloque paralelo (nadie más toca este
  mecanismo).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registrar automáticamente cada operación que modifica datos (Priority: P1)

Como equipo, quiero que cada operación que modifica datos quede registrada
automáticamente con quién la hizo, qué se hizo y cuándo, para poder investigar un
dato incorrecto o un incidente sin revisar la base de datos a mano.

**Why this priority**: Sin el registro no hay nada que consultar; es el punto de
entrada de la historia. Es la capacidad que le da trazabilidad operativa al
producto.

**Independent Test**: Realizar una operación de escritura autenticada (por
ejemplo, crear una liga) y verificar que queda una entrada con el actor, la
acción y la fecha.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado, **When** realiza una operación de escritura
   exitosa, **Then** queda registrada una entrada con el actor, la acción y la
   fecha.
2. **Given** cualquier usuario, **When** realiza una consulta de lectura, **Then**
   esa lectura NO se registra.
3. **Given** una operación de escritura, **When** se registra, **Then** el
   registro no incluye el contenido de lo que se envió ni de lo que se respondió
   (solo método, destino, resultado y actor).

---

### User Story 2 - Consultar el historial de auditoría (Priority: P2)

Como organizador, quiero consultar el historial de operaciones para trazar qué
cambió, quién lo hizo y cuándo.

**Why this priority**: Es la parte que hace útil al registro; depende de que
existan entradas (Historia 1), pero aporta valor por sí sola como consulta.

**Independent Test**: Tras registrar una escritura, abrir el historial como
organizador y verificar que aparece la entrada en orden cronológico.

**Acceptance Scenarios**:

1. **Given** un organizador autenticado, **When** consulta el historial, **Then**
   ve las entradas ordenadas por fecha (la más reciente primero).
2. **Given** un usuario sin rol de organizador, **When** intenta consultar el
   historial, **Then** el sistema rechaza el acceso.
3. **Given** un visitante sin sesión, **When** intenta consultar el historial,
   **Then** el sistema rechaza el acceso.

---

### Edge Cases

- ¿Qué ocurre con una operación de escritura que falla (por ejemplo, validación o
  permisos)? No queda registrada (solo se registran escrituras exitosas).
- ¿Qué ocurre si la operación se hace sin sesión? No puede ser una escritura
  exitosa (las escrituras requieren sesión), por lo que no aplica.
- ¿Qué ocurre si el historial está vacío? La consulta devuelve una lista vacía,
  sin errores.
- ¿Qué ocurre si dos escrituras ocurren casi a la vez? Cada una genera su propia
  entrada, sin sobrescribirse.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST registrar automáticamente toda operación de
  escritura exitosa (crear, modificar o eliminar datos) con el actor, la acción
  y la fecha.
- **FR-002**: El sistema MUST NOT registrar las consultas de lectura.
- **FR-003**: Cada registro MUST contener el método de la acción, el destino, el
  resultado y el actor, y MUST NOT contener el cuerpo de la petición ni de la
  respuesta.
- **FR-004**: El actor del registro MUST ser el usuario autenticado que realizó
  la operación; si no es determinable, el registro lo indica explícitamente.
- **FR-005**: El organizador MUST poder consultar el historial de auditoría en
  orden cronológico (más reciente primero).
- **FR-006**: El sistema MUST rechazar la consulta del historial a usuarios sin
  rol de organizador o sin sesión.
- **FR-007**: La captura MUST ser genérica y automática, sin requerir modificar
  cada operación existente para que quede registrada.

### Key Entities

- **Registro de auditoría**: entrada que documenta una operación de escritura.
  Atributos: acción (método), destino, resultado, actor (usuario, o ausencia de
  sesión) y fecha. Se escribe de forma automática y transversal.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las operaciones de escritura exitosas quedan registradas
  con actor, acción y fecha.
- **SC-002**: El 0% de las consultas de lectura quedan registradas.
- **SC-003**: El 0% de los registros contiene el cuerpo de una petición o de una
  respuesta (verificable sobre el historial completo).
- **SC-004**: El 100% de los intentos de consultar el historial sin rol de
  organizador o sin sesión se rechazan.
- **SC-005**: Un organizador encuentra una operación reciente en el historial en
  3 interacciones o menos.

## Assumptions

- **Solo escrituras exitosas**: se registran las operaciones de escritura que
  terminan con éxito; las que fallan por validación o permisos no se registran.
- **Captura transversal**: la captura es automática y genérica; no se instrumenta
  cada operación una por una.
- **Retención indefinida**: los registros se conservan indefinidamente en esta
  versión (sin purga automática).
- **Sin datos sensibles**: el registro nunca almacena el contenido de peticiones
  ni respuestas, para no exponer datos personales ni credenciales.

## Out of Scope

- Registro de operaciones de lectura.
- Registro del cuerpo de peticiones o respuestas.
- Purga o rotación automática de registros antiguos.
- Exportación del historial de auditoría.
- Notificaciones o alertas sobre operaciones sospechosas.
