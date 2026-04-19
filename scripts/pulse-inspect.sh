#!/bin/bash
# Pulse Monitor — v1.1 inspector.
# Reads convention-mandated paths, emits .pulse-state.json to stdout or to a path.
# Language-agnostic (pure bash + standard tools). Portable across macOS + Linux.
#
# Usage:
#   ./archetype/scripts/pulse-inspect.sh > .pulse-state.json
#   ./archetype/scripts/pulse-inspect.sh --out .pulse-state.json
#   ./archetype/scripts/pulse-inspect.sh --root /path/to/project --out state.json
#
# Reads:
#   - References.md        (project root or archetype/)
#   - feature-tree.md      (same)
#
# Emits JSON conforming to the v1.1 data contract documented in
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

# Helper: extract a named ## section using a flag state machine.
# Stops cleanly at the next ## header.
extract_section() {
  local file="$1"
  local header="$2"
  awk -v hdr="$header" '
    $0 ~ "^## " hdr { flag=1; next }
    /^## [A-Za-z]/ { flag=0 }
    flag { print }
  ' "$file"
}

json_escape() {
  # Escape for JSON string context.
  printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e "s/$(printf '\t')/\\\\t/g"
}

# ---------- Section 1: Project overview ----------
project_section="$(extract_section "$REFS" "Project")"
project_name="$(printf '%s\n' "$project_section" | grep -iE '^\-[[:space:]]*Name:' | head -1 | sed -E 's/^-[[:space:]]*Name:[[:space:]]*//' || true)"
project_purpose="$(printf '%s\n' "$project_section" | grep -iE '^\-[[:space:]]*Purpose' | head -1 | sed -E 's/^-[[:space:]]*Purpose[^:]*:[[:space:]]*//' || true)"
project_stage="$(printf '%s\n' "$project_section" | grep -iE '^\-[[:space:]]*Stage:' | head -1 | sed -E 's/^-[[:space:]]*Stage:[[:space:]]*//' || true)"

# ---------- Section 2: Tech stack ----------
tech_stack_json="[]"
tech_section="$(extract_section "$REFS" "Tech Stack")"
if [ -n "$tech_section" ]; then
  items=""
  first=1
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    # Only process lines starting with "- "
    case "$line" in
      -*)
        content="${line#*- }"
        # Split on first colon
        key="${content%%:*}"
        val="${content#*:}"
        key="$(printf '%s' "$key" | sed -E 's/^[[:space:]]+|[[:space:]]+$//g')"
        val="$(printf '%s' "$val" | sed -E 's/^[[:space:]]+|[[:space:]]+$//g')"
        [ -z "$key" ] && continue
        [ "$first" -eq 0 ] && items="${items},"
        items="${items}{\"key\":\"$(json_escape "$key")\",\"value\":\"$(json_escape "$val")\"}"
        first=0
        ;;
    esac
  done <<< "$tech_section"
  tech_stack_json="[${items}]"
fi

# ---------- Section 3: Foundational systems ----------
systems_json="[]"
systems_section="$(extract_section "$TREE" "Foundational Systems")"
if [ -n "$systems_section" ]; then
  items=""
  first=1
  while IFS= read -r row; do
    [ -z "$row" ] && continue
    case "$row" in
      \|*)
        # Skip header+separator rows
        echo "$row" | grep -qE '^\|[[:space:]]*[0-9-]+[[:space:]]*\|' || continue
        # Skip markdown table separator rows (|---|---|---|)
        echo "$row" | grep -qE '^\|[[:space:]]*-+[[:space:]]*\|[[:space:]]*-+' && continue
        num="$(printf '%s' "$row" | awk -F'|' '{gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2); print $2}')"
        name="$(printf '%s' "$row" | awk -F'|' '{gsub(/^[[:space:]]+|[[:space:]]+$/, "", $3); print $3}')"
        conv="$(printf '%s' "$row" | awk -F'|' '{gsub(/^[[:space:]]+|[[:space:]]+$/, "", $4); print $4}')"
        loc="$(printf '%s' "$row" | awk -F'|' '{gsub(/^[[:space:]]+|[[:space:]]+$/, "", $5); print $5}')"
        status="$(printf '%s' "$row" | awk -F'|' '{gsub(/^[[:space:]]+|[[:space:]]+$/, "", $6); print $6}')"
        [ "$first" -eq 0 ] && items="${items},"
        items="${items}{\"num\":\"$(json_escape "$num")\",\"name\":\"$(json_escape "$name")\",\"convention\":\"$(json_escape "$conv")\",\"location\":\"$(json_escape "$loc")\",\"status\":\"$(json_escape "$status")\"}"
        first=0
        ;;
    esac
  done <<< "$systems_section"
  systems_json="[${items}]"
fi

