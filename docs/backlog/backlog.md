# Backlog detallado — LeagueFlow

**Estado**: Documento de referencia (no es una spec de Spec Kit)

**Creado**: 2026-08-18 · **Superseded**: 2026-08-18

**Origen**: `Input` original — "Construir LeagueFlow, una plataforma web para que un organizador de liga universitaria/amateur gestione equipos, jugadores, partidos y consulte clasificación y estadísticas. Roles: Organizador/Administrador (principal), Operador (registra resultados/eventos) y Espectador (consulta información pública). Modelo de dominio League -> Teams -> Players y League -> Matches -> MatchEvents. Standings y estadísticas de jugadores siempre derivadas de los resultados. 15 Historias de Usuario priorizadas (Must/Should/Could)."

> Este documento fue la spec inicial `specs/001-gestion-ligas/spec.md`, ya
> clarificada (ver sección Clarifications abajo). El equipo decidió que cada
> Historia de Usuario tiene su propia spec de Spec Kit en `specs/NNN-*/`, así
> que este archivo se movió aquí como **backlog de referencia**: de dónde
> salió cada requisito y por qué, para consultar al escribir cada spec
> individual. **No se planifica ni se implementa desde aquí.**
>
> Mapa hacia las specs reales:
>
> | Este documento | Spec activa |
> |---|---|
> | User Story 16 (HU-AUTH) | `specs/001-fundacion-y-autenticacion/` |
> | User Story 1 (HU01) | `specs/002-crear-liga/` |
> | User Story 2 (HU02) | `specs/003-registrar-equipos/` |
> | User Story 3 (HU03) | `specs/004-registrar-jugadores/` |
> | User Story 4 (HU04) | `specs/005-programar-partido/` |
> | User Story 5 (HU05) | `specs/006-registrar-resultado/` |
> | User Story 6 (HU06) | `specs/007-consultar-calendario/` |
> | User Story 7 (HU07) | `specs/008-consultar-clasificacion/` |
> | User Story 8 (HU08) | `specs/009-registrar-goles/` |
> | User Story 9 (HU09) | `specs/010-alineaciones-estadisticas/` |
> | User Story 10 (HU10) | `specs/011-dashboard-liga/` |
> | User Story 11 (HU11) — Identidad visual | `specs/012-identidad-visual/` |
> | User Story 12 (HU12) — Grupos/divisiones | `specs/013-grupos-divisiones/` |
> | User Story 13 (HU13) — Tarjetas y sanciones | `specs/014-tarjetas-sanciones/` |
> | User Story 14 (HU14) — Exportación a CSV | `specs/015-exportacion-csv/` |
> | User Story 15 (HU15) — Auditoría de operaciones | `specs/016-auditoria/` |
> | User Story 16 (HU16) — Bloqueo de login | `specs/017-bloqueo-login/` |
>
> Las specs `013` a `017` son las cinco historias del **trabajo en paralelo**
> (Demo Day): cada una vive en su propia zona y no comparte archivo de código
> con las demás. Los slugs de directorio son provisionales hasta que
> `/speckit-specify` cree cada carpeta.

## Clarifications

### Session 2026-08-18

- **Q: ¿Qué forma toma el flujo explícito de corrección de resultados de un partido
  finalizado (HU05)?** → A: Solicitud de corrección aprobada por el organizador. El
  operador propone el nuevo marcador con un motivo; el resultado y la clasificación
  solo cambian cuando el organizador aprueba la solicitud.
- **Q: ¿De dónde salen los "partidos jugados" de un jugador (HU09), si el modelo de
  eventos solo registra goles?** → A: Se registra la alineación (jugadores que
  participaron) de cada partido, y los partidos jugados se derivan de ella.
- **Q: ¿Qué nivel de autenticación se implementa para las operaciones de escritura?**
  → A: Autenticación real con usuarios, contraseña y sesión; cada usuario tiene un rol
  asignado. Esto añade la historia de usuario HU-AUTH (User Story 17), que no estaba en
  el backlog original y es un habilitador P1.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Crear una liga (Priority: P1)

Como organizador, quiero crear una liga para tener un contenedor donde registrar
equipos, jugadores y partidos.

**Why this priority**: La liga es la raíz del modelo de dominio. Sin ella no existe
contexto para ninguna otra entidad, así que ninguna otra HU puede entregarse antes.

**Independent Test**: Crear una liga con nombre y temporada, y verificar que aparece
en el listado de ligas y que se puede abrir su ficha vacía.

**Acceptance Scenarios**:

1. **Given** que no existe ninguna liga, **When** el organizador crea una liga con
   nombre y temporada válidos, **Then** la liga queda registrada y visible en el
   listado.
2. **Given** que ya existe una liga con el nombre "Interfacultades 2026",
   **When** el organizador intenta crear otra con el mismo nombre y temporada,
   **Then** el sistema rechaza la creación e informa que el nombre ya está en uso.
3. **Given** el formulario de creación, **When** el organizador envía el nombre vacío,
   **Then** el sistema rechaza la creación e indica qué campo falta.

---

### User Story 2 - Registrar equipos en una liga (Priority: P1)

Como organizador, quiero registrar equipos dentro de una liga para que puedan
participar en partidos.

**Why this priority**: Sin equipos no hay partidos ni clasificación. Es el segundo
eslabón obligatorio de la cadena de valor.

**Independent Test**: Sobre una liga existente, registrar dos equipos y verificar que
ambos aparecen en la lista de equipos de esa liga y no en la de otra liga.

**Acceptance Scenarios**:

1. **Given** una liga existente, **When** el organizador registra un equipo con nombre
   válido, **Then** el equipo queda asociado a esa liga y aparece en su listado.
2. **Given** una liga con el equipo "Ingeniería FC", **When** el organizador intenta
   registrar otro equipo con el mismo nombre en esa liga, **Then** el sistema rechaza
   el registro por nombre duplicado.
3. **Given** dos ligas distintas, **When** existe un equipo llamado "Ingeniería FC" en
   cada una, **Then** ambos son válidos y se mantienen independientes.

