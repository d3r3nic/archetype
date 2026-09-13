#!/bin/bash
# Validates the operating profile (PROFILE.md) and the deferrals that depend on it
# (TECHNICAL-DEBT.md entries with Kind: deferral). Convention #30.
# Run from the project root:  scripts/validate-profile.sh [--strict]
#
# Checks:
#   1. PROFILE.md parses: the facts block (everything before the first "## " heading) holds
#      exactly the known keys, each once, each with a value in its enumeration, no template
#      placeholders left
#   2. The operating stage agrees with the facts: an isolated experiment has only the owner,
#      synthetic disposable data, no external effects, no reliance, no valuable records, no
#      commitments; a trial is not public, not relied upon, and has a fallback not recorded as no;
#      regulated data contradicts synthetic-only data
#   3. Deferrals are well-formed: Kind: deferral needs Control, Due-before, Review-by, and
#      Closure-evidence; Control names a convention, a backend rule, or a floor item; Due-before is
#      a known trigger or a real date; a floor item is never a deferral; each of the six fields this
#      script reads (Status, Kind, Control, Due-before, Review-by, Closure-evidence) appears once
#      per entry and the first value wins; a Kind line with no value fails; ids are unique; an entry
#      runs from its "## TD-" heading to the next one or a level-one heading; a TD heading of any
#      other shape (another level, no space, underlined) fails if it carries entry fields and
#      warns otherwise; a field is a list item with a bold label and the value on the same line;
#      a field label written in another recognizable shape fails rather than vanishing; any other
#      line inside an entry that mentions a field name warns as a possible unread field; fenced
#      examples are skipped with fence length respected, and an unclosed code fence fails (it would
#      hide every entry after it)
#   The contract is the documented format. The parser recognizes many deviations and fails them; it
#   does not parse arbitrary Markdown or HTML, so a deviation it cannot recognize is caught only by the
#   warning above and by review.
#   4. Triggered deferrals fail: a Due-before trigger the facts make true, or a Due-before date
#      reached (inclusive), blocks until the entry is fixed; won't-fix does not clear it
#   5. A Review-by date in the past warns
#
# Result words: OK, FAIL, WARN, plus DEFERRED (a deferral whose trigger is not yet true) and
# UNVERIFIED (a fact recorded as unknown, or a trigger resting on one).
# Profile source: "declared" when PROFILE.md exists, "missing" otherwise. A missing profile is read
# as the strictest profile (operational, every fact unknown) with a WARN; a deferral that cannot be
# evaluated without a profile is a FAIL, so never creating the file is not a way around deferrals.
# --strict (or VALIDATE_PROFILE_STRICT=1): every UNVERIFIED result is an error too. Use it before
# any action that changes exposure and in maintenance of operational projects.
# Exit 1 when any check FAILs; 0 otherwise.
# This script reads declared facts. It observes nothing about users, data, or money, cannot tell
# whether a stated fact is true, and has no memory of earlier profiles.

STRICT="${VALIDATE_PROFILE_STRICT:-0}"
for arg in "$@"; do
  case "$arg" in
    --strict) STRICT=1 ;;
    -h|--help) sed -n '2,28p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $arg (accepted: --strict)"; exit 2 ;;
  esac
done

PROJECT_ROOT="$(pwd)"
PROFILE="$PROJECT_ROOT/PROFILE.md"
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
  warn "PROFILE.md not found: reading the strictest profile (operational, every fact unknown). Create it from templates/profile.md (#30)."
  STAGE="operational"; AUTH="unknown"; AUTHSRC="unknown"; AUD="unknown"; DATA="unknown"; EFF="unknown"; REL="unknown"
  VAL="unknown"; FALLBACK="unknown"; CONTRIB="unknown"; REG="unknown"; COMMIT="unknown"
else
  echo "Profile source: declared"
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
if [ ! -f "$TD" ]; then
  pass "no TECHNICAL-DEBT.md, so no deferrals to check"
