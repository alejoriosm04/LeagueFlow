# Research: Registrar y corregir el resultado de un partido

**Feature**: `006-registrar-resultado` · **Date**: 2026-08-19

**Sin decisiones de stack.** Se heredan los artefactos de 001 y las
convenciones de API. Estas decisiones cubren únicamente los bordes de esta HU.

## 1. Corrección propuesta idéntica al marcador vigente

**Decision**: permitir crear y aprobar una corrección cuyo marcador propuesto
sea idéntico al actual. La solicitud conserva su ciclo y auditoría normal.

**Rationale**: la spec exige que el marcador propuesto sea válido y que toda
corrección quede auditada, pero no exige que cambie. Rechazarla inventaría una
regla. Aprobarla es idempotente sobre `Match` y deja evidencia de la revisión.

**Alternatives considered**: rechazar al crear o aprobar con `409` (regla
ausente); cerrar automáticamente (elude FR-007 y FR-012).

## 2. Resultado y correcciones bajo concurrencia

**Decision**: cada transición usa una transacción con bloqueo de `Match` o
actualización condicional por estado. Solo `scheduled` pasa a `finished`; un
segundo escritor recibe `409 result_already_recorded`. Un índice único parcial
PostgreSQL sobre `match_id WHERE status = 'pending'` protege FR-011. Una
decisión actualiza solo una solicitud aún `pending`.

**Rationale**: una comprobación previa aislada sufre TOCTOU. La condición de
estado más la restricción de BD hacen cumplir FR-003, FR-007 y FR-011 aun con
peticiones simultáneas.

**Alternatives considered**: validar solo en Python (carrera); bloqueo global
(serializa partidos independientes); añadir versión a `Match` (campo no
requerido cuando la condición de estado basta).

## 3. Clasificación mientras una corrección está pendiente

**Decision**: el marcador vigente de `Match` sigue siendo la fuente de verdad.
Una solicitud `pending` no altera el partido ni la futura clasificación; solo
una aprobación sustituye el marcador en la misma transacción.

**Rationale**: FR-006 conserva el marcador mientras la solicitud está
pendiente, y 008 deriva exclusivamente de partidos `finished`.

**Alternatives considered**: excluir temporalmente el partido (contradice que
siga finalizado); mostrar el marcador propuesto (aplica algo no aprobado).

## 4. Forma de las operaciones HTTP

**Decision**: `PUT /matches/{matchId}/result`, `POST/GET
/matches/{matchId}/result-corrections`, y `POST
/result-corrections/{correctionId}/decision`. La decisión usa
`approved|rejected`; `decision_reason` es obligatorio al rechazar. El historial
GET es público, igual que el detalle del partido en 005.

**Rationale**: `PUT` expresa la asignación única del resultado; sobre
`finished` devuelve conflicto y dirige al flujo explícito. Una operación de
decisión limita estados y evita lógica duplicada. El historial público cumple
FR-010 desde la ficha pública y solo expone la auditoría exigida por la spec.

**Alternatives considered**: `PATCH /matches/{id}` (confunde registro con
sobrescritura); endpoints `approve`/`reject` separados (duplicación); historial
autenticado (006 no exige restringir la consulta pública heredada de 005).

## 5. Motivos y separación de funciones

**Decision**: `reason` se recorta y debe contener al menos un carácter. En una
decisión `rejected`, `decision_reason` cumple lo mismo; al aprobar se omite. El
servidor deriva autores de la sesión. Conforme al modelo compartido de 001,
quien decide es un organizador distinto del solicitante tanto al aprobar como
al rechazar.

**Rationale**: FR-005 y FR-009 declaran motivos obligatorios; whitespace no es
un motivo. FR-012 y el escenario 8 prohíben al solicitante aprobar o rechazar,
en línea con `decided_by != requested_by` del modelo central.

**Alternatives considered**: aceptar espacios (evade obligatoriedad); permitir
autorrechazo (contradice FR-012 y el modelo de 001); límites máximos arbitrarios
(no están especificados).

## 6. Estados admitidos para el resultado inicial

**Decision**: únicamente `scheduled` admite el registro inicial. `in_progress`
y `cancelled` responden `409 match_not_scheduled`; `finished` responde `409
result_already_recorded` para dirigir al flujo de corrección.

**Rationale**: FR-013 hace explícita la precondición que antes solo aparecía en
el escenario feliz. Evita inventar una transición desde estados reservados o
terminales del modelo compartido.

**Alternatives considered**: permitir `in_progress` (no existe una transición
definida por la spec); reabrir `cancelled` (contradice su carácter terminal).
