# Métricas — HU 012: Identidad visual y experiencia de usuario consistente

**Spec**: `specs/012-identidad-visual/spec.md` · **Responsable**: jonathan.sandoval · **Cerrada**: 2026-08-20

## Llenado por el agente (al terminar la HU, antes del PR)

| Métrica | Valor |
|---|---|
| Tareas en `tasks.md` (total) | 105 (82 + 11 de la primera ampliación visual + 12 del marco sobre la maqueta) |
| Tareas completadas | 102 (las 3 pendientes son verificación manual con backend) |
| Tests escritos (backend) | 0 — la HU no toca `backend/` (FR-032) |
| Tests escritos (frontend) | 132 nuevos, en 13 archivos nuevos |
| Tests en verde al cerrar | 197 / 197 (21 archivos). Línea base: 44 |
| Ciclos de corrección | 25 (16 en la primera pasada + 6 en la ampliación visual + 3 en el marco sobre la maqueta) |
| Archivos de código creados/modificados | 40 (11 nuevos + 29 modificados), todos bajo `frontend/` |

**Ciclos de corrección**: cuántas veces hubo que volver sobre algo ya dado por
terminado (test que falló tras implementar, requisito mal interpretado,
refactor por un choque con otra HU). Cuenta honesta, no aspiracional: `0` es
sospechoso en una HU no trivial.

**Qué se reprocesó y por qué** (una línea por ciclo):

*Defectos de diseño detectados por una prueba o por la app corriendo (5)*

- **`useLigaEnContexto` reescrito por completo.** Al escribir la prueba de la
  sección activa se vio que en `/teams/:teamId/players` no hay liga en la ruta,
  así que las seis secciones quedaban inertes por FR-006 y **Jugadores no podía
  resaltarse nunca**. El hook pasó de leer solo `/leagues/:id` a resolver la
  liga también desde el equipo y desde el partido. Cambió el contrato.
- **"Programar partido" y "Registrar jugador" duplicados.** Al añadir la acción
  al estado vacío (FR-014) quedaron dos enlaces idénticos junto al enlace de
  cabecera. Se ocultó el de cabecera cuando la lista está vacía.
- **El asterisco de obligatorio contaminaba el nombre accesible** del campo
  ("Usuario *"), rompiendo lector de pantalla y consultas por etiqueta. Se sacó
  fuera del `<label>`.
- **`CreateTeamForm` enviaba *todos* los errores al campo "Nombre"**, incluidos
  los de permisos o red. Lo delató un import sin usar que el linter marcó.
- **Cuatro pantallas perdían su `<h1>` en estado de carga y error**, porque
  retornaban antes de renderizarlo. **Solo se vio ejecutando la aplicación**, no
  en las pruebas. Igual que `/admin`, que tenía un `<h2>` suelto sin `<h1>`.

*Cambios de requisito legítimos que obligaron a actualizar pruebas existentes (7)*

Ninguna prueba se borró, se saltó ni se debilitó (Principio IV). Cada cambio
lleva su justificación escrita en el propio test:

- Celda de posición `"1"` → `"🥇 1.º"` en la clasificación (FR-011).
- `"X vs Y"` → `"LOCAL 3 — 1 VISITANTE"` en listado, calendario y detalle, 4
  aserciones en 2 archivos (FR-009).
- Sustituto de escudo `"I"` → `"IF"`: FR-012 pide iniciales, no una letra.
- Etiqueta del estado vacío → `"Registrar el primer equipo"` (quickstart §12).
- Etiquetas `"Colores (opcional)"` → `"Colores"` + texto de ayuda separado.
- **Cinco mensajes de error dejaron de ser el `message` del servidor** y pasaron
  al catálogo en español (FR-015, SC-003): login, clasificación, liga
  duplicada, equipo duplicado, dorsal duplicado y equipo contra sí mismo.
- `GoalForm` tenía su **propio catálogo de mensajes local**: se absorbió en
  `lib/mensajesDeError.ts` conservando su redacción, que era mejor.

*Ampliación visual — Historia 6, segunda pasada (6)*

La primera entrega cumplía la estructura del mockup pero se leía plana, y la
pantalla de inicio mostraba seis secciones deshabilitadas. La revisión con el
equipo abrió una enmienda del spec (FR-006 reescrito, FR-034 a FR-039, SC-011
y SC-012) y una segunda pasada de implementación. **Los cinco primeros ciclos
los abrió la aplicación corriendo en el navegador, no una prueba**:

