# Phase 0 — Research: Bloqueo tras intentos fallidos de inicio de sesión

**Spec**: [spec.md](./spec.md) · **Plan**: [plan.md](./plan.md)

Esta HU **no re-decide stack ni modelo de dominio** (`AGENTS.md` §5): Python
3.12 / FastAPI / SQLAlchemy 2.0 async / PostgreSQL 16 / Alembic vienen fijados
en `specs/001-fundacion-y-autenticacion/plan.md` y `research.md`. Lo que sigue
son únicamente las decisiones **propias** de esta historia.

Es la única spec del bloque paralelo (013–017) que **modifica código
existente** (`backend/src/auth/`), por lo que cada decisión se evalúa además
contra el Principio IV de la constitución (no romper lo que ya funciona).

---

## §1. Dónde vive el conteo de intentos fallidos

**Decisión**: tabla nueva `login_attempts` en PostgreSQL, una fila por
identificador normalizado, dentro del módulo `backend/src/auth/`.

**Rationale**:

- La spec lo exige explícitamente: *"El conteo persiste, para que el bloqueo
  siga siendo efectivo"* (Edge Case + Assumption "Conteo persistente"). Un
  contador en memoria se pierde en cada despliegue de Railway, y el ataque
  simplemente espera al siguiente reinicio.
- El módulo `auth` ya es el dueño del dominio de sesión (Principio VIII):
  `login_attempts` no lo consulta ningún otro módulo, y `auth` no adquiere
  dependencias nuevas.
- Es la misma base de datos y el mismo `AsyncSession` que ya usa
  `AuthService`; no añade infraestructura.

**Alternativas descartadas**:

| Alternativa | Por qué se descarta |
|---|---|
| Diccionario en memoria del proceso | Se pierde al reiniciar (contradice la spec) y no se comparte entre workers de Uvicorn/Railway: con 2 workers el umbral efectivo se duplica |
| Redis / cache externo | La constitución fija monolito modular; introducir un servicio nuevo exige enmienda con justificación. Un contador de 5 enteros no la justifica |
| Columnas en la tabla `users` | Rompe FR-001: hay que contar intentos de identificadores **que no existen**, y esos no tienen fila en `users`. Además acopla el contador al ciclo de vida del usuario |
| Reutilizar la tabla de auditoría de `specs/016` | Crea una dependencia entre dos specs que se desarrollan en paralelo, y obliga a un `COUNT(*)` sobre una tabla de log que crece sin límite en cada intento de login |

---

## §2. Clave del contador: el identificador normalizado

**Decisión**: la clave es `username.lower()`, exactamente la misma expresión
con la que `AuthService.autenticar` ya busca al usuario
(`func.lower(Usuario.username) == username.lower()`, `service.py:75`).
Columna `username_normalizado` con índice **único**.

**Rationale**: la clarificación de la spec (Session 2026-08-21) lo fija, y la
razón es que el bloqueo no sea esquivable alternando mayúsculas. Usar la misma
expresión que el lookup —y no una normalización "mejor"— es lo que garantiza
que el identificador contado y el identificador buscado sean siempre el mismo.

**Nota deliberada**: **no** se aplica `trim()`. El lookup existente tampoco lo
aplica, así que añadirlo aquí crearía una asimetría entre "a quién se cuenta" y
"a quién se busca". Además evita el problema de índices funcionales
`lower(trim(...))` documentado en `AGENTS.md` — este índice es sobre una
columna normalizada en Python, no una expresión SQL, así que
`alembic --autogenerate` no lo verá cambiar espuriamente.

---

## §3. Tensión entre FR-002 y FR-006 — cómo se resuelve

> **Resuelto en el origen (2026-08-21).** `/speckit-analyze` marcó este
> conflicto como HIGH y **la spec se enmendó**: FR-006 y SC-005 ya solo hablan
> de simetría de *existencia*, y la clarificación correspondiente quedó
> registrada en `spec.md` §Clarifications. Esta sección se conserva porque
> documenta **por qué** se decidió así; el texto de abajo cita la redacción
> **anterior** de FR-006/SC-005, no la vigente.

Los dos requisitos, tal como estaban redactados originalmente, se contradecían:

- **FR-002**: *"MUST rechazar los intentos posteriores con un error de bloqueo
  que indique cuánto falta para reintentar"*.
- **FR-006 / SC-005**: *"MUST NOT revelar en sus respuestas si un identificador
  existe **o si está bloqueado**"*.

No se puede a la vez devolver un error de bloqueo distinguible y que ese error
no revele que hay un bloqueo.

