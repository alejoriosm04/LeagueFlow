# Feature Specification: Identidad visual y experiencia de usuario consistente

**Feature Branch**: `012-identidad-visual`

**Created**: 2026-08-20

**Status**: Draft

**Input**: User description: "HU12 — Identidad visual y experiencia de usuario consistente en toda la aplicación. Como cualquier usuario de LeagueFlow (espectador, operador u organizador), quiero que la aplicación se vea y se comporte como un producto real y no como un prototipo sin estilos, para poder navegarla con confianza y entender el estado de la liga de un vistazo. Referencia visual obligatoria: el mockup ASCII del dashboard en `docs/enunciado.md` §2 y las capturas de referencia de ese mismo documento."

## Dependencies

Historia **transversal de presentación**. No introduce reglas de negocio, no
altera contratos de API, no añade entidades ni campos, y no genera migraciones
de esquema.

- **Depende de** las pantallas ya entregadas por `specs/001` a `specs/009`:
  autenticación, ligas, equipos, jugadores, partidos (programación, resultado,
  corrección), calendario/resultados, clasificación y registro de goles.
- **No re-decide stack ni modelo de dominio.** Se rige por `AGENTS.md` §5 y por
  `specs/001-fundacion-y-autenticacion/plan.md`. Su `plan.md` solo documenta lo
  que **añade** en la capa de presentación.
- **Habilita a** `specs/010-alineaciones-estadisticas` y
  `specs/011-dashboard-liga`: ambas construyen sobre este sistema visual y no
  vuelven a decidir nada de estilo.
- **Principio IV de la constitución**: no puede romper funcionalidad ni pruebas
  existentes. La suite automatizada actual —**unitaria y de componente
  (Vitest + React Testing Library)**— debe seguir completamente en verde. El
  proyecto no tiene hoy suite de extremo a extremo: `frontend/e2e/` está vacío
  a propósito desde `specs/001` y añadir esa herramienta sería una decisión de
  stack que `AGENTS.md` §5 no permite tomar en esta historia.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reconocer la aplicación como un producto (Priority: P1)

Como cualquier usuario, al abrir LeagueFlow quiero encontrar siempre la misma
cabecera de marca, el mismo indicador de la liga en la que estoy, mi estado de
sesión y una navegación lateral con las secciones del producto, de modo que en
cualquier pantalla sepa dónde estoy y a dónde puedo ir.

