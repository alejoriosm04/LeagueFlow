# Flujo de trabajo del equipo (SDD con Spec Kit)

Este documento es el "contrato operativo" del repo: cómo se trabaja, qué se
versiona y cómo se reparte el trabajo. Si algo aquí choca con la
`constitution.md`, manda la constitution.

---

## 1. Qué se versiona y qué no

| Ruta | ¿Se sube? | Por qué |
|---|---|---|
| `.specify/templates/`, `.specify/scripts/`, `.specify/workflows/` | ✅ Sí | Es el motor SDD. Todos deben tener exactamente el mismo. |
| `.specify/memory/constitution.md` | ✅ Sí | Reglas del proyecto; es artefacto evaluable. |
| `.specify/feature.json` | ❌ No | Puntero local a la feature activa de **tu** máquina. Ya está en `.specify/.gitignore`. |
| `.claude/skills/speckit-*/` | ✅ Sí | Comandos `/speckit-*`. Sin esto un compañero no puede correr el motor. |
| `.claude/settings.local.json` | ❌ No | Permisos personales de cada quien. |
| `.codex/`, `.cursor/`, … | ✅ Sí | Integraciones de otros agentes del equipo (ver 2.1). |
| `AGENTS.md` / `CLAUDE.md` | ✅ Sí | Reglas que **todos** los agentes leen automáticamente. Editarlas es editar el comportamiento del equipo entero. |
| `specs/NNN-*/` (spec, plan, tasks, research…) | ✅ Sí | **Es el entregable principal.** La nota depende de que la trazabilidad spec → código esté en el repo. |
| `.env` | ❌ Nunca | Secretos. Se sube `.env.example` con las llaves vacías. |

> Regla de oro: **el spec se commitea junto con el código que genera**, en el
> mismo PR. Un PR con código sin su carpeta `specs/` no se aprueba.

---

## 2. Setup de cada integrante (una sola vez)

```bash
git clone git@github.com:alejoriosm04/LeagueFlow.git
cd LeagueFlow

# Spec Kit (requiere Python 3.11+ y uv)
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
specify check          # verifica que el CLI y el agente estén disponibles
```

**No corran `specify init` de nuevo.** El repo ya viene inicializado
(`.specify/` + `.claude/skills/`); volver a inicializar sobrescribe plantillas y
genera conflictos. Con el clone es suficiente.

Verificación rápida de que quedaste listo: abre Claude Code en la carpeta y
escribe `/speckit-` — deben aparecer los 10 comandos.

---

## 2.1. Si usas otro agente (Codex, Cursor, Gemini…)

El repo está inicializado con la integración `claude`, pero **Spec Kit soporta
varios agentes en el mismo proyecto**. Nadie debe correr `specify init` de nuevo:
el comando correcto es `integration install`, que agrega *solo* la carpeta de tu
agente sin tocar `.specify/`.

```bash
specify integration list                  # ver los ~40 agentes disponibles
specify integration install codex         # Codex CLI
specify integration install cursor-agent  # Cursor
specify integration install gemini        # Gemini CLI
specify integration install copilot --force   # ver nota abajo
```

Qué cambia al instalar:

| Se modifica | Qué pasa |
|---|---|
| `.codex/`, `.cursor/`, … | Nueva carpeta con los comandos `speckit.*` de tu agente |
| `.specify/integration.json` | Tu agente se agrega a `installed_integrations` |
| `.specify/templates/`, `.specify/scripts/` | **No se tocan** — son compartidos |

**Sí se commitea.** Instálalo una sola vez, súbelo, y el resto del equipo ya lo
tiene al hacer `pull`. Todos los agentes leen las mismas plantillas y escriben en
la misma carpeta `specs/`, así que el trabajo es intercambiable entre integrantes
sin importar con qué herramienta lo hicieron.

Detalles a tener en cuenta:

- **`--force` para los no "safe".** `specify integration list` tiene una columna
  *Safe*: `yes` = convive sin problema con otras integraciones. GitHub Copilot,
  Amp, opencode y Zed están marcados `no` (suelen pelearse por rutas como
  `.github/prompts/`), así que exigen `--force` para instalarse junto a otra.
- **No corran `specify integration use` ni `switch`.** Cambian el agente *default*
  del proyecto en `.specify/integration.json`, que es un archivo compartido: si
  cada quien lo cambia, se generan conflictos de merge inútiles. Dejamos el
  default en `claude` y punto — el default solo afecta a `specify workflow run`
  con `integration: auto`; los comandos de tu agente funcionan igual.
- **Los comandos cambian de nombre según el agente.** En Claude Code son
  `/speckit-specify`; en otros aparecen como `/speckit.specify` o
  `speckit.specify`. Es el mismo motor y produce los mismos artefactos.
- **`specify check`** te dice si el CLI de tu agente está instalado y detectado.

---

## 3. Ciclo por Historia de Usuario

Una HU = una rama = una carpeta en `specs/` = un PR.

