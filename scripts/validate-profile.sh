#!/bin/bash
# Validates the operating profile (PROFILE.md) and the deferrals that depend on it
# (TECHNICAL-DEBT.md entries with Kind: deferral). Convention #30.
# Run from the project root:  scripts/validate-profile.sh [--strict] [--declared]
#
# Checks:
#   1. PROFILE.md parses: the facts block (everything before the first "## " heading) holds
#      exactly the known keys, each once, each with a value in its enumeration, no template
#      placeholders left
#   2. The operating stage agrees with the facts: an isolated experiment has only the owner,
#      synthetic disposable data, no external effects, no reliance, no valuable records, no
#      commitments; a trial is not public, not relied upon, and has a fallback not recorded as no;
#      regulated data contradicts synthetic-only data
#   3. Deferrals are readable and well-formed: an entry starts at a heading whose text begins
#      "TD-"; its fields are read in the common written forms (a list item or a plain line, the
#      label bold or not, the value after the colon). A deferral names its Control and its
#      Due-before trigger or date; a floor item is never postponed. An entry the parser cannot read
#      (a field given two values, a Kind that is neither shortcut nor deferral, entries hidden by a
#      code fence that never closes) is UNVERIFIED, which --strict fails; it never passes.
#   4. Triggered deferrals fail: a Due-before trigger the facts make true, or a Due-before date
#      reached (inclusive), blocks until the entry is fixed; won't-fix does not clear it
#   5. A Review-by date in the past warns; Review-by and Closure-evidence are optional
#
# Result words: OK, FAIL, WARN, plus DEFERRED (a deferral whose trigger is not yet true) and
# UNVERIFIED (a fact recorded as unknown, a trigger resting on one, or an entry the parser cannot read).
# Profile source: "declared" when PROFILE.md exists, "missing" otherwise. A missing profile is read
# as the strictest profile (operational, every fact unknown) with a WARN; a deferral that cannot be
# evaluated without a profile is a FAIL, so never creating the file is not a way around deferrals.
# --strict (or VALIDATE_PROFILE_STRICT=1): every UNVERIFIED result is an error too. Use it before
# any action that changes exposure and in maintenance of operational projects.
# --declared: PROFILE.md must exist; a missing profile is a FAIL, not a WARN. The bootstrap step
# that produces the profile closes on this (bootstrap/ONBOARD.md Step 4.3).
# Exit 1 when any check FAILs; 0 otherwise.
# This script reads declared facts. It observes nothing about users, data, or money, cannot tell
# whether a stated fact is true, and has no memory of earlier profiles.

# Text is read as bytes, the same on every system: in a UTF-8 locale the macOS awk exits on a
# character that substr cut in two, and the macOS grep, sed and tr fail on bytes that are not UTF-8.
export LC_ALL=C

STRICT="${VALIDATE_PROFILE_STRICT:-0}"
DECLARED=0
for arg in "$@"; do
  case "$arg" in
    --strict) STRICT=1 ;;
    --declared) DECLARED=1 ;;
    -h|--help) sed -n '2,35p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $arg (accepted: --strict, --declared)"; exit 2 ;;
  esac
done

PROJECT_ROOT="$(pwd)"
PROFILE="$PROJECT_ROOT/PROFILE.md"
# One PROFILE.md per repository (#30). An endpoint folder of a fullstack layout has none of its
# own: look above it, as far as the repository's top folder, or one folder up where the endpoints
# are repositories of their own.
if [ ! -f "$PROFILE" ]; then
  TOP="$(cd "$PROJECT_ROOT" && git rev-parse --show-toplevel 2>/dev/null)"
  d="$PROJECT_ROOT"
  while [ -n "$TOP" ] && [ "$d" != "$TOP" ] && [ "$d" != "/" ]; do
    d="$(dirname "$d")"
    if [ -f "$d/PROFILE.md" ]; then PROFILE="$d/PROFILE.md"; break; fi
  done
  if [ ! -f "$PROFILE" ] && [ -f "$(dirname "$PROJECT_ROOT")/PROFILE.md" ]; then PROFILE="$(dirname "$PROJECT_ROOT")/PROFILE.md"; fi
