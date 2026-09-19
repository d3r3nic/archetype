#!/bin/bash
# The step ledger's tool (development/STEPS.md). A playbook is a list of steps; a project's
# PROGRESS.md records which are closed. This script names the next open step and what to
# read for it, closes a step only when its check passes, and, on every run in a project,
# first re-runs the checks behind closed steps, so a tick cannot outlive the thing it ticked.
#
# Run from the project (its root, or any folder under it):
#   scripts/next-step.sh                          the next open step: what to read, what closes it
#   scripts/next-step.sh --list                   every step of the project's playbooks with its state
#   scripts/next-step.sh --close ID [--evidence TEXT]   close the next open step (its check must pass)
#   scripts/next-step.sh --skip ID --reason TEXT        record a step that does not apply; only a step
#                                                       whose playbook says when it may be skipped
#   add --unit NAME for a playbook that repeats (one run of its steps per feature)
#   add --verify to re-run the project's own commands behind closed steps now (they are
#   otherwise re-run whenever a step closes or is skipped; engine scripts are re-run every time)
# Run from the engine:
#   scripts/next-step.sh --lint                   every stepped playbook is well formed (the self-test runs this)
#
# What it reads in a playbook: a "Step ledger: <id>" line (with "(per feature)" when the steps
# repeat), headings of the form "## Step N: Title" or "### Step N.M - Title", and inside each
# step, before any sub-heading, the lines "Read:", "Produces:", "Check:", and optionally
# "Skip when:". A step with sub-steps (2 with 2.1, 2.2) is a container; only its sub-steps
# open and close. A check passes when it exits 0.
#
# What it cannot do: tell whether a step was done well, whether quoted evidence is what the
# owner said, whether a skip's reason is true, or stop anyone editing PROGRESS.md by hand.
# A skipped step's check is never run. A check it can run, it re-runs.
#
# Exit 0: a next step was named, a step was closed or skipped, or everything is closed.
# Exit 1: refused, or a closed step's check now fails, or the lint found a fault.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENGINE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
START_DIR="$(pwd)"
SEP="$(printf '\037')"

MODE="next"; ID=""; UNIT=""; EVIDENCE=""; REASON=""; VERIFY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --lint) MODE="lint" ;;
    --list) MODE="list" ;;
    --verify) VERIFY=1 ;;
    --close) MODE="close"; ID="${2:-}"; [ $# -gt 1 ] && shift ;;
    --skip) MODE="skip"; ID="${2:-}"; [ $# -gt 1 ] && shift ;;
    --unit) UNIT="${2:-}"; [ $# -gt 1 ] && shift ;;
    --evidence) EVIDENCE="${2:-}"; [ $# -gt 1 ] && shift ;;
    --reason) REASON="${2:-}"; [ $# -gt 1 ] && shift ;;
    *) echo "Unknown argument: $1 (the head of this script lists them)"; exit 1 ;;
  esac
  shift
done
case "$ID" in --*) echo "Name the step: --close ID or --skip ID."; exit 1 ;; esac

