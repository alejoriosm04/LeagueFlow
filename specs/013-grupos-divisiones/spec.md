# Feature Specification: Divisiones (grupos) dentro de una liga

**Feature Branch**: `013-grupos-divisiones`

**Created**: 2026-08-21

**Status**: Draft

**Input**: User description: "Un organizador de una liga necesita poder dividir los equipos inscritos en grupos o divisiones (por ejemplo \"Grupo A\" y \"Grupo B\") para organizar torneos con fase de grupos. Necesita crear, renombrar y eliminar grupos dentro de su liga, y asignar cada equipo a un grupo (un equipo pertenece como máximo a un grupo por liga). Cualquier visitante, sin iniciar sesión, debe poder consultar qué equipos están en cada grupo de una liga. Una liga sin grupos definidos sigue funcionando exactamente igual que hoy."

## Dependencies

Historia **aditiva** sobre el modelo ya entregado. No re-decide stack ni modelo
(AGENTS.md §5): su `plan.md` referencia `specs/001-fundacion-y-autenticacion/plan.md`
y `data-model.md`, y solo documenta lo que **añade**.

- **Depende de** `specs/002-crear-liga` (la liga existe) y
  `specs/003-registrar-equipos` (los equipos a agrupar existen).
- **No modifica** entidades ni contratos existentes: introduce un módulo nuevo
  y lee `teams`/`leagues` por su interfaz pública de servicio (Principio VIII).
- **Habilita** futuras fases de grupos/playoffs, sin decidirlas aquí.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Crear y gestionar los grupos de una liga (Priority: P1)

Como organizador, quiero crear, renombrar y eliminar grupos dentro de mi liga
para organizar la competición por divisiones.

**Why this priority**: Sin un grupo que exista, no hay nada que asignar ni que
consultar. Es el punto de entrada de toda la historia.

**Independent Test**: Crear dos grupos en una liga y verificar que ambos quedan
registrados con su nombre; renombrar uno y verificar el cambio; eliminar el
otro y verificar que desaparece.

**Acceptance Scenarios**:

1. **Given** una liga existente, **When** el organizador crea un grupo con un
   nombre, **Then** el grupo queda registrado en esa liga.
2. **Given** una liga con un grupo llamado "Grupo A", **When** el organizador
   intenta crear otro grupo con el mismo nombre en la misma liga, **Then** el
   sistema rechaza la operación por nombre duplicado.
3. **Given** dos ligas distintas, **When** cada una crea un grupo con el mismo
   nombre, **Then** ambos se crean sin conflicto (la unicidad es por liga).
4. **Given** un grupo existente, **When** el organizador lo renombra, **Then** el
   nuevo nombre queda registrado.
5. **Given** un grupo existente, **When** el organizador lo elimina, **Then** el
   grupo desaparece y sus membresías se borran, pero ningún equipo se elimina.

---

### User Story 2 - Asignar equipos a un grupo (Priority: P1)

Como organizador, quiero asignar y desasignar equipos de mi liga a un grupo
para componer las divisiones.

**Why this priority**: La asignación es lo que le da contenido a un grupo; sin
ella los grupos son cajas vacías.

**Independent Test**: Asignar un equipo a un grupo y verificar que aparece en
su composición; desasignarlo y verificar que deja de aparecer.

**Acceptance Scenarios**:

1. **Given** un grupo y un equipo de la misma liga, **When** el organizador
   asigna el equipo al grupo, **Then** el equipo queda asociado al grupo.
2. **Given** un equipo que ya pertenece a un grupo de la liga, **When** el
   organizador intenta asignarlo a otro grupo de la misma liga, **Then** el
   sistema rechaza la operación (a lo sumo un grupo por liga).
3. **Given** un equipo que no pertenece a la liga del grupo, **When** el
   organizador intenta asignarlo, **Then** el sistema rechaza la operación
   indicando que el equipo no es de esa liga.
4. **Given** un equipo asignado a un grupo, **When** el organizador lo desasigna,
   **Then** el equipo deja de pertenecer al grupo sin ser eliminado.

---

### User Story 3 - Consultar la composición de los grupos (Priority: P2)

Como visitante (sin sesión), quiero consultar qué equipos están en cada grupo de
una liga para entender la organización de la competición.

**Why this priority**: Es la parte pública de la historia; depende de que existan
grupos y asignaciones, pero aporta valor por sí sola como consulta.

**Independent Test**: Abrir la vista de grupos de una liga con equipos asignados
y verificar que muestra cada grupo con sus equipos.