```bash
git switch main && git pull            # 1. parte siempre de main actualizado
git switch -c 003-registro-equipos     # 2. rama con el MISMO número que la spec
```

Luego, dentro de Claude Code:

| Paso | Comando | Qué produce |
|---|---|---|
| 1 | `/speckit-specify <descripción de la HU>` | `specs/NNN-nombre/spec.md` (el **qué**, sin tecnología) |
| 2 | `/speckit-clarify` | Resuelve ambigüedades antes de planear (evita replanear después) |
| 3 | `/speckit-plan` | `plan.md`, `research.md`, `data-model.md`, `contracts/` (el **cómo**) |
| 4 | `/speckit-tasks` | `tasks.md` — tareas ordenadas por dependencias |
| 5 | `/speckit-analyze` | Chequeo de consistencia spec ↔ plan ↔ tasks (opcional pero barato) |
| 6 | `/speckit-implement` | Escribe el código siguiendo `tasks.md` |

> Ojo: Spec Kit **no crea la rama de git** en esta configuración; solo crea la
> carpeta `specs/NNN-*`. La rama la creas tú y debe llevar el mismo número, para
> que rama, spec y PR queden alineados.

Al terminar:

```bash
git add -A
git commit -m "feat(003): registro de equipos"
git push -u origin 003-registro-equipos
gh pr create --fill
```

---

## 4. Convenciones

**Ramas:** `NNN-slug-corto` (el `NNN` lo asigna Spec Kit al correr `/speckit-specify`).

**Commits y títulos de PR:** Conventional Commits, con el número de la HU en el scope.

```
feat(003): registro de equipos
fix(004): validar cupo máximo del torneo
docs(spec): constitution v1.0.0
chore(ci): pipeline de tests en PR
```

> ⚠️ **El título del PR es lo que queda en `main`.** El repo está configurado con
> *squash merge* únicamente: al mergear, todos los commits de la rama se colapsan
> en uno solo cuyo mensaje es el **título del PR** (cuerpo = descripción del PR).
> Los `wip`, `fix typo` y `asdf` de tu rama desaparecen — pero un PR titulado
> "cambios" queda para siempre en el historial de `main`.
>
> Consecuencia práctica: dentro de tu rama commitea como quieras; **el título del
> PR sí se escribe con cuidado** y en formato Conventional Commit.

**PRs:** título en formato `tipo(NNN): descripción`, descripción con link a
`specs/NNN-*/spec.md` y checklist de criterios de aceptación. La rama se borra
sola al mergear.

**`main` siempre desplegable.** Nada se mergea con el pipeline en rojo.

### Reglas activas en el repositorio (ruleset "main protegida")

`main` está protegida. Estas reglas están activas y **no** son sugerencias:

| Regla | Efecto |
|---|---|
| `deletion` | No se puede borrar `main` |
| `non_fast_forward` | **No se puede hacer `git push --force` a `main`** |
| `pull_request` | Todo cambio entra por PR, con 1 aprobación |

**Bypass:** los roles Write, Maintain y Admin pueden mergear sin esperar la
aprobación. Esto existe **solo para la demo en vivo**, donde esperar una revisión
puede costar el deploy. En la fase de línea base **se pide la revisión igual**:
el bypass es una salida de emergencia, no el flujo normal.

Si un push a `main` te sale rechazado, no busques cómo forzarlo — abre un PR.

Además están activos: *secret scanning con push protection* (GitHub rechaza el
push que contenga una API key o cadena de conexión) y *Dependabot* (alertas y
PRs automáticos por dependencias vulnerables).

---

## 5. Reparto para la demo en vivo

El profesor asigna 2 HU nuevas en el momento, y **cada integrante debe correr el
motor SDD desde su propia máquina**. Para que eso no se vuelva un caos:

1. Una sola persona corre `/speckit-specify` de la HU y hace push de la spec.
   Así todos parten de la misma verdad.
2. Los demás hacen `git pull` y toman **tareas distintas** de `tasks.md`
   (`/speckit-implement` acepta un subconjunto de tareas), cada uno en su rama
   `NNN-slug--<inicial>`.
3. Se reparte por capa para minimizar conflictos: BD/migraciones, API, UI, tests.
4. Se mergea en orden (BD → API → UI → tests) y el deploy automático de `main`
   publica el resultado.

Antes de la sustentación: `git pull`, `specify check` y una corrida de prueba
del ciclo completo en cada máquina. El ensayo se hace **antes**, no en vivo.

---

## 6. Calidad y seguridad (requisito del enunciado)

Lo mínimo que debe existir y quedar demostrable en el repo:

- Pruebas automatizadas corriendo en CI en cada PR (unitarias + al menos un
  flujo end-to-end).
- Validación de entradas en el backend y manejo de errores sin filtrar stack traces.
- Autenticación/autorización real en los endpoints que la necesiten.
- Secretos solo por variables de entorno; `.env` jamás en git.
- Escaneo de dependencias (Dependabot o `npm audit` / `pip-audit` en CI).
- Rama `main` protegida: PR obligatorio, CI en verde.