fi
TD="$PROJECT_ROOT/TECHNICAL-DEBT.md"
TODAY="${VALIDATE_PROFILE_TODAY:-$(date +%Y-%m-%d)}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0
WARNINGS=0
DEFERRALS=0
UNKNOWNS=0

fail()  { printf "${RED}FAIL${NC}: %s\n" "$1"; ERRORS=$((ERRORS + 1)); }
warn()  { printf "${YELLOW}WARN${NC}: %s\n" "$1"; WARNINGS=$((WARNINGS + 1)); }
pass()  { printf "${GREEN}OK${NC}: %s\n" "$1"; }
defer() { printf "${BLUE}DEFERRED${NC}: %s\n" "$1"; DEFERRALS=$((DEFERRALS + 1)); }
unver() { printf "${YELLOW}UNVERIFIED${NC}: %s\n" "$1"; UNKNOWNS=$((UNKNOWNS + 1)); }
group() { printf "\n[%s] %s\n" "$1" "$2"; }

echo "Operating Profile Check"
echo "Project: $PROJECT_ROOT"
echo "Today: $TODAY"
[ "$STRICT" = "1" ] && echo "Mode: strict (unverified counts as error)"

# Vocabulary. templates/profile.md and templates/technical-debt.md carry the same words;
# validate-framework.sh checks that they agree with this script.
TRIGGERS="first-outside-participant public-access real-data personal-data real-money-or-external-action operational-reliance valuable-records second-contributor regulated-data-or-commitment trial-stage operational-stage"
STAGES="isolated trial operational"
FLOOR="secrets trust-boundary irreversible-effects personal-data authorized-reuse honest-completion"
KEYS=("Schema" "Operating stage" "Stage reason" "Decision authority" "Authority source" "Audience" "Data" "External effects" "Operational reliance" "Valuable records" "Fallback" "Contributors" "Regulated data" "Customer commitments" "Monthly running-cost ceiling" "AI spend envelope" "Observed-on" "Review")

is_date() {
  # A real calendar date in YYYY-MM-DD form.
  [[ "$1" =~ ^([0-9]{4})-([0-9]{2})-([0-9]{2})$ ]] || return 1
  local y=$((10#${BASH_REMATCH[1]})) m=$((10#${BASH_REMATCH[2]})) d=$((10#${BASH_REMATCH[3]})) dim=31
  [ "$m" -ge 1 ] && [ "$m" -le 12 ] || return 1
  case "$m" in
    4|6|9|11) dim=30 ;;
    2) dim=28; if [ $((y % 4)) -eq 0 ] && { [ $((y % 100)) -ne 0 ] || [ $((y % 400)) -eq 0 ]; }; then dim=29; fi ;;
  esac
  [ "$d" -ge 1 ] && [ "$d" -le "$dim" ]
}
in_list() { local w; for w in $2; do [ "$w" = "$1" ] && return 0; done; return 1; }
is_trigger() { in_list "$1" "$TRIGGERS"; }
is_known_key() { local k; for k in "${KEYS[@]}"; do [ "$k" = "$1" ] && return 0; done; return 1; }

# The facts block is everything before the first "## " heading. Plain awk on the file, so the
# reader does not depend on the shell's grep.
get() {
  awk -v k="$1" '{ sub(/\r$/, "") } /^## / { exit } index($0, "- " k ":") == 1 { v = substr($0, length(k) + 4); sub(/^[ \t]+/, "", v); sub(/[ \t]+$/, "", v); print v; exit }' "$PROFILE"
}
count_key() { awk -v k="$1" '{ sub(/\r$/, "") } /^## / { exit } index($0, "- " k ":") == 1 { n++ } END { print n + 0 }' "$PROFILE"; }
fact_keys() { awk '{ sub(/\r$/, "") } /^## / { exit } /^- [^:]+:/ { s = $0; sub(/^- /, "", s); sub(/:.*/, "", s); print s }' "$PROFILE"; }

