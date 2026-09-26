#!/bin/bash
# Validates Phase 4 (Maintain): the project's map against the project. Reads no fixed layout:
# every location comes from feature-tree.md. Run from the project root during a look at the
# project (development/MAINTAIN.md).
#
# Checks:
#   1. TECHNICAL-DEBT.md exists, or References.md says why there is none (warning)
#   2. Every feature and system row points at a location that exists
#   3. When the feature rows share one parent folder, every folder in it has a row (warning)
#   4. Every TECHNICAL-DEBT.md entry has a Status (warning)
#   5. Every feature record's backticked type names still appear in the feature's location
#      (a coarse drift warning)

# Text is read as bytes, the same on every system: in a UTF-8 locale the macOS awk exits on a
# character that substr cut in two, and the macOS grep, sed and tr fail on bytes that are not UTF-8.
export LC_ALL=C

PROJECT_ROOT="$(pwd)"
TREE="$PROJECT_ROOT/feature-tree.md"
REFS="$PROJECT_ROOT/References.md"
TD="$PROJECT_ROOT/TECHNICAL-DEBT.md"

if [ ! -f "$TREE" ]; then
  echo "Error: feature-tree.md not found at project root. Run from a scaffolded project."
  exit 1
fi

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

echo "Maintain Self-Test"
echo "Project: $PROJECT_ROOT"

# A Location value names a place only as a plain local path; anything else is left unread.
plain_path() {
  case "$1" in
    /*|'~'*|*://*|'') return 1 ;;
    *[[:space:]]*|*'['*|*']'*|*'('*|*')'*|*'<'*|*'>'*|*'"'*|*"'"*|*'#'*|*\\*|*'*'*) return 1 ;;
  esac
  return 0
}

# Rows of both tables: table|num|name|location|status. A row is a line that starts with a pipe and
# whose first cell, bold markers removed, is a number (the rule scripts/pulse-inspect.sh applies).
ROWS="$(tr -d '\r' < "$TREE" | awk -F'|' '
  function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
  { gsub(/\*\*/, "") }
  /^## / { table = ""; if ($0 ~ /^## Features/) table = "feature"; else if (tolower($0) ~ /^## (foundational systems|systems)/) table = "system"; next }
  table == "" || !/^\|/ { next }
  /^\|[ \t]*[0-9]+[ \t]*\|/ {
    # Features: #, Feature, Location, Routes, Systems Used, Status. Systems: #, Name, Convention, Location, Status.
    if (table == "feature") printf "%s|%s|%s|%s|%s\n", table, trim($2), trim($3), trim($4), trim($7)
    else printf "%s|%s|%s|%s|%s\n", table, trim($2), trim($3), trim($5), trim($6)
  }')"

# ----------------------------------------------------------------------
group 1 "TECHNICAL-DEBT.md exists or its absence is explained"
# ----------------------------------------------------------------------
if [ -f "$TD" ]; then
  pass "TECHNICAL-DEBT.md exists"
elif [ -f "$REFS" ] && grep -qiE '(technical.?debt|tech.?debt).*(n/a|none yet|deferred|not yet)' "$REFS"; then
  pass "TECHNICAL-DEBT.md absent, and References.md says why"
else
  warn "TECHNICAL-DEBT.md not found, and References.md does not say why; create it from templates/technical-debt.md when the first shortcut or deferral is taken"
fi

# ----------------------------------------------------------------------
group 2 "Every row points at a location that exists"
# ----------------------------------------------------------------------
MISSING=0
FEATURE_PARENTS=""
while IFS='|' read -r table num name location status; do
  [ -n "$table" ] || continue
  loc="$(printf '%s' "$location" | tr -d '`')"; loc="${loc#./}"; loc="${loc%/}"
  case "$loc" in ''|'['*|none|n/a|-) continue ;; esac
  status_lc="$(printf '%s' "$status" | tr '[:upper:]' '[:lower:]')"
  case "$status_lc" in *'not started'*|*deferred*|*blocked*|*'not applicable'*) continue ;; esac
  if ! plain_path "$loc"; then continue; fi
  if [ ! -e "$PROJECT_ROOT/$loc" ]; then
    fail "$table row $num ($name) names $loc, which does not exist; correct the row or restore what it names"
    MISSING=$((MISSING + 1))
  elif [ "$table" = feature ]; then
    FEATURE_PARENTS="$FEATURE_PARENTS
$(dirname "$loc")"
  fi
done <<EOF
$ROWS
EOF
[ "$MISSING" -eq 0 ] && pass "every row with a location points at one that exists"

