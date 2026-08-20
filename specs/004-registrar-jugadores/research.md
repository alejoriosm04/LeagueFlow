# Research: Registrar jugadores en un equipo

**Feature**: `004-registrar-jugadores` · **Date**: 2026-08-19

**Sin decisiones de stack.** Todo el stack está fijado en
`specs/001-fundacion-y-autenticacion/research.md` y no se re-decide aquí
(`AGENTS.md` §5). Este documento cubre solo lo específico de esta HU.

## 1. Rango y semántica del dorsal (`number`)

**Decision**: entero entre 1 y 99 inclusive cuando se informa; `null` permitido
(jugador sin dorsal). La unicidad `(team_id, number)` solo aplica cuando
`number` no es nulo — varios jugadores del mismo equipo pueden no tener dorsal.

**Rationale**: FR-001 marca el dorsal como opcional y FR-003 solo rechaza
duplicados "cuando el dorsal esté informado". El modelo compartido de `001`
usa el campo `number` (no `jersey`). El rango 1–99 cubre el uso amateur /
universitario sin inventar dorsales especiales (0, 100+) que la spec no pide.
Rechazar fuera de rango con `400` / `validation_error` es coherente con el
envelope de `conventions.md`.

**Alternatives considered**: permitir cualquier entero no negativo (descartado:
abre valores absurdos en UI); exigir dorsal siempre (descartado: contradice
FR-001); unicidad también sobre `null` (descartado: en SQL/Postgres los
`NULL` no colisionan en UNIQUE parcial y FR-003 solo habla del caso
informado).

## 2. Formato de `position`

**Decision**: texto libre de hasta 40 caracteres (ej. `"delantero"`,
`"portero"`), sin catálogo cerrado ni enum.

**Rationale**: `spec.md` lo describe como opcional y descriptivo, sin lista de
posiciones. Imponer un enum (GK/DF/MF/FW) inventaría alcance y obligaría a
traducir etiquetas en la UI — prohibido por el Principio I. Si una HU futura
quiere posiciones tipadas, será un cambio aditivo con su propia spec.

**Alternatives considered**: enum FIFA (descartado: no está en la spec);
campo ausente hasta una HU posterior (descartado: FR-001 ya lo admite como
opcional).

## 3. Efecto del borrado lógico (`status = inactive`) en las consultas

**Decision**: un jugador `inactive` desaparece de la plantilla por defecto y
de los selectores de alta (alineaciones / goles en HUs posteriores), pero
**sigue visible en todo dato histórico** — eventos de gol y alineaciones ya
registradas — y en `GET /players/{id}`.

**Rationale**: FR-005 exige no eliminar jugadores con historial. Si un
jugador inactivo desapareciera también del historial, goles y alineaciones
quedarían huérfanos y las estadísticas dejarían de cuadrar. La distinción
"invisible para operaciones nuevas, visible en el historial" es la misma
lectura que `specs/003-registrar-equipos/research.md` §3 aplica a equipos.

**Alternatives considered**: ocultarlo en todas partes (descartado: rompe el
historial); hard-delete cuando no tiene historial y soft-delete cuando sí
(descartado: dos caminos de borrado sin beneficio de producto en esta HU;
el endpoint de baja siempre marca `inactive`).

## 4. Alta sobre un equipo inactivo

**Decision**: rechazar `POST /teams/{teamId}/players` con `404`
(`team_not_found`) cuando el equipo está `inactive` o no existe. No se
distingue "inexistente" de "dado de baja" en el mensaje al cliente.

**Rationale**: `003` ya oculta equipos inactivos de los selectores de alta
(`research.md` §3 de esa spec). Permitir ampliar la plantilla de un equipo
dado de baja contradice esa semántica. Usar `404` (y no `409`) evita filtrar
existencia cruzada, alineado con `conventions.md`.

**Alternatives considered**: `409 team_inactive` (descartado: filtra estado
interno y no aporta al organizador más que "elige otro equipo"); permitir el
alta (descartado: incoherente con el listado de equipos activos).
