#!/bin/bash
# Validates an existing project's adoption (bootstrap/EXISTING-PROJECT.md): the records the
# adoption must leave. It cannot tell whether every rule found its home; the walk through each
# original that the flow describes does that, and the independent review reads the map.
# Run after adoption, before committing.
#
# Checks:
#   1. The earlier entry files were kept as .pre-archetype copies (reported, not required: a
#      project may have had none)
#   2. References.md and feature-tree.md exist
#   3. The map exists: MIGRATION-NOTES.md, or INDEX.md from an adoption under an earlier version
#   4. Copies an earlier version made in docs/migrated/ still match their originals
#   5. References.md records the owner's peer-coding answer (bootstrap Step 2.6), through
#      validate-bootstrap.py peer
#
# Exit 0 on pass, 1 on any error. Warnings do not fail.

# Text is read as bytes, the same on every system: in a UTF-8 locale the macOS awk exits on a
# character that substr cut in two, and the macOS grep, sed and tr fail on bytes that are not UTF-8.
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run from the project root. Engine location follows this script, including
# custom injection directory names. Do not guess a sibling project's root.
PROJECT_ROOT="$(pwd -P)"
ARCHETYPE="$(cd "$SCRIPT_DIR/.." && pwd -P)"
if [ ! -f "$PROJECT_ROOT/CLAUDE.md" ] || [ ! -f "$ARCHETYPE/Conventions.md" ]; then
  echo "Error: run the installed migration validator from the project root."
  exit 1
fi

# New outputs live at project root. Inspect legacy engine-owned outputs too
# when the corresponding local path has not yet been migrated.
project_path() {
  if [ -e "$PROJECT_ROOT/$1" ]; then
    printf '%s\n' "$PROJECT_ROOT/$1"
  else
    printf '%s\n' "$ARCHETYPE/$1"
  fi
}

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
group 1 "The earlier entry files were kept"
# ----------------------------------------------------------------------
if [ -f "$PROJECT_ROOT/CLAUDE.md.pre-archetype" ]; then
  pass "original CLAUDE.md archived as CLAUDE.md.pre-archetype"
else
  warn "no CLAUDE.md.pre-archetype — either no prior CLAUDE.md existed, or inject.sh was not used"
fi
if [ -f "$PROJECT_ROOT/AGENTS.md.pre-archetype" ]; then
  pass "original AGENTS.md archived as AGENTS.md.pre-archetype"
fi

# ----------------------------------------------------------------------
group 2 "References.md and feature-tree.md exist"
# ----------------------------------------------------------------------
REQUIRED=("References.md" "feature-tree.md")
for f in "${REQUIRED[@]}"; do
  if [ ! -f "$PROJECT_ROOT/$f" ] && [ ! -f "$ARCHETYPE/$f" ]; then
    fail "required artifact missing: $f (checked project root and archetype/)"
  fi
done
[ "$ERRORS" -eq 0 ] && pass "required artifacts present"

# ----------------------------------------------------------------------
group 3 "The map of where each original rule lives"
# ----------------------------------------------------------------------
MAP=""
MAP_FILE=""
for candidate in MIGRATION-NOTES.md INDEX.md; do
  if [ -f "$PROJECT_ROOT/$candidate" ]; then MAP="$candidate"; MAP_FILE="$PROJECT_ROOT/$candidate"; break; fi
  if [ -f "$ARCHETYPE/$candidate" ]; then MAP="$(basename "$ARCHETYPE")/$candidate"; MAP_FILE="$ARCHETYPE/$candidate"; break; fi
done
if [ -n "$MAP" ]; then
  if [ "$(wc -l < "$MAP_FILE" | tr -d ' ')" -lt 3 ]; then
    warn "the map $MAP is nearly empty: it should say where each original rule and section lives now"
  else
    pass "the map is $MAP"
  fi
else
  fail "no MIGRATION-NOTES.md: write the map of where each original rule and section lives now (bootstrap/EXISTING-PROJECT.md, Part B)"
fi

# ----------------------------------------------------------------------
group 4 "Copies an earlier version made in docs/migrated/ match their originals"
# ----------------------------------------------------------------------
MIGRATED_DIR="$(project_path docs/migrated)"
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
group 5 "The owner's peer-coding answer (bootstrap Step 2.6)"
# ----------------------------------------------------------------------
if [ -f "$PROJECT_ROOT/References.md" ]; then
  if PEER_RESULT="$(cd "$PROJECT_ROOT" && python3 "$ARCHETYPE/scripts/validate-bootstrap.py" peer 2>&1)"; then
    pass "References.md records the owner's peer-coding answer"
  else
    fail "${PEER_RESULT#FAIL: }"
  fi
fi

# ----------------------------------------------------------------------
echo ""
echo "==="
if [ "$ERRORS" -gt 0 ]; then
  printf "${RED}%d errors${NC}, %d warnings\n" "$ERRORS" "$WARNINGS"
  echo "Fix errors before committing. A rule with no home in the map is lost; walk each original again."
  exit 1
else
  printf "${GREEN}Pass${NC}: 0 errors, %d warnings\n" "$WARNINGS"
  exit 0
fi
