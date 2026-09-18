#!/bin/bash
# Validates a project's References.md § Design Artifact (convention #27): the facts every
# design tool, every session, and the design review read first.
# Run from the project root:  scripts/validate-design.sh
# (archetype/scripts/validate-design.sh when the engine sits in a subfolder.)
#
# Checks:
#   1. Every label of the contract (scripts/design-artifact-labels.txt) appears exactly once
#   2. No line of the section still holds its template placeholder: a value that is empty or
#      opens with "[" fails, except "[to be created]" on Artifact location, which #27 allows
#      until the artifact is first published
#   3. "Brand decided: yes" is refused while "First task" or "Return tasks" is unknown: a
#      direction composes the screen for the first return task, so a look cannot be settled
#      for a product whose main task nobody recorded
#
# A project with no Design Artifact section (a backend, a platform) has nothing to check
# and passes. What this script cannot check: whether a recorded value is true, whether the
# owner was asked, whether a path it names exists. It reads the lines; the review reads
# what they point at.
#
# Exit 0 on pass, 1 on any error.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(pwd)"
LABELS_FILE="$SCRIPT_DIR/design-artifact-labels.txt"

REFS=""
for dir in "$PROJECT_ROOT" "$PROJECT_ROOT/project" "$PROJECT_ROOT/archetype"; do
  [ -f "$dir/References.md" ] && REFS="$dir/References.md"
done

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

ERRORS=0
fail() { printf "${RED}FAIL${NC}: %s\n" "$1"; ERRORS=$((ERRORS + 1)); }
pass() { printf "${GREEN}OK${NC}: %s\n" "$1"; }

echo "Design Artifact Self-Test"

if [ -z "$REFS" ]; then
  echo "Error: References.md not found. Run from the project root."
  exit 1
fi
if [ ! -f "$LABELS_FILE" ]; then
  echo "Error: $LABELS_FILE not found; the label contract ships beside this script."
  exit 1
fi
echo "References: $REFS"

if ! grep -qE '^## Design Artifact' "$REFS"; then
  pass "No Design Artifact section: nothing to check for a project without a screen"
  exit 0
fi

SECTION="$(awk '/^## Design Artifact/{flag=1;next} /^## /{flag=0} flag' "$REFS")"

# The value of a label's first line: everything after "- Label:", trimmed.
da_value() { printf '%s\n' "$SECTION" | awk -v l="- $1:" 'index($0, l) == 1 { v = substr($0, length(l) + 1); sub(/^[ \t]+/, "", v); sub(/[ \t]+$/, "", v); print v; exit }'; }
da_count() { printf '%s\n' "$SECTION" | awk -v l="- $1:" 'index($0, l) == 1 { n++ } END { print n + 0 }'; }

# 1. Every label once.
MISSING=""
REPEATED=""
while IFS= read -r label; do
  case "$label" in ''|'#'*) continue ;; esac
  n="$(da_count "$label")"
  if [ "$n" -eq 0 ]; then MISSING="$MISSING $label,"
  elif [ "$n" -gt 1 ]; then REPEATED="$REPEATED $label,"
  fi
done < "$LABELS_FILE"
[ -n "$MISSING" ] && fail "Design Artifact section lacks label(s):${MISSING%,} (copy each line from the References template and fill it in; conv #27)"
[ -n "$REPEATED" ] && fail "Design Artifact section repeats label(s):${REPEATED%,} (one line per field)"
[ -z "$MISSING" ] && [ -z "$REPEATED" ] && pass "Every label of the contract appears exactly once"

# 2. No placeholder left, on any labelled line of the section.
UNFILLED=""
while IFS= read -r line; do
  case "$line" in '- '*:*) ;; *) continue ;; esac
  label="${line#- }"; label="${label%%:*}"
  value="$(da_value "$label")"
  case "$value" in
    '') UNFILLED="$UNFILLED $label," ;;
    '[to be created]'*) [ "$label" = "Artifact location" ] || UNFILLED="$UNFILLED $label," ;;
    '['*) UNFILLED="$UNFILLED $label," ;;
  esac
done <<EOF
$SECTION
EOF
if [ -n "$UNFILLED" ]; then
  fail "Design Artifact line(s) still hold the template placeholder or no value:${UNFILLED%,} (record the fact, or unknown with what was assumed; a blank is not an answer)"
else
  pass "No Design Artifact line holds a template placeholder"
fi

# 3. A settled look needs the main task on record.
BRAND="$(da_value "Brand decided" | tr '[:upper:]' '[:lower:]')"
case "$BRAND" in
  yes*)
    OWED=""
    for label in "First task" "Return tasks"; do
      v="$(da_value "$label" | tr '[:upper:]' '[:lower:]')"
      case "$v" in ''|'['*|unknown*) OWED="$OWED $label," ;; esac
    done
    if [ -n "$OWED" ]; then
      fail "Brand decided is yes, but unknown:${OWED%,}. A direction composes the screen for the first return task (bootstrap/DESIGN-INTERVIEW.md). Ask the owner, record the answer, then settle the look."
    else
      pass "Brand decided is yes and the tasks the direction was composed for are on record"
    fi
    ;;
esac

echo ""
echo "==="
if [ "$ERRORS" -gt 0 ]; then
  printf "${RED}%d errors${NC}\n" "$ERRORS"
  exit 1
fi
printf "${GREEN}Pass${NC}: 0 errors\n"
exit 0
