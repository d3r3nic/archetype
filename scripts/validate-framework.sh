#!/bin/bash
# Archetype Framework Self-Test
# Validates internal consistency of the framework:
#   1. File paths referenced in CLAUDE.md exist
#   2. Convention count in intro text matches actual numbered files
#   3. Every #N reference in Conventions.md resolves to a real file
#   4. Every convention doc has required sections
#   5. No duplicate convention numbers
#   6. Backend convention paths resolve (if backend/ exists)
#   7. Templates and pulse-inspect agree on parse contract; the Design Artifact
#      label contract in the UI templates agrees with convention #27
#   8. No project artifacts inside the framework folder
#   9. Task protocol routing targets exist
#  10. Timeless conventions: no expirable content outside Research Notes
#      (delegates to scripts/validate-timeless.sh)
#  11. Self-claims: counts, engine paths, and convention references in the
#      shipped docs match the tree (delegates to scripts/validate-claims.sh)
#  12. Profile vocabulary: the stages, triggers, and floor items that
#      scripts/validate-profile.sh evaluates are the ones the profile and debt
#      templates and convention #30 name
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
  pass "Conventions.md states no convention count (the index names them; group 11 checks the counts it knows about)"
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
group 7 "Templates ↔ pulse-inspect parse contract; Design Artifact label contract (#27)"
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

# UI-centric templates must carry the labelled Design Artifact section (convention #27):
# every design tool, every session, and the maintain audit read the same fields. The
# label list below is the contract; the mobile template adds Platform parity. The section
# is closed: a bullet whose label is not in the contract fails, so a note belongs outside
# the section. Presence only: a label with an empty value passes; the placeholders'
# content is reviewed, not parsed. Labels are matched literally (no regex, no glob); a
# label may carry any character except a backslash, which awk -v would expand, or a colon, which the reverse extraction reads as the label's end. Convention
# #27 must name every label, mobile included,
# inside its "Design tools" section, so the vocabulary is checked in both directions.
DA_LABELS="Primary tool
Direction of truth
Artifact location
Published view
Tokens source
Component catalog
Brand book
Design working files
Sync
Brand decided
Every UI state designed
Update responsibility
Complementary tools
Primary context
Committed contexts
Density
Vocabulary"
DA_MOBILE_EXTRA="Platform parity"
DA_CONV="conventions/27-design-foundation.md"
da_count() { printf '%s\n' "$1" | awk -v l="- $2:" 'index($0, l) == 1 { n++ } END { print n + 0 }'; }
for REF in templates/references-frontend.md templates/references-mobile.md; do
  [ -f "$REF" ] || continue
  if ! grep -qE '^## Design Artifact' "$REF"; then
    fail "$(basename "$REF") must include a '## Design Artifact' section (conv #27 pipeline). Bootstrap relies on this placeholder."
    continue
  fi
  DA_SECTION="$(awk '/^## Design Artifact/{flag=1;next} /^## /{flag=0} flag' "$REF")"
  DA_EXTRA=""
  case "$REF" in *references-mobile.md) DA_EXTRA="$DA_MOBILE_EXTRA";; esac
  DA_MISSING=""
  DA_REPEATED=""
  DA_UNKNOWN=""
  while IFS= read -r label; do
    [ -n "$label" ] || continue
    n="$(da_count "$DA_SECTION" "$label")"
    if [ "$n" -eq 0 ]; then DA_MISSING="$DA_MISSING $label,"
    elif [ "$n" -gt 1 ]; then DA_REPEATED="$DA_REPEATED $label,"
    fi
  done <<EOF
$DA_LABELS
$DA_EXTRA
EOF
  while IFS= read -r found; do
    [ -n "$found" ] || continue
    case "
$DA_LABELS
$DA_EXTRA
" in *"
$found
"*) ;; *) DA_UNKNOWN="$DA_UNKNOWN $found,";; esac
  done <<EOF
$(printf '%s\n' "$DA_SECTION" | sed -n 's/^- \([^:]*\):.*/\1/p')
EOF
  if [ -z "$DA_MISSING" ] && [ -z "$DA_REPEATED" ] && [ -z "$DA_UNKNOWN" ]; then
    pass "$(basename "$REF") Design Artifact section carries every label of the contract exactly once (conv #27)"
  fi
  [ -n "$DA_MISSING" ] && fail "$(basename "$REF") Design Artifact section lacks label(s):${DA_MISSING%,} (conv #27 contract; a design tool reads these lines first)"
  [ -n "$DA_REPEATED" ] && fail "$(basename "$REF") Design Artifact section repeats label(s):${DA_REPEATED%,} (one line per field)"
  [ -n "$DA_UNKNOWN" ] && fail "$(basename "$REF") Design Artifact section has label(s) the contract does not know:${DA_UNKNOWN%,} (add to DA_LABELS in validate-framework.sh and to conv #27, or move the line out of the section)"
