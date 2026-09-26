#!/bin/bash
# Validates Phase 3 (Develop) against the project's own recorded choices. It reads no fixed
# folder layout and names no library: its reach is what the project recorded.
# Run from the unit's root, the folder that holds References.md, before merging feature work.
#
# Checks:
#   1. References.md § Boundaries exists and holds: no file outside a shared system's recorded
#      paths uses what only that system may use (scripts/check-boundaries.sh --required)
#   2. Every feature row of feature-tree.md has its record: the path its Docs column names, or
#      docs/features/<name>.md (a feature is a row of the Features table whose first cell is a
#      number; a row with an empty or placeholder name fails; the smoke-test feature is exempt)
#   3. Every feature record's Tests line names tests that exist, or says none with the reason; a
#      record with no Tests line passes when the feature's location holds a test file

# Text is read as bytes, the same on every system: in a UTF-8 locale the macOS awk exits on a
# character that substr cut in two, and the macOS grep, sed and tr fail on bytes that are not UTF-8.
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
PROJECT_ROOT="$(pwd -P)"
TREE="$PROJECT_ROOT/feature-tree.md"
[ ! -f "$TREE" ] && TREE="$PROJECT_ROOT/archetype/feature-tree.md"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

fail()  { printf "${RED}FAIL${NC}: %s\n" "$1"; ERRORS=$((ERRORS + 1)); }
warn()  { printf "${YELLOW}WARN${NC}: %s\n" "$1"; WARNINGS=$((WARNINGS + 1)); }
pass()  { printf "${GREEN}OK${NC}: %s\n" "$1"; }
group() { printf "\n[%s] %s\n" "$1" "$2"; }

RECORDS="${TMPDIR:-/tmp}/archetype-develop-$$.records"
: > "$RECORDS"
trap 'rm -f "$RECORDS"' EXIT HUP INT TERM

echo "Develop Self-Test"
echo "Project: $PROJECT_ROOT"

# ----------------------------------------------------------------------
group 1 "Each shared system's boundary holds (References.md § Boundaries)"
# ----------------------------------------------------------------------
if ! BOUNDARY_OUT="$(cd "$PROJECT_ROOT" && bash "$SCRIPT_DIR/check-boundaries.sh" --required 2>&1)"; then
  printf '%s\n' "$BOUNDARY_OUT" | sed 's/^/  /'
  fail "References.md § Boundaries: see the lines above"
else
  printf '%s\n' "$BOUNDARY_OUT" | sed 's/^/  /'
  pass "every recorded boundary holds"
fi

