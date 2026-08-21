# Caso de negocio y comparativa de costos

Componente complementario del entregable. Se llena **con datos reales medidos
durante el proyecto**, no estimados al final: por eso conviene ir registrando
tiempos desde la primera HU.

## 1. Métricas por HU (se llenan solas sobre la marcha)

Cada HU deja su archivo en `docs/metricas/NNN-slug.md` al cerrarse — el agente
lo escribe como parte del ciclo de la HU (`AGENTS.md` §7), y la persona añade
dos números que el agente no puede conocer (tiempo real de trabajo y costo de
IA). La tabla de abajo la genera `./scripts/metricas.sh --escribir` a partir de
esos archivos más `git log`.

**No editar la tabla a mano**: se regenera. Ver `docs/metricas/README.md` para
qué dato es automático, cuál es aproximado y cuál requiere a una persona.

<!-- METRICAS:INICIO (generado por scripts/metricas.sh — no editar a mano) -->

| HU | Tareas (hechas/total) | Tests | Ciclos corrección | Tiempo spec+plan+tasks | Tiempo implement | Costo IA | Días calendario | Commits |
|---|---|---|---|---|---|---|---|---|
| 001-fundacion-y-autenticacion | 41/41 | 21 / 21 | 10 | <pendiente> | <pendiente> | <pendiente, del panel de uso> | 0.7 | 4 |
| 002-crear-liga | 16/16 | 25 / 25 | 4 | <ej. 45 min> | <ej. 2 h> | <del panel de uso de tu herramienta> | 0.8 | 4 |
| 003-registrar-equipos | 15/15 | 26 / 26 | 3 | <ej. 45 min> | <ej. 2 h> | <del panel de uso de tu herramienta> | 0.8 | 4 |
| 004-registrar-jugadores | 14/15 | 26 / 26 (21 backend + 5 frontend) | 1 | <ej. 45 min> | <ej. 2 h> | <del panel de uso de tu herramienta> | 0.9 | 3 |
| 005-programar-partido | 14/15 | 21 / 21 (16 backend + 5 frontend) | 1 | <ej. 45 min> | <ej. 2 h> | <del panel de uso de tu herramienta> | 0.9 | 3 |
| 006-registrar-resultado | 24/24 | 116 backend + 27 frontend | 3 | <ej. 45 min> | <ej. 2 h> | <del panel de uso de tu herramienta> | 1.0 | 3 |
| 007-consultar-calendario | 18/18 | 127 backend + 32 frontend | 3 | <ej. 45 min> | <ej. 2 h> | <del panel de uso de tu herramienta> | 1.1 | 3 |
| 008-consultar-clasificacion | 22/22 | 163 backend (74 unit+contrato, 89 integración) + 38 frontend | 6 | <ej. 45 min> | <ej. 2 h> | <del panel de uso de tu herramienta> | 1.7 | 3 |
| 009-registrar-goles | 23/23 | 169 backend (76 unit+contrato, 93 integración) + 38 frontend | 5 | <ej. 45 min> | <ej. 2 h> | <del panel de uso de tu herramienta> | 1.7 | 3 |
| 010-alineaciones-estadisticas | 23/29 | Frontend: 52/52 (`npx vitest run`, suite completa). Backend: no ejecutable en este entorno (sin PostgreSQL); revisados manualmente y verificados por lint, `ruff check`/`format`, compilación y generación del schema OpenAPI de la app viva | 4 | <ej. 45 min> | <ej. 2 h> | <del panel de uso de tu herramienta> | 1.9 | 4 |
| 011-dashboard-liga | 18/19 | Backend: 217 recolectados, 215 en verde localmente (12 nuevos del dashboard incluidos); 2 fallos preexistentes, ajenos a esta HU (ver Observaciones). Frontend: 51 en verde (7 nuevos) | 7 | <ej. 45 min> | <ej. 2 h> | <del panel de uso de tu herramienta> | 2.0 | 3 |

> `⬜` = falta `docs/metricas/<spec>.md`. **Días calendario** y **commits**
> salen de `git log` y miden tiempo transcurrido, no esfuerzo: el esfuerzo
> real son las columnas de tiempo, que aporta cada persona al cerrar su HU.
> Regenerar con `./scripts/metricas.sh --escribir`.

<!-- METRICAS:FIN -->

## 2. Costos de infraestructura (capa gratuita)

| Servicio | Uso | Plan | Costo/mes | Límite del plan gratuito |
|---|---|---|---|---|
| Hosting frontend | | | USD 0 | |
| Backend / API | | | USD 0 | |
| Base de datos | | | USD 0 | |
| CI/CD | GitHub Actions | Free | USD 0 | 2.000 min/mes en repos privados |

Costo real de infraestructura del proyecto: **USD 0** (capa gratuita + licencias
estudiantiles). Se debe documentar también el **costo si el proyecto escalara**
a plan pagado, que es lo que un evaluador de negocio querría ver.

## 3. Costos de IA

| Herramienta | Licencia | Costo real (estudiante) | Costo de lista |
|---|---|---|---|
| GitHub Copilot | Student Pack | USD 0 | ~USD 10/mes |
| Claude Code | | | |

## 4. Comparativa: SDD vs. desarrollo tradicional vs. prompts sueltos

| Criterio | Tradicional | Prompts sueltos | **SDD (Spec Kit)** |
|---|---|---|---|
| Tiempo por HU | | | |
| Retrabajo por requisitos mal entendidos | | | |
| Trazabilidad requisito → código | | | |
| Consistencia entre integrantes | | | |
| Onboarding de un nuevo integrante | | | |
| Costo de un cambio de alcance tardío | | | |

## 5. ROI

- **CAPEX** (construcción): horas-persona × tarifa referencia + costo IA.
- **OPEX** (operación mensual): infraestructura + licencias IA + mantenimiento.
- **Ahorro atribuible a SDD**: horas evitadas de retrabajo × tarifa.
- **ROI = (Ahorro − Inversión) / Inversión**, con el supuesto de tarifa
  documentado explícitamente (es un caso sintético; lo que se evalúa es el
  razonamiento, no el número).
