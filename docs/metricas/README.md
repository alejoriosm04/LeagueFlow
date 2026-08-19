# Métricas por HU — cómo se llenan

Alimentan `docs/caso-de-negocio.md`, que es un entregable evaluado y exige
**datos reales medidos durante el proyecto**, no estimados al final.

## Por qué un archivo por HU y no una tabla compartida

Varias personas trabajan HU distintas en ramas paralelas. Si todas editaran la
misma tabla en `caso-de-negocio.md`, cada PR chocaría con el anterior en las
mismas líneas. Con un archivo por HU (`NNN-slug.md`), cada rama toca solo su
propio archivo: **cero conflictos de merge**. El script agrega los archivos en
la tabla final cuando se corre sobre `main`.

## Flujo

1. Al **terminar** una HU (tests en verde, antes de abrir el PR), el agente
   copia `_plantilla.md` a `docs/metricas/NNN-slug.md` y la llena.
2. El archivo se commitea **en el mismo PR de la HU** (igual que la spec).
3. Cuando alguien quiere la tabla consolidada:

   ```bash
   ./scripts/metricas.sh            # imprime la tabla
   ./scripts/metricas.sh --escribir # además la inserta en docs/caso-de-negocio.md
   ```

## Qué es automático y qué no — sin fingir precisión

| Dato | Origen | Confiabilidad |
|---|---|---|
| Fechas, nº de commits, tiempo transcurrido | `scripts/metricas.sh` desde `git log` | Alta, pero mide **tiempo de calendario**, no esfuerzo: si empezaste el lunes y terminaste el miércoles con un día sin tocar nada, salen 48h, no las 5h reales |
| Nº de tareas totales / completadas | script, desde `tasks.md` | Alta |
| Nº de tests y cuántos pasan | el agente, tras correr la suite | Alta |
| Ciclos de corrección (reprocesos) | el agente, contando cuántas veces tuvo que arreglar algo que ya había dado por hecho | Media — es un conteo honesto, no una métrica exacta |
| **Tiempo real de trabajo** | **la persona**, a ojo al cerrar la HU | Solo la sabe quien trabajó; el agente no puede medirla |
| **Costo / tokens de IA** | **la persona**, desde el panel de uso de su herramienta | El modelo no tiene acceso a su propio consumo; si un agente lo "reporta", se lo está inventando |

Las dos últimas filas son las únicas que exigen intervención humana, y son
literalmente dos números al cerrar cada HU.
