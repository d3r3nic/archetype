#!/bin/bash
# Validates Phase 4 (Maintain) artifacts + discipline. Machine-verifiable gates.
# Run from project root during or after a maintenance cycle.
#
# Checks:
#   1. TECHNICAL-DEBT.md exists OR documented justification in References.md
#   2. feature-tree.md has an Audit Log section if N+ features exist
#   3. Feature directory basename == feature-tree Feature column == docs/features filename
#   4. No TECHNICAL-DEBT.md entries in `open` status older than threshold without escalation
#   5. Every docs/features/*.md still references existing source types (coarse drift check)

PROJECT_ROOT="$(pwd)"

# Tolerant of layouts
SRC_DIR=""
for candidate in "$PROJECT_ROOT/src" "$PROJECT_ROOT/app" "$PROJECT_ROOT/lib"; do
  [ -d "$candidate" ] && SRC_DIR="$candidate" && break
done

TREE="$PROJECT_ROOT/feature-tree.md"
REFS="$PROJECT_ROOT/References.md"
TD="$PROJECT_ROOT/TECHNICAL-DEBT.md"
DOCS_FEATURES="$PROJECT_ROOT/docs/features"

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

# ----------------------------------------------------------------------
group 1 "TECHNICAL-DEBT.md exists or absence is documented"
# ----------------------------------------------------------------------
if [ -f "$TD" ]; then
  lines=$(wc -l < "$TD" | tr -d ' ')
  if [ "$lines" -lt 5 ]; then
    warn "TECHNICAL-DEBT.md exists but is nearly empty — ensure entries are being logged"
  else
    pass "TECHNICAL-DEBT.md exists ($lines lines)"
  fi
else
  # Allow documented absence — e.g., very early-stage project, or documented in References.md
  if [ -f "$REFS" ] && grep -qiE '(technical.?debt|tech.?debt).*(n/a|none yet|deferred)' "$REFS"; then
    pass "TECHNICAL-DEBT.md absent but documented in References.md"
  else
    warn "TECHNICAL-DEBT.md not found and no documented justification in References.md"
  fi
fi

# ----------------------------------------------------------------------
group 2 "feature-tree.md has Audit Log if project has N+ features"
# ----------------------------------------------------------------------
FEATURES_DIR="$SRC_DIR/features"
if [ -d "$FEATURES_DIR" ]; then
  # Count feature directories (exclude smoke/health)
  FEATURE_COUNT=0
  for dir in "$FEATURES_DIR"/*/; do
    [ -d "$dir" ] || continue
    base=$(basename "$dir")
    case "$base" in health|_health|ping|smoke) continue ;; esac
    FEATURE_COUNT=$((FEATURE_COUNT + 1))
  done

  if [ "$FEATURE_COUNT" -ge 2 ]; then
    if grep -qE '^## Audit Log' "$TREE"; then
      pass "feature-tree.md has Audit Log section ($FEATURE_COUNT features)"
    else
      fail "feature-tree.md has $FEATURE_COUNT features but no ## Audit Log section. Phase 4 audits must leave a record."
    fi
  else
    pass "feature-tree.md audit log not required yet ($FEATURE_COUNT features — threshold is 2)"
  fi
fi

# ----------------------------------------------------------------------
group 3 "Feature directory == feature-tree Feature column == docs/features filename"
# ----------------------------------------------------------------------
# This catches the "src/features/sessions/ hosts record-session" drift.
MISMATCH=0
if [ -d "$FEATURES_DIR" ] && [ -d "$DOCS_FEATURES" ]; then
  for dir in "$FEATURES_DIR"/*/; do
    [ -d "$dir" ] || continue
    base=$(basename "$dir")
    case "$base" in health|_health|ping|smoke) continue ;; esac

    # Check if feature-tree.md has a row where Feature column matches base
    if ! grep -qE "^\|[[:space:]]*[0-9-]+[[:space:]]*\|[[:space:]]*${base}[[:space:]]*\|" "$TREE"; then
      fail "feature directory '$base' has no matching row in feature-tree.md Feature column"
      MISMATCH=$((MISMATCH + 1))
      continue
    fi

    # Check if docs/features/{base}.md exists
    if [ ! -f "$DOCS_FEATURES/${base}.md" ]; then
      fail "feature directory '$base' has no matching docs/features/${base}.md"
      MISMATCH=$((MISMATCH + 1))
    fi
  done
  [ "$MISMATCH" -eq 0 ] && pass "feature directory / feature-tree / docs/features all align"