---

### User Story 3 - Registrar jugadores en un equipo (Priority: P1)

Como organizador, quiero registrar jugadores dentro de un equipo para llevar el
registro de la plantilla.

**Why this priority**: La plantilla es requisito para las estadísticas individuales y
para el registro de goles por jugador (HU08/HU09).

**Independent Test**: Sobre un equipo existente, registrar tres jugadores y verificar
que la plantilla del equipo los lista.

**Acceptance Scenarios**:

1. **Given** un equipo existente, **When** el organizador registra un jugador con
   nombre válido, **Then** el jugador queda asociado a ese equipo y aparece en su
   plantilla.
2. **Given** un equipo donde ya existe un jugador con dorsal 10, **When** el
   organizador registra otro jugador con dorsal 10 en el mismo equipo, **Then** el
   sistema rechaza el registro por dorsal duplicado.
3. **Given** un jugador registrado en el equipo A, **When** se consulta la plantilla
   del equipo B de la misma liga, **Then** ese jugador no aparece.

---

### User Story 4 - Programar un partido (Priority: P1)

Como organizador, quiero crear y programar un partido entre dos equipos de la misma
liga para planificar el calendario.

**Why this priority**: El partido es la unidad que produce resultados; sin él no hay
clasificación ni estadísticas.

**Independent Test**: Crear un partido entre dos equipos de una liga con fecha futura
y verificar que aparece en el calendario con estado "programado".

**Acceptance Scenarios**:

1. **Given** una liga con los equipos A y B, **When** el organizador programa un
   partido A vs B con fecha y hora, **Then** el partido queda creado en estado
   programado, sin marcador.
2. **Given** una liga con el equipo A, **When** el organizador intenta programar el
   partido A vs A, **Then** el sistema rechaza la creación porque un equipo no puede
   enfrentarse a sí mismo.
3. **Given** el equipo A en la liga 1 y el equipo C en la liga 2, **When** el
   organizador intenta programar A vs C, **Then** el sistema rechaza la creación
   porque ambos equipos deben pertenecer a la misma liga que el partido.

---

### User Story 5 - Registrar y corregir el resultado de un partido (Priority: P1)

Como operador, quiero registrar el resultado de un partido (goles de cada equipo)
para que se refleje en la clasificación, y quiero poder proponer una corrección
cuando el resultado registrado sea erróneo.

**Why this priority**: Es el evento que alimenta toda la analítica del sistema. Sin
resultados, la clasificación y las estadísticas están vacías.

**Independent Test**: Registrar el marcador de un partido programado y verificar que
el partido queda finalizado con ese marcador y que la clasificación cambia; después,
proponer una corrección y verificar que solo se aplica tras la aprobación del
organizador.

**Acceptance Scenarios**:

1. **Given** un partido programado, **When** el operador registra 3-1, **Then** el
   partido pasa a estado finalizado con ese marcador y la clasificación se actualiza.
2. **Given** un partido programado, **When** el operador intenta registrar un marcador
   negativo, **Then** el sistema rechaza el registro porque los goles deben ser
   enteros mayores o iguales a cero.
3. **Given** un partido ya finalizado con marcador 3-1, **When** el operador intenta
   sobrescribir el marcador directamente, **Then** el sistema rechaza la operación e
   indica que debe crear una solicitud de corrección.
4. **Given** un partido finalizado con marcador 3-1, **When** el operador crea una
   solicitud de corrección a 2-1 con motivo, **Then** la solicitud queda pendiente y
   el partido conserva el marcador 3-1 y su aporte a la clasificación.
5. **Given** una solicitud de corrección pendiente, **When** el organizador la
   aprueba, **Then** el partido pasa a tener el marcador corregido y la clasificación
   y las estadísticas quedan recalculadas.
6. **Given** una solicitud de corrección pendiente, **When** el organizador la
   rechaza indicando el motivo, **Then** el resultado original se mantiene intacto y
   la solicitud queda cerrada como rechazada.
7. **Given** una solicitud de corrección pendiente sobre un partido, **When** se
   intenta crear una segunda solicitud sobre el mismo partido, **Then** el sistema la
   rechaza porque solo puede haber una solicitud pendiente por partido.
8. **Given** una solicitud creada por un operador, **When** ese mismo usuario intenta
   aprobarla, **Then** el sistema rechaza la operación: aprobar es competencia del
   organizador.
9. **Given** un partido con correcciones aplicadas, **When** se consulta su historial,
   **Then** se ven el marcador anterior, el nuevo, el motivo, quién solicitó, quién
   decidió y las fechas.

---

### User Story 6 - Consultar el calendario y los resultados (Priority: P1)

Como espectador, quiero consultar los partidos jugados y próximos de una liga para
saber el calendario y los resultados.

**Why this priority**: Es la vista pública mínima que da valor a los espectadores y
cierra el ciclo "registrar → consultar".

**Independent Test**: Con una liga que tiene partidos finalizados y programados,
consultar la vista de partidos y verificar que ambos grupos se muestran correctamente
ordenados.

**Acceptance Scenarios**:

1. **Given** una liga con partidos finalizados y programados, **When** el espectador
   consulta los partidos, **Then** ve los próximos ordenados por fecha ascendente y
   los jugados con su marcador, ordenados por fecha descendente.
2. **Given** una liga sin partidos, **When** el espectador consulta los partidos,
   **Then** ve un mensaje de estado vacío en vez de un error.
3. **Given** una liga con partidos, **When** el espectador filtra por estado,
   **Then** solo se muestran los partidos de ese estado.

---

### User Story 7 - Consultar la clasificación (Priority: P1)

Como espectador, quiero consultar la tabla de posiciones de una liga para conocer el
desempeño de los equipos.

**Why this priority**: Es el entregable analítico central del producto y la razón por
la que un organizador adopta la plataforma.

**Independent Test**: Con una liga que tiene al menos tres partidos finalizados,
consultar la clasificación y verificar puntos, diferencia de goles y orden.

**Acceptance Scenarios**:

