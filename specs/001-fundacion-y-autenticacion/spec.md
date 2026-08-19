# Feature Specification: Fundación técnica y autenticación

**Feature Branch**: `001-fundacion-y-autenticacion`

**Created**: 2026-08-18

**Status**: Draft

**Input**: User description: "Como organizador, quiero que las operaciones de escritura requieran iniciar sesión con un usuario que tenga el rol adecuado, para que solo las personas autorizadas registren o modifiquen información de la liga." Extraído y adaptado de `docs/backlog/backlog.md` (User Story 16 / HU-AUTH), añadido en la sesión de clarificación del 2026-08-18 (respuesta a la pregunta sobre nivel de autenticación).

## Scope Note — por qué esta spec va primero

Esta spec no es una de las 10 HU de línea base del enunciado del curso; es un
**habilitador transversal**. Su justificación de negocio es la autenticación
(HU-AUTH), pero por ser la primera spec en construirse, su fase de
planificación (`/speckit-plan`) es también donde se fijan, **una sola vez para
todo el proyecto**:

- El stack técnico (backend, frontend, base de datos, ORM, testing).
- El modelo de dominio completo (`League`, `Team`, `Player`, `Match`,
  `MatchEvent`, `User`), aunque esta HU solo *usa* la entidad `User`
  directamente — las demás se documentan aquí porque toda spec posterior las
  referencia y ninguna debe volver a diseñarlas.
- Las convenciones de API (formato de error, autenticación de requests, CORS).

Ninguna spec posterior (`specs/002-*` en adelante) debe re-decidir estos
aspectos: su propio `plan.md` referencia `specs/001-fundacion-y-autenticacion/plan.md`
y `data-model.md`, y solo añade lo específico de su HU. Ver `AGENTS.md` §5.

**Esta spec DEBE mezclarse a `main` antes de que cualquier otra empiece su
`/speckit-plan`.**

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Autenticación y control de acceso por rol (Priority: P1)

Como organizador, quiero que las operaciones de escritura requieran iniciar
sesión con un usuario que tenga el rol adecuado, para que solo las personas
autorizadas registren o modifiquen información de la liga.

**Why this priority**: Habilitador P1. Varias reglas de negocio de otras HU
dependen de saber quién actúa — en particular, la aprobación de correcciones
de resultado (spec 006) y la atribución de cada operación de escritura no son
implementables sin identidad. Sin esta spec, ninguna otra puede completar sus
criterios de aceptación relacionados con roles.

**Independent Test**: Iniciar sesión como operador y verificar que puede
registrar resultados pero no aprobar correcciones ni crear ligas; iniciar
sesión como organizador y verificar que sí puede; navegar sin sesión y
verificar que las vistas públicas siguen accesibles.

**Acceptance Scenarios**:

1. **Given** un usuario con credenciales válidas, **When** inicia sesión,
   **Then** accede a las operaciones permitidas por su rol.
2. **Given** credenciales inválidas, **When** se intenta iniciar sesión,
   **Then** el acceso se rechaza con un mensaje genérico que no revela si el
   usuario existe.
3. **Given** un visitante sin sesión, **When** consulta calendario,
   clasificación, estadísticas o perfiles, **Then** accede sin necesidad de
   autenticarse.
4. **Given** un visitante sin sesión, **When** intenta cualquier operación de
   escritura, **Then** el sistema la rechaza y le solicita iniciar sesión.
5. **Given** un usuario con rol operador, **When** intenta crear una liga o
   aprobar una corrección, **Then** el sistema rechaza la operación por
   permisos insuficientes.
6. **Given** una sesión iniciada, **When** el usuario cierra sesión, **Then**
   pierde el acceso a las operaciones de escritura.
7. **Given** cualquier operación de escritura completada, **When** se consulta
   su registro, **Then** queda atribuida al usuario que la realizó.

---

### Edge Cases

- ¿Qué ocurre si la liga se queda sin ningún usuario con rol de organizador
  activo?
- ¿Qué ocurre si dos organizadores modifican el rol del mismo usuario al mismo
  tiempo?
