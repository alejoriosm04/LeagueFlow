# Quickstart: Identidad visual y experiencia de usuario consistente

Catálogo de componentes y contrato de estilo:
[`contracts/ui-contracts.md`](./contracts/ui-contracts.md).
Tokens y estados: [`data-model.md`](./data-model.md).

Esta historia es de presentación: **no hay endpoints nuevos que probar con
`curl`**. La validación es (a) la suite de Vitest, (b) un recorrido por las
pantallas ya entregadas y (c) dos comprobaciones de accesibilidad y
adaptabilidad que no se automatizan en este proyecto ([research.md §9](./research.md)).

## Prerrequisitos

- `specs/009-registrar-goles` en `main` (ya lo está) y PostgreSQL en `head`.
- Datos de prueba con: una liga con **al menos cuatro equipos** (uno de ellos
  con `crest_url` válida, otro con `crest_url` nula y otro con una URL que no
  resuelve), partidos en los cuatro estados —programado, en curso, finalizado,
  cancelado— y una liga **vacía**, sin equipos, para el estado vacío.
- Dos sesiones a mano: una de `organizador` y una de `operador`; y el navegador
  sin sesión para el caso de espectador.

## Ejecutar

```bash
cd backend && uv run alembic upgrade head && uv run uvicorn src.main:app --reload
```

```bash
cd frontend && npm run dev
```

## Suite automatizada (gate de no regresión, FR-033 / SC-008)

```bash
cd frontend && npx vitest run
```

Línea base antes de esta historia: **9 archivos, 44 pruebas, 100% en verde**.
Al terminar la historia el total sube con las pruebas nuevas del shell, los
estados y el catálogo, y **ninguna de las 44 originales queda borrada, saltada
ni debilitada**. Dos de las pruebas nuevas son gates del sistema visual:

- **Contraste (SC-004)**: lee `src/styles/tokens.css`, calcula el ratio WCAG de
  cada par texto/fondo declarado y falla por debajo de 4.5:1.
- **Auditoría de tokens (SC-009)**: recorre los `*.module.css` y falla si algún
  archivo distinto de `tokens.css` declara un color literal.

```bash
cd frontend && npm run lint && npm run build
```

## Escenarios de validación

### Estructura de aplicación (Historia 1)

1. **Shell en todas las pantallas (AS1, FR-001, SC-001)**: recorrer inicio de
   sesión, ligas, detalle de liga, equipos, jugadores, partidos, detalle de
   partido, calendario y clasificación. Todas muestran la misma cabecera
   "LEAGUEFLOW" y la misma navegación de seis secciones.
2. **Estado de sesión (AS2, FR-002)**: con sesión, la cabecera muestra usuario
   y rol; sin sesión, muestra "Iniciar sesión". Cerrar sesión cambia el
   indicador sin recargar la página.
3. **Liga en contexto (AS3, FR-002)**: dentro de `/leagues/:id/...` la cabecera
   muestra el nombre de la liga. En `/`, `/login`, `/leagues` y `/leagues/new`
   muestra "Sin liga seleccionada".
4. **Sección activa (AS4, FR-004)**: ir de Equipos a Tabla; solo la sección
   destino queda con `aria-current="page"` y con su marca no cromática
   (marcador antes de la etiqueta + peso). Comprobarlo con el inspector, no
   solo a ojo.
5. **Sin liga (FR-006, SC-011)**: sin liga en contexto la navegación **no
   lista** las secciones —ni siquiera deshabilitadas— y ofrece en su lugar el
   acceso "Ver ligas", que desaparece si ya estás en `/leagues`. Comprobar con
   el inspector que no queda ningún `aria-disabled` dentro del `<nav>`.
6. **Secciones pendientes**: activar Dashboard y Estadísticas: se muestra la
   pantalla "aún no disponible" que nombra `specs/011` y `specs/010`, con el
   shell intacto.
6b. **Portada (FR-034, Historia 6)**: abrir `/` sin sesión — la acción
   principal es "Iniciar sesión"; iniciar sesión y volver a `/` — la acción
   principal pasa a "Ver mis ligas" y aparece el nombre de usuario. En ambos
   casos se ven la marca, la propuesta de valor y una tarjeta por sección, con
   "Próximamente" en Dashboard y Estadísticas.
