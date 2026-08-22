# Implementation Plan: Bloqueo tras intentos fallidos de inicio de sesión

**Branch**: `017-bloqueo-login` | **Date**: 2026-08-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/017-bloqueo-login/spec.md`

**Nota**: esta HU no re-decide stack ni modelo de dominio — hereda ambos de
[`specs/001-fundacion-y-autenticacion/plan.md`](../001-fundacion-y-autenticacion/plan.md)
y [`data-model.md`](../001-fundacion-y-autenticacion/data-model.md)
(`AGENTS.md` §5). Es la **única spec del bloque paralelo (013–017) que modifica
código existente** (`backend/src/auth/`), a propósito: la autenticación es
territorio de un solo integrante y no compite con las demás.

## Summary

Se añade una barrera de fuerza bruta al login existente sin reescribirlo. Una
tabla nueva `login_attempts` guarda, por **identificador normalizado**
(`username.lower()`, el mismo criterio con que `AuthService.autenticar` ya
busca al usuario), el número de fallos consecutivos y hasta cuándo está
bloqueado. `AuthService` gana dos pasos alrededor de la verificación que ya
existe: **antes**, rechazar con `429 login_locked` si hay bloqueo vigente —lo
que hace que ni la contraseña correcta pase (FR-003)—; **después**, contar el
fallo con un UPSERT atómico de PostgreSQL y, al alcanzar el umbral, fijar
`blocked_until`. Un login correcto borra la fila (FR-005) y el desbloqueo es
implícito: no hay job ni scheduler, solo una comparación de timestamps
(FR-004).

La respuesta `401 invalid_credentials` existente **no cambia**, ni su forma ni
su simetría entre usuario inexistente y contraseña incorrecta; el `429` se
aplica por igual a identificadores registrados e inventados, de modo que
ninguna de las dos respuestas filtra si la cuenta existe (FR-006). Umbral y
duración salen de variables de entorno con los defaults de la spec — 5 intentos
y 15 minutos (FR-007). El frontend solo suma un código al catálogo de mensajes.

El detalle de cada decisión —incluida la tensión real entre FR-002 y FR-006, y
cómo se resuelve— está en [`research.md`](./research.md); la entidad nueva y
sus transiciones en [`data-model.md`](./data-model.md); el delta de contrato en
[`contracts/auth-lockout.openapi.yaml`](./contracts/auth-lockout.openapi.yaml);
qué hay que demostrar para cerrarla en [`quickstart.md`](./quickstart.md).

## Technical Context

**Language/Version**: Python 3.12 (backend) · TypeScript 5.7 + React 18
(frontend) — fijado en 001, sin cambios.

**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0 async, Alembic ·
React, Vite. **Ninguna dependencia nueva**: el UPSERT usa
`sqlalchemy.dialects.postgresql.insert`, que ya viene con SQLAlchemy.

**Storage**: PostgreSQL 16. Una tabla nueva (`login_attempts`) con un índice
único. Cero cambios sobre `users` y `sessions`.

**Testing**: `pytest` + `httpx.AsyncClient` (integration + contract) ·
`Vitest` (catálogo de mensajes del frontend).

**Target Platform**: backend Linux/Railway · SPA Vercel · navegador web.

**Project Type**: aplicación web con backend y frontend separados.

**Performance Goals**: el coste añadido al login normal es **una consulta por
índice único** (~1 ms), despreciable frente al `bcrypt` que ya se ejecuta. Bajo
bloqueo el coste **baja**: se rechaza antes de hashear (`research.md` §5). El
login sigue completándose en menos de 5 s (SC-003 de 001).

**Constraints**:

- El bloqueo se comprueba **antes** de verificar la contraseña; si no, un
  acierto se colaría y FR-003 quedaría incumplido.
- El incremento del contador **se commitea antes** de lanzar el error del
  login; si se lanza primero, la sesión se descarta, el contador se pierde y
  el bloqueo nunca se activa (`research.md` §7).
- El conteo debe ser consistente ante intentos simultáneos: UPSERT atómico, no
  `SELECT`+`UPDATE` (`research.md` §6).
- El conteo persiste a reinicios (lo exige la spec): nada en memoria de proceso.
- El bloqueo **no se auto-extiende** con intentos durante el bloqueo; si lo
  hiciera, un atacante persistente dejaría al usuario legítimo bloqueado para
  siempre y FR-004 dejaría de cumplirse.
- Ninguna prueba existente se modifica (Principio IV).
- Bloqueo por identificador, nunca por IP ni dispositivo (Out of Scope).

**Scale/Scope**: hasta 10 ligas y una decena de usuarios operativos (volumen de
referencia de 001). Una fila de `login_attempts` por identificador que haya
fallado; las de usuarios legítimos se borran al acertar.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio / regla | Estado | Cómo se cumple |
|---|---|---|
| I. La Especificación Manda | PASS | Cada elemento del diseño mapea a un FR: la tabla a FR-001, el `429` a FR-002, el orden de comprobación a FR-003, `blocked_until` a FR-004, el borrado al acertar a FR-005, la simetría a FR-006, las dos variables de entorno a FR-007. Nada fuera de la spec: sin desbloqueo manual, sin captcha, sin bloqueo por IP, sin notificaciones (Out of Scope) |
| II. Toda Regla de Negocio se Prueba | PASS | Los 7 Acceptance Scenarios más los edge cases (mayúsculas, concurrencia, contraseña correcta bajo bloqueo) tienen prueba nombrada en `quickstart.md` §Escenarios |
| III. Contratos de API Explícitos | PASS | `contracts/auth-lockout.openapi.yaml` documenta el delta. Añade `429` **solo** a `/auth/login`: adición aditiva y local, ningún endpoint existente cambia de status ni de forma. El frontend consume el `code`, nunca el `message` del servidor |
| IV. No Romper lo que ya Funciona | PASS | Ninguna prueba se borra, salta ni debilita. `test_as2_login_invalido_mensaje_generico` sigue en verde: hace 1 intento por identificador (umbral 5) y la simetría que afirma se conserva a ambos lados del umbral. `conftest.py` recrea el esquema por test, así que ningún contador se arrastra. Verificado sobre el código real en `research.md` §3 |
| V. Migraciones Versionadas | PASS | Un único archivo Alembic, `create_table` + índice, reproducible desde base vacía. Sin `DROP`/`CREATE` espurio de índices funcionales ajenos (`AGENTS.md`). Orden de merge del bloque paralelo respetado: 017 es la última (`research.md` §11) |
| VI. Cero Secretos en el Repositorio | PASS | `LOGIN_MAX_FAILED_ATTEMPTS` y `LOGIN_LOCKOUT_SECONDS` **no son secretos**, pero van por entorno y se documentan vacías en `.env.example` por convención. Los fixtures de prueba siguen generando credenciales en tiempo de ejecución (`secrets.token_urlsafe`), como ya hace `conftest.py` |
| VII. Código de IA con la Misma Vara | PASS | Regla de proceso de PR; el diseño no introduce excepción alguna |
| VIII. Entregabilidad Independiente por Dominio | PASS | Todo el cambio de backend vive en `src/auth/` y `src/core/config.py`. `login_attempts` no la lee ningún otro módulo y `auth` no adquiere dependencias nuevas. Sin ciclos. Desplegable sola: con la tabla creada y el default de 5 intentos, el comportamiento previo solo cambia al superar el umbral |
| Arquitectura: monolito modular | PASS | Cero servicios nuevos. Se descartó Redis explícitamente: la constitución exigiría una enmienda y un contador de 5 enteros no la justifica (`research.md` §1) |
| Regla de Derivación de Estadísticas | N/A | Esta HU no toca resultados, standings ni estadísticas |
| Estándares de Seguridad: validación de payloads | PASS | `LoginRequest` (Pydantic) ya valida y topa `username` a 60 caracteres, que es el largo de la columna |
| Estándares de Seguridad: SQL parametrizado / ORM | PASS | El UPSERT se construye con `postgresql.insert(...).on_conflict_do_update(...)` de SQLAlchemy. Cero concatenación de strings |
| Estándares de Seguridad: sin stack traces al cliente | PASS | El bloqueo viaja como `ErrorDeNegocio`, que el manejador existente traduce al envelope estándar |

**Una tensión que el gate obliga a declarar**: FR-002 (el error debe indicar
cuánto falta) y FR-006 (la respuesta no debe revelar que hay bloqueo) son
literalmente incompatibles. `research.md` §3 documenta la resolución: se cumple
FR-002 al pie de la letra y FR-006 en lo que protege de verdad —la simetría de
**existencia**—, porque el `429` se devuelve igual para identificadores
registrados e inexistentes y por tanto no filtra si la cuenta existe. **No es
una desviación de la constitución** (no hay principio en tensión), sino una
lectura de dos FR en conflicto, y por eso no ocupa la tabla de Complexity
Tracking. **Ya no está pendiente**: `/speckit-analyze` la marcó como HIGH y la
spec se enmendó el 2026-08-21 — FR-006 y SC-005 hablan ahora de simetría de
*existencia*, con la clarificación registrada en `spec.md` §Clarifications. Lo
que sigue describe, por tanto, un diseño alineado con la spec vigente, no una
reinterpretación de ella.

*Re-check post Phase 1*: el diseño de `data-model.md` y `contracts/` no
introdujo nada fuera de lo aprobado arriba. Al contrario, dos decisiones
**refuerzan** gates en vez de tensionarlos: la ausencia de clave foránea a
`users` es lo que permite contar identificadores inexistentes sin filtrar
existencia (FR-006), y el índice sobre columna normalizada —en lugar de un
índice funcional `lower(trim(...))`— evita el `--autogenerate` espurio que
`AGENTS.md` documenta para specs posteriores. **PASS confirmado.**

## Project Structure

### Documentation (this feature)

```text
specs/017-bloqueo-login/
├── plan.md                          # este archivo
├── research.md                      # Phase 0 — decisiones propias de esta HU
├── data-model.md                    # Phase 1 — entidad LoginAttempt y transiciones
├── contracts/
│   └── auth-lockout.openapi.yaml    # Phase 1 — delta de POST /auth/login (429)
├── quickstart.md                    # Phase 1 — validación end-to-end
├── checklists/
│   └── requirements.md              # ya existente (/speckit-specify)
└── tasks.md                         # Phase 2 (/speckit-tasks — aún no generado)
```

### Source Code (repository root)

Estructura heredada de 001 (`backend/` + `frontend/`). Solo se listan los
archivos que esta HU toca o crea:

```text
backend/
├── src/
│   ├── auth/
│   │   ├── models.py        # MODIFICADO  + IntentoDeLogin (tabla login_attempts)
│   │   └── service.py       # MODIFICADO  bloqueo antes de autenticar, conteo después
│   └── core/
│       ├── config.py        # MODIFICADO  + LOGIN_MAX_FAILED_ATTEMPTS, LOGIN_LOCKOUT_SECONDS
│       └── errors.py        # MODIFICADO  + headers opcionales en ErrorDeNegocio (Retry-After)
├── alembic/versions/
│   └── <nueva>_crear_tabla_login_attempts.py   # NUEVO — única migración de la HU
└── tests/
    ├── integration/
    │   └── test_bloqueo_login.py               # NUEVO — los 7 AS + edge cases
    └── contract/
        └── test_auth_contract.py               # MODIFICADO  + caso 429/Retry-After

