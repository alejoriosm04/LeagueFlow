<!--
SYNC IMPACT REPORT
==================
Version change: sin versión (plantilla sin ratificar) -> 1.0.0
Bump rationale: MAJOR inicial — primera ratificación del documento. El archivo
previo era el andamio de Spec Kit con placeholders, sin principios definidos.

Principios definidos (todos nuevos, 8 en total; la plantilla base traía 5 slots):
  - [PRINCIPLE_1_NAME] -> I. La Especificación Manda (NO NEGOCIABLE)
  - [PRINCIPLE_2_NAME] -> II. Toda Regla de Negocio se Prueba
  - [PRINCIPLE_3_NAME] -> III. Contratos de API Explícitos
  - [PRINCIPLE_4_NAME] -> IV. No Romper lo que ya Funciona (NO NEGOCIABLE)
  - [PRINCIPLE_5_NAME] -> V. Migraciones Versionadas
  - (nuevo)            -> VI. Cero Secretos en el Repositorio (NO NEGOCIABLE)
  - (nuevo)            -> VII. El Código de IA se Mide con la Misma Vara
  - (nuevo)            -> VIII. Entregabilidad Independiente por Dominio

Secciones añadidas:
  - [SECTION_2_NAME]   -> Arquitectura de Referencia y Estándares de Seguridad
  - [SECTION_3_NAME]   -> Flujo de Desarrollo y Quality Gates
  - Governance         -> procedimiento de enmienda, versionado y cumplimiento

Secciones eliminadas: ninguna.

Follow-up TODOs: ninguno. No quedan placeholders sin resolver.
-->

# LeagueFlow Constitution

LeagueFlow es una plataforma de gestión y analítica de ligas deportivas amateur.
Esta constitución define las reglas no negociables del proyecto. Cuando cualquier
otro documento (`AGENTS.md`, `CLAUDE.md`, `docs/flujo-sdd.md`) choque con ella,
manda la constitución.

## Core Principles

### I. La Especificación Manda (NO NEGOCIABLE)

Todo comportamiento del sistema DEBE originarse en una especificación antes de
implementarse. No se escribe código sin una Historia de Usuario con sus acceptance
criteria definidos en `specs/NNN-*/spec.md`.

- Un Pull Request con código pero sin su carpeta `specs/NNN-*` correspondiente DEBE
  ser rechazado.
- Si falta información para implementar, se pregunta o se registra como *Assumption*
  explícita en la spec. NUNCA se inventa la regla directamente en el código.
- Los acceptance criteria DEBEN ser verificables: cada uno se puede traducir a una
  prueba automatizada o a un paso de verificación manual reproducible.

**Rationale:** el entregable evaluable del proyecto es la trazabilidad spec → plan →
tasks → código. Código sin spec destruye esa trazabilidad y hace imposible auditar
por qué el sistema se comporta como se comporta.

### II. Toda Regla de Negocio se Prueba

Toda regla de negocio DEBE tener al menos una prueba automatizada que la verifique:
`pytest` en el backend, `Vitest` en el frontend.

- Una regla de negocio es cualquier restricción, cálculo o decisión del dominio
  (cupos de un torneo, validez de un resultado, cálculo de puntos, elegibilidad de
  un jugador). No es "regla de negocio" el cableado de framework ni el maquetado.
- Las pruebas DEBEN afirmar el comportamiento descrito en los acceptance criteria,
  no la implementación interna.
- Un acceptance criterion sin prueba asociada DEBE justificarse por escrito en el PR;
  la justificación "no me dio tiempo" no es válida.

**Rationale:** las reglas del dominio deportivo (puntajes, desempates, sanciones) son
donde más caro sale un error silencioso y donde más fácil es introducir regresiones al
refactorizar.

### III. Contratos de API Explícitos

Backend y frontend DEBEN comunicarse únicamente a través de contratos de API definidos
explícitamente (OpenAPI/schema), versionados en `specs/NNN-*/contracts/`.

- El frontend NUNCA asume detalles de implementación interna del backend (nombres de
  tablas, estructura del ORM, orden de queries).
- Un cambio incompatible en un contrato DEBE documentarse en la spec de la HU que lo
  introduce y DEBE actualizar el schema en el mismo PR.
- Los tipos del cliente se derivan del contrato, no se transcriben a mano cuando exista
  una vía de generación disponible.

**Rationale:** el contrato es la frontera que permite que frontend y backend avancen en
paralelo, y es lo que hace que las pruebas de integración signifiquen algo.

### IV. No Romper lo que ya Funciona (NO NEGOCIABLE)

Ninguna Historia de Usuario se considera terminada si rompe pruebas existentes.

