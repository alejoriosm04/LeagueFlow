# Métricas — HU 016: Auditoría de operaciones administrativas

**Spec**: `specs/016-auditoria/spec.md` · **Responsable**: <nombre> · **Cerrada**: 2026-08-22

## Llenado por el agente (al terminar la HU, antes del PR)

| Métrica | Valor |
|---|---|
| Tareas en `tasks.md` (total) | 27 |
| Tareas completadas | 27 |
| Tests escritos (backend) | 11 funciones de prueba nuevas (4 contrato incluyendo la verificación del propio contrato, 7 integración en `test_audit.py`) |
| Tests escritos (frontend) | 6 |
| Tests en verde al cerrar | Backend: 270 en verde localmente (11 nuevos de auditoría incluidos: 128 unit+contrato, 142 integración); 3 fallos preexistentes, ajenos a esta HU (ver Observaciones). Frontend: 229 en verde (6 nuevos), ESLint y build limpios |
| Ciclos de corrección | 7 |
| Archivos de código creados/modificados | 15 (3 modificados: `alembic/env.py`, `src/main.py`, `frontend/src/routes.tsx`; 12 nuevos: migración, 6 archivos de `backend/src/audit/`, 2 archivos de test backend, 3 archivos de `frontend/src/features/audit/`; no cuenta `specs/016-*` ni este archivo) |

**Ciclos de corrección**: cuántas veces hubo que volver sobre algo ya dado por
terminado (test que falló tras implementar, requisito mal interpretado,
refactor por un choque con otra HU). Cuenta honesta, no aspiracional: `0` es
sospechoso en una HU no trivial.

**Qué se reprocesó y por qué** (una línea por ciclo; es el dato más valioso
para la comparativa SDD vs. prompts sueltos del caso de negocio):

- `uv run alembic` como ejecutable directo lo bloqueó una directiva de Control
  de aplicaciones de Windows en este entorno (`os error 4551`); se resolvió
  invocando `uv run python -m alembic` en su lugar para todos los comandos de
  esta HU (T002, T005, T024).
- `uv run alembic upgrade head` completo contra SQLite falla en una migración
  **anterior** a esta HU (`d6e7f8a9b0c1`, usa `ALTER` de constraint que SQLite
  no soporta) — no se pudo generar `117e48f74b7c` con
  `alembic revision --autogenerate` (necesita una BD ya al head para diffear).
  Se escribió a mano siguiendo el patrón exacto de
  `c51b15d41886_crear_tablas_users_y_sessions.py`, y se validó por separado:
  `alembic heads`/`history` confirman un solo head sin bifurcación, y un
  script aparte creó solo `users`+`audit_logs` vía `Base.metadata.create_all`
  contra SQLite para confirmar que el DDL generado (tipos, FK, índice) es
  correcto.
- El propio middleware de esta HU reutiliza `AuthService.obtener_sesion_valida`
  (research.md §3), que bajo el sustituto SQLite local dispara el mismo
  `TypeError: can't compare offset-naive and offset-aware datetimes` ya
  documentado en HUs anteriores (pérdida de `tzinfo` al releer
  `DateTime(timezone=True)`) — pero aquí afecta a *cada* test autenticado de
  la propia HU, no solo a un caso aislado. Se construyó un arnés de
  verificación local (fuera del repo, en el directorio de scratchpad) que
  parchea `sqlalchemy.dialects.sqlite.base.DATETIME.result_processor` para
  adjuntar `tzinfo=UTC` al releer, replicando el comportamiento real de
  asyncpg/Postgres solo para poder correr los tests en este entorno; no se
  commiteó nada de esto.
- Diseñando T013 (historial vacío) se descubrió que es estructuralmente
  imposible dejar `audit_logs` vacía usando un login HTTP normal: acceder al
  endpoint exige sesión de organizador, y el propio `POST /auth/login` exitoso
  que la crea ya queda auditado (FR-004). Se corrigió el test para crear la
  sesión directamente en la base de datos (sin pasar por HTTP), como ya
  anticipaba el Independent Test de US2 en `tasks.md`.
