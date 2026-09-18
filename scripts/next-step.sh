#!/bin/bash
# The step ledger's tool (development/STEPS.md). A playbook is a list of steps; a project's
# PROGRESS.md records which are closed. This script names the next open step and what to
# read for it, closes a step only when its check passes, and re-runs the checks of closed
# steps so a tick cannot outlive the thing it ticked.
#
# Run from the project root:
#   scripts/next-step.sh                          the next open step: what to read, what closes it
#   scripts/next-step.sh --list                   every step of the project's playbooks with its state
#   scripts/next-step.sh --close ID [--evidence TEXT]   close the next open step (its check must pass)
#   scripts/next-step.sh --skip ID --reason TEXT        record a step that does not apply
#   add --unit NAME for a playbook that repeats (one run of its steps per feature)
# Run from the engine:
#   scripts/next-step.sh --lint                   every stepped playbook is well formed (the self-test runs this)
#
# What it reads in a playbook: a "Step ledger: <id>" line (with "(per feature)" when the steps
# repeat), headings of the form "## Step N: Title" or "### Step N.M - Title", and inside each
# step the lines "Read:", "Produces:", "Check:", and optionally "Required: yes". A step with
# sub-steps (2 with 2.1, 2.2) is a container; only its sub-steps open and close.
#
# What it cannot do: tell whether a step was done well, whether quoted evidence is what the
# owner said, or stop anyone editing PROGRESS.md by hand. A check it can run, it re-runs.
#
# Exit 0: a next step was named, or everything is closed. Exit 1: refused, or a closed step's
# check now fails, or the lint found a fault.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENGINE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(pwd)"
LEDGER="$PROJECT_ROOT/PROGRESS.md"
SEP="$(printf '\037')"

