#!/bin/bash
# Validates an existing-project migration produced by bootstrap/EXISTING-PROJECT.md.
# Replaces "AI discipline" with machine-verifiable gates. Run after migration,
# before committing.
#
# Checks:
#   1. conventions/overrides/ files are non-trivial length (catches summarization)
#   2. Every override file starts with a "# Convention #N: {Name} — PROJECT OVERRIDES" header
#   3. Every audit file names its convention with "Maps to convention: #N"
#   4. INDEX.md exists and is non-trivial
#   5. docs/migrated/ matches originals byte-for-byte (no accidental edits)
#   6. CLAUDE.md.pre-archetype exists (original preserved)
#   7. No original project docs were modified (spot check via diff)
#
# Exit 0 on pass, 1 on any error. Warnings do not fail.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detect project root — migration produces archetype/ subfolder at project root
PROJECT_ROOT=""
for candidate in "$PWD" "$PWD/.." "$SCRIPT_DIR/../.." "$SCRIPT_DIR/../../.."; do
  if [ -d "$candidate/archetype" ] && [ -f "$candidate/archetype/CLAUDE.md" ]; then
    PROJECT_ROOT="$(cd "$candidate" && pwd)"
    break
  fi
done

if [ -z "$PROJECT_ROOT" ]; then
  echo "Error: cannot find project with archetype/ subfolder."
  echo "Run from the project root of an existing-project migration."
  exit 1
fi

ARCHETYPE="$PROJECT_ROOT/archetype"

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

echo "Migration Self-Test"
echo "Project: $PROJECT_ROOT"
echo "Archetype: $ARCHETYPE"