fi

# ----------------------------------------------------------------------
group 4 "TECHNICAL-DEBT.md entries with open status not over-aged"
# ----------------------------------------------------------------------
if [ -f "$TD" ]; then
  # Extract entries with Status: open and their Logged dates
  # Simple approach: count entries marked 'Status:*open' that were logged > 180 days ago
  STALE=0
  THRESHOLD_DAYS=180
  NOW_EPOCH=$(date +%s)
  while IFS= read -r logged_line; do
    # Extract YYYY-MM-DD
    date_str=$(echo "$logged_line" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1)
    [ -z "$date_str" ] && continue
    # Convert to epoch (works on macOS and Linux)
    if date -j -f "%Y-%m-%d" "$date_str" "+%s" >/dev/null 2>&1; then
      logged_epoch=$(date -j -f "%Y-%m-%d" "$date_str" "+%s")
    elif date -d "$date_str" "+%s" >/dev/null 2>&1; then
      logged_epoch=$(date -d "$date_str" "+%s")
    else
      continue
    fi
    age_days=$(( (NOW_EPOCH - logged_epoch) / 86400 ))
    if [ "$age_days" -gt "$THRESHOLD_DAYS" ]; then
      STALE=$((STALE + 1))
    fi
  done < <(grep -B 5 -iE '^- \*\*Status:\*\* *open' "$TD" 2>/dev/null | grep -iE '^- \*\*Logged:' || true)

  if [ "$STALE" -gt 0 ]; then
    warn "$STALE TECHNICAL-DEBT entries in open status are older than $THRESHOLD_DAYS days — review for escalation or force-fix"
  else
    pass "no stale open tech-debt entries"
  fi
fi

# ----------------------------------------------------------------------
group 5 "docs/features/*.md coarse type-reference freshness"
# ----------------------------------------------------------------------
# For each feature doc, extract referenced type names (heuristic: CamelCase words
# that look like type/schema names) and verify they still exist in the feature source.
# Coarse — catches wholesale removals, misses subtle shape changes.
if [ -d "$DOCS_FEATURES" ] && [ -d "$FEATURES_DIR" ]; then
  DRIFTED=0
  for doc in "$DOCS_FEATURES"/*.md; do
    [ -f "$doc" ] || continue
    name=$(basename "$doc" .md)
    # Find matching feature dir — either exact match or with - substituted
    feature_src=""
    if [ -d "$FEATURES_DIR/$name" ]; then
      feature_src="$FEATURES_DIR/$name"
    else
      # Try with first-word match
      first_word=$(echo "$name" | cut -d- -f1)
      [ -d "$FEATURES_DIR/$first_word" ] && feature_src="$FEATURES_DIR/$first_word"
      # Try plural/singular
      [ -d "$FEATURES_DIR/${first_word}s" ] && feature_src="$FEATURES_DIR/${first_word}s"
    fi
    [ -z "$feature_src" ] && continue

    # Extract type names in backticks from the doc (heuristic)
    TYPES=$(grep -oE '`[A-Z][a-zA-Z]*(Schema|Input|Output|Request|Response|Entry)`' "$doc" | tr -d '`' | sort -u)
    for t in $TYPES; do
      if ! grep -rqE "(interface|type|const|class|function)[[:space:]]+$t\b|^export[[:space:]]+(const|type|interface|class|function)[[:space:]]+$t\b" "$feature_src" 2>/dev/null; then
        warn "$doc references type '$t' but it's not found in $feature_src — possible doc drift"
        DRIFTED=$((DRIFTED + 1))
      fi
    done
  done
  [ "$DRIFTED" -eq 0 ] && pass "docs/features type references are present in source"
fi

# ----------------------------------------------------------------------
echo ""
echo "==="
if [ "$ERRORS" -gt 0 ]; then
  printf "${RED}%d errors${NC}, %d warnings\n" "$ERRORS" "$WARNINGS"
  echo "Fix errors before the next release cycle. See development/MAINTAIN-RED-FLAGS.md for context."
  exit 1
else
  printf "${GREEN}Pass${NC}: 0 errors, %d warnings\n" "$WARNINGS"
  [ "$WARNINGS" -gt 0 ] && echo "Warnings are advisory — review each for real risk."
  exit 0
fi
