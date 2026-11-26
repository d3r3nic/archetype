#!/bin/bash
# Reads feature-tree.md and checks the map against the unit's files (#16): every location a row
# names exists, and where the map names a folder's entries one by one, it names them all.
# Run from the unit's root, the folder that holds feature-tree.md. Used by
# scripts/validate-develop.sh and scripts/validate-maintain.sh; it can also run on its own.
#
# A Location cell holds one or more paths separated by commas, each from the unit's root, or from
# the repository's top for something outside the unit: the top is read only for a path whose
# first part the unit's root does not hold. Backticks around a path are fine. A cell
# that is empty, "-", none, n/a, or still the template's bracketed placeholder names nothing, and
# a row whose Status is not started, deferred, blocked or not applicable is not read. Anything
# else in a cell is read as a path, so a note or a shortened name fails as a path that does not
# exist: nothing the check cannot read counts as a pass.
#
# Checks:
#   1. Every path a row names exists, spelled as the folder spells it.
#   2. In each folder below the unit's root that the map does not name as a whole: when a row
#      names one of its files, every file in it is named; when a row names one of its subfolders,
#      every subfolder is named or holds something the map names. A folder the map names as a
#      whole is one thing, and its direct contents are not compared.
#      Entries are the files git tracks and the untracked ones it does not ignore. The installed
#      framework folder and a folder with a feature-tree.md of its own are left out.
# Exit 0 when the map holds, 1 on any failure, 2 on a usage error.

# Text is read as bytes, the same on every system: in a UTF-8 locale the macOS awk exits on a
# character that substr cut in two, and the macOS grep, sed and tr fail on bytes that are not UTF-8.
export LC_ALL=C

case "${1:-}" in
  '') ;;
  -h|--help) sed -n '2,23p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
  *) echo "unknown argument: $1 (this check takes none)"; exit 2 ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
ENGINE_DIR="$(cd "$SCRIPT_DIR/.." && pwd -P)"
ROOT="$(pwd -P)"
# The map is read where scripts/validate-develop.sh reads it.
TREE="$ROOT/feature-tree.md"
[ -f "$TREE" ] || TREE="$ROOT/archetype/feature-tree.md"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
ERRORS=0
fail() { printf "${RED}FAIL${NC}: %s\n" "$1"; ERRORS=$((ERRORS + 1)); }
warn() { printf "${YELLOW}WARN${NC}: %s\n" "$1"; }
pass() { printf "${GREEN}OK${NC}: %s\n" "$1"; }

if [ ! -f "$TREE" ]; then
  warn "no feature-tree.md at the unit's root: there is no map to check"
  exit 0
fi

TMP_BASE="${TMPDIR:-/tmp}/archetype-map-$$"
NAMED="$TMP_BASE.named"
FILES="$TMP_BASE.files"
GONE="$TMP_BASE.gone"
FOUND="$TMP_BASE.found"
RAW="$TMP_BASE.raw"
trap 'rm -f "$NAMED" "$FILES" "$GONE" "$FOUND" "$RAW"' EXIT HUP INT TERM
: > "$NAMED"

# The repository, when there is one: its top resolves a path that names something outside the
# unit, and its prefix turns a path written from the top into one from the unit's root.
TOP=""; PREFIX=""; IN_GIT=0
if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  IN_GIT=1
  TOP="$(git -C "$ROOT" rev-parse --show-toplevel 2>/dev/null)"
  PREFIX="$(git -C "$ROOT" rev-parse --show-prefix 2>/dev/null)"
fi

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

# True when every part of the path, read from the folder given, is an entry spelled exactly so.
# A file system that ignores case finds a path under any spelling; the map must use the real one,
# or the comparison below would read a folder that holds nothing.
spelled_so() {
  local base="$1" rest="$2" part
  while [ -n "$rest" ]; do
    part="${rest%%/*}"
    if [ "$part" = "$rest" ]; then rest=""; else rest="${rest#*/}"; fi
    [ -n "$part" ] || continue
    ls -a "$base" 2>/dev/null | grep -F -x -q -e "$part" || return 1
    base="$base/$part"
  done
  return 0
}

# One named entry of the unit, as its kind (d for a folder, f for a file) and its path from the root.
name_it() { if [ -d "$ROOT/$1" ]; then printf 'd %s\n' "$1" >> "$NAMED"; else printf 'f %s\n' "$1" >> "$NAMED"; fi; }