case "$SCRIPT_DIR" in
  "$PROJECT_ROOT"/*) SELF="${SCRIPT_DIR#$PROJECT_ROOT/}/next-step.sh" ;;
  *) SELF="$SCRIPT_DIR/next-step.sh" ;;
esac

MODE="next"; ID=""; UNIT=""; EVIDENCE=""; REASON=""
while [ $# -gt 0 ]; do
  case "$1" in
    --lint) MODE="lint" ;;
    --list) MODE="list" ;;
    --close) MODE="close"; ID="$2"; shift ;;
    --skip) MODE="skip"; ID="$2"; shift ;;
    --unit) UNIT="$2"; shift ;;
    --evidence) EVIDENCE="$2"; shift ;;
    --reason) REASON="$2"; shift ;;
    *) echo "Unknown argument: $1 (see the head of $SELF)"; exit 1 ;;
  esac
  shift
done

# One line per step of every stepped playbook, fields separated by the unit separator:
# playbook id, once|unit, step id, title, file, line, Read, Produces, Check, Required,
# count of Read lines, of Produces lines, of Check lines, leaf|container.
steps_table() {
  for f in "$ENGINE_DIR"/bootstrap/*.md "$ENGINE_DIR"/scaffolding/*.md "$ENGINE_DIR"/development/*.md; do
    [ -f "$f" ] || continue
    grep -q '^Step ledger: ' "$f" || continue
    awk -v file="${f#$ENGINE_DIR/}" -v S="$SEP" '
      function flush() {
        if (sid != "") { n++; a_sid[n]=sid; a_title[n]=title; a_line[n]=line; a_rd[n]=rd; a_pr[n]=pr; a_ck[n]=ck; a_rq[n]=rq; a_rc[n]=rc; a_pc[n]=pc; a_cc[n]=cc }
        sid = ""
      }
      /^```/ { fence = !fence; next }
      fence { next }
      /^Step ledger: / { pid = $3; mode = ($0 ~ /\(per [a-z]+\)/) ? "unit" : "once"; next }
      /^###? Step / {
        flush()
        h = $0; sub(/^###? Step /, "", h)
        sid = h; sub(/[ :].*$/, "", sid)
        title = h; sub(/^[^ :]+:? */, "", title); sub(/^(—|-) */, "", title)
        line = NR; rd = ""; pr = ""; ck = ""; rq = "no"; rc = 0; pc = 0; cc = 0
        next
      }
      /^#+ / { flush(); next }
      sid != "" && /^Read: /     { rd = substr($0, 7);  rc++; next }
      sid != "" && /^Produces: / { pr = substr($0, 11); pc++; next }
      sid != "" && /^Check: /    { ck = substr($0, 8);  cc++; next }
      sid != "" && /^Required: / { rq = substr($0, 11); next }
      END {
        flush()
        if (n == 0) { print pid S mode S "" S "" S file S 0 S "" S "" S "" S "no" S 0 S 0 S 0 S "empty"; exit }
        for (i = 1; i <= n; i++) {
          kind = "leaf"
          for (j = 1; j <= n; j++) if (j != i && index(a_sid[j], a_sid[i] ".") == 1) kind = "container"
          print pid S mode S a_sid[i] S a_title[i] S file S a_line[i] S a_rd[i] S a_pr[i] S a_ck[i] S a_rq[i] S a_rc[i] S a_pc[i] S a_cc[i] S kind
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
valid_command() { printf '%s' "$1" | grep -qE '^scripts/[A-Za-z0-9._-]+\.(sh|py)( [-A-Za-z0-9=._ ]+)?$'; }

CHECK_OUT=""
run_check() {
  local cmd="$1" script args runner
  script="${cmd%% *}"; args=""
  [ "$script" != "$cmd" ] && args="${cmd#* }"
  case "$script" in *.py) runner="python3" ;; *) runner="bash" ;; esac
  # shellcheck disable=SC2086
  CHECK_OUT="$(cd "$PROJECT_ROOT" && $runner "$ENGINE_DIR/$script" $args 2>&1)"
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
  SEEN=""
  COUNT=0
  while IFS="$SEP" read -r pid mode sid title file line rd pr ck rq rc pc cc kind; do
    [ -n "$file" ] || continue
    if [ -z "$pid" ]; then bad "$file: the 'Step ledger:' line names no id, or comes after the first step"; continue; fi
    printf '%s' "$pid" | grep -qE '^[a-z][a-z0-9-]*$' || bad "$file: ledger id '$pid' must be lower-case letters, digits, and hyphens"
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
    [ "$rc" = "1" ] || bad "$where: needs exactly one 'Read:' line (found $rc); write 'Read: none' when nothing is read"
    [ "$pc" = "1" ] || bad "$where: needs exactly one 'Produces:' line (found $pc)"
    [ "$cc" = "1" ] || bad "$where: needs exactly one 'Check:' line (found $cc)"
    [ "$pc" = "1" ] && [ -z "$(trim "$pr")" ] && bad "$where: 'Produces:' is empty"
    case "$rq" in yes|no) ;; *) bad "$where: 'Required:' is yes or no, not '$rq'" ;; esac
    if [ "$rc" = "1" ]; then
      [ -z "$(trim "$rd")" ] && bad "$where: 'Read:' is empty; write none when nothing is read"
      OLDIFS="$IFS"; IFS=";"
      for entry in $rd; do
        IFS="$OLDIFS"
        entry="$(trim "$entry")"
        case "$entry" in
          ''|none|'project: '*) ;;
          '#'[0-9]*)
            r="$(resolve_read "$entry")"
            case "$r" in conventions/*) ;; *) bad "$where: Read names $entry and no convention file has that number" ;; esac ;;
          *)
            path="${entry%% § *}"
            [ -e "$ENGINE_DIR/$path" ] || bad "$where: Read names '$path', which is not in the engine (a project file is written 'project: <file>')" ;;
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
# Everything below works on a project.
if [ ! -f "$LEDGER" ]; then
  echo "No PROGRESS.md in $PROJECT_ROOT."
  echo "Copy ${SELF%scripts/next-step.sh}templates/progress.md to PROGRESS.md, fill its Playbooks line, and run this again."
  echo "For work that began before the ledger: close the finished steps one at a time, oldest first; each check still has to pass."
  exit 1
fi

PLAYBOOKS="$(tr -d '\r' < "$LEDGER" | sed -n 's/^- Playbooks:[[:space:]]*//p' | head -1)"
case "$PLAYBOOKS" in
  ''|'['*) echo "PROGRESS.md: fill the '- Playbooks:' line with the ledger ids this project follows, in order (run --lint in the engine to see them)."; exit 1 ;;
esac
TABLE="$(steps_table)"
CLOSED_LINES="$(tr -d '\r' < "$LEDGER" | grep -E '^- \[[x-]\] ')"
state_of() { # key -> closed | skipped | open
  local hit
  hit="$(printf '%s\n' "$CLOSED_LINES" | awk -v k="$1" '{ l = $0; sub(/^- \[.\] /, "", l); sub(/ *\|.*$/, "", l); if (l == k) { print substr($0, 4, 1); exit } }')"
  case "$hit" in x) echo closed ;; -) echo skipped ;; *) echo open ;; esac
}
key_of() { if [ "$2" = "unit" ]; then printf '%s @%s' "$1" "$UNIT"; else printf '%s' "$1"; fi; }

# Walk the project's playbooks in order. Sets NEXT_* to the first open leaf step.
NEXT_ID=""; NEED_UNIT=""
LISTING=""
OLDIFS="$IFS"; IFS=","
for pb in $PLAYBOOKS; do
  IFS="$OLDIFS"
  pb="$(trim "$pb")"
  [ -n "$pb" ] || { IFS=","; continue; }
  if ! printf '%s\n' "$TABLE" | awk -F"$SEP" -v p="$pb" '$1 == p { f = 1 } END { exit !f }'; then
    echo "PROGRESS.md names the playbook '$pb', and no playbook in the engine declares that ledger id."
    exit 1
  fi
  while IFS="$SEP" read -r pid mode sid title file line rd pr ck rq rc pc cc kind; do
    [ "$pid" = "$pb" ] && [ "$kind" = "leaf" ] || continue
    if [ "$mode" = "unit" ] && [ -z "$UNIT" ]; then NEED_UNIT="$pb"; continue; fi
    key="$(key_of "$pid.$sid" "$mode")"
    st="$(state_of "$key")"
    LISTING="$LISTING
