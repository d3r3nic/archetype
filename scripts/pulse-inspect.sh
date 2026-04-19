#!/bin/bash
# Pulse Monitor — v1 inspector.
# Reads convention-mandated paths, emits .pulse-state.json to stdout or to a path.
# Language-agnostic (pure bash + standard tools). Portable across projects.
#
# Usage:
#   ./archetype/scripts/pulse-inspect.sh > .pulse-state.json
#   ./archetype/scripts/pulse-inspect.sh --out .pulse-state.json
#
# Reads:
#   - References.md        (project root or archetype/)
#   - feature-tree.md      (same)
#   - package.json         (root, if present — tech-stack hints)
#
# Emits JSON conforming to the v1 data contract documented in
# templates/pulse-monitor-spec.md and conventions/26-pulse-monitor.md.

set -euo pipefail

PROJECT_ROOT="$(pwd)"
OUT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --out) OUT="$2"; shift 2 ;;
    --root) PROJECT_ROOT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Locate References.md and feature-tree.md
REFS=""
TREE=""
for dir in "$PROJECT_ROOT" "$PROJECT_ROOT/archetype"; do
  [ -z "$REFS" ] && [ -f "$dir/References.md" ] && REFS="$dir/References.md"
  [ -z "$TREE" ] && [ -f "$dir/feature-tree.md" ] && TREE="$dir/feature-tree.md"
done

if [ -z "$REFS" ] || [ -z "$TREE" ]; then
  echo "{\"error\":\"References.md or feature-tree.md not found. Run from a bootstrapped project root.\"}" >&2
  exit 1
fi

# ---------- Section 1: Project overview ----------
# From References.md ## Project
project_name=""
project_purpose=""
project_stage=""
if grep -qE '^## Project' "$REFS"; then
  # Extract lines after ## Project until next ## header
  section=$(awk '/^## Project/,/^## [A-Z]/' "$REFS" | head -n -1)
  project_name=$(echo "$section" | grep -iE '^\-[[:space:]]*Name:' | head -1 | sed -E 's/^-[[:space:]]*Name:[[:space:]]*//')
  project_purpose=$(echo "$section" | grep -iE '^\-[[:space:]]*Purpose' | head -1 | sed -E 's/^-[[:space:]]*Purpose[^:]*:[[:space:]]*//')
  project_stage=$(echo "$section" | grep -iE '^\-[[:space:]]*Stage:' | head -1 | sed -E 's/^-[[:space:]]*Stage:[[:space:]]*//')
fi

# ---------- Section 2: Tech stack ----------
# From References.md ## Tech Stack — bullet list of key: value pairs
tech_stack_json="[]"
if grep -qE '^## Tech Stack' "$REFS"; then
  lines=$(awk '/^## Tech Stack/,/^## [A-Z]/' "$REFS" | grep -E '^\-[[:space:]]' | sed -E 's/^-[[:space:]]*//')
  items=""
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    key=$(echo "$line" | awk -F':' '{print $1}' | sed -E 's/[[:space:]]+$//')
    val=$(echo "$line" | awk -F':' '{$1=""; sub(/^: */,""); print}' | sed -E 's/^[[:space:]]+|[[:space:]]+$//g')
    # JSON-escape quotes and backslashes
    key_esc=$(echo "$key" | sed 's/\\/\\\\/g; s/"/\\"/g')
    val_esc=$(echo "$val" | sed 's/\\/\\\\/g; s/"/\\"/g')
    items="${items}{\"key\":\"${key_esc}\",\"value\":\"${val_esc}\"},"
  done <<< "$lines"
  items="${items%,}"
  tech_stack_json="[${items}]"
fi

