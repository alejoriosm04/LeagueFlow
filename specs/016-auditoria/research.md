# Research: Auditoría de operaciones administrativas

**Feature**: `016-auditoria` · **Date**: 2026-08-21

No hay `NEEDS CLARIFICATION` pendiente en el Technical Context (stack
heredado de `specs/001-*`, sin dependencias nuevas). Este documento resuelve
las decisiones de diseño propias de esta spec, todas dictadas o acotadas por
el enunciado de entrada.

## 1. Middleware ASGI puro, no `Starlette.BaseHTTPMiddleware`

**Decision**: `AuditMiddleware` es una clase ASGI de bajo nivel —
`__init__(self, app)` + `async __call__(self, scope, receive, send)` —
registrada con `app.add_middleware(AuditMiddleware)`, no un middleware
basado en `BaseHTTPMiddleware`/`@app.middleware("http")`.

**Rationale**: `BaseHTTPMiddleware` bufferiza la respuesta completa en
memoria para exponerla como `response.body`, lo que (a) invita a que algún
día alguien "aproveche" ese body ya cargado para guardarlo — justo lo que
FR-003 prohíbe — y (b) rompe respuestas en streaming. Un middleware ASGI
puro solo necesita mirar dos cosas del tráfico que pasa por él: el
`scope["method"]`/`scope["path"]` de la petición, y el campo `status` del
mensaje `http.response.start` de la respuesta — nunca lee `receive()` más
allá de lo que la propia app ya consume, y reenvía cada mensaje
`http.response.body` a `send()` sin tocarlo. La imposibilidad de guardar el
body queda garantizada por la forma del código, no por disciplina del autor
al escribirlo.

**Alternatives considered**:
- `BaseHTTPMiddleware` — rechazado por lo anterior.
- Un `Depends` de auditoría añadido a cada router de escritura — rechazado:
  el enunciado pide explícitamente no tocar routers de otros dominios, y
  FR-007 exige que la captura sea genérica sin instrumentar operación por
  operación.

## 2. Sesión de BD propia, sin `Depends(get_db)`

**Decision**: `AuditMiddleware` abre su propia sesión con
`SessionLocal()` (la misma fábrica de `src/core/db.py`, no una nueva),
dentro de un `async with`, independiente de la sesión que la ruta de negocio
recibe vía `Depends(get_db)`.

**Rationale**: el sistema de inyección de dependencias de FastAPI solo se
resuelve para funciones de *path operation*; un middleware ASGI corre antes
y fuera de ese mecanismo, así que `Depends(get_db)` no es invocable ahí —
no es una preferencia de diseño, es una restricción del framework. Usar una
sesión completamente independiente tiene además una ventaja: un fallo al
escribir el registro de auditoría (por ejemplo, la BD momentáneamente no
responde) no puede interferir con ni revertir la transacción de negocio que
está describiendo, porque son transacciones distintas de principio a fin
(Principio IV — no romper lo que ya funciona).

**Alternatives considered**:
- Guardar la sesión de la ruta en `request.state` desde un `Depends` para
  que el middleware la reutilice — rechazado: reintroduce exactamente el
  "tocar cada router" que se quiere evitar, y acopla el resultado de la
  escritura de negocio con el de la escritura de auditoría en la misma
  transacción (un rollback de una tumbaría la otra).

## 3. Resolución del actor: reutilizar `AuthService.obtener_sesion_valida`

**Decision**: el middleware construye un `starlette.requests.Request(scope)`
(sin `receive`/body — el constructor solo necesita `scope` para exponer
`.cookies`, no consume el body) para leer la cookie `lf_session`
(`NOMBRE_COOKIE` de `src/auth/dependencies.py`), y resuelve el actor
llamando `AuthService(db).obtener_sesion_valida(token)` — el mismo método
que ya usan `usuario_opcional`/`usuario_actual`.

**Rationale**: reutiliza la única fuente de verdad de "qué hace válida una
sesión" (expiración, revocación) en vez de reimplementar esa lógica una
segunda vez fuera de sincronía con la real. Es exactamente lo que pide el
enunciado.

