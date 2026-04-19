#!/bin/bash
# Archetype Framework Self-Test
# Validates internal consistency of the framework:
#   1. File paths referenced in CLAUDE.md exist
#   2. Convention count in intro text matches actual numbered files
#   3. Every #N reference in Conventions.md resolves to a real file
#   4. Every convention doc has required sections
#   5. No duplicate convention numbers
#   6. Backend convention paths resolve (if backend/ exists)
# Exit 0 on pass, 1 on any error. Warnings do not fail the check.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

FRAMEWORK_DIR=""
for candidate in "$SCRIPT_DIR/.." "$SCRIPT_DIR" "$PWD" "$PWD/archetype" "$PWD/dist"; do
  if [ -f "$candidate/CLAUDE.md" ] && [ -d "$candidate/conventions" ]; then
    FRAMEWORK_DIR="$(cd "$candidate" && pwd)"
    break
  fi
done

if [ -z "$FRAMEWORK_DIR" ]; then
  echo "Error: cannot find framework root (needs CLAUDE.md + conventions/)"
  echo "Run this script from framework root, archetype/scripts/, or project root containing archetype/."
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

cd "$FRAMEWORK_DIR"

echo "Archetype Framework Self-Test"
echo "Root: $FRAMEWORK_DIR"

# ----------------------------------------------------------------------
group 1 "File paths in CLAUDE.md"
# ----------------------------------------------------------------------
BROKEN=0
for path in $(grep -oE 'conventions/[a-zA-Z0-9_-]+\.md' CLAUDE.md | sort -u); do
  if [ ! -f "$path" ]; then
    fail "CLAUDE.md references missing file: $path"
    BROKEN=$((BROKEN + 1))
  fi
done
[ "$BROKEN" -eq 0 ] && pass "all CLAUDE.md paths resolve"

# ----------------------------------------------------------------------
group 2 "Convention count consistency"
# ----------------------------------------------------------------------
CLAIMED=$(grep -oE 'all [0-9]+ convention' Conventions.md | head -1 | grep -oE '[0-9]+')
ACTUAL=$(find conventions -maxdepth 1 -type f -name '[0-9]*.md' | wc -l | tr -d ' ')
if [ -z "$CLAIMED" ]; then
  warn "Conventions.md has no 'all N convention' count claim"
elif [ "$CLAIMED" != "$ACTUAL" ]; then
  fail "Conventions.md claims 'all $CLAIMED' but found $ACTUAL numbered convention files"
else
  pass "convention count matches: $ACTUAL"
fi

# ----------------------------------------------------------------------
group 3 "#N references resolve to files"
# ----------------------------------------------------------------------
BROKEN=0
for ref in $(grep -oE '#[0-9]+' Conventions.md | sort -u); do
  num="${ref#\#}"
  padded=$(printf '%02d' "$num")
  if ! ls conventions/${padded}-*.md > /dev/null 2>&1; then
    fail "$ref referenced in Conventions.md but no conventions/${padded}-*.md file"
    BROKEN=$((BROKEN + 1))
  fi
done
[ "$BROKEN" -eq 0 ] && pass "all #N references resolve"

# ----------------------------------------------------------------------
group 4 "Required sections in convention docs"
# ----------------------------------------------------------------------
MISSING=0
for file in conventions/[0-9]*.md; do
  [ -f "$file" ] || continue
  for section in "## Principle" "## Rules" "## Violations" "## Wrong vs Right" "## Research Notes"; do
    if ! grep -qF "$section" "$file"; then
      warn "$file missing section: $section"
      MISSING=$((MISSING + 1))
    fi
  done
done
[ "$MISSING" -eq 0 ] && pass "all convention docs have required sections"

# ----------------------------------------------------------------------
group 5 "Unique convention numbers"
# ----------------------------------------------------------------------
DUPS=$(find conventions -maxdepth 1 -name '[0-9]*.md' -exec basename {} \; | grep -oE '^[0-9]+' | sort | uniq -d)
if [ -n "$DUPS" ]; then
  fail "duplicate convention numbers: $DUPS"
else
  pass "all convention numbers unique"
fi

