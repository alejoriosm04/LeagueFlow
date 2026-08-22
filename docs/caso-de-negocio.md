# Caso de negocio y comparativa de costos

Componente complementario del entregable. Se llena **con datos reales medidos
durante el proyecto**, no estimados al final: por eso conviene ir registrando
tiempos desde la primera HU.

> **Pitch de ventas** (versión presentable de este documento, para Demo Day):
> `docs/pitch-sdd.html` — publicado como Artifact en
> <https://claude.ai/code/artifact/00513ce6-3706-425d-8a5c-791be8300b77>.
> Este archivo es la fuente de verdad numérica; el pitch solo lo resume.

## 1. Métricas por HU (se llenan solas sobre la marcha)

Cada HU deja su archivo en `docs/metricas/NNN-slug.md` al cerrarse — el agente
lo escribe como parte del ciclo de la HU (`AGENTS.md` §7), y la persona añade
dos números que el agente no puede conocer (tiempo real de trabajo y costo de
IA). La tabla de abajo la genera `./scripts/metricas.sh --escribir` a partir de
esos archivos más `git log`.

**No editar la tabla a mano**: se regenera. Ver `docs/metricas/README.md` para
qué dato es automático, cuál es aproximado y cuál requiere a una persona.

<!-- METRICAS:INICIO (generado por scripts/metricas.sh — no editar a mano) -->

| HU | Tareas (hechas/total) | Tests | Ciclos corrección | Tiempo spec+plan+tasks | Tiempo implement | Costo IA | Días calendario | Commits |
|---|---|---|---|---|---|---|---|---|
| 001-fundacion-y-autenticacion | 41/41 | 21 / 21 | 10 | <pendiente> | <pendiente> | <pendiente, del panel de uso> | 0.7 | 4 |
| 002-crear-liga | 16/16 | 25 / 25 | 4 | <ej. 45 min> | <ej. 2 h> | <del panel de uso de tu herramienta> | 0.8 | 4 |
| 003-registrar-equipos | 15/15 | 26 / 26 | 3 | <ej. 45 min> | <ej. 2 h> | <del panel de uso de tu herramienta> | 0.8 | 4 |
| 004-registrar-jugadores | 14/15 | 26 / 26 (21 backend + 5 frontend) | 1 | <ej. 45 min> | <ej. 2 h> | <del panel de uso de tu herramienta> | 0.9 | 3 |
| 005-programar-partido | 14/15 | 21 / 21 (16 backend + 5 frontend) | 1 | <ej. 45 min> | <ej. 2 h> | <del panel de uso de tu herramienta> | 0.9 | 3 |
| 006-registrar-resultado | 24/24 | 116 backend + 27 frontend | 3 | <ej. 45 min> | <ej. 2 h> | <del panel de uso de tu herramienta> | 1.0 | 3 |
| 007-consultar-calendario | 18/18 | 127 backend + 32 frontend | 3 | <ej. 45 min> | <ej. 2 h> | <del panel de uso de tu herramienta> | 1.1 | 3 |
| 008-consultar-clasificacion | 22/22 | 163 backend (74 unit+contrato, 89 integración) + 38 frontend | 6 | <ej. 45 min> | <ej. 2 h> | <del panel de uso de tu herramienta> | 1.7 | 3 |
| 009-registrar-goles | 23/23 | 169 backend (76 unit+contrato, 93 integración) + 38 frontend | 5 | <ej. 45 min> | <ej. 2 h> | <del panel de uso de tu herramienta> | 1.7 | 3 |
| 010-alineaciones-estadisticas | 23/29 | Frontend: 52/52 (`npx vitest run`, suite completa). Backend: no ejecutable en este entorno (sin PostgreSQL); revisados manualmente y verificados por lint, `ruff check`/`format`, compilación y generación del schema OpenAPI de la app viva | 4 | <ej. 45 min> | <ej. 2 h> | <del panel de uso de tu herramienta> | 1.9 | 4 |
| 011-dashboard-liga | 18/19 | Backend: 217 recolectados, 215 en verde localmente (12 nuevos del dashboard incluidos); 2 fallos preexistentes, ajenos a esta HU (ver Observaciones). Frontend: 51 en verde (7 nuevos) | 7 | <ej. 45 min> | <ej. 2 h> | <del panel de uso de tu herramienta> | 2.0 | 3 |

