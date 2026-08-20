# Feature Specification: Consultar la clasificación

**Feature Branch**: `008-consultar-clasificacion`

**Created**: 2026-08-18

**Status**: Draft

**Input**: User description: "Como espectador, quiero consultar la clasificación (tabla de posiciones) de una liga, para conocer el desempeño de los equipos. Reglas: Victoria = 3 puntos, Empate = 1 punto, Derrota = 0 puntos. Orden de desempate: 1) puntos, 2) diferencia de goles (GD = GF - GA), 3) goles a favor." (HU07, backlog `docs/backlog/backlog.md`).

## Dependencies

Depende de `specs/006-registrar-resultado` (los resultados finalizados son la
única fuente de la clasificación). Es de solo lectura: no requiere
`specs/001-fundacion-y-autenticacion`. No re-decide stack ni modelo — ver
`AGENTS.md` §5.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar la clasificación (Priority: P1)

Como espectador, quiero consultar la tabla de posiciones de una liga para
conocer el desempeño de los equipos.

**Why this priority**: Es el entregable analítico central del producto y la
razón por la que un organizador adopta la plataforma.

**Independent Test**: Con una liga que tiene al menos tres partidos
finalizados, consultar la clasificación y verificar puntos, diferencia de
goles y orden.

**Acceptance Scenarios**:

1. **Given** que el equipo A derrotó al equipo B, **When** se consulta la
   clasificación, **Then** A recibe 3 puntos y B recibe 0 puntos.
2. **Given** que dos equipos empataron, **When** se consulta la clasificación,
   **Then** ambos reciben 1 punto.
3. **Given** dos equipos con los mismos puntos, **When** se consulta la
   clasificación, **Then** el de mayor diferencia de goles aparece primero.
4. **Given** dos equipos con los mismos puntos y la misma diferencia de goles,
   **When** se consulta la clasificación, **Then** el de más goles a favor
   aparece primero.
5. **Given** una liga con partidos programados y finalizados, **When** se
   consulta la clasificación, **Then** solo los partidos finalizados
   contribuyen a los puntos.
6. **Given** una clasificación publicada, **When** cualquier usuario intenta
   editar directamente los puntos de un equipo, **Then** el sistema no ofrece
   ninguna vía para hacerlo y rechaza el intento.

---

### Edge Cases

- ¿Qué pasa si dos o más equipos empatan en puntos, diferencia de goles y
  goles a favor simultáneamente?
- ¿Qué pasa con un partido cancelado: cuenta o no en la clasificación?
- ¿Qué se muestra en la clasificación mientras hay una solicitud de corrección
  pendiente sobre un partido ya contabilizado?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST calcular la clasificación exclusivamente a
  partir de los resultados de los partidos finalizados. Los puntos y
  estadísticas de la tabla NUNCA se editan manualmente.
- **FR-002**: El sistema MUST NOT exponer ninguna vía (interfaz, operación o
  carga masiva) para modificar directamente los puntos, la posición o las
  estadísticas acumuladas de un equipo.
- **FR-003**: El sistema MUST asignar 3 puntos por victoria, 1 por empate y 0
  por derrota.
- **FR-004**: La clasificación MUST mostrar, por equipo: partidos jugados,
  ganados, empatados, perdidos, goles a favor, goles en contra, diferencia de
  goles y puntos.
- **FR-005**: El sistema MUST ordenar la clasificación por: 1) puntos
  descendente, 2) diferencia de goles descendente (GD = GF - GA), 3) goles a
  favor descendente.
- **FR-006**: Cuando dos equipos empaten en los tres criterios anteriores, el
  sistema MUST aplicar un desempate determinista y estable (orden alfabético
  por nombre de equipo), de modo que consultas sucesivas devuelvan siempre el
  mismo orden.
- **FR-007**: Los partidos cancelados MUST NOT contribuir a la clasificación.
- **FR-008**: Esta consulta MUST ser accesible sin autenticación.

### Key Entities

- **Standings (Clasificación)**: vista derivada, por liga, con una fila por
  equipo (PJ, G, E, P, GF, GC, GD, Pts, posición). NUNCA se edita: siempre se
  recalcula desde los partidos finalizados (`specs/006-registrar-resultado`).
  Entidad propia de esta spec.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En 100% de los casos, la clasificación calculada por el sistema
  coincide con la clasificación calculada manualmente a partir del mismo
  conjunto de resultados, incluidos los escenarios de desempate.
- **SC-002**: La clasificación refleja el resultado de un partido
  inmediatamente después de registrarlo, sin ninguna acción manual adicional
  de recálculo.
- **SC-003**: La vista de clasificación se muestra completa en menos de 2
  segundos para una liga de 20 equipos.

## Assumptions

- **Idioma**: la interfaz está en español.
- **Equipos que aparecen en la tabla**: figuran todos los equipos activos de la
  liga (con ceros si aún no han jugado) más cualquier equipo dado de baja
  lógica que tenga al menos un partido finalizado. Excluir a un equipo inactivo
  con historial dejaría la tabla incoherente: sus rivales conservan los puntos
  que ganaron contra él.
- **Partidos `in_progress`**: no contribuyen a la clasificación. Solo
  `finished` aporta (FR-001); `scheduled`, `in_progress` y `cancelled` se
  ignoran por igual.
- **Correcciones pendientes**: la clasificación refleja siempre el resultado
  vigente del partido. Una solicitud de corrección pendiente
  (`specs/006-registrar-resultado`) no altera la tabla hasta que se aprueba; al
  aprobarse, la tabla cambia sola en la siguiente consulta, sin recálculo
  manual.
- **Empate absoluto**: cuando dos equipos coinciden en puntos, diferencia de
  goles y goles a favor, el desempate alfabético de FR-006 compara el nombre
  normalizado (sin mayúsculas ni espacios sobrantes), igual que la unicidad de
  nombre por liga ya definida en `specs/003-registrar-equipos`.
