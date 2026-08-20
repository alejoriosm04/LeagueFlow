# Research: Consultar el calendario y los resultados

**Feature**: `007-consultar-calendario` · **Date**: 2026-08-20

## 1. Interfaz del calendario

**Decision**: ampliar `GET /leagues/{leagueId}/matches` con `status` opcional.

**Rationale**: 005 ya expone recurso, paginación y error de liga; sin el nuevo
parámetro el comportamiento permanece compatible.

**Alternatives considered**: `/calendar` agrupado, descartado por duplicar la
interfaz; filtro solo en navegador, descartado por descargar datos innecesarios.

## 2. Orden estable

**Decision**: `finished` usa `scheduled_at DESC, id DESC`; los demás filtros y
la consulta sin filtro usan `scheduled_at ASC, id ASC`.

**Rationale**: cumple el orden global incluso entre páginas y conserva 005.

**Alternatives considered**: ordenar en frontend, descartado porque cada página
no garantiza el orden total.

## 3. Volumen y paginación

**Decision**: conservar el máximo de 100 y hacer que el cliente recorra páginas
hasta `total`; en la vista general solicita `scheduled` y `finished` en paralelo.

**Rationale**: 190 filas requieren como máximo dos páginas por estado, sin
debilitar el límite compartido.

**Alternatives considered**: subir el límite a 200 o usar scroll infinito,
descartados por compatibilidad y porque SC-001 exige la vista completa.

## 4. Nombres de equipos

**Decision**: conservar `teamsApi.listar` y resolver UUID a nombre en frontend.

**Rationale**: respeta la interfaz pública del dominio Team y evita joins entre
módulos internos.

**Alternatives considered**: join directo desde MatchService y duplicación de
nombres, descartados por acoplamiento y desnormalización.

## 5. Estados visibles

**Decision**: la vista general agrupa `scheduled` como “Próximos” y `finished`
como “Jugados”. `in_progress` y `cancelled` aparecen solo bajo su filtro.

**Rationale**: no clasifica falsamente un cancelado como próximo o jugado y
cubre el enum completo de FR-002.

**Alternatives considered**: ocultarlos o mezclar cancelados con próximos,
descartados por cobertura incompleta o semántica falsa.

## 6. Criterios medibles

**Decision**: automatizar conteo/orden con 190 partidos y proporcionar un script
idempotente de datos de desarrollo que construya 20 equipos/190 partidos en la
base configurada, usando como autor al organizador semilla identificado por
`SEED_ADMIN_USERNAME`. Con esos datos se mide manualmente el render completo;
SC-002 se verifica desde la liga hasta el primer próximo en dos interacciones o
menos.

**Rationale**: el tiempo de consulta aislado no representa la vista completa y
los fixtures de pytest se eliminan al terminar; el script persistente hace la
medición manual repetible sin mezclar datos semilla con migraciones ni guardar
credenciales en el repositorio.

**Alternatives considered**: medir solo SQL, descartado porque SC-001 es una
experiencia de navegador; reutilizar directamente fixtures pytest, descartado
porque su limpieza deja la aplicación sin el escenario manual.