- La suite completa DEBE estar en verde antes de mezclar un PR a `main`.
- Está PROHIBIDO borrar, saltar (`skip`/`xfail`) o debilitar una prueba existente para
  hacer pasar el pipeline. Si una prueba quedó obsoleta por un cambio de requisito
  legítimo, el cambio de requisito DEBE estar escrito en la spec y el PR DEBE explicar
  por qué la prueba cambia.
- Los merges a `main` son siempre por Pull Request. NUNCA `git push --force` ni push
  directo a `main`.

**Rationale:** el valor de una suite de pruebas es exactamente su credibilidad. Una
prueba desactivada para "desbloquear" un merge convierte toda la suite en decoración.

### V. Migraciones Versionadas

Cualquier cambio de esquema de base de datos DEBE entrar como una migración versionada
y commiteada junto a la HU que lo requiere.

- Están PROHIBIDAS las modificaciones manuales directas sobre cualquier base de datos
  (desarrollo, staging o producción).
- Cada migración DEBE ser reproducible desde cero sobre una base vacía.
- Los datos semilla (seeds) para desarrollo se mantienen separados de las migraciones
  de esquema.

**Rationale:** sin migraciones versionadas, el esquema real deja de estar en el repo y
cada máquina del equipo termina con una base distinta e irreproducible.

### VI. Cero Secretos en el Repositorio (NO NEGOCIABLE)

NUNCA se escriben secretos ni credenciales en el código: ni API keys, ni cadenas de
conexión, ni tokens, ni contraseñas — tampoco en ejemplos, tests, fixtures o comentarios.

- Todo secreto vive en variables de entorno.
- Cada llave nueva DEBE documentarse, vacía, en `.env.example`.
- `.env` NUNCA se commitea.
- Si un secreto llega a commitearse, DEBE rotarse inmediatamente; borrar el commit no
  es suficiente.

**Rationale:** un secreto en el historial de git es un secreto comprometido de forma
permanente. GitHub tiene push protection activo y rechazará el push, pero la regla
existe independientemente de que la herramienta la detecte.

### VII. El Código de IA se Mide con la Misma Vara

Todo código generado por IA DEBE cumplir exactamente los mismos criterios de calidad,
linting y cobertura de pruebas que el código escrito manualmente.

- El autor humano del PR es responsable del código que mezcla, sin importar quién o qué
  lo escribió.
- Está PROHIBIDO mezclar código generado que el autor no entiende o no puede explicar
  en la revisión.
- La IA no es excusa para saltarse el Principio I: generar código sigue requiriendo una
  spec previa.

**Rationale:** el proyecto se construye con asistentes de IA por diseño. Aceptar un
estándar de calidad menor para ese código convertiría la velocidad inicial en deuda
técnica no auditable.

### VIII. Entregabilidad Independiente por Dominio

Cada Historia de Usuario DEBE poder desplegarse de forma independiente sin romper
funcionalidades ya existentes.

- Los dominios del sistema son: **League, Team, Player, Match, Statistics**. Cada
  módulo expone una interfaz explícita; el acceso entre dominios ocurre por esa
  interfaz, nunca alcanzando tablas o modelos internos de otro dominio.
- Una HU que exige desplegar simultáneamente varios cambios acoplados DEBE dividirse,
  o DEBE entregar el cambio detrás de una bandera de activación.
- Ningún módulo puede introducir dependencias circulares con otro módulo.

**Rationale:** la separación por dominios es lo que permite que varios integrantes
trabajen HU distintas en paralelo sin bloquearse ni pisarse.

## Arquitectura de Referencia y Estándares de Seguridad

### Arquitectura

La arquitectura del sistema es un **monolito modular**, NO microservicios:

- Frontend: React/TypeScript o Next.js.
- API Backend.
- Base de datos: PostgreSQL.

Proponer microservicios, colas o servicios separados requiere una enmienda a esta
constitución con justificación explícita.

### Modelo de Dominio Central

```
League -> Teams -> Players
League -> Matches -> MatchEvents
```

### Regla de Derivación de Estadísticas (NO NEGOCIABLE)

Las estadísticas y la tabla de posiciones (Standings) SIEMPRE se derivan de los
resultados de los partidos:

```
MatchResult -> StandingsCalculator -> Standings
```

- Está PROHIBIDO editar directamente una tabla de posiciones o un conteo de
  estadísticas por cualquier vía: endpoint, panel de administración, script o SQL.
- Corregir una posición o una estadística se hace corrigiendo el `MatchResult` o el
  `MatchEvent` de origen y recalculando.