1. **Given** que el equipo A derrotó al equipo B, **When** se consulta la
   clasificación, **Then** A recibe 3 puntos y B recibe 0 puntos.
2. **Given** que dos equipos empataron, **When** se consulta la clasificación,
   **Then** ambos reciben 1 punto.
3. **Given** dos equipos con los mismos puntos, **When** se consulta la clasificación,
   **Then** el de mayor diferencia de goles aparece primero.
4. **Given** dos equipos con los mismos puntos y la misma diferencia de goles,
   **When** se consulta la clasificación, **Then** el de más goles a favor aparece
   primero.
5. **Given** una liga con partidos programados y finalizados, **When** se consulta la
   clasificación, **Then** solo los partidos finalizados contribuyen a los puntos.
6. **Given** una clasificación publicada, **When** cualquier usuario intenta editar
   directamente los puntos de un equipo, **Then** el sistema no ofrece ninguna vía
   para hacerlo y rechaza el intento.

---

### User Story 8 - Registrar goles por jugador (Priority: P2)

Como operador, quiero registrar los goles anotados por jugadores específicos dentro de
un partido para poder calcular goleadores.

**Why this priority**: Añade granularidad analítica sobre lo ya construido, pero la
liga funciona sin ella: la clasificación solo necesita el marcador.

**Independent Test**: Sobre un partido finalizado, registrar dos goles atribuidos a
jugadores concretos y verificar que quedan listados como eventos del partido.

**Acceptance Scenarios**:

1. **Given** un partido entre los equipos A y B, **When** el operador registra un gol
   del jugador P (plantilla de A) en el minuto 23, **Then** el evento queda asociado al
   partido, al jugador y a su equipo.
2. **Given** un partido entre A y B, **When** el operador intenta registrar un gol de
   un jugador que no pertenece ni a A ni a B, **Then** el sistema rechaza el registro.
3. **Given** un partido con alineación registrada, **When** el operador intenta
   atribuir un gol a un jugador que no aparece en ella, **Then** el sistema rechaza el
   registro.
4. **Given** un partido con marcador 3-1, **When** los goles atribuidos a jugadores no
   suman ese marcador, **Then** el sistema muestra una advertencia de inconsistencia
   sin bloquear el registro.

---

### User Story 9 - Registrar alineaciones y consultar estadísticas de jugadores (Priority: P2)

Como operador, quiero registrar qué jugadores participaron en cada partido, y como
espectador quiero consultar las estadísticas de jugadores (goles anotados, partidos
jugados) para conocer su desempeño individual.

**Why this priority**: Depende directamente de la HU08 y entrega el segundo bloque
analítico del producto. La alineación es el dato que hace derivable "partidos
jugados": sin ella, esa métrica no existe.

**Independent Test**: Registrar la alineación de dos partidos finalizados y goles de
un jugador, y verificar que la ficha del jugador muestra el conteo correcto de goles y
de partidos jugados, y que la tabla de goleadores lo ordena bien.

**Acceptance Scenarios**:

1. **Given** un partido entre A y B, **When** el operador registra la alineación con
   los jugadores participantes de cada equipo, **Then** la alineación queda asociada
   al partido y visible en su ficha.
2. **Given** un partido entre A y B, **When** el operador intenta incluir en la
   alineación a un jugador que no pertenece a ninguno de los dos equipos, **Then** el
   sistema rechaza la operación.
3. **Given** un jugador que aparece en la alineación de 3 partidos finalizados,
   **When** se consultan sus estadísticas, **Then** se muestran 3 partidos jugados.
4. **Given** un jugador con 4 goles registrados en la liga, **When** se consultan sus
   estadísticas, **Then** se muestran 4 goles anotados.
5. **Given** varios jugadores con goles, **When** se consulta la tabla de goleadores,
   **Then** aparecen ordenados por goles descendente.
6. **Given** un jugador sin goles y sin participaciones, **When** se consultan sus
   estadísticas, **Then** se muestran cero goles y cero partidos jugados en lugar de
   un error o una ficha vacía.
7. **Given** una corrección de resultado aprobada que elimina un gol, **When** se
   consultan las estadísticas del goleador, **Then** el conteo refleja la corrección.

---

### User Story 10 - Dashboard general de la liga (Priority: P2)

Como espectador, quiero un dashboard con partidos recientes, próximos partidos y los
líderes de la clasificación para tener una vista rápida del estado de la liga.

**Why this priority**: Agrega datos que ya existen; su valor es de usabilidad, no de
capacidad nueva.

**Independent Test**: Con una liga en curso, abrir el dashboard y verificar que los
tres bloques muestran datos coherentes con las vistas de detalle.

**Acceptance Scenarios**:

1. **Given** una liga con partidos finalizados y programados, **When** el espectador
   abre el dashboard, **Then** ve los últimos 5 resultados, los próximos 5 partidos y
   los 5 primeros de la clasificación.
2. **Given** una liga recién creada sin partidos, **When** el espectador abre el
   dashboard, **Then** cada bloque muestra su estado vacío sin errores.
3. **Given** un resultado recién registrado, **When** el espectador recarga el
   dashboard, **Then** el nuevo resultado y la clasificación actualizada se reflejan.

---

### User Story 11 - Identidad visual y experiencia consistente (Priority: P1)

Como cualquier usuario (espectador, operador u organizador), quiero que la aplicación
se vea y se comporte como un producto real, con una estructura de aplicación única
(cabecera de marca, indicador de liga, estado de sesión y navegación), un catálogo de
componentes reutilizables y estados explícitos de carga/vacío/error, para navegarla
con confianza y entender el estado de la liga de un vistazo.