# ----------------------------------------------------------------------
# 1. Every path a row names exists
# ----------------------------------------------------------------------
MISSING=0
while IFS='|' read -r table num name location status; do
  [ -n "$table" ] || continue
  status_lc="$(printf '%s' "$status" | tr '[:upper:]' '[:lower:]')"
  case "$status_lc" in *'not started'*|*deferred*|*blocked*|*'not applicable'*) continue ;; esac
  cell="$(printf '%s' "$location" | tr -d '`')"
  cell_lc="$(printf '%s' "$cell" | tr '[:upper:]' '[:lower:]')"
  case "$cell_lc" in ''|'['*']'|none|n/a|-) continue ;; esac
  rest="$cell"
  while [ -n "$rest" ]; do
    item="${rest%%,*}"
    if [ "$item" = "$rest" ]; then rest=""; else rest="${rest#*,}"; fi
    while :; do case "$item" in ' '*|'	'*) item="${item#?}" ;; *) break ;; esac; done
    while :; do case "$item" in *' '|*'	') item="${item%?}" ;; *) break ;; esac; done
    [ -n "$item" ] || continue
    shown="$item"
    case "$item" in
      /*|'~'*) fail "$table row $num ($name) names \`$shown\`, which is not a path inside the project"; MISSING=$((MISSING + 1)); continue ;;
    esac
    case "/$item/" in
      */../*) fail "$table row $num ($name) names \`$shown\`, which leaves the project"; MISSING=$((MISSING + 1)); continue ;;
    esac
    # One spelling per path: no "./", no doubled or trailing slash.
    while :; do case "$item" in ./*) item="${item#./}" ;; *) break ;; esac; done
    while :; do case "$item" in *//*) item="${item%%//*}/${item#*//}" ;; *) break ;; esac; done
    while :; do case "$item" in */./*) item="${item%%/./*}/${item#*/./}" ;; *) break ;; esac; done
    while :; do case "$item" in */.) item="${item%/.}" ;; *) break ;; esac; done
    while :; do case "$item" in */) item="${item%/}" ;; *) break ;; esac; done
    case "$item" in ''|.) continue ;; esac   # the unit's root itself
    if [ -e "$ROOT/$item" ]; then
      if spelled_so "$ROOT" "$item"; then
        name_it "$item"
      else
        fail "$table row $num ($name) names \`$shown\`, which exists only under another spelling; spell it as the folder does, capitals included"
        MISSING=$((MISSING + 1))
      fi
    elif [ -n "$TOP" ] && [ "$TOP" != "$ROOT" ] && [ ! -e "$ROOT/${item%%/*}" ] && [ -e "$TOP/$item" ]; then
      if ! spelled_so "$TOP" "$item"; then
        fail "$table row $num ($name) names \`$shown\`, which exists only under another spelling; spell it as the folder does, capitals included"
        MISSING=$((MISSING + 1))
      elif [ -n "$PREFIX" ]; then
        # Written from the repository's top: inside the unit it is compared like any other.
        case "$item/" in
          "$PREFIX") ;;   # the unit's root itself
          "$PREFIX"?*) name_it "${item#"$PREFIX"}" ;;
        esac
      fi
    else
      fail "$table row $num ($name) names \`$shown\`, which does not exist"
      MISSING=$((MISSING + 1))
    fi
  done
done <<EOF
$ROWS
EOF
if [ "$MISSING" -eq 0 ]; then
  pass "every location the map names exists"
else
  echo "  A Location cell holds paths separated by commas, each from the unit's root, or from the repository's top for something outside the unit; a note belongs in the record, not in the cell."
fi

# ----------------------------------------------------------------------
# 2. Where the map names a folder's entries one by one, it names them all
# ----------------------------------------------------------------------
if ! grep -q / "$NAMED"; then
  pass "the map names no single entry of a folder below the unit's root: nothing to compare"
elif [ "$IN_GIT" -eq 0 ]; then
  fail "the unit is not inside a git repository, so the entries beside the ones the map names cannot be listed; the check reads the files git tracks and the untracked ones it does not ignore"
