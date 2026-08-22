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

## 4. Comparativa: SDD vs. tradicional vs. prompts sueltos

### 4.1 Cualitativa

| Criterio | Tradicional (sin IA) | Prompts sueltos (IA sin spec) | **SDD (Spec Kit)** |
|---|---|---|---|
| Tiempo por HU | ~30 h | ~18 h | **11,25 h** |
| Retrabajo por requisito mal entendido | Alto — se descubre en pruebas de aceptación | **El más alto** — el modelo rellena los huecos con supuestos plausibles y nadie los revisa | Bajo — `/speckit-clarify` fuerza las preguntas *antes* de escribir código |
| Trazabilidad requisito → código | Manual, se degrada | Nula — el prompt se pierde en el chat | **Total** — FR-NNN → tarea → commit → prueba |
| Consistencia entre integrantes | Depende de convenciones y revisión | Baja — cada quien negocia su propia arquitectura con el modelo | **Alta** — constitución + plan `001` congelado son vinculantes |
| Onboarding de un integrante nuevo | Días leyendo código | Días, y sin fuente de verdad que leer | **Horas** — lee `spec.md` y `tasks.md` de la HU |
| Costo de un cambio de alcance tardío | Muy alto | Muy alto y silencioso | Moderado — se edita la spec y se regeneran las tareas |
| Evidencia para auditar la decisión | Actas dispersas | Ninguna | `specs/` y `docs/metricas/` versionados en el mismo PR |

La fila que decide el caso no es la del tiempo, es la de la trazabilidad.
"Prompts sueltos" es más rápido que lo tradicional y **más peligroso que
ambos**: produce código verosímil sin dejar rastro de qué se pidió, así que el
defecto no se detecta hasta que un usuario lo encuentra.

### 4.2 Cuantitativa — costo total de las mismas 12 HU

Tarifa cargada de referencia: **COP 60.000/hora (USD 15/h)**; TRM fija
**COP 4.000/USD**. Costo de un defecto que llega a producción: **8 h**
(diagnóstico + hotfix + despliegue + comunicación) = **COP 480.000**.

| Concepto | Tradicional | Prompts sueltos | **SDD** |
|---|---|---|---|
| Horas por HU | 30 | 18 | **11,25** |
| Horas, 12 HU | 360 | 216 | **135** |
| Costo de construcción (COP) | 21.600.000 | 12.960.000 | **8.100.000** |
| Defectos escapados a producción por HU | 0,9 | 1,8 | **0,3** |
| Costo del retrabajo en producción (COP) | 5.184.000 | 10.368.000 | **1.728.000** |
| **Costo total del alcance (COP)** | **26.784.000** | **23.328.000** | **9.828.000** |
| **Costo total del alcance (USD)** | **6.696** | **5.832** | **2.457** |
| Ahorro de SDD frente a esta alternativa | −63 % | −58 % | — |

**Ahorro por HU frente a prompts sueltos: COP 1.125.000 (USD 281).** Es la
cifra que alimenta el flujo de caja de §5, y es la comparación *conservadora*:
frente al desarrollo tradicional el ahorro por HU sería COP 1.413.000.

## 5. Valor Presente Neto de adoptar SDD

### 5.1 Qué se está valorando

No se valora el producto —LeagueFlow opera a COP 0 y su VPN es trivialmente
positivo— sino **la decisión de método**: ¿cuánto vale, hoy, que un equipo
adopte Spec-Driven Development en vez de seguir con prompts sueltos?

El flujo de caja es diferencial: *inversión en adoptar el método* contra
*ahorro recurrente por HU*. Equipo modelado: **3 desarrolladores, 4 HU/mes
(48 HU/año), horizonte 3 años, tasa de descuento 18 % E. A.**

### 5.2 Inversión inicial (t = 0)

| Componente | Horas | COP |
|---|---|---|
| Formación del equipo (3 × 16 h) | 48 | 2.880.000 |
| Constitución, plantillas, flujo y CI de specs | 40 | 2.400.000 |
| Curva de aprendizaje: 30 % de sobrecosto los 2 primeros meses | 288 | 17.280.000 |
| **Inversión total** | **376** | **22.560.000 (USD 5.640)** |