**Why this priority**: Es la meta explícita del enunciado ("al entrar, quiero que ya
parezca un producto real"). Historia **transversal de presentación**: no introduce
reglas de negocio, contratos de API, entidades ni migraciones.

**Independent Test**: Recorrer las pantallas ya implementadas y verificar la misma
cabecera y navegación, con la sección activa resaltada por medios no cromáticos.

**Acceptance Scenarios**: definidos en `specs/012-identidad-visual/spec.md` (seis
historias internas P1–P6, FR-001 a FR-046, SC-001 a SC-014). El backlog solo registra
el enlace: la fuente de verdad es esa spec.

---

### User Story 12 - Grupos/divisiones de una liga (Priority: P2)

Como organizador, quiero agrupar los equipos de una liga en divisiones ("Grupo A",
"Grupo B") para organizar la competición por fases o categorías, y que cualquier
persona consulte la composición de cada grupo sin iniciar sesión.

**Why this priority**: Habilita fases de grupos sobre la liga ya existente; es la
pieza que abre el producto a competiciones más reales. Es un módulo nuevo
(`groups/`), sin tocar los dominios existentes.

**Independent Test**: Crear dos grupos en una liga, asignar equipos y consultar la
composición de un grupo sin sesión.

**Acceptance Scenarios**:

1. **Given** una liga con equipos registrados, **When** el organizador crea un grupo
   con nombre, **Then** el grupo queda registrado en la liga.
2. **Given** un grupo existente, **When** el organizador asigna un equipo que aún no
   pertenece a ningún grupo de esa liga, **Then** el equipo queda asociado al grupo.
3. **Given** un equipo que ya pertenece a un grupo de la liga, **When** el organizador
   intenta asignarlo a otro grupo de la misma liga, **Then** el sistema rechaza la
   operación (a lo sumo un grupo por liga).
4. **Given** un grupo con equipos asignados, **When** un visitante sin sesión consulta
   su composición, **Then** ve los equipos del grupo.
5. **Given** un equipo que no es de la liga del grupo, **When** el organizador intenta
   asignarlo, **Then** el sistema rechaza la operación.

**Nota de diseño (acordada)**: los grupos viven en un módulo nuevo `groups/` con su
propia tabla de pertenencias (`group_memberships`), sin modificar `teams/models.py`.
Lee `teams`/`leagues` por su interfaz pública de servicio.

---

### User Story 13 - Tarjetas y sanciones disciplinarias (Priority: P2)

Como operador, quiero registrar tarjetas amarillas y rojas de un partido y que el
sistema derive si un jugador queda suspendido, para llevar el control disciplinario de
la liga.

**Why this priority**: Extiende el punto de extensión `MatchEvent` (diseñado en la
HU08 para admitir tipos nuevos) y es la regla de negocio más demostrable del bloque de
trabajo paralelo.

**Independent Test**: Sobre un partido, registrar una roja directa a un jugador
participante y verificar que queda reportado como suspendido.

**Acceptance Scenarios**:

1. **Given** un partido, **When** el operador registra una tarjeta amarilla a un
   jugador participante, **Then** el evento queda registrado como `YELLOW_CARD`.
2. **Given** un partido, **When** el operador registra una tarjeta roja directa,
   **Then** el jugador queda reportado como suspendido.
3. **Given** un jugador con dos amarillas en partidos distintos, **When** se registra
   la segunda, **Then** el sistema deriva su suspensión automáticamente.
4. **Given** un partido, **When** el operador intenta registrar una tarjeta a un
   jugador que no pertenece a ninguno de los dos equipos, **Then** el sistema rechaza
   el evento.

**Nota de diseño (acordada)**: la tarjeta ES un `MatchEvent` (se amplía el CHECK
`type` de `matches/models.py`); la derivación de suspensión vive en un módulo nuevo
`sanctions/` que lee `MatchEvent` por servicio.

---

### User Story 14 - Exportación de clasificación y calendario a CSV (Priority: P3)

Como organizador, quiero descargar la clasificación y el calendario de una liga en CSV
para compartirlos fuera de la plataforma.

**Why this priority**: Utilidad de distribución sobre datos ya calculados; no persiste
nada, solo transforma. Es la historia más desacoplada del bloque.

**Independent Test**: Descargar la clasificación de una liga con partidos y verificar
que el CSV contiene las mismas filas y columnas que la vista.

**Acceptance Scenarios**:

1. **Given** una clasificación con equipos, **When** el organizador descarga el CSV,
   **Then** el archivo contiene las mismas filas, columnas y orden que la vista, con
   nombre de liga y fecha de generación.
2. **Given** un calendario con partidos, **When** el organizador descarga el CSV,
   **Then** el archivo contiene los partidos con sus equipos, fecha y estado.
3. **Given** una liga sin partidos finalizados, **When** se descarga la clasificación,
   **Then** el CSV es válido y lista los equipos en cero.

**Nota de diseño (acordada)**: sin migración; reempaqueta lo que ya exponen
`standings` y `matches` por sus servicios, sin tocar sus modelos.

---

### User Story 15 - Auditoría de operaciones administrativas (Priority: P2)

Como organizador, quiero que cada operación de escritura quede registrada con quién la
hizo, qué cambió y cuándo, para poder trazar la actividad de la liga.

**Why this priority**: Es la capacidad transversal/observabilidad del bloque de trabajo
paralelo; ningún otro spec necesita instrumentar su propio código para quedar
auditado.

**Independent Test**: Realizar una escritura autenticada y verificar que aparece en el
registro de auditoría con el actor y la acción correctos.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado, **When** realiza una operación de escritura
   exitosa, **Then** queda registrada una entrada de auditoría con actor, acción y
   fecha.
2. **Given** un organizador, **When** consulta el registro de auditoría, **Then** ve
   las entradas ordenadas por fecha.
3. **Given** un usuario sin rol suficiente, **When** intenta consultar la auditoría,
   **Then** el sistema rechaza el acceso.

**Nota de diseño (acordada)**: middleware genérico que registra las escrituras en una
tabla `audit_log`, sin instrumentar endpoint por endpoint.

---

### User Story 16 - Bloqueo tras intentos fallidos de inicio de sesión (Priority: P2)

Como sistema, quiero bloquear temporalmente una cuenta tras varios intentos fallidos de
inicio de sesión, para dificultar ataques de fuerza bruta.

**Why this priority**: Es la capacidad de seguridad del bloque de trabajo paralelo;
`auth/` es el territorio exclusivo de un solo integrante, así que no compite con
nadie más.

**Independent Test**: Fallar el login repetidamente y verificar que la cuenta queda
bloqueada y que un intento válido no la desbloquea antes de tiempo.

**Acceptance Scenarios**:

1. **Given** una cuenta y varios intentos fallidos consecutivos, **When** se supera el
   umbral, **Then** la cuenta queda bloqueada temporalmente.
2. **Given** una cuenta bloqueada, **When** el usuario intenta iniciar sesión con la
   contraseña correcta, **Then** el sistema rechaza el intento mientras dure el bloqueo.
3. **Given** una cuenta bloqueada, **When** transcurre el periodo de bloqueo, **Then**
   el usuario puede volver a intentar iniciar sesión.
4. **Given** un intento fallido, **When** se responde, **Then** el mensaje no revela si
   la cuenta existe o si está bloqueada.

**Nota de diseño (acordada)**: modifica `auth/` (el único spec que lo toca) y persiste
los intentos fallidos para sobrevivir a reinicios.

---

### User Story 17 - Autenticación y control de acceso (HU-AUTH) (Priority: P1)

Como organizador, quiero que las operaciones de escritura requieran iniciar sesión con
un usuario que tenga el rol adecuado, para que solo las personas autorizadas registren
o modifiquen información de la liga.

**Why this priority**: Habilitador P1 derivado de la clarificación Q3. Varias reglas de
negocio dependen de saber quién actúa: la aprobación de correcciones (HU05) y la
auditoría de cambios no son implementables sin identidad. No formaba parte del backlog
original de 15 HU: es alcance añadido.

**Independent Test**: Iniciar sesión como operador y verificar que puede registrar
resultados pero no aprobar correcciones ni crear ligas; iniciar sesión como
organizador y verificar que sí puede; navegar sin sesión y verificar que las vistas
públicas siguen accesibles.

**Acceptance Scenarios**:

1. **Given** un usuario con credenciales válidas, **When** inicia sesión, **Then**
   accede a las operaciones permitidas por su rol.
2. **Given** credenciales inválidas, **When** se intenta iniciar sesión, **Then** el
   acceso se rechaza con un mensaje genérico que no revela si el usuario existe.
3. **Given** un visitante sin sesión, **When** consulta calendario, clasificación,
   estadísticas o perfiles, **Then** accede sin necesidad de autenticarse.
4. **Given** un visitante sin sesión, **When** intenta cualquier operación de
   escritura, **Then** el sistema la rechaza y le solicita iniciar sesión.
5. **Given** un usuario con rol operador, **When** intenta crear una liga o aprobar una
   corrección, **Then** el sistema rechaza la operación por permisos insuficientes.
6. **Given** una sesión iniciada, **When** el usuario cierra sesión, **Then** pierde el
   acceso a las operaciones de escritura.
7. **Given** cualquier operación de escritura completada, **When** se consulta su
   registro, **Then** queda atribuida al usuario que la realizó.

---

### Edge Cases

- ¿Qué ocurre si se elimina un equipo que ya tiene partidos finalizados? La
  clasificación histórica no puede quedar inconsistente.
- ¿Qué ocurre si se elimina un jugador que tiene goles registrados o aparece en
  alineaciones ya guardadas?
- ¿Qué pasa con un partido cancelado o aplazado: cuenta o no en la clasificación?
- ¿Qué pasa si dos o más equipos empatan en puntos, diferencia de goles y goles a
  favor simultáneamente?
- ¿Qué pasa si un jugador cambia de equipo a mitad de temporada? ¿Sus goles previos
  siguen contando para el equipo anterior?
- ¿Qué ocurre al registrar un resultado de un partido cuya fecha programada aún no ha
  llegado?
- ¿Qué ocurre si se registran más goles por jugador que los del marcador oficial?
- ¿Qué se muestra en la clasificación mientras hay una solicitud de corrección
  pendiente sobre un partido ya contabilizado?
- ¿Qué ocurre si el organizador aprueba una corrección que deja el marcador idéntico al
  actual?
- ¿Qué ocurre si un gol está atribuido a un jugador y luego una corrección de alineación
  lo excluye del partido?
- ¿Qué ocurre si nunca se registra la alineación de un partido finalizado?
- ¿Qué ocurre con un equipo asignado a un grupo si ese grupo se elimina?
- ¿Qué pasa con las tarjetas acumuladas si el partido se corrige o se cancela?
- ¿Cuánto dura el bloqueo de login y cómo se desbloquea una cuenta (automático o manual)?
- ¿Se audita una escritura que falla a mitad de camino, o solo las exitosas?
- ¿Qué pasa si dos operadores registran el resultado del mismo partido al mismo tiempo?
- ¿Qué ocurre si la liga se queda sin ningún usuario con rol de organizador activo?
- ¿Qué ve un espectador al abrir una liga sin equipos ni partidos?

## Requirements *(mandatory)*

### Functional Requirements

#### Ligas

- **FR-001**: El sistema MUST permitir al organizador crear una liga con nombre y
  temporada obligatorios, y descripción opcional.
- **FR-002**: El sistema MUST rechazar la creación de una liga cuyo nombre y temporada
  coincidan con los de una liga existente.
- **FR-003**: El sistema MUST permitir listar las ligas y consultar el detalle de una
  liga.
- **FR-004**: El sistema MUST soportar la coexistencia de varias ligas independientes,
  sin que los datos de una afecten a otra.

#### Equipos

- **FR-005**: El organizador MUST poder registrar un equipo dentro de una liga con
  nombre obligatorio y, opcionalmente, escudo y colores.
- **FR-006**: El sistema MUST rechazar dos equipos con el mismo nombre dentro de la
  misma liga, y MUST permitirlos en ligas distintas.
- **FR-007**: Cada equipo MUST pertenecer exactamente a una liga.

#### Jugadores

- **FR-008**: El organizador MUST poder registrar un jugador dentro de un equipo con
  nombre obligatorio y, opcionalmente, dorsal y posición.
- **FR-009**: Cada jugador MUST pertenecer exactamente a un equipo.
- **FR-010**: El sistema MUST rechazar dos jugadores con el mismo dorsal dentro del
  mismo equipo cuando el dorsal esté informado.

#### Partidos

- **FR-011**: El organizador MUST poder programar un partido indicando liga, equipo
  local, equipo visitante y fecha/hora programada; el partido MUST nacer en estado
  programado y sin marcador.
- **FR-012**: El sistema MUST rechazar un partido donde el equipo local y el visitante
  sean el mismo equipo.
- **FR-013**: El sistema MUST rechazar un partido cuyos equipos no pertenezcan ambos a
  la liga del partido.
- **FR-014**: El sistema MUST soportar los estados de partido: programado, en curso,
  finalizado y cancelado.
- **FR-015**: El sistema MUST permitir consultar el detalle de un partido, incluyendo
  equipos, estado, marcador (si existe), alineación y eventos.

#### Resultados

- **FR-016**: El operador MUST poder registrar el resultado de un partido con goles
  del local y del visitante como enteros mayores o iguales a cero.
- **FR-017**: El registro del resultado MUST transicionar el partido a estado
  finalizado.
- **FR-018**: El sistema MUST rechazar cualquier modificación directa del marcador de
  un partido en estado finalizado.

#### Corrección de resultados

- **FR-019**: El operador MUST poder crear una solicitud de corrección sobre un partido
  finalizado, indicando el nuevo marcador propuesto y un motivo obligatorio.
- **FR-020**: Una solicitud de corrección MUST nacer en estado pendiente y MUST NOT
  alterar el marcador del partido, la clasificación ni las estadísticas mientras siga
  pendiente.
- **FR-021**: El organizador MUST poder aprobar o rechazar una solicitud de corrección
  pendiente.
- **FR-022**: Al aprobarse una solicitud, el sistema MUST sustituir el marcador del
  partido por el propuesto y MUST recalcular la clasificación y las estadísticas
  afectadas.
- **FR-023**: Al rechazarse una solicitud, el sistema MUST conservar el resultado
  original y MUST registrar el motivo del rechazo.
- **FR-024**: El sistema MUST conservar y permitir consultar el historial de
  correcciones de cada partido: marcador anterior, marcador nuevo, motivo, autor de la
  solicitud, autor de la decisión y fechas.
- **FR-025**: El sistema MUST permitir como máximo una solicitud de corrección
  pendiente por partido.
- **FR-026**: El sistema MUST impedir que el usuario que creó una solicitud de
  corrección sea quien la apruebe.

#### Consulta de partidos

- **FR-027**: El espectador MUST poder consultar los partidos de una liga separados
  entre próximos (orden ascendente por fecha) y jugados (orden descendente por fecha).
- **FR-028**: El sistema MUST permitir filtrar los partidos de una liga por estado.

#### Clasificación

- **FR-029**: El sistema MUST calcular la clasificación exclusivamente a partir de los
  resultados de los partidos finalizados. Los puntos y estadísticas de la tabla NUNCA
  se editan manualmente.
- **FR-030**: El sistema MUST NOT exponer ninguna vía (interfaz, operación o carga
  masiva) para modificar directamente los puntos, la posición o las estadísticas
  acumuladas de un equipo.
- **FR-031**: El sistema MUST asignar 3 puntos por victoria, 1 por empate y 0 por
  derrota.
- **FR-032**: La clasificación MUST mostrar, por equipo: partidos jugados, ganados,
  empatados, perdidos, goles a favor, goles en contra, diferencia de goles y puntos.
- **FR-033**: El sistema MUST ordenar la clasificación por: 1) puntos descendente,
  2) diferencia de goles descendente (GD = GF - GA), 3) goles a favor descendente.
