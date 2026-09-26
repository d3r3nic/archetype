#!/bin/bash
# Validates the one live References.md Design Artifact section (convention #27) for what a
# script can check without judging the design:
#   - a project known to have a screen (--required known-screen) has exactly one live section;
#   - no line of the section still holds its template placeholder;
#   - Brand decided reads as a known state, and a settled brand (yes) waits until First task and
#     Return tasks are known, because a direction composes the screen for the first return task.
# The section's other lines are the project's brief; which of them it keeps is its own choice.
# Run from the project root: scripts/validate-design.sh [--required known-screen]
# Use --required known-screen when the caller already knows the project has a screen.

# Text is read as bytes, the same on every system: in a UTF-8 locale the macOS awk exits on a
# character that substr cut in two, and the macOS grep, sed and tr fail on bytes that are not UTF-8.
export LC_ALL=C

REQUIRED=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --required)
      [ "$#" -ge 2 ] || { echo "--required needs a value (accepted: known-screen)"; exit 2; }
      REQUIRED="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $1 (accepted: --required known-screen)"; exit 2 ;;
  esac
done
[ -z "$REQUIRED" ] || [ "$REQUIRED" = "known-screen" ] || {
  echo "unknown required mode: $REQUIRED (accepted: known-screen)"; exit 2;
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(pwd)"
# The brief's own lines, as the UI References templates carry them: a line of these still holding
# its template placeholder, or no value, is unfilled. Other lines in the section are the project's.
LABELS_FILE="$SCRIPT_DIR/design-artifact-labels.txt"

REFS=""
for dir in "$PROJECT_ROOT" "$PROJECT_ROOT/project" "$PROJECT_ROOT/archetype"; do
  if [ -f "$dir/References.md" ]; then REFS="$dir/References.md"; break; fi
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
echo "References: $REFS"

TMP_BASE="${TMPDIR:-/tmp}/archetype-design-$$"
LIVE="$TMP_BASE.live"
SECTION_FILE="$TMP_BASE.section"
FACTS="$TMP_BASE.facts"
trap 'rm -f "$LIVE" "$SECTION_FILE" "$FACTS"' EXIT HUP INT TERM

# Remove both backtick and tilde fenced examples. A longer opening fence needs an equally
# long closing fence of the same character. Only live prose reaches the section parser.
tr -d '\r' < "$REFS" | awk '
  function marker_length(s, c, n) {
    c = substr(s, 1, 1); n = 0
    while (substr(s, n + 1, 1) == c) n++
    return n
  }
  {
    s = $0; sub(/^[ \t]*/, "", s)
    if (!fenced && (substr(s, 1, 3) == "```" || substr(s, 1, 3) == "~~~")) {
      fence_char = substr(s, 1, 1); fence_length = marker_length(s); fenced = 1; next
    }
    if (fenced) {
      if (substr(s, 1, 1) == fence_char && marker_length(s) >= fence_length) {
        tail = substr(s, marker_length(s) + 1)
        if (tail ~ /^[ \t]*$/) fenced = 0
      }
      next
    }
    print
  }
' > "$LIVE"

SECTION_COUNT="$(grep -cE '^## Design Artifact[[:space:]]*$' "$LIVE" 2>/dev/null || true)"
if [ "$SECTION_COUNT" -eq 0 ]; then
  if [ "$REQUIRED" = "known-screen" ]; then
    fail "References.md needs exactly one live '## Design Artifact' section for a known-screen project; found 0"
    exit 1
  fi
  pass "No live Design Artifact section: nothing to check for a project without a screen"
  exit 0
fi
if [ "$SECTION_COUNT" -ne 1 ]; then
  fail "References.md needs exactly one live '## Design Artifact' section; found $SECTION_COUNT"
  exit 1
fi

awk '
  /^## Design Artifact[[:space:]]*$/ { in_section = 1; next }
  in_section && /^##[[:space:]]+/ { exit }
  in_section { print }
' "$LIVE" > "$SECTION_FILE"

# Parse one-line list facts. Harmless inline decoration around a label is normalized so
# the same field cannot evade missing, duplicate, or unfinished-value checks.
awk '
  function trim(s) { sub(/^[ \t]+/, "", s); sub(/[ \t]+$/, "", s); return s }
  index($0, "- ") == 1 {
    fact = substr($0, 3); colon = index(fact, ":")
    if (!colon) next
    label = trim(substr(fact, 1, colon - 1))
    value = trim(substr(fact, colon + 1))
    gsub(/[`*_]/, "", label); label = trim(label)
    sub(/^\*\*/, "", value); sub(/^__/, "", value)
    print label "\t" value
  }
' "$SECTION_FILE" > "$FACTS"

fact_count() { awk -F '\t' -v label="$1" '$1 == label { n++ } END { print n + 0 }' "$FACTS"; }
fact_value() { awk -F '\t' -v label="$1" '$1 == label { sub(/^[^\t]*\t/, ""); print; exit }' "$FACTS"; }

# The lines this script reads appear once: two values for one of them would be two facts.
for label in "Brand decided" "First task" "Return tasks"; do
  n="$(fact_count "$label")"
  [ "$n" -gt 1 ] && fail "Design Artifact section repeats \"$label\"; keep one line"
done

normalize_value() {
  printf '%s' "$1" | sed -E \
    -e 's/[`*_]//g' \
    -e 's/^[[:space:]"'"'"']+//' \
    -e 's/[[:space:]"'"'"']+$//' \
    -e 's/^[[:space:]]+//' \
    -e 's/[[:space:]]+$//' | tr '[:upper:]' '[:lower:]'
}

is_placeholder_text() {
  stripped="$(printf '%s' "$1" | sed -E 's/\[[^][]+\]\([^()]+\)//g')"
  case "$stripped" in *'['*']'*) return 0 ;; esac
  return 1
}

is_incomplete() {
  label="$1"; raw="$2"
  [ -n "$(normalize_value "$raw")" ] || return 0
  if is_placeholder_text "$raw"; then
    case "$raw" in '[to be created]'*) [ "$label" = "Artifact location" ] && return 1 ;; esac
    return 0
  fi
  return 1
}