else
  BEFORE=$ERRORS
  SEEN=0
  SUPPRESS_PASS=0
  SEEN_IDS=" "
  while IFS="$US" read -r id status kind control due review closure dups strays kindpresent metapresent mentions; do
    [ -z "$id" ] && continue
    ENTRY_ERRORS=$ERRORS
    PENDING_DEFER=""
    if [ "$id" = "UNCLOSED-FENCE" ]; then
      fail "TECHNICAL-DEBT.md has a code fence that never closes (opened at line $status); every entry after it is hidden from this check"
      SUPPRESS_PASS=1
      continue
    fi
    if [ "$id" = "ODD-HEADING" ]; then
      if [ "$kind" = "1" ]; then
        fail "TECHNICAL-DEBT.md: \"$status\" carries entry fields but is not a level-two heading, so it would not be checked; entries start with \"## TD-\""
        SUPPRESS_PASS=1
      else
        warn "TECHNICAL-DEBT.md: \"$status\" is not a level-two heading, so it is not read as an entry; entries start with \"## TD-\""
      fi
      continue
    fi
    case "$SEEN_IDS" in
      *" $id "*) fail "$id appears more than once in TECHNICAL-DEBT.md; one entry per id" ;;
      *) SEEN_IDS="$SEEN_IDS$id " ;;
    esac
    if [ -n "$dups" ]; then
      fail "$id: field(s) repeated inside the entry:$dups; one value each"
    fi
    if [ -n "$strays" ]; then
      fail "$id: field label(s) found on lines the validator does not read as fields:$strays; write each as a list item such as \"- **Kind:** deferral\""
      SUPPRESS_PASS=1
    fi
    if [ -n "$mentions" ]; then
      warn "$id: line(s)$mentions mention a field name but were not read as fields; if one of them is a field, write it as \"- **Name:** value\" (the six field names are reserved words inside an entry)"
    fi
    if [ -z "$kind" ] && [ "$kindpresent" != "1" ] && [ "$metapresent" = "1" ]; then
      fail "$id: carries deferral fields (Control, Due-before, Review-by, or Closure-evidence) but no Kind line; add \"- **Kind:** deferral\" or \"- **Kind:** shortcut\""
      SUPPRESS_PASS=1
      continue
    fi
    # The Control is checked for every open entry that declares one, whatever the Kind says: it must
    # name a convention, a backend rule, or a floor item, and a floor item is never postponed.
    if [ -n "$control" ] && [ "$status" != "fixed" ]; then
      lc_control="$(printf '%s' "$control" | tr '[:upper:]' '[:lower:]' | sed -E 's/[[:space:]]*:[[:space:]]*/:/; s/^[[:space:]]+//; s/[[:space:]]+$//')"
      case "$lc_control" in
        \[*) fail "$id: Control still holds a template placeholder"; SUPPRESS_PASS=1 ;;
        floor|floor:)
          fail "$id: Control says floor but names no floor item; floor items: ${FLOOR// /, }"; SUPPRESS_PASS=1 ;;
        floor:*)
          item="${lc_control#floor:}"; item="${item%% *}"
          if in_list "$item" "$FLOOR"; then
            if [ "$kind" = "deferral" ]; then
              fail "$id: a floor item ($item) is never a deferral (#30)"
            else
              fail "$id: a floor item ($item) is never postponed, as a deferral or as a shortcut (#30)"
            fi
          else
            fail "$id: Control names unknown floor item \"$item\"; floor items: ${FLOOR// /, }"
          fi
          SUPPRESS_PASS=1 ;;
        '#'[0-9]*|b[0-9]*) ;;
        *) fail "$id: Control is \"$control\"; name a convention (#N and the obligation), a backend rule (BN), or a floor item (floor: name)"; SUPPRESS_PASS=1 ;;
      esac
    fi
    if [ -z "$kind" ] && [ "$kindpresent" = "1" ]; then
      fail "$id: Kind is present but has no value on its line; write \"- **Kind:** shortcut\" or \"- **Kind:** deferral\""
      SUPPRESS_PASS=1
      continue
    fi
    case "$kind" in
      ""|shortcut) continue ;;
      deferral) ;;
      *) fail "$id: Kind is \"$kind\"; expected shortcut or deferral (lower case)"; SUPPRESS_PASS=1; continue ;;
    esac
    SEEN=$((SEEN + 1))
    [ "$status" = "fixed" ] && continue
    [ -z "$control" ] && fail "$id: deferral without Control"
    [ -z "$due" ] && fail "$id: deferral without Due-before (a trigger or a date)"
    [ -z "$review" ] && fail "$id: deferral without Review-by"
    [ -z "$closure" ] && fail "$id: deferral without Closure-evidence"
    case "$closure" in \[*) fail "$id: Closure-evidence still holds a template placeholder" ;; esac
    if [ "$PROFILE_PRESENT" -eq 0 ]; then
      fail "$id: a deferral cannot be evaluated without PROFILE.md; create the profile or fix the entry"
      continue
    fi
    if [ -n "$due" ]; then
      if is_date "$due"; then
        if [[ "$due" < "$TODAY" ]] || [ "$due" = "$TODAY" ]; then
          fail "$id: Due-before date $due reached; the deferral is blocking until fixed (status: $status)"
        else
          PENDING_DEFER="$id until $due"
        fi
      elif is_trigger "$due"; then
        state="$(trigger_state "$due")"
        case "$state" in
          true) fail "$id: trigger $due is true per PROFILE.md; the deferral is blocking until fixed (status: $status; won't-fix does not clear it)" ;;
          false) PENDING_DEFER="$id until $due" ;;
          unknown) unver "$id is due before $due, which rests on a fact recorded as unknown" ;;
        esac
      else
        fail "$id: Due-before \"$due\" is neither a known trigger nor a date. Triggers: ${TRIGGERS// /, }"
      fi
    fi
    if [ -n "$review" ]; then
      if is_date "$review"; then
        if [[ "$review" < "$TODAY" ]]; then warn "$id: Review-by $review has passed; review it and write the new date with the reason"; fi
      else
        fail "$id: Review-by \"$review\" is not a real calendar date YYYY-MM-DD"
      fi
    fi
    # The DEFERRED line is printed only for an entry that passed every check above.
    if [ -n "$PENDING_DEFER" ] && [ "$ERRORS" -eq "$ENTRY_ERRORS" ]; then defer "$PENDING_DEFER"; fi
  done < <(awk -v US="$US" '
    function flush(   mp) {
      mp = (("Control" in seen) || ("Due-before" in seen) || ("Review-by" in seen) || ("Closure-evidence" in seen)) ? 1 : 0
      if (id != "") printf "%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%d%s%d%s%s\n", id, US, status, US, kind, US, control, US, due, US, review, US, closure, US, dups, US, strays, US, kindpresent, US, mp, US, mentions
      if (odd != "") printf "ODD-HEADING%s%s%s%d\n", US, odd, US, oddfields
    }
    function reset() { id = ""; status = ""; kind = ""; control = ""; due = ""; review = ""; closure = ""; dups = ""; strays = ""; mentions = ""; odd = ""; oddfields = 0; kindpresent = 0; split("", seen) }
    # A governed label that appears on a line the list-item rule does not read (a tab-indented or
    # deeply indented block, a label in running text) is a stray: the entry fails instead of the
    # field vanishing.
    # Stray detection casts a wide net on purpose: a governed name followed by a colon anywhere on a
    # line that is not a field line (any markup around it, or none) fails loudly instead of being
    # read as prose, so no spelling of a field can vanish.
    # Returns every governed label found on a non-field line, space separated: any governed name
    # followed by a colon anywhere on the line, plus a label wrapped in emphasis at the start of the
    # line (after indentation or a list marker) even without a colon. Mid-sentence italics of an
    # everyday word are not labels.
    # Position where the markup opened at the start of r has all closed again (inclusive), or the end
    # of r when something never closes. Brackets pair with brackets (a stray "]" is content); tags
    # nest and close with their closing tags, void elements open nothing. An emphasis run closes when
    # it can close (it follows a non-space, and if it follows punctuation it precedes a space,
    # punctuation, or the end) and something of its character is open; otherwise it opens when it can
    # open (it precedes a non-space, and if it precedes punctuation it follows a space, punctuation, or
    # the start); otherwise it is content. A closing run consumes as much of the open runs of its
    # character as its length covers, so "**note *Kind***" closes both at once.
    function stacklast(st) { sub(/,$/, "", st); sub(/^.*,/, "", st); return st + 0 }
    function stackpop(st) { sub(/,$/, "", st); if (st ~ /,/) sub(/,[^,]*$/, ",", st); else st = ""; return st }
    function labelend(r,   i, j, c, ch, q, n, runlen, prev, nxt, canopen, canclose, opened, brackets, tags, emopen, stk, tagtxt, tname, L, t, k, m2, found_close) {
      n = length(r); i = 1; opened = 0; brackets = 0; tags = 0; emopen = 0; LABCLOSED = 0
      split("", stk)
      while (i <= n) {
        c = substr(r, i, 1)
        if (c == "<") {
          j = i + 1; q = ""
          while (j <= n) { ch = substr(r, j, 1); if (q != "") { if (ch == q) q = "" } else if (ch == "\"" || ch == "\047") q = ch; else if (ch == ">") break; j++ }
          if (j > n) return n
          tagtxt = substr(r, i, j - i + 1); tname = tolower(tagtxt); sub(/^<\/?[ \t]*/, "", tname); sub(/[^a-z0-9].*$/, "", tname)
          if (tagtxt ~ /^<\//) { if (tags > 0) tags-- }
          else if (tagtxt !~ /\/>$/ && tname !~ /^(area|base|br|col|embed|hr|img|input|link|meta|source|track|wbr)$/) { tags++; opened = 1 }
          i = j + 1
        } else if (c == "[") { brackets++; opened = 1; i++ }
        else if (c == "]") { if (brackets > 0) brackets--; i++ }
        else if (c == "`") {
          # A code span: a backtick run closed by the next run of the same length, contents opaque,
          # padding allowed. Without a closer the run is literal text.
          j = i; while (j <= n && substr(r, j, 1) == c) j++
          runlen = j - i; k = j; found_close = 0
          while (k <= n) {
            if (substr(r, k, 1) == "`") { m2 = k; while (m2 <= n && substr(r, m2, 1) == "`") m2++; if (m2 - k == runlen) { found_close = 1; break } k = m2 } else k++
          }
          if (found_close) { if (i == 1) { opened = 1; i = k + runlen; if (brackets + tags + emopen <= 0) { LABCLOSED = 1; return i - 1 } } else i = k + runlen }
          else i = j
        }
        else if (c == "*" || c == "_") {
          j = i; while (j <= n && substr(r, j, 1) == c) j++
          runlen = j - i; prev = (i == 1) ? " " : substr(r, i - 1, 1); nxt = (j > n) ? " " : substr(r, j, 1)
          canopen = (nxt !~ /[ \t]/) && (nxt !~ /[[:punct:]]/ || prev ~ /[ \t[:punct:]]/)
          canclose = (prev !~ /[ \t]/) && (prev !~ /[[:punct:]]/ || nxt ~ /[ \t[:punct:]]/)
          # A run that could both open and close may not close an opener when the two lengths add up
          # to a multiple of three unless both are multiples of three; it opens instead.
          if (canclose && canopen && stk[c] != "") { t = stacklast(stk[c]); if ((t + runlen) % 3 == 0 && !(t % 3 == 0 && runlen % 3 == 0)) canclose = 0 }
          if (canclose && stk[c] != "") {
            L = runlen
            while (L > 0 && stk[c] != "") {
              t = stacklast(stk[c]); stk[c] = stackpop(stk[c]); emopen--
              if (t > L) { stk[c] = stk[c] (t - L) ","; emopen++; L = 0 } else L -= t
            }
          } else if (canopen) { stk[c] = stk[c] runlen ","; emopen++; opened = 1 }
          i = j
        } else i++
        if (opened && brackets + tags + emopen <= 0) { LABCLOSED = 1; return i - 1 }
      }
      return n
    }
    # In a closed label the governed name must be the first or the last word of a short span ("Kind,
    # if any", "note Kind", "(Kind)", at most four words); a bold sentence that mentions the word is
    # prose. An unclosed label is malformed markup, so a governed name anywhere in it is reported
    # rather than risked. Returns the lower-case name found, or "".
    function labelname(lab, unclosed,   nwords, words, m) {
      gsub(/^[^a-z]+|[^a-z]+$/, "", lab); nwords = split(lab, words, /[ \t]+/)
      if ((unclosed && match(lab, /(^|[^a-z-])(status|kind|control|due-before|review-by|closure-evidence)([^a-z-]|$)/)) || (nwords <= 4 && (match(lab, /^(status|kind|control|due-before|review-by|closure-evidence)([^a-z-]|$)/) || match(lab, /(^|[^a-z-])(status|kind|control|due-before|review-by|closure-evidence)$/)))) {
        m = substr(lab, RSTART, RLENGTH); gsub(/[^a-z-]/, "", m); return m
      }
      return ""
    }
    # Remove tags, code marks, and emphasis marks from a span; with spaces = 1 the marks become spaces.
    function decode(x, spaces) {
      if (spaces) gsub(/<([^>"\047]|"[^"]*"|\047[^\047]*\047)*>/, " ", x); else gsub(/<([^>"\047]|"[^"]*"|\047[^\047]*\047)*>/, "", x)
      gsub(/\]\(([^()"]|"[^"]*"|\([^()]*\))*\)/, "]", x); gsub(/[\[\]()]/, " ", x)
      if (spaces) gsub(/[`*_]/, " ", x); else gsub(/[`*_]/, "", x)
      return x
    }
    function strayname(s,   found, m, t, s0, rest, lab, op, full, unclosed, tail) {
      s = tolower(s); s0 = s; found = ""
      # An emphasized or tagged span at the start of the line (after an optional list marker and
      # markup-free leading words) is decoded, parentheses and punctuation included, and a governed
      # name found in it as a whole word is a stray even without a colon. A prose sentence with an
      # italic everyday word has no list marker and no leading markup, so it is not a label.
      if (match(s, /^[ \t]*(([-*+]|[0-9]+[.)])[ \t]+([^*_`<\[]*[ \t])?)?([*_`\[]|<([^>"\047]|"[^"]*"|\047[^\047]*\047)*>)+/)) {
        op = substr(s, RSTART, RLENGTH); sub(/^[ \t]*(([-*+]|[0-9]+[.)])[ \t]+([^*_`<\[]*[ \t])?)?/, "", op)
        rest = substr(s, RSTART + RLENGTH)
        # The label is the span from the opening markup to the point where every bracket, tag, and
        # emphasis opened inside it has closed again (brackets pair with brackets, tags with their closing
        # tags, emphasis runs with runs of the same character); an unclosed label runs to the end of the
        # line. Link destinations, values, and annotations after the label stay outside it.
        full = op rest
        lab = substr(full, 1, labelend(full))
        unclosed = !LABCLOSED
        # A word fused to a closed label ("**note**Kind**", "<span>note</span>Control") is taken as a
        # separate trailing word; a link destination that follows the label is not part of it.
        tail = ""
        if (LABCLOSED && substr(full, length(lab) + 1) ~ /^[^ \t(]/) { tail = substr(full, length(lab) + 1); sub(/[ \t].*$/, "", tail); sub(/\(.*$/, "", tail) }
        # The label is decoded in more than one way and a governed name found in any of them counts:
        # with tags, code marks, and emphasis marks removed without adding a space ("K<span>ind</span>"
        # and "K*ind*" read "kind"), with the marks turned into spaces ("**note**Kind**" reads "note
        # kind"), and with the fused word decoded on its own and joined by a space ("**note**K*ind***"
        # reads "note kind"); brackets and parentheses become spaces throughout.
        m = labelname(decode(lab, 0), unclosed)
        if (m == "") m = labelname(decode(lab, 1), unclosed)
        if (m == "" && tail != "") m = labelname(decode(lab, 0) " " decode(tail, 0), unclosed)
        if (m == "" && tail != "") m = labelname(decode(lab, 1) " " decode(tail, 0), unclosed)
        if (m != "") {
          found = " " canon(m)
          s = substr(s, length(s) - length(rest) + length(lab) + length(tail) + 1)
        }
      }
      # A governed name followed by a colon anywhere, with any markup between the name and the colon.
      t = s0; gsub(/<([^>"\047]|"[^"]*"|\047[^\047]*\047)*>/, "", t); gsub(/\]\(([^()]|\([^()]*\))*\)/, "", t); gsub(/[*_`\[\]]/, "", t)
      while (match(t, /(^|[^a-z-])(status|kind|control|due-before|review-by|closure-evidence)[ \t]*:/)) {
        m = substr(t, RSTART, RLENGTH); sub(/^[^a-z]/, "", m); sub(/[ \t]*:$/, "", m)
        if (index(found, " " canon(m)) == 0) found = found " " canon(m)
        t = substr(t, RSTART + RLENGTH)
      }
      sub(/^ /, "", found); return found
    }
    # Labels are compared without regard to letter case; canon() returns the spelling the template uses.
    function governed(n) { n = tolower(n); return (n == "status" || n == "kind" || n == "control" || n == "due-before" || n == "review-by" || n == "closure-evidence") }
    function canon(n) {
      n = tolower(n)
      if (n == "status") return "Status"; if (n == "kind") return "Kind"; if (n == "control") return "Control"
      if (n == "due-before") return "Due-before"; if (n == "review-by") return "Review-by"; if (n == "closure-evidence") return "Closure-evidence"
      return n
    }
    # A field line is a list item (marker "-", "*", "+", or an ordered marker such as "1." or "1)",
    # indented at most three spaces, followed by spaces or tabs) whose text starts with a bold label
    # in either bold syntax and either colon placement: "**Name:** value", "**Name**: value",
    # "__Name:__ value". The list marker is required; a bold label in running text is not a field.
    # A field line is a list item whose text up to the first colon is a label carrying some inline
    # markup (bold, italic, code, a link, an HTML tag, nested in any order). The label is normalized
    # by removing every marker and tag before the name is compared, so "**Kind:**", "**Kind**:",
    # "***Control***:", "**_Control_**:", "**`Kind`:**", "[**Kind**](#k):" all read as the field.
    # A plain "Kind: value" list item carries no markup and is left to the stray rule.
    # The label delimiter is the first colon that sits outside parentheses (link destinations, which
    # may nest one level) and outside HTML tags, so "https:" inside a link never splits a label.
    # Heading identifier normalization, shared by ATX and underlined headings: closed HTML tags are
    # removed (so "<span>TD</span>-12" reads TD-12), then whitespace, emphasis markers, brackets, and
    # an unclosed tag start ("<span TD-12") are peeled off in turn.
    # Literal character count (markers are regex metacharacters, so gsub cannot count them).
    function countchar(str, ch,   i, n) { n = 0; for (i = 1; i <= length(str); i++) if (substr(str, i, 1) == ch) n++; return n }
    function idtext(t) {
      gsub(/<([^>"\047]|"[^"]*"|\047[^\047]*\047)*>/, "", t)
      while (t ~ /^([ \t]|[*_`\[]|<[^ \t>]*[ \t])/) sub(/^([ \t]+|[*_`\[]+|<[^ \t>]*[ \t]+)/, "", t)
      # Inline markup inside the identifier itself ("**TD**-903", "T*D*-903", "[TD](#x)-903") is
      # removed too: link destinations first, then markers and brackets.
      gsub(/\]\(([^()"]|"[^"]*"|\([^()]*\))*\)/, "]", t); gsub(/[*_`\[\]]/, "", t); sub(/^[ \t]+/, "", t)
      # The identifier prefix is read in any letter case and reported as TD-.
      if (tolower(substr(t, 1, 3)) == "td-") t = "TD-" substr(t, 4)
      return t
    }
    function delimpos(s,   i, c, depth, intag, q) {
      depth = 0; intag = 0; q = ""
      for (i = 1; i <= length(s); i++) {
        c = substr(s, i, 1)
        if (intag) {
          if (q != "") { if (c == q) q = ""; continue }
          if (c == "\"" || c == "\047") { q = c; continue }
          if (c == ">") intag = 0
          continue
        }
        if (c == "<") { intag = 1; continue }
        if (c == "(") { depth++; continue }
        if (c == ")") { if (depth > 0) depth--; continue }
        if (c == ":" && depth == 0) return i
      }
      return 0
    }
    # The label must carry some inline markup; every marker, tag, and link destination is removed
    # from it before the name is compared. A label that is not a governed name but contains one as a
    # word ("oops Kind", "Control value") is recorded in mixedlabel so the caller fails it loudly.
    function fieldname(s,   pos, label, lab0, lab1) {
      mixedlabel = ""
      if (s !~ /^ ? ? ?([-*+]|[0-9]+[.)])[ \t]+/) return ""
      sub(/^ ? ? ?([-*+]|[0-9]+[.)])[ \t]+/, "", s)
      pos = delimpos(s); if (pos == 0) return ""
      label = substr(s, 1, pos - 1)
      if (label !~ /[*_`<\[]/) return ""
      # Two decodings: marks and tags removed ("K<span>ind</span>" reads Kind), and marks and tags
      # turned into spaces ("**note**Control" reads "note Control").
      lab0 = decode(label, 0); gsub(/#/, "", lab0); sub(/^[ \t]+/, "", lab0); sub(/[ \t]+$/, "", lab0)
      lab1 = decode(label, 1); gsub(/#/, "", lab1); gsub(/[ \t]+/, " ", lab1); sub(/^ /, "", lab1); sub(/ $/, "", lab1)
      if (governed(lab0)) return lab0
      if (governed(lab1)) return lab1
      # A governed name as a whole word among other words or punctuation ("Control / rule",
      # "Control, if any", "note Control") in either decoding is recorded so the caller fails it.
      if (match(tolower(lab0), /(^|[^a-z-])(status|kind|control|due-before|review-by|closure-evidence)([^a-z-]|$)/) || match(tolower(lab1), /(^|[^a-z-])(status|kind|control|due-before|review-by|closure-evidence)([^a-z-]|$)/)) {
        mixedlabel = substr(tolower(lab0 " " lab1), RSTART, RLENGTH); if (mixedlabel !~ /(status|kind|control|due-before|review-by|closure-evidence)/) { match(tolower(lab0 " " lab1), /(status|kind|control|due-before|review-by|closure-evidence)/); mixedlabel = substr(tolower(lab0 " " lab1), RSTART, RLENGTH) }
        gsub(/[^a-z-]/, "", mixedlabel); mixedlabel = canon(mixedlabel); return ""
      }
      # A label that markup splits into several parts and that holds a governed name inside
      # ("**note**C*ontrol***" reads "notecontrol" one way and "note c ontrol" the other) is not a
      # clean field name either; "Controller" has no split and stays free.
      if (lab1 ~ / / && match(tolower(lab0), /(status|kind|control|due-before|review-by|closure-evidence)/)) {
        mixedlabel = canon(substr(tolower(lab0), RSTART, RLENGTH)); return ""
      }
      if (lab0 !~ /^[A-Za-z][A-Za-z \t-]*$/) return ""
      return lab0
    }
    # The value is everything after the delimiter, with the markers that closed the label stripped,
    # then whitespace; the value itself, links and all, is left alone.
    function val(s,   pos) {
      sub(/^ ? ? ?([-*+]|[0-9]+[.)])[ \t]+/, "", s)
      pos = delimpos(s); if (pos == 0) return ""
      s = substr(s, pos + 1)
      sub(/^(\*|_|`|<[^>]*>)*/, "", s); sub(/^[ \t]+/, "", s); sub(/[ \t]+$/, "", s); return s
    }
    { sub(/\r$/, "") }
    # Fenced examples are skipped. Fences are classified on the raw line, before any HTML rewriting. A fence opens with three or more backticks or tildes indented by
    # at most three spaces and closes only with a run of the same character at least as long,
    # indented by at most three spaces, followed by nothing but whitespace; a shorter or different
    # run inside the fence, or one indented four spaces or more, is content.
    /^ ? ? ?(```|~~~)/ {
      body = $0; sub(/^ ? ? ?/, "", body)
      c = substr(body, 1, 1); n = 0
      while (substr(body, n + 1, 1) == c) n++
      rest = substr(body, n + 1)
      # A backtick run followed by more backticks on the same line is inline code, not a fence: the
      # line is left for the ordinary rules instead of being skipped.
      if (!infence) {
        if (!(c == "`" && rest ~ /`/)) { infence = 1; fchar = c; flen = n; fence_line = NR; next }
      }
      else if (c == fchar && n >= flen && rest ~ /^[ \t]*$/) { infence = 0; next }
      else next
    }
    infence { next }
    # HTML bold tags in any letter case, with attributes (quoted values may contain ">") or inner
    # whitespace, are rewritten to bold markers so a field written with them is still a field.
    { gsub(/<[ \t]*\/?[ \t]*([bB]|[sS][tT][rR][oO][nN][gG])([ \t]([^>"\047]|"[^"]*"|\047[^\047]*\047)*)?[ \t]*>/, "**"); gsub(/<[ \t]*\/?[ \t]*([iI]|[eE][mM])([ \t]([^>"\047]|"[^"]*"|\047[^\047]*\047)*)?[ \t]*>/, "*") }
    # HTML italic tags become single emphasis markers, so an italic label is caught as a stray; HTML
    # code tags become backticks, which the label rules unwrap or the stray rule ignores.
    { gsub(/<[ \t]*\/?[ \t]*([cC][oO][dD][eE]|[tT][tT])([ \t]([^>"\047]|"[^"]*"|\047[^\047]*\047)*)?[ \t]*>/, "`") }
    # Code spans and links around a label are unwrapped inside the label only (see fieldname), so
    # "**`Kind`:**" and "**[Kind](#kind):**" read as Kind while values keep their brackets.
    # A paragraph that starts with a "TD-" line and is underlined with dashes or equals signs (any
    # length, possibly after wrapped title lines) is a setext heading the parser does not read as an
    # entry; it is recorded like a wrong-level heading so its fields cannot vanish. The identifier is
    # exposed by the same normalization the ATX path uses.
    /^ ? ? ?(-+|=+)[ \t]*$/ && prevtd != "" { flush(); reset(); odd = prevtd; prevtd = ""; next }
    {
      if (idtext($0) ~ /^TD-[^ \t]/) prevtd = $0
      else if ($0 ~ /^[ \t]*$/ || $0 ~ /^ ? ? ?([-*+]|[0-9]+[.)])[ \t]/ || $0 ~ /^ ? ? ?#/) prevtd = ""
    }
    # Headings: up to three spaces of indentation, one to six marks, then whitespace. An entry starts
    # at a level-two "TD-" heading and runs until the next one or a level-one heading; other headings
    # inside it, such as "### Follow-up" or a stray "## Follow-up", stay part of it, so fields written
    # under them are still read and a repeated field still fails. A "TD-" heading at any other level
    # is recorded so the shell can fail or warn about it.
    /^ ? ? ?#/ {
      h = $0; sub(/^ ? ? ?/, "", h)
      level = 0; while (substr(h, level + 1, 1) == "#") level++
      text = idtext(substr(h, level + 1))
      if (text ~ /^TD-/) {
        # A TD heading of any shape: level two with a space is an entry; anything else (another
        # level, seven or more marks, no space after the marks) is recorded for the shell.
        flush(); reset()
        if (level == 2 && h ~ /^##[ \t]/) { id = text; sub(/[^A-Za-z0-9-].*$/, "", id) } else { odd = $0 }
        next
      }
      if (h ~ /^#+([ \t]|$)/) {
        if (level == 1) { flush(); reset() }
        next
      }
    }
    odd != "" { name = fieldname($0); if ((name != "" && governed(name)) || mixedlabel != "" || strayname($0) != "") oddfields = 1; next }
    id == "" { next }
    {
      name = fieldname($0)
      if (name == "") {
        st = strayname($0)
        if (st == "" && mixedlabel != "") st = mixedlabel
        if (st != "") strays = strays " " st
        else {
          # The broad net: a line that is not a field and not a recognized stray but still mentions a
          # field name, in any letter case and under any markup, is reported as a possible field the
          # validator did not read. Prose that merely uses the word is warned about, not failed.
          lw = tolower(decode($0, 0)); lw1 = tolower(decode($0, 1))
          if (match(lw, /(^|[^a-z-])(status|kind|control|due-before|review-by|closure-evidence)([^a-z-]|$)/) || match(lw1, /(^|[^a-z-])(status|kind|control|due-before|review-by|closure-evidence)([^a-z-]|$)/)) mentions = mentions " " FNR
          else {
            # A word split by markup ("K[ind](#f)", "K<span>ind</span>") shows as a letter touching a
            # marker, bracket, or tag; then the letters alone are searched for a field name.
            lw2 = tolower($0)
            if (lw2 ~ /[a-z]([*_`\[<]|\]\()|([*_`\]>])[a-z]/) { lw2 = decode(lw2, 0); gsub(/[^a-z]/, "", lw2); if (lw2 ~ /(status|kind|control|due-before|review-by|closure-evidence|duebefore|reviewby|closureevidence)/) mentions = mentions " " FNR }
          }
        }
        next
      }
      if (!governed(name)) next
      name = canon(name)
      seen[name]++; if (seen[name] == 2) dups = dups " " name
      if (seen[name] > 1) next
      v = val($0)
      if (name == "Status") status = v
      else if (name == "Kind") { kind = v; kindpresent = 1 }
      else if (name == "Control") control = v
      else if (name == "Due-before") due = v
      else if (name == "Review-by") review = v
      else if (name == "Closure-evidence") closure = v
    }
    END { flush(); if (infence) printf "UNCLOSED-FENCE%s%d\n", US, fence_line }
  ' "$TD")
  if [ "$SUPPRESS_PASS" -eq 1 ]; then
    :
  elif [ "$SEEN" -eq 0 ]; then
    pass "TECHNICAL-DEBT.md has no deferrals"
  elif [ "$ERRORS" -eq "$BEFORE" ]; then
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