- **FR-034**: Cuando dos equipos empaten en los tres criterios anteriores, el sistema
  MUST aplicar un desempate determinista y estable (orden alfabético por nombre de
  equipo), de modo que consultas sucesivas devuelvan siempre el mismo orden.
- **FR-035**: Los partidos cancelados MUST NOT contribuir a la clasificación.

#### Eventos de partido

- **FR-036**: El operador MUST poder registrar un gol como evento de partido,
  indicando el jugador anotador y el minuto.
- **FR-037**: El sistema MUST rechazar un evento de gol cuyo jugador no pertenezca a
  ninguno de los dos equipos del partido.
- **FR-038**: El modelo de eventos MUST admitir tipos adicionales en el futuro
  (por ejemplo tarjeta amarilla, tarjeta roja, sustitución) sin rediseñar el modelo;
  en esta versión solo se implementa el tipo gol.
- **FR-039**: Cuando la suma de goles atribuidos a jugadores no coincida con el
  marcador oficial del partido, el sistema MUST advertirlo sin bloquear el registro,
  y el marcador oficial MUST seguir siendo la fuente de verdad para la clasificación.

#### Alineaciones

- **FR-040**: El operador MUST poder registrar la alineación de un partido: el conjunto
  de jugadores que participaron, por cada uno de los dos equipos.