done
if [ -f "$DA_CONV" ]; then
  DA_CONV_SECTION="$(awk '/^## Design tools/{flag=1;next} /^## /{flag=0} flag' "$DA_CONV")"
  if [ -z "$DA_CONV_SECTION" ]; then
    fail "$DA_CONV has no '## Design tools' section to name the Design Artifact labels in"
  else
    DA_CONV_MISSING=""
    while IFS= read -r label; do
      [ -n "$label" ] || continue
      printf '%s\n' "$DA_CONV_SECTION" | grep -qF "\`${label}\`" || DA_CONV_MISSING="$DA_CONV_MISSING $label,"
    done <<EOF
$DA_LABELS
$DA_MOBILE_EXTRA
EOF
    if [ -z "$DA_CONV_MISSING" ]; then
      pass "$DA_CONV names every Design Artifact label the templates carry, in its Design tools section"
    else
      fail "$DA_CONV does not name label(s):${DA_CONV_MISSING%,} in its Design tools section (the convention and the templates must agree)"
    fi
  fi
else
  fail "$DA_CONV missing; the Design Artifact contract has no convention to agree with"
fi

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

# These routes are part of the shared task contract, not proof of enforcement.
group 9 "Task protocol routing"
for path in AGENTS.md bootstrap/REPOSITORIES.md development/TASKS.md development/FRESHNESS.md templates/task-context.md; do
  if [ ! -f "$path" ]; then
    fail "task protocol target missing: $path"
  fi
done
if ! grep -qF '<!-- archetype-managed-entrypoint -->' AGENTS.md 2>/dev/null; then
  fail "AGENTS.md lacks the managed entry-point marker"
fi

# ----------------------------------------------------------------------
group 10 "Timeless conventions (no expirable content outside Research Notes)"
# ----------------------------------------------------------------------
# The framework encodes character; specifics live in project artifacts.
# scripts/validate-timeless.sh fails on tool or vendor names outside a
# Research Notes section, factory step references, statistics attached to
# AI claims, tool-bound numeric limits, changelog language, and Research
# Notes sections without the dated notice.
if [ -f "$SCRIPT_DIR/validate-timeless.sh" ]; then
  if TIMELESS_OUT="$(bash "$SCRIPT_DIR/validate-timeless.sh" 2>&1)"; then
    pass "timeless check clean"
  else
    printf '%s\n' "$TIMELESS_OUT" | grep -E 'FAIL' | sed 's/\x1b\[[0-9;]*m//g' | while IFS= read -r line; do
      printf '  %s\n' "$line"
    done
    fail "timeless check reported violations (see lines above)"
  fi
else
  fail "scripts/validate-timeless.sh missing"
fi

# ----------------------------------------------------------------------
group 11 "Self-claims (counts, engine paths, convention references match the tree)"
# ----------------------------------------------------------------------
if [ -f "$SCRIPT_DIR/validate-claims.sh" ]; then
  if CLAIMS_OUT="$(bash "$SCRIPT_DIR/validate-claims.sh" 2>&1)"; then
    pass "self-claims check clean"
  else
    printf '%s\n' "$CLAIMS_OUT" | grep -E 'FAIL' | sed 's/\x1b\[[0-9;]*m//g' | while IFS= read -r line; do
      printf '  %s\n' "$line"
    done
    fail "self-claims check reported violations (see lines above)"
  fi
else
  fail "scripts/validate-claims.sh missing"
fi

# ----------------------------------------------------------------------
group 12 "Profile vocabulary (validator, templates, and convention #30 agree)"
# ----------------------------------------------------------------------
PV="$SCRIPT_DIR/validate-profile.sh"
if [ ! -f "$PV" ]; then
  fail "scripts/validate-profile.sh missing"
