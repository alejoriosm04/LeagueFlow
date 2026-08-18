# LeagueFlow

Aplicación web para la gestión de ligas y torneos deportivos amateur —
inscripción de equipos, calendario de partidos, registro de resultados y tabla
de posiciones automática.

Proyecto académico construido de punta a punta (frontend, backend, base de datos,
despliegue y seguridad) con la metodología **Spec-Driven Development (SDD)**
usando [GitHub Spec Kit](https://github.com/github/spec-kit) y Claude Code.

> El enunciado completo de la actividad está en [`docs/enunciado.md`](docs/enunciado.md).

---

## Estado

| Área | Estado |
|---|---|
| Repositorio y convenciones | ✅ Listo |
| Spec Kit inicializado (v0.16.4, integración `claude`) | ✅ Listo |
| Constitution del proyecto | ⬜ Pendiente — `/speckit-constitution` en equipo |
| Backlog de ~10 HU priorizadas | ⬜ Pendiente — se gestiona en el **GitHub Project** del repo |
| Stack técnico | ⬜ Se decide en el primer `/speckit-plan` |
| Despliegue | ⬜ Pendiente |
| Caso de negocio | ⬜ Pendiente — [`docs/caso-de-negocio.md`](docs/caso-de-negocio.md) |

---

## Empezar

```bash
git clone git@github.com:alejoriosm04/LeagueFlow.git
cd LeagueFlow
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
specify check
```

El repo **ya está inicializado** con Spec Kit: no corras `specify init` otra vez.
Los pasos completos y las convenciones del equipo están en
[`docs/flujo-sdd.md`](docs/flujo-sdd.md) — léelo antes de tu primer commit.

## El ciclo SDD, en corto

```
/speckit-constitution   → reglas del proyecto (una sola vez, en equipo)
/speckit-specify        → QUÉ se construye        specs/NNN-*/spec.md
/speckit-clarify        → resuelve ambigüedades
/speckit-plan           → CÓMO se construye       plan.md, data-model.md, contracts/
/speckit-tasks          → tareas ejecutables      tasks.md
/speckit-implement      → código
```

Una HU = una rama = una carpeta en `specs/` = un PR.

## Estructura

```
AGENTS.md            Reglas que leen los agentes de IA (Codex, Cursor, Claude Code…)
.specify/            Motor de Spec Kit (plantillas, scripts, constitution) — se versiona
.claude/skills/      Comandos /speckit-* para Claude Code — se versiona
specs/               Una carpeta por Historia de Usuario — el entregable principal
docs/                Enunciado, flujo de trabajo, caso de negocio
```

## Equipo

| Integrante | GitHub | Rol principal |
|---|---|---|
| Alejandro Ríos | [@alejoriosm04](https://github.com/alejoriosm04) | _por definir_ |
| _pendiente_ | | |
| _pendiente_ | | |