- **FR-041**: El sistema MUST rechazar la inclusión en la alineación de un jugador que
  no pertenezca a ninguno de los dos equipos del partido.
- **FR-042**: El sistema MUST permitir modificar la alineación de un partido mientras
  se mantenga la coherencia con los eventos ya registrados.
- **FR-043**: Cuando un partido tenga alineación registrada, el sistema MUST rechazar
  eventos de gol atribuidos a jugadores que no figuren en ella.
- **FR-044**: La alineación MUST ser opcional: un partido puede finalizarse sin ella, y
  en ese caso el sistema MUST señalarlo en la ficha del partido.

#### Estadísticas de jugadores

- **FR-045**: El sistema MUST calcular los goles de cada jugador exclusivamente a
  partir de los eventos de gol registrados.
- **FR-046**: El sistema MUST calcular los partidos jugados de cada jugador como el
  número de partidos finalizados en cuya alineación figura.
- **FR-047**: El sistema MUST NOT permitir editar directamente el conteo de goles,
  los partidos jugados ni ninguna estadística acumulada de un jugador.
- **FR-048**: El espectador MUST poder consultar la tabla de goleadores de una liga,
  ordenada por goles descendente.
- **FR-049**: El espectador MUST poder consultar la ficha estadística de un jugador
  individual.