# One line per step of every stepped playbook, fields separated by the unit separator:
# playbook id, once|unit, step id, title, file, line, Read, Produces, Check, Skip when,
# count of Read lines, of Produces lines, of Check lines, and a kind:
# leaf|container|empty|malformed|nopart|partdecl.
# A playbook is its entry file (the one carrying "Step ledger:") followed by the files its
# "Step files:" line lists, in that order: a file is what a session opens, so a step, or a
# few small ones, gets a file of its own. Lines inside a code fence declare nothing.
playbook_head() { # entry file -> id, once|unit, the step files (semicolon-separated)
  awk -v S="$SEP" '
    { sub(/\r$/, "") }
    /^```/ { fence = !fence; next }
    fence { next }
    /^Step ledger: / && !declared { declared = 1; pid = $3; mode = ($0 ~ /\(per [a-z]+\)/) ? "unit" : "once"; next }
    /^Step files: / { parts = parts (parts == "" ? "" : ";") substr($0, 13) }
    END { if (declared) print pid S mode S parts }' "$1"
}
parse_steps() { # file (from the engine root), playbook id, once|unit -> one row per step heading
  awk -v file="$1" -v pid="$2" -v mode="$3" -v S="$SEP" '
    function flush() {
      if (sid != "") print pid S mode S sid S title S file S line S rd S pr S ck S sw S rc S pc S cc S "step"
      sid = ""
    }
    { sub(/\r$/, "") }
    /^```/ { fence = !fence; next }
    fence { next }
    /^Step ledger: / { if (part) print pid S mode S "" S "" S file S NR S "" S "" S "" S "" S 0 S 0 S 0 S "partdecl"; next }
    /^###? Step [A-Za-z0-9][A-Za-z0-9.]*(:| )/ {
      flush()
      h = $0; sub(/^###? Step /, "", h)
      sid = h; sub(/[ :].*$/, "", sid)
      title = h; sub(/^[^ :]+:? */, "", title); sub(/^(—|-) */, "", title)
      line = NR; rd = ""; pr = ""; ck = ""; sw = ""; rc = 0; pc = 0; cc = 0
      next
    }
    /^#+[ \t]+Step([ \t:]|$)/ { flush(); print pid S mode S "" S "" S file S NR S "" S "" S "" S "" S 0 S 0 S 0 S "malformed"; next }
    /^#+ / { flush(); next }
    sid != "" && /^Read: /      { rd = substr($0, 7);  rc++; next }
    sid != "" && /^Produces: /  { pr = substr($0, 11); pc++; next }
    sid != "" && /^Check: /     { ck = substr($0, 8);  cc++; next }
    sid != "" && /^Skip when: / { sw = substr($0, 12); next }
    END { flush() }' part="$4" "$ENGINE_DIR/$1"
}
steps_table() {
  local f rel head pid mode parts rows part OLDIFS
  for f in "$ENGINE_DIR"/bootstrap/*.md "$ENGINE_DIR"/scaffolding/*.md "$ENGINE_DIR"/development/*.md; do
    [ -f "$f" ] || continue
    grep -q '^Step ledger: ' "$f" || continue
    head="$(playbook_head "$f")"
    [ -n "$head" ] || continue
    rel="${f#$ENGINE_DIR/}"
    pid="${head%%$SEP*}"; head="${head#*$SEP}"; mode="${head%%$SEP*}"; parts="${head#*$SEP}"
    rows="$(parse_steps "$rel" "$pid" "$mode" "")"
    OLDIFS="$IFS"; IFS=";"
    for part in $parts; do
      IFS="$OLDIFS"
      part="$(printf '%s' "$part" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
      if [ -z "$part" ]; then IFS=";"; continue; fi
      if [ -f "$ENGINE_DIR/$part" ] && case "$part" in /*|*..*) false ;; *) true ;; esac; then
        rows="$rows
$(parse_steps "$part" "$pid" "$mode" 1)"
      else
        rows="$rows
$pid$SEP$mode$SEP$SEP$SEP$part$SEP""0$SEP$SEP$SEP$SEP$SEP""0$SEP""0$SEP""0$SEP""nopart"
      fi
      IFS=";"
    done
    IFS="$OLDIFS"
    # A step with sub-steps anywhere in the playbook is a container; a playbook with no step is empty.
    printf '%s\n' "$rows" | awk -F"$SEP" -v S="$SEP" -v pid="$pid" -v mode="$mode" -v file="$rel" '
      NF < 14 { next }
      { n++; row[n] = $0; sid[n] = $3; kind[n] = $14 }
      END {
        steps = 0
        for (i = 1; i <= n; i++) {
          if (kind[i] != "step") { print row[i]; continue }
          steps++
          k = "leaf"
          for (j = 1; j <= n; j++) if (j != i && kind[j] == "step" && index(sid[j], sid[i] ".") == 1) k = "container"
          sub(/step$/, k, row[i]); print row[i]
        }
        if (steps == 0) print pid S mode S "" S "" S file S 0 S "" S "" S "" S "" S 0 S 0 S 0 S "empty"
      }'
  done
}

trim() { printf '%s' "$1" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'; }

# A Read entry as a path a person can open: "#8" becomes its convention file.
resolve_read() {
  local e; e="$(trim "$1")"
  case "$e" in
    '#'[0-9]*)
      local num rest file
      num="${e#\#}"; rest=""
      case "$num" in *' '*) rest=" ${num#* }"; num="${num%% *}" ;; esac
      file="$(cd "$ENGINE_DIR" && ls conventions/"$(printf '%02d' "$num" 2>/dev/null)"-*.md 2>/dev/null | head -1)"
      if [ -n "$file" ]; then printf '%s%s' "$file" "$rest"; else printf '%s' "$e"; fi ;;
    *) printf '%s' "$e" ;;
  esac
}

# "path § Section": true when the file has a heading that opens with the section's name
# (a heading may say more after it), or when no section is named.
has_section() {
  case "$1" in *' § '*) ;; *) return 0 ;; esac
  local file="${1%% § *}" want="${1#* § }"
  [ -f "$ENGINE_DIR/$file" ] || return 0
  tr -d '\r' < "$ENGINE_DIR/$file" | W="$want" awk '/^```/ { fence = !fence; next } fence { next }
    /^#+ / { h = $0; sub(/^#+ +/, "", h); if (index(h, ENVIRON["W"]) == 1) { found = 1; exit } } END { exit !found }'
}

# A Check line is "run <command>", "evidence: <what is recorded>", or both: "run <command>; evidence: <...>".
# The command is an engine script ("scripts/x.sh --flag") or the project's own recorded commands
# ("project: typecheck, lint, test": labels of References.md, section Commands).
check_command() { case "$1" in 'run '*) local c="${1#run }"; printf '%s' "${c%%; evidence: *}" ;; esac; }
check_evidence() { case "$1" in 'evidence: '*) printf '%s' "${1#evidence: }" ;; *'; evidence: '*) printf '%s' "${1#*; evidence: }" ;; esac; }
is_project_command() { case "$1" in 'project: '*) return 0 ;; esac; return 1; }
valid_command() {
  if is_project_command "$1"; then
    printf '%s' "$1" | grep -qE '^project: [a-z][a-z0-9_-]*(, *[a-z][a-z0-9_-]*)*$'; return $?
  fi
  printf '%s' "$1" | grep -qE '^scripts/[A-Za-z0-9._-]+\.(sh|py)( [-A-Za-z0-9=._/ ]+)?$' || return 1
  case " ${1#* }" in *' /'*|*'..'*) return 1 ;; esac
  return 0
}
command_exists() { is_project_command "$1" || [ -f "$ENGINE_DIR/${1%% *}" ]; }

# The project's recorded command for a label: the "label: command" line of References.md, section Commands.
project_command() {
  local refs="" dir
  for dir in "$PROJECT_ROOT" "$PROJECT_ROOT/project" "$PROJECT_ROOT/archetype"; do
    if [ -f "$dir/References.md" ]; then refs="$dir/References.md"; break; fi
  done
  [ -n "$refs" ] || return 1
  tr -d '\r' < "$refs" | L="$1" awk '/^## Commands/ { f = 1; next } /^## / { f = 0 }
    f { l = ENVIRON["L"] ":"; if (index($0, l) == 1) { v = substr($0, length(l) + 1); sub(/^[ \t]+/, "", v); sub(/[ \t]+$/, "", v); print v; exit } }'
}

CHECK_OUT=""
run_check() {
  local cmd="$1" script args runner label value labels OLDIFS
  if is_project_command "$cmd"; then
    CHECK_OUT=""
    labels="${cmd#project: }"
    OLDIFS="$IFS"; IFS=","
    for label in $labels; do
      IFS="$OLDIFS"
      label="$(trim "$label")"
      value="$(project_command "$label")"
      case "$(printf '%s' "$value" | tr '[:upper:]' '[:lower:]')" in
        ''|'['*) CHECK_OUT="FAIL: References.md, section Commands, records no command for '$label' (write the command, or none when the project has no such command)"; return 1 ;;
        none*|n/a*) IFS=","; continue ;;
      esac
      if ! CHECK_OUT="$(cd "$PROJECT_ROOT" && ARCHETYPE_STEP_UNIT="$UNIT" bash -c "$value" 2>&1)"; then
        CHECK_OUT="FAIL: the project's $label command failed: $value
$CHECK_OUT"
        return 1
      fi
      IFS=","
    done
    IFS="$OLDIFS"
    return 0
  fi
  script="${cmd%% *}"; args=""
  [ "$script" != "$cmd" ] && args="${cmd#* }"
  case "$script" in *.py) runner="python3" ;; *) runner="bash" ;; esac
  # shellcheck disable=SC2086
  CHECK_OUT="$(cd "$PROJECT_ROOT" && ARCHETYPE_STEP_UNIT="$UNIT" $runner "$ENGINE_DIR/$script" $args 2>&1)"
}
show_check_output() {
  local lines
  lines="$(printf '%s\n' "$CHECK_OUT" | grep -E 'FAIL|Error' | head -12)"
  [ -n "$lines" ] || lines="$(printf '%s\n' "$CHECK_OUT" | sed '/^[[:space:]]*$/d' | tail -5)"
  [ -n "$lines" ] || lines="(the check printed nothing and exited non-zero)"
  printf '%s\n' "$lines" | sed 's/^/    /'
}

# ----------------------------------------------------------------------
if [ "$MODE" = "lint" ]; then
  ERRORS=0
  bad() { printf 'FAIL: %s\n' "$1"; ERRORS=$((ERRORS + 1)); }
  TABLE="$(steps_table)"
  if [ -z "$TABLE" ]; then
    echo "OK: no stepped playbook yet (none carries a 'Step ledger:' line)"
    exit 0
  fi
  SEEN=""; COUNT=0
  # One playbook per ledger id, and a step file belongs to one playbook, once.
  HEADS=""
  for f in "$ENGINE_DIR"/bootstrap/*.md "$ENGINE_DIR"/scaffolding/*.md "$ENGINE_DIR"/development/*.md; do
    [ -f "$f" ] || continue
    grep -q '^Step ledger: ' "$f" || continue
    h="$(playbook_head "$f")"
    [ -n "$h" ] || continue
    HEADS="$HEADS
${f#$ENGINE_DIR/}$SEP$h"
  done
  printf '%s\n' "$HEADS" | awk -F"$SEP" '
    NF < 3 { next }
    { if ($2 in owner) print "ID" FS $2 FS owner[$2] FS $1; else owner[$2] = $1
      n = split($4, parts, ";")
      for (i = 1; i <= n; i++) { p = parts[i]; gsub(/^[ \t]+|[ \t]+$/, "", p); if (p == "") continue
        if (p in used) print "PART" FS p FS used[p] FS $1; else used[p] = $1 } }' > "${TMPDIR:-/tmp}/next-step-lint.$$"
  while IFS="$SEP" read -r what a b c; do
    case "$what" in
      ID) bad "$c: ledger id '$a' is also declared by $b; one playbook per id" ;;
      PART) bad "$c: step file $a is already listed by $b; a step file belongs to one playbook, once" ;;
    esac
  done < "${TMPDIR:-/tmp}/next-step-lint.$$"
  rm -f "${TMPDIR:-/tmp}/next-step-lint.$$"
  while IFS="$SEP" read -r pid mode sid title file line rd pr ck sw rc pc cc kind; do
    [ -n "$file" ] || continue
    if [ -z "$pid" ]; then bad "$file: the 'Step ledger:' line names no id"; continue; fi
    printf '%s' "$pid" | grep -qE '^[a-z][a-z0-9-]*$' || bad "$file: ledger id '$pid' must be lower-case letters, digits, and hyphens"
    if [ "$kind" = "nopart" ]; then bad "playbook '$pid': its 'Step files:' line names $file, which is not a file in the engine"; continue; fi
    if [ "$kind" = "partdecl" ]; then bad "$file:$line: a step file carries no 'Step ledger:' line of its own; its playbook's entry file declares the ledger and lists it"; continue; fi
    if [ "$kind" = "malformed" ]; then bad "$file:$line: a heading that opens with 'Step' is not a step: write '## Step <id>: Title' or '### Step <id>: Title', one space after the marks, an id of letters, digits, and dots"; continue; fi
    if [ "$kind" = "empty" ]; then bad "$file: declares a step ledger and has no 'Step' heading"; continue; fi
    where="$file:$line ($pid.$sid)"
    case "
$SEEN
" in *"
$pid.$sid
"*) bad "$where: the step id appears twice" ;; esac
    SEEN="$SEEN
$pid.$sid"
    [ "$kind" = "container" ] && continue
    COUNT=$((COUNT + 1))
    [ "$rc" = "1" ] || bad "$where: needs exactly one 'Read:' line directly under the heading (found $rc); write 'Read: none' when nothing is read"
    [ "$pc" = "1" ] || bad "$where: needs exactly one 'Produces:' line directly under the heading (found $pc)"
    [ "$cc" = "1" ] || bad "$where: needs exactly one 'Check:' line directly under the heading (found $cc)"
    [ "$pc" = "1" ] && [ -z "$(trim "$pr")" ] && bad "$where: 'Produces:' is empty"
    if [ "$rc" = "1" ]; then
      [ -z "$(trim "$rd")" ] && bad "$where: 'Read:' is empty; write none when nothing is read"
      OLDIFS="$IFS"; IFS=";"
      for entry in $rd; do
        IFS="$OLDIFS"
        entry="$(trim "$entry")"
        case "$entry" in *' (when '*')') entry="$(trim "${entry%% (when *}")" ;; esac
        case "$entry" in
          ''|none|'project: '*) ;;
          '#'[0-9]*)
            r="$(resolve_read "$entry")"
            case "$r" in conventions/*) has_section "$r" || bad "$where: Read names $entry, and ${r%% § *} has no heading that opens with '${r#* § }'" ;; *) bad "$where: Read names $entry and no convention file has that number" ;; esac ;;
          *)
            path="${entry%% § *}"
            [ -e "$ENGINE_DIR/$path" ] && { has_section "$entry" || bad "$where: Read names '$entry', and $path has no heading that opens with '${entry#* § }'"; }
            [ -e "$ENGINE_DIR/$path" ] || bad "$where: Read names '$path', which is not in the engine (a project file is written 'project: <file>'; entries are separated by semicolons, so a section name holds none)" ;;
        esac
        IFS=";"
      done
      IFS="$OLDIFS"
    fi
    if [ "$cc" = "1" ]; then
      case "$ck" in
        'run '*)
          cmd="$(check_command "$ck")"
          if ! valid_command "$cmd"; then bad "$where: Check runs '$cmd'; it may run an engine script under scripts/ with plain arguments, or 'project: <labels>' naming commands recorded in References.md"
          elif ! command_exists "$cmd"; then bad "$where: Check runs ${cmd%% *}, which does not exist"
          fi
          case "$ck" in *'; evidence: ') bad "$where: Check asks for evidence and does not say what" ;; esac ;;
        'evidence: '?*) ;;
        *) bad "$where: Check is 'run scripts/<script> [arguments]', 'run project: <labels>', 'evidence: <what is recorded, in whose words>', or a run followed by '; evidence: <...>'" ;;
      esac
    fi
  done <<EOF
$TABLE
EOF
  if [ "$ERRORS" -gt 0 ]; then echo "$ERRORS fault(s) in stepped playbooks"; exit 1; fi
  echo "OK: $COUNT steps in stepped playbooks each carry Read, Produces, and Check; every engine path and script named exists"
  exit 0
fi

# ----------------------------------------------------------------------
# Everything below works on a project: the nearest folder, from here upward, with a ledger.
PROJECT_ROOT="$START_DIR"
d="$START_DIR"
while [ -n "$d" ] && [ "$d" != "/" ]; do
  if [ -f "$d/PROGRESS.md" ]; then PROJECT_ROOT="$d"; break; fi
  d="$(dirname "$d")"
done
LEDGER="$PROJECT_ROOT/PROGRESS.md"
case "$SCRIPT_DIR" in
  "$PROJECT_ROOT"/*) SELF="${SCRIPT_DIR#$PROJECT_ROOT/}/next-step.sh" ;;
  *) SELF="$SCRIPT_DIR/next-step.sh" ;;
esac

if [ ! -f "$LEDGER" ]; then
  echo "No PROGRESS.md in $START_DIR or any folder above it."
  echo "In the project root, copy ${SELF%scripts/next-step.sh}templates/progress.md to PROGRESS.md, fill its Playbooks line, and run this again."
  echo "For work that began before the ledger: close the finished steps one at a time, oldest first; each check still has to pass."
  exit 1
fi
case "$UNIT" in
  -*|*[!A-Za-z0-9._-]*)
    echo "Refused: a unit name is letters, digits, dots, hyphens, and underscores (the feature's folder name)."
    exit 1 ;;
esac

PLAYBOOKS="$(tr -d '\r' < "$LEDGER" | sed -n 's/^- Playbooks:[[:space:]]*//p' | head -1)"
case "$PLAYBOOKS" in
  ''|'['*) echo "PROGRESS.md: fill the '- Playbooks:' line with the ledger ids this project follows, in order (run --lint in the engine to see them)."; exit 1 ;;
