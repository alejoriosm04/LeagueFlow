# Métricas — HU 015: Exportación de clasificación y calendario a CSV

**Spec**: `specs/015-exportacion-csv/spec.md` · **Responsable**: <nombre> · **Cerrada**: <pendiente>

## Llenado por el agente (al terminar la HU, antes del PR)

| Métrica | Valor |
|---|---|
| Tareas en `tasks.md` (total) | 23 |
| Tareas completadas | 21 (T021 y T022 pendientes de validación de cierre) |
| Tests escritos (backend) | 7 |
| Tests escritos (frontend) | 5 |
| Tests en verde al cerrar | Pendiente de suite backend PostgreSQL; 7 focalizados backend y 228 frontend en verde |
| Ciclos de corrección | 3 |
| Archivos de código creados/modificados | 9 |

**Ciclos de corrección**: cuántas veces hubo que volver sobre algo ya dado por
terminado (test que falló tras implementar, requisito mal interpretado,
refactor por un choque con otra HU). Cuenta honesta, no aspiracional: `0` es
sospechoso en una HU no trivial.

**Qué se reprocesó y por qué**:

- Se corrigieron los nombres de fixtures de integración para usar el cliente anónimo real del proyecto.
- Se ajustó la aserción CRLF para permitir saltos de línea embebidos y correctamente quoted.
- Se adaptó la comprobación de bytes del `Blob` a las capacidades de Blob de JSDOM.

## Llenado por la persona (dos números, al cerrar)

| Métrica | Valor |
|---|---|
| Tiempo real de trabajo — spec + plan + tasks | <ej. 45 min> |
| Tiempo real de trabajo — implement + tests | <ej. 2 h> |
| Costo IA aproximado de la HU | <del panel de uso de tu herramienta> |

## Observaciones

La implementación y sus pruebas focalizadas quedaron completas. El cierre permanece
pendiente de ejecutar la suite backend contra PostgreSQL y la matriz manual en
LibreOffice/Excel; esas herramientas no estuvieron disponibles en este entorno.