# ---------- Section 3: Foundational systems ----------
# From feature-tree.md ## Foundational Systems — markdown table
systems_json="[]"
if grep -qE '^## Foundational Systems' "$TREE"; then
  rows=$(awk '/^## Foundational Systems/,/^## [A-Z]/' "$TREE" | grep -E '^\|[[:space:]]*[0-9-]+[[:space:]]*\|')
  items=""
  while IFS= read -r row; do
    [ -z "$row" ] && continue
    # Split on pipe, trim each cell
    num=$(echo "$row" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2}')
    name=$(echo "$row" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/, "", $3); print $3}')
    convention=$(echo "$row" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/, "", $4); print $4}')
    location=$(echo "$row" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/, "", $5); print $5}')
    status=$(echo "$row" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/, "", $6); print $6}')
    # Escape quotes
    num_e=$(echo "$num" | sed 's/\\/\\\\/g; s/"/\\"/g')
    name_e=$(echo "$name" | sed 's/\\/\\\\/g; s/"/\\"/g')
    convention_e=$(echo "$convention" | sed 's/\\/\\\\/g; s/"/\\"/g')
    location_e=$(echo "$location" | sed 's/\\/\\\\/g; s/"/\\"/g')
    status_e=$(echo "$status" | sed 's/\\/\\\\/g; s/"/\\"/g')
    items="${items}{\"num\":\"${num_e}\",\"name\":\"${name_e}\",\"convention\":\"${convention_e}\",\"location\":\"${location_e}\",\"status\":\"${status_e}\"},"
  done <<< "$rows"
  items="${items%,}"
  systems_json="[${items}]"
fi

# ---------- Section 4: Features ----------
# From feature-tree.md ## Features — markdown table (variable columns)
features_json="[]"
if grep -qE '^## Features' "$TREE"; then
  rows=$(awk '/^## Features/,/^## [A-Z]/' "$TREE" | grep -E '^\|' | grep -vE '^\|[[:space:]]*-+[[:space:]]*\|' | grep -vE '^\|[[:space:]]*#[[:space:]]*\|')
  items=""
  while IFS= read -r row; do
    [ -z "$row" ] && continue
    name=$(echo "$row" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/, "", $3); print $3}')
    location=$(echo "$row" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/, "", $4); print $4}')
    routes=$(echo "$row" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/, "", $5); print $5}')
    [ "$name" = "Feature" ] && continue
    [ -z "$name" ] && continue
    name_e=$(echo "$name" | sed 's/\\/\\\\/g; s/"/\\"/g')
    location_e=$(echo "$location" | sed 's/\\/\\\\/g; s/"/\\"/g')
    routes_e=$(echo "$routes" | sed 's/\\/\\\\/g; s/"/\\"/g')
    items="${items}{\"name\":\"${name_e}\",\"location\":\"${location_e}\",\"routes\":\"${routes_e}\"},"
  done <<< "$rows"
  items="${items%,}"
  features_json="[${items}]"
fi

# ---------- Section 5: Architecture (folder structure block) ----------
# From References.md ## Folder Structure — first ```...``` code block
architecture=""
if grep -qE '^## Folder Structure' "$REFS"; then
  architecture=$(awk '/^## Folder Structure/,/^## [A-Z]/' "$REFS" | awk '/^```/{flag=!flag; next} flag')
fi
architecture_e=$(echo "$architecture" | awk '{printf "%s\\n", $0}' | sed 's/\\/\\\\/g; s/"/\\"/g' | sed 's/\\\\n/\\n/g')

# ---------- Emit JSON ----------
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

JSON=$(cat <<EOF
{
  "generatedAt": "${TIMESTAMP}",
  "dataContractVersion": "v1",
  "project": {
    "name": "$(echo "$project_name" | sed 's/\\/\\\\/g; s/"/\\"/g')",
    "purpose": "$(echo "$project_purpose" | sed 's/\\/\\\\/g; s/"/\\"/g')",
    "stage": "$(echo "$project_stage" | sed 's/\\/\\\\/g; s/"/\\"/g')"
  },
  "techStack": ${tech_stack_json},
  "foundationalSystems": ${systems_json},
  "features": ${features_json},
  "architecture": "${architecture_e}"
}
EOF
)

if [ -n "$OUT" ]; then
  echo "$JSON" > "$OUT"
  echo "pulse state written to $OUT" >&2
else
  echo "$JSON"
fi