esac
TABLE="$(steps_table)"
CLOSED_LINES="$(tr -d '\r' < "$LEDGER" | grep -E '^- \[[x-]\] ')"
ledger_key='{ l = $0; sub(/^- \[.\] /, "", l); sub(/ *\|.*$/, "", l) }'
state_of() { # key -> closed | skipped | open
  local hit
  hit="$(printf '%s\n' "$CLOSED_LINES" | K="$1" awk "$ledger_key"' l == ENVIRON["K"] { print substr($0, 4, 1); exit }')"
  case "$hit" in x) echo closed ;; -) echo skipped ;; *) echo open ;; esac
}
# Every closed (not skipped) ledger key of a step, across all units: "id" and "id @unit".
closed_keys_of() {
  printf '%s\n' "$CLOSED_LINES" | K="$1" awk "$ledger_key"' substr($0, 4, 1) == "x" && (l == ENVIRON["K"] || index(l, ENVIRON["K"] " @") == 1) { print l }'
}
key_of() { if [ "$2" = "unit" ]; then printf '%s @%s' "$1" "$UNIT"; else printf '%s' "$1"; fi; }

# Walk the project's playbooks in order. Sets NEXT_* to the first open leaf step.
NEXT_ID=""; NEED_UNIT=""; LISTING=""; WALKED=""
OLDIFS="$IFS"; IFS=","
for pb in $PLAYBOOKS; do
  IFS="$OLDIFS"
  pb="$(trim "$pb")"
  case ",$WALKED," in *",$pb,"*) pb="" ;; esac
  [ -n "$pb" ] || { IFS=","; continue; }
  WALKED="$WALKED,$pb"
  if ! printf '%s\n' "$TABLE" | awk -F"$SEP" -v p="$pb" '$1 == p { f = 1 } END { exit !f }'; then
    echo "PROGRESS.md names the playbook '$pb', and no playbook in the engine declares that ledger id."
    exit 1
  fi
  while IFS="$SEP" read -r pid mode sid title file line rd pr ck sw rc pc cc kind; do
    [ "$pid" = "$pb" ] && [ "$kind" = "leaf" ] || continue
    if [ "$mode" = "unit" ] && [ -z "$UNIT" ]; then NEED_UNIT="$pb"; continue; fi
    key="$(key_of "$pid.$sid" "$mode")"
    st="$(state_of "$key")"
    LISTING="$LISTING
