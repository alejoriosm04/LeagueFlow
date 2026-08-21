# Métricas — HU 009: Registrar goles por jugador

**Spec**: `specs/009-registrar-goles/spec.md` · **Responsable**: <nombre> · **Cerrada**: 2026-08-20

## Llenado por el agente (al terminar la HU, antes del PR)

| Métrica | Valor |
|---|---|
| Tareas en `tasks.md` (total) | 23 |
| Tareas completadas | 23 |
| Tests escritos (backend) | 39 funciones de prueba; 42 casos recolectados (16 unit, 8 contrato, 15 integración + 3 parametrizaciones) |
| Tests escritos (frontend) | 6 |
| Tests en verde al cerrar | 205 backend + 44 frontend (suite completa tras integrar `main` con la 008 mezclada; 169 backend + 38 frontend antes de esa integración) |
| Ciclos de corrección | 6 |
| Archivos de código creados/modificados | 14 |

**Ciclos de corrección**: cuántas veces hubo que volver sobre algo ya dado por
terminado (test que falló tras implementar, requisito mal interpretado,
refactor por un choque con otra HU). Cuenta honesta, no aspiracional: `0` es
sospechoso en una HU no trivial.

**Qué se reprocesó y por qué** (una línea por ciclo; es el dato más valioso
para la comparativa SDD vs. prompts sueltos del caso de negocio):

- `/speckit-analyze` detectó que T007 y el quickstart mandaban comprobar la clasificación con `GET /leagues/{id}/standings`, endpoint de la spec 008 que no existía en la rama porque 008 seguía sin mezclar; se sustituyó por la aserción sobre el marcador oficial del propio partido, que era el invariante disponible. Al mezclarse 008 (PR #36) se cumplió la condición que T007 dejó escrita y se añadió también la aserción sobre la clasificación.
- `/speckit-analyze` detectó que T006 pedía probar `403 insufficient_role` en un endpoint que acepta los dos únicos roles existentes: el 403 es inalcanzable ahí. Se sustituyó por afirmar el `401` anónimo y que ambos roles son aceptados.
- `/speckit-analyze` detectó que FR-004 solo tenía cobertura de diseño (CHECK y `Literal`) y ninguna prueba de comportamiento; se añadió el caso `type: "RED_CARD"` → `400`.
- La fixture nueva se escribió apoyándose en dos helpers de `conftest.py` que existen en la rama de la 008 pero no en `main`; hubo que reescribirla autocontenida, lo que además evita definiciones duplicadas al mezclar los dos PR en paralelo.
- En la fase roja, `test_registrar_goles_no_altera_el_marcador_oficial` pasaba en vacío: no afirmaba que los `POST` tuvieran éxito, así que con el endpoint ausente el marcador "no cambiaba" trivialmente. Se reforzó exigiendo `201` en cada registro.
- Limpiezas tras las compuertas: dos líneas de más de 100 caracteres que rompían Ruff E501 en las pruebas de integración.
- Al integrar `main` con la 008 ya mezclada hubo que resolver a mano un conflicto en `backend/tests/conftest.py`: las dos ramas habían añadido fixtures distintas al final del archivo. Se conservaron ambos bloques; la suite completa (205 backend + 44 frontend) quedó en verde tras la resolución. Es el mismo choque que ya se había anticipado al escribir la fixture autocontenida — la rama salió de `main` antes del squash de 008 y arrastró esa deuda hasta el final.

## Llenado por la persona (dos números, al cerrar)

| Métrica | Valor |
|---|---|
| Tiempo real de trabajo — spec + plan + tasks | <ej. 45 min> |
| Tiempo real de trabajo — implement + tests | <ej. 2 h> |
| Costo IA aproximado de la HU | <del panel de uso de tu herramienta> |

## Observaciones

`MatchEvent` ya estaba declarada en
`specs/001-fundacion-y-autenticacion/data-model.md`: esta HU la implementó sin
rediseñarla, que es exactamente lo que AGENTS.md §5 pretendía al fijar el
modelo de dominio una sola vez.

**FR-003 se entrega con una desviación aprobada en `plan.md`**: la regla de
alineación está implementada y cubierta por seis pruebas unitarias con un doble
del puerto `jugadores_alineados`, pero **no tiene cobertura de integración**
porque `MatchLineup` es entidad de `specs/010-alineaciones-estadisticas` y en
esta HU no existe forma de crear una alineación. El puerto devuelve `None`
siempre y está documentado como tal. T023 dejó el compromiso escrito en la spec
de 010: sin esa implementación y su prueba, FR-003 quedaría sin cobertura
extremo a extremo de forma permanente. **Es el punto que la revisión humana del
PR debe aprobar explícitamente.**

La migración `020b6dc9a54e` es la primera desde la 006 y confirmó el problema
que documenta AGENTS.md: el autogenerate añadió un `DROP`/`CREATE` de
`ix_leagues_unique_name_season` e `ix_teams_unique_league_name` por la
normalización `trim` → `TRIM(BOTH FROM ...)`. Se borraron a mano y se dejó
constancia en el docstring de la migración. Verificada `upgrade`/`downgrade`
sobre una base vacía creada al efecto, y `alembic check` posterior solo reporta
ese mismo falso positivo, sin diferencias sobre `match_events`.

Escenarios del quickstart verificados a mano sobre la aplicación corriendo con
datos reales (liga, dos equipos, cinco jugadores y un partido 3-1): registro de
gol con derivación del equipo desde el jugador, `401` sin sesión, `400` por
minuto negativo, `404` de partido inexistente, advertencia de descuadre visible
en la ficha con 0 de 4 goles y desaparecida al completar el 3-1, listado
público ordenado por minuto con nombres resueltos, y marcador oficial intacto
tras registrar los cuatro goles. Los escenarios 2, 3 y 6 (jugador ajeno,
alineación y partidos sin juego) quedaron cubiertos por la suite automatizada,
no por comprobación manual.

**SC-001 no se midió**: "un operador registra los goles de un partido en menos
de 1 minuto" es tiempo de una persona con cronómetro, y un agente haciendo
clics automatizados no es un proxy honesto de eso. Lo que sí se verificó es que
el flujo no tiene obstáculos: el formulario permanece utilizable entre goles y
la lista se refresca sola, sin recargar la página. La medición queda para la
persona.
