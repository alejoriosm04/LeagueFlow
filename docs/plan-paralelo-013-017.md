# Guía de trabajo paralelo — specs 013–017

Bloque de cinco historias de usuario que se desarrollan **en paralelo**, cada
una por un integrante distinto y en una zona independiente del código. Mapa en
`docs/backlog/backlog.md`; contexto en `docs/flujo-sdd.md` §5.1.

## Cómo se usa esta guía

- **`/speckit.specify` y `/speckit.clarify` YA ESTÁN HECHOS** (de forma central,
  en orden `013 → 017`): las 5 specs existen en `specs/013-*` a `specs/017-*`,
  con su `spec.md` y su checklist. No los vuelvas a correr.
- Cada integrante ahora ejecuta `/speckit.plan → /speckit.tasks →
  /speckit.implement` **en su propia rama y máquina**.
- Los prompts de abajo quedan como referencia de lo que se corrió y de lo que
  debe guiar cada `plan.md`. La sección de `/speckit.clarify` de cada HU refleja
  lo que **ya se resolvió**, no preguntas pendientes.

## Reglas de oro (todas en `AGENTS.md` y `constitution.md`)

1. **No re-decidir stack ni modelo.** Cada `plan.md` referencia
   `specs/001-fundacion-y-autenticacion/plan.md` y `data-model.md`, y solo
   documenta lo que **añade** (regla 5 de AGENTS.md).
2. **La spec se commitea junto con el código que genera**, en el mismo PR.
3. **Conventional Commits**; el título del PR es el commit que queda en `main`
   (squash merge). Título `tipo(NNN): descripción en imperativo, minúscula`.
4. **Migraciones en paralelo**: ver la nota al final y `AGENTS.md`.

---

## HU 013 — Divisiones (grupos) dentro de una liga

**Qué hace**: un organizador agrupa los equipos de su liga en "Grupo A",
"Grupo B", etc. Cualquiera consulta esa organización sin sesión. Una liga sin
grupos sigue funcionando igual que hoy.

**Git — crear rama:**

```bash
git checkout main && git pull
git checkout -b 013-grupos-divisiones
```

**`/speckit.specify`**

```text
Un organizador de una liga necesita poder dividir los equipos inscritos en
grupos o divisiones (por ejemplo "Grupo A" y "Grupo B") para organizar torneos
con fase de grupos. Necesita crear, renombrar y eliminar grupos dentro de su
liga, y asignar cada equipo a un grupo (un equipo pertenece como máximo a un
grupo por liga). Cualquier visitante, sin iniciar sesión, debe poder consultar
qué equipos están en cada grupo de una liga. Una liga sin grupos definidos
sigue funcionando exactamente igual que hoy.
```

**`/speckit.plan`** (referencia el plan de 001; no re-decidas stack)

```text
Referencia el stack y el modelo ya fijados en
specs/001-fundacion-y-autenticacion/plan.md y data-model.md (regla 5 de
AGENTS.md). Solo documenta lo que añade esta HU: un paquete nuevo
backend/src/groups/ (router, service, schemas, models y una migración propia).
No importa modelos de teams ni leagues: valida con
TeamService.obtener_equipo(team_id) y LeagueService.obtener_liga(league_id)
(mismo patrón que matches/service.py). Frontend en /leagues/:id/groups.
```

**`/speckit.clarify`** — resuelto en la spec

- Equipos inactivos: se muestran en la composición si ya son miembros, pero NO
  se pueden asignar a un grupo nuevo (FR-011 y FR-012 de la spec).

**`/speckit.tasks`** → **`/speckit.implement`**

**Requisitos clave**

- Nombre de grupo único por liga.
- Eliminar un grupo borra solo sus membresías, nunca los equipos.
- `404 team_not_found_in_league` si el equipo no es de esa liga.
- `GET /leagues/{id}/groups` público; `200` con lista vacía si no hay grupos.
- Equipos inactivos: se muestran si ya son miembros, no se pueden asignar.

**Entidades**

- `LeagueGroup (id, league_id, name, position)`
- `GroupTeamMembership (group_id, team_id)`

**Qué toca**: solo `main.py` con el `import` + `include_router` del nuevo router.

**Git — subir cambios:**

```bash
git add -A
git commit -m "feat(013): dividir equipos de una liga en grupos"
git push -u origin 013-grupos-divisiones
gh pr create --title "feat(013): dividir equipos de una liga en grupos" \
  --body "Implementa specs/013-grupos-divisiones/spec.md." --base main
```

