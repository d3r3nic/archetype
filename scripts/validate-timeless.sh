#!/bin/bash
# Archetype Timeless-Conventions Check
#
# The framework encodes character; project artifacts hold specifics. This
# check fails when the shipped conventions, enforcers, index files, README,
# or file templates carry content that expires:
#
#   A. Product, library, service, or vendor proper names outside a section
#      titled "Research Notes" (term list: scripts/timeless-terms.txt;
#      per-file exceptions with a written reason: scripts/timeless-allowlist.txt)
#   B. Factory step references ("Step 48 added this")
#   C. Statistics or multipliers attached to claims about AI
#      ("AI does this at 80-90% frequency", "2.74x more vulnerabilities")
#   D. Numeric limits tied to tool capability: line-count limits and
#      minute cadences ("keep files under 300 lines", "every 25-30 minutes").
#      A project-set dial names no number ("the project sets its limit in
#      References.md"), so it never matches.
#   E. Changelog language: version-scoped headers (v1, v2), "(shipped)",
#      "not yet implemented", "added in Step N", "promoted from".
#   F. Every "Research Notes" section must open with a line starting
#      "Dated notes:" so readers know anything named there expires.
#
# Also validates the allowlist itself: every entry needs a justification,
# and every entry must match something (no placeholders).
#
# Usage:
#   scripts/validate-timeless.sh            # scan the default file set
#   scripts/validate-timeless.sh FILE...    # scan specific files (relative to root)
#
# Exit 0 on pass, 1 on any finding. Portable bash + awk + grep only.
#
# Scope note: the default set is conventions/, backend/conventions/, the
# root and backend CLAUDE.md and Conventions.md, README.md, and
# templates/*.md. Phase playbooks (bootstrap/, scaffolding/, development/)
# are not yet in scope; pass them as arguments to measure them.

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

TERMS_FILE="$SCRIPT_DIR/timeless-terms.txt"
ALLOW_FILE="$SCRIPT_DIR/timeless-allowlist.txt"

for required in "$TERMS_FILE" "$ALLOW_FILE"; do
  if [ ! -f "$required" ]; then
    echo "Error: missing $required"
    exit 1
  fi
done

cd "$FRAMEWORK_DIR" || exit 1

if [ "$#" -gt 0 ]; then
  FILES="$*"
