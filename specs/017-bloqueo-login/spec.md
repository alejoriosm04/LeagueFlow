# Feature Specification: Bloqueo tras intentos fallidos de inicio de sesión

**Feature Branch**: `017-bloqueo-login`

**Created**: 2026-08-21

**Status**: Draft

**Input**: User description: "El sistema necesita protegerse de ataques de fuerza bruta contra el inicio de sesión: si alguien falla varias veces seguidas al iniciar sesión con el mismo identificador de usuario, ese identificador debe quedar bloqueado temporalmente antes de poder intentarlo de nuevo, incluso si luego usa la contraseña correcta. El bloqueo es específico por identificador de usuario: no debe afectar el inicio de sesión de nadie más, y no debe revelar si ese identificador existe o no en el sistema. Pasado el tiempo de bloqueo, el inicio de sesión vuelve a funcionar normalmente."

## Clarifications

### Session 2026-08-21

- Q: ¿El conteo de intentos fallidos debe usar el identificador normalizado (sin distinguir mayúsculas), o la cadena exacta tal como se envió? → A: Identificador normalizado, sin distinguir mayúsculas (el mismo criterio con que el login busca al usuario), para que el bloqueo no sea esquivables alternando mayúsculas.

## Dependencies

Historia de **seguridad del inicio de sesión**. Es la única del bloque paralelo que
modifica código existente (`auth/`), a propósito: la autenticación es territorio
exclusivo de un solo integrante y no compite con las demás specs. No re-decide
stack ni modelo (AGENTS.md §5): su `plan.md` referencia
`specs/001-fundacion-y-autenticacion/plan.md` y `data-model.md`, y solo documenta
lo que **añade**.

- **Depende de** `specs/001-fundacion-y-autenticacion` (el flujo de login y la
  sesión ya existen).
- **Añade** el conteo de intentos fallidos y la lógica de bloqueo en el login,
  reutilizando la respuesta genérica ya existente para no revelar si el usuario
  existe.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bloquear un identificador tras varios intentos fallidos (Priority: P1)

Como sistema, quiero bloquear temporalmente un identificador de usuario cuando
alguien falla varias veces seguidas al iniciar sesión, para dificultar ataques de
fuerza bruta.

**Why this priority**: Es el núcleo de la historia: sin el bloqueo no hay
protección efectiva contra intentos repetidos.

**Independent Test**: Fallar el inicio de sesión varias veces consecutivas con el
mismo identificador y verificar que, al superar el umbral, queda bloqueado.

**Acceptance Scenarios**:

1. **Given** un identificador con varios intentos fallidos consecutivos, **When**
   se supera el umbral, **Then** el identificador queda bloqueado temporalmente.
2. **Given** un identificador bloqueado, **When** alguien intenta iniciar sesión
   con la contraseña correcta, **Then** el sistema rechaza el intento mientras
   dure el bloqueo.
3. **Given** un identificador bloqueado, **When** otro usuario intenta iniciar
   sesión, **Then** su inicio de sesión no se ve afectado.
4. **Given** un intento fallido, **When** el sistema responde, **Then** la
   respuesta no revela si el identificador existe o si está bloqueado.

---

### User Story 2 - Desbloquear automáticamente al expirar (Priority: P2)

Como sistema, quiero que el bloqueo expire automáticamente tras un periodo, para
que el usuario legítimo recupere el acceso sin intervención manual.

**Why this priority**: Sin desbloqueo automático, el bloqueo sería permanente y
bloquearía a usuarios legítimos; depende del bloqueo (Historia 1) pero es la
segunda mitad del comportamiento.

**Independent Test**: Bloquear un identificador, esperar a que expire el periodo
y verificar que el inicio de sesión vuelve a funcionar.

**Acceptance Scenarios**:

1. **Given** un identificador bloqueado, **When** transcurre el periodo de
   bloqueo, **Then** el inicio de sesión vuelve a funcionar normalmente.