> `⬜` = falta `docs/metricas/<spec>.md`. **Días calendario** y **commits**
> salen de `git log` y miden tiempo transcurrido, no esfuerzo: el esfuerzo
> real son las columnas de tiempo, que aporta cada persona al cerrar su HU.
> Regenerar con `./scripts/metricas.sh --escribir`.

<!-- METRICAS:FIN -->

### 1.1 Agregados del proyecto (datos duros, no supuestos)

Todo lo de esta tabla sale de `git log`, de `docs/metricas/*.md` y de correr la
suite. Es la única base empírica del caso; los supuestos económicos vienen
después y están marcados como tales.

| Indicador | Valor | Origen |
|---|---|---|
| HU cerradas con métricas | 12 (`001`–`012`) | `docs/metricas/` |
| Specs escritas (incl. bloque paralelo `013`–`017`) | 17 | `specs/` |
| Tareas planificadas / completadas | 342 / 330 (96,5 %) | `tasks.md` de cada HU |
| Ciclos de corrección registrados | 73 | `docs/metricas/*.md` |
| Ciclos de corrección que llegaron a producción | 0 | los 73 están descritos y cerrados antes del merge |
| Pruebas automatizadas en verde | ~414 (217 backend + 197 frontend) | suite completa tras `012` |
| Líneas de código (`.py`, `.ts`, `.tsx`, `.css`) | 18.348 | `git ls-files` |
| Personas | 6 | `git shortlog` |
| Días calendario | 5 (2026-08-17 → 2026-08-21) | `git log` |

Dos cifras merecen leerse juntas: **73 reprocesos** y **0 en producción**. SDD
no evita el error — lo hace ocurrir temprano, con nombre y apellido escrito en
`docs/metricas/`. Ese desplazamiento es el que se monetiza en §5 y §6.

## 2. Costos de infraestructura

### 2.1 Hoy — capa gratuita y licenciamiento estudiantil

| Servicio | Uso | Plan | Costo/mes | Límite del plan gratuito |
|---|---|---|---|---|
| Hosting frontend | Vercel — `leagueflow-pdms2.vercel.app` | Hobby | USD 0 | 100 GB de ancho de banda; proyectos no comerciales |
| Backend / API | Railway — `leagueflow-production.up.railway.app` | Trial / crédito estudiantil | USD 0 | USD 5 de crédito mensual; el servicio duerme al agotarlo |
| Base de datos | PostgreSQL gestionado en Railway | Incluido en el crédito | USD 0 | Comparte el mismo crédito de USD 5 |
| CI/CD | GitHub Actions | Free | USD 0 | 2.000 min/mes en repos privados |
| Repositorio, protección de rama, secret scanning | GitHub | Free / Student Pack | USD 0 | — |

**OPEX real del proyecto: USD 0 / mes (COP 0).** No es un truco contable: el
proyecto está en línea y el costo de bolsillo es cero.

### 2.2 Si escalara — costo de salir de la capa gratuita

Es la cifra que un evaluador de negocio quiere ver: qué pasa el día que el
producto tiene usuarios de verdad y las licencias estudiantiles caducan.

| Servicio | Plan pagado | USD/mes | COP/mes |
|---|---|---|---|
| Vercel | Pro | 20 | 80.000 |
| Railway (API + Postgres) | Hobby + uso | 25 | 100.000 |
| Dominio y correo transaccional | — | 10 | 40.000 |
| Monitoreo y logs | Capa de entrada | 10 | 40.000 |
| **Subtotal infraestructura** | | **65** | **260.000** |
| Licencias IA, 3 desarrolladores (§3) | | 90 | 360.000 |
| **OPEX total en modo pagado** | | **155** | **620.000** |