La curva de aprendizaje es el 77 % de la inversión y es la objeción real de
cualquier equipo. Está adentro del modelo, no maquillada.

### 5.3 Flujo de caja

Dos ajustes conservadores, deliberados:

- **Factor de atribución 70 %.** No todo el ahorro medido es de SDD; parte es
  de usar IA en general. Se le acredita al método solo el 70 %.
- **Rampa año 1 al 60 %.** El equipo todavía está aprendiendo.

| Año | Ahorro bruto (COP) | × 70 % atribución | OPEX del método¹ | **Flujo neto (COP)** |
|---|---|---|---|---|
| 0 | — | — | 22.560.000 (inversión) | **−22.560.000** |
| 1 | 54.000.000 × 60 % = 32.400.000 | 22.680.000 | 5.760.000 | **+16.920.000** |
| 2 | 54.000.000 | 37.800.000 | 5.760.000 | **+32.040.000** |
| 3 | 54.000.000 | 37.800.000 | 5.760.000 | **+32.040.000** |

¹ Mantenimiento del método (0,5 h/HU × 48 HU = COP 1.440.000) + licencias IA a
precio de lista para 3 desarrolladores (COP 4.320.000).

### 5.4 Resultado

| Indicador | Valor (COP) | Valor (USD) |
|---|---|---|
| **VPN @ 18 % E. A.** | **34.290.000** | **8.573** |
| TIR | **≈ 89 % E. A.** | — |
| Periodo de recuperación | **14 meses** | — |
| Índice de rentabilidad (VP beneficios / inversión) | **2,52** | — |

**Sensibilidad a la tasa de descuento** — el VPN nunca cambia de signo:

| Tasa de descuento | 12 % | 18 % | 25 % |
|---|---|---|---|
| VPN (COP) | 40.900.000 | 34.290.000 | 27.900.000 |
| VPN (USD) | 10.225 | 8.573 | 6.975 |

**Punto de equilibrio del supuesto más discutible.** El factor de atribución
puede caer de 70 % a **35,4 %** antes de que el VPN llegue a cero. Dicho de
otra forma: **el método puede incumplir dos tercios de lo que promete y la
decisión sigue sin destruir valor.** Ese margen, y no el VPN puntual, es el
argumento.

### 5.5 ROI y encuadre CAPEX / OPEX

| | CAPEX (una vez) | OPEX (anual, en régimen) |
|---|---|---|
| **Método SDD** | COP 22.560.000 — formación, plantillas, curva | COP 5.760.000 — mantenimiento de specs + licencias IA |
| **Producto LeagueFlow** | COP 8.100.000 — 135 h × COP 60.000 (costo de bolsillo real: COP 0) | COP 0 hoy; COP 7.440.000 en modo pagado (§2.2) |

- **ROI a 3 años (no descontado)** = (81.000.000 − 22.560.000) / 22.560.000 =
  **259 %**, donde 81.000.000 es la suma de los flujos netos de los años 1 a 3
  (ya descontado el OPEX del método).
- **ROI descontado** = VPN / Inversión = 34.290.000 / 22.560.000 = **152 %**.

## 6. Reducción de riesgo operativo

El VPN de §5 **no incluye** este capítulo. Es upside deliberadamente excluido
para no inflar el número.

### 6.1 Exposición esperada anual (probabilidad × impacto)

| Riesgo | Impacto (COP) | P sin SDD | P con SDD | Exposición sin | Exposición con | Control que lo baja |
|---|---|---|---|---|---|---|
| Requisito mal entendido llega a producción | 4.800.000 | 60 % | 20 % | 2.880.000 | 960.000 | `/speckit-clarify` + criterios de aceptación en la spec |
| Dependencia de una sola persona (bus factor) | 9.600.000 | 40 % | 10 % | 3.840.000 | 960.000 | 17 specs versionadas; cualquiera retoma leyendo `spec.md` |
| Regresión en funcionalidad ya entregada | 2.400.000 | 50 % | 10 % | 1.200.000 | 240.000 | 414 pruebas en CI como gate de cada PR |
| Secreto filtrado al repositorio | 12.000.000 | 15 % | 3 % | 1.800.000 | 360.000 | Push protection + GitGuardian + `AGENTS.md` §3 |
| Colisión de trabajo paralelo (dos cabezas de Alembic) | 1.200.000 | 70 % | 20 % | 840.000 | 240.000 | Orden de merge pactado `013 → 014 → 016 → 017` |
| **Total exposición anual** | | | | **10.560.000** | **2.760.000** | |