# ----------------------------------------------------------------------
group 3 "Folders beside the features have rows"
# ----------------------------------------------------------------------
PARENTS="$(printf '%s\n' "$FEATURE_PARENTS" | grep -v '^$' | sort -u)"
if [ -n "$PARENTS" ] && [ "$(printf '%s\n' "$PARENTS" | wc -l | tr -d ' ')" -eq 1 ] && [ "$PARENTS" != "." ]; then
  UNLISTED=0
  for dir in "$PROJECT_ROOT/$PARENTS"/*/; do
    [ -d "$dir" ] || continue
    rel="$PARENTS/$(basename "$dir")"
    if ! printf '%s\n' "$ROWS" | awk -F'|' -v r="$rel" '{ l = $4; gsub(/`/, "", l); sub(/^\.\//, "", l); sub(/\/$/, "", l); if (l == r) found = 1 } END { exit found ? 0 : 1 }'; then
      warn "$rel sits beside the features in $PARENTS/ but has no row in feature-tree.md; add its row, or note why it is not a feature"
      UNLISTED=$((UNLISTED + 1))
    fi
  done
  [ "$UNLISTED" -eq 0 ] && pass "every folder in $PARENTS/ has a row"
else
  pass "the feature rows share no single parent folder; nothing to compare"
fi

# ----------------------------------------------------------------------
group 4 "TECHNICAL-DEBT.md entries have a Status"
# ----------------------------------------------------------------------
if [ -f "$TD" ]; then
  NO_STATUS="$(tr -d '\r' < "$TD" | awk '
    /^ ? ? ?(```|~~~)/ { fence = !fence; next }
    fence { next }
    /^#+[ \t]/ { t = $0; sub(/^#+[ \t]+/, "", t); gsub(/[*_`]/, "", t)
      if (toupper(substr(t, 1, 3)) == "TD-") { if (id != "" && !st) print id; id = t; sub(/[^A-Za-z0-9-].*$/, "", id); st = 0; next }
      if ($0 ~ /^#[ \t]/) { if (id != "" && !st) print id; id = "" }
      next }
    id != "" && tolower($0) ~ /^[ \t]*([-*+][ \t]+)?[*_`]*status[*_`]*[ \t]*:/ { st = 1 }
    END { if (id != "" && !st) print id }')"
  if [ -n "$NO_STATUS" ]; then
    warn "TECHNICAL-DEBT.md entries without a Status: $(printf '%s' "$NO_STATUS" | tr '\n' ' ')(record open, in-progress, fixed or won't-fix so each can be revisited)"
  else
    pass "every TECHNICAL-DEBT.md entry has a Status"
  fi
fi

# ----------------------------------------------------------------------
group 5 "Feature records still name types their features define"
# ----------------------------------------------------------------------
# For each feature row with a record and a location: type-like names in backticks in the record
# (ending Schema, Input, Output, Request, Response or Entry) should still appear in the location.
# Coarse: it catches a wholesale removal, not a subtle change of shape.
DRIFTED=0
while IFS='|' read -r table num name location status; do
  [ "$table" = feature ] || continue
  loc="$(printf '%s' "$location" | tr -d '`')"; loc="${loc#./}"; loc="${loc%/}"
  plain_path "$loc" && [ -e "$PROJECT_ROOT/$loc" ] || continue
  cell="$(printf '%s' "$name" | tr -d ' ')"
  doc="$PROJECT_ROOT/docs/features/$cell.md"
  [ -f "$doc" ] || continue
  TYPES="$(grep -oE '`[A-Z][a-zA-Z]*(Schema|Input|Output|Request|Response|Entry)`' "$doc" | tr -d '`' | sort -u)"
  for t in $TYPES; do
    if ! grep -rqE "(^|[^A-Za-z0-9_])$t([^A-Za-z0-9_]|\$)" "$PROJECT_ROOT/$loc" 2>/dev/null; then
      warn "docs/features/$cell.md names type '$t', which no longer appears in $loc: the record may have drifted"
      DRIFTED=$((DRIFTED + 1))
    fi
  done
done <<EOF
$ROWS
EOF
[ "$DRIFTED" -eq 0 ] && pass "feature records' type names are present in their features"

# ----------------------------------------------------------------------
echo ""
echo "==="
if [ "$ERRORS" -gt 0 ]; then
  printf "${RED}%d errors${NC}, %d warnings\n" "$ERRORS" "$WARNINGS"
  echo "Fix the map before relying on it. See development/MAINTAIN-RED-FLAGS.md."
  exit 1
else
  printf "${GREEN}Pass${NC}: 0 errors, %d warnings\n" "$WARNINGS"
  [ "$WARNINGS" -gt 0 ] && echo "Warnings are advisory: review each for real drift."
  exit 0
fi