check_enum() {
  # $1 key, $2 value, $3 allowed words (space separated)
  [ -z "$2" ] && return
  case "$2" in \[*) return ;; esac
  if ! in_list "$2" "$3"; then
    fail "PROFILE.md: \"$1\" is \"$2\"; allowed: ${3// /, }"
  fi
}

STAGE=""; AUTH=""; AUTHSRC=""; AUD=""; DATA=""; EFF=""; REL=""; VAL=""; FALLBACK=""; CONTRIB=""; REG=""; COMMIT=""; OBS=""; REVIEW=""
PROFILE_PRESENT=0

# ----------------------------------------------------------------------
group 1 "PROFILE.md parses"
# ----------------------------------------------------------------------
if [ ! -f "$PROFILE" ]; then
  echo "Profile source: missing"
  [ "$DECLARED" = "1" ] && fail "PROFILE.md not found, and --declared requires it: create it from templates/profile.md (#30)"
  warn "PROFILE.md not found: reading the strictest profile (operational, every fact unknown). Create it from templates/profile.md (#30)."
  STAGE="operational"; AUTH="unknown"; AUTHSRC="unknown"; AUD="unknown"; DATA="unknown"; EFF="unknown"; REL="unknown"
  VAL="unknown"; FALLBACK="unknown"; CONTRIB="unknown"; REG="unknown"; COMMIT="unknown"
else
  echo "Profile source: declared"
  [ "$PROFILE" = "$PROJECT_ROOT/PROFILE.md" ] || echo "Profile file: $PROFILE (above this folder)"
  PROFILE_PRESENT=1
  BEFORE=$ERRORS

  # Every "- Key: value" line in the facts block must be a known key.
  FACT_LINES="$(fact_keys)"
  if [ -z "$FACT_LINES" ]; then
    fail "PROFILE.md has no facts block: the '- Key: value' lines must come before the first '## ' heading"
  fi
  while IFS= read -r key; do
    [ -z "$key" ] && continue
    is_known_key "$key" || fail "PROFILE.md: unknown key \"$key\""
  done <<< "$FACT_LINES"

  [ -n "$FACT_LINES" ] && for k in "${KEYS[@]}"; do
    n="$(count_key "$k")"
    if [ "$n" -gt 1 ]; then
      fail "PROFILE.md: key \"$k\" appears $n times; exactly once"
      continue
    fi
    v="$(get "$k")"
    if [ -z "$v" ]; then
      fail "PROFILE.md: missing or empty key \"$k\""
    else
      case "$v" in
        \[*) fail "PROFILE.md: \"$k\" still holds the template placeholder; fill it in" ;;
      esac
    fi
  done

  SCHEMA="$(get Schema)"
  STAGE="$(get 'Operating stage')"; AUTH="$(get 'Decision authority')"; AUTHSRC="$(get 'Authority source')"
  AUD="$(get Audience)"; DATA="$(get Data)"; EFF="$(get 'External effects')"
  REL="$(get 'Operational reliance')"; VAL="$(get 'Valuable records')"; FALLBACK="$(get Fallback)"
  CONTRIB="$(get Contributors)"; REG="$(get 'Regulated data')"; COMMIT="$(get 'Customer commitments')"
  OBS="$(get Observed-on)"; REVIEW="$(get Review)"

  [ -n "$SCHEMA" ] && [ "$SCHEMA" != "1" ] && fail "PROFILE.md: Schema is \"$SCHEMA\"; this validator reads schema 1"
  check_enum "Operating stage" "$STAGE" "$STAGES"
  check_enum "Decision authority" "$AUTH" "owner-decides ai-decides"
  check_enum "Authority source" "$AUTHSRC" "owner-stated defaulted"
  check_enum "Audience" "$AUD" "owner-only identified-participants public unknown"
  check_enum "Data" "$DATA" "synthetic-disposable real-nonpersonal personal unknown"
  check_enum "Operational reliance" "$REL" "yes no unknown"
  check_enum "Valuable records" "$VAL" "yes no unknown"
  check_enum "Fallback" "$FALLBACK" "yes no unknown"
  check_enum "Contributors" "$CONTRIB" "one several unknown"
  check_enum "Regulated data" "$REG" "yes no unknown"
  check_enum "Customer commitments" "$COMMIT" "yes no unknown"
  if [ -n "$EFF" ]; then
    case "$EFF" in
      \[*|none|unknown) ;;
      *)
        if [[ "$EFF" == ,* ]] || [[ "$EFF" == *, ]] || [[ "$EFF" == *,,* ]]; then
          fail "PROFILE.md: \"External effects\" contains an empty item; write none, unknown, or a comma-separated list"
        else
          IFS=',' read -ra EFF_PARTS <<< "$EFF"
          for part in "${EFF_PARTS[@]}"; do
            w="${part#"${part%%[![:space:]]*}"}"; w="${w%"${w##*[![:space:]]}"}"
            if [ -z "$w" ]; then
              fail "PROFILE.md: \"External effects\" contains an empty item; write none, unknown, or a comma-separated list"
            elif ! in_list "$w" "money messages records health-safety-access"; then
              fail "PROFILE.md: \"External effects\" lists \"$w\"; allowed: none, unknown, or any of money, messages, records, health-safety-access"
            fi
          done
        fi ;;
    esac
  fi
  if [ -n "$OBS" ]; then
    case "$OBS" in \[*) ;; *) is_date "$OBS" || fail "PROFILE.md: \"Observed-on\" is \"$OBS\"; expected a real calendar date YYYY-MM-DD" ;; esac
  fi
  if [ -n "$REVIEW" ]; then
    case "$REVIEW" in
      \[*) ;;
      *) if ! is_date "$REVIEW" && ! is_trigger "$REVIEW"; then
           fail "PROFILE.md: \"Review\" is \"$REVIEW\"; expected a real calendar date YYYY-MM-DD or a trigger name"
         fi ;;
    esac
  fi
  [ "$ERRORS" -eq "$BEFORE" ] && pass "PROFILE.md parses (operating stage $STAGE, decision authority $AUTH, $AUTHSRC)"