- Si los Standings se almacenan materializados por rendimiento, DEBEN ser
  reconstruibles por completo desde los resultados, y esa reconstrucción DEBE estar
  cubierta por pruebas.

**Rationale:** una tabla de posiciones editable a mano es una tabla en la que nadie
puede confiar; la única fuente de verdad son los partidos jugados.

### Estándares de Seguridad Obligatorios

Todo endpoint y todo PR DEBEN cumplir:

- **Validación de payloads:** toda entrada externa se valida contra un schema antes de
  llegar a la lógica de negocio.
- **Sanitización de entradas:** todo contenido de usuario que se renderiza o persiste
  se sanitiza contra inyección (XSS incluido).
- **SQL parametrizado / ORM:** NUNCA SQL construido por concatenación de strings.
- **CORS restringido:** lista explícita de orígenes permitidos. NUNCA `*` en entornos
  desplegados.
- **Secretos por variables de entorno:** ver Principio VI.
- **Sin stack traces al cliente:** los errores devuelven un mensaje seguro y un
  identificador; el detalle va a los logs del servidor.
- **Dependencias escaneadas en CI:** el pipeline ejecuta escaneo de vulnerabilidades de
  dependencias, y las vulnerabilidades críticas bloquean el merge.

## Flujo de Desarrollo y Quality Gates

### Ciclo por Historia de Usuario

Una HU = una rama = una carpeta en `specs/` = un Pull Request.

```
/speckit-specify  -> specs/NNN-*/spec.md      (el QUÉ)
/speckit-clarify  -> resuelve ambigüedades
/speckit-plan     -> plan.md, data-model.md, contracts/   (el CÓMO)
/speckit-tasks    -> tasks.md
/speckit-analyze  -> consistencia spec <-> plan <-> tasks
/speckit-implement-> código
```

La rama se crea manualmente y DEBE llevar el mismo número que la spec (`NNN-slug`),
para que rama, spec y PR queden alineados.

### Convenciones de Commits y PRs

- Conventional Commits con el número de la HU en el scope: `feat(003): registro de
  equipos`.
- El repo usa **squash merge** únicamente: el título del PR se convierte en el commit
  que queda en `main`. El título DEBE seguir `tipo(NNN): descripción en imperativo, en
  minúscula`. Están PROHIBIDOS títulos genéricos ("cambios", "update", "WIP").
- El cuerpo del PR DEBE enlazar `specs/NNN-*/spec.md` e incluir el checklist de
  acceptance criteria.
- El spec se commitea junto con el código que genera, en el mismo PR.

### Quality Gates (bloquean el merge)

Un Pull Request NO puede mezclarse si falla cualquiera de estos:

1. Existe la spec de la HU y el PR la enlaza (Principio I).
2. Las reglas de negocio nuevas tienen pruebas (Principio II).
3. La suite completa de pruebas está en verde (Principio IV).
4. El linter pasa, sin excepciones silenciosas (Principio VII).
5. Los cambios de esquema vienen como migración versionada (Principio V).
6. No hay secretos en el diff (Principio VI).
7. El escaneo de dependencias no reporta vulnerabilidades críticas.
8. Al menos una revisión humana aprobada.

## Governance

Esta constitución supersede cualquier otra práctica, documento o convención del
proyecto. `AGENTS.md`, `CLAUDE.md` y `docs/flujo-sdd.md` son documentos operativos
subordinados a ella.

**Procedimiento de enmienda.** Toda enmienda DEBE entrar por Pull Request dedicado que
incluya: (a) el texto exacto que cambia, (b) la justificación del cambio, (c) el bump
de versión propuesto con su razonamiento, y (d) el plan de migración si la enmienda
invalida código o specs existentes. La enmienda requiere la aprobación de la mayoría
del equipo antes de mezclarse.

**Política de versionado.** La constitución usa versionado semántico:

- **MAJOR:** se elimina o redefine un principio de forma incompatible con lo anterior.
- **MINOR:** se añade un principio o una sección, o se expande materialmente una guía.
- **PATCH:** aclaraciones, redacción, correcciones tipográficas sin cambio semántico.

**Cumplimiento.** Cada revisión de PR DEBE verificar el cumplimiento de los Quality
Gates listados arriba. Cualquier complejidad que se aparte de la arquitectura de
referencia DEBE justificarse explícitamente en `plan.md`, en la sección de desviaciones;
sin justificación escrita, la desviación se revierte. Las excepciones temporales DEBEN
tener fecha de vencimiento y una tarea de seguimiento registrada.

**Version**: 1.0.0 | **Ratified**: 2026-08-18 | **Last Amended**: 2026-08-18