# ----------------------------------------------------------------------
if [ -d backend ]; then
  group 6 "Backend convention paths"
  BROKEN=0
  for path in $(grep -oE 'backend/conventions/B[0-9]+-[a-z-]+\.md' backend/Conventions.md 2>/dev/null | sort -u); do
    if [ ! -f "$path" ]; then
      fail "backend/Conventions.md references missing file: $path"
      BROKEN=$((BROKEN + 1))
    fi
  done
  [ "$BROKEN" -eq 0 ] && pass "all backend convention paths resolve"
fi

# ----------------------------------------------------------------------
group 7 "Templates ↔ pulse-inspect parse contract"
# ----------------------------------------------------------------------
# Templates teach the AI what to produce; the inspector parses the output.
# If the columns drift, pulse silently produces garbage. These checks keep
# the two in lockstep.

FT="templates/feature-tree.md"
if [ -f "$FT" ]; then
  # Systems table: must have `| # | Name |` header so inspector's numeric
  # column-2 check matches.
  if grep -qE '^\|[[:space:]]*#[[:space:]]*\|[[:space:]]*Name[[:space:]]*\|' "$FT"; then
    pass "feature-tree.md Systems header starts with '# | Name |'"
  else
    fail "feature-tree.md Systems table must start '| # | Name | ...' (pulse-inspect needs numeric col 2)"
  fi
  # Features table: must have `| # | Feature | Location | Routes |`.
  if grep -qE '^\|[[:space:]]*#[[:space:]]*\|[[:space:]]*Feature[[:space:]]*\|[[:space:]]*Location[[:space:]]*\|[[:space:]]*Routes[[:space:]]*\|' "$FT"; then
    pass "feature-tree.md Features header is '# | Feature | Location | Routes | ...'"
  else
    fail "feature-tree.md Features table must be '| # | Feature | Location | Routes | Systems Used | ...' (pulse-inspect reads \$3=name, \$4=loc, \$5=routes, \$6=systems)"
  fi
else
  warn "feature-tree.md template missing at $FT"
fi

for REF in templates/references-frontend.md templates/references-backend.md templates/references-mobile.md; do
  [ -f "$REF" ] || continue
  # Project section must use `- Name:` bullets.
  if awk '/^## Project/{flag=1;next} /^## /{flag=0} flag' "$REF" | grep -qE '^- Name:'; then
    pass "$(basename "$REF") Project section uses '- Name:' bullet"
  else
    fail "$(basename "$REF") Project section must use '- Name: ...' bullets (pulse-inspect requires leading dash)"
  fi
  # Tech Stack section must use `- Key:` bullets.
  if awk '/^## Tech Stack/{flag=1;next} /^## /{flag=0} flag' "$REF" | grep -qE '^- [A-Za-z]'; then
    pass "$(basename "$REF") Tech Stack uses '- Key: Value' bullets"
  else
    fail "$(basename "$REF") Tech Stack must use '- Key: Value' bullets"
  fi
done

# ----------------------------------------------------------------------
group 8 "No project artifacts inside the framework folder"
# ----------------------------------------------------------------------
# The framework is read-only from a project's perspective. Per-project
# artifacts (VERSION-LOG, docs/, References.md, etc.) must live at the
# project root, not inside archetype/. This check catches accidental
# writes from old inject.sh / update.sh versions.

LEAKS=0
for leak_file in VERSION-LOG.md FRAMEWORK-SOURCE.md References.md feature-tree.md; do
  if [ -f "$leak_file" ]; then
    fail "framework folder contains project artifact: $leak_file (move to project root)"
    LEAKS=$((LEAKS + 1))
  fi
done
if [ -d docs ]; then
  fail "framework folder contains docs/ (move project docs to project root)"
  LEAKS=$((LEAKS + 1))
fi
[ "$LEAKS" -eq 0 ] && pass "framework folder is clean (no project artifacts)"

# ----------------------------------------------------------------------
echo ""
echo "==="
if [ "$ERRORS" -gt 0 ]; then
  printf "${RED}%d errors${NC}, %d warnings\n" "$ERRORS" "$WARNINGS"
  exit 1
else
  printf "${GREEN}Pass${NC}: 0 errors, %d warnings\n" "$WARNINGS"
  exit 0
fi