frontend/
└── src/lib/mensajesDeError.ts                  # MODIFICADO  + code login_locked

.env.example                                    # MODIFICADO  + las dos llaves, vacías
docs/metricas/017-bloqueo-login.md              # NUEVO — al cerrar la HU (AGENTS.md §7)
```

**Structure Decision**: se mantiene la estructura de 001 sin alteración. El
cambio de backend está confinado al módulo de dominio `auth`, su dueño natural
(Principio VIII): `login_attempts` es estado de autenticación y ningún otro
módulo la consulta. La única excepción es `core/config.py`, que es el sitio
único donde el proyecto declara configuración por entorno — añadir dos campos
a `Settings` es usar esa convención, no romper el aislamiento del módulo.

`test_auth_contract.py` se **amplía** con el caso `429`, no se reescribe: sus
aserciones actuales quedan intactas (Principio IV).

**`router.py` no se toca.** La primera versión de este plan daba por hecho que
la cabecera `Retry-After` se emitiría desde el router; al desglosar las tareas
se comprobó que no puede ser: el bloqueo viaja como `ErrorDeNegocio` y lo
serializa el manejador global de `core/errors.py`, que construye su
`JSONResponse` **sin cabeceras** y por tanto las descartaría. La solución es
añadir un campo `headers: dict[str, str] | None = None` a `ErrorDeNegocio` y
pasarlo al `JSONResponse` del manejador: tres líneas, estrictamente aditivas
—el default `None` deja intacto el comportamiento de todos los errores
existentes de todas las specs— y sin duplicar la construcción del envelope en
el router. Es la única razón por la que esta HU toca `core/`, además de las dos
variables de configuración.

## Complexity Tracking

*Sin violaciones que justificar — tabla vacía a propósito.* La tensión FR-002 /
FR-006 está declarada arriba, en Constitution Check: es un conflicto entre dos
requisitos de la spec, no una desviación de la arquitectura ni de la
constitución.