A precio de lista, operar LeagueFlow cuesta **USD 1.860 al año (COP 7,44 M)**,
de los cuales **el 58 % es herramienta de IA, no servidores**. Es el dato que
invierte la intuición habitual: en un producto de este tamaño la nube ya es
commodity barata; el gasto que hay que gestionar es el de la capa de IA.

## 3. Costos de IA

| Herramienta | Licencia usada | Costo real | Costo de lista (USD/mes) | Costo de lista (COP/mes) |
|---|---|---|---|---|
| GitHub Copilot | GitHub Student Developer Pack | USD 0 | 10 | 40.000 |
| Claude Code | Plan del equipo / crédito | USD 0 de bolsillo para el proyecto | 20 (Pro) | 80.000 |
| **Por desarrollador** | | **USD 0** | **30** | **120.000** |
| **Equipo de 3, al año** | | **USD 0** | **1.080** | **4.320.000** |

**Consumo real de tokens y costo de IA por HU: pendiente.** Cada persona lo
toma del panel de uso de su herramienta al cerrar su HU (`AGENTS.md` §7). El
agente no tiene acceso a su propio consumo; cualquier cifra que "reportara"
sería inventada, y un caso de negocio con un número inventado no vale nada.
Las columnas `Costo IA` de la tabla de §1 quedan en `<pendiente>` a propósito.

**Control del gasto.** Tres palancas ya aplicadas, no aspiracionales:

1. **Licenciamiento estudiantil** (Copilot vía Student Pack) — elimina el 33 %
   del costo de lista de IA.
2. **La spec como caché de contexto.** El agente no re-descubre el dominio en
   cada sesión: `spec.md`, `plan.md` y `data-model.md` ya lo tienen escrito.
   Menos tokens de exploración por tarea.
3. **Decisiones técnicas congeladas** (`AGENTS.md` §5): ninguna HU posterior a
   la `001` vuelve a correr `/speckit-plan` para re-decidir stack o modelo de
   dominio. Se evitan 16 replanteos completos de arquitectura.

## 4. Comparativa: sin IA, IA sin spec, IA con spec

### 4.1 De dónde salen los contrafactuales

La versión anterior de este documento inventaba las horas de las alternativas
(«30 h por HU a la antigüita, 18 h con prompts sueltos»). No tenían fuente. Se
reemplazaron por cifras publicadas, y el resultado **cambió a la baja**: el
ahorro atribuible al método es mucho menor de lo que decía la primera versión.

| # | Ancla | Qué mide | Cifra usada |
|---|---|---|---|
| A1 | Peng, Kalliamvakou, Cihon y Demirer (2023), ensayo controlado, n = 70 | Tarea **bien especificada** de antemano (servidor HTTP), con y sin Copilot: 71 min vs. 161 min | **55,8 % más rápido** con IA |
| A2 | METR (2025), ensayo controlado, n = 16, 246 tareas reales | Trabajo **ambiguo** en repositorios que los devs ya conocían | **19 % más lento** con IA — y los mismos devs creían haber sido 20 % más rápidos |
| A3 | DORA / Google Cloud (2025), ~5.000 profesionales | Adopción de IA vs. desempeño de entrega | Relación **positiva con throughput**, **negativa con estabilidad**: más fallos de cambio y más retrabajo. 30 % desconfía del código generado |
| A4 | Boehm y Basili (2001), *IEEE Computer* | Retrabajo evitable como fracción del esfuerzo; costo de corregir tras la entrega | **40–50 % del esfuerzo**; corregir tras entregar cuesta ~100×, y **5:1 en proyectos pequeños no críticos** |
| A5 | Leffingwell (1997) | Origen del retrabajo | **70–85 %** del costo de retrabajo viene de defectos de requisitos |
| A6 | Tassey / NIST (2002) | Costo de una infraestructura de pruebas inadecuada en EE. UU. | USD 59,5 mil millones/año, de los cuales **USD 22,2 mil millones son evitables** |

De cada rango se toma **el extremo que perjudica al caso**: 40 % de retrabajo y
no 50 %, 5:1 y no 100:1, 70 % de origen en requisitos y no 85 %.

