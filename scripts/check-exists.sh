#!/bin/bash
# A step's check for "this file is there" (development/STEPS.md). Run from the project root:
#   scripts/check-exists.sh References.md feature-tree.md docs/systems
# Passes when every path named exists under the project root and, for a file, is not empty.
# A path that is absolute or climbs out of the project is refused. It checks that a file is
# there, never what is in it: whether the content is right is the step's other evidence and
# the review's reading.
ERRORS=0
[ $# -gt 0 ] || { echo "FAIL: name at least one path"; exit 1; }
for path in "$@"; do
  case "$path" in
    /*|*..*) echo "FAIL: $path: a path inside the project, written from its root"; ERRORS=$((ERRORS + 1)); continue ;;
  esac
  if [ -d "$path" ]; then echo "OK: $path/ exists"
  elif [ -s "$path" ]; then echo "OK: $path exists and is not empty"
  elif [ -e "$path" ]; then echo "FAIL: $path is empty"; ERRORS=$((ERRORS + 1))
  else echo "FAIL: $path does not exist"; ERRORS=$((ERRORS + 1))
  fi
done
[ "$ERRORS" -eq 0 ]