$st  $key  $title"
    if [ "$st" = "open" ] && [ -z "$NEXT_ID" ]; then
      NEXT_ID="$pid.$sid"; NEXT_KEY="$key"; NEXT_TITLE="$title"; NEXT_FILE="$file"; NEXT_LINE="$line"
      NEXT_READ="$rd"; NEXT_PROD="$pr"; NEXT_CHECK="$ck"; NEXT_SKIP="$sw"
    fi
  done <<EOF
$TABLE
EOF
  IFS=","
done
IFS="$OLDIFS"

# Every closed step's check is run again, whatever its unit, once per distinct command.
# The command always comes from the playbook, never from the ledger.
REVERIFY_OK=1
done_cmds=""
FAILED_KEYS=""
PROJECT_CHECKS_WAITING=0
while IFS="$SEP" read -r pid mode sid title file line rd pr ck sw rc pc cc kind; do
  [ "$kind" = "leaf" ] || continue
  cmd="$(check_command "$ck")"
  [ -n "$cmd" ] || continue
  keys="$(closed_keys_of "$pid.$sid")"
  [ -n "$keys" ] || continue
  if is_project_command "$cmd" && [ "$MODE" != "close" ] && [ "$MODE" != "skip" ] && [ "$VERIFY" != "1" ]; then PROJECT_CHECKS_WAITING=1; continue; fi
  keys_line="$(printf '%s' "$keys" | tr '\n' ',' | sed 's/,/, /g')"
  if ! valid_command "$cmd" || ! command_exists "$cmd"; then
    REVERIFY_OK=0
    FAILED_KEYS="$FAILED_KEYS