**Reducción de exposición: COP 7.800.000/año (USD 1.950), un 74 %.**

### 6.2 Evidencia, no promesa

Cada control de la tabla tiene una huella verificable en este repositorio:

- **73 ciclos de corrección documentados, 0 escapados a producción.** Están
  escritos uno por uno en `docs/metricas/*.md` con su causa.
- **El caso más caro se detectó en la HU `001`**: el primer `logout` borraba la
  cookie pero **no revocaba la sesión en base de datos**. Habría dejado tokens
  vivos en el servidor rompiendo el AS6 en silencio — un fallo de seguridad
  que ninguna prueba de humo encuentra. Lo encontró el criterio de aceptación
  escrito en la spec.
- **La HU `012` acumuló 25 ciclos** contra 1 de la `005`. La dispersión es
  información: el trabajo visual y de accesibilidad es donde la spec rinde
  menos y la ejecución real de la app rinde más. Está anotado, no escondido.

### 6.3 VPN ampliado

Incluyendo la reducción de exposición al riesgo con el mismo factor de
atribución del 70 % y la misma rampa:

| | VPN base | + riesgo evitado | **VPN ampliado** |
|---|---|---|---|
| COP | 34.290.000 | 10.020.000 | **44.310.000** |
| USD | 8.573 | 2.505 | **11.078** |

## 7. Supuestos y honestidad del modelo

Lo que sigue separa qué está medido de qué está supuesto. Es la sección que
hace auditable el caso.

| Parámetro | Valor | Naturaleza |
|---|---|---|
| Tareas, ciclos de corrección, pruebas, commits, LOC, personas | Tabla §1 y §1.1 | **Medido** — `git` y `docs/metricas/` |
| Esfuerzo del proyecto: 135 h-persona | 12 HU × 11,25 h | **Supuesto triangulado** — (a) capacidad de calendario: 6 personas × 5 días × ~4 h efectivas ≈ 120 h; (b) bottom-up: 342 tareas × ~0,4 h ≈ 137 h. Se toma el punto medio |
| Tarifa cargada COP 60.000/h (USD 15/h) | Junior–semi senior en Medellín, con prestaciones y overhead | **Supuesto de mercado** |
| TRM COP 4.000/USD | Fija para todo el documento | **Convención** |
| 30 h/HU tradicional, 18 h/HU prompts sueltos | Contrafactuales | **Supuestos** — 2,7× y 1,6× sobre lo medido |
| Costo de un defecto en producción: 8 h | Diagnóstico + hotfix + despliegue + comunicación | **Supuesto**, conservador frente a la curva clásica de costo del defecto (10–15× respecto a detectarlo en desarrollo) |
| Tasa de escape de defectos: 0,3 / 1,8 / 0,9 por HU | SDD / prompts / tradicional | **Supuesto**, anclado en los 73 reprocesos observados |
| Tasa de descuento 18 % E. A. | Proyecto de software temprano en Colombia | **Supuesto**, sensibilizado a 12 % y 25 % |
| Factor de atribución 70 % | Parte del ahorro es de la IA, no del método | **Supuesto conservador**, con punto de equilibrio calculado en 35,4 % |
| **Tiempo real de trabajo y costo/tokens de IA por HU** | `<pendiente>` | **No se estima.** Los llena cada persona; inventarlos invalidaría el resto |

**Qué invalidaría este caso.** Si el esfuerzo real resultara ser el doble de
135 h, el costo de construcción de SDD subiría a COP 16,2 M y el ahorro por HU
caería a ~COP 560.000 — el VPN seguiría siendo positivo (≈ COP 6 M), pero el
margen desaparecería. Por eso las dos columnas pendientes de §1 importan: son
las que convierten este caso sintético en uno medido.