---

## HU 014 — Tarjetas y sanciones disciplinarias

**Qué hace**: un operador registra tarjetas amarillas y rojas de un jugador en
un partido (en curso o finalizado); cualquiera consulta la ficha disciplinaria
(tarjetas + si está suspendido) sin sesión.

> **Decisión acordada**: la tarjeta ES un `MatchEvent` (se amplía el CHECK
> `type`), no una tabla aparte. La derivación de suspensión vive en un módulo
> nuevo `sanctions/`. Esta HU es la **dueña exclusiva de `matches/`** entre las
> cinco — ninguna otra lo toca.

**Git — crear rama:**

```bash
git checkout main && git pull
git checkout -b 014-tarjetas-sanciones
```

**`/speckit.specify`**

```text
Un operador necesita registrar las tarjetas amarillas y rojas que recibe un
jugador durante un partido en curso o finalizado. La tarjeta se registra como
un evento del partido. El sistema debe derivar automáticamente, en cada
consulta, si un jugador está suspendido (dos amarillas en partidos distintos o
una roja). Cualquier visitante, sin iniciar sesión, debe poder consultar la
ficha disciplinaria de un jugador: cuántas tarjetas tiene y si está suspendido.
```

**`/speckit.plan`** (referencia el plan de 001; no re-decidas stack)

```text
Referencia el stack y el modelo ya fijados en
specs/001-fundacion-y-autenticacion/plan.md y data-model.md (regla 5 de
AGENTS.md). Solo documenta lo que añade esta HU: amplía el tipo de MatchEvent
para admitir YELLOW_CARD y RED_CARD (CHECK en matches/models.py + validación en
matches/schemas.py + migración del CHECK), añade el registro de tarjeta en
matches (mismo patrón que MatchService.registrar_gol) y un módulo nuevo
backend/src/sanctions/ que deriva la suspensión leyendo MatchEvent por servicio
(patrón de statistics). Frontend: registrar tarjetas sobre un partido y página
pública de ficha disciplinaria.
```

**`/speckit.clarify`** — resuelto en la spec

- Suspensión sin expiración: "suspendido" es una marca derivada (una roja, o dos
  amarillas en partidos distintos) que no se cumple ni se borra (FR-007 de la
  spec).

**`/speckit.tasks`** → **`/speckit.implement`**

**Requisitos clave**

- Solo sobre partido en curso o finalizado (`409` si programado/cancelado).
- Si hay alineación registrada y el jugador no está en ella, `409
  player_not_in_lineup`; si no hay alineación, se permite igual.
- Se permiten varias tarjetas del mismo jugador en el mismo partido.
- El equipo del jugador se toma de `jugador.team_id`, nunca del cliente.
- "Suspendido" se calcula en cada lectura, nunca se guarda como bandera, y no
  tiene expiración dentro de la temporada.

**Entidades**

- Sin entidad nueva de tarjeta: la tarjeta es un `MatchEvent` con `type`
  ampliado a `GOAL | YELLOW_CARD | RED_CARD`.
- Suspensión: vista derivada en lectura (no se persiste).

**Qué toca**: `matches/models.py` (CHECK), `matches/schemas.py` (validación de
tipo), una migración del CHECK, módulo `sanctions/`, y `main.py` con el
`include_router` de `sanctions`.

**Git — subir cambios:**

```bash
git add -A
git commit -m "feat(014): registrar tarjetas y sanciones de jugadores"
git push -u origin 014-tarjetas-sanciones
gh pr create --title "feat(014): registrar tarjetas y sanciones de jugadores" \
  --body "Implementa specs/014-tarjetas-sanciones/spec.md." --base main
```

---

## HU 015 — Exportación de clasificación y calendario a CSV

**Qué hace**: un botón para descargar la tabla de posiciones y el calendario
como CSV, con los mismos datos que ya se ven en la app. No recalcula nada: solo
empaqueta.

**Git — crear rama:**

```bash
git checkout main && git pull
git checkout -b 015-exportacion-csv
```

**`/speckit.specify`**

```text
Un visitante o un organizador necesita poder descargar, como archivo CSV, la
tabla de posiciones de una liga y su calendario de partidos, para compartirlos
o abrirlos en una hoja de cálculo. La información exportada debe ser
exactamente la misma que ya se puede consultar en la aplicación — esta
funcionalidad no recalcula nada, solo la empaqueta como archivo descargable. No
requiere iniciar sesión, igual que las consultas de las que parte.
```

