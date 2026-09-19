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

MODE="next"; ID=""; UNIT=""; EVIDENCE=""; REASON=""
while [ $# -gt 0 ]; do
  case "$1" in
    --lint) MODE="lint" ;;
    --list) MODE="list" ;;
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
# count of Read lines, of Produces lines, of Check lines, leaf|container|empty|malformed.
# A file whose only "Step ledger:" line sits inside a code fence declares nothing.
steps_table() {
  for f in "$ENGINE_DIR"/bootstrap/*.md "$ENGINE_DIR"/scaffolding/*.md "$ENGINE_DIR"/development/*.md; do
    [ -f "$f" ] || continue
    grep -q '^Step ledger: ' "$f" || continue
    awk -v file="${f#$ENGINE_DIR/}" -v S="$SEP" '
      function flush() {
        if (sid != "") { n++; a_sid[n]=sid; a_title[n]=title; a_line[n]=line; a_rd[n]=rd; a_pr[n]=pr; a_ck[n]=ck; a_sw[n]=sw; a_rc[n]=rc; a_pc[n]=pc; a_cc[n]=cc }
        sid = ""
      }
      { sub(/\r$/, "") }
      /^```/ { fence = !fence; next }
      fence { next }
      /^Step ledger: / { declared = 1; pid = $3; mode = ($0 ~ /\(per [a-z]+\)/) ? "unit" : "once"; next }
      /^###? Step [A-Za-z0-9][A-Za-z0-9.]*(:| )/ {
        flush()
        h = $0; sub(/^###? Step /, "", h)
        sid = h; sub(/[ :].*$/, "", sid)
        title = h; sub(/^[^ :]+:? */, "", title); sub(/^(—|-) */, "", title)
        line = NR; rd = ""; pr = ""; ck = ""; sw = ""; rc = 0; pc = 0; cc = 0
        next
      }
      /^#+[ \t]+Step([ \t:]|$)/ { flush(); m++; m_line[m] = NR; next }
      /^#+ / { flush(); next }
      sid != "" && /^Read: /      { rd = substr($0, 7);  rc++; next }
      sid != "" && /^Produces: /  { pr = substr($0, 11); pc++; next }
      sid != "" && /^Check: /     { ck = substr($0, 8);  cc++; next }
      sid != "" && /^Skip when: / { sw = substr($0, 12); next }
      END {
        if (!declared) exit
        flush()
        for (i = 1; i <= m; i++) print pid S mode S "" S "" S file S m_line[i] S "" S "" S "" S "" S 0 S 0 S 0 S "malformed"
        if (n == 0) { print pid S mode S "" S "" S file S 0 S "" S "" S "" S "" S 0 S 0 S 0 S "empty"; exit }
        for (i = 1; i <= n; i++) {
          kind = "leaf"
          for (j = 1; j <= n; j++) if (j != i && index(a_sid[j], a_sid[i] ".") == 1) kind = "container"
          print pid S mode S a_sid[i] S a_title[i] S file S a_line[i] S a_rd[i] S a_pr[i] S a_ck[i] S a_sw[i] S a_rc[i] S a_pc[i] S a_cc[i] S kind
        }
      }' "$f"
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

# The check's command, when the check is one: "run scripts/x.sh --flag" gives "scripts/x.sh --flag".
check_command() { case "$1" in 'run '*) printf '%s' "${1#run }" ;; esac; }
valid_command() {
  printf '%s' "$1" | grep -qE '^scripts/[A-Za-z0-9._-]+\.(sh|py)( [-A-Za-z0-9=._/ ]+)?$' || return 1
  case " ${1#* }" in *' /'*|*'..'*) return 1 ;; esac
  return 0
}

