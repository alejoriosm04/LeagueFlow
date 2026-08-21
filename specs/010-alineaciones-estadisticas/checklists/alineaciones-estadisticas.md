# Requirements Quality Checklist: Alineaciones y Estadisticas

**Purpose**: Validar la calidad de redaccion de requisitos para alineaciones y estadisticas derivadas (completitud, claridad, consistencia, medibilidad y cobertura)
**Created**: 2026-08-20
**Feature**: [spec.md](../spec.md)

**Note**: Este checklist fue generado con enfoque de calidad de requisitos (no de verificacion de implementacion).
**Review Ownership**: Este checklist pertenece a quien revisa requisitos. Marcar un item con [x] solo cuando el criterio de calidad de requisitos este satisfecho.
**Marker Semantics**: [x] significa criterio revisado y satisfecho para calidad de requisitos; no significa trabajo de implementacion completado.

## Requirement Completeness

- [x] CHK001 Estan definidos los criterios de pertenencia de jugador para ambos equipos del partido sin dejar casos implicitos (titulares/suplentes/participantes)? [Completeness, Spec §FR-001, Spec §FR-002]
- [x] CHK002 Esta documentado de forma completa que ocurre cuando el partido finaliza sin alineacion registrada, incluyendo la respuesta esperada de API? [Completeness, Spec §FR-004, Spec §Edge Cases]
- [x] CHK003 Estan definidos los requisitos de recalculo para estadisticas cuando cambian eventos de gol, no solo cuando cambian marcadores? [Completeness, Spec §FR-006, Spec §Acceptance Scenario 7]
- [x] CHK004 Estan definidos los requisitos de acceso anonimo para todas las consultas de estadisticas relevantes (tabla y ficha individual)? [Completeness, Spec §FR-009, Spec §FR-010, Spec §FR-011]

## Requirement Clarity

- [x] CHK005 Esta claramente especificado que "no pertenezca a ninguno de los dos equipos" incluye cualquier jugador externo aunque exista en la misma liga? [Clarity, Spec §FR-002]
- [x] CHK006 Esta claramente distinguido el significado de "correccion de resultado" frente a "eliminacion/anulacion de evento GOAL" para evitar interpretaciones opuestas del conteo de goles? [Ambiguity, Spec §Acceptance Scenario 7, Assumption]
- [x] CHK007 Esta cuantificado de forma objetiva que "nunca se editan directamente" las estadisticas (por ejemplo, ausencia de endpoints de escritura o regla equivalente)? [Clarity, Spec §FR-008]
- [x] CHK008 Estan definidos con precision los estados observables de alineacion opcional y su nomenclatura para cliente/API? [Clarity, Spec §FR-004, Assumption]

## Requirement Consistency

- [x] CHK009 Son consistentes entre si los requisitos de derivacion de goles (eventos) y los escenarios de correccion de resultado para que no existan dos fuentes de verdad? [Consistency, Spec §FR-006, Spec §Acceptance Scenario 7]
- [x] CHK010 Son consistentes los requisitos de autorizacion de escritura (operador/organizador) con el requisito de lectura anonima de estadisticas? [Consistency, Spec §FR-005, Spec §FR-011]
- [x] CHK011 Estan alineados los terminos "alineacion", "participacion" y "partidos jugados" sin cambio de significado entre historias, FR y supuestos? [Consistency, Spec §FR-001, Spec §FR-007, Spec §Assumptions]

## Acceptance Criteria Quality

- [x] CHK012 Son medibles los acceptance scenarios sobre conteo de goles y partidos jugados con datos observables y comparables? [Measurability, Spec §Acceptance Scenarios 3-7]
- [x] CHK013 Esta definido un criterio objetivo para decidir que una correccion "se refleja" en el conteo de goles y bajo que condicion exacta? [Measurability, Spec §Acceptance Scenario 7]
- [ ] CHK014 Es verificable de forma objetiva el criterio de exito SC-002 sin depender de interpretaciones subjetivas del evaluador? [Measurability, Spec §SC-002] — GAP real: SC-002 no define protocolo de la prueba de usabilidad (muestra, criterio de "identificar correctamente"). No bloquea implementacion (no hay tarea automatizada que dependa de esto); queda como deuda de redaccion de la spec.