**`/speckit.plan`** (referencia el plan de 001; no re-decidas stack)

```text
Referencia el stack y el modelo ya fijados en
specs/001-fundacion-y-autenticacion/plan.md y data-model.md (regla 5 de
AGENTS.md). Solo documenta lo que añade esta HU: un paquete backend/src/export/
sin tabla ni migración (solo lectura/transformación). Reutiliza
StandingsService.obtener_clasificacion(league_id) (ya sin paginar). Para el
calendario completo, matches/service.py no tiene hoy un método sin paginar que
incluya también los programados (listar_finalizados solo trae finalizados):
añadir un método nuevo y aditivo a MatchService, sin tocar los existentes, o
paginar en bucle sin tocar ese archivo. Frontend: página /leagues/:id/reportes
con botones de descarga.
```

**`/speckit.clarify`** — sin preguntas (diferido a `plan.md`)

- Método nuevo en `matches/service.py` (aditivo) vs paginar en bucle → decisión de plan.
- Nombre del CSV con nombre de liga vs solo ID → decisión de plan.

**`/speckit.tasks`** → **`/speckit.implement`**

**Requisitos clave**

- `200` con CSV solo de encabezados si no hay datos (nunca error).
- `400 unsupported_export_format` si no es csv.
- El CSV debe coincidir exactamente con el JSON equivalente.

**Entidades**: ninguna (no persiste nada).

**Qué toca**: `main.py` (`include_router`). Único cruce real: el método nuevo
aditivo en `matches/service.py` (si se elige esa opción), de bajo riesgo.

**Git — subir cambios:**

```bash
git add -A
git commit -m "feat(015): exportar clasificacion y calendario a csv"
git push -u origin 015-exportacion-csv
gh pr create --title "feat(015): exportar clasificacion y calendario a csv" \
  --body "Implementa specs/015-exportacion-csv/spec.md." --base main
```

---

## HU 016 — Auditoría de operaciones administrativas

**Qué hace**: queda un registro de cada acción que modifica datos (quién, qué,
cuándo), consultable solo por el organizador.

**Git — crear rama:**

```bash
git checkout main && git pull
git checkout -b 016-auditoria
```

**`/speckit.specify`**

```text
El equipo necesita poder ver un historial de qué operación administrativa se
hizo, quién la hizo y cuándo (crear una liga, registrar un resultado, etc.),
para poder investigar un dato incorrecto o un incidente sin tener que revisar
la base de datos manualmente. Solo un organizador autenticado puede consultar
ese historial; las consultas públicas (lecturas) no se registran, solo las
operaciones que modifican datos.
```

**`/speckit.plan`** (referencia el plan de 001; no re-decidas stack)

```text
Referencia el stack y el modelo ya fijados en
specs/001-fundacion-y-autenticacion/plan.md y data-model.md (regla 5 de
AGENTS.md). Solo documenta lo que añade esta HU: un middleware ASGI genérico
registrado en main.py junto al CORSMiddleware existente (app.add_middleware),
que intercepta toda petición POST/PUT/PATCH/DELETE y escribe en una tabla
propia de backend/src/audit/, sin tocar routers de otros dominios. Router
propio de solo lectura, GET /admin/audit-log, restringido a sesión de
organizador. Frontend: página /admin/audit-log.
```

**`/speckit.clarify`** — resuelto en la spec

- Solo se auditan escrituras exitosas; los fallos por validación o permisos
  (401/403/400) NO se registran.

**`/speckit.tasks`** → **`/speckit.implement`**

**Requisitos clave**

- Solo escrituras exitosas (los fallos no se registran).
- No registrar `GET`.
- Cada registro guarda método, ruta, código de estado, actor (o `null`) y fecha.
- Nunca el cuerpo de la petición ni de la respuesta (datos sensibles/stack
  traces; exigido por la constitución).
- El actor se obtiene decodificando la sesión en el middleware; si no es
  posible, queda `null`.

**Entidad**: `AuditLogEntry (id, method, path, status_code, actor_id nullable,
created_at)`.

**Qué toca**: `main.py` (1 línea de middleware + 2 del router).

**Git — subir cambios:**

