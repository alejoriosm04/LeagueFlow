# Research: Crear una liga

**Feature**: `002-crear-liga` · **Date**: 2026-08-19

**Sin decisiones de stack.** Lenguaje, framework, ORM, migraciones, testing,
CORS, hosting y CI están fijados en
`specs/001-fundacion-y-autenticacion/research.md` y no se re-deciden aquí
(`AGENTS.md` §5). Este documento cubre solo lo específico de esta HU.

## 1. Dónde se aplica la unicidad de `(name, season)`

**Decision**: restricción `UNIQUE (name, season)` en la base de datos, más una
comprobación previa en el servicio para poder devolver el error de negocio con
el envelope estándar.

**Rationale**: FR-002 exige rechazar la liga duplicada. Solo con la
comprobación en el servicio hay ventana de carrera entre dos organizadores
creando la misma liga a la vez; solo con la restricción de base de datos, el
error llega como excepción de integridad y se traduciría en un 500 genérico en
vez del 409 con `code`/`message` que exige `contracts/conventions.md`. Con
ambas: el camino normal devuelve un 409 legible, y la restricción actúa como
red de seguridad ante la carrera (se captura la violación de integridad y se
traduce al mismo 409).

**Alternatives considered**: solo servicio (descartado: carrera real, y la HU
puede tener dos organizadores); solo constraint (descartado: mensaje de error
no cumple FR-011 de `specs/001-*`).

## 2. Comparación de nombre: sensible o insensible a mayúsculas

**Decision**: unicidad insensible a mayúsculas y a espacios sobrantes —
`"Interfacultades 2026"` y `"interfacultades 2026 "` se consideran la misma
liga. Se normaliza el nombre (trim + colapsar espacios internos) antes de
guardar; se preserva la capitalización que escribió el organizador para
mostrarla.

**Rationale**: el Acceptance Scenario 2 de `spec.md` trata el nombre duplicado
como error de usuario. Si la unicidad fuera sensible a mayúsculas, crear
"Interfacultades 2026" y "INTERFACULTADES 2026" en la misma temporada estaría
permitido y produciría exactamente la confusión que el escenario busca evitar.
Es coherente con la unicidad case-insensitive de `username` ya decidida en
`specs/001-*/data-model.md`.

**Alternatives considered**: unicidad exacta (descartado por lo anterior);
normalizar también a minúsculas al mostrar (descartado: degrada la
presentación sin aportar).

## 3. Alcance de la temporada (`season`)

**Decision**: campo de texto libre obligatorio (ej. `"2026-1"`, `"2026"`,
`"Apertura 2026"`), sin formato impuesto.

**Rationale**: `spec.md` no define un formato y las ligas universitarias usan
convenciones distintas (semestre, año, torneo nombrado). Imponer un formato
sería inventar una regla que la spec no pide — prohibido por el Principio I.
La unicidad opera sobre el par `(name, season)` normalizado, así que un formato
libre no rompe FR-002.
