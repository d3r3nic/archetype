#!/bin/bash
# Archetype Self-Claims Check
#
# The framework must tell the truth about itself. This check fails when a
# shipped document makes a claim about the framework's own parts that the
# tree does not bear out:
#
#   1. Counts. "29 convention docs", "7 backend conventions", "4 phases",
#      "two starter hooks", "01-28.md": each is compared with the tree
#      (conventions/[0-9]*.md, backend/conventions/B*.md, the four phase
#      playbooks, bootstrap/hooks/*.sh). A count of red-flag or
#      silent-failure patterns is never allowed: name the catalogue, not
#      its size, because that number changes with every addition.
#   2. Engine references. Every path into the engine (bootstrap/, scaffolding/,
#      development/, conventions/, backend/, templates/, scripts/, plus the
#      root files), with or without a leading "./" or "archetype/", must
#      exist. Placeholders ({name}, <N>, *, NN) and
#      project-owned files (conventions/overrides/, anything marked within
#      forty characters as "or equivalent", "if present", "if a file exists",
#      "when available", "optionally", "project-owned", "generated") are
#      skipped.
#   3. Convention references. "#N" must resolve to conventions/NN-*.md and
#      "BN" to backend/conventions/BN-*.md. "#N" after "issue", "ticket",
#      "PR", or "pull request" is not a convention reference. Ordinals such
#      as "Phase 3 silent-failure patterns" are names, not counts.
#
# Usage:
#   scripts/validate-claims.sh            # scan every shipped markdown file
#   scripts/validate-claims.sh FILE...    # scan specific files (relative to root)
#
# Exit 0 on pass, 1 on any finding. Portable bash + awk + grep only.
# Limits: a count phrased in words above "twenty" or split across lines is
# not seen; a reference wrapped in a placeholder is not resolved.

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
  exit 1
fi
cd "$FRAMEWORK_DIR" || exit 1

FILES=()
if [ "$#" -gt 0 ]; then
  for f in "$@"; do FILES+=("$f"); done
else
  for f in CLAUDE.md Conventions.md README.md AGENTS.md META-BATTLE-TESTING.md backend/CLAUDE.md backend/Conventions.md \
           conventions/*.md backend/conventions/*.md templates/*.md \
           bootstrap/*.md bootstrap/hooks/README.md scaffolding/*.md development/*.md; do
    [ -f "$f" ] && FILES+=("$f")
  done
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'
ERRORS=0
fail() { printf "${RED}FAIL${NC}: %s\n" "$1"; ERRORS=$((ERRORS + 1)); }
pass() { printf "${GREEN}OK${NC}: %s\n" "$1"; }

echo "Archetype Self-Claims Check"
echo "Root: $FRAMEWORK_DIR"

# ----------------------------------------------------------------------
# Derived facts about the tree.
# ----------------------------------------------------------------------
CONV_COUNT=$(find conventions -maxdepth 1 -name '[0-9]*.md' | wc -l | tr -d ' ')
BACK_COUNT=$(find backend/conventions -maxdepth 1 -name 'B[0-9]*.md' 2>/dev/null | wc -l | tr -d ' ')
HOOK_COUNT=$(find bootstrap/hooks -maxdepth 1 -name '*.sh' 2>/dev/null | wc -l | tr -d ' ')
PHASE_COUNT=0
for p in bootstrap/ONBOARD.md scaffolding/SCAFFOLD.md development/DEVELOP.md development/MAINTAIN.md; do
  [ -f "$p" ] && PHASE_COUNT=$((PHASE_COUNT + 1))
done
MAX_ID=$(find conventions -maxdepth 1 -name '[0-9]*.md' | sed 's|.*/||' | cut -d- -f1 | sort -n | tail -1)
MAX_ID=$((10#$MAX_ID))

word_to_number() {
  case "$(printf '%s' "$1" | tr 'A-Z' 'a-z')" in
    one) echo 1 ;; two) echo 2 ;; three) echo 3 ;; four) echo 4 ;; five) echo 5 ;;
    six) echo 6 ;; seven) echo 7 ;; eight) echo 8 ;; nine) echo 9 ;; ten) echo 10 ;;
    eleven) echo 11 ;; twelve) echo 12 ;; thirteen) echo 13 ;; fourteen) echo 14 ;; fifteen) echo 15 ;;
    sixteen) echo 16 ;; seventeen) echo 17 ;; eighteen) echo 18 ;; nineteen) echo 19 ;; twenty) echo 20 ;;
    *) echo "$1" ;;
  esac
}