**Why this priority**: Es la meta explícita del enunciado ("Al entrar, quiero
que ya parezca un producto real"). Sin una estructura común, cada pantalla se
lee como una página suelta y el resto del sistema visual no tiene dónde
apoyarse.

**Independent Test**: Recorrer las pantallas ya implementadas (inicio de
sesión, ligas, equipos, jugadores, partidos, calendario, clasificación) y
verificar que todas presentan la misma cabecera y la misma navegación, con la
sección actual resaltada de forma perceptible sin depender solo del color.

**Acceptance Scenarios**:

1. **Given** un usuario en cualquier pantalla de la aplicación, **When**
   observa la interfaz, **Then** ve la misma cabecera con la marca
   "LEAGUEFLOW" y la misma navegación de secciones, con la sección actual
   resaltada.
2. **Given** un usuario con sesión iniciada, **When** observa la cabecera,
   **Then** ve su nombre de usuario y su rol; **Given** un usuario sin sesión,
   **Then** ve en su lugar un acceso para iniciar sesión.
3. **Given** un usuario situado dentro de una liga, **When** observa la
   cabecera, **Then** ve el nombre de la liga en contexto.
4. **Given** un usuario que activa un elemento de la navegación, **When** llega
   a la pantalla destino, **Then** esa sección queda marcada como activa y la
   anterior deja de estarlo.
5. **Given** una pantalla estrecha, **When** el usuario abre la aplicación,
   **Then** la navegación se colapsa y sigue siendo alcanzable mediante un
   control visible y operable.

---

### User Story 2 - Leer el estado de la liga de un vistazo (Priority: P2)

Como espectador quiero que marcadores, estados de partido, tablas y posiciones
de podio se presenten siempre con el mismo lenguaje visual, para entender qué
está pasando en la liga sin tener que leer con detenimiento cada pantalla.

**Why this priority**: Es lo que convierte los datos ya disponibles en
información legible. Depende de que exista el contenedor de la Historia 1, pero
aporta valor por sí sola en cada listado.

**Independent Test**: Abrir el listado de partidos y la clasificación de una
liga con datos en todos los estados posibles y verificar el formato de
marcador, los distintivos de estado, la alineación numérica y el destacado de
las tres primeras posiciones.

**Acceptance Scenarios**:

1. **Given** la tabla de posiciones de una liga, **When** se consulta,
   **Then** los puntos y la diferencia de goles se leen alineados a la derecha
   y las tres primeras posiciones se distinguen visualmente del resto.
2. **Given** un partido en cada uno de sus estados posibles (programado, en
   curso, finalizado, cancelado), **When** aparece en un listado, **Then** su
   estado es identificable por el texto de su distintivo y no solo por su
   color.
3. **Given** un partido con resultado registrado, **When** se muestra en
   cualquier pantalla, **Then** su marcador se presenta con el formato
   "LOCAL 3 — 1 VISITANTE", idéntico en todas las vistas.
4. **Given** un equipo sin escudo disponible, **When** aparece en un listado,
   **Then** se muestra un sustituto con sus iniciales y el listado conserva su
   alineación.
5. **Given** cualquier fecha u hora mostrada en la aplicación, **When** se
   compara entre dos pantallas distintas, **Then** ambas usan el mismo formato.

---

### User Story 3 - Entender qué está pasando cuando no hay datos o algo falla (Priority: P3)

Como usuario quiero que cada pantalla me diga si está cargando, si no hay nada
que mostrar y qué hacer al respecto, o si algo falló, en español y sin
tecnicismos, para no quedarme frente a una pantalla en blanco sin saber si el
problema es mío o del sistema.

**Why this priority**: Es la diferencia perceptible entre un prototipo y un
producto, y es donde hoy la aplicación se siente incompleta.

**Independent Test**: Forzar cada uno de los tres estados (carga, vacío, error)
en una pantalla que consulta datos y verificar el mensaje mostrado y que la
aplicación sigue navegable.

**Acceptance Scenarios**:

1. **Given** una liga sin equipos registrados, **When** se abre el listado de
   equipos, **Then** se muestra un estado vacío con la acción sugerida y no una
   tabla vacía sin explicación.
2. **Given** una consulta de datos al servidor que falla, **When** la pantalla
   recibe la respuesta,
   **Then** se muestra un mensaje de error en español, sin detalles técnicos
   internos ni trazas, y la aplicación sigue navegable.
3. **Given** una pantalla que está recuperando datos, **When** el usuario la
   abre, **Then** ve un estado de carga explícito en lugar de un área vacía
   ambigua.
4. **Given** un formulario con un campo inválido, **When** el usuario intenta
   enviarlo, **Then** el mensaje de error aparece junto al campo afectado y
   queda asociado a él.
5. **Given** un formulario con un envío en curso, **When** el usuario vuelve a
   activar el botón de envío, **Then** el reenvío queda bloqueado y el control
   comunica que hay una operación en progreso.

---

### User Story 4 - Usar la aplicación solo con teclado y con buen contraste (Priority: P4)

Como usuario que no usa ratón, o que necesita buen contraste para leer, quiero
poder recorrer y operar cualquier pantalla con el teclado viendo siempre dónde
está el foco, para completar las mismas tareas que cualquier otro usuario.

**Why this priority**: Es un requisito de calidad del entregable y una
restricción que condiciona cómo se construyen los componentes; retrasarla
obligaría a rehacerlos.

**Independent Test**: Recorrer una pantalla con formulario y un listado
usando exclusivamente el teclado, y medir el contraste del texto contra su
fondo en las superficies definidas por el sistema visual.

**Acceptance Scenarios**:

1. **Given** un usuario que navega solo con teclado, **When** recorre una
   pantalla con formulario, **Then** puede alcanzar y activar todos los
   controles y siempre ve dónde está el foco.
2. **Given** cualquier texto de la interfaz, **When** se mide su contraste
   contra su fondo, **Then** la relación es de al menos 4.5:1.
3. **Given** un campo de formulario, **When** se inspecciona su estructura,
   **Then** tiene una etiqueta asociada y, si aplica, su texto de ayuda y su
   mensaje de error también quedan asociados al campo.
4. **Given** cualquier información de estado (estado de partido, posición de
   podio, error de validación), **When** se elimina el color de la
   presentación, **Then** la información sigue siendo identificable por texto
   o forma.
5. **Given** cualquier pantalla, **When** se recorre su estructura, **Then**
   presenta un encabezado principal único y regiones identificables de
   cabecera, navegación y contenido.

---

### User Story 5 - Usar la aplicación desde tablet o móvil (Priority: P5)

Como usuario que consulta la liga desde el teléfono quiero que la aplicación
sea legible y operable sin desplazamiento horizontal de la página, para
consultar resultados y clasificación donde esté.

**Why this priority**: Amplía el alcance de uso, pero solo tiene sentido una
vez que existe el sistema visual que debe adaptarse.

**Independent Test**: Abrir cada pantalla implementada a 1280 px, 768 px y
375 px de ancho y comprobar legibilidad y ausencia de desbordamiento
horizontal de la página.

**Acceptance Scenarios**:

1. **Given** la aplicación abierta a 375 px de ancho, **When** se recorre
   cualquier pantalla, **Then** el contenido es legible y la página no se
   desplaza horizontalmente.
2. **Given** una tabla más ancha que la pantalla, **When** se consulta a
   375 px, **Then** la tabla se desplaza dentro de su propio contenedor y el
   resto de la página permanece fija.
3. **Given** la aplicación abierta a 768 px, **When** se recorre cualquier
   pantalla, **Then** la navegación sigue siendo alcanzable y el contenido
   conserva su jerarquía.

---

### User Story 6 - Llegar a una portada que presenta el producto (Priority: P6)

Como visitante que abre LeagueFlow por primera vez —o como usuario que vuelve
sin haber elegido todavía una liga— quiero encontrar una portada que explique
qué es el producto y me lleve a mi primer destino útil, en lugar de una
navegación gris de secciones que todavía no puedo usar.

**Why this priority**: Es la primera pantalla que se ve y hoy es la más pobre
de la aplicación: un título, dos líneas de texto y una lista lateral de seis
secciones inertes. El enunciado abre con "al entrar, quiero que ya parezca un
producto real" y esa frase se juzga precisamente aquí. Va la última porque se
apoya en el sistema visual completo de las Historias 1 a 5.

**Independent Test**: Abrir `/` sin sesión y con sesión iniciada y comprobar
que en ambos casos se presenta la marca, la propuesta de valor y un acceso
claro al siguiente paso, sin mostrar secciones inoperables.

**Acceptance Scenarios**:

1. **Given** un visitante sin sesión, **When** abre la pantalla de inicio,
   **Then** ve la marca, una descripción breve del producto y un acceso
   destacado para iniciar sesión.
2. **Given** un usuario con sesión iniciada y sin liga en contexto, **When**
   abre la pantalla de inicio, **Then** ve un acceso destacado a sus ligas y
   una presentación de las secciones del producto.
3. **Given** cualquier usuario en una pantalla sin liga en contexto, **When**
   observa la estructura, **Then** no ve la lista de secciones de liga
   presentada como elementos deshabilitados.
4. **Given** un usuario en la portada, **When** recorre la pantalla solo con
   el teclado, **Then** alcanza todos sus accesos en orden y con el foco
   visible.
5. **Given** un usuario en cualquier pantalla, **When** observa la interfaz,
   **Then** ve una única superficie de marca que contiene navegación, cabecera
   y contenido, y las tarjetas de datos se leen como superficies claras
   elevadas sobre ella.
6. **Given** un usuario en la portada, **When** quiere entrar a una liga,
   **Then** puede elegirla directamente desde la propia portada, sin pasar por
   otra pantalla intermedia.

---

### Edge Cases

- ¿Qué muestra el indicador de liga en contexto en pantallas que no pertenecen
  a ninguna liga (inicio de sesión, listado de ligas, creación de liga)?
- ¿Qué ocurre con las secciones que dependen de una liga cuando todavía no hay
  ninguna liga en contexto?
- ¿Qué se muestra cuando un nombre de equipo, liga o jugador es mucho más largo
  que el espacio disponible en una celda, un distintivo o el indicador de liga?
- ¿Qué se muestra cuando el enlace externo del escudo de un equipo existe pero
  no carga?
- ¿Cómo se comporta el estado vacío de una pantalla que además es de solo
  lectura para el usuario actual (un espectador no puede "crear el primer
  equipo")?
- ¿Qué pasa si una operación falla mientras el formulario está bloqueado por un
  envío en curso: queda el usuario atrapado sin poder reintentar?
- ¿Cómo se distingue el podio en una liga con menos de tres equipos?

## Requirements *(mandatory)*

### Functional Requirements

#### Estructura de aplicación (shell)

- **FR-001**: Todas las pantallas, públicas y autenticadas, MUST compartir una
  misma estructura de aplicación compuesta por una cabecera superior y una
  navegación de secciones.
- **FR-002**: La cabecera MUST mostrar la marca tipográfica "LEAGUEFLOW", el
  indicador de la liga en contexto y el estado de sesión (nombre de usuario y
  rol si hay sesión; acceso a iniciar sesión si no la hay).
- **FR-003**: La navegación MUST ofrecer las secciones Dashboard, Equipos,
  Jugadores, Partidos, Tabla y Estadísticas.
- **FR-004**: La sección correspondiente a la pantalla actual MUST distinguirse
  visualmente y MUST estar identificada además por medios no cromáticos.
- **FR-005**: En anchos de pantalla reducidos la navegación MUST colapsarse y
  MUST seguir siendo alcanzable y operable mediante un control visible.
- **FR-006**: Cuando no exista una liga en contexto, el indicador de liga MUST
  comunicarlo explícitamente y la navegación de secciones de liga MUST NOT
  presentarse como una lista de elementos deshabilitados: en su lugar la
  estructura MUST ofrecer un acceso directo al listado de ligas, de modo que
  ninguna sección conduzca a una pantalla rota.

#### Componentes reutilizables

- **FR-007**: El sistema MUST definir una sola vez, y reutilizar en todas las
  pantallas, los siguientes componentes: panel/tarjeta con título, tabla de
  datos, fila de marcador, distintivo de estado de partido, botón con jerarquía
  primaria/secundaria/destructiva, campo de formulario con etiqueta, texto de
  ayuda y mensaje de error, y destacado de posiciones de podio.
- **FR-008**: La tabla de datos MUST presentar encabezado diferenciado, filas
  alternas y alineación a la derecha de los valores numéricos.
- **FR-009**: La fila de marcador MUST usar el formato "LOCAL 3 — 1 VISITANTE"
  de forma idéntica en todas las vistas que muestren un resultado.
- **FR-010**: El distintivo de estado de partido MUST cubrir los estados
  programado, en curso, finalizado y cancelado, y MUST identificar el estado
  por su texto además de por su color.
- **FR-011**: Los listados de líderes y la clasificación MUST destacar las
  posiciones 1.ª, 2.ª y 3.ª respecto del resto de filas.
- **FR-012**: Cuando un equipo no tenga escudo disponible, el sistema MUST
  mostrar un sustituto con las iniciales del equipo, ocupando el mismo espacio
  que un escudo presente.

#### Estados de interfaz

- **FR-013**: Toda pantalla que cargue datos MUST disponer de tres estados
  explícitos: carga, vacío y error.
- **FR-014**: El estado vacío MUST incluir un mensaje que indique qué hacer a
  continuación, ajustado a lo que el usuario actual puede realmente hacer.
- **FR-015**: El estado de error MUST mostrar un mensaje comprensible en
  español y MUST NOT exponer detalles técnicos internos, trazas, códigos
  crudos ni mensajes originados en el servidor sin traducir.
- **FR-016**: Tras un error, la aplicación MUST seguir siendo navegable: la
  estructura de aplicación permanece disponible y el usuario puede ir a otra
  sección.
- **FR-017**: Los formularios MUST mostrar los errores de validación junto al
  campo afectado y asociados a él.
- **FR-018**: Los formularios MUST bloquear el reenvío mientras haya un envío
  en curso, y MUST desbloquearse al terminar la operación, tanto si tuvo éxito
  como si falló.

#### Consistencia

- **FR-019**: Colores, tipografía, espaciado, bordes y sombras MUST definirse
  como un conjunto único de valores reutilizables, compartido por toda la
  aplicación.
- **FR-020**: Las pantallas individuales MUST NOT definir su propia paleta, sus
  propias tipografías ni sus propios tamaños ad hoc fuera de ese conjunto
  único.
- **FR-021**: El idioma de toda la interfaz MUST ser español.
- **FR-022**: Los formatos de fecha y de hora MUST ser uniformes en todas las
  vistas.

#### Accesibilidad

- **FR-023**: El contraste de todo texto respecto a su fondo MUST ser de al
  menos 4.5:1.
- **FR-024**: Todo elemento interactivo MUST presentar un indicador de foco
  visible.
- **FR-025**: Toda funcionalidad MUST ser alcanzable y operable únicamente con
  el teclado.
- **FR-026**: Todo campo de formulario MUST tener una etiqueta asociada.
- **FR-027**: Cada pantalla MUST tener una estructura semántica con un
  encabezado principal y regiones identificables de cabecera, navegación y
  contenido.
- **FR-028**: El sistema MUST NOT transmitir ninguna información únicamente
  mediante color.

#### Adaptabilidad

- **FR-029**: La aplicación MUST ser usable y legible a 1280 px, 768 px y
  375 px de ancho.
- **FR-030**: La página MUST NOT producir desplazamiento horizontal en ninguno
  de esos anchos; las tablas más anchas que el espacio disponible MUST desplazarse
  dentro de su propio contenedor.

#### Alcance y no regresión

- **FR-031**: El sistema visual MUST aplicarse a todas las pantallas ya
  implementadas: inicio de sesión; ligas (listado, detalle, creación); equipos
  (listado, creación); jugadores (listado, creación); partidos (listado,
  detalle, programación, registro de resultado, solicitud y decisión de
  corrección, registro de goles, alineaciones); calendario y resultados;
  clasificación; dashboard general de la liga (`specs/011`); y estadísticas
  —tabla de goleadores y ficha individual de jugador (`specs/010`)—.
- **FR-032**: Esta historia MUST NOT modificar reglas de negocio, contratos de
  API, entidades, campos ni esquema de base de datos.
- **FR-033**: Toda la suite de pruebas automatizadas existente MUST seguir en
  verde. Si un selector de prueba debe cambiar por el nuevo marcado, MUST
  actualizarse en el mismo Pull Request, prefiriendo selectores accesibles por
  rol y etiqueta.

#### Marco de aplicación (FR-040 a FR-046)

- **FR-040**: Toda la aplicación MUST presentarse dentro de un marco único: un
  lienzo claro que enmarca una superficie de marca redondeada, dentro de la
  cual viven la navegación, la cabecera de pantalla y el contenido.
- **FR-041**: Cada sección de la navegación MUST llevar, además de su etiqueta,
  una marca visual no textual propia, y la sección activa MUST distinguirse por
  relleno, filete de acento y peso tipográfico —tres canales— además del color.
- **FR-042**: Cada pantalla MUST presentar una cabecera de contenido con el
  estado de sesión y el título de la pantalla como encabezado principal.
- **FR-043**: Paneles y tarjetas MUST leerse como superficies claras elevadas
  sobre la superficie de marca.
- **FR-044**: Ningún texto colocado directamente sobre la superficie de marca
  MUST usar los colores de texto pensados para superficies claras; el sistema
  MUST declarar los colores de texto propios de la superficie de marca.
- **FR-045**: El color de acento MUST emplearse como texto únicamente sobre las
  superficies de marca en las que alcanza el umbral de FR-023; sobre las demás
  MUST limitarse a relleno, filete o marca decorativa.
- **FR-046**: La portada MUST permitir elegir la liga de trabajo desde la
  propia pantalla, listando las ligas realmente disponibles.

#### Portada y expresividad visual

- **FR-034**: La pantalla de inicio (`/`) MUST presentar una portada de
  producto compuesta por un bloque principal con la marca y la propuesta de
  valor, una acción principal coherente con el estado de sesión (iniciar
  sesión si no la hay, ir a las ligas si la hay) y una presentación de las
  secciones que ofrece el producto.
- **FR-035**: La portada MUST NOT introducir contratos de API nuevos: todo
  dato real que muestre MUST provenir de endpoints ya publicados por
  `specs/001` a `specs/009`.
- **FR-036**: El conjunto único de valores visuales (FR-019) MUST incluir,
  además de los colores planos, los degradados de marca y los niveles de
  elevación que usen las pantallas; ninguna pantalla MUST declarar un
  degradado o una sombra propios.
- **FR-037**: El sistema MUST definir un color de acento distinto del color de
  acción y del color de peligro, reservado a destacar datos e identidad. El
  color de peligro MUST seguir reservado a error y acción destructiva.
- **FR-038**: Todo texto que se muestre sobre una superficie con degradado
  MUST declarar su contraste contra un color sólido equivalente del sistema,
  de forma que FR-023 siga siendo verificable de manera automática.
- **FR-039**: Paneles, tarjetas y navegación MUST compartir el mismo
  tratamiento de superficie —radio, borde y elevación— en todas las pantallas
  del alcance.

### Key Entities

Esta historia **no introduce entidades de datos**: no hay persistencia, ni
campos nuevos, ni migraciones. Las siguientes son piezas de vocabulario de la
capa de presentación, definidas aquí para que `specs/010` y `specs/011` las
hereden sin volver a decidirlas:

- **Sistema de valores visuales**: conjunto único y compartido de colores,
  tipografía, escala de espaciado, radios de borde y sombras. Fuente única de
  verdad del aspecto de la aplicación.
- **Estructura de aplicación (shell)**: cabecera de marca + indicador de liga +
  estado de sesión, más la navegación de secciones y el área de contenido.
- **Liga en contexto**: la liga a la que pertenece la pantalla actual, mostrada
  en la cabecera. Se deriva de la navegación; no se persiste ni se modela.
- **Catálogo de componentes**: panel con título, tabla de datos, fila de
  marcador, distintivo de estado de partido, botón (primario, secundario,
  destructivo), campo de formulario (etiqueta, ayuda, error) y destacado de
  podio.
- **Estados de pantalla**: carga, vacío y error, con su mensaje asociado en
  español.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las pantallas ya implementadas presenta la misma
  cabecera de marca y la misma navegación de secciones. En las pantallas que
  pertenecen a una liga, además, la sección actual queda resaltada, y **solo
  una** a la vez; en las pantallas sin liga en contexto (inicio de sesión,
  listado y creación de ligas) ninguna sección aparece como activa.
- **SC-002**: El 100% de las pantallas que cargan datos ofrece los tres estados
  de carga, vacío y error, cada uno con su mensaje en español.
- **SC-003**: Ningún mensaje de error visible al usuario contiene detalles
  técnicos internos, trazas ni texto sin traducir: 0 casos en la revisión de
  todas las pantallas del alcance.
- **SC-004**: El 100% del texto de la interfaz alcanza una relación de
  contraste de al menos 4.5:1 contra su fondo.
- **SC-005**: Un usuario que solo utiliza el teclado puede completar de
  principio a fin las tareas de iniciar sesión, crear un equipo y registrar un
  resultado, viendo el foco en todo momento.
- **SC-006**: A 1280 px, 768 px y 375 px de ancho, ninguna de las pantallas del
  alcance produce desplazamiento horizontal de la página.
- **SC-007**: Un usuario que no conoce la aplicación identifica el estado de un
  partido y las tres primeras posiciones de la clasificación sin ayuda y sin
  recurrir al color.
- **SC-008**: La suite de pruebas automatizadas existente permanece al 100% en
  verde tras aplicar el sistema visual, sin pruebas eliminadas, saltadas ni
  debilitadas.
- **SC-009**: Los valores de color, tipografía, espaciado, borde y sombra
  provienen de un único conjunto compartido: 0 definiciones de paleta o de
  tamaños propios en pantallas individuales.
- **SC-010**: `specs/010` y `specs/011` pueden construir sus pantallas usando
  exclusivamente el catálogo de componentes y los valores visuales definidos
  aquí, sin necesidad de tomar decisiones de estilo nuevas.

- **SC-011**: La pantalla de inicio presenta marca, propuesta de valor y una
  acción principal coherente con el estado de sesión; en las pantallas sin
  liga en contexto la navegación muestra **0** secciones deshabilitadas.
- **SC-012**: Degradados y elevaciones provienen del conjunto único de
  valores: **0** degradados y **0** sombras declarados fuera de él.

- **SC-013**: En las pantallas del alcance, **0** textos quedan con color de
  superficie clara sobre la superficie de marca, y **0** pares texto/fondo
  nuevos quedan sin declarar en el conjunto único de valores.
- **SC-014**: Un usuario sin liga en contexto llega a una liga desde la portada
  en **una** interacción.

## Assumptions

Asunciones tomadas al redactar esta especificación, en ausencia de una
definición explícita:

- **Tema único**: existe un solo tema claro. El modo oscuro queda fuera de
  alcance.
- **Marca tipográfica**: la marca es exclusivamente tipográfica. No existe un
  logotipo propio ni se han entregado activos de diseño.
- **Escudos de equipo**: son enlaces externos. Cuando falten —o cuando el
  enlace exista pero no cargue— se muestra un sustituto con las iniciales del
  equipo.
- **Activos alojados**: no se alojan imágenes ni fuentes propias en el
  repositorio si puede evitarse.
- **Referencia visual**: la referencia obligatoria es el mockup ASCII del
  dashboard de `docs/enunciado.md` §2 y las capturas de ese mismo documento;
  se toman como guía de estructura y jerarquía, no como especificación de
  píxeles. Sobre esa estructura —cabecera de marca, navegación lateral de seis
  secciones y área de contenido en paneles— se aplica un tratamiento visual
  más expresivo (superficies claras sobre fondo azul acero, tarjetas
  elevadas, degradados de marca) inspirado en las referencias de estilo
  aportadas por el equipo. La estructura del mockup no se altera: cambia el
  acabado, no la disposición.
- **Maqueta de referencia del marco**: el equipo aportó una maqueta navegable
  (`LeagueFlow Wow`, hecha con Claude Design) que fija el marco de aplicación,
  la barra lateral sobre superficie de marca, la cabecera de pantalla y el
  tratamiento de tarjetas. Se toma como referencia de **disposición y color**,
  no como inventario de funcionalidad. Lo que la maqueta dibuja y esta historia
  **no** implementa, con su razón:
  - **Buscador global y campana de notificaciones**: no existe contrato de API
    que los sirva y FR-032/FR-035 prohíben inventarlo. Se omiten en lugar de
    dibujar controles que no hacen nada. Es la única pieza de la cabecera de
    la maqueta que no se reproduce: el saludo ("Hola, {usuario} · {rol}"),
    el badge de liga con sus iniciales y el botón "Cambiar liga" sí están,
    porque todos se derivan de datos ya publicados (`specs/001` y
    `specs/002`).
  - **Tarjetas de dashboard con datos agregados** (próximo partido,
    rendimiento de la temporada, goles por jornada, contadores de equipos y
    jugadores, porcentaje completado): eran el alcance de
    `specs/011-dashboard-liga`, que en el momento de redactar esta historia no
    estaba entregada. `specs/011` se entregó después y se integró aquí: el
    Dashboard navega a `DashboardPage` (`/leagues/:id/dashboard`) y esa
    pantalla reproduce las tarjetas de la maqueta —construidas enteramente
    sobre el catálogo de componentes y los valores visuales de esta historia
    (SC-010), sin publicar ningún contrato de API nuevo (FR-032/FR-035)—
    combinando en el cliente los endpoints ya publicados por `specs/003`
    (equipos), `specs/005` (partidos) y el propio resumen de `specs/011`.
    Donde el dominio no tiene el campo que la maqueta da por hecho, la
    tarjeta se adapta en vez de inventarlo:
    - No hay "jornada" ni "cancha" en `Match` (`specs/005`): "Goles por
      jornada" se muestra como **"Goles por fecha"**, agrupando por la fecha
      real del calendario; el bloque "Próximo partido" no muestra número de
      jornada ni sede.
    - "Rendimiento de la temporada" conserva su título, su barra segmentada
      de tres colores y su grid de cuatro métricas, pero **no** puede rotular
      "GANADOS / EMPATES / PERDIDOS": ese es el balance de *un* equipo. A
      nivel de liga cada victoria es a la vez la derrota de alguien, así que
      "ganados" y "perdidos" serían siempre el mismo número y la barra no
      significaría nada. El equivalente correcto —y que sí suma el total— es
      cómo se repartieron los partidos jugados: **Jugados / Gana local /
      Empates / Gana visitante**, derivado de `home_score` vs `away_score`
      de los partidos finalizados (`specs/005`, `specs/006`).
    - Estadísticas navega a la tabla de goleadores de `specs/010`
      (`/leagues/:id/top-scorers`), entregada en el mismo lote que
      `specs/011`.
    El feed "Última actividad" de la maqueta no tiene endpoint que lo sirva
    en ninguna spec entregada y sigue sin implementarse.
    `specs/011` sí publicaba, además, dos listas propias —"Últimos
    resultados" y "Próximos partidos", hasta 5 filas cada una— que la
    maqueta de referencia **no dibuja**: "Próximo partido" ya resuelve "qué
    sigue" con la primera fila de `upcoming_matches`. Mantener las tres
    tarjetas a la vez leía como el mismo dato repetido dos veces seguidas.
    Se retiraron ambas listas del panel para igualar la maqueta; los datos
    siguen accesibles desde "Ver calendario" (enlace de la propia tarjeta
    "Próximo partido", hacia `/leagues/:id/matches`) sin necesidad de una
    tarjeta de resumen adicional. Cada tarjeta que en la maqueta lleva un
    enlace de cabecera (`acciones` de `Panel`, ya parte del catálogo) navega
    a un destino real: "Ver calendario" (`/leagues/:id/matches`), "Ver
    estadísticas" (`/leagues/:id/top-scorers`, la única pantalla de
    estadísticas de liga que existe) y "Ver tabla completa"
    (`/leagues/:id/standings`).
  - **Números de "Estado de la temporada" en el color de su segmento**: la
    maqueta pinta "GANADOS"/"EMPATES"/"PERDIDOS" en verde/ámbar/rojo, a
    juego con la barra. Se conserva ese refuerzo visual sobre las etiquetas
    ya adaptadas (Jugados/Programados/Cancelados): el texto identifica el
    dato (FR-028), el color solo lo refuerza. Añade dos pares nuevos a la
    auditoría de contraste de FR-023 (`exito sobre superficie`, `aviso sobre
    superficie`, en `styles/tokens.css`), ambos por encima de 7:1.
  - **Fotografía de acción**: la propia maqueta la marca como hueco
    (`foto de acción · 1200×1400`). Se sustituye por el patrón de franjas
    diagonales que la maqueta usa de relleno, generado en CSS.
  - **Métricas de la portada**: solo las derivables del listado de ligas que ya
    publica `specs/002`. No se muestran contadores de equipos o jugadores
    globales porque exigirían un endpoint agregador que no existe.
  - **Secciones deshabilitadas con candado**: la maqueta las dibuja; esta
    historia mantiene FR-006 enmendado (no listarlas), que es una decisión
    explícita del equipo y prevalece sobre la maqueta.
- **Sin activos fotográficos**: las referencias de estilo aportadas incluyen
  fotografía a sangre. No se dispone de esos activos ni de su licencia, así
  que el bloque principal de la portada se resuelve con degradados y formas
  vectoriales generados en CSS, coherente con la asunción "Activos alojados".
- **Acento de identidad**: el acento cálido se usa para destacar datos e
  identidad. El azul sigue siendo el color de acción (botones, enlaces,
  sección activa) y el rojo sigue reservado a error y acción destructiva, para
  no reabrir el contraste ya verificado de formularios y avisos (FR-037).
- **Secciones ya construidas**: Dashboard y Estadísticas aparecen en la
  navegación desde el primer momento, por fidelidad al mockup. Al redactar
  esta historia, `specs/011-dashboard-liga` y `specs/010-alineaciones-estadisticas`
  no estaban entregadas y esas secciones mostraban un estado explícito de
  "aún no disponible" (`PendienteDeEntrega`) en lugar de un destino roto.
  Ambas specs se entregaron después y esta historia se actualizó para
  integrarlas: Dashboard navega a `/leagues/:id/dashboard` (`DashboardPage`,
  `specs/011`) y Estadísticas a `/leagues/:id/top-scorers` (`TopScorersPage`,
  `specs/010`). El componente `PendienteDeEntrega` se retiró por no tener ya
  ningún destino que cubrir; las seis secciones del mockup navegan hoy a una
  pantalla real (FR-006).
- **Alcance de la sección Jugadores**: los jugadores se consultan por equipo
  según las rutas ya publicadas por `specs/004`. La sección Jugadores conduce
  al camino existente de selección de equipo; no se crea una vista agregada de
  jugadores por liga, que sería una pantalla nueva y queda fuera de alcance.
- **Liga en contexto**: se deriva de la pantalla que se está viendo, no de una
  preferencia guardada. En pantallas sin liga (inicio de sesión, listado y
  creación de ligas) el indicador comunica que no hay liga seleccionada.
- **Textos largos**: los nombres que exceden el espacio disponible se truncan
  visualmente conservando el texto completo accesible, para no romper la
  alineación de las tablas.
- **Estados vacíos según permisos**: la acción sugerida del estado vacío se
  ajusta a lo que el usuario actual puede hacer; a un espectador se le informa
  del estado sin ofrecerle una acción que no tiene permitida.
- **Podio con menos de tres equipos**: se destacan únicamente las posiciones
  existentes.
- **`specs/009` ya integrada**: el registro de goles está entregado en `main`,
  por lo que sus pantallas forman parte del alcance a cubrir (FR-031) y no de
  las pendientes.
- **Suite existente**: las pruebas unitarias y de componente actuales del
  frontend son el criterio de no regresión de FR-033; los ajustes de
  selectores se hacen hacia consultas por rol y etiqueta accesibles. Las
  verificaciones que no se automatizan en este proyecto —recorrido solo con
  teclado (SC-005) y los tres anchos de pantalla (SC-006)— se hacen de forma
  manual reproducible según la guía de validación de la historia.

## Out of Scope

- Nuevas pantallas o funcionalidades de negocio.
- Modo oscuro y personalización de tema por liga.
- Internacionalización a otros idiomas.
- Animaciones o transiciones elaboradas: se admiten transiciones breves de
  estado (foco, `:hover`, apertura de la navegación), nunca animación
  decorativa continua ni movimiento que ignore `prefers-reduced-motion`.
- Fotografía, ilustración e iconografía alojadas en el repositorio.
- Rediseño o cambio de los contratos de la API publicados por `specs/001` a
  `specs/009`.
- Cambios de esquema y migraciones.
- Todo lo listado en "Qué NO construiría" del enunciado (`docs/enunciado.md`
  §18): apuestas, streaming, chat, aplicación móvil nativa, múltiples
  deportes, microservicios, notificaciones push, pagos, predicciones con ML,
  mapas, tracking GPS y WebSockets.