```bash
git add -A
git commit -m "feat(016): auditar operaciones administrativas"
git push -u origin 016-auditoria
gh pr create --title "feat(016): auditar operaciones administrativas" \
  --body "Implementa specs/016-auditoria/spec.md." --base main
```

---

## HU 017 — Bloqueo tras intentos fallidos de login

**Qué hace**: si alguien falla varias veces seguidas iniciando sesión con el
mismo usuario, queda bloqueado un rato antes de poder intentar de nuevo.

**Git — crear rama:**

```bash
git checkout main && git pull
git checkout -b 017-bloqueo-login
```

**`/speckit.specify`**

```text
El sistema necesita protegerse de ataques de fuerza bruta contra el inicio de
sesión: si alguien falla varias veces seguidas al iniciar sesión con el mismo
identificador de usuario, ese identificador debe quedar bloqueado
temporalmente antes de poder intentarlo de nuevo, incluso si luego usa la
contraseña correcta. El bloqueo es específico por identificador de usuario: no
debe afectar el inicio de sesión de nadie más, y no debe revelar si ese
identificador existe o no en el sistema. Pasado el tiempo de bloqueo, el inicio
de sesión vuelve a funcionar normalmente.
```

**`/speckit.plan`** (referencia el plan de 001; no re-decidas stack)

```text
Referencia el stack y el modelo ya fijados en
specs/001-fundacion-y-autenticacion/plan.md y data-model.md (regla 5 de
AGENTS.md). Solo documenta lo que añade esta HU: modifica únicamente
backend/src/auth/ — tabla de conteo de intentos fallidos por username y la
lógica de bloqueo dentro de AuthService.autenticar(username, password), antes y
después de verificar la contraseña. Reutiliza el hash señuelo _HASH_SENUELO ya
existente para que el conteo no filtre por temporización si el usuario existe.
Umbral y duración configurables por variable de entorno. 429 con
retry_after_seconds si está bloqueado.
```

**`/speckit.clarify`** — resuelto en la spec

- Conteo por identificador normalizado (sin mayúsculas), el mismo criterio con
  que el login busca al usuario. El umbral/duración por defecto (5 intentos /
  15 min) queda como *Assumption* en la spec.

**`/speckit.tasks`** → **`/speckit.implement`**

**Requisitos clave**

- Contar fallidos por `username` normalizado (sin mayúsculas), exista o no (para
  no revelar nada).
- `429 login_locked` + `retry_after_seconds` al llegar al umbral.
- Reset del contador tras login exitoso; desbloqueo automático al expirar.
- Nunca romper la simetría existente entre "usuario no existe" y "contraseña
  incorrecta" (ambas `401`).

**Entidad**: `LoginAttempt (username, failed_count, locked_until nullable,
updated_at)`.

**Qué toca**: `auth/` (la única HU que modifica código existente — a propósito,
para que nadie más lo toque en paralelo).

**Git — subir cambios:**

```bash
git add -A
git commit -m "feat(017): bloquear login tras intentos fallidos"
git push -u origin 017-bloqueo-login
gh pr create --title "feat(017): bloquear login tras intentos fallidos" \
  --body "Implementa specs/017-bloqueo-login/spec.md." --base main
```

---

## Nota de merge (aplica a las cinco)

Cuatro de las cinco specs crean migraciones (013, 014, 016, 017); la 015 no
persiste nada. **No se mergean las cinco a la vez sin coordinarse.** El
protocolo completo está en `AGENTS.md`, sección "migraciones en paralelo":

1. **Orden de merge pactado**: `013 → 014 → 016 → 017`. La `015` en cualquier
   momento.
2. **Una migración = un archivo**, generada contra `main` actualizado y
   revisada (borrar el `DROP/CREATE INDEX` espurio de los índices funcionales
   de `leagues`/`teams`; ver AGENTS.md).
3. **Antes de abrir el PR**, rebasea tu rama sobre `main` y re-punta el
   `down_revision` de tu migración a la cabeza ya mezclada:

   ```bash
   git fetch origin
   git rebase origin/main   # o: git merge origin/main
   ```

4. Si aun así quedan dos cabezas, se arregla como último recurso con
   `alembic merge heads -m "fusionar <hu-a> y <hu-b>"` — pero preferir el
   rebase del punto 3.

**Reglas de PR** (constitution): squash merge únicamente, título
`tipo(NNN): descripción en imperativo, minúscula`, el PR enlaza su `spec.md` y
necesita 1 revisión humana aprobada.