# ----------------------------------------------------------------------
# 1. Count claims.
# ----------------------------------------------------------------------
NUMBERS='([0-9]+|[Oo]ne|[Tt]wo|[Tt]hree|[Ff]our|[Ff]ive|[Ss]ix|[Ss]even|[Ee]ight|[Nn]ine|[Tt]en|[Ee]leven|[Tt]welve|[Tt]hirteen|[Ff]ourteen|[Ff]ifteen|[Ss]ixteen|[Ss]eventeen|[Ee]ighteen|[Nn]ineteen|[Tt]wenty)'
NOUNS='(numbered )?(universal )?(convention docs?|conventions|backend conventions|(known )?silent-failure patterns?|red[- ]flag patterns?|red[- ]flags|patterns|phase playbooks?|phases|starter hooks?|working hook scripts?|hook scripts?)'
COUNT_FAILS=0
for file in "${FILES[@]}"; do
  while IFS= read -r hit; do
    [ -z "$hit" ] && continue
    lineno="${hit%%:*}"
    phrase="${hit#*:}"
    # A range like "2-4 conventions" is not a count claim.
    lead="$(sed -n "${lineno}p" "$file" | grep -oE "[0-9]+-${phrase}" | head -1)"
    [ -n "$lead" ] && continue
    num_word="$(printf '%s' "$phrase" | grep -oE "^$NUMBERS" | head -1)"
    num="$(word_to_number "$num_word")"
    noun="$(printf '%s' "$phrase" | sed -E "s/^$NUMBERS[ -]//")"
    context="$(sed -n "${lineno}p" "$file")"
    # An ordinal such as "Phase 3 silent-failure patterns" is a name, not a count.
    printf '%s' "$context" | grep -qE "(Phase|Step|Group|Part|Tier|Option) $num_word[ -]$noun" && continue
    case "$noun" in
      patterns)
        printf '%s' "$context" | grep -qiE 'RED-FLAGS|red[- ]flag|silent-failure' || continue
        fail "$file:$lineno: counts a red-flag catalogue (\"$phrase\"); name the catalogue, never its size"
        COUNT_FAILS=$((COUNT_FAILS + 1)); continue ;;
      *silent-failure*|*red-flag*|*red\ flag*)
        fail "$file:$lineno: counts a red-flag catalogue (\"$phrase\"); name the catalogue, never its size"
        COUNT_FAILS=$((COUNT_FAILS + 1)); continue ;;
      *backend\ conventions*) expected="$BACK_COUNT" ;;
      *convention*)
        if printf '%s' "$context" | grep -qiE "$phrase[^.]{0,40}backend"; then expected="$BACK_COUNT"; else expected="$CONV_COUNT"; fi ;;
      *phase*) expected="$PHASE_COUNT" ;;
      *hook*) expected="$HOOK_COUNT" ;;
      *) continue ;;
    esac
    if [ "$num" != "$expected" ]; then
      fail "$file:$lineno: claims \"$phrase\" but the tree has $expected"
      COUNT_FAILS=$((COUNT_FAILS + 1))
    fi
  done < <(grep -noE "(^|[^0-9-])$NUMBERS[ -]$NOUNS" "$file" | sed -E 's/^([0-9]+):[^0-9A-Za-z]?/\1:/')
  # Id-range claims such as "01-28.md".
  while IFS= read -r hit; do
    [ -z "$hit" ] && continue
    lineno="${hit%%:*}"; range="${hit#*:}"
    hi="${range#*-}"; hi="${hi%.md}"
    if [ "$hi" != "$(printf '%02d' "$MAX_ID")" ]; then
      fail "$file:$lineno: id range \"$range\" but the highest convention is $(printf '%02d' "$MAX_ID")"
      COUNT_FAILS=$((COUNT_FAILS + 1))
    fi
  done < <(grep -noE '[0-9]{2}-[0-9]{2}\.md' "$file")