#### Dashboard

- **FR-050**: El sistema MUST ofrecer un dashboard por liga con los últimos 5 partidos
  finalizados, los próximos 5 partidos programados y los 5 primeros de la
  clasificación.
- **FR-051**: Cada bloque del dashboard MUST mostrar un estado vacío legible cuando no
  haya datos.

#### Grupos y divisiones

- **FR-052**: El organizador MUST poder crear un grupo dentro de una liga con nombre
  obligatorio.
- **FR-053**: El organizador MUST poder asignar y desasignar equipos de la liga a un
  grupo.
- **FR-054**: Un equipo MUST poder pertenecer a lo sumo a un grupo dentro de una liga.
- **FR-055**: La composición de un grupo MUST ser consultable sin autenticación.

#### Tarjetas y sanciones

- **FR-056**: El operador MUST poder registrar una tarjeta amarilla o roja como evento
  de partido, indicando jugador y minuto.
- **FR-057**: El sistema MUST rechazar una tarjeta atribuida a un jugador que no
  pertenezca a ninguno de los dos equipos del partido.
- **FR-058**: El sistema MUST derivar la suspensión de un jugador a partir de las
  tarjetas registradas (roja directa o acumulación de amarillas).
- **FR-059**: Las sanciones MUST derivarse exclusivamente de los eventos registrados y
  MUST NOT editarse manualmente.

#### Exportación a CSV

- **FR-060**: El organizador MUST poder exportar la clasificación y el calendario de
  una liga en CSV.
- **FR-061**: El CSV de clasificación MUST contener las mismas filas, columnas y orden
  que la vista, e incluir nombre de liga y fecha de generación.
- **FR-062**: El CSV de calendario MUST contener los partidos con sus equipos, fecha y
  estado.

#### Auditoría

- **FR-063**: Toda operación de escritura exitosa MUST quedar registrada con actor,
  acción y fecha.
- **FR-064**: El registro de auditoría MUST ser consultable por un organizador, en
  orden cronológico.
- **FR-065**: La auditoría MUST capturarse de forma genérica (middleware), sin
  instrumentar cada endpoint individualmente.

#### Autenticación, roles y acceso

- **FR-066**: El sistema MUST distinguir tres roles: organizador (gestiona ligas,
  equipos, jugadores, partidos y aprueba correcciones), operador (registra
  resultados, eventos y alineaciones, y solicita correcciones) y espectador (solo
  consulta).
- **FR-067**: Toda la información de consulta (calendario, resultados, clasificación,
  estadísticas) MUST ser accesible sin autenticación.
- **FR-068**: Toda operación de escritura MUST requerir una sesión autenticada con un
  rol suficiente.
- **FR-069**: Cada usuario MUST tener credenciales propias (identificador y contraseña)
  y exactamente un rol asignado.
- **FR-070**: El sistema MUST NOT mostrar, registrar ni almacenar las contraseñas de
  forma que permitan recuperarlas en texto claro.
- **FR-071**: El usuario MUST poder cerrar sesión, y la sesión MUST expirar tras un
  periodo de inactividad.
- **FR-072**: Un usuario con rol organizador MUST poder crear cuentas de usuario y
  asignarles rol; el sistema MUST NOT permitir el autorregistro público.
- **FR-073**: El sistema MUST atribuir cada operación de escritura al usuario que la
  realizó, y esa atribución MUST estar disponible para consulta.
- **FR-074**: Un intento de operación con rol insuficiente MUST rechazarse con un
  mensaje de permisos insuficientes.
- **FR-075**: Un intento de inicio de sesión fallido MUST responder con un mensaje
  genérico que no revele si el identificador existe.
- **FR-076**: Tras superar un umbral de intentos fallidos consecutivos, el sistema
  MUST bloquear temporalmente la cuenta.
- **FR-077**: El sistema MUST rechazar el inicio de sesión de una cuenta bloqueada
  mientras dure el bloqueo, y MUST permitirlo de nuevo al transcurrir el periodo.

#### Errores y validación

- **FR-078**: Toda operación rechazada MUST devolver un mensaje comprensible que
  indique qué regla se incumplió y qué campo corregir.
- **FR-079**: El sistema MUST NOT mostrar detalles técnicos internos al usuario cuando
  ocurra un error inesperado.

### Key Entities

- **League (Liga)**: contenedor raíz de una competición. Atributos: nombre, temporada,
  descripción. Contiene equipos y partidos.
- **Team (Equipo)**: participante de una liga. Atributos: nombre, escudo, colores.
  Pertenece a una liga; contiene jugadores.
- **Player (Jugador)**: integrante de la plantilla de un equipo. Atributos: nombre,
  dorsal, posición. Pertenece a un equipo.
- **Match (Partido)**: enfrentamiento entre dos equipos de la misma liga. Atributos:
  equipo local, equipo visitante, fecha/hora programada, estado, goles del local, goles
  del visitante. Contiene alineación y eventos.
- **MatchLineup (Alineación)**: conjunto de jugadores que participaron en un partido,
  agrupados por equipo. Pertenece a un partido; es la fuente de los partidos jugados de
  cada jugador.
- **MatchEvent (Evento de partido)**: hecho ocurrido durante un partido. Atributos:
  tipo (gol; extensible a tarjeta amarilla y roja), jugador, equipo, minuto. Pertenece
  a un partido.
- **ResultCorrectionRequest (Solicitud de corrección)**: propuesta de nuevo marcador
  para un partido finalizado. Atributos: marcador propuesto, motivo, estado
  (pendiente/aprobada/rechazada), solicitante, decisor, fechas, marcador anterior.
  Pertenece a un partido.
- **User (Usuario)**: persona autenticada que opera el sistema. Atributos:
  identificador, credencial, rol (organizador u operador), estado.