### 4.2 El costo de las mismas 12 HU

Punto de partida medido: **135 horas-persona** (triangulado, §7) con **73 ciclos
de corrección** registrados. A media hora por ciclo, el retrabajo de este
proyecto fue de ~37 h — el **27 % del esfuerzo**, contra el 40 % que A4 da como
línea base de la industria.

Las dos alternativas se derivan de ahí, no se inventan:

- **IA sin spec** hace el mismo trabajo nuevo (98 h). Por A3, la IA sube el
  throughput con spec o sin ella: **se le concede la misma velocidad de
  construcción**. Lo que cambia es el retrabajo, que vuelve al 40 % de A4.
- **Sin IA** hace el mismo trabajo nuevo pero sin el 55,8 % de A1, y también
  con el 40 % de retrabajo de A4.

| | Trabajo nuevo | Retrabajo | Total | Costo (COP) | Costo (USD) |
|---|---|---|---|---|---|
| Sin IA | 223 h | 149 h (40 %) | **371 h** | **22,3 M** | 5.571 |
| IA sin spec | 98 h | 66 h (40 %) | **164 h** | **9,85 M** | 2.463 |
| **IA con spec (medido)** | 98 h | 37 h (**27 %**) | **135 h** | **8,10 M** | 2.025 |

**Lo que hay que decir en voz alta:** el salto grande —de 371 h a 164 h— es
mérito de la IA, no del método. Nadie debería venderlo como propio. Lo que
aporta la spec es el tramo de 164 h a 135 h: **18 % menos, COP 145.833 por
historia**. Modesto, y por eso creíble.

### 4.3 Comparativa cualitativa

| Criterio | Sin IA | IA sin spec | **IA con spec** |
|---|---|---|---|
| Velocidad de construcción | Base | Alta (A1, A3) | Alta (A1, A3) |
| Estabilidad de la entrega | Base | **Peor** (A3: más fallos de cambio y retrabajo) | Base o mejor |
| Trazabilidad requisito → código | Manual, se degrada | Nula — el prompt se pierde en el chat | Total: FR-NNN → tarea → commit → prueba |
| Onboarding de un integrante | Días leyendo código | Días, y sin fuente de verdad que leer | Horas: lee `spec.md` y `tasks.md` |
| Evidencia para auditar | Actas dispersas | Ninguna | `specs/` y `docs/metricas/` en el mismo PR |

## 5. Valor Presente Neto de adoptar SDD

### 5.1 El hallazgo incómodo

Con las cifras ancladas, **la productividad sola no paga la adopción**. Equipo
de 3, 48 HU/año, 3 años, 18 % E. A.:

- Ahorro de productividad: COP 145.833/HU × 48 = **COP 7,00 M/año**
- Mantenimiento del método (0,5 h/HU × 48 h): **COP 1,44 M/año**
- Inversión de adopción (§5.2): **COP 22,56 M**

VPN solo con productividad: **−COP 12,84 M**. Negativo.

Nótese que aquí **ya no hace falta el «factor de atribución» de la versión
anterior**: la comparación es IA contra IA, así que el efecto de la herramienta
está neteado por construcción. Ese supuesto desapareció del modelo.

### 5.2 Inversión inicial (t = 0)

| Componente | Horas | COP |
|---|---|---|
| Formación del equipo (3 × 16 h) | 48 | 2.880.000 |
| Constitución, plantillas, flujo y CI de specs | 40 | 2.400.000 |
| Curva de aprendizaje: 30 % de sobrecosto los 2 primeros meses | 288 | 17.280.000 |
| **Inversión total** | **376** | **22.560.000 (USD 5.640)** |

El 77 % es curva de aprendizaje. Sigue siendo un supuesto (§7), pero es el
supuesto que perjudica al caso, no el que lo ayuda.

### 5.3 Dónde sí está el retorno: los defectos que no se escapan