BRIEF_LABELS="Platform parity"
[ -f "$LABELS_FILE" ] && BRIEF_LABELS="$(tr -d '\r' < "$LABELS_FILE" | grep -v '^#' | grep -v '^[[:space:]]*$')
Platform parity"
is_brief_label() {
  printf '%s\n' "$BRIEF_LABELS" | grep -qxF -- "$1"
}
UNFILLED=""
while IFS="$(printf '\t')" read -r label value; do
  [ -n "$label" ] || continue
  is_brief_label "$label" || continue
  if is_incomplete "$label" "$value"; then UNFILLED="$UNFILLED $label,"; fi
done < "$FACTS"
if [ -n "$UNFILLED" ]; then
  fail "Design Artifact line(s) still hold the template placeholder or no value:${UNFILLED%,} (record the fact, unknown with what was assumed, or none with why)"
else
  pass "No Design Artifact line holds a template placeholder"
fi

# Brand decided uses a leading canonical state. Later prose cannot turn a leading no into
# yes, and synonyms cannot silently settle the brand. Open and template states stay legal.
BRAND_VALUE="$(normalize_value "$(fact_value "Brand decided")")"
BRAND_STATE=""
if [ "$(fact_count "Brand decided")" -eq 0 ]; then
  fail "Design Artifact section has no Brand decided line: record yes, not yet, no, unknown, or deferred to downstream projects"
fi
case "$BRAND_VALUE" in
  yes|yes[[:space:]]*|yes,*|yes.*|yes:*|yes-*|yes\;*) BRAND_STATE="yes" ;;
  'not yet'|'not yet '*|'not yet,'*|'not yet.'*|'not yet:'*|'not yet-'*|'not yet;'*|no|no[[:space:]]*|no,*|no.*|no:*|no-*|no\;*|unknown|unknown[[:space:]]*|unknown,*|unknown.*|unknown:*|unknown-*|unknown\;*) BRAND_STATE="open" ;;
  'deferred to downstream projects') BRAND_STATE="template-deferred" ;;
  '') ;;
  *) fail "Brand decided must start with a canonical state: yes, not yet, no, unknown, or deferred to downstream projects" ;;
esac

if [ "$BRAND_STATE" = "yes" ]; then
  OWED=""
  for label in "First task" "Return tasks"; do
    value="$(normalize_value "$(fact_value "$label")")"
    case "$value" in ''|unknown|unknown[[:space:]]*|unknown,*|unknown.*|unknown:*|unknown-*|unknown\;*) OWED="$OWED $label," ;; esac
  done
  if [ -n "$OWED" ]; then
    fail "Brand decided is yes, but unknown:${OWED%,}. A direction composes the screen for the first return task (bootstrap/DESIGN-INTERVIEW.md). Ask the owner, record the answer, then settle the look."
  else
    pass "Brand decided is yes and the tasks the direction was composed for are on record"
  fi
fi

echo ""
echo "==="
if [ "$ERRORS" -gt 0 ]; then
  printf "${RED}%d errors${NC}\n" "$ERRORS"
  exit 1
fi
printf "${GREEN}Pass${NC}: 0 errors\n"
exit 0
