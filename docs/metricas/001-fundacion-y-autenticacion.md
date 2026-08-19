# Métricas — HU 001: Fundación técnica y autenticación

**Spec**: `specs/001-fundacion-y-autenticacion/spec.md` · **Responsable**: Alejo · **Cerrada**: 2026-08-19

## Llenado por el agente (al terminar la HU, antes del PR)

| Métrica | Valor |
|---|---|
| Tareas en `tasks.md` (total) | 41 |
| Tareas completadas | 36 (las 5 restantes exigen cuentas en Railway/Vercel) |
| Tests escritos (backend) | 17 (11 integración + 6 contrato) |
| Tests escritos (frontend) | 4 |
| Tests en verde al cerrar | 21 / 21 |
| Ciclos de corrección | 8 |
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

Dos de los ocho reprocesos (logout sin revocar, seed sin leer `.env`) fueron
defectos donde el código hacía algo distinto de lo que su propia documentación
prometía — el tipo de fallo que solo aparece si se ejecuta de verdad, no
leyendo el diff.