# A Docs or Tests value names a path only as a plain local path; anything else gets a
# diagnostic, not a guess.
plain_path() {
  case "$1" in
    /*|'~'*|*://*|'') return 1 ;;
    *[[:space:]]*|*'`'*|*'['*|*']'*|*'('*|*')'*|*'<'*|*'>'*|*'"'*|*"'"*|*'#'*|*\\*) return 1 ;;
  esac
  return 0
}

# ----------------------------------------------------------------------
group 2 "Every feature has its record"
# ----------------------------------------------------------------------
# Feature rows of feature-tree.md's Features section: a row is a line that starts with a pipe
# and whose first cell, bold markers removed, is a number (the rule scripts/pulse-inspect.sh
# applies). The Docs column is found by its header; the leading columns have fixed positions:
# #, Feature, Location. Printed as num|name|location|status|docs.
ROWS=""
if [ -f "$TREE" ]; then
  ROWS="$(tr -d '\r' < "$TREE" | awk -F'|' '
    function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
    { gsub(/\*\*/, "") }
    /^## / { inf = ($0 ~ /^## Features/); docs = 0; status = 0; prev = ""; next }
    !inf || !/^\|/ { next }
    /^\|[ \t:|-]*$/ && /-/ {
      docs = 0; status = 0
      n = split(prev, head, "|")
      for (i = 2; i <= n; i++) {
        c = tolower(trim(head[i])); gsub(/[`*]/, "", c)
        if (c == "docs") docs = i
        if (c == "status") status = i
      }
      next
    }
    /^\|[ \t]*[0-9]+[ \t]*\|/ {
      printf "%s|%s|%s|%s|%s\n", trim($2), trim($3), trim($4), (status ? trim($status) : ""), (docs ? trim($docs) : "")
      next
    }
    { prev = $0 }')"
fi

SKIPPED_SMOKE=""
if [ ! -f "$TREE" ]; then
  warn "no feature-tree.md at the project root: cannot check feature records"
else
  MISSING=0
  FEATURES=0
  while IFS='|' read -r num cell location status docs; do
    [ -n "$num" ] || continue
    name="$(printf '%s' "$cell" | tr -d ' ')"
    if [ -z "$name" ]; then
      fail "feature row $num has no name (its Feature cell is empty); name the feature or delete the row"
      MISSING=$((MISSING + 1)); continue
    fi
    if printf '%s\n' "$cell" | grep -qE '^\[[^]]*\]$'; then
      fail "feature row $num is the placeholder row left from the template (name $cell); replace it with a real feature or delete it"
      MISSING=$((MISSING + 1)); continue
    fi
    status_lc="$(printf '%s' "$status" | tr -d '`*' | tr '[:upper:]' '[:lower:]')"
    case "$status_lc" in *smoke-test*) SKIPPED_SMOKE="$SKIPPED_SMOKE $name"; continue ;; esac
    # The conventional smoke-test names, for a tree that predates the smoke-test status.
    case "$name" in health|_health|ping|smoke) SKIPPED_SMOKE="$SKIPPED_SMOKE $name"; continue ;; esac
    FEATURES=$((FEATURES + 1))
    record=""
    docs_plain="$(printf '%s' "$docs" | tr -d '`')"
    if [ -n "$docs_plain" ] && [ "$docs_plain" != "-" ]; then
      case "$docs_plain" in
        *.md) if plain_path "$docs_plain"; then record="${docs_plain#./}"; fi ;;
      esac
      if [ -z "$record" ]; then
        fail "feature '$name': its Docs cell '$docs' is not a plain local .md path; write the record's path from the project root, like docs/features/$name.md"
        MISSING=$((MISSING + 1)); continue
      fi
    else
      record="docs/features/$name.md"
    fi
    if [ ! -f "$PROJECT_ROOT/$record" ]; then
      fail "feature '$name' has no record at $record"
      MISSING=$((MISSING + 1)); continue
    fi
    printf '%s|%s|%s\n' "$name" "$record" "$location" >> "$RECORDS"
  done <<EOF
$ROWS
EOF
  if [ "$MISSING" -eq 0 ]; then
    if [ "$FEATURES" -eq 0 ]; then pass "no feature rows yet"; else pass "every feature in feature-tree.md has its record"; fi
  fi
fi

# ----------------------------------------------------------------------
group 3 "Every feature's tests are where its record says"
# ----------------------------------------------------------------------
if [ -s "$RECORDS" ]; then
  BAD=0
  while IFS='|' read -r name record location; do
    [ -n "$name" ] || continue
    tests_line="$(tr -d '\r' < "$PROJECT_ROOT/$record" | grep -E '^[[:space:]]*([-*][[:space:]]+)?(\*\*|__)?Tests(\*\*|__)?[[:space:]]*:' | head -1)"
    if [ -n "$tests_line" ]; then
      value="${tests_line#*:}"
      value="$(printf '%s' "$value" | sed -e 's/^[[:space:]]*//' -e 's/^\*\*[[:space:]]*//' -e 's/^__[[:space:]]*//' -e 's/[[:space:]]*$//')"
      lower="$(printf '%s' "$value" | tr '[:upper:]' '[:lower:]')"
      case "$value" in
        '['*)
          fail "feature '$name': the Tests line of $record still holds the template's placeholder; name where its tests are, or none with the reason"
          BAD=$((BAD + 1)); continue ;;
      esac
      case "$lower" in
        none*)
          reason="$(printf '%s' "$value" | sed -E 's/^[Nn][Oo][Nn][Ee][[:space:]:,;.-]*//')"
          if [ -z "$reason" ]; then
            fail "feature '$name': its record says Tests: none without a reason; say why"
            BAD=$((BAD + 1))
          else
            warn "feature '$name' records no tests: $reason"
          fi
          continue ;;
      esac
      paths="$(printf '%s\n' "$value" | awk '{ s = $0; while ((i = index(s, "`")) > 0) { s = substr(s, i + 1); j = index(s, "`"); if (!j) break; print substr(s, 1, j - 1); s = substr(s, j + 1) } }')"
      if [ -z "$paths" ]; then
        fail "feature '$name': the Tests line of $record names no path in backticks; write each path as \`path\`, or none with the reason"
        BAD=$((BAD + 1)); continue
      fi
      while IFS= read -r tp; do
        [ -n "$tp" ] || continue
        tp="${tp#./}"
        case "$tp" in
          /*|'~'*|*..*) fail "feature '$name': the test path \`$tp\` in $record must be inside the project, from its root"; BAD=$((BAD + 1)); continue ;;
        esac
        found=0
        case "$tp" in
          *'*'*|*'?'*|*'['*) for g in "$PROJECT_ROOT"/$tp; do [ -e "$g" ] && { found=1; break; }; done ;;
          *) [ -e "$PROJECT_ROOT/$tp" ] && found=1 ;;
        esac
        if [ "$found" -eq 0 ]; then
          fail "feature '$name': its record names tests at \`$tp\`, which does not exist"
          BAD=$((BAD + 1))
        fi
      done <<EOF
$paths
EOF
    else
      # No Tests line: look for a test file in the feature's location, as earlier releases did.
      loc="$(printf '%s' "$location" | tr -d '`')"; loc="${loc#./}"; loc="${loc%/}"
      found=0
      if plain_path "$loc" && [ -d "$PROJECT_ROOT/$loc" ]; then
        if find "$PROJECT_ROOT/$loc" -maxdepth 3 -type f \( -name '*.test.*' -o -name '*_test.*' -o -name 'test_*' -o -name '*.spec.*' \) 2>/dev/null | grep -q .; then
          found=1
        fi
      fi
      if [ "$found" -eq 0 ]; then
        fail "feature '$name': its record ($record) has no Tests line, and no test file was found in its location ($location); add Tests: naming where its tests are, or none with the reason"
        BAD=$((BAD + 1))
      fi
    fi
  done < "$RECORDS"
  [ "$BAD" -eq 0 ] && pass "every feature's tests are where its record says"
elif [ -f "$TREE" ]; then
  pass "no feature records to read"
fi
[ -n "$SKIPPED_SMOKE" ] && echo "  (the smoke-test feature is exempt:$SKIPPED_SMOKE)"

# ----------------------------------------------------------------------
echo ""
echo "==="
if [ "$ERRORS" -gt 0 ]; then
  printf "${RED}%d errors${NC}, %d warnings\n" "$ERRORS" "$WARNINGS"
  echo "Fix a real violation; correct a record that is wrong and say why. See development/RED-FLAGS.md."
  exit 1
else
  printf "${GREEN}Pass${NC}: 0 errors, %d warnings\n" "$WARNINGS"
  exit 0
fi
