# Caso de negocio y comparativa de costos

Componente complementario del entregable. Se llena **con datos reales medidos
durante el proyecto**, no estimados al final: por eso conviene ir registrando
tiempos desde la primera HU.

## 1. Qué medir (registrar sobre la marcha)

Por cada HU de la línea base:

| HU | Tiempo spec+plan+tasks | Tiempo implement | Reprocesos | Tokens / costo IA |
|---|---|---|---|---|
| 1 | | | | |

Fuentes de dato: timestamps de commits (`git log`), duración de las sesiones de
Claude Code, y el consumo reportado por la herramienta de IA.

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