6c. **Marco de aplicación (FR-040 a FR-045)**: en cualquier pantalla, la barra
   lateral, la cabecera y el contenido viven dentro de una única superficie de
   marca que llena el alto de la ventana, incluso en pantallas con poco
   contenido (p. ej. Tabla con dos equipos). Cada sección de la navegación
   lleva su propio icono, no solo su etiqueta.
6d. **Selector de ligas de la portada (FR-046, SC-014)**: en `/`, la tarjeta
   "Elige una liga para empezar" lista las ligas reales; activar una lleva a
   `/leagues/:id` en una sola interacción. Sin ligas registradas se ve el
   estado vacío, no una tarjeta rota.

### Lenguaje visual de los datos (Historia 2)

7. **Clasificación (AS1, FR-008, FR-011)**: puntos y diferencia de goles
   alineados a la derecha; filas 1.ª, 2.ª y 3.ª destacadas con su distintivo de
   texto, no solo con fondo. En una liga con dos equipos, solo se destacan las
   dos posiciones existentes.
8. **Distintivos de estado (AS2, FR-010)**: en el listado de partidos aparecen
   "Programado", "En curso", "Finalizado" y "Cancelado" como texto legible.
9. **Marcador (AS3, FR-009)**: el mismo partido finalizado se ve como
   "EAFIT 3 — 1 CES" en el listado, en el calendario y en el detalle.
10. **Escudo ausente y escudo roto (AS4, FR-012)**: el equipo sin `crest_url`
    y el equipo con URL que no resuelve muestran ambos las iniciales, ocupando
    el mismo cuadro; la columna no se desalinea.
11. **Fechas (AS5, FR-022)**: la fecha del mismo partido se lee idéntica en el
    listado, el calendario y el detalle.

### Estados de pantalla (Historia 3)

12. **Vacío (AS1, FR-014)**: abrir los equipos de la liga vacía como
    organizador: estado vacío con la acción "Registrar el primer equipo". Abrir
    la misma pantalla sin sesión: mismo estado, **sin** acción ofrecida.
13. **Error (AS2, FR-015, FR-016, SC-003)**: detener el backend y recargar la
    clasificación: mensaje en español, sin códigos ni trazas, con el shell
    disponible para navegar a otra sección. Repetir para un `404` real
    (`/leagues/<uuid-inexistente>/standings`).
14. **Carga (AS3, FR-013)**: con el backend arrancado y la red limitada desde
    las herramientas del navegador, se ve el estado de carga explícito, no un
    área en blanco.
15. **Error de campo (AS4, FR-017)**: enviar el formulario de creación de
    equipo con un nombre duplicado: el mensaje aparece junto al campo y el
    campo queda con `aria-invalid="true"`.
16. **Reenvío bloqueado (AS5, FR-018)**: pulsar dos veces seguidas el botón de
    envío: solo se registra una operación; el botón vuelve a habilitarse al
    terminar, tanto si el resultado fue éxito como si fue error.

## Verificación manual de SC-005 (solo teclado)

Sin tocar el ratón, con `Tab`, `Mayús+Tab`, `Enter` y `Espacio`:

1. Iniciar sesión como organizador.
2. Crear un equipo en la liga de prueba.
3. Registrar el resultado de un partido programado.

Durante todo el recorrido el foco debe ser visible en cada parada, incluidos
los ítems de navegación, el botón de menú en móvil y el contenedor con
desplazamiento de las tablas. Un solo salto de foco invisible falla el criterio.

## Verificación manual de SC-006 (1280 / 768 / 375 px)

Para cada una de las pantallas del alcance (FR-031), en los tres anchos:

- La página **no** desplaza en horizontal (`document.body.scrollWidth` no supera
  el ancho de la ventana).
- A 375 px la navegación está colapsada y se abre con el botón "Menú".
- Las tablas más anchas que la pantalla se desplazan **dentro de su contenedor**
  y son alcanzables con teclado.

## Comprobación de FR-032 (esta historia no toca el negocio)

```bash
git diff --stat main...012-identidad-visual -- backend/ specs/001-fundacion-y-autenticacion/ specs/002-crear-liga/
```

El diff sobre `backend/` debe ser **vacío**: sin cambios de esquema, sin
migraciones, sin contratos de API modificados.