Dato medido: **73 problemas detectados, 0 escapados a producción** — 6,08 por
historia. Dato de A4: en un proyecto pequeño no crítico, corregir después de
entregar cuesta **5×** lo que cuesta corregirlo durante el desarrollo. Con 1 h
por corrección en desarrollo, cada defecto que **no** se escapa ahorra 4 h:
**COP 240.000**.

Lo que nadie sabe es qué fracción de esos 73 se habría escapado sin la spec. En
vez de inventarla, se calcula **cuánta haría falta**:

| Si sin spec se hubiera escapado… | Defectos evitados/año | **VPN (COP)** |
|---|---|---|
| 0 % (la spec no evita ninguno) | 0 | **−12,84 M** |
| **10 % — punto de equilibrio** | 29 | **≈ 0** |
| 20 % | 58 | **+12,88 M** |
| 30 % | 88 | **+25,74 M** |

> **El caso completo se reduce a una sola pregunta:** ¿la spec evita que **1 de
> cada 10** de los problemas que detecta llegue a producción? Son **0,61
> defectos por historia**. Por encima de eso, adoptarla crea valor; por debajo,
> no.

Escenario central (20 %): **VPN COP 12,88 M (USD 3.220)**, con recuperación de
la inversión a los **19 meses**. A 12 % de tasa el VPN sube a COP 16,95 M; a
25 % baja a COP 8,93 M, y sigue positivo.

### 5.4 CAPEX / OPEX

| | CAPEX (una vez) | OPEX (anual) |
|---|---|---|
| **Método SDD** | COP 22,56 M — formación, plantillas, curva | COP 1,44 M — mantenimiento de specs |
| **Producto LeagueFlow** | COP 8,10 M — 135 h × COP 60.000 (costo de bolsillo real: COP 0) | COP 0 hoy; COP 7,44 M en modo pagado (§2.2) |

Las licencias de IA salieron del cálculo diferencial: ambos escenarios comparados
las usan, así que no distinguen entre ellos. Siguen contabilizadas en §3 como
OPEX del proyecto.

## 6. Riesgo operativo

La versión anterior traía una tabla de cinco riesgos con probabilidades
inventadas (60 %, 40 %, 50 %…). Se eliminó: no había forma de sostener ninguna
de esas cifras. Lo que queda es lo que sí tiene respaldo.

### 6.1 Lo que dicen las fuentes

- **La IA acelera y desestabiliza al mismo tiempo.** A3 (DORA 2025, ~5.000
  profesionales) encuentra relación positiva con throughput y **negativa con
  estabilidad de entrega**: más fallos de cambio, más retrabajo. Es exactamente
  el perfil de «IA sin spec».
- **La percepción no sirve como métrica.** A2 (METR): con IA los devs tardaron
  19 % más y creyeron haber ido 20 % más rápido. A3: más del 80 % cree que la
  IA lo hace más productivo. El sesgo va siempre en la misma dirección, y es la
  razón por la que este documento se apoya en `git` y no en impresiones.
- **El requisito es el punto caro.** A5: 70–85 % del costo de retrabajo nace de
  defectos de requisitos. Es justamente la clase de defecto que `/speckit-clarify`
  y los criterios de aceptación atacan antes de que exista una línea de código.

### 6.2 Lo que se midió aquí

- **73 problemas, 0 escapados.** Cada uno está descrito con su causa en
  `docs/metricas/*.md`.
- **414 pruebas** como compuerta obligatoria de cada PR.
- **El caso más caro fue de requisitos, no de código:** el primer `logout`
  borraba la cookie pero **no revocaba la sesión en base de datos**. Habría
  dejado tokens vivos en el servidor, en silencio. No lo detectó una prueba de
  humo: lo detectó un criterio de aceptación escrito en la spec. Es A5 ocurriendo
  en este repositorio.

## 7. Supuestos: qué está medido y qué no