else
  ENGINE_REL=""
  case "$ENGINE_DIR/" in "$ROOT/"?*) ENGINE_REL="${ENGINE_DIR#"$ROOT"/}" ;; esac
  # The unit's files as git lists them, one a line, without the ones deleted and not yet committed.
  # A listing git could not finish is a failure, never an empty folder.
  LISTED=1
  ( cd "$ROOT" && git ls-files -z --deleted ) > "$RAW" 2>/dev/null || LISTED=0
  tr '\0' '\n' < "$RAW" > "$GONE"
  ( cd "$ROOT" && git ls-files -z --cached --others --exclude-standard ) > "$RAW" 2>/dev/null || LISTED=0
  # Paths reach awk through the environment: -v would read a backslash in one as an escape.
  tr '\0' '\n' < "$RAW" | MAP_GONE="$GONE" awk '
    BEGIN { gone = ENVIRON["MAP_GONE"]; while ((getline line < gone) > 0) deleted[line] = 1 }
    $0 != "" && !($0 in deleted)' > "$FILES"
  sort -u "$NAMED" -o "$NAMED"
  MAP_ENGINE="$ENGINE_REL" MAP_NAMED="$NAMED" awk '
    function parent(s,   i, k) { k = 0; while ((i = index(substr(s, k + 1), "/")) > 0) k += i; return k ? substr(s, 1, k - 1) : "" }
    function base(s,   p) { p = parent(s); return p == "" ? s : substr(s, length(p) + 2) }
    BEGIN {
      engine = ENVIRON["MAP_ENGINE"]; named_file = ENVIRON["MAP_NAMED"]
      while ((getline line < named_file) > 0) {
        if (length(line) < 3) continue
        n = substr(line, 3)
        named[n] = substr(line, 1, 1)
        for (p = parent(n); p != ""; p = parent(p)) holds[p] = 1
      }
      # A folder is compared when it is below the root and not named itself: for its files once a
      # row names one of them, for its subfolders once a row names one of them.
      for (n in named) {
        d = parent(n)
        if (d != "" && !(d in named)) { if (!(d in folder)) { folder[d] = 1; compared++ }; item[d, named[n]] = 1 }
      }
    }
    {
      f = $0
      if (engine != "" && (f == engine || index(f, engine "/") == 1)) next
      if (length(f) > 16 && substr(f, length(f) - 15) == "/feature-tree.md") unit[substr(f, 1, length(f) - 16)] = 1
      pos = 0
      while ((i = index(substr(f, pos + 1), "/")) > 0) {
        pos += i
        a = substr(f, 1, pos - 1)
        rest = substr(f, pos + 1); j = index(rest, "/")
        kind = j ? "d" : "f"
        if ((a, kind) in item) {
          c = a "/" (j ? substr(rest, 1, j - 1) : rest)
          if (!((a, c) in seen)) { seen[a, c] = 1; order[++count] = c; of[count] = a; is[count] = kind }
        }
      }
    }
    END {
      for (k = 1; k <= count; k++) {
        c = order[k]; a = of[k]
        if (c in named || c in holds || c in unit) continue
        if (!(a in missing)) dirs[++nd] = a
        missing[a]++
        if (missing[a] <= 10) shown[a] = shown[a] == "" ? base(c) : shown[a] ", " base(c)
      }
      for (k = 1; k <= nd; k++) {
        a = dirs[k]
        more = missing[a] > 10 ? " and " (missing[a] - 10) " more" : ""
        print "F " a "/ holds " shown[a] more ", which no row names"
      }
      print "C " compared + 0
    }' "$FILES" > "$FOUND"
  UNNAMED=0
  COMPARED=""
  while IFS= read -r line; do
    case "$line" in
      'C '*) COMPARED="${line#C }" ;;
      'F '*) fail "${line#F }"; UNNAMED=$((UNNAMED + 1)) ;;
    esac
  done < "$FOUND"
  # The count line is the last thing the comparison prints: without it, it did not finish.
  if [ "$LISTED" -eq 0 ] || [ -z "$COMPARED" ]; then
    fail "the entries beside the ones the map names could not be listed, so nothing was compared"
  elif [ "$UNNAMED" -eq 0 ]; then
    pass "where the map names a folder's entries one by one, it names them all (folders compared: $COMPARED)"
  else
    echo "  Where the map names a folder's files or subfolders one by one, it names them all: add each to its row in feature-tree.md, or name the folder as a whole when it is one thing."
  fi
fi

[ "$ERRORS" -gt 0 ] && exit 1
exit 0