**Efecto secundario aceptado**: `obtener_sesion_valida` extiende
`expires_at` como parte de su contrato (expiración por inactividad, ver
`specs/001-*/data-model.md` §Session). Al llamarse una vez desde el
middleware y, para toda ruta protegida, otra vez desde
`usuario_actual`/`usuario_opcional` dentro del propio endpoint, la ventana
de inactividad se extiende dos veces en el mismo request. Es idempotente en
efecto (el resultado final es el mismo `expires_at` que produciría una sola
llamada) y cuesta un `UPDATE` extra por escritura auditada — aceptado como
tradeoff razonable frente a mantener dos implementaciones de validación de
sesión.

**Actor no determinable (FR-004)**: el caso típico donde esto ocurre es
`POST /auth/login` sin una cookie `lf_session` previa — la petición que
*crea* la sesión no trae todavía la cookie que identificaría al actor. En
ese caso `actor_id` (y `actor_username`) quedan `null` explícitamente en el
registro; no se inventa un actor. Esto no es absoluto: si el cliente ya
tenía una cookie de sesión válida y vuelve a llamar a `/auth/login` (p. ej.
para reautenticarse), esa cookie sí viaja y el middleware resuelve el actor
de la sesión anterior — comportamiento correcto (la reautenticación queda
atribuida a quien la hizo), simplemente no es el caso que motiva esta
excepción. El resto de escrituras exigen sesión previa para llegar siquiera
a ejecutarse (Edge Cases de `spec.md`), así que en la práctica el actor es
casi siempre determinable.

## 4. Cuándo se escribe el registro: después de que la respuesta ya se envió

**Decision**: el middleware envuelve `send` solo para capturar el `status`
del mensaje `http.response.start` (una variable local, no una escritura a
BD); la fila de auditoría se escribe **después** de que
`await self.app(scope, receive, send_wrapper)` retorna — es decir, una vez
que el ciclo de la respuesta ya terminó del lado del cliente.

**Rationale**: desacopla por completo la auditoría del camino crítico de la
respuesta. Un error al escribir el registro de auditoría nunca puede
demorar, cortar o corromper la respuesta que el cliente ya recibió; se
captura con `try/except` y se registra con `logger.exception` (mismo patrón
de `src/core/errors.py`), sin relanzar — perder una entrada de auditoría
por un incidente de infraestructura no debe tumbar la operación de negocio
que sí tuvo éxito.

**Filtro de éxito (clarificación de `spec.md`)**: solo se escribe si
`200 <= status < 300`. Como todo error de negocio (`ErrorDeNegocio`,
`RequestValidationError`, excepción no controlada) ya se traduce a un
`status` no-2xx por los manejadores globales existentes
(`src/core/errors.py`) antes de que `send` emita `http.response.start`, el
filtro por rango de status es suficiente y no requiere ninguna señal
adicional del router.

## 5. Qué operaciones se interceptan

**Decision**: solo `scope["method"] in {"POST", "PUT", "PATCH", "DELETE"}`
hace algún trabajo (incluida la resolución del actor); todo lo demás (`GET`,
`HEAD`, `OPTIONS`) se reenvía a `self.app` sin ningún trabajo adicional.

**Rationale**: FR-002 tal cual. Como efecto colateral, las peticiones
`OPTIONS` de preflight CORS no pagan ningún costo de auditoría.

## 6. Qué guarda cada registro ("destino" y "resultado")

**Decision**: `path` = `scope["path"]` tal cual (incluye el prefijo
`/api/v1/...` y cualquier segmento de recurso, p. ej.
`/api/v1/leagues/3fa8…`), **sin** query string. `method` = `scope["method"]`.
`status_code` = el entero capturado de `http.response.start`. Nada del
cuerpo de la petición ni de la respuesta se lee ni se guarda (FR-003) — ver
§1: el middleware ni siquiera tiene una vía para acceder a esos bytes sin
tocar `receive`/reenviar `send` manualmente, cosa que no hace.

