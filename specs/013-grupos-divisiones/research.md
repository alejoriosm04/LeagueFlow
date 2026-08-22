# Research: Divisiones (grupos) dentro de una liga

Decisiones de diseño propias de `013-grupos-divisiones`. Todo lo heredado
(stack, autenticación, convenciones de API, modelo base) está en
`specs/001-fundacion-y-autenticacion/research.md` y `plan.md`.

## 1. Modelado de la pertenencia: tabla puente, no FK en `teams`

- **Decision**: `GroupTeamMembership` como tabla propia (`group_memberships`)
  que relaciona `groups` y `teams`. `teams` no gana ninguna columna nueva.
- **Rationale**: el equipo ya definió que las specs del bloque paralelo no
  tocan dominios ajenos (Principio VIII). Un `group_id` en `teams` acoplaría el
  módulo `groups/` al modelo interno de `teams` y crearía un punto de merge con
  cualquier spec futura que toque `teams`. La tabla puente mantiene la historia
  de membresías separada y permite evolucionar a fases de grupos/playoffs sin
  migrar `teams`.
- **Alternatives considered**:
  - `group_id` FK en `teams`: más simple de consultar, pero modifica el dominio
    `Team` (rechazado por el criterio de aislamiento).
  - Campo `group` (string) en `teams`: pierde integridad referencial (rechazado).

## 2. "A lo sumo un grupo por liga": `UNIQUE (team_id)` en membresías

- **Decision**: la tabla `group_memberships` lleva `UNIQUE (team_id)`.
- **Rationale**: un equipo pertenece a exactamente una liga (modelo de `001`),
  así que "a lo sumo un grupo por liga" (FR-007) es equivalente a "a lo sumo un
  grupo en total". Un `UNIQUE` a nivel de base garantiza la regla incluso bajo
  concurrencia, sin depender solo de una comprobación en el servicio.
- **Alternatives considered**:
  - Solo comprobación en `service.py`: funciona, pero dos asignaciones
    concurrentes podrían colarse (rechazado por no ser a prueba de carrera).
  - `UNIQUE (league_id, team_id)` con `league_id` desnormalizado en la
    membresía: redundante y requiere mantener el dato (rechazado).

## 3. Eliminar un grupo borra membresías, nunca equipos

- **Decision**: FK `group_memberships.group_id → groups.id ON DELETE CASCADE`;
  `team_id → teams.id ON DELETE RESTRICT`.
- **Rationale**: FR-004 exige que al borrar un grupo desaparezcan sus membresías
  y NUNCA los equipos. El `CASCADE` deja la integridad en la base; `RESTRICT`
  sobre `teams` impide borrar un equipo que está en un grupo (los equipos con
  historia se marcan inactivos, no se borran — `specs/003`).
- **Alternatives considered**: borrar membresías a mano en el servicio antes de
  borrar el grupo (rechazado: la base debe garantizar la integridad por sí sola).

## 4. Equipos inactivos (clarificación de `spec.md`)

- **Decision**: un equipo inactivo se **muestra** en la composición si ya es
  miembro del grupo, pero **no se puede asignar** a un grupo nuevo (FR-011,
  FR-012).
- **Rationale**: coherente con la clasificación (`specs/008`), que mantiene
  visible al equipo inactivo con historial. La composición es la "foto" del
  grupo; la asignación es una operación de organización que solo aplica a
  equipos activos.
- **Alternatives considered**: omitir los inactivos de la composición (rechazado:
  perdería el registro de quién estuvo en el grupo); permitir asignar inactivos
  (rechazado: contradice el sentido de "inactivo" como baja).

## 5. Orden de presentación de los grupos

- **Decision**: campo `position` (entero) opcional en `groups`; solo afecta el
  orden de listado, sin reglas de negocio asociadas.
- **Rationale**: el organizador quiere controlar el orden ("Grupo A" antes que
  "Grupo B"); dejarlo opcional evita imponer un ordenamiento.
- **Alternatives considered**: orden alfabético por nombre (rechazado: no da
  control); obligar `position` único (rechazado: innecesario para la demo).

## 6. Códigos de error nuevos

- **Decision**: reutilizar el envelope de error de `001` y añadir estos códigos
  en `src/core/errors.py` (o local al módulo, según patrón existente):
  `group_not_found`, `group_name_duplicate`, `team_not_found_in_league`,
  `team_already_in_group`, `team_inactive`.
- **Rationale**: cada Acceptance Scenario de `spec.md` exige un rechazo
  identificable y testeable; los códigos siguen el patrón `*_not_found` /
  `*_duplicate` ya usado por `teams` y `leagues`.
- **Alternatives considered**: reutilizar `team_not_found` para todos los casos
  (rechazado: no distingue "equipo ajeno a la liga" de "equipo ya en un grupo",
  y FR-008 exige esa distinción).
