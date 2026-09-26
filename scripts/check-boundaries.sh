#!/bin/bash
# Reads References.md § Boundaries and checks that each shared system's recorded owner is
# the only place that uses what the project said only it may use (#0, #25).
# Run from the unit's root, the folder that holds References.md. Used by
# scripts/validate-develop.sh and scripts/validate-scaffold.sh; it can also run on its own.
#
#   scripts/check-boundaries.sh              the section is optional: absent is a warning
#   scripts/check-boundaries.sh --required   the section must exist
#   scripts/check-boundaries.sh --rules      print each readable rule as label<TAB>pattern and stop
#
# A line of the section is one of:
#   - <concern>: `<pattern>` only in `<path>`, `<path>`
#   - none: <reason>
# The pattern is an extended regular expression (grep -E) for the project's own tool. A path is
# a folder ending in "/", a file, or a shell glob (such as `*.test.*`), from the unit's root.
# The check lists the unit's files through git (tracked and untracked, not ignored), leaves out
# Markdown files and the installed framework folder, and fails when a file outside a rule's
# paths contains its pattern. A line it cannot read fails; a line still holding the template's
# bracketed placeholder fails. Nothing it cannot read counts as a pass.
# Exit 0 when every rule holds, 1 on any failure, 2 on a usage error.

# Text is read as bytes, the same on every system: in a UTF-8 locale the macOS awk exits on a
# character that substr cut in two, and the macOS grep, sed and tr fail on bytes that are not UTF-8.
export LC_ALL=C

MODE=check
REQUIRED=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --required) REQUIRED=1; shift ;;
    --rules) MODE=rules; shift ;;
    -h|--help) sed -n '2,19p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $1 (accepted: --required, --rules)"; exit 2 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT="$(pwd -P)"
REFS=""
for dir in "$ROOT" "$ROOT/project" "$ROOT/archetype"; do
  if [ -f "$dir/References.md" ]; then REFS="$dir/References.md"; break; fi
done

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
ERRORS=0
fail() { printf "${RED}FAIL${NC}: %s\n" "$1"; ERRORS=$((ERRORS + 1)); }
warn() { printf "${YELLOW}WARN${NC}: %s\n" "$1"; }
pass() { printf "${GREEN}OK${NC}: %s\n" "$1"; }

if [ -z "$REFS" ]; then
  [ "$MODE" = rules ] && exit 0
  echo "Error: References.md not found. Run from the unit's root."
  exit 2
fi

TMP_BASE="${TMPDIR:-/tmp}/archetype-boundaries-$$"
SECTION="$TMP_BASE.section"
RULES="$TMP_BASE.rules"
LIST="$TMP_BASE.list"
HITS="$TMP_BASE.hits"
trap 'rm -f "$SECTION" "$RULES" "$LIST" "$LIST.out" "$HITS"' EXIT HUP INT TERM