$keys"
    echo "REOPENED: $keys_line: the playbook's check '$cmd' is not a check that can be run (run --lint in the engine)"
    continue
  fi
  case "
$done_cmds
" in *"
$cmd$SEP"fail"
"*) REVERIFY_OK=0; FAILED_KEYS="$FAILED_KEYS
$keys"; echo "REOPENED: $keys_line: closed, and its check now fails: $cmd"; continue ;;
    *"
$cmd$SEP"pass"
"*) continue ;;
  esac
  if run_check "$cmd"; then
    done_cmds="$done_cmds
$cmd$SEP"pass""
  else
    done_cmds="$done_cmds
$cmd$SEP"fail""
    REVERIFY_OK=0
    FAILED_KEYS="$FAILED_KEYS
$keys"
    echo "REOPENED: $keys_line: closed, and its check now fails: $cmd"
    show_check_output
  fi
done <<EOF
$TABLE
EOF

if [ "$MODE" = "list" ]; then
  printf '%s\n' "$LISTING" | sed '/^$/d' | F="$FAILED_KEYS" awk 'BEGIN { n = split(ENVIRON["F"], f, "\n"); for (i = 1; i <= n; i++) if (f[i] != "") bad[f[i]] = 1 }
    { for (k in bad) if (index($0, "closed  " k "  ") == 1) { sub(/^closed  /, "reopened  "); break } print }'
  [ -n "$NEED_UNIT" ] && echo "(the playbook '$NEED_UNIT' repeats: add --unit NAME to list one run of it)"
  [ "$REVERIFY_OK" = "1" ] || exit 1
  exit 0