- `uv run ruff check`/`format` sobre los archivos nuevos encontró 2 líneas
  >100 columnas en los tests y un bloque de imports desordenado en
  `test_audit.py`; `ruff format` además reformateó `middleware.py`
  (colapsó un `logger.exception(...)` multilínea). Se corrigieron antes de
  cerrar T026. La plantilla autogenerada de la migración (`typing.Union`,
  import sin ordenar) se dejó tal cual: `ci.yml` solo lintea `src tests`, no
  `alembic/`, y las migraciones previas del repo tienen exactamente el mismo
  patrón.
- La primera versión de `audit.test.tsx` afirmaba
  `screen.getAllByRole('columnheader')` justo después de esperar el
  encabezado `<h1>` (que se renderiza de inmediato, antes de que la petición
  mockeada resuelva) — pasó en aislamiento pero falló de forma intermitente
  al correr la suite completa de Vitest. Se corrigió esperando
  `screen.findByRole('table')` antes de leer las columnas.
- La prueba de estado de carga capturaba inicialmente el "Cargando…" de
  `ProtectedRoute` (mientras resuelve `/auth/me`, sin `role`), no el
  `role="status"` propio de `AuditLogPage`; se corrigió con una respuesta de
  `/admin/audit-log` controlada manualmente (una promesa que se resuelve
  después de la aserción) para separar ambos estados de carga.

## Llenado por la persona (dos números, al cerrar)

| Métrica | Valor |
|---|---|
| Tiempo real de trabajo — spec + plan + tasks | <ej. 45 min> |
| Tiempo real de trabajo — implement + tests | <ej. 2 h> |
| Costo IA aproximado de la HU | <del panel de uso de tu herramienta> |

## Observaciones

**Sin PostgreSQL en el entorno de esta sesión.** Igual que en HUs anteriores
(ver `011-dashboard-liga.md`), no había servicio local ni Docker. La
verificación se hizo contra SQLite (`aiosqlite`), con un arnés adicional
—descrito arriba— para neutralizar la pérdida de `tzinfo` que de otro modo
bloquea *todo* test autenticado, no solo los de esta HU. Bajo ese arnés, los
11 tests nuevos de auditoría pasan limpio, y también pasa la regresión
completa de la suite existente salvo 3 fallos ya conocidos y **confirmados
ajenos a esta HU** (se reprodujeron idénticos con
`git stash push -- backend/src/main.py`, es decir, sin el middleware ni el
router de auditoría presentes):

1. `test_lineups_statistics.py::test_eliminar_el_evento_gol...` —
   `AttributeError: 'str' object has no attribute 'hex'` al borrar un
   `MatchEvent` bajo SQLite (manejo de `Uuid` específico del dialecto).
2. `test_result_corrections.py::test_aprobar_aplica_y_rechazar_conserva` —
   mismo índice parcial (`postgresql_where`) documentado en `011` como
   caveat de SQLite.
3. `test_results.py::test_dos_registros_concurrentes_solo_aplican_uno` —
   mismo `with_for_update()` sin bloqueo real por fila bajo SQLite,
   documentado también en `011`.

Se recomienda que la persona responsable corra `uv run pytest` completo
contra Postgres real antes de mezclar, para confirmar que estos 3 fallos no
aparecen ahí — la expectativa, justificada arriba, es que no aparezcan.

**Migración escrita a mano, no autogenerada** (ver ciclo de corrección
arriba). `down_revision` apunta al head confirmado con `alembic heads`
(`919f3bd57721`) antes de implementar; al momento de cerrar esta HU, ninguna
de `013-grupos-divisiones`/`014-tarjetas-sanciones` había mezclado a `main`
todavía, así que ese head sigue vigente — si eso cambia antes de abrir el PR,
`AGENTS.md` exige re-confirmar `alembic heads` contra el `main` real y
re-apuntar `down_revision`.

**Quickstart validado vía la suite automatizada.** Los 5 escenarios de
`quickstart.md` corresponden 1:1 a aserciones de `test_audit.py`/
`test_audit_contract.py` (el propio documento los llama "pruebas
automatizadas equivalentes"); no había servidor+Postgres real disponible en
este entorno para repetirlos manualmente con `curl`.