- **Standings (Clasificación)**: vista derivada, por liga, con una fila por equipo
  (PJ, G, E, P, GF, GC, GD, Pts, posición). NUNCA se edita: siempre se recalcula desde
  los partidos finalizados.
- **PlayerStatistics (Estadísticas de jugador)**: vista derivada, por jugador, con
  goles anotados y partidos jugados. NUNCA se edita: siempre se recalcula desde los
  eventos y las alineaciones.
- **Group (Grupo)**: división de una liga que agrupa equipos. Atributos: nombre, liga.
  La pertenencia de un equipo se registra en una tabla aparte
  (`group_memberships`) dentro del módulo `groups/`.
- **Sanction (Sanción)**: suspensión derivada de las tarjetas de un jugador. Vista
  derivada; NUNCA se edita manualmente.
- **AuditLog (Registro de auditoría)**: entrada que documenta una operación de
  escritura. Atributos: actor, acción y fecha. Se escribe por un middleware genérico.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un organizador que usa la plataforma por primera vez logra crear una liga
  con 8 equipos y su calendario completo en menos de 20 minutos, sin ayuda externa.
- **SC-002**: Un operador registra el resultado de un partido en menos de 30 segundos
  desde que abre la ficha del partido.
- **SC-003**: La clasificación refleja el resultado de un partido inmediatamente
  después de registrarlo, sin ninguna acción manual adicional de recálculo.
- **SC-004**: En 100% de los casos, la clasificación calculada por el sistema coincide
  con la clasificación calculada manualmente a partir del mismo conjunto de resultados,
  incluidos los escenarios de desempate.
- **SC-005**: No existe ninguna vía en el producto por la que un usuario pueda alterar
  puntos, posiciones o conteos de goles sin modificar un resultado, una alineación o un
  evento de partido.
- **SC-006**: Un espectador que llega a la plataforma sin conocerla encuentra la
  clasificación de una liga en 3 interacciones o menos desde la página inicial.
- **SC-007**: Las vistas de consulta (calendario, clasificación, dashboard) se
  muestran completas en menos de 2 segundos para una liga de 20 equipos y 190 partidos.
- **SC-008**: 90% de los espectadores de una prueba de usabilidad identifican
  correctamente el líder de la liga y el máximo goleador en su primer intento.
- **SC-009**: El sistema soporta al menos 10 ligas simultáneas de 20 equipos cada una
  sin degradación perceptible de las vistas de consulta.
- **SC-010**: 100% de las operaciones rechazadas por regla de negocio muestran un
  mensaje que identifica la regla incumplida, verificado sobre el catálogo de
  validaciones de la spec.
- **SC-011**: 100% de las operaciones de escritura son rechazadas cuando se intentan
  sin sesión o con un rol insuficiente, verificado sobre el catálogo completo de
  operaciones.
- **SC-012**: 100% de los cambios de resultado sobre partidos finalizados quedan
  registrados con solicitante, aprobador, motivo y marcador anterior, sin excepción.

## Assumptions

- **Deporte único**: la liga es de fútbol (u otro deporte cuyo resultado se expresa en
  goles). No se soportan varios deportes con reglas de puntuación distintas.
- **Empates permitidos**: no existen prórrogas ni penaltis; un partido puede terminar
  en empate y así se refleja en la clasificación.
- **Grupos opcionales**: la liga puede, o no, dividirse en grupos. La presencia de
  grupos no altera la clasificación (que sigue derivando de los partidos) ni el resto
  de la operación.
- **Estados de partido**: los estados son programado, en curso, finalizado y cancelado.
  Solo los finalizados alimentan la clasificación y las estadísticas.
- **Alineación opcional**: registrar la alineación no es obligatorio para finalizar un
  partido. Los jugadores de un partido sin alineación no suman partidos jugados, y la
  ficha del partido lo indica explícitamente.
- **Coherencia alineación-eventos**: los goles solo pueden atribuirse a jugadores de la
  alineación cuando esta existe; si no existe, basta con que el jugador pertenezca a uno
  de los dos equipos.
- **Cuentas de usuario**: el sistema se despliega con una cuenta inicial de organizador;
  a partir de ahí, los organizadores crean el resto de cuentas. No hay autorregistro
  público ni registro de espectadores: el espectador es un visitante anónimo.
- **Recuperación de contraseña**: no se implementa autoservicio de recuperación en esta
  versión; un organizador restablece la credencial de un usuario.
- **Escudo del equipo**: se almacena como enlace externo. La plataforma no aloja
  archivos multimedia.
- **Jugador en un solo equipo**: un jugador pertenece a un único equipo dentro de una
  liga; el traspaso a mitad de temporada no está soportado en esta versión.
- **Eliminación de entidades con historial**: los equipos y jugadores con partidos,
  alineaciones o eventos asociados no se eliminan; se marcan como inactivos para
  preservar la integridad histórica de la clasificación.
- **Idioma**: la interfaz está en español.
- **Volumen esperado**: ligas de hasta 20 equipos, 30 jugadores por equipo y una
  temporada por liga.
- **Marcador oficial como fuente de verdad**: la clasificación se calcula desde el
  marcador del partido, no desde la suma de eventos de gol; los eventos alimentan solo
  las estadísticas individuales.

## Out of Scope

Esta versión NO incluye, de forma explícita:

- Apuestas o cualquier funcionalidad de índole económica.
- Streaming en vivo o alojamiento de video.
- Chat, comentarios o mensajería entre usuarios.
- Aplicación móvil nativa.
- Múltiples deportes simultáneos con reglas de puntuación distintas.
- Arquitectura de microservicios.
- Notificaciones push.
- Pagos, inscripciones de pago o facturación.
- Predicciones o analítica basada en machine learning.
- Mapas, sedes geolocalizadas o tracking GPS.
- Actualizaciones en tiempo real vía WebSockets.
- Exportación en PDF y generación automática de calendario round-robin (fuera del
  alcance actual; la exportación se ofrece en CSV).
- Autorregistro público de usuarios y autoservicio de recuperación de contraseña.