**Rationale**: es la información mínima que pide FR-003 ("método, destino,
resultado y actor") y es la que un organizador necesita para reconstruir
"qué operación se hizo" sin ambigüedad (la ruta ya identifica el recurso).
Excluir la query string es una precaución adicional — ningún endpoint de
escritura actual la usa para datos sensibles, pero omitirla evita que una
spec futura la introduzca sin que nadie recuerde revisar esta captura
genérica.

## 7. Actor: FK + snapshot de username

**Decision**: `AuditLogEntry.actor_id` es un UUID nullable, `FOREIGN KEY
(users.id) ON DELETE SET NULL`; `AuditLogEntry.actor_username` es un
`string` nullable, copiado del `Usuario.username` resuelto en el momento de
escribir el registro (no vía join en la lectura).

**Rationale**: el propósito del historial es ser un registro fiel de lo que
pasó *en su momento*. Hoy no existe endpoint para renombrar o borrar un
`User` (`specs/001-*/data-model.md`), así que un join en `GET
/admin/audit-log` daría hoy exactamente el mismo resultado que el snapshot —
pero si una spec futura añade renombrado de usuario, un audit log que
resolviera el nombre "en vivo" reescribiría silenciosamente la historia
("quién lo hizo" cambiaría con el tiempo), que es precisamente lo que un
registro de auditoría no debe hacer. Guardar el snapshot además evita un
`JOIN` en el endpoint de listado. `actor_id` se conserva igualmente por
trazabilidad e integridad referencial.

## 8. Dónde se registra el middleware en `main.py`

**Decision**: `app.add_middleware(AuditMiddleware)` se añade inmediatamente
después de la llamada existente a `app.add_middleware(CORSMiddleware, ...)`,
tal como pide el enunciado.

**Rationale**: el middleware solo inspecciona método/ruta/status, nunca
encabezados o comportamiento de CORS, así que su posición relativa a
`CORSMiddleware` en la pila no cambia ningún resultado observable de la
spec — se resuelve por la instrucción explícita y por legibilidad (ambas
líneas de infraestructura transversal quedan juntas), no por una necesidad
técnica de ordenar una antes que la otra.

## 9. Autorización del endpoint de lectura

**Decision**: `GET /admin/audit-log` depende de `requiere_rol("organizador")`
de `src/auth/dependencies.py` — la misma dependencia que ya protege `POST
/leagues` y `POST /users` — sin crear una dependencia nueva.

**Rationale**: instrucción explícita del enunciado; además es exactamente
FR-006 (rechazar sin rol organizador o sin sesión) sin duplicar la regla de
autorización en un segundo lugar del código.

## 10. Migración: confirmar el head antes de generar

**Decision**: se corrió `uv run alembic heads` sobre el estado actual del
repositorio antes de diseñar la migración.

```text
$ uv run alembic heads
919f3bd57721 (head)
```

Un único head, sin fan-out pendiente por fusionar. La migración nueva de
esta spec fija `down_revision = "919f3bd57721"`.

**Nota de proceso (`AGENTS.md` "migraciones en paralelo")**: `013`
(grupos), `014` (tarjetas) y `017` (bloqueo de login) también migran y se
desarrollan en paralelo a esta rama, con orden de merge pactado
`013 → 014 → 016 → 017`. Como ninguna de esas specs tiene todavía `plan.md`
(no han corrido `/speckit-plan`) al momento de planear `016`, no hay
migraciones en vuelo con las que colisionar hoy. Antes de abrir el PR de
`016-auditoria`, la tarea de implementación DEBE re-correr
`uv run alembic heads` contra el `main` vigente en ese momento y, si
`013`/`014` ya se mezclaron,
rebasear y re-apuntar `down_revision` al head real (no a `919f3bd57721` a
ciegas) — este research documenta la decisión tomada *hoy*, no congela el
valor para siempre.

## 11. Índice de `audit_logs`

**Decision**: un índice simple (no funcional, no único) sobre `created_at`,
para soportar el orden "más reciente primero" de FR-005 sin escanear la
tabla completa a medida que crece.

**Rationale**: al no usar `lower()`/`trim()` ni ser `unique=True`, este
índice no cae en la advertencia de `AGENTS.md` sobre índices funcionales de
`leagues`/`teams` (esa nota aplica a índices que Alembic podría recrear
espuriamente por cómo Postgres normaliza `trim()`; no es este caso). Se deja
constancia de que se revisó la nota y no aplica, para que quien implemente
no la pase por alto.