2. **Given** un usuario que falla una vez y luego acierta antes del umbral,
   **When** inicia sesión correctamente, **Then** su conteo de fallos se reinicia.
3. **Given** un usuario bloqueado que inicia sesión correctamente tras el
   desbloqueo, **When** lo hace, **Then** su conteo de fallos queda en cero.

---

### Edge Cases

- ¿Qué ocurre si el identificador no existe? Se cuenta igual el intento fallido
  (para no revelar su inexistencia) y, al superar el umbral, se bloquea ese
  identificador igualmente.
- ¿Qué ocurre si se alternan mayúsculas y minúsculas en el identificador? Cuentan
  como el mismo identificador (el conteo se hace normalizado).
- ¿Qué ocurre si se reintenta con la contraseña correcta durante el bloqueo? Se
  rechaza igualmente hasta que expire.
- ¿Qué ocurre si el conteo se pierde al reiniciar el sistema? El conteo persiste,
  para que el bloqueo siga siendo efectivo.
- ¿Qué ocurre con dos intentos simultáneos sobre el mismo identificador? El
  conteo es consistente y no se salta el bloqueo.
- ¿Qué ocurre si el umbral o la duración cambian entre intentos? Se aplican los
  valores configurados en el momento de la verificación.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST contar los intentos fallidos de inicio de sesión
  por identificador de usuario normalizado (sin distinguir mayúsculas), el mismo
  criterio con que el login busca al usuario, exista o no ese usuario.
- **FR-002**: El sistema MUST bloquear temporalmente un identificador al superar
  un umbral de intentos fallidos consecutivos, y MUST rechazar los intentos
  posteriores con un error de bloqueo que indique cuánto falta para reintentar.
- **FR-003**: El sistema MUST rechazar el inicio de sesión de un identificador
  bloqueado incluso si la contraseña es correcta, mientras dure el bloqueo.
- **FR-004**: El sistema MUST desbloquear automáticamente el identificador al
  expirar el periodo de bloqueo.
- **FR-005**: El sistema MUST reiniciar el conteo de fallos tras un inicio de
  sesión exitoso.
- **FR-006**: El sistema MUST NOT revelar en sus respuestas si un identificador
  existe o si está bloqueado (la respuesta de "credenciales inválidas" es la
  misma que la ya existente).
- **FR-007**: El umbral de intentos y la duración del bloqueo MUST ser
  configurables, sin cambios de código.

### Key Entities

- **Intento de inicio de sesión**: registro por identificador normalizado de
  usuario (sin mayúsculas) con el conteo de fallos consecutivos, el momento hasta
  el que está bloqueado (si aplica) y su última actualización. No expone si el
  identificador existe.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los identificadores que superan el umbral de fallos
  quedan bloqueados temporalmente.
- **SC-002**: El 100% de los intentos con contraseña correcta durante el bloqueo
  son rechazados.
- **SC-003**: El 100% de los identificadores bloqueados recuperan el acceso
  automáticamente al expirar el periodo.
- **SC-004**: Un bloqueo de un identificador no impide el inicio de sesión de
  ningún otro (0 interferencias).
- **SC-005**: El 0% de las respuestas de inicio de sesión revela si el
  identificador existe o está bloqueado.

## Assumptions

- **Umbral y duración por defecto**: 5 intentos fallidos consecutivos y 15
  minutos de bloqueo, configurables por variable de entorno.
- **Bloqueo por identificador**: se bloquea por nombre de usuario, no por
  dirección IP ni por dispositivo.
- **Conteo persistente**: el conteo de fallos sobrevive a reinicios, para que el
  bloqueo sea efectivo.
- **Sin distinción de error**: "usuario no existe" y "contraseña incorrecta"
  siguen devolviendo la misma respuesta (la simetría ya existente no se rompe).

## Out of Scope

- Bloqueo por dirección IP o por dispositivo.
- Captcha u otros desafíos anti-bot.
- Notificación al usuario de que su cuenta quedó bloqueada.
- Desbloqueo manual por un organizador.