done
[ "$COUNT_FAILS" -eq 0 ] && pass "every count claim matches the tree ($CONV_COUNT conventions, $BACK_COUNT backend, $PHASE_COUNT phases, $HOOK_COUNT hooks)"

# ----------------------------------------------------------------------
# 2. Engine path references.
# ----------------------------------------------------------------------
REF_FAILS=0
EXEMPT='or equivalent|if a file exists|if present|when available|optionally|project-owned|generated|does not exist|do not exist|never ships|not shipped'
for file in "${FILES[@]}"; do
  while IFS= read -r hit; do
    [ -z "$hit" ] && continue
    lineno="${hit%%:*}"; ref="${hit#*:}"
    ref="${ref#./}"; ref="${ref#archetype/}"
    case "$ref" in
      *'{'*|*'<'*|*'*'*|*'['*|*NN*|*overrides/*|*XX*) continue ;;
    esac
    # Exemption phrases count only near the reference (40 characters before it
    # or after it), so one "(or equivalent)" cannot excuse every path on its line.
    context="$(sed -n "${lineno}p" "$file")"
    window="$(printf '%s' "$context" | awk -v r="$ref" '{ i = index($0, r); if (i == 0) { print $0; exit } s = i - 40; if (s < 1) s = 1; print substr($0, s, (i - s) + length(r) + 40) }')"
    printf '%s' "$window" | grep -qiE "$EXEMPT" && continue
    if [ ! -e "$ref" ]; then
      fail "$file:$lineno: references $ref, which does not exist in the engine"
      REF_FAILS=$((REF_FAILS + 1))
    fi
  done < <(grep -noE '(^|[^A-Za-z0-9_.~-])(\./)?(archetype/)?(bootstrap|scaffolding|development|conventions|backend|templates|scripts)/[A-Za-z0-9_./-]+\.(md|sh|py|json|txt|html|css|js)' "$file" | sed -E 's/^([0-9]+):[^A-Za-z.]*/\1:/')
done
[ "$REF_FAILS" -eq 0 ] && pass "every engine path reference resolves"

# ----------------------------------------------------------------------
# 3. Convention references (#N, BN).
# ----------------------------------------------------------------------
CONV_FAILS=0
for file in "${FILES[@]}"; do
  while IFS= read -r hit; do
    [ -z "$hit" ] && continue
    lineno="${hit%%:*}"; n="${hit#*:}"
    # An issue, ticket, or pull-request number is not a convention reference.
    if sed -n "${lineno}p" "$file" | grep -qiE "(issue|ticket|bug|PR|MR|pull request)[[:space:]#]*#?$n([^0-9]|$)"; then continue; fi
    padded=$(printf '%02d' "$((10#$n))")
    if ! ls conventions/${padded}-*.md > /dev/null 2>&1; then
      fail "$file:$lineno: references convention #$n but conventions/${padded}-*.md does not exist"
      CONV_FAILS=$((CONV_FAILS + 1))
    fi
  done < <(grep -noE "(^|[^A-Za-z0-9\"'#&])#[0-9]{1,2}([^0-9]|$)" "$file" | sed -E 's/^([0-9]+):[^#]*#([0-9]+).*/\1:\2/')
  while IFS= read -r hit; do
    [ -z "$hit" ] && continue
    lineno="${hit%%:*}"; n="${hit#*:}"
    if ! ls backend/conventions/B${n}-*.md > /dev/null 2>&1; then
      fail "$file:$lineno: references backend convention B$n but backend/conventions/B${n}-*.md does not exist"
      CONV_FAILS=$((CONV_FAILS + 1))
    fi
  done < <(grep -noE "(^|[^A-Za-z0-9/])B[1-9]([^0-9A-Za-z-]|$)" "$file" | sed -E 's/^([0-9]+):[^B]*B([0-9]).*/\1:\2/')
done
[ "$CONV_FAILS" -eq 0 ] && pass "every #N and BN reference resolves"

echo "==="
if [ "$ERRORS" -gt 0 ]; then
  printf "${RED}%d self-claim violations${NC}\n" "$ERRORS"
  exit 1
else
  printf "${GREEN}Pass${NC}: self-claims check clean\n"
  exit 0
fi