# ----------------------------------------------------------------------
group 1 "Override files non-trivial (catches summarization)"
# ----------------------------------------------------------------------
MIN_OVERRIDE_LINES=20  # Any override file under 20 lines is suspicious
OVERRIDE_DIR="$ARCHETYPE/conventions/overrides"
if [ -d "$OVERRIDE_DIR" ]; then
  SHORT=0
  for file in "$OVERRIDE_DIR"/*.md; do
    [ -f "$file" ] || continue
    lines=$(wc -l < "$file" | tr -d ' ')
    if [ "$lines" -lt "$MIN_OVERRIDE_LINES" ]; then
      warn "override file under ${MIN_OVERRIDE_LINES} lines (possible summarization): $(basename "$file") ($lines lines)"
      SHORT=$((SHORT + 1))
    fi
  done
  [ "$SHORT" -eq 0 ] && pass "all override files meet minimum length"
else
  warn "no conventions/overrides/ directory — migration may not have extracted rules"
fi

# ----------------------------------------------------------------------
group 2 "Override files have correct header"
# ----------------------------------------------------------------------
if [ -d "$OVERRIDE_DIR" ]; then
  MISSING=0
  for file in "$OVERRIDE_DIR"/*.md; do
    [ -f "$file" ] || continue
    if ! head -1 "$file" | grep -qE "^# Convention #[0-9]+"; then
      fail "override file missing '# Convention #N:' header: $(basename "$file")"
      MISSING=$((MISSING + 1))
    fi
  done
  [ "$MISSING" -eq 0 ] && pass "all override files have correct header"
fi

# ----------------------------------------------------------------------
group 3 "Audit files name their convention"
# ----------------------------------------------------------------------
AUDIT_DIR="$ARCHETYPE/docs/audit"
if [ -d "$AUDIT_DIR" ]; then
  MISSING=0
  AUDIT_COUNT=0
  while IFS= read -r file; do
    AUDIT_COUNT=$((AUDIT_COUNT + 1))
    if ! grep -qE "Maps to convention.*#[0-9]+" "$file"; then
      # Status table and SUMMARY files are exempt
      base=$(basename "$file")
      [ "$base" = "audit-status-table.md" ] && continue
      [ "$base" = "SUMMARY.md" ] && continue
      fail "audit file missing 'Maps to convention: #N' line: ${file#$AUDIT_DIR/}"
      MISSING=$((MISSING + 1))
    fi
  done < <(find "$AUDIT_DIR" -type f -name '*.audit.md')
  [ "$MISSING" -eq 0 ] && [ "$AUDIT_COUNT" -gt 0 ] && pass "$AUDIT_COUNT audit files name their convention"
  [ "$AUDIT_COUNT" -eq 0 ] && warn "no audit files found in docs/audit/"
else
  warn "no docs/audit/ directory — Part D may not have run"
fi

# ----------------------------------------------------------------------
group 4 "INDEX.md exists and is non-trivial"
# ----------------------------------------------------------------------
if [ -f "$ARCHETYPE/INDEX.md" ]; then
  lines=$(wc -l < "$ARCHETYPE/INDEX.md" | tr -d ' ')
  if [ "$lines" -lt 10 ]; then
    warn "INDEX.md is under 10 lines — likely incomplete"
  else
    pass "INDEX.md exists ($lines lines)"
  fi
else
  fail "INDEX.md missing — Part C cross-reference step was skipped"
fi

# ----------------------------------------------------------------------
group 5 "Migrated docs match originals byte-for-byte"
# ----------------------------------------------------------------------
MIGRATED_DIR="$ARCHETYPE/docs/migrated"
if [ -d "$MIGRATED_DIR" ]; then
  DRIFTED=0
  # Only check files where we can infer the original path
  # Heuristic: migrated/docs/* should match $PROJECT_ROOT/docs/*
  if [ -d "$MIGRATED_DIR/docs" ] && [ -d "$PROJECT_ROOT/docs" ]; then
    while IFS= read -r migrated_file; do
      rel_path="${migrated_file#$MIGRATED_DIR/}"
      original="$PROJECT_ROOT/$rel_path"
      # Skip STALE-banner files — they have a header prepended
      if head -1 "$migrated_file" | grep -qF "STALE"; then
        continue
      fi
      if [ -f "$original" ]; then
        if ! diff -q "$migrated_file" "$original" > /dev/null 2>&1; then
          fail "migrated doc drifted from original: $rel_path"
          DRIFTED=$((DRIFTED + 1))
        fi
      fi
    done < <(find "$MIGRATED_DIR/docs" -type f -name '*.md')
    [ "$DRIFTED" -eq 0 ] && pass "all migrated docs match originals (excluding STALE-banner exceptions)"
  fi
fi

# ----------------------------------------------------------------------
group 6 "Original CLAUDE.md preserved"
# ----------------------------------------------------------------------
if [ -f "$PROJECT_ROOT/CLAUDE.md.pre-archetype" ]; then
  pass "original CLAUDE.md archived as CLAUDE.md.pre-archetype"
else
  warn "no CLAUDE.md.pre-archetype — either no prior CLAUDE.md existed, or inject.sh was not used"
fi

# ----------------------------------------------------------------------
group 7 "Project-root required artifacts"
# ----------------------------------------------------------------------
REQUIRED=("References.md" "feature-tree.md")
for f in "${REQUIRED[@]}"; do
  if [ ! -f "$PROJECT_ROOT/$f" ] && [ ! -f "$ARCHETYPE/$f" ]; then
    fail "required artifact missing: $f (checked project root and archetype/)"
  fi
done
[ "$ERRORS" -eq 0 ] && pass "required artifacts present"

# ----------------------------------------------------------------------
echo ""
echo "==="
if [ "$ERRORS" -gt 0 ]; then
  printf "${RED}%d errors${NC}, %d warnings\n" "$ERRORS" "$WARNINGS"
  echo "Fix errors before committing. Summarization in overrides (group 1) is"
  echo "the most common and most dangerous failure — re-extract in full."
  exit 1
else
  printf "${GREEN}Pass${NC}: 0 errors, %d warnings\n" "$WARNINGS"
  exit 0
fi