| Parámetro | Valor | Naturaleza |
|---|---|---|
| Tareas, ciclos de corrección, pruebas, commits, LOC, personas, días | §1 y §1.1 | **Medido** — `git` y `docs/metricas/` |
| Costo de infraestructura | USD 0 | **Medido** — servicios en capa gratuita |
| Ventaja de la IA: 55,8 % | A1 | **Publicado** — ensayo controlado, n = 70 |
| Retrabajo evitable: 40 % del esfuerzo | A4 | **Publicado** — extremo bajo del rango 40–50 % |
| Costo de corregir tras entregar: 5× | A4 | **Publicado** — cifra para proyectos pequeños, no el 100× de proyectos grandes |
| Esfuerzo: 135 h-persona | 12 HU × 11,25 h | **Supuesto triangulado** — (a) capacidad de calendario: 6 personas × 5 días × ~4 h ≈ 120 h; (b) bottom-up: 342 tareas × ~0,4 h ≈ 137 h |
| Media hora por ciclo de corrección | 73 ciclos → 37 h | **Supuesto** |
| Tarifa cargada COP 60.000/h (USD 15/h) | Junior–semi en Medellín | **Supuesto de mercado** |
| TRM COP 4.000/USD | Fija en todo el documento | **Convención** |
| Inversión de adopción: 376 h | §5.2 | **Supuesto** — el componente más grande (288 h de curva de aprendizaje) no tiene fuente |
| Equipo de 3, 48 HU/año, horizonte 3 años | Modelo | **Supuesto de escenario** |
| Tasa de descuento 18 % E. A. | Software temprano en Colombia | **Supuesto**, sensibilizado a 12 % y 25 % |
| **Fracción de defectos que se escaparía sin spec** | No se estima | **Deliberadamente no supuesta** — se calcula el punto de equilibrio (10 %) y se deja la decisión al lector |
| **Tiempo real de trabajo y costo/tokens de IA por HU** | `<pendiente>` | **No se estima.** Los llena cada persona (`AGENTS.md` §7) |

### Qué invalidaría este caso

1. **Si la spec no evita ni 1 de cada 10 escapes**, el VPN es negativo y no hay
   caso. Es el supuesto del que cuelga todo.
2. **Si el esfuerzo real fue el doble de 135 h**, el ahorro de productividad se
   desvanece y el caso depende por completo del punto anterior.
3. **A2 (METR) es evidencia en contra** de la premisa de que la IA acelera: con
   trabajo ambiguo, la frenó. Este documento la usa como argumento a favor de la
   spec —la diferencia entre A1 y A2 es precisamente si la tarea estaba
   especificada— pero es una interpretación, no un resultado de esos estudios.

## 8. Fuentes

- **A1** — Peng, S., Kalliamvakou, E., Cihon, P. y Demirer, M. (2023). *The
  Impact of AI on Developer Productivity: Evidence from GitHub Copilot*.
  arXiv:2302.06590. <https://arxiv.org/abs/2302.06590>
- **A2** — Becker, J., Rush, N., Barnes, E. y Rein, D. (2025). *Measuring the
  Impact of Early-2025 AI on Experienced Open-Source Developer Productivity*.
  METR. arXiv:2507.09089. <https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/>
- **A3** — DORA / Google Cloud (2025). *State of DevOps Report 2025*.
  <https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report>
- **A4** — Boehm, B. y Basili, V. (2001). *Software Defect Reduction Top 10
  List*. IEEE Computer, 34(1), 135–137. <https://dl.acm.org/doi/10.1109/2.962984>
- **A5** — Leffingwell, D. (1997). *Calculating the return on investment from
  more effective requirements management*. American Programmer, 10(4).
- **A6** — Tassey, G. (2002). *The Economic Impacts of Inadequate Infrastructure
  for Software Testing*. NIST Planning Report 02-3.
  <https://www.nist.gov/document/report02-3pdf>

**Una cita que este documento NO usa:** el famoso «100× del IBM Systems Sciences
Institute», que circula en casi toda la literatura de calidad de software. No
existe un estudio original localizable detrás de esa cifra. El escalamiento de
costo que sí se usa aquí viene de A4, que es un artículo revisado por pares, y
se toma su valor para proyectos pequeños (5:1), no el titular de 100:1.