fi
if [ "$REVERIFY_OK" != "1" ]; then
  echo "Fix what failed, then run this again. Nothing is named, closed, or skipped while a closed step's check fails."
  exit 1
fi

if [ "$MODE" = "next" ]; then
  if [ -z "$NEXT_ID" ]; then
    if [ -n "$NEED_UNIT" ]; then echo "Every one-time step is closed. The playbook '$NEED_UNIT' repeats: run with --unit NAME (the feature's name)."
    else echo "Every step is closed."; fi
    exit 0
  fi
  echo "Next step: $NEXT_KEY  $NEXT_TITLE"
  echo "Playbook:  $NEXT_FILE, line $NEXT_LINE"
  echo "Read, for this step only:"
  OLDIFS="$IFS"; IFS=";"
  for entry in $NEXT_READ; do
    IFS="$OLDIFS"
    entry="$(trim "$entry")"
    [ -n "$entry" ] && echo "  - $(resolve_read "$entry")"
    IFS=";"
  done
  IFS="$OLDIFS"
  echo "Produces:  $NEXT_PROD"
  echo "Check:     $NEXT_CHECK"
  if [ -n "$NEXT_SKIP" ]; then echo "Skip when: $NEXT_SKIP"; else echo "Skip when: never"; fi
  UNIT_ARG=""; [ -n "$UNIT" ] && UNIT_ARG=" --unit $UNIT"
  if [ -n "$(check_evidence "$NEXT_CHECK")" ]; then echo "Close it:  $SELF --close $NEXT_ID$UNIT_ARG --evidence \"<what the check asks for>\""
  else echo "Close it:  $SELF --close $NEXT_ID$UNIT_ARG"; fi
  [ "$PROJECT_CHECKS_WAITING" = "1" ] && echo "Note:      closed steps that ran the project's own commands are re-run when a step closes, or now with --verify."
  exit 0