$st  $key  $title"
    if [ "$st" = "open" ] && [ -z "$NEXT_ID" ]; then
      NEXT_ID="$pid.$sid"; NEXT_KEY="$key"; NEXT_TITLE="$title"; NEXT_FILE="$file"; NEXT_LINE="$line"
      NEXT_READ="$rd"; NEXT_PROD="$pr"; NEXT_CHECK="$ck"; NEXT_REQ="$rq"
    fi
  done <<EOF
$TABLE
EOF
  IFS=","
done
IFS="$OLDIFS"

if [ "$MODE" = "list" ]; then
  printf '%s\n' "$LISTING" | sed '/^$/d'
  [ -n "$NEED_UNIT" ] && echo "(the playbook '$NEED_UNIT' repeats: add --unit NAME to list one run of it)"
  exit 0
fi

# A closed step's check is run again, once per distinct command.
reverify() {
  local failed=0 done_cmds="" cmd key
  while IFS="$SEP" read -r pid mode sid title file line rd pr ck rq rc pc cc kind; do
    [ "$kind" = "leaf" ] || continue
    cmd="$(check_command "$ck")"
    [ -n "$cmd" ] || continue
    key="$(key_of "$pid.$sid" "$mode")"
    [ "$(state_of "$key")" = "closed" ] || continue
    case "
$done_cmds
" in *"
$cmd
"*) continue ;; esac
    done_cmds="$done_cmds
$cmd"
    if ! run_check "$cmd"; then
      failed=1
      echo "REOPENED: $key was closed, and its check now fails: $cmd"
      printf '%s\n' "$CHECK_OUT" | grep -E 'FAIL|Error' | head -8 | sed 's/^/    /'
    fi
  done <<EOF
$TABLE
EOF
  return $failed
}

if [ "$MODE" = "next" ]; then
  if ! reverify; then
    echo "Fix what failed, then run this again. No next step is named while a closed step's check fails."
    exit 1
  fi
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
  [ "$NEXT_REQ" = "yes" ] && echo "Required:  yes (it cannot be skipped)"
  UNIT_ARG=""; [ -n "$UNIT" ] && UNIT_ARG=" --unit \"$UNIT\""
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
  echo "Refused: the next open step is $NEXT_KEY ($NEXT_TITLE). Steps close in order; a step that does not apply is recorded with --skip and a reason."
  exit 1
fi
clean() { printf '%s' "$1" | tr '\n\r|' '   ' | sed -e 's/  */ /g' -e 's/^ //' -e 's/ $//'; }
REV="$(cd "$PROJECT_ROOT" && git rev-parse --short HEAD 2>/dev/null)"; [ -n "$REV" ] || REV="-"
TODAY="$(date +%F)"

if [ "$MODE" = "skip" ]; then
  if [ "$NEXT_REQ" = "yes" ]; then echo "Refused: $NEXT_KEY is required and cannot be skipped."; exit 1; fi
  REASON="$(clean "$REASON")"
  if [ -z "$REASON" ]; then echo "Refused: a skipped step records why it does not apply (--reason)."; exit 1; fi
  printf -- '- [-] %s | %s | rev %s | skipped: %s\n' "$NEXT_KEY" "$TODAY" "$REV" "$REASON" >> "$LEDGER"
  echo "Recorded: $NEXT_KEY skipped."
  exit 0
fi

EVIDENCE="$(clean "$EVIDENCE")"
CMD="$(check_command "$NEXT_CHECK")"
if [ -n "$CMD" ]; then
  if ! valid_command "$CMD" || [ ! -f "$ENGINE_DIR/${CMD%% *}" ]; then echo "Refused: the playbook's check '$CMD' cannot be run (run --lint in the engine)."; exit 1; fi
  if ! run_check "$CMD"; then
    echo "Refused: $NEXT_KEY stays open, its check fails: $CMD"
    printf '%s\n' "$CHECK_OUT" | grep -E 'FAIL|Error' | head -12 | sed 's/^/    /'
    exit 1
  fi
  RESULT="check passed: $CMD"
  [ -n "$EVIDENCE" ] && RESULT="$RESULT | evidence: $EVIDENCE"
else
  if [ -z "$EVIDENCE" ]; then echo "Refused: $NEXT_KEY closes on evidence (${NEXT_CHECK#evidence: }). Give it with --evidence."; exit 1; fi
  RESULT="evidence: $EVIDENCE"
fi
printf -- '- [x] %s | %s | rev %s | %s\n' "$NEXT_KEY" "$TODAY" "$REV" "$RESULT" >> "$LEDGER"
echo "Closed: $NEXT_KEY."
exit 0