- ¿Qué pasa con las sesiones activas de un usuario al que se le revoca el rol?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST distinguir tres roles: organizador (gestiona
  ligas, equipos, jugadores y partidos, y aprueba correcciones), operador
  (registra resultados, eventos y alineaciones, y solicita correcciones) y
  espectador (solo consulta, sin cuenta).
- **FR-002**: Toda la información de consulta (calendario, resultados,
  clasificación, estadísticas, perfiles, búsqueda) MUST ser accesible sin
  autenticación.
- **FR-003**: Toda operación de escritura definida en cualquier spec del
  proyecto MUST requerir una sesión autenticada con un rol suficiente.
- **FR-004**: Cada usuario MUST tener credenciales propias (identificador y
  contraseña) y exactamente un rol asignado.
- **FR-005**: El sistema MUST NOT almacenar ni mostrar las contraseñas de
  forma que permitan recuperarlas en texto claro.
- **FR-006**: El usuario MUST poder cerrar sesión, y la sesión MUST expirar
  tras un periodo de inactividad.
- **FR-007**: Un usuario con rol organizador MUST poder crear cuentas de
  usuario y asignarles rol; el sistema MUST NOT permitir el autorregistro
  público.
- **FR-008**: El sistema MUST atribuir cada operación de escritura al usuario
  que la realizó, y esa atribución MUST estar disponible para consulta.
- **FR-009**: Un intento de operación con rol insuficiente MUST rechazarse con
  un mensaje de permisos insuficientes.
- **FR-010**: Un intento de inicio de sesión fallido MUST responder con un
  mensaje genérico que no revele si el identificador existe.
- **FR-011**: Toda operación rechazada en cualquier parte del sistema MUST
  devolver un mensaje comprensible que indique qué regla se incumplió y qué
  campo corregir.
- **FR-012**: El sistema MUST NOT mostrar detalles técnicos internos al
  usuario cuando ocurra un error inesperado.

### Key Entities

- **User (Usuario)**: persona autenticada que opera el sistema. Atributos:
  identificador, credencial, rol (organizador u operador), estado. Entidad
  propia de esta spec.
- **Session**: entidad de infraestructura que sostiene FR-003/FR-006/FR-008;
  no es una entidad de negocio con Key Entity propia en el backlog original,
  pero se documenta en `data-model.md` porque toda ruta de escritura la usa.
- **League, Team, Player, Match, MatchLineup, MatchEvent,
  ResultCorrectionRequest**: documentadas aquí por ser el modelo de dominio
  compartido que toda spec posterior usa; su ciclo de vida (creación, reglas)
  se especifica en `specs/002-*` en adelante, no aquí.
- **Standings, PlayerStatistics**: vistas derivadas (nunca tablas editables)
  que consultan `specs/008-*` y `specs/010-*` respectivamente.
- Descripción completa de atributos, relaciones y transiciones de estado de
  las diez entidades: `data-model.md` (Phase 1 de esta spec). Origen de
  negocio de cada una: `docs/backlog/backlog.md` sección Key Entities.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de las operaciones de escritura son rechazadas cuando se
  intentan sin sesión o con un rol insuficiente, verificado sobre el catálogo
  completo de operaciones de todas las specs.
- **SC-002**: 100% de las operaciones rechazadas por regla de negocio muestran
  un mensaje que identifica la regla incumplida.
- **SC-003**: Un usuario autenticado con el rol correcto completa el inicio de
  sesión en menos de 5 segundos.

## Assumptions

- **Cuentas de usuario**: el sistema se despliega con una cuenta inicial de
  organizador (semilla); a partir de ahí, los organizadores crean el resto de
  cuentas. No hay autorregistro público ni registro de espectadores: el
  espectador es un visitante anónimo.
- **Recuperación de contraseña**: no se implementa autoservicio de
  recuperación en esta versión; un organizador restablece la credencial de un
  usuario.
- **Idioma**: la interfaz está en español.

## Out of Scope

- Autorregistro público de usuarios.
- Autoservicio de recuperación de contraseña.
- Roles adicionales a organizador/operador (el espectador no tiene cuenta).
- Integraciones de autenticación externa (SSO, OAuth de terceros).