fi

# --close and --skip
if [ -z "$ID" ]; then echo "Name the step: --close ID or --skip ID."; exit 1; fi
if [ -z "$NEXT_ID" ]; then
  if [ -n "$NEED_UNIT" ]; then echo "The playbook '$NEED_UNIT' repeats: add --unit NAME."; else echo "Every step is already closed."; fi
  exit 1
fi
if [ "$ID" != "$NEXT_ID" ]; then
  echo "Refused: the next open step is $NEXT_KEY ($NEXT_TITLE). Steps close in order."
  exit 1
fi
clean() { printf '%s' "$1" | tr '\n\r|' '   ' | sed -e 's/  */ /g' -e 's/^ //' -e 's/ $//'; }
REV="$(cd "$PROJECT_ROOT" && git rev-parse --short HEAD 2>/dev/null)"; [ -n "$REV" ] || REV="-"
TODAY="$(date +%F)"
append() { # a ledger without a final newline must not swallow the new line
  if [ -s "$LEDGER" ] && [ -n "$(tail -c 1 "$LEDGER")" ]; then printf '\n' >> "$LEDGER"; fi
  printf '%s\n' "$1" >> "$LEDGER"
}

if [ "$MODE" = "skip" ]; then
  if [ -z "$NEXT_SKIP" ]; then echo "Refused: $NEXT_KEY cannot be skipped; its playbook names no condition under which it does not apply."; exit 1; fi
  REASON="$(clean "$REASON")"
  if [ -z "$REASON" ]; then echo "Refused: this step is skipped only when: $NEXT_SKIP. Say with --reason how that holds here."; exit 1; fi
  append "- [-] $NEXT_KEY | $TODAY | rev $REV | skipped (allowed when: $(clean "$NEXT_SKIP")): $REASON"
  echo "Recorded: $NEXT_KEY skipped."
  exit 0