**Acceptance Scenarios**:

1. **Given** una liga con grupos y equipos asignados, **When** un visitante sin
   sesión consulta los grupos, **Then** ve cada grupo con su lista de equipos.
2. **Given** una liga sin grupos definidos, **When** se consulta la composición,
   **Then** la consulta responde con una lista vacía, sin errores.
3. **Given** un equipo sin grupo asignado, **When** se consulta la composición,
   **Then** ese equipo no aparece listado en ningún grupo (su ausencia de grupo
   es un estado normal, no un error).

---

### Edge Cases

- ¿Qué ocurre con los equipos de un grupo cuando el grupo se elimina? Quedan sin
  grupo, intactos.
- ¿Qué ocurre al asignar un equipo a un grupo cuando ya pertenece a otro de la
  misma liga? Se rechaza.
- ¿Qué ocurre al intentar asignar un equipo de otra liga? Se rechaza.
- ¿Qué ocurre al consultar los grupos de una liga inexistente? Se responde con
  el error de "liga no encontrada" ya definido por `specs/002`.
- ¿Qué ocurre si un grupo tiene nombre con espacios o mayúsculas? La unicidad se
  evalúa de forma normalizada (mismo criterio que ligas y equipos).
- ¿Qué ocurre con una liga sin grupos? Funciona exactamente igual que hoy: la
  clasificación y el resto de la operación no dependen de los grupos.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El organizador MUST poder crear un grupo dentro de una liga con
  nombre obligatorio.
- **FR-002**: El nombre de grupo MUST ser único dentro de su liga, evaluado de
  forma normalizada (sin distinguir mayúsculas ni espacios periféricos).
- **FR-003**: El organizador MUST poder renombrar un grupo.
- **FR-004**: El organizador MUST poder eliminar un grupo; al hacerlo se borran
  sus membresías y NUNCA los equipos.
- **FR-005**: El organizador MUST poder asignar un equipo de la liga a un grupo.
- **FR-006**: El organizador MUST poder desasignar un equipo de un grupo.
- **FR-007**: Un equipo MUST pertenecer a lo sumo a un grupo dentro de una misma
  liga.
- **FR-008**: El sistema MUST rechazar la asignación de un equipo que no
  pertenezca a la liga del grupo.
- **FR-009**: Cualquier visitante, sin autenticación, MUST poder consultar los
  grupos de una liga y su composición.
- **FR-010**: Una liga sin grupos MUST mantener intacto el comportamiento del
  resto de la aplicación (la clasificación no depende de los grupos).

### Key Entities

- **Grupo (LeagueGroup)**: división de una liga. Atributos: nombre, liga y
  posición (orden de presentación). Pertenece a una liga.
- **Membresía (GroupTeamMembership)**: pertenencia de un equipo a un grupo.
  Atributos: grupo y equipo. Relaciona un grupo con sus equipos; no modifica la
  entidad `Team`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un organizador crea un grupo y le asigna un equipo en 3
  interacciones o menos.
- **SC-002**: La composición de un grupo refleja una asignación o desasignación
  inmediatamente, sin recálculo ni acción manual adicional.
- **SC-003**: El 100% de los intentos de asignar un equipo a un segundo grupo de
  la misma liga se rechazan.
- **SC-004**: Un visitante sin sesión consulta la composición de los grupos de
  una liga sin ningún paso de autenticación.
- **SC-005**: Una liga sin grupos presenta el mismo comportamiento observable
  que antes de esta historia (0 regresiones).

## Assumptions

- **Equipo sin grupo es un estado normal e indefinido**: no es un error ni exige
  corregirse; un equipo puede permanecer sin grupo toda la temporada.
- **Sin límite de grupos por liga** (no hay un máximo duro en esta versión).
- **Membresía por liga**: la regla "a lo sumo un grupo" se evalúa dentro de una
  misma liga; el mismo equipo no puede estar en dos grupos de la misma liga.
- **Orden de presentación**: el campo `position` del grupo es opcional y solo
  afecta el orden en que se muestran; no tiene reglas de negocio asociadas.
- **La clasificación no depende de los grupos**: los grupos son organización
  adicional, no alteran la tabla de posiciones ni el resto de la operación.

## Out of Scope

- Generación automática de calendario por grupos (round-robin por división).
- Playoffs, eliminatorias o ascensos/descensos entre grupos.
- Grupos que abarquen equipos de varias ligas.
- Edición directa de la tabla de posiciones a partir de los grupos.