else
  VOCAB_FAILS=0
  vocab_words() { sed -n "s/^$1=\"\(.*\)\"\$/\1/p" "$PV" | head -1; }
  # Split a list on commas and slashes into one word per line, trimmed.
  norm() { tr ',/' '  ' | tr -s ' \n' '\n' | sed -e 's/^ *//' -e 's/ *$//' -e '/^$/d'; }
  in_set() { local x; for x in $2; do [ "$x" = "$1" ] && return 0; done; return 1; }
  compare_sets() {
    # $1 label, $2 source file, $3 validator words, $4 words the source names
    local label="$1" src="$2" exp="$3" got="$4" w
    [ -z "$exp" ] && { fail "validate-profile.sh defines no $label list"; VOCAB_FAILS=$((VOCAB_FAILS + 1)); return; }
    [ -z "$got" ] && { fail "$src names no $label where the contract lists them"; VOCAB_FAILS=$((VOCAB_FAILS + 1)); return; }
    for w in $exp; do
      in_set "$w" "$got" || { fail "$src does not name $label \"$w\", which validate-profile.sh evaluates"; VOCAB_FAILS=$((VOCAB_FAILS + 1)); }
    done
    for w in $got; do
      in_set "$w" "$exp" || { fail "$src names $label \"$w\", which validate-profile.sh does not evaluate"; VOCAB_FAILS=$((VOCAB_FAILS + 1)); }
    done
  }
  T_V="$(vocab_words TRIGGERS)"; S_V="$(vocab_words STAGES)"; F_V="$(vocab_words FLOOR)"
  T_PROFILE="$(sed -n 's/^- Review: .*expected: *//p' templates/profile.md | sed 's/\].*//' | norm | tr '\n' ' ')"
  S_PROFILE="$(sed -n 's/^- Operating stage: *\[//p' templates/profile.md | sed 's/\].*//' | norm | tr '\n' ' ')"
  T_DEBT="$(sed -n 's/^- \*\*Due-before:\*\* .*PROFILE\.md (//p' templates/technical-debt.md | head -1 | sed 's/).*//' | norm | tr '\n' ' ')"
  F_DEBT="$(sed -n 's/^- \*\*Control:\*\* .*floor: *//p' templates/technical-debt.md | head -1 | sed 's/).*//' | norm | tr '\n' ' ')"
  T_CONV="$(sed -n 's/^- Triggers are named and evaluated from the recorded facts: *//p' conventions/30-operating-profile.md | sed 's/\. .*//' | tr -d '\140' | norm | tr '\n' ' ')"
  compare_sets "trigger" templates/profile.md "$T_V" "$T_PROFILE"
  compare_sets "stage" templates/profile.md "$S_V" "$S_PROFILE"
  compare_sets "trigger" templates/technical-debt.md "$T_V" "$T_DEBT"
  compare_sets "floor item" templates/technical-debt.md "$F_V" "$F_DEBT"
  compare_sets "trigger" conventions/30-operating-profile.md "$T_V" "$T_CONV"
  # The validator's key set and the template's facts block must match exactly.
  K_V="$(sed -n 's/^KEYS=(\(.*\))$/\1/p' "$PV" | sed -e 's/" "/\n/g' -e 's/^"//' -e 's/"$//' | sort)"
  K_T="$(awk '/^## / { exit } /^- [^:]+:/ { s = $0; sub(/^- /, "", s); sub(/:.*/, "", s); print s }' templates/profile.md | sort)"
  if [ -z "$K_V" ] || [ -z "$K_T" ]; then
    fail "could not read the profile key set from validate-profile.sh or templates/profile.md"
    VOCAB_FAILS=$((VOCAB_FAILS + 1))
  else
    while IFS= read -r k; do
      [ -z "$k" ] && continue
      fail "templates/profile.md lacks key \"$k\", which validate-profile.sh requires"; VOCAB_FAILS=$((VOCAB_FAILS + 1))
    done < <(comm -23 <(printf '%s\n' "$K_V") <(printf '%s\n' "$K_T"))
    while IFS= read -r k; do
      [ -z "$k" ] && continue
      fail "templates/profile.md has key \"$k\", which validate-profile.sh does not know"; VOCAB_FAILS=$((VOCAB_FAILS + 1))
    done < <(comm -13 <(printf '%s\n' "$K_V") <(printf '%s\n' "$K_T"))
  fi
  [ "$VOCAB_FAILS" -eq 0 ] && pass "profile vocabulary agrees in both directions across validator, templates, and convention #30 (stages, triggers, floor items, keys)"
fi

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
