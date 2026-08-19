# Research: Registrar equipos en una liga

**Feature**: `003-registrar-equipos` · **Date**: 2026-08-19

**Sin decisiones de stack.** Todo el stack está fijado en
`specs/001-fundacion-y-autenticacion/research.md` y no se re-decide aquí
(`AGENTS.md` §5). Este documento cubre solo lo específico de esta HU.

## 1. Validación de `crest_url` (escudo del equipo)

**Decision**: validar que sea una URL absoluta con esquema `https`, con
longitud máxima; **no** verificar que el recurso exista ni que sea una imagen.
El frontend muestra una representación por defecto si la imagen no carga.

**Rationale**: la Assumption de `spec.md` fija que el escudo es un enlace
externo y que la plataforma no aloja archivos. Verificar la existencia del
recurso en el servidor implicaría una petición saliente en cada alta —
lentitud, dependencia de un tercero, y un vector de SSRF (el servidor pidiendo
URLs arbitrarias que envía el usuario). Exigir `https` evita contenido mixto
cuando la app se sirva por HTTPS en producción (Vercel).

**Alternatives considered**: descargar y validar el content-type (descartado
por SSRF y latencia); permitir `http` (descartado: el navegador bloquearía la
imagen como contenido mixto en producción).

## 2. Formato de `colors`

**Decision**: texto libre de hasta 60 caracteres (ej. `"azul/blanco"`), sin
paleta ni formato hex impuesto.

**Rationale**: `spec.md` lo describe como opcional y descriptivo, sin exigir
que la interfaz lo use para pintar nada. Imponer formato hex obligaría a un
selector de color en el formulario y a una regla de validación que la spec no
pide — inventar alcance, prohibido por el Principio I. Si más adelante alguna
HU quiere pintar el color real, será un cambio aditivo con su propia spec.

## 3. Efecto del borrado lógico (`status = inactive`) en las consultas

**Decision**: un equipo `inactive` desaparece de los listados y selectores de
alta (no se puede programar un partido nuevo con él), pero **sigue visible en
todo dato histórico** — partidos ya jugados, clasificación y estadísticas.

**Rationale**: FR-005 exige preservar la integridad histórica de la
clasificación. Si un equipo inactivo desapareciera también del historial, los
partidos que jugó quedarían huérfanos y la tabla de posiciones dejaría de
cuadrar, que es exactamente lo que la regla busca evitar. La distinción
"invisible para operaciones nuevas, visible en el historial" es la única
lectura compatible con esa restricción.

**Alternatives considered**: ocultarlo en todas partes (descartado: rompe el
historial); no ocultarlo en ningún lado (descartado: permitiría seguir
programando partidos de un equipo dado de baja).
