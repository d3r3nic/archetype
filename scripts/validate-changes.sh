#!/bin/bash
# Checks that development/CHANGES.md is in the form update.sh reads. The updater prints the
# entries a project has not seen by matching the revision the project had installed against each
# entry's Follows line, so every entry needs:
#   - a heading "## <YYYY-MM-DD>: <title>", entries newest first;
#   - exactly one "Follows: <full revision>" line, a revision no other entry names;
#   - at least one "- **Session:**" line and one "- **Project:**" line.
# Usage: scripts/validate-changes.sh [file]   (default: the framework's development/CHANGES.md)
# Exit 0 when the file is in form, 1 otherwise.

# Text is read as bytes, the same on every system.
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FILE="${1:-$SCRIPT_DIR/../development/CHANGES.md}"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

if [ ! -f "$FILE" ]; then
  printf "${RED}FAIL${NC}: development/CHANGES.md missing\n"
  exit 1
fi

PROBLEMS="$(tr -d '\r' < "$FILE" | awk '
  function close_entry() {
    if (n == 0) return
    if (follows != 1) print "entry \"" title "\" has " follows " Follows lines; it needs exactly one"
    if (!session) print "entry \"" title "\" has no Session line"
    if (!project) print "entry \"" title "\" has no Project line"
  }
  /^## / {
    close_entry(); n++; title = substr($0, 4); follows = 0; session = 0; project = 0
    if (title !~ /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]: ./) { print "heading \"" title "\" is not <date>: <title>"; next }
    date = substr(title, 1, 10)
    if (dated && date > previous) print "entry \"" title "\" is newer than the one above it; newest first"
    previous = date; dated = 1
    next
  }
  # An entry whose heading is not "## " falls before the first heading, where the updater never
  # reads it: its lines there are reported.
  n == 0 && /^(Follows:|- [*][*](Session|Project):[*][*])/ { print "line " NR " comes before the first entry heading \"## <date>: <title>\": " $0; next }
  /^Follows:/ {
    follows++; value = $0; sub(/^Follows: /, "", value)
    if (value !~ /^[0-9a-f]+$/ || length(value) != 40) print "entry \"" title "\" Follows line is not a full revision: " value
    else if (value in seen) print "entry \"" title "\" follows the same revision as \"" seen[value] "\""
    else seen[value] = title
    next
  }
  /^- [*][*]Session:[*][*]/ { session = 1 }
  /^- [*][*]Project:[*][*]/ { project = 1 }
  END { close_entry(); if (n == 0) print "no entries" }
')"

if [ -n "$PROBLEMS" ]; then
  printf '%s\n' "$PROBLEMS" | while IFS= read -r line; do printf "${RED}FAIL${NC}: development/CHANGES.md: %s\n" "$line"; done
  exit 1
fi
printf "${GREEN}OK${NC}: development/CHANGES.md: every entry is dated, newest first, with one full Follows revision\n"
exit 0