fi

for pair in "Audience=$AUD" "Data=$DATA" "External effects=$EFF" "Operational reliance=$REL" "Valuable records=$VAL" "Fallback=$FALLBACK" "Contributors=$CONTRIB" "Regulated data=$REG" "Customer commitments=$COMMIT"; do
  k="${pair%%=*}"; v="${pair#*=}"
  [ "$v" = "unknown" ] && unver "PROFILE.md: \"$k\" is unknown; learn it before any action that depends on it"
done

# ----------------------------------------------------------------------
group 2 "Operating stage agrees with the facts"
# ----------------------------------------------------------------------
BEFORE=$ERRORS
if [ "$PROFILE_PRESENT" -eq 1 ] && in_list "$STAGE" "$STAGES"; then
  if [ "$STAGE" = "isolated" ]; then
    case "$AUD" in identified-participants|public) fail "Operating stage is isolated but Audience is $AUD" ;; esac
    case "$DATA" in real-nonpersonal|personal) fail "Operating stage is isolated but Data is $DATA" ;; esac
    case "$EFF" in none|unknown|"") ;; *) fail "Operating stage is isolated but External effects is \"$EFF\"" ;; esac
    [ "$REL" = "yes" ] && fail "Operating stage is isolated but Operational reliance is yes"
    [ "$VAL" = "yes" ] && fail "Operating stage is isolated but Valuable records is yes"
    [ "$COMMIT" = "yes" ] && fail "Operating stage is isolated but Customer commitments is yes"
  elif [ "$STAGE" = "trial" ]; then
    [ "$AUD" = "public" ] && fail "Operating stage is trial but Audience is public"
    [ "$REL" = "yes" ] && fail "Operating stage is trial but Operational reliance is yes"
    [ "$FALLBACK" = "no" ] && fail "Operating stage is trial but Fallback is no; a trial needs a workable fallback"
  fi
  if [ "$REG" = "yes" ] && [ "$DATA" = "synthetic-disposable" ]; then
    fail "Regulated data is yes but Data is synthetic-disposable; regulated data is real data"
  fi
  [ "$ERRORS" -eq "$BEFORE" ] && pass "operating stage $STAGE is consistent with the recorded facts"
