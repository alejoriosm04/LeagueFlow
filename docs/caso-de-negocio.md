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
| 001-fundacion-y-autenticacion | 41/41 | 21 / 21 | 10 | <pendiente> | <pendiente> | <pendiente, del panel de uso> | 0.7 | 3 |
| 002-crear-liga | — | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 0.1 | 2 |
| 003-registrar-equipos | — | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 0.1 | 2 |
| 004-registrar-jugadores | — | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 0.1 | 2 |
| 005-programar-partido | — | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 0.1 | 2 |
| 006-registrar-resultado | — | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 0.1 | 2 |
| 007-consultar-calendario | — | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 0.1 | 2 |
| 008-consultar-clasificacion | — | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 0.1 | 2 |
| 009-registrar-goles | — | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 0.1 | 2 |
| 010-alineaciones-estadisticas | — | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 0.1 | 2 |
| 011-dashboard-liga | — | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 0.1 | 2 |

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
