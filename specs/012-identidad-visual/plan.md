# Implementation Plan: Identidad visual y experiencia de usuario consistente

**Branch**: `012-identidad-visual` | **Date**: 2026-08-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/012-identidad-visual/spec.md`

**Nota de alcance**: historia **transversal de presentación**. No re-decide
stack ni modelo de dominio: se rige por `AGENTS.md` §5 y por
[`specs/001-fundacion-y-autenticacion/plan.md`](../001-fundacion-y-autenticacion/plan.md)
y su [`data-model.md`](../001-fundacion-y-autenticacion/data-model.md). Este
plan documenta **solo lo que añade en la capa de presentación** del frontend ya
existente.

## Summary

Dotar a las pantallas ya entregadas (`specs/001`–`009`) de una identidad
visual única y de una experiencia consistente, sin tocar reglas de negocio,
contratos de API, entidades ni esquema (FR-032).

El enfoque técnico: un **sistema de valores visuales** en custom properties de
CSS (`tokens.css`) como fuente única de verdad, un **shell de aplicación**
(cabecera de marca + liga en contexto + estado de sesión + navegación de seis
secciones) que envuelve todas las rutas desde `App.tsx`, y un **catálogo de
ocho componentes** más tres estados de pantalla que las pantallas consumen en
lugar de resolver cada una por su cuenta. Todo con CSS nativo y CSS Modules:
**cero dependencias nuevas**. Las alternativas evaluadas y descartadas
(Tailwind, CSS-in-JS, biblioteca de componentes) están en
[research.md §1](./research.md).

El punto de partida real es que el frontend **no tiene ni un archivo CSS**: el
único estilo son estilos en línea en `App.tsx` (medido en
[research.md §0](./research.md)). La línea base de no regresión son las
**44 pruebas en verde** de Vitest.

## Technical Context

**Language/Version**: TypeScript 5.7 + React 18.3 (heredado de `specs/001`; el
backend no se toca en esta historia)

**Primary Dependencies**: React Router 7, Vite 6 — **ninguna dependencia nueva**.
CSS nativo con custom properties + CSS Modules, ambos ya soportados por Vite sin
configuración

**Storage**: N/A — esta historia no persiste nada (FR-032). La liga en contexto
se deriva de la ruta, no se guarda

**Testing**: Vitest 3 + React Testing Library (`npx vitest run`), con consultas
accesibles por rol y etiqueta. Se añaden dos pruebas de sistema: ratio de
contraste sobre `tokens.css` (SC-004) y auditoría de colores literales en los
`*.module.css` (SC-009). Playwright queda fuera: no está instalado y añadirlo
sería una decisión de stack que `AGENTS.md` §5 no permite tomar aquí

**Target Platform**: navegador web; SPA estática en Vercel (heredado)

**Project Type**: web (frontend + backend separados). **Esta historia solo toca
`frontend/`**

**Performance Goals**: sin regresión perceptible sobre las vistas de consulta ya
entregadas (< 2 s para una liga de 20 equipos / 190 partidos, referencia de
`specs/001`). El sistema visual no añade trabajo en tiempo de ejecución: es CSS
estático, sin runtime de estilos

**Constraints**: contraste ≥ 4.5:1 en todo texto (FR-023); operable solo con
teclado con foco visible (FR-024, FR-025); sin desplazamiento horizontal de
página a 1280/768/375 px (FR-029, FR-030); interfaz íntegramente en español
(FR-021); ningún mensaje del servidor se muestra sin traducir (FR-015); las 44
pruebas existentes siguen en verde (FR-033)

**Scale/Scope**: 8 pantallas de consulta y 9 formularios ya implementados
(FR-031), 6 secciones de navegación, 8 componentes de catálogo, 3 estados de
pantalla. Tema claro único; sin modo oscuro ni i18n (Out of Scope)

**Unknowns**: ninguno. Cero marcadores `NEEDS CLARIFICATION`: la spec llegó con
16/16 ítems de su checklist en verde y con las decisiones abiertas resueltas
como *Assumptions* explícitas.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio / regla | Estado | Cómo se cumple |
|---|---|---|
| I. La Especificación Manda | PASS | Cada componente y cada token de este plan responde a un FR de `spec.md`; la trazabilidad está en [data-model.md §7](./data-model.md) |
| II. Toda Regla de Negocio se Prueba | PASS (no aplica ampliar) | Esta historia **no introduce reglas de negocio** (FR-032). Las reglas existentes conservan sus pruebas intactas; lo que sí se prueba con Vitest es el comportamiento observable que sí introduce: shell, sección activa, estados, bloqueo de reenvío, contraste y auditoría de tokens |
| III. Contratos de API Explícitos | PASS | No se crea, modifica ni versiona ningún contrato HTTP. El frontend sigue consumiendo `specs/001`–`009` tal cual; se versiona en cambio el contrato de la otra frontera, la de componentes: [contracts/ui-contracts.md](./contracts/ui-contracts.md) |
| IV. No Romper lo que ya Funciona | PASS | Línea base de 44 pruebas en verde; FR-033 obliga a mantenerlas y prohíbe borrarlas, saltarlas o debilitarlas. Los selectores que rompa el remarcado se migran **hacia** consultas por rol y etiqueta ([research.md §9](./research.md)) |
| V. Migraciones Versionadas | PASS (no aplica) | Cero cambios de esquema y cero migraciones; el diff sobre `backend/` debe ser vacío (verificable, [quickstart.md](./quickstart.md)) |
| VI. Cero Secretos en el Repositorio | PASS | No se añaden variables de entorno ni credenciales; no se alojan activos externos ni claves de fuentes |
| VII. Código de IA con la Misma Vara | PASS | `npm run lint`, `npm run build` y `npx vitest run` son el mismo gate que para el resto del código |
| VIII. Entregabilidad Independiente por Dominio | PASS | La capa de presentación no cruza dominios de backend. El orden de tareas por prioridad (P1 shell → P5 adaptabilidad) deja la aplicación entregable al final de cada prioridad |
| Arquitectura: monolito modular | PASS | Un solo frontend SPA; no se añaden procesos, servicios ni build steps |
| Regla de Derivación de Estadísticas | PASS | La clasificación se sigue **mostrando**, nunca editando; esta historia solo cambia cómo se ve |
| Estándares de Seguridad: sin stack traces al cliente | PASS (refuerza) | El catálogo de mensajes por `code` garantiza que ningún texto del servidor llegue crudo a la pantalla (FR-015, SC-003) |
| Estándares de Seguridad: sanitización / XSS | PASS | Todo el contenido de usuario (nombres de equipo, liga, jugador) se renderiza como texto de React; **no se usa `dangerouslySetInnerHTML`** en ningún componente del catálogo |

Sin violaciones. **Complexity Tracking no aplica** (tabla vacía al final, a
propósito).

*Re-check post Phase 1*: el diseño de [data-model.md](./data-model.md) y
[contracts/ui-contracts.md](./contracts/ui-contracts.md) no introdujo ninguna
entidad, ningún endpoint ni ninguna dependencia. El único elemento que tensionó
un gate fue la **liga en contexto**: se resolvió como valor derivado de la ruta,
sin persistencia ni estado global, reforzando el Principio III en vez de
esquivarlo. **PASS confirmado.**

## Project Structure

### Documentation (this feature)

```text
specs/012-identidad-visual/
├── plan.md                      # este archivo
├── research.md                  # Phase 0 — decisiones de la capa de presentación
├── data-model.md                # Phase 1 — tokens, shell, catálogo, estados (nada persistido)
├── contracts/
│   └── ui-contracts.md          # Phase 1 — contrato de componentes (no hay contrato de API)
├── quickstart.md                # Phase 1 — guía de validación
├── checklists/
│   └── requirements.md          # 16/16 en verde
└── tasks.md                     # Phase 2 (/speckit-tasks — aún no generado)
```

### Source Code (repository root)

Solo `frontend/`. `backend/` no se toca.

```text
frontend/
├── index.html                       # (sin cambios; lang="es" ya presente)
├── src/
│   ├── main.tsx                     # + import único de styles/tokens.css y styles/global.css
│   ├── App.tsx                      # los estilos en línea salen; envuelve las rutas en <AppShell>
│   ├── routes.tsx                   # + rutas de las secciones pendientes (Dashboard, Estadísticas)
│   ├── styles/                      # NUEVO
│   │   ├── tokens.css               #   fuente única de color/tipografía/espaciado/radio/sombra
│   │   └── global.css               #   reset mínimo, tipografía base, :focus-visible
│   ├── components/                  # NUEVO — catálogo compartido (specs/001 ya reservó la carpeta)
│   │   ├── index.ts
│   │   ├── layout/
│   │   │   ├── AppShell.tsx + .module.css
│   │   │   ├── secciones.ts
│   │   │   ├── IndicadorDeLiga.tsx
│   │   │   ├── EstadoDeSesion.tsx
│   │   │   ├── useLigaEnContexto.ts
│   │   │   └── PendienteDeEntrega.tsx
│   │   ├── datos/
│   │   │   ├── Panel.tsx | TablaDeDatos.tsx | FilaDeMarcador.tsx
│   │   │   ├── DistintivoDeEstado.tsx | DestacadoDePodio.tsx | EscudoEquipo.tsx
│   │   ├── formulario/
│   │   │   ├── Boton.tsx | CampoDeFormulario.tsx
│   │   ├── estado/
│   │   │   ├── EstadoCarga.tsx | EstadoVacio.tsx | EstadoError.tsx
│   │   └── __tests__/               # pruebas del catálogo, tokens y contraste
│   ├── lib/                         # NUEVO
│   │   ├── formato.ts               #   fecha, hora, marcador, diferencia, iniciales
│   │   └── mensajesDeError.ts       #   code del envelope -> español
│   ├── features/                    # se restilan; su lógica y sus llamadas NO cambian
│   │   ├── auth/ leagues/ teams/ players/ matches/ standings/ events/
│   └── services/apiClient.ts        # sin cambios
└── e2e/                             # sigue vacío a propósito (research.md §9)
```

**Structure Decision**: se conserva la estructura "Web application" fijada por
`specs/001` y se **rellenan dos carpetas que ese plan ya había reservado y que
todavía estaban vacías**: `src/components/` ("UI compartida") y, junto a ella,
`src/lib/` y `src/styles/` para las utilidades y los valores transversales. Las
carpetas de `src/features/` no se reorganizan: cada pantalla sigue donde está y
solo cambia su marcado y sus importaciones. Es la mínima estructura que permite
que `specs/010` y `specs/011` construyan sin decidir estilo (SC-010).

## Alcance por pantalla (FR-031)

Pantallas existentes que esta historia restila. Ninguna cambia su lógica, sus
llamadas ni sus reglas.

| Pantalla | Archivo | Qué recibe |
|---|---|---|
| Inicio de sesión | `features/auth/LoginPage.tsx` | Shell, `CampoDeFormulario`, `Boton` con bloqueo de reenvío, error traducido |
| Ligas (listado) | `features/leagues/LeaguesPage.tsx` | `Panel`, `TablaDeDatos`, tres estados |
| Liga (detalle) | `features/leagues/LeagueDetailPage.tsx` | `Panel`, liga en contexto en la cabecera |
| Liga (creación) | `features/leagues/CreateLeagueForm.tsx` | Formulario del catálogo |
| Equipos (listado/creación) | `features/teams/TeamsPage.tsx`, `CreateTeamForm.tsx` | `TablaDeDatos`, `EscudoEquipo`, estado vacío según rol |
| Jugadores (listado/creación) | `features/players/PlayersPage.tsx`, `CreatePlayerForm.tsx` | `TablaDeDatos`, formulario del catálogo |
| Partidos y calendario | `features/matches/MatchesPage.tsx` | `FilaDeMarcador`, `DistintivoDeEstado`, formato de fecha compartido |
| Partido (detalle) | `features/matches/MatchDetailPage.tsx` | `FilaDeMarcador`, `Panel`, liga en contexto vía `league_id` |
| Resultado y correcciones | `features/matches/ResultForm.tsx`, `CorrectionRequestForm.tsx`, `CorrectionDecisionForm.tsx` | Formularios del catálogo, errores por campo |
| Programar partido | `features/matches/CreateMatchForm.tsx` | Formulario del catálogo |
| Registro de goles | `features/events/GoalForm.tsx` | Formulario del catálogo, bloqueo de reenvío |
| Clasificación | `features/standings/StandingsPage.tsx` | `TablaDeDatos` con numéricos a la derecha y `DestacadoDePodio` |

## Orden de entrega

Alineado con las prioridades de la spec; cada bloque deja la aplicación
entregable:

1. **P1 — Fundación + shell**: `tokens.css`, `global.css`, `AppShell`,
   secciones, liga en contexto, secciones pendientes. Cubre FR-001 a FR-006,
   FR-019 a FR-021, FR-027 y SC-001.
2. **P2 — Catálogo de datos**: `Panel`, `TablaDeDatos`, `FilaDeMarcador`,
   `DistintivoDeEstado`, `DestacadoDePodio`, `EscudoEquipo`, `formato.ts`.
   Cubre FR-007 a FR-012 y FR-022.
3. **P3 — Estados y formularios**: `EstadoCarga`/`EstadoVacio`/`EstadoError`,
   `Boton`, `CampoDeFormulario`, `mensajesDeError.ts`, y su aplicación a todas
   las pantallas del alcance. Cubre FR-013 a FR-018 y SC-002/SC-003.
4. **P4 — Accesibilidad**: recorrido de teclado, foco visible, prueba de
   contraste y auditoría de tokens. Cubre FR-023 a FR-028 y SC-004/SC-005/SC-009.
5. **P5 — Adaptabilidad**: media queries, navegación colapsable y tablas con
   desplazamiento propio. Cubre FR-029, FR-030 y SC-006.

6. **P6 — Portada y expresividad visual** (ampliación posterior a la primera
   pasada): tokens de marca y acento, degradados y elevaciones en `tokens.css`;
   `features/inicio/Portada`; navegación sin secciones deshabilitadas cuando no
   hay liga; acabado compartido de superficies. Cubre FR-006 reescrito y
   FR-034 a FR-039, SC-011 y SC-012.

7. **P6b — Marco de aplicación sobre la maqueta de referencia** (segunda
   ampliación): el equipo aportó `LeagueFlow Wow` (Claude Design) como
   referencia de disposición y color. `AppShell` pasa a un marco único —
   lienzo claro, superficie de marca, barra lateral con icono propio por
   sección, cabecera translúcida, contenido como superficie clara elevada— y
   la portada gana un selector de ligas real. Cubre FR-006 (conducta ya fijada
   en P6), FR-040 a FR-046, SC-013 y SC-014.

La migración de selectores de prueba (FR-033) no es un bloque aparte: ocurre
dentro del bloque que rompe cada selector.

**Sobre P6b.** La maqueta de referencia (`LeagueFlow Wow`) es orientación de
disposición y color, no un inventario de funcionalidad: buscador global,
campana de notificaciones y las tarjetas de dashboard con datos agregados que
dibuja no se implementan porque no hay contrato de API que los sirva
(FR-032/FR-035) — ver spec.md, Assumption "Maqueta de referencia del marco". El
marco reutiliza el `<h1>` y los `Panel` que ya tenía cada pantalla: ninguna
pantalla de negocio cambió una línea para vivir dentro de él.

**Sobre P6.** Nace de una revisión visual con el equipo: la primera pasada
cumplía la estructura del mockup de `docs/enunciado.md` §2 pero se leía plana.
No re-decide nada del stack ni del modelo (`AGENTS.md` §5) y no toca `backend/`
(FR-032): es exclusivamente capa de presentación. La estructura del mockup se
respeta — cabecera de marca, navegación lateral de seis secciones, contenido en
paneles; lo que cambia es el acabado.

## Complexity Tracking

*Sin violaciones que justificar — tabla vacía a propósito.*
