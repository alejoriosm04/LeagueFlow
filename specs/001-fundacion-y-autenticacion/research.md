# Research: Fundación técnica y autenticación

**Feature**: `001-fundacion-y-autenticacion` · **Date**: 2026-08-18

Este documento resuelve las decisiones técnicas del proyecto completo, no solo
de esta HU. Es Phase 0 de la única spec cuyo `plan.md` decide stack — ver
`AGENTS.md` §5. Fuentes: `docs/enunciado.md` (recomendación del profesor/mentor
del curso), `.specify/memory/constitution.md` (restricciones no negociables),
`docs/actividad.md` (restricción de tiempo: entrega el 2026-08-22).

## 1. Backend: lenguaje y framework

**Decision**: Python 3.12 + FastAPI.

**Rationale**: `docs/enunciado.md` §9 lo recomienda explícitamente para
maximizar velocidad de desarrollo, crítico porque la Fase 2 de la actividad
exige construir una HU nueva en vivo en 5-10 minutos. FastAPI valida payloads
por diseño con Pydantic (cumple el requisito de seguridad "validación de
payloads" de la constitución sin código adicional) y genera OpenAPI
automáticamente a partir de las rutas (facilita el Principio III —
"Contratos de API Explícitos" — porque el contrato no se redacta a mano por
separado, se deriva del código y se congela en `contracts/`).

**Alternatives considered**:
- *Spring Boot (Java)*: mencionado como alternativa en el enunciado "si quieren
  demostrar Java empresarial", pero explícitamente en contra para una demo de
  5-10 min por su ceremonia de arranque y configuración. Rechazado por tiempo.
- *Express/Node.js*: unificaría lenguaje con el frontend (TypeScript en ambos
  extremos), pero su ecosistema de validación/ORM tipado es más disperso que
  Pydantic + SQLAlchemy. Rechazado: no aporta suficiente sobre FastAPI para
  justificar perder la recomendación explícita del enunciado.

## 2. Frontend: framework

**Decision**: React 18 + TypeScript + Vite (SPA), sin Next.js.

**Rationale**: El backend es un servicio HTTP separado (FastAPI); LeagueFlow no
necesita SSR ni SEO (las vistas públicas son de consulta interna a la liga, no
contenido indexable con urgencia de posicionamiento). Una SPA con Vite tiene
arranque de proyecto casi instantáneo y build a estático, compatible con
Vercel igual que Next.js. Usar Next.js añadiría un segundo lugar donde "podría"
vivir lógica de servidor (API routes de Next) que compite conceptualmente con
el único backend real (FastAPI) — contradice la arquitectura de monolito
modular con un solo backend que fija la constitución.

**Alternatives considered**:
- *Next.js*: válido si el equipo ya lo domina (enunciado lo deja abierto), pero
  sin esa señal explícita del equipo se prefiere la opción más simple. Revisar
  esta decisión si el equipo confirma dominio previo de Next.js — el costo de
  cambiar antes de escribir código de UI es bajo.

## 3. Base de datos y ORM

**Decision**: PostgreSQL + SQLAlchemy 2.0 (modo async) + Alembic para
migraciones.

**Rationale**: PostgreSQL está fijado por la constitución (Arquitectura de
Referencia). SQLAlchemy cumple el requisito de seguridad "SQL parametrizado/ORM
— nunca SQL concatenado". Alembic es el compañero estándar de SQLAlchemy y
satisface el Principio V (migraciones versionadas, reproducibles desde cero).

**Alternatives considered**: ORMs más ligeros (SQLModel, Tortoise) se
descartaron por menor madurez de su tooling de migraciones frente a
Alembic+SQLAlchemy, que es la combinación con más documentación para el plazo
de 4 días de la actividad.

## 4. Autenticación y sesiones

**Decision**: Sesión de servidor con token opaco en cookie `httpOnly` +
`Secure` + `SameSite=None`, respaldada por una tabla `sessions` con expiración
por inactividad. Contraseñas con `passlib[bcrypt]`.

**Corrección 2026-08-18 (checklist api.md CHK008/CHK014)**: la decisión
original fijaba `SameSite=Lax`, incompatible con la decisión de hosting de
§7 (frontend en Vercel, backend en Railway — dominios distintos). Con
`Lax`, los navegadores no envían la cookie en peticiones `fetch`/XHR
cross-site, solo en navegaciones top-level: el login habría funcionado en
desarrollo (mismo origen) y fallado en producción. `SameSite=None` exige
`Secure` (ya presente) y es obligatorio para que la cookie viaje entre
`*.vercel.app` y `*.railway.app`.

**Trade-off que introduce `SameSite=None`**: la cookie ahora viaja también
en peticiones cross-site iniciadas por otros orígenes (superficie de CSRF
mayor que con `Lax`). Mitigación ya presente sin trabajo adicional: todas
las rutas de escritura exigen `Content-Type: application/json`
(`contracts/conventions.md`), y un formulario HTML simple no puede fijar
ese header — un ataque CSRF clásico basado en formularios no puede
disparar estas peticiones. Un token CSRF de doble envío queda fuera de
esta corrección puntual; si se quiere profundizar, es un ítem nuevo de
`checklists/security.md`, no un bloqueante para implementar.

**Rationale**: FR-006 (`specs/001-fundacion-y-autenticacion/spec.md`) exige que
cerrar sesión revoque el acceso de inmediato. Con JWT sin estado, revocar antes
de que expire el token requiere una lista de revocación — es decir, terminas
reintroduciendo estado en el servidor de todas formas. Una sesión opaca en
tabla resuelve FR-006 de forma directa (se borra la fila, la sesión muere) y
FR-008 (atribuir cada escritura al usuario) porque cada request de escritura
valida su sesión contra esa misma tabla. Es la opción más simple que cumple
ambos requisitos a la vez.

**Alternatives considered**:
- *JWT stateless*: descartado por el problema de revocación inmediata en
  logout (FR-006) explicado arriba.
- *OAuth de terceros*: fuera de alcance — `specs/001-fundacion-y-autenticacion/spec.md`
  excluye explícitamente integraciones de autenticación externa.

## 5. Testing

**Decision**: `pytest` + `httpx.AsyncClient` (contract/integration backend),
con foco explícito en reglas de negocio (cálculo de puntos, desempates,
validaciones de partido); `Vitest` + React Testing Library (unit frontend);
`Playwright` limitado al camino crítico único: **crear liga → registrar
equipo → registrar partido → ver clasificación** (más el login como
precondición técnica del flujo, no como camino crítico adicional).

**Rationale**: `pytest`/`Vitest` son mandato directo del Principio II de la
constitución, sin alternativa. El foco de `pytest` en cálculo de puntos,
desempates y validaciones de partido, y el camino único de Playwright, son
indicación explícita del profesor/mentor del curso — evita la tentación de
escribir una suite E2E extensa que no aporta más señal que la unitaria.

**Alternatives considered**: Cypress para E2E — descartado, Playwright tiene
mejor soporte nativo para probar contra FastAPI+React sin configuración
adicional y es el sugerido en el enunciado.

## 6. CORS y configuración

**Decision**: `CORSMiddleware` de FastAPI con lista explícita de orígenes leída
de una variable de entorno (`ALLOWED_ORIGINS`), nunca `*`.

**Rationale**: Mandato directo de la constitución (Estándares de Seguridad
Obligatorios: "CORS restringido... NUNCA `*` en entornos desplegados") y del
Principio VI (secretos/configuración por variables de entorno).

## 7. Despliegue (hosting)

**Decision**: Backend + PostgreSQL en Railway; frontend estático en Vercel.
Ambos en capa gratuita.

**Rationale**: Sugerencia explícita del enunciado (§10), y ambos ofrecen capa
gratuita suficiente para el volumen esperado del proyecto (`Scale/Scope` en
Technical Context). Es una decisión de bajo costo de cambio: no afecta el
código del dominio si se revisa después.

**Alternatives considered**: Render, Fly.io — no descartados por mérito propio,
simplemente no evaluados por presión de tiempo (entrega 2026-08-22); si
Railway no alcanza en la capa gratuita, son la alternativa a probar primero.

## 8. CI/CD

**Decision**: Pipeline en GitHub Actions, en cada Pull Request: lint → tests
unitarios → tests de integración → escaneo de dependencias → build. El merge
a `main` (squash) dispara el deploy (frontend a Vercel, backend a Railway).

**Rationale**: Indicación explícita del profesor/mentor del curso. Además
implementa mecánicamente los Quality Gates 3, 4 y 7 de la constitución
("La suite completa de pruebas está en verde", "El linter pasa", "El escaneo
de dependencias no reporta vulnerabilidades críticas") — sin el pipeline, esos
gates dependen de que un humano los corra a mano antes de aprobar el PR, lo
cual no escala con 5 personas trabajando en paralelo.

**Alternatives considered**: ninguna evaluada — GitHub Actions es gratuito
para el repo, ya está donde vive el código, y es lo que pide el enunciado.

## 9. Convención de errores de API

**Decision**: Toda respuesta de error usa el envelope
`{"error": {"code": "<slug>", "message": "<texto para usuario>", "field": "<campo o null>"}}`,
con status HTTP semántico (400 validación, 401 sin sesión, 403 rol
insuficiente, 404 no encontrado, 409 conflicto de negocio, 500 solo con
mensaje genérico).

**Rationale**: Satisface FR-011/FR-012 de esta spec (mensaje comprensible que
identifica la regla incumplida, sin exponer detalles internos) y el Principio
III (contrato explícito) — todas las specs 002-011 reutilizan este envelope en
vez de inventar el suyo.

## 10. Parámetros concretos de sesión, credenciales y CORS

**Contexto**: decisiones tomadas el 2026-08-19 al iniciar `/speckit-implement`,
para cerrar los cinco ítems de `checklists/security.md` y `checklists/api.md`
que bloqueaban tareas concretas. Se documentan aquí, y no en el código, porque
el Principio I prohíbe inventar reglas directamente en la implementación.

| Parámetro | Valor | Justificación |
|---|---|---|
| Inactividad que expira la sesión | **8 horas**, deslizante (se extiende en cada request válido) | FR-006 exige expiración por inactividad sin fijar número. 8 h cubre una jornada de trabajo del organizador sin re-login, y deja la sesión muerta al día siguiente. Un valor corto (30 min) haría insufrible registrar una jornada completa de partidos |
| Cookie `Path` / `Max-Age` | `Path=/`, `Max-Age` = 8 h | Alineado con la expiración de servidor. `Path=/` porque la API vive bajo `/api/v1` pero el frontend necesita que la cookie viaje en toda la app |
| Longitud de contraseña | mínimo **10**, máximo **128** caracteres, sin reglas de composición | Recomendación vigente del NIST SP 800-63B: la longitud aporta más entropía que forzar símbolos, y las reglas de composición empujan a contraseñas predecibles. El máximo evita abuso de CPU en el hash bcrypt |
| Credencial del organizador semilla | Variables de entorno `SEED_ADMIN_USERNAME` y `SEED_ADMIN_PASSWORD`; el script **falla** si faltan | Principio VI: ningún secreto en el repo, ni siquiera una contraseña por defecto. Fallar en vez de usar un default evita el escenario clásico de dejar `admin/admin` en producción |
| Origen CORS en desarrollo | `http://localhost:5173` | Puerto por defecto de Vite. En despliegue se sustituye por el dominio real de Vercel vía `ALLOWED_ORIGINS` (T038), nunca `*` |

**Nota sobre `bcrypt` y el máximo de 128**: bcrypt trunca a 72 bytes. El límite
de 128 caracteres es de validación de entrada (evitar payloads enormes), no una
promesa de que los 128 se usen criptográficamente.

## 11. Versión de Python en desarrollo local

**Decision**: mantener Python 3.12 como versión objetivo (`pyproject.toml`,
CI y Railway), y usar `uv` para provisionar 3.12 localmente aunque el sistema
traiga otra versión.

**Rationale**: la máquina de desarrollo donde se implementó esta spec tiene
Python 3.10.12 de sistema. Bajar el objetivo a 3.10 por comodidad local
degradaría el entorno de producción sin razón; `uv` resuelve el desfase sin
tocar el Python del sistema. `uv venv --python 3.12` descarga e instala la
versión correcta de forma aislada.

**Consecuencia para el equipo**: nadie necesita instalar Python 3.12 a mano;
basta `uv venv --python 3.12` en `backend/` (documentado en `quickstart.md`).
