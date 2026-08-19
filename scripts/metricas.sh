#!/usr/bin/env bash
# Agrega las métricas por HU en una tabla para docs/caso-de-negocio.md.
#
#   ./scripts/metricas.sh              imprime la tabla en stdout
#   ./scripts/metricas.sh --escribir   además la inserta en docs/caso-de-negocio.md
#                                      entre los marcadores METRICAS:INICIO/FIN
#
# Lo derivado de git es tiempo de CALENDARIO (primer commit -> último commit de
# la spec), no esfuerzo real. El esfuerzo real lo aporta cada persona en
# docs/metricas/NNN-slug.md. Ver docs/metricas/README.md.

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

DEST="docs/caso-de-negocio.md"
INICIO="<!-- METRICAS:INICIO (generado por scripts/metricas.sh — no editar a mano) -->"
FIN="<!-- METRICAS:FIN -->"

campo() { # campo <archivo> <etiqueta> -> valor de la columna de una fila markdown
  [ -f "$1" ] || { echo ""; return; }
  grep -m1 -F "| $2 " "$1" 2>/dev/null | awk -F'|' '{gsub(/^ +| +$/,"",$3); print $3}' || echo ""
}

tabla() {
  echo "$INICIO"
  echo
  echo "| HU | Tareas (hechas/total) | Tests | Ciclos corrección | Tiempo spec+plan+tasks | Tiempo implement | Costo IA | Días calendario | Commits |"
  echo "|---|---|---|---|---|---|---|---|---|"

  for dir in specs/*/; do
    slug=$(basename "$dir")
    tasks_file="$dir/tasks.md"
    met_file="docs/metricas/${slug}.md"

    # --- derivado de tasks.md ---
    if [ -f "$tasks_file" ]; then
      total=$(grep -cE '^- \[[ x]\] T[0-9]{3}' "$tasks_file" || true)
      hechas=$(grep -cE '^- \[x\] T[0-9]{3}' "$tasks_file" || true)
      tareas="${hechas:-0}/${total:-0}"
    else
      tareas="—"
    fi

    # --- derivado de git ---
    primero=$(git log --reverse --format=%at -- "$dir" 2>/dev/null | head -1 || true)
    ultimo=$(git log -1 --format=%at -- "$dir" 2>/dev/null || true)
    commits=$(git log --oneline -- "$dir" 2>/dev/null | wc -l | tr -d ' ')
    if [ -n "$primero" ] && [ -n "$ultimo" ] && [ "$ultimo" -ge "$primero" ]; then
      dias=$(awk -v a="$primero" -v b="$ultimo" 'BEGIN{printf "%.1f", (b-a)/86400}')
    else
      dias="—"
    fi

    # --- aportado en docs/metricas/NNN-slug.md ---
    tests=$(campo "$met_file" "Tests en verde al cerrar")
    ciclos=$(campo "$met_file" "Ciclos de corrección")
    t_spec=$(campo "$met_file" "Tiempo real de trabajo — spec + plan + tasks")
    t_impl=$(campo "$met_file" "Tiempo real de trabajo — implement + tests")
    costo=$(campo "$met_file" "Costo IA aproximado de la HU")

    [ -f "$met_file" ] || { tests="⬜"; ciclos="⬜"; t_spec="⬜"; t_impl="⬜"; costo="⬜"; }

    echo "| $slug | $tareas | ${tests:-—} | ${ciclos:-—} | ${t_spec:-—} | ${t_impl:-—} | ${costo:-—} | $dias | $commits |"
  done

  echo
  echo "> \`⬜\` = falta \`docs/metricas/<spec>.md\`. **Días calendario** y **commits**"
  echo "> salen de \`git log\` y miden tiempo transcurrido, no esfuerzo: el esfuerzo"
  echo "> real son las columnas de tiempo, que aporta cada persona al cerrar su HU."
  echo "> Regenerar con \`./scripts/metricas.sh --escribir\`."
  echo
  echo "$FIN"
}

if [ "${1:-}" = "--escribir" ]; then
  [ -f "$DEST" ] || { echo "No existe $DEST" >&2; exit 1; }
  tmp=$(mktemp)
  if grep -qF "$INICIO" "$DEST"; then
    awk -v ini="$INICIO" -v fin="$FIN" -v nueva="$(tabla)" '
      index($0, ini) { print nueva; saltando=1; next }
      index($0, fin) { saltando=0; next }
      !saltando { print }
    ' "$DEST" > "$tmp"
  else
    { cat "$DEST"; echo; tabla; } > "$tmp"
  fi
  mv "$tmp" "$DEST"
  echo "Tabla actualizada en $DEST"
else
  tabla
fi