elif [ "$PROFILE_PRESENT" -eq 0 ]; then
  pass "no profile: strictest reading (operational, facts unknown) applied"
else
  warn "stage not checked against the facts because it did not parse"
fi

# ----------------------------------------------------------------------
# Trigger evaluation from the recorded facts: true, false, or unknown.
# ----------------------------------------------------------------------
yn() { case "$1" in yes) echo true ;; no) echo false ;; *) echo unknown ;; esac; }
trigger_state() {
  case "$1" in
    first-outside-participant) case "$AUD" in identified-participants|public) echo true ;; owner-only) echo false ;; *) echo unknown ;; esac ;;
    public-access) case "$AUD" in public) echo true ;; owner-only|identified-participants) echo false ;; *) echo unknown ;; esac ;;
    real-data) case "$DATA" in real-nonpersonal|personal) echo true ;; synthetic-disposable) echo false ;; *) echo unknown ;; esac ;;
    personal-data) case "$DATA" in personal) echo true ;; synthetic-disposable|real-nonpersonal) echo false ;; *) echo unknown ;; esac ;;
    real-money-or-external-action) case "$EFF" in none) echo false ;; unknown|"") echo unknown ;; *) echo true ;; esac ;;
    operational-reliance) if [ "$STAGE" = "operational" ]; then echo true; else yn "$REL"; fi ;;
    valuable-records) yn "$VAL" ;;
    second-contributor) case "$CONTRIB" in several) echo true ;; one) echo false ;; *) echo unknown ;; esac ;;
    regulated-data-or-commitment)
      if [ "$REG" = "yes" ] || [ "$COMMIT" = "yes" ]; then echo true
      elif [ "$REG" = "no" ] && [ "$COMMIT" = "no" ]; then echo false
      else echo unknown; fi ;;
    trial-stage) case "$STAGE" in trial|operational) echo true ;; *) echo false ;; esac ;;
    operational-stage) if [ "$STAGE" = "operational" ]; then echo true; else echo false; fi ;;
    *) echo invalid ;;
  esac
}

# ----------------------------------------------------------------------
group 3 "Deferrals are well-formed and not yet due"
# ----------------------------------------------------------------------
US=$'\x1f'
first_word() { printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sed -e 's/^[^a-z]*//' -e 's/[^a-z-].*$//'; }
if [ ! -f "$TD" ]; then
  pass "no TECHNICAL-DEBT.md, so no deferrals to check"