## Scenario Coverage

- [ ] CHK015 Estan cubiertos de forma explicita los escenarios primarios y alternos para registrar, corregir y consultar alineaciones/estadisticas? [Coverage, Spec §User Story 1, Spec §Acceptance Scenarios] — GAP real: no hay acceptance scenario dedicado a "corregir alineacion" (solo FR-003); resuelto operativamente en `research.md` Decision 4 (409 `lineup_conflicts_with_events`), pero spec.md no tiene el escenario explicito.
- [ ] CHK016 Estan especificados escenarios de excepcion para jugador invalido, partido inexistente y acceso no autorizado con resultados esperados coherentes? [Coverage, Spec §FR-002, Spec §FR-005, Spec §FR-011] — GAP real: "partido inexistente" no tiene escenario propio en spec.md (se resuelve por convencion REST estandar 404 ya usada en specs previas, no por texto explicito de esta spec).
- [x] CHK017 Estan cubiertos escenarios de recuperacion tras correcciones de datos (resultado/evento) para evitar estados ambiguos de estadisticas? [Coverage, Spec §Acceptance Scenario 7, Gap] — Resuelto en `research.md` Decision 6 (recalculo siempre desde `match_events`+`match_lineups`).

## Edge Case Coverage

- [x] CHK018 Esta definido el comportamiento para partido finalizado que nunca tuvo alineacion, incluyendo impacto en partidos jugados del jugador? [Edge Case, Spec §Edge Cases, Spec §Assumptions]
- [x] CHK019 Esta definido que ocurre si una correccion de alineacion excluye a un jugador con gol ya registrado, sin romper coherencia normativa? [Edge Case, Spec §FR-003, Spec §Edge Cases] — Resuelto en `research.md` Decision 4 (rechazo `409 lineup_conflicts_with_events`).

## Non-Functional Requirements

- [x] CHK020 Existen requisitos no funcionales suficientes para asegurar trazabilidad y auditabilidad de cambios que impactan conteos estadisticos? [NFR, Gap]
- [x] CHK021 Estan definidos requisitos de seguridad y privacidad minimos para endpoints publicos de estadisticas sin autenticacion? [NFR, Spec §FR-011, Gap]

## Dependencies & Assumptions

- [x] CHK022 Estan explicitadas y validadas las dependencias con specs 001, 004, 005 y 009 para evitar huecos de contrato entre artefactos? [Dependency, Spec §Dependencies]
- [x] CHK023 Estan documentadas las asunciones operativas de derivacion (eventos/alineaciones) de manera no contradictoria con los FR? [Assumption, Spec §Assumptions, Spec §FR-006, Spec §FR-007]

## Ambiguities & Conflicts

- [x] CHK024 Se resolvio si "correccion de resultado" implica obligatoriamente cambio en eventos de gol o solo en marcador oficial? [Ambiguity, Conflict, Spec §Acceptance Scenario 7, Gap]
- [x] CHK025 Se resolvio si la "ficha del partido" requerida por FR-004 corresponde al endpoint de partido existente, al endpoint de alineacion, o a ambos? [Ambiguity, Spec §FR-004, Gap] — Resuelto en `research.md` Decision 1/2 (`GET /matches/{id}/lineup` + `lineup_status` en la ficha del partido).

## Notes

- Marcar items con [x] solo cuando el criterio de calidad de requisitos este satisfecho.
- Dejar items sin marcar cuando exista ambiguedad, conflicto o falta de cobertura.
- speckit-implement puede leer el estado de checkboxes como gate, pero no debe modificar estos marcadores.
- checklists/requirements.md tiene un ciclo distinto mantenido por speckit-specify y speckit-clarify.