else
  FILES=""
  for f in CLAUDE.md Conventions.md README.md backend/CLAUDE.md backend/Conventions.md \
           conventions/*.md backend/conventions/*.md templates/*.md; do
    [ -f "$f" ] && FILES="$FILES $f"
  done
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

ERRORS=0
fail() { printf "${RED}FAIL${NC}: %s\n" "$1"; ERRORS=$((ERRORS + 1)); }
pass() { printf "${GREEN}OK${NC}: %s\n" "$1"; }

echo "Archetype Timeless-Conventions Check"
echo "Root: $FRAMEWORK_DIR"

# ----------------------------------------------------------------------
# Load the term list (longest first so multi-word names win) and allowlist.
# ----------------------------------------------------------------------
# Temp copies: sorted terms and stripped allowlist. Passed to awk as files
# (not -v strings) so newlines and backslashes survive every awk flavor.
TMP_TERMS="$(mktemp -t timeless-terms.XXXXXX)"
TMP_ALLOW="$(mktemp -t timeless-allow.XXXXXX)"
trap 'rm -f "$TMP_TERMS" "$TMP_ALLOW"' EXIT

grep -v '^#' "$TERMS_FILE" | grep -v '^[[:space:]]*$' \
  | awk -F'\t' '{ print length($1) "\t" $0 }' | sort -t "$(printf '\t')" -k1,1rn | cut -f2- > "$TMP_TERMS"
grep -v '^#' "$ALLOW_FILE" | grep -v '^[[:space:]]*$' > "$TMP_ALLOW"

if [ ! -s "$TMP_TERMS" ]; then
  fail "term list is empty: $TERMS_FILE"
fi

ALLOW_ENTRIES="$(cat "$TMP_ALLOW")"

# Allowlist hygiene: three tab-separated fields, non-empty justification.
BAD_ALLOW=0
while IFS= read -r entry; do
  [ -z "$entry" ] && continue
  fields=$(printf '%s' "$entry" | awk -F'\t' '{ print NF }')
  reason=$(printf '%s' "$entry" | awk -F'\t' '{ print $3 }')
  if [ "$fields" -lt 3 ] || [ -z "$(printf '%s' "$reason" | tr -d '[:space:]')" ]; then
    fail "allowlist entry lacks a justification: $entry"
    BAD_ALLOW=$((BAD_ALLOW + 1))
  fi
done <<< "$ALLOW_ENTRIES"
[ "$BAD_ALLOW" -eq 0 ] && pass "allowlist entries carry justifications"

# ----------------------------------------------------------------------
# Scan. One awk pass per file: track the Research Notes zone, apply checks.
# Output lines: <class>\t<file>:<line>\t<detail>
# ----------------------------------------------------------------------
FINDINGS="$(
for file in $FILES; do
  awk -v FILE="$file" -v TERMS_PATH="$TMP_TERMS" -v ALLOW_PATH="$TMP_ALLOW" '
  function bounded(term) { return "(^|[^[:alnum:]_])" term "([^[:alnum:]_]|$)" }
  BEGIN {
    FS = "\t"
    nterms = 0
    while ((getline tline < TERMS_PATH) > 0) {
      split(tline, parts, "\t")
      nterms++; term[nterms] = parts[1]; cat[nterms] = parts[2]
    }
    close(TERMS_PATH)
    while ((getline aline < ALLOW_PATH) > 0) {
      split(aline, parts, "\t")
      if (parts[1] == "*" || parts[1] == FILE) allowed[parts[2]] = 1
    }
    close(ALLOW_PATH)
    research = 0; notice = 0; research_line = 0
    stat_trigger = "(^|[^[:alnum:]])(AI|agents?|models?|LLMs?|compliance|generated)([^[:alnum:]]|$)"
    stat_number = "[0-9]+(\\.[0-9]+)?x([^[:alnum:]]|$)|[0-9]+(-[0-9]+)?%"
    limit_words = "(under|below|beyond|over|exceeds?|exceeding|more than|less than|fewer than|up to|at most|max|maximum|maximum of|limit of|limited to|past|within|no more than|longer than|shorter than|every|each|per)"
    line_limit = limit_words " [0-9]+(-[0-9]+)? lines?([^[:alnum:]]|$)|[0-9]+\\+ lines?([^[:alnum:]]|$)|[0-9]+-line (limit|max|maximum|cap|ceiling)|[0-9]+ lines? (max|maximum|limit|cap|or (more|less|fewer))"
    minute_limit = limit_words " [0-9]+(-[0-9]+)? minutes?([^[:alnum:]]|$)"
    version_ref = "(^|[[:space:](])v[0-9]+([^[:alnum:]]|$)"
  }
  function report(class, detail) { printf "%s\t%s:%d\t%s\n", class, FILE, NR, detail }
  {
    line = $0
    # Zone tracking.
    if (line ~ /^#{2,3} Research Notes[[:space:]]*$/) { research = 1; notice = 0; research_line = NR; next_is_zone = 1 }
    else if (line ~ /^#{1,3} /) {
      if (research && !notice) report("F", "Research Notes section at line " research_line " lacks a line starting \"Dated notes:\"")
      research = 0
    }
    if (research && line ~ /^Dated notes:/) notice = 1

    # B. Factory step references. Playbook steps are single-digit within a
    #    named document; factory steps are two or more digits.
    if (line ~ /(^|[^[:alnum:]])Steps? [0-9][0-9]+/ || line ~ /(framework|factory) Step [0-9]+/ || line ~ /Step [0-9]+ (added|shipped|introduced|landed|promoted)/)
      report("B", "factory step reference: " line)

    # C. Statistics attached to claims about AI.
    if (line ~ stat_trigger && line ~ stat_number)
      report("C", "statistic attached to an AI claim: " line)

    # D. Tool-capability numeric limits.
    if (line ~ line_limit) report("D", "line-count limit (make it a project-set dial): " line)
    if (line ~ minute_limit) report("D", "minute cadence (make it a project-set dial): " line)

    # E. Changelog language.
    if (line ~ /^#{1,6} / && line ~ version_ref) report("E", "version-scoped header: " line)
    else if (line ~ /\((shipped|not yet implemented|not planned)\)|not yet implemented|(^|[^[:alnum:]])was shipped|shipped in (Step|v[0-9])|added (in|by|with|since) (Step|v[0-9])|(Step [0-9]+|v[0-9]+) (added|shipped|introduced|landed)|promoted from (Step|the factory)|(^|[[:space:](])v[0-9]+\+/ )
      report("E", "changelog language: " line)
    else if (line ~ version_ref && line !~ /^[[:space:]]*"/ && line !~ /```/)
      report("E", "version-scoped scope language: " line)

    # A. Named tools outside Research Notes.
    if (!research) {
      scan = line
      for (i = 1; i <= nterms; i++) {
        re = bounded(term[i])
        while (match(scan, re)) {
          hit = substr(scan, RSTART, RLENGTH)
          # Strip the boundary characters captured on either side.
          gsub(/^[^[:alnum:]_]/, "", hit); gsub(/[^[:alnum:]_]$/, "", hit)
          if (allowed[term[i]]) { used[term[i]] = 1 }
          else report("A", "named tool outside Research Notes [" cat[i] "]: " hit)
          # Blank the match so shorter terms cannot re-match inside it.
          pad = ""; for (k = 0; k < RLENGTH; k++) pad = pad " "
          scan = substr(scan, 1, RSTART - 1) pad substr(scan, RSTART + RLENGTH)
        }
      }
    }
  }
  END {
    if (research && !notice) report("F", "Research Notes section at line " research_line " lacks a line starting \"Dated notes:\"")
    for (t in used) printf "USED\t%s\t%s\n", FILE, t
  }' "$file"
done
)"

# ----------------------------------------------------------------------
# Report by class.
# ----------------------------------------------------------------------
report_class() {
  local class="$1" label="$2"
  local hits
  hits="$(printf '%s\n' "$FINDINGS" | awk -F'\t' -v c="$class" '$1 == c { print $2 ": " $3 }')"
  if [ -n "$hits" ]; then
    while IFS= read -r h; do fail "[$class] $h"; done <<< "$hits"
  else
    pass "$label"
  fi
}

report_class A "no named tools outside Research Notes"
report_class B "no factory step references"
report_class C "no statistics attached to AI claims"
report_class D "no tool-capability numeric limits"
report_class E "no changelog language"
report_class F "every Research Notes section carries the dated notice"

# Allowlist entries that matched nothing are placeholders.
STALE=0
while IFS= read -r entry; do
  [ -z "$entry" ] && continue
  apath=$(printf '%s' "$entry" | awk -F'\t' '{ print $1 }')
  aterm=$(printf '%s' "$entry" | awk -F'\t' '{ print $2 }')
  if [ "$apath" = "*" ]; then
    matched=$(printf '%s\n' "$FINDINGS" | awk -F'\t' -v t="$aterm" '$1 == "USED" && $3 == t' | head -1)
  else
    matched=$(printf '%s\n' "$FINDINGS" | awk -F'\t' -v p="$apath" -v t="$aterm" '$1 == "USED" && $2 == p && $3 == t' | head -1)
  fi
  if [ -z "$matched" ]; then
    fail "allowlist entry matches nothing (remove it): $apath / $aterm"
    STALE=$((STALE + 1))
  fi
done <<< "$ALLOW_ENTRIES"
[ "$STALE" -eq 0 ] && pass "every allowlist entry is in use"

echo "==="
if [ "$ERRORS" -gt 0 ]; then
  printf "${RED}%d timeless violations${NC}\n" "$ERRORS"
  exit 1
else
  printf "${GREEN}Pass${NC}: timeless check clean\n"
  exit 0
fi