# The live list lines of the one "## Boundaries" section: fenced examples are skipped, and a
# section that appears twice is reported, since two records of one boundary can disagree.
tr -d '\r' < "$REFS" | awk '
  function marker_length(s, c, n) { c = substr(s, 1, 1); n = 0; while (substr(s, n + 1, 1) == c) n++; return n }
  {
    s = $0; sub(/^[ \t]*/, "", s)
    if (!fenced && (substr(s, 1, 3) == "```" || substr(s, 1, 3) == "~~~")) { fc = substr(s, 1, 1); fl = marker_length(s); fenced = 1; next }
    if (fenced) { if (substr(s, 1, 1) == fc && marker_length(s) >= fl && substr(s, marker_length(s) + 1) ~ /^[ \t]*$/) fenced = 0; next }
    if ($0 ~ /^## /) { inside = ($0 ~ /^## Boundaries[ \t]*$/); if (inside) sections++; next }
    if (inside && $0 ~ /^[ \t]*[-*][ \t]+/) { line = $0; sub(/^[ \t]*[-*][ \t]+/, "", line); sub(/[ \t]+$/, "", line); print line }
  }
  END { if (sections > 1) print "\001TWICE"; if (sections == 0) print "\001ABSENT" }
' > "$SECTION"

if grep -q "$(printf '\001')ABSENT" "$SECTION"; then
  [ "$MODE" = rules ] && exit 0
  if [ "$REQUIRED" -eq 1 ]; then
    fail "References.md has no ## Boundaries section: record each shared system's one owner and what only it may use, one line per concern (the section in templates/references-*.md), or - none: <reason> when the project has nothing to guard"
    exit 1
  fi
  warn "References.md has no ## Boundaries section yet: nothing to check (the scaffold records a line as it builds each shared system)"
  exit 0
fi
if grep -q "$(printf '\001')TWICE" "$SECTION"; then
  fail "References.md has more than one ## Boundaries section; keep one"
fi

# Parse each line into label<TAB>pattern<TAB>paths (paths separated by TAB), or report it.
: > "$RULES"
NONE_REASON=""
LINES=0
while IFS= read -r line; do
  case "$line" in "$(printf '\001')"*) continue ;; esac
  LINES=$((LINES + 1))
  case "$line" in
    '['*) fail "References.md § Boundaries still holds the template's placeholder line: $line (replace it with this project's line, or remove it)"; continue ;;
  esac
  lower="$(printf '%s' "$line" | tr '[:upper:]' '[:lower:]')"
  case "$lower" in
    none:*|none' '*:*)
      reason="${line#*:}"; reason="$(printf '%s' "$reason" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
      if [ -z "$reason" ]; then fail "References.md § Boundaries records none without a reason: write - none: <reason>"; else NONE_REASON="$reason"; fi
      continue ;;
  esac
  parsed="$(printf '%s\n' "$line" | awk '
    {
      colon = index($0, ": `"); if (!colon) { print "BAD"; exit }
      label = substr($0, 1, colon - 1); rest = substr($0, colon + 2)
      if (label ~ /`/ || label ~ /^[ \t]*$/) { print "BAD"; exit }
      rest = substr(rest, 2); end = index(rest, "`"); if (end < 2) { print "BAD"; exit }
      pattern = substr(rest, 1, end - 1); rest = substr(rest, end + 1)
      if (rest !~ /^[ \t]+only in[ \t]+`/) { print "BAD"; exit }
      sub(/^[ \t]+only in[ \t]+/, "", rest)
      paths = ""; n = 0
      while (rest != "") {
        if (substr(rest, 1, 1) != "`") { print "BAD"; exit }
        rest = substr(rest, 2); end = index(rest, "`"); if (end < 2) { print "BAD"; exit }
        paths = paths "\t" substr(rest, 1, end - 1); n++; rest = substr(rest, end + 1)
        sub(/^[ \t]*(,[ \t]*)?(and[ \t]+)?/, "", rest)
        if (rest ~ /^\.?[ \t]*$/) rest = ""
      }
      if (n == 0) { print "BAD"; exit }
      printf "%s\t%s%s\n", label, pattern, paths
    }')"
  if [ "$parsed" = BAD ] || [ -z "$parsed" ]; then
    fail "References.md § Boundaries line not readable: $line (write - <concern>: \`<pattern>\` only in \`<path>\`, \`<path>\`)"
    continue
  fi
  printf '%s\n' "$parsed" >> "$RULES"
done < "$SECTION"

if [ "$MODE" = rules ]; then
  cut -f1-2 "$RULES"
  exit 0
fi

if [ "$LINES" -eq 0 ]; then
  if [ "$REQUIRED" -eq 1 ]; then
    fail "References.md § Boundaries is empty: record each shared system's line, or - none: <reason>"
  else
    warn "References.md § Boundaries is empty: nothing to check yet"
  fi
fi
if [ -n "$NONE_REASON" ] && [ -s "$RULES" ]; then
  fail "References.md § Boundaries records none and also records rules; keep one"
fi

if [ -s "$RULES" ]; then
  # The unit's files, through git. The installed framework folder and Markdown are left out.
  if ! git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    fail "the unit is not inside a git repository, so its files cannot be listed; the boundary check reads the files git tracks and the untracked ones it does not ignore"
  else
    ENGINE_REL=""
    ENGINE_DIR="$(cd "$SCRIPT_DIR/.." && pwd -P)"
    case "$ENGINE_DIR/" in "$ROOT/"?*) ENGINE_REL="${ENGINE_DIR#"$ROOT"/}/" ;; esac
    ( cd "$ROOT" && git ls-files -z --cached --others --exclude-standard ) | tr '\000' '\n' | awk -v engine="$ENGINE_REL" '
      $0 == "" { next }
      engine != "" && index($0, engine) == 1 { next }
      $0 ~ /\.[Mm][Dd]$/ { next }
      { print }' | sort -u > "$LIST"
    GREP_I=""
    printf 'a\n' | grep -I a >/dev/null 2>&1 && GREP_I="-I"
    while IFS="$(printf '\t')" read -r label pattern paths; do
      [ -n "$label" ] || continue
      printf '' | grep -E -e "$pattern" >/dev/null 2>&1
      if [ "$?" -eq 2 ]; then
        fail "References.md § Boundaries, $label: the pattern \`$pattern\` is not a valid extended regular expression"
        continue
      fi
      # The files outside the rule's paths, then one search across them.
      : > "$HITS"
      : > "$LIST.out"
      while IFS= read -r f; do
        allowed=0
        rest="$paths"
        while [ -n "$rest" ]; do
          p="${rest%%	*}"; if [ "$p" = "$rest" ]; then rest=""; else rest="${rest#*	}"; fi
          p="${p#./}"
          [ -n "$p" ] || continue
          case "$p" in
            *'*'*|*'?'*|*'['*) case "$f" in $p) allowed=1 ;; esac ;;
            */) case "$f" in "$p"*) allowed=1 ;; esac ;;
            *) if [ "$f" = "$p" ]; then allowed=1; else case "$f" in "$p/"*) allowed=1 ;; esac; fi ;;
          esac
          [ "$allowed" -eq 1 ] && break
        done
        [ "$allowed" -eq 1 ] || printf '%s\n' "$f" >> "$LIST.out"
      done < "$LIST"
      if [ -s "$LIST.out" ]; then
        ( cd "$ROOT" && tr '\n' '\000' < "$LIST.out" | xargs -0 grep $GREP_I -l -s -E -e "$pattern" ) > "$HITS" 2>/dev/null
      fi
      if [ -s "$HITS" ]; then
        count="$(wc -l < "$HITS" | tr -d ' ')"
        shown="$(head -10 "$HITS" | tr '\n' ',' | sed -e 's/,$//' -e 's/,/, /g')"
        more=""; [ "$count" -gt 10 ] && more=" and $((count - 10)) more"
        where="$(printf '%s' "$paths" | sed -e 's/^	//' -e 's/	/, /g')"
        verb="use"; [ "$count" -eq 1 ] && verb="uses"
        fail "$label: $shown$more $verb \`$pattern\`, which only $where may use (References.md § Boundaries)"
      else
        pass "$label: only its recorded paths use \`$pattern\`"
      fi
    done < "$RULES"
  fi
fi
[ -n "$NONE_REASON" ] && [ ! -s "$RULES" ] && pass "References.md § Boundaries records none: $NONE_REASON"

[ "$ERRORS" -gt 0 ] && exit 1
exit 0
