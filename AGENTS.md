# Instrucciones para agentes de IA — LeagueFlow

Proyecto académico bajo **Spec-Driven Development** con GitHub Spec Kit.
Documento completo del flujo: `docs/flujo-sdd.md`. Principios del proyecto:
`.specify/memory/constitution.md` (léela antes de generar código).

## Reglas no negociables

1. **La spec manda.** No implementes nada que no esté en `specs/NNN-*/spec.md`.
   Si falta información, pregunta o anótalo como *Assumption* en la spec — no lo
   inventes en el código.
2. **Nunca hagas `git push --force` ni pushes directos a `main`.** La rama está
   protegida por un ruleset (`non_fast_forward`, `deletion`, `pull_request`).
   Todo cambio entra por Pull Request desde una rama `NNN-slug`.
3. **Nunca escribas secretos en el repo.** Ni API keys, ni cadenas de conexión,
   ni tokens — tampoco en ejemplos, tests o comentarios. Todo va por variables de
   entorno; las llaves nuevas se documentan vacías en `.env.example`. GitHub
   tiene push protection activo y rechazará el push.
4. **El spec se commitea junto con el código que genera**, en el mismo PR.
5. **Decisiones técnicas compartidas: no se re-deciden por HU.** El stack, el
   modelo de dominio (`League/Team/Player/Match/MatchEvent/User`) y el esquema
   de autenticación y roles están fijados en
   `specs/001-fundacion-y-autenticacion/plan.md` y `data-model.md`. Ninguna
   spec posterior (`specs/002-*` en adelante) vuelve a correr `/speckit-plan`
   para decidir stack o remodelar esas entidades: su `plan.md` referencia el
   de `001` y solo documenta lo que **añade** sobre ese modelo (entidades o
   campos nuevos propios de esa HU). `specs/001-fundacion-y-autenticacion`
   DEBE mezclarse a `main` antes de que cualquier otra spec empiece su propio
   `/speckit-plan`.
6. **`docs/backlog/backlog.md` es solo referencia histórica.** Contiene el
   backlog completo ya clarificado, de donde se extrajo cada spec individual.
   No se planifica ni se implementa desde ahí — la fuente de verdad para
   `/speckit-plan` e `/speckit-implement` es siempre `specs/NNN-*/spec.md`.
7. **Al cerrar una HU, registra sus métricas.** Antes de dar por terminada una
   HU (tests en verde, antes de abrir el PR), copia
   `docs/metricas/_plantilla.md` a `docs/metricas/NNN-slug.md` y llena la
   sección "Llenado por el agente" con datos reales de esa HU: tareas
   completadas, tests escritos y en verde, ciclos de corrección, y **qué se
   reprocesó y por qué**. El archivo se commitea en el mismo PR de la HU.
   Alimenta `docs/caso-de-negocio.md`, que es un entregable evaluado.
   - **Nunca inventes el costo/tokens de IA ni el tiempo real de trabajo.** Esos
     dos campos los llena la persona; el modelo no tiene acceso a su propio
     consumo ni al reloj de quien trabaja. Déjalos como están en la plantilla.
   - Un `0` en "ciclos de corrección" de una HU no trivial es sospechoso:
     cuenta honestamente, el valor del dato está en que sea real.

## Formato de commits y PRs

Conventional Commits, con el número de la HU en el scope:

```
feat(003): registro de equipos
fix(004): validar cupo máximo del torneo
docs(spec): constitution v1.0.0
chore(ci): pipeline de tests en PR
```

**El título del PR es crítico:** el repo usa *squash merge* únicamente, así que
el título del PR se convierte en el mensaje del commit que queda en `main`
(y la descripción del PR en el cuerpo). Al abrir un PR:

- Título: `tipo(NNN): descripción en imperativo, en minúscula`.
- Cuerpo: link a `specs/NNN-*/spec.md` y checklist de criterios de aceptación.
- Nunca títulos genéricos tipo "cambios", "update" o "WIP".

Dentro de la rama los commits intermedios pueden ser informales (se colapsan).
