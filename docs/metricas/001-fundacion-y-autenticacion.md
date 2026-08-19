# Métricas — HU 001: Fundación técnica y autenticación

**Spec**: `specs/001-fundacion-y-autenticacion/spec.md` · **Responsable**: Alejo · **Cerrada**: 2026-08-19

## Llenado por el agente (al terminar la HU, antes del PR)

| Métrica | Valor |
|---|---|
| Tareas en `tasks.md` (total) | 41 |
| Tareas completadas | 41 / 41 |
| Tests escritos (backend) | 17 (11 integración + 6 contrato) |
| Tests escritos (frontend) | 4 |
| Tests en verde al cerrar | 21 / 21 |
| Ciclos de corrección | 10 |
| Archivos de código creados/modificados | 38 |

**Qué se reprocesó y por qué**:

- `src/core/db.py` salió con `from collections.abc AsyncGenerator` (sin `import`) — error de tipeo detectado al validar sintaxis, no en ejecución.
- El primer `logout` solo borraba la cookie y **no revocaba la sesión en la base de datos**: habría dejado el token vivo en el servidor y roto el AS6 en silencio. Reescrito por completo.
- El contract test buscaba el YAML con `parents[2]` (llegaba a `backend/`) en vez de `parents[3]` (raíz del repo).
- `RuntimeError: Event loop is closed` en 8 tests: el engine de SQLAlchemy se crea al importar el módulo y queda atado a un event loop, pero pytest-asyncio crea uno por test. Resuelto con `engine.dispose()` en el teardown.
- El test de atributos de cookie asumía `SameSite=None` siempre, pero en local la app cae a `lax` a propósito (los navegadores rechazan `None` sin `Secure` sobre http). Reescrito para forzar la configuración de producción, que es la que describe el contrato.
- Dos errores de TypeScript en el build: faltaban los tipos de `import.meta.env` y `vite.config.ts` necesitaba `defineConfig` de `vitest/config`.
- Vitest 2 traía su propia copia de Vite 6 y los tipos duplicados rompían el build. Actualizado a Vitest 3.
- `scripts/seed_admin.py` usaba `os.getenv`, que **no lee el archivo `.env`**, aunque el README prometía que sí. Migrado a `Settings` (pydantic-settings), que sí lo carga.
- **(configuración, no código)** `ALLOWED_ORIGINS` en Railway se guardó con barra final (`https://…vercel.app/`). Un encabezado `Origin` nunca lleva barra, así que la comparación literal fallaba y el backend rechazaba **todas** las peticiones del frontend.
- **(configuración, no código)** `VITE_API_URL` en Vercel se guardó sin el esquema (`leagueflow-production.up.railway.app`). El bundle construía una ruta relativa, pedía el recurso al propio dominio de Vercel, caía en el rewrite del SPA y recibía HTML en vez de JSON.

## Llenado por la persona (dos números, al cerrar)

| Métrica | Valor |
|---|---|
| Tiempo real de trabajo — spec + plan + tasks | <pendiente> |
| Tiempo real de trabajo — implement + tests | <pendiente> |
| Costo IA aproximado de la HU | <pendiente, del panel de uso> |

## Observaciones

El hallazgo más caro de haber descubierto tarde habría sido el `SameSite`: el
checklist de calidad de requisitos (`checklists/api.md` CHK008) lo detectó
**antes de escribir código**, cuando corregirlo costó cinco ediciones de
documento. Descubrirlo en la demo, con el frontend en Vercel y el backend en
Railway, habría significado un login roto sin forma de reproducirlo en local.

Dos de los reprocesos de código (logout sin revocar, seed sin leer `.env`)
fueron defectos donde el código hacía algo distinto de lo que su propia
documentación prometía — el tipo de fallo que solo aparece si se ejecuta de
verdad, no leyendo el diff.

Los dos últimos reprocesos son de **configuración de despliegue**, no de
código, y merecen atención aparte para el caso de negocio: una barra de más y
un `https://` de menos dejaron la aplicación completamente inutilizable, con
el backend sano, el frontend sirviendo y todos los tests en verde. **Ninguno
era reproducible en local**, porque en desarrollo frontend y backend comparten
origen. Es la justificación empírica de T039, la tarea que existía solo para
verificar el login en el entorno desplegado: sin ella, ambos fallos habrían
aparecido por primera vez durante la demostración.

GitGuardian aportó una lección aparte: de sus 5 detecciones iniciales, 3 eran
credenciales reales de PostgreSQL en CI y documentación (eliminadas de raíz con
`POSTGRES_HOST_AUTH_METHOD=trust`) y el resto falsos positivos sobre pares
`username`/`password` de test cuyos valores se generan en tiempo de ejecución.
Distinguir unas de otros costó varias iteraciones; conviene que el equipo lo
sepa antes de escribir sus propios tests de autenticación.