else
  BEFORE=$ERRORS
  UNREAD_BEFORE=$UNKNOWNS
  SEEN=0
  SEEN_IDS=" "
  PARSER_EXIT=""
  while IFS="$US" read -r id status kind control due review closure conflicts; do
    [ -z "$id" ] && continue
    # The parser's exit status arrives as the last record; a parser that stopped early has read only
    # part of the file, and what it did not read must not pass as "no deferrals".
    if [ "$id" = "PARSER-EXIT" ]; then PARSER_EXIT="$status"; continue; fi
    if [ "$id" = "UNCLOSED-FENCE" ]; then
      unver "TECHNICAL-DEBT.md has a code fence that never closes (opened at line $status); the entries after it could not be read"
      continue
    fi
    ENTRY_ERRORS=$ERRORS
    PENDING_DEFER=""
    case "$SEEN_IDS" in
      *" $id "*) warn "$id appears more than once in TECHNICAL-DEBT.md; give each entry its own id" ;;
      *) SEEN_IDS="$SEEN_IDS$id " ;;
    esac
    if [ -n "$conflicts" ]; then
      unver "$id: field(s) given two different values:$conflicts; this entry cannot be read until one value remains"
      continue
    fi
    kind_w="$(first_word "$kind")"
    status_w="$(first_word "$status")"
    # The Control of every open entry that declares one is read, whatever its Kind: a floor item is
    # never postponed (#30).
    if [ -n "$control" ] && [ "$status_w" != "fixed" ]; then
      lc_control="$(printf '%s' "$control" | tr '[:upper:]' '[:lower:]' | sed -E 's/[[:space:]]*:[[:space:]]*/:/; s/^[[:space:]]+//; s/[[:space:]]+$//')"
      case "$lc_control" in
        \[*) warn "$id: Control still holds a template placeholder" ;;
        floor|floor:) unver "$id: Control says floor but names no floor item; floor items: ${FLOOR// /, }" ;;
        floor:*)
          item="${lc_control#floor:}"; item="${item%% *}"
          if in_list "$item" "$FLOOR"; then
            fail "$id: a floor item ($item) is never postponed, as a deferral or as a shortcut (#30)"
          else
            unver "$id: Control names an unknown floor item \"$item\"; floor items: ${FLOOR// /, }"
          fi ;;
        '#'[0-9]*|b[0-9]*) ;;
        *) warn "$id: Control is \"$control\"; name the convention (#N and the obligation), the backend rule (BN), or the floor item (floor: name), so a review can see what is postponed" ;;
      esac
    fi
    case "$kind_w" in
      shortcut) continue ;;
      deferral) ;;
      '')
        if [ -n "$due" ]; then
          unver "$id carries a Due-before but no Kind; say whether it is a deferral or a shortcut"
        fi
        continue ;;
      *) unver "$id: Kind is \"$kind\", neither shortcut nor deferral; this entry cannot be read"; continue ;;
    esac
    SEEN=$((SEEN + 1))
    [ "$status_w" = "fixed" ] && continue
    [ -z "$control" ] && fail "$id: deferral without Control; name what is postponed"
    if [ -z "$due" ]; then
      fail "$id: deferral without Due-before; name the trigger or the date that ends it"
      continue
    fi
    if [ "$PROFILE_PRESENT" -eq 0 ]; then
      fail "$id: a deferral cannot be evaluated without PROFILE.md; create the profile or fix the entry"
      continue
    fi
    due_w="$(printf '%s' "$due" | sed -e 's/^[[:space:]`*_]*//' -e 's/[[:space:]`*_.,;]*$//')"
    if is_date "$due_w"; then
      if [[ "$due_w" < "$TODAY" ]] || [ "$due_w" = "$TODAY" ]; then
        fail "$id: Due-before date $due_w reached; the deferral is blocking until fixed (status: ${status:-open})"
      else
        PENDING_DEFER="$id until $due_w"
      fi
    elif is_trigger "$due_w"; then
      state="$(trigger_state "$due_w")"
      case "$state" in
        true) fail "$id: trigger $due_w is true per PROFILE.md; the deferral is blocking until fixed (status: ${status:-open}; won't-fix does not clear it)" ;;
        false) PENDING_DEFER="$id until $due_w" ;;
        unknown) unver "$id is due before $due_w, which rests on a fact recorded as unknown" ;;
      esac
    else
      fail "$id: Due-before \"$due\" is neither a known trigger nor a date. Triggers: ${TRIGGERS// /, }"
    fi
    if [ -n "$review" ]; then
      review_w="$(printf '%s' "$review" | sed -e 's/^[[:space:]`*_]*//' -e 's/[[:space:]`*_.,;]*$//')"
      if is_date "$review_w"; then
        if [[ "$review_w" < "$TODAY" ]]; then warn "$id: Review-by $review_w has passed; review it and write the new date with the reason"; fi
      else
        warn "$id: Review-by \"$review\" is not a calendar date YYYY-MM-DD"
      fi
    fi
    case "$closure" in \[*) warn "$id: Closure-evidence still holds a template placeholder" ;; esac
    # The DEFERRED line is printed only for an entry that passed every check above.
    if [ -n "$PENDING_DEFER" ] && [ "$ERRORS" -eq "$ENTRY_ERRORS" ]; then defer "$PENDING_DEFER"; fi
  done < <(awk -v US="$US" '
    # An entry starts at a heading whose text begins "TD-" and runs to the next such heading or a
    # level-one heading. A field is a line whose label, with or without a list marker and with or
    # without bold, italic or code marks around it, is one of the six names below, followed by a
    # colon; "due before", "review by" and "closure evidence" may be written with a space. Every
    # other line is left alone. A field written twice with two different values is reported, so the
    # shell can count the entry as unreadable.
    function trim(s) { sub(/^[ \t]+/, "", s); sub(/[ \t]+$/, "", s); return s }
    function flush() {
      if (id != "") printf "%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n", id, US, f["status"], US, f["kind"], US, f["control"], US, f["due-before"], US, f["review-by"], US, f["closure-evidence"], US, conflicts
    }
    function reset() { id = ""; conflicts = ""; split("", f); split("", seen) }
    { sub(/\r$/, "") }
    # Fenced examples are skipped: a fence opens with three or more backticks or tildes, indented
    # at most three spaces, and closes with a run of the same character at least as long.
    /^ ? ? ?(```|~~~)/ {
      body = $0; sub(/^ ? ? ?/, "", body)
      c = substr(body, 1, 1); n = 0
      while (substr(body, n + 1, 1) == c) n++
      rest = substr(body, n + 1)
      if (!infence) {
        if (!(c == "`" && rest ~ /`/)) { infence = 1; fchar = c; flen = n; fence_line = NR; next }
      }
      else if (c == fchar && n >= flen && rest ~ /^[ \t]*$/) { infence = 0; next }
      else next
    }
    infence { next }
    /^ ? ? ?#/ {
      h = $0; sub(/^ ? ? ?/, "", h)
      level = 0; while (substr(h, level + 1, 1) == "#") level++
      text = substr(h, level + 1); gsub(/[*_`]/, "", text); text = trim(text)
      if (toupper(substr(text, 1, 3)) == "TD-") {
        flush(); reset()
        id = "TD-" substr(text, 4); sub(/[^A-Za-z0-9-].*$/, "", id)
        next
      }
      if (level == 1) { flush(); reset() }
      next
    }
    id == "" { next }
    {
      low = tolower($0)
      if (match(low, /^[ \t]*(([-*+]|[0-9]+[.)])[ \t]+)?[*_`]*(status|kind|control|due[- ]before|review[- ]by|closure[- ]evidence)([*_`]*[ \t]*:|[ \t]*:[*_`]*)/)) {
        lab = substr(low, 1, RLENGTH)
        sub(/^[ \t]*(([-*+]|[0-9]+[.)])[ \t]+)?[*_`]*/, "", lab)
        sub(/[*_` \t]*:.*$/, "", lab)
        gsub(/ /, "-", lab)
        v = substr($0, RLENGTH + 1); sub(/^[*_` \t]+/, "", v); v = trim(v)
        if (lab in seen) { if (f[lab] != v && index(conflicts, " " lab) == 0) conflicts = conflicts " " lab }
        else { seen[lab] = 1; f[lab] = v }
      }
    }
    END { flush(); if (infence) printf "UNCLOSED-FENCE%s%d\n", US, fence_line }
  ' "$TD"; printf 'PARSER-EXIT%s%s\n' "$US" "$?")
  if [ "$PARSER_EXIT" != "0" ]; then
    fail "TECHNICAL-DEBT.md was not read to the end (the parser exited with status ${PARSER_EXIT:-unknown}); nothing after the point where it stopped was checked"
  elif [ "$SEEN" -eq 0 ] && [ "$ERRORS" -eq "$BEFORE" ] && [ "$UNKNOWNS" -eq "$UNREAD_BEFORE" ]; then
    pass "TECHNICAL-DEBT.md has no deferrals"
  elif [ "$ERRORS" -eq "$BEFORE" ] && [ "$UNKNOWNS" -eq "$UNREAD_BEFORE" ]; then
    pass "every deferral is well-formed and none is due"
  fi
fi

if [ "$STRICT" = "1" ] && [ "$UNKNOWNS" -gt 0 ]; then
  fail "strict mode: $UNKNOWNS unverified result(s) count as errors; learn the facts before the action"
fi

echo ""
echo "==="
echo "Deferred: $DEFERRALS   Unverified: $UNKNOWNS   Warnings: $WARNINGS   Errors: $ERRORS"
echo "Exit 0 means the recorded facts permit the current state; it does not mean production-ready."
if [ "$ERRORS" -gt 0 ]; then
  echo "$ERRORS profile violation(s)"
  exit 1
fi
exit 0
