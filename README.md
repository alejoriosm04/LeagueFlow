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
| Constitution del proyecto | ✅ v1.0.0 — [`.specify/memory/constitution.md`](.specify/memory/constitution.md) |
| Backlog de 10 HU priorizadas | ✅ Repartido en `specs/002-*` a `specs/011-*` (origen: [`docs/backlog/backlog.md`](docs/backlog/backlog.md)) |
| Stack técnico | ✅ Fijado en [`specs/001-fundacion-y-autenticacion/plan.md`](specs/001-fundacion-y-autenticacion/plan.md) — FastAPI + PostgreSQL + React/TS |
| Spec 001 (fundación + auth) | ✅ Implementada y desplegada (41/41 tareas) |
| Spec 002 (crear liga) | ✅ Implementada y desplegada |
| Spec 003 (registrar equipos) | ✅ Implementada y desplegada |
| Spec 004 (registrar jugadores) | ✅ Implementada y desplegada |
| Spec 005 (programar partidos) | ✅ Implementada y desplegada |
| Spec 006 (registrar resultados) | ✅ Implementada y desplegada |
| Spec 007 (calendario y resultados) | ✅ Implementada y desplegada |
| Spec 008 (clasificación) | ✅ Implementada y desplegada (22/22 tareas, PR #36) |
| Spec 009 (registrar goles por jugador) | ✅ Implementada y desplegada (23/23 tareas, PR #37) |
| Spec 010 (alineaciones y estadísticas de jugadores) | ✅ Implementada y desplegada (PR #40) |
| Spec 011 (dashboard general de la liga) | ✅ Implementada y desplegada (PR #42) |
| Spec 012 (identidad visual y experiencia consistente) | 🔄 Implementada en rama `012-identidad-visual`, integrando Dashboard y Estadísticas (specs 010–011, mezcladas a `main` después de redactar esta historia) sobre el mismo catálogo visual, pendiente de PR |
| Despliegue | ✅ En línea — ver URLs abajo (la identidad visual de la Spec 012 aún no está desplegada: llega a producción cuando se mezcle su PR) |
| Caso de negocio | ⬜ Pendiente — [`docs/caso-de-negocio.md`](docs/caso-de-negocio.md); **medir tiempos desde la primera HU** |

> **Sobre lo visual:** hasta la Spec 012 el frontend era HTML funcional sin
> estilos — las specs 001 a 009 no definen apariencia, layout ni
> accesibilidad a propósito (esa decisión se aplazó, no se improvisó sobre la
> marcha). La Spec 012 es la que cierra esa brecha: sistema de valores
> visuales único (`frontend/src/styles/tokens.css`), marco de aplicación,
> catálogo de componentes reutilizable, tres estados de pantalla, contraste
> WCAG verificado por prueba automática y adaptabilidad a 1280/768/375 px. Su
> `spec.md` es la referencia — [`specs/012-identidad-visual/spec.md`](specs/012-identidad-visual/spec.md).

---

## Aplicación desplegada

| | URL |
|---|---|
| **Frontend** | https://leagueflow-pdms2.vercel.app |
| **API** | https://leagueflow-production.up.railway.app |
| Salud de la API | https://leagueflow-production.up.railway.app/api/health |
| Documentación de la API | https://leagueflow-production.up.railway.app/api/docs |

Frontend en Vercel, backend y PostgreSQL en Railway, ambos en capa gratuita.
Cada merge a `main` despliega automáticamente; las migraciones de Alembic se
aplican en el arranque de cada deploy.

Las consultas son públicas. Para registrar información hace falta iniciar
sesión: las credenciales del organizador viven en las variables de entorno de
Railway, nunca en el repositorio.

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

### Entorno local (obligatorio para `/speckit-implement`)

Escribir specs, planes y tareas no necesita nada más. **Implementar sí**: la
suite de pruebas corre contra un PostgreSQL real, así que necesitas Docker.

```bash
docker run -d --name leagueflow-db \
  -e POSTGRES_USER=leagueflow -e POSTGRES_DB=leagueflow \
  -e POSTGRES_HOST_AUTH_METHOD=trust \
  -p 5432:5432 postgres:16
docker exec leagueflow-db psql -U leagueflow -d postgres -c "CREATE DATABASE leagueflow_test;"
```

Sin contraseña a propósito: contenedor local y ninguna credencial en el repo
(Principio VI). Detalle completo — venv, `.env`, migraciones, organizador
semilla — en [`backend/README.md`](backend/README.md) y
[`frontend/README.md`](frontend/README.md); el porqué y los tropiezos típicos,
en [`docs/flujo-sdd.md`](docs/flujo-sdd.md) §2.2.

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
| Alejandro Ríos | [@alejoriosm04](https://github.com/alejoriosm04) | Fundación y autenticación (001), ligas (002) y equipos (003) |
| Quinn Villa | [@quinnie9](https://github.com/quinnie9) | Jugadores (004) y programación de partidos (005) |
| Lina Ballesteros | | Resultados y correcciones (006), calendario (007) |
| Jonathan Sandoval | [@jasgidp](https://github.com/jasgidp) | Clasificación (008), registro de goles (009) e identidad visual (012) |
