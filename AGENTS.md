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
