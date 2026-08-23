# Métricas — HU 017: Bloqueo tras intentos fallidos de inicio de sesión

**Spec**: `specs/017-bloqueo-login/spec.md` · **Responsable**: jonathan.sandoval · **Cerrada**: 2026-08-22

## Llenado por el agente (al terminar la HU, antes del PR)

| Métrica | Valor |
|---|---|
| Tareas en `tasks.md` (total) | 22 |
| Tareas completadas | 22 de 22 |
| Tests escritos (backend) | 12 (11 de integración + 1 de contrato) |
| Tests escritos (frontend) | 1 |
| Tests en verde al cerrar | 274 backend + 224 frontend, sin `skip` ni `xfail` |
| Ciclos de corrección | 3 |
| Archivos de código creados/modificados | 10 |

**Ciclos de corrección**: cuántas veces hubo que volver sobre algo ya dado por
terminado (test que falló tras implementar, requisito mal interpretado,
refactor por un choque con otra HU). Cuenta honesta, no aspiracional: `0` es
sospechoso en una HU no trivial.

**Qué se reprocesó y por qué** (una línea por ciclo; es el dato más valioso
para la comparativa SDD vs. prompts sueltos del caso de negocio):

- Los helpers del archivo de pruebas se escribieron con `await f(...)[0:1][0]`,
  que no hace lo que parece: `await` tiene menor precedencia que el subscript,
  así que se habría intentado indexar la corrutina. Hubo que rehacerlos con un
  helper explícito `fallar_una_vez`.
- `ruff format --check` rechazó el corte de línea manual de `_registrar_fallo`
  en `service.py`; se pasó el formateador y se volvió a verificar el linter.
- La validación manual de `quickstart.md` §6 (mensaje en la interfaz) se dio
  primero por imposible: el navegador del agente no alcanzaba el servidor de
  desarrollo. Se cerró la HU con ese paso pendiente y se compensó con una prueba
  de frontend nueva —que `login_locked` tiene mensaje propio, distinto del
  genérico y del de credenciales inválidas—. Al liberarse el puerto hubo que
  volver sobre la tarea y recorrer el paso 6 de verdad, que pasó a la primera.
  La prueba añadida se queda: cubre en CI lo que la comprobación visual solo
  demuestra una vez.

## Llenado por la persona (dos números, al cerrar)

| Métrica | Valor |
|---|---|
| Tiempo real de trabajo — spec + plan + tasks | <ej. 45 min> |
| Tiempo real de trabajo — implement + tests | <ej. 2 h> |
| Costo IA aproximado de la HU | <del panel de uso de tu herramienta> |

## Observaciones

**Lo que el SDD evitó aquí.** Las tres trampas caras de esta HU estaban
identificadas en `research.md` *antes* de escribir código, y ninguna llegó a
morder: (1) commitear el contador **antes** del `raise` de credenciales
inválidas —si se lanza primero, la sesión se descarta, el incremento se pierde
y el bloqueo no se activa nunca—; (2) comprobar el bloqueo **antes** de
verificar la contraseña, que es lo único que hace cumplir FR-003; y (3) el
UPSERT atómico en vez de `SELECT`+`UPDATE`, que habría dejado pasar un *lost
update* con intentos simultáneos. Las tres tienen hoy una prueba que las
afirma. Es el caso más claro del bloque a favor de especificar antes: los tres
fallos son silenciosos —la feature "funciona" en una prueba manual y falla bajo
carga o en el escenario que importa.

**FR-004 no necesitó código.** El desbloqueo automático es una comparación de
timestamps dentro del gate, no un job. La prueba correspondiente pasó en verde
en cuanto estuvo escrito el gate, antes de tocar nada de la Historia 2. El plan
ya lo anticipaba y lo dejó dicho para que el `0` de esa fase no pareciera un
olvido.

**El falso positivo de Alembic ocurrió, exactamente como estaba documentado.**
`--autogenerate` propuso recrear `ix_leagues_unique_name_season` y
`ix_teams_unique_league_name` (el `trim(x)` vs `TRIM(BOTH FROM x)` de
`AGENTS.md`). Se borraron del diff a mano. No se cuenta como ciclo de
corrección porque la propia tarea T004 ya mandaba revisarlo: fue trabajo
previsto, no reproceso.

**Orden de merge del bloque paralelo: la realidad se desvió del pacto.** El
pacto era `013 → 014 → 016 → 017`. Cuando se cerró esta HU, `main` ya tenía
mezclada la 016 —pero **solo su documentación**, sin código ni migración— y las
ramas `013` y `014` seguían sin mezclar. La cabeza de Alembic en `main` sigue
siendo `919f3bd57721`, que es justo lo que apunta el `down_revision` de esta
HU, así que no hizo falta re-puntear nada. **Aviso para quien mezcle 013 y
014**: si esta HU entra antes que ellas, sus migraciones tendrán que colgar de
`c0bd195efdda`, no de `919f3bd57721`.

**Lo que quedó fuera a propósito.** `login_attempts` crece con una fila por
identificador distinto que haya fallado, incluidos los inexistentes, y no hay
job de limpieza (`research.md` §12). Es una limitación conocida y aceptada para
el alcance del proyecto, no un olvido.