**Decisión**: se respeta FR-002 al pie de la letra, y FR-006 se cumple en lo
que protege de verdad — la **simetría de existencia**:

1. Mientras no se supera el umbral, la respuesta es exactamente la ya existente
   (`401 invalid_credentials`), idéntica exista o no el identificador. Sin
   cambios.
2. Al superarse el umbral, la respuesta pasa a `429 login_locked`, **y lo hace
   igual para un identificador que existe y para uno que no** (la spec lo exige
   en Edge Cases: *"Se cuenta igual el intento fallido […] y, al superar el
   umbral, se bloquea ese identificador igualmente"*).

Como el bloqueo se aplica de forma idéntica a identificadores existentes e
inexistentes, la respuesta `429` **no filtra ni un bit sobre si la cuenta
existe**, que es el ataque que FR-006 previene. Lo único que revela es que
alguien —posiblemente el propio atacante— ya falló 5 veces contra ese
identificador, información que el atacante ya tiene.

**Alternativa descartada**: devolver `401 invalid_credentials` también durante
el bloqueo, sin indicar nada. Cumpliría FR-006 literalmente, pero incumple
FR-002 (que pide indicar el tiempo restante) y deja al usuario legítimo sin
forma de saber por qué su contraseña correcta no funciona — el escenario
justamente que la Historia 2 quiere hacer recuperable.

**Consecuencia para las pruebas existentes**: el test
`test_as2_login_invalido_mensaje_generico`
(`backend/tests/integration/test_auth.py:37`) afirma
`inexistente.json() == mala_clave.json()`. Sigue en verde: hace 1 intento por
identificador, muy por debajo del umbral de 5, y la simetría que afirma se
mantiene en ambos lados del umbral. **Ninguna prueba existente se toca**
(Principio IV).

---

## §4. Código HTTP y forma del error

**Decisión**: `429 Too Many Requests`, cabecera `Retry-After` con los segundos
restantes, y el envelope estándar con `code: "login_locked"`.

```
HTTP/1.1 429 Too Many Requests
Retry-After: 847
{"error":{"code":"login_locked","message":"Demasiados intentos fallidos. Vuelve a intentarlo en 15 minutos.","field":null}}
```

**Rationale**:

- `429` es el código semánticamente correcto y el que espera cualquier cliente
  o proxy ante un límite de intentos.
- `Retry-After` es la forma estándar de "cuánto falta" (FR-002), legible por
  máquina y sin inventar campos fuera del envelope.
- El envelope `{error:{code,message,field}}` es el de
  `specs/001-.../contracts/conventions.md`: no se redefine, solo se usa.

**Extensión del contrato compartido**: la tabla de códigos HTTP de
`conventions.md` no contempla `429`. Esta HU **añade** ese status **solo para
`POST /auth/login`**, documentado en
[`contracts/auth-lockout.openapi.yaml`](./contracts/auth-lockout.openapi.yaml).
Es una adición aditiva y local, no un cambio incompatible: ningún endpoint
existente cambia de status ni de forma (Principio III).

**Alternativas descartadas**: `403` (no comunica "reintenta más tarde" y se
confunde con el `403` de rol insuficiente ya en uso); `423 Locked` (es
WebDAV, ningún cliente lo trata especialmente); añadir un campo
`retry_after_seconds` al envelope (rompería la forma fija del envelope para
todas las specs).

---

## §5. Orden de las comprobaciones dentro del login

**Decisión**: el bloqueo se comprueba **antes** de verificar la contraseña, y
el incremento del contador se hace **después** de que la verificación falle.

```
1. normalizar    username -> clave
2. leer          fila de login_attempts por clave
3. si bloqueado  -> 429 login_locked   (aún no se toca la contraseña)
4. autenticar    (lógica existente, incluido el hash señuelo)
5a. si falla     -> incrementar contador; si alcanza el umbral, fijar bloqueo; -> 401
5b. si acierta   -> borrar la fila del contador -> sesión normal
```

**Rationale**:

- El paso 3 antes del 4 es lo que hace cumplir **FR-003** ("rechazar incluso si
  la contraseña es correcta"): si se verificara primero, un acierto se colaría.
- También evita gastar un `bcrypt` completo por cada intento durante un ataque
  activo: durante el bloqueo el coste por request cae a una consulta indexada.
- El paso 5b (borrar la fila al acertar) es **FR-005**, y cubre los dos
  escenarios de la Historia 2: fallar-luego-acertar reinicia el conteo, y
  acertar tras el desbloqueo lo deja en cero.

**Nota sobre el hash señuelo**: `_HASH_SENUELO` (`service.py:28`) iguala el
tiempo de respuesta entre usuario inexistente y contraseña incorrecta. El paso
3 introduce una respuesta **más rápida** cuando hay bloqueo, pero eso no filtra
existencia: el bloqueo es igual de probable para un identificador inexistente.

---

## §6. Concurrencia: dos intentos simultáneos

**Decisión**: el incremento es un **UPSERT atómico** de PostgreSQL, en una sola
sentencia:

```sql
INSERT INTO login_attempts (id, username_normalizado, failed_count, last_attempt_at)
VALUES (:id, :clave, 1, now())
ON CONFLICT (username_normalizado) DO UPDATE
  SET failed_count = login_attempts.failed_count + 1,
      last_attempt_at = now()
RETURNING failed_count;
```

**Rationale**: el Edge Case *"dos intentos simultáneos sobre el mismo
identificador: el conteo es consistente y no se salta el bloqueo"* es
exactamente el *lost update* clásico. Un `SELECT` + `UPDATE` en Python permite
que dos requests lean 4 y ambos escriban 5. El `ON CONFLICT DO UPDATE`
serializa a nivel de fila en el motor, y el `RETURNING` devuelve el valor real
post-incremento, que es el que se compara contra el umbral.

`SQLAlchemy` lo expresa con `postgresql.insert(...).on_conflict_do_update(...)`
— ORM, sin SQL concatenado (Estándar de Seguridad de la constitución).

**Alternativa descartada**: `SELECT ... FOR UPDATE` + `UPDATE`. Correcto, pero
son dos viajes a la base y un lock explícito sostenido durante la verificación
de contraseña; el upsert consigue lo mismo en una sentencia.

---

## §7. Transacción: el contador debe sobrevivir al error

**Decisión**: el incremento se **commitea antes** de lanzar
`_CREDENCIALES_INVALIDAS`.

**Rationale**: es el fallo más fácil de cometer en esta HU. Si el `raise` ocurre
antes del `commit`, la sesión de SQLAlchemy se descarta con la petición, el
incremento se pierde y **el bloqueo nunca llega a activarse** — la feature
entera queda inerte y los tests de umbral fallan de forma confusa. Se documenta
aquí para que la tarea de implementación lo trate como requisito, no como
detalle.

---

## §8. Semántica del bloqueo y del desbloqueo

**Decisión**:

- Al alcanzar el umbral: se fija `blocked_until = now() + LOGIN_LOCKOUT_SECONDS`
  y se **reinicia `failed_count` a 0**.
- El desbloqueo es **implícito**: no hay job ni tarea programada. Un
  identificador está bloqueado si y solo si `blocked_until > now()` en el
  momento de la comprobación.

**Rationale**:

- Reiniciar el contador al bloquear hace que, tras expirar el bloqueo, el
  usuario legítimo disponga otra vez de las 5 oportunidades completas (FR-004:
  *"el inicio de sesión vuelve a funcionar normalmente"*). Si el contador
  quedara en 5, el siguiente fallo re-bloquearía de inmediato.
- El desbloqueo implícito es lo que hace **FR-004** verificable sin reloj de
  servidor ni scheduler: no hay estado que "caduque", solo una comparación de
  timestamps. Es también lo que permite probarlo en un test moviendo
  `blocked_until` al pasado, sin `sleep(900)`.

---

## §9. Configuración (FR-007)

**Decisión**: dos variables nuevas en `src/core/config.py` (`Settings`),
documentadas vacías en `.env.example`:

| Variable | Default | Significado |
|---|---|---|
| `LOGIN_MAX_FAILED_ATTEMPTS` | `5` | Fallos consecutivos que disparan el bloqueo |
| `LOGIN_LOCKOUT_SECONDS` | `900` | Duración del bloqueo (15 minutos) |

Los defaults son los de la sección *Assumptions* de la spec. **No son
secretos** — se documentan en `.env.example` porque es la convención del
proyecto para toda llave de configuración, no por el Principio VI.

**Sobre el Edge Case "si el umbral o la duración cambian entre intentos"**:

- El **umbral** se lee en cada comprobación, así que un cambio aplica al
  siguiente intento.
- La **duración** se materializa como el timestamp absoluto `blocked_until` en
  el instante en que se crea el bloqueo. Un cambio de duración **no** re-calcula
  bloqueos ya activos. Es la lectura honesta de *"se aplican los valores
  configurados en el momento de la verificación"*: el momento de verificación
  que fija la duración es aquel en que el bloqueo se decide.
- `get_settings()` está bajo `@lru_cache`, de modo que un cambio de variable de
  entorno requiere reiniciar el proceso. Ya es así para toda la configuración
  del proyecto; FR-007 pide "sin cambios de código", no "en caliente".

---

## §10. Frontend: un código más en el catálogo

**Decisión**: añadir `login_locked` a
`frontend/src/lib/mensajesDeError.ts`, con un mensaje fijo en español y **sin
el número de minutos**.

**Rationale**: sin esa entrada, el usuario bloqueado vería `MENSAJE_GENERICO`
("No fue posible completar la operación") y no entendería por qué su contraseña
correcta falla. El catálogo existe precisamente para eso.

El número exacto de minutos **no** se muestra: el catálogo es estático por
diseño y `mensajesDeError` nunca renderiza el `message` del servidor (regla
documentada en la cabecera de ese archivo, y lo que hace verificable SC-003 de
`specs/012`). `ApiError` tampoco expone cabeceras, así que leer `Retry-After`
exigiría cambiar `apiClient` para todas las specs. FR-002 queda cumplido en el
contrato de API (`Retry-After` + `message` del servidor); la UI da la versión
cualitativa. Es un cambio de **una línea** en el frontend, sin tocar
`LoginPage` ni `AuthContext`.

---

## §11. Migración Alembic y orden de merge del bloque paralelo

**Decisión**: **un solo archivo** de migración que crea `login_attempts` y su
índice único. Nada más.

Al abrir el PR, según la nota de `AGENTS.md` sobre migraciones en paralelo:

1. Orden de merge pactado: `013 → 014 → 016 → **017**`. Esta HU es la **última**
   de las cuatro que migran.
2. Se rebasa la rama sobre `main` actualizado y se re-puntea `down_revision` a
   la cabeza ya mezclada (hoy `919f3bd57721`, pero será la de `016` cuando le
   toque el turno a esta HU).
3. Se **borra del diff** cualquier `drop_index`/`create_index` espurio sobre
   `ix_leagues_unique_name_season` o `ix_teams_unique_league_name` que
   `--autogenerate` invente (nota de índices funcionales de `AGENTS.md`).

`login_attempts` es una tabla **nueva y aislada**: sin claves foráneas —a
propósito, ver §1— así que no colisiona con las migraciones de 013, 014 ni 016.

---

## §12. Riesgo aceptado: crecimiento de la tabla

`login_attempts` crece con una fila por identificador **distinto** que haya
fallado alguna vez, incluidos los inexistentes. Un atacante que pruebe un
millón de nombres distintos crea un millón de filas, y nada las borra (las
filas de usuarios legítimos sí se borran al acertar la contraseña, §5).

**Se acepta para el alcance de este proyecto**, sin job de limpieza:

- La spec no lo pide y *Out of Scope* no lo contempla; añadir un scheduler
  sería inventar alcance (Principio I).
- Cada fila son ~90 bytes y `username` está topado a 60 caracteres por
  `LoginRequest`.
- El volumen de referencia del proyecto (10 ligas, `specs/001/plan.md`) no se
  parece a un ataque sostenido.

Queda **registrado aquí como limitación conocida**: si el sistema saliera a
producción real, la mitigación natural es un borrado periódico de filas con
`last_attempt_at` antiguo y sin bloqueo activo. Sería una HU aparte.

---

## Resumen de decisiones

| # | Decisión |
|---|---|
| §1 | Tabla `login_attempts` en PostgreSQL, dentro del módulo `auth` |
| §2 | Clave = `username.lower()`, idéntica al lookup existente; sin `trim()` |
| §3 | FR-002 gana sobre la letra de FR-006; la simetría de **existencia** se conserva intacta |
| §4 | `429` + `Retry-After` + `code: login_locked`; añade `429` solo a `/auth/login` |
| §5 | Comprobar bloqueo **antes** de verificar contraseña; contar **después** de fallar |
| §6 | `INSERT ... ON CONFLICT DO UPDATE ... RETURNING` para un conteo sin *lost update* |
| §7 | Commit del incremento **antes** del `raise` |
| §8 | Al bloquear se reinicia el contador; desbloqueo implícito por comparación de timestamps |
| §9 | `LOGIN_MAX_FAILED_ATTEMPTS=5`, `LOGIN_LOCKOUT_SECONDS=900` por entorno |
| §10 | Una entrada `login_locked` en el catálogo de mensajes del frontend |
| §11 | Una migración, re-punteada al mergear; 017 es la última del bloque paralelo |
| §12 | Crecimiento de la tabla: limitación conocida y aceptada, sin job de limpieza |
