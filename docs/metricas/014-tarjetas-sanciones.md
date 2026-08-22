# Métricas — HU 014: Tarjetas y sanciones disciplinarias

**Spec**: `specs/014-tarjetas-sanciones/spec.md` · **Responsable**: <nombre> · **Cerrada**: 2026-08-22

## Llenado por el agente (al terminar la HU, antes del PR)

| Métrica | Valor |
|---|---|
| Tareas en `tasks.md` (total) | 33 |
| Tareas completadas | 33 |
| Tests escritos (backend) | 26 casos nuevos (6 unit card rules, 5 unit sanction rules, 4 contrato, 11 integración) |
| Tests escritos (frontend) | 5 (3 tarjetas en ficha de partido + 2 ficha disciplinaria) |
| Tests en verde al cerrar | 294 backend + suite frontend completa |
| Ciclos de corrección | 3 |
| Archivos de código creados/modificados | 22 |

**Ciclos de corrección**: cuántas veces hubo que volver sobre algo ya dado por
terminado (test que falló tras implementar, requisito mal interpretado,
refactor por un choque con otra HU). Cuenta honesta, no aspiracional: `0` es
sospechoso en una HU no trivial.

**Qué se reprocesó y por qué** (una línea por ciclo; es el dato más valioso
para la comparativa SDD vs. prompts sueltos del caso de negocio):

- Tras añadir el formulario de tarjetas en la ficha del partido, los tests de goles fallaban porque había dos campos «Jugador»/«Minuto»; se acotaron las consultas con `within(seccion)` en `events.test.tsx`.
- Ruff F401 por importar `validar_registro_de_gol` en el servicio tras generalizar a `validar_registro_de_evento`; se eliminó el import no usado.
- `DisciplinePage.module.css` usaba valores literales sin tokens `--lf-*`; se alineó con el patrón de `PlayerStatsPage.module.css` para pasar la auditoría SC-009.

## Llenado por la persona (dos números, al cerrar)

| Métrica | Valor |
|---|---|
| Tiempo real de trabajo — spec + plan + tasks | <ej. 45 min> |
| Tiempo real de trabajo — implement + tests | <ej. 2 h> |
| Costo IA aproximado de la HU | <del panel de uso de tu herramienta> |

## Observaciones

Implementación alineada con el plan paralelo: tarjeta como `MatchEvent`, módulo
`sanctions/` para la ficha derivada, migración solo del CHECK. La migración usa
`down_revision = 919f3bd57721`; re-puntear tras merge de 013 según AGENTS.md
antes de mergear a `main`.