CHECK_OUT=""
run_check() {
  local cmd="$1" script args runner
  script="${cmd%% *}"; args=""
  [ "$script" != "$cmd" ] && args="${cmd#* }"
  case "$script" in *.py) runner="python3" ;; *) runner="bash" ;; esac
  # shellcheck disable=SC2086
  CHECK_OUT="$(cd "$PROJECT_ROOT" && $runner "$ENGINE_DIR/$script" $args 2>&1)"
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
  SEEN=""; OWNERS=""; COUNT=0; DUP_TOLD=""
  while IFS="$SEP" read -r pid mode sid title file line rd pr ck sw rc pc cc kind; do
    [ -n "$file" ] || continue
    if [ -z "$pid" ]; then bad "$file: the 'Step ledger:' line names no id"; continue; fi
    printf '%s' "$pid" | grep -qE '^[a-z][a-z0-9-]*$' || bad "$file: ledger id '$pid' must be lower-case letters, digits, and hyphens"
    other="$(printf '%s\n' "$OWNERS" | awk -F"$SEP" -v p="$pid" -v f="$file" '$1 == p && $2 != f { print $2; exit }')"
    if [ -n "$other" ]; then
      case " $DUP_TOLD " in *" $pid "*) ;; *) bad "$file: ledger id '$pid' is also declared by $other; one playbook per id"; DUP_TOLD="$DUP_TOLD $pid" ;; esac
      continue
    fi
    OWNERS="$OWNERS
$pid$SEP$file"
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
            case "$r" in conventions/*) ;; *) bad "$where: Read names $entry and no convention file has that number" ;; esac ;;
          *)
            path="${entry%% § *}"
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
          if ! valid_command "$cmd"; then bad "$where: Check runs '$cmd'; only an engine script under scripts/ with plain arguments can be run"
          elif [ ! -f "$ENGINE_DIR/${cmd%% *}" ]; then bad "$where: Check runs ${cmd%% *}, which does not exist"
          fi ;;
        'evidence: '?*) ;;
        *) bad "$where: Check is 'run scripts/<script> [arguments]' or 'evidence: <what is recorded, in whose words>'" ;;
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
while IFS="$SEP" read -r pid mode sid title file line rd pr ck sw rc pc cc kind; do
  [ "$kind" = "leaf" ] || continue
  cmd="$(check_command "$ck")"
  [ -n "$cmd" ] || continue
  keys="$(closed_keys_of "$pid.$sid")"
  [ -n "$keys" ] || continue
  keys_line="$(printf '%s' "$keys" | tr '\n' ',' | sed 's/,/, /g')"
  if ! valid_command "$cmd" || [ ! -f "$ENGINE_DIR/${cmd%% *}" ]; then
    REVERIFY_OK=0
    FAILED_KEYS="$FAILED_KEYS
$keys"
    echo "REOPENED: $keys_line: the playbook's check '$cmd' is not an engine script that can be run (run --lint in the engine)"
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
  case "$NEXT_CHECK" in
    'run '*) echo "Close it:  $SELF --close $NEXT_ID$UNIT_ARG" ;;
    *)       echo "Close it:  $SELF --close $NEXT_ID$UNIT_ARG --evidence \"<what the check asks for>\"" ;;
  esac
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
  if ! valid_command "$CMD" || [ ! -f "$ENGINE_DIR/${CMD%% *}" ]; then echo "Refused: the playbook's check '$CMD' cannot be run (run --lint in the engine)."; exit 1; fi
  if ! run_check "$CMD"; then
    echo "Refused: $NEXT_KEY stays open, its check fails: $CMD"
    show_check_output
    exit 1
  fi
  RESULT="check passed: $CMD"
  [ -n "$EVIDENCE" ] && RESULT="$RESULT | evidence: $EVIDENCE"
else
  if [ -z "$EVIDENCE" ]; then echo "Refused: $NEXT_KEY closes on evidence (${NEXT_CHECK#evidence: }). Give it with --evidence."; exit 1; fi
  RESULT="evidence: $EVIDENCE"
fi
append "- [x] $NEXT_KEY | $TODAY | rev $REV | $RESULT"
echo "Closed: $NEXT_KEY."
exit 0