fi

EVIDENCE="$(clean "$EVIDENCE")"
CMD="$(check_command "$NEXT_CHECK")"
if [ -n "$CMD" ]; then
  if ! valid_command "$CMD" || ! command_exists "$CMD"; then echo "Refused: the playbook's check '$CMD' cannot be run (run --lint in the engine)."; exit 1; fi
  WANTED="$(check_evidence "$NEXT_CHECK")"
  if [ -n "$WANTED" ] && [ -z "$EVIDENCE" ]; then echo "Refused: besides its command, $NEXT_KEY closes on evidence ($WANTED). Give it with --evidence."; exit 1; fi
  if ! run_check "$CMD"; then
    echo "Refused: $NEXT_KEY stays open, its check fails: $CMD"
    show_check_output
    exit 1
  fi
  RESULT="check passed: $CMD"
  [ -n "$EVIDENCE" ] && RESULT="$RESULT | evidence: $EVIDENCE"
else
  if [ -z "$EVIDENCE" ]; then echo "Refused: $NEXT_KEY closes on evidence ($(check_evidence "$NEXT_CHECK")). Give it with --evidence."; exit 1; fi
  RESULT="evidence: $EVIDENCE"
fi
append "- [x] $NEXT_KEY | $TODAY | rev $REV | $RESULT"
echo "Closed: $NEXT_KEY."
exit 0