- **La navegación sin liga le robaba el ancho a la portada.** Al quitar los
  ítems deshabilitados quedaba una columna con un solo botón y el bloque
  principal comprimido al lado. Se convirtió en barra compacta a todo lo ancho.
- **Esa barra volvía a ser columna estrecha por debajo de 1024 px**: la media
  query anterior fijaba `width: 180px` y ganaba por orden en la hoja. Hizo
  falta anular explícitamente la variante compacta dentro de cada corte.
- **Los nueve formularios quedaban sueltos sobre el fondo**, sin superficie que
  los contuviera, justo cuando el resto de la aplicación pasó a tarjetas
  elevadas. Se resolvió en `.lf-formulario`, que ya era el contenedor
  compartido, no pantalla por pantalla.
- **El acceso "Ver ligas" apuntaba a la pantalla en la que ya estabas** cuando
  la ruta era `/leagues`. Se oculta ahí: el acceso que pide FR-006 ya está.
- **El botón "Menú" seguía apareciendo en pantallas sin secciones**, es decir,
  un control que no controlaba nada. Ahora solo existe si hay lista detrás.
- **La prueba de FR-006 afirmaba justo lo contrario de la conducta nueva**
  (esperaba las seis secciones inertes en el `<nav>`). Se reescribió con la
  enmienda citada en el propio test, y se le añadió la aserción de SC-011:
  cero elementos con `aria-disabled` en la navegación.

*Fricción de herramienta (4)*

- Dos fixtures de prueba mal elegidos: `username` idéntico al `role`, y un
  equipo de una sola palabra cuyas iniciales coinciden con su nombre.
- Error de campo sin `role="alert"`: no se anunciaba al aparecer.
- **Las dos pruebas de sistema se escribieron tres veces.** `tsc` no compila
  `node:fs` sin `@types/node`, y el plan exige cero dependencias nuevas. Se
  intentó `import.meta.glob` con `?raw` (devuelve el proxy de CSS Modules) y con
  `?inline` (devuelve cadena vacía, lo que habría dejado **la auditoría pasando
  en vacío**). Se volvió a `node:fs` con una declaración de tipos local.

*Marco de aplicación sobre la maqueta de referencia — segunda ampliación (3)*

El equipo aportó una maqueta navegable (`LeagueFlow Wow`, Claude Design) como
referencia de disposición y color para una tercera pasada del shell. Los tres
ciclos:

- **La auditoría de tokens rechazó los `rgb(255 255 255 / 8-16%)`** que usé
  para las superposiciones translúcidas de la navegación sobre la nueva
  superficie de marca. Es exactamente el gate haciendo su trabajo (SC-009): se
  declararon como tokens (`--lf-color-marca-superponer-*`) en `tokens.css` en
  vez de como literales en el componente.
- **El nombre accesible de la marca se rompió al partirla en dos colores.**
  "LEAGUEFLOW" en dos `<span>` de color distinto se lee como "LEAGUE FLOW"
  (con espacio) para un lector de pantalla, y el test que buscaba el enlace
  por nombre exacto lo delató de inmediato. Se fijó `aria-label="LEAGUEFLOW"`
  en el enlace y se ocultaron los `<span>` internos.
- **El marco no llenaba el alto de la ventana en pantallas con poco
  contenido** (Tabla con dos equipos dejaba una franja clara enorme debajo del
  marco oscuro). Verlo en el navegador, no una prueba, lo mostró: hizo falta
  que `.lienzo` centrara `.marco` por flex en vez de por `margin: 0 auto`, para
  que el marco heredara el alto disponible. Al aplicar el mismo `stretch` en
  el corte móvil (una sola columna, dos filas) apareció un segundo defecto
  gemelo — una franja oscura vacía entre la marca y la cabecera — que se
  corrigió con `align-content: start` acotado a esa media query.

## Llenado por la persona (dos números, al cerrar)

| Métrica | Valor |
|---|---|
| Tiempo real de trabajo — spec + plan + tasks | <ej. 45 min> |
| Tiempo real de trabajo — implement + tests | <ej. 2 h> |
| Costo IA aproximado de la HU | <del panel de uso de tu herramienta> |

## Observaciones

**Lo que el spec traía mal y se descubrió después** — evidencia directa del
valor y del costo de SDD:

1. El spec afirmaba que la línea base de no regresión incluía una suite **de
   extremo a extremo**. No existe: `@playwright/test` no está instalado y
   `frontend/e2e/` solo tiene un README. Lo detectó `/speckit-analyze` y se
   corrigió antes de implementar. Coste si no se detecta: instalar Playwright,
   que `AGENTS.md` §5 prohíbe decidir en esta HU.
2. El `data-model` asignaba a **Jugadores el mismo destino que a Equipos**, lo
   que dejaba dos secciones activas a la vez. `/speckit-analyze` lo detectó
   como conflicto con FR-004; la corrección (separar `ruta` de `coincide`) se
   diseñó **antes** de escribir el shell. Implementándolo se descubrió además
   la segunda mitad del problema, que el análisis no vio: sin liga en contexto
   fuera de `/leagues/:id`, Jugadores no podía resaltarse **nunca**.
3. SC-001 exigía "sección resaltada" en el **100%** de las pantallas, pero en
   login y listado de ligas no hay ninguna sección aplicable. Era un criterio
   no satisfacible; se acotó.
4. El `data-model` declaraba un contraste mínimo de **6.35:1**. El real, medido
   sobre los 18 pares, es **6.25:1** (`peligro` sobre `peligro-tinte`). Ambos
   superan el 4.5:1 exigido, pero el dato estaba mal.

**Lo que funcionó mejor de lo esperado.** Las 44 pruebas heredadas hicieron de
red de seguridad real: **12 de los 16 ciclos** los abrió una prueba que falló,
no una revisión manual. Los dos gates automatizados (contraste sobre
`tokens.css` y auditoría de literales de color) convierten SC-004 y SC-009 en
comprobaciones de CI; se verificó que **no son vacuos** inyectando un
`#ff0000` a propósito y comprobando que la auditoría falla nombrando el archivo.
En la ampliación visual ese gate se pagó solo: la paleta nueva (azul acero,
acento cálido y cuatro degradados) se validó de una pasada contra los **30**
pares de contraste declarados, mínimo real **4.76:1**, sin inspección manual.

**Lo que las pruebas no vieron.** El defecto del `<h1>` ausente en los estados
de carga y error apareció solo al abrir la aplicación en el navegador. Es el
argumento para no dar por cerrada una HU de presentación sin ejecutarla, y la
segunda pasada lo confirmó: **5 de sus 6 ciclos** salieron de mirar la pantalla,
no de una aserción. Una suite verde no dice si algo se ve bien.

**Una fragilidad que conviene vigilar.** La prueba del calendario de 190
partidos tarda ~0,9 s aislada, pero en una corrida con la máquina cargada
superó el presupuesto por defecto de 5 s de Vitest y falló una vez de tres. No
es una regresión de código —el marcado por fila pasó de 1 a ~12 elementos y
aun así rinde—, pero el margen se estrechó. No se tocó el presupuesto ni la
prueba; queda anotado por si vuelve a aparecer en CI.

**Verificación en la segunda pasada, ya con backend sirviendo datos.** Se
recorrieron en navegador real portada, listado de ligas, detalle de liga,
partidos, clasificación e inicio de sesión, a 1280 / 768 / 375 px: marcador
`TIGRES 3 — 1 HALCONES` con su distintivo "FINALIZADO", podio con 1.º y 2.º
destacados sobre datos reales, sección activa resaltada por pastilla y punto
—no solo por color—, y `document.body.scrollWidth === window.innerWidth` a
375 px. **Sigue sin ejecutarse el recorrido de teclado de SC-005**: exige
iniciar sesión con credenciales reales, que el agente no introduce.

**Verificación manual pendiente (primera pasada, redactada sin backend).** El recorrido completo de teclado (SC-005:
iniciar sesión → crear equipo → registrar resultado) **no pudo ejecutarse**: no
hay PostgreSQL levantado en este entorno, así que el backend no sirve datos. Sí
se verificó en navegador real, a 1280/768/375 px: shell y navegación presentes,
`:focus-visible` con contorno sólido de 3 px, los 8 controles enfocables con
nombre accesible, el botón "Menú" colapsando y expandiendo la navegación con
`aria-expanded`, y **cero desbordamiento horizontal** en los tres anchos. Queda
para la persona el recorrido de las tres tareas con backend en marcha, y la
comprobación de tablas anchas y podio con datos reales.