# ---------- Section 4: Features (+ gather edges for the diagram) ----------
features_json="[]"
features_section="$(extract_section "$TREE" "Features")"
features_edges=""
if [ -n "$features_section" ]; then
  items=""
  first=1
  while IFS= read -r row; do
    [ -z "$row" ] && continue
    case "$row" in
      \|*)
        # Skip table separators (|---|---|)
        echo "$row" | grep -qE '^\|[[:space:]]*-+[[:space:]]*\|' && continue
        # Extract columns; tolerate variable column layouts
        c3="$(printf '%s' "$row" | awk -F'|' '{gsub(/^[[:space:]]+|[[:space:]]+$/, "", $3); print $3}')"
        c4="$(printf '%s' "$row" | awk -F'|' '{gsub(/^[[:space:]]+|[[:space:]]+$/, "", $4); print $4}')"
        c5="$(printf '%s' "$row" | awk -F'|' '{gsub(/^[[:space:]]+|[[:space:]]+$/, "", $5); print $5}')"
        c6="$(printf '%s' "$row" | awk -F'|' '{gsub(/^[[:space:]]+|[[:space:]]+$/, "", $6); print $6}')"
        [ "$c3" = "Feature" ] && continue
        [ -z "$c3" ] && continue
        [ "$c3" = "#" ] && continue
        # c3 = feature name, c4 = location, c5 = routes, c6 = systems used
        [ "$first" -eq 0 ] && items="${items},"
        items="${items}{\"name\":\"$(json_escape "$c3")\",\"location\":\"$(json_escape "$c4")\",\"routes\":\"$(json_escape "$c5")\",\"systemsUsed\":\"$(json_escape "$c6")\"}"
        first=0
        # Gather edges from c6 (systems used)
        if [ -n "$c6" ]; then
          feat_id="$(printf '%s' "$c3" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/_/g')"
          IFS=',' read -ra sys_arr <<< "$c6"
          for s in "${sys_arr[@]}"; do
            s_clean="$(printf '%s' "$s" | sed -E 's/^[[:space:]]+|[[:space:]]+$//g')"
            [ -z "$s_clean" ] && continue
            s_id="$(printf '%s' "$s_clean" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/_/g')"
            features_edges="${features_edges}  feat_${feat_id} --> sys_${s_id}"$'\n'
          done
        fi
        ;;
    esac
  done <<< "$features_section"
  features_json="[${items}]"
fi

# ---------- Section 5: Folder structure (verbatim code block from References.md) ----------
architecture=""
arch_section="$(extract_section "$REFS" "Folder Structure")"
if [ -n "$arch_section" ]; then
  architecture="$(printf '%s\n' "$arch_section" | awk '/^```/{flag=!flag; next} flag')"
fi
architecture_escaped="$(printf '%s' "$architecture" | awk '{ gsub(/\\/, "\\\\"); gsub(/"/, "\\\""); printf "%s\\n", $0 }')"

# ---------- Section 6: Architecture diagram (Mermaid flowchart) ----------
diagram="flowchart LR"$'\n'

# Foundational systems subgraph
if [ -n "$systems_section" ]; then
  diagram="${diagram}  subgraph systems[\"Foundational Systems\"]"$'\n'
  diagram="${diagram}    direction TB"$'\n'
  while IFS= read -r row; do
    [ -z "$row" ] && continue
    case "$row" in
      \|*)
        echo "$row" | grep -qE '^\|[[:space:]]*[0-9-]+[[:space:]]*\|' || continue
        # Skip markdown table separator rows (|---|---|---|)
        echo "$row" | grep -qE '^\|[[:space:]]*-+[[:space:]]*\|[[:space:]]*-+' && continue
        name="$(printf '%s' "$row" | awk -F'|' '{gsub(/^[[:space:]]+|[[:space:]]+$/, "", $3); print $3}')"
        [ -z "$name" ] && continue
        node_id="$(printf '%s' "$name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/_/g')"
        diagram="${diagram}    sys_${node_id}[\"${name}\"]"$'\n'
        ;;
    esac
  done <<< "$systems_section"
  diagram="${diagram}  end"$'\n'
fi

# Features subgraph
if [ -n "$features_section" ]; then
  diagram="${diagram}  subgraph features_group[\"Features\"]"$'\n'
  diagram="${diagram}    direction TB"$'\n'
  while IFS= read -r row; do
    [ -z "$row" ] && continue
    case "$row" in
      \|*)
        echo "$row" | grep -qE '^\|[[:space:]]*-+[[:space:]]*\|' && continue
        c3="$(printf '%s' "$row" | awk -F'|' '{gsub(/^[[:space:]]+|[[:space:]]+$/, "", $3); print $3}')"
        [ -z "$c3" ] && continue
        [ "$c3" = "Feature" ] && continue
        [ "$c3" = "#" ] && continue
        node_id="$(printf '%s' "$c3" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/_/g')"
        diagram="${diagram}    feat_${node_id}[\"${c3}\"]"$'\n'
        ;;
    esac
  done <<< "$features_section"
  diagram="${diagram}  end"$'\n'
fi

# Edges (feature → system)
if [ -n "$features_edges" ]; then
  diagram="${diagram}${features_edges}"
fi

diagram_escaped="$(printf '%s' "$diagram" | awk '{ gsub(/\\/, "\\\\"); gsub(/"/, "\\\""); printf "%s\\n", $0 }')"

# ---------- Emit JSON ----------
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

JSON=$(cat <<EOF
{
  "generatedAt": "${TIMESTAMP}",
  "dataContractVersion": "v1.1",
  "project": {
    "name": "$(json_escape "$project_name")",
    "purpose": "$(json_escape "$project_purpose")",
    "stage": "$(json_escape "$project_stage")"
  },
  "techStack": ${tech_stack_json},
  "foundationalSystems": ${systems_json},
  "features": ${features_json},
  "architecture": "${architecture_escaped}",
  "architectureDiagram": "${diagram_escaped}"
}
EOF
)

if [ -n "$OUT" ]; then
  printf '%s\n' "$JSON" > "$OUT"
  echo "pulse state written to $OUT" >&2
else
  printf '%s\n' "$JSON"
fi
