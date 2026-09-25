#!/bin/bash
# Validates a scaffolded project against the framework's scaffold conventions.
# Replaces AI-discipline-only verification with machine-verifiable gates.
# Run from the project root after scaffolding.
# Use --required known-screen when the scaffold route is known to produce screens.
#
# Checks (categorical, not prescriptive); ids match the groups the script prints:
#   1.  Every foundational system in feature-tree.md has its page: the path its row names
#       in the Docs column, or docs/systems/{slug}.md; a system blocked on the owner is
#       reported on every run with its owner action
#   2.  An env-validation module or a named validation function exists in source
#       (that the call sits at startup is the scaffold step's own verify line)
#   3.  No console-level output in source outside dev-guarded blocks
#   4.  Audit log path exists when the unit handles regulated data (PROFILE.md, or References.md)
#   4b. In-memory audit store not shipped to regulated production
#   5.  Smoke-test feature exists
#   6.  CI workflow doesn't auto-run migrations on main/master pushes
#   6b. Pre-commit hook present
#   6c. Persisted queries for mobile/public GraphQL clients (if declared)
#   6d. Telemetry exporter configured (if References.md names the standard)
#   7.  VERSION-LOG.md has a Scaffold entry
#   8.  References.md § Design Artifact is filled in (delegates to validate-design.sh;
#       a project with no such section passes)
#
# Exit 0 on pass, 1 on any error. Warnings do not fail.

DESIGN_REQUIRED=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --required)
      [ "$#" -ge 2 ] || { echo "--required needs a value (accepted: known-screen)"; exit 2; }
      DESIGN_REQUIRED="$2"; shift 2 ;;
    -h|--help) sed -n '2,5p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $1 (accepted: --required known-screen)"; exit 2 ;;
  esac
done
[ -z "$DESIGN_REQUIRED" ] || [ "$DESIGN_REQUIRED" = "known-screen" ] || {
  echo "unknown required mode: $DESIGN_REQUIRED (accepted: known-screen)"; exit 2;
}

PROJECT_ROOT="$(pwd)"

# Detect project layout: framework at root, in archetype/ subfolder, or in ./project/
SRC_DIR=""
for candidate in "$PROJECT_ROOT/src" "$PROJECT_ROOT/project/src" "$PROJECT_ROOT/app" "$PROJECT_ROOT/lib"; do
  if [ -d "$candidate" ]; then
    SRC_DIR="$candidate"
    break
  fi
done

# Find References.md and feature-tree.md (may be at project root or in a subfolder)
REFS=""
TREE=""
for dir in "$PROJECT_ROOT" "$PROJECT_ROOT/project" "$PROJECT_ROOT/archetype"; do
  [ -f "$dir/References.md" ] && REFS="$dir/References.md"
  [ -f "$dir/feature-tree.md" ] && TREE="$dir/feature-tree.md"
done

if [ -z "$REFS" ]; then
  echo "Error: References.md not found. Run from the scaffolded project root."
  exit 1
fi

if [ -z "$TREE" ]; then
  echo "Error: feature-tree.md not found. Run from the scaffolded project root."
  exit 1
fi

PROJECT_DIR="$(dirname "$REFS")"
DOCS_SYSTEMS="$PROJECT_DIR/docs/systems"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

fail()  { printf "${RED}FAIL${NC}: %s\n" "$1"; ERRORS=$((ERRORS + 1)); }
warn()  { printf "${YELLOW}WARN${NC}: %s\n" "$1"; WARNINGS=$((WARNINGS + 1)); }
pass()  { printf "${GREEN}OK${NC}: %s\n" "$1"; }
group() { printf "\n[%s] %s\n" "$1" "$2"; }

echo "Scaffold Self-Test"
echo "Project: $PROJECT_DIR"
echo "Source:  ${SRC_DIR:-(not found)}"

# ----------------------------------------------------------------------
group 1 "Every foundational system has a docs/systems/ entry"
# ----------------------------------------------------------------------
# Rows of feature-tree.md's Foundational Systems table ONLY: the walk stops at the next
# ## header (usually ## Features), so feature docs are never flagged as missing system docs.
# A row is a line that starts with a pipe and whose first cell, bold markers removed, is a
# number: the row rule scripts/pulse-inspect.sh applies.
# A system's page is the path its row names in the Docs column, which is found by the
# table's header cell "Docs" (only the leading columns have fixed positions) and read from
# the project root. A declared path is checked exactly as written. A row that names no path
# is checked against a page named after the system: docs/systems/<slug>.md, the slug being
# the name in lowercase with every run of characters other than a-z and 0-9 turned into one
# dash and edge dashes trimmed; the older name form (lowercase, spaces to dashes) is still
# accepted. Status `blocked (owner: <action>)` (#29) is read like any other status for the
# page check, and every run reports the system as not complete, with its owner action.
SYSTEM_ROWS="$(awk -F'|' '
  function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
  { sub(/\r$/, ""); gsub(/\*\*/, "") }
  tolower($0) ~ /^## (foundational systems|systems)/ { insec = 1; docs = 0; prev = ""; next }
  insec && /^## / { insec = 0; next }
  !insec || !/^\|/ { next }
  /^\|[ \t:|-]*$/ && /-/ {
    # A separator row: the pipe line above it is the header that names the columns.
    docs = 0
    n = split(prev, head, "|")
    for (i = 2; i <= n; i++) {
      c = trim(head[i]); gsub(/[*`]/, "", c)
      if (tolower(c) == "docs") { docs = i; break }
    }
    next
  }
  /^\|[[:space:]]*[0-9]+[[:space:]]*\|/ {
    printf "%s|%s|%s|%s|%s\n", trim($2), trim($3), trim($6), (docs > 0 ? "declared" : "none"), (docs > 0 ? trim($docs) : "")
    next
  }
  { prev = $0 }
' "$TREE")"

# A Docs cell names a page only as a plain local .md path; anything else (a link, a
# URL, an absolute path, several paths, a placeholder) gets a diagnostic, not a guess.
plain_md_path() {
  case "$1" in
    /*|'~'*|*://*) return 1 ;;
    *[[:space:]]*|*'`'*|*'['*|*']'*|*'('*|*')'*|*'<'*|*'>'*|*'*'*|*'"'*|*"'"*|*'#'*|*\\*) return 1 ;;
    *.md) return 0 ;;
  esac
  return 1
}

DOCS_READY=1
if [ ! -d "$DOCS_SYSTEMS" ]; then
  warn "docs/systems/ directory does not exist — scaffold may be incomplete"
  DOCS_READY=0
fi
MISSING=0
BLOCKED=0
while IFS='|' read -r num name status docs_mode docs_cell; do
  [ -n "$num" ] || continue
  # Every numbered row is a system, whatever its name; one with an empty Name cell is named.
  if [ -z "$name" ]; then
    warn "system row $num has no name (its Name cell is empty); name the system or delete the row"
    MISSING=$((MISSING + 1))
    continue
  fi
  status_clean="$(printf '%s' "$status" | tr -d '`*')"
  status_lc="$(printf '%s' "$status_clean" | LC_ALL=C tr '[:upper:]' '[:lower:]')"
  hint=""
  case "$status_lc" in
    'blocked (owner:'*')')
      action="${status_clean#*:}"; action="${action%)}"
      action="$(printf '%s' "$action" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
      BLOCKED=$((BLOCKED + 1))
      if [ -n "$action" ]; then
        warn "system '$name' is blocked on the owner: $action. It is not complete; features that need it wait (#29)"
      else
        warn "system '$name' is blocked (Status '$status') but names no owner action; write blocked (owner: <action>) (#29)"
      fi
      hint="; a system blocked on the owner keeps a page that names the owner action, what exists, and what stays unavailable (#29)" ;;
    blocked*)
      BLOCKED=$((BLOCKED + 1))
      warn "system '$name' has Status '$status', which is not the recorded form blocked (owner: <action>); name the owner action there (#29)"
      hint="; a system blocked on the owner keeps a page that names the owner action, what exists, and what stays unavailable (#29)" ;;
    'deferred (td-'*')')
      hint="; a deferred system keeps a page that says what is deferred and until which trigger (#30)" ;;
  esac
  [ "$DOCS_READY" -eq 1 ] || continue
  slug="$(printf '%s' "$name" | LC_ALL=C tr '[:upper:]' '[:lower:]' | LC_ALL=C sed -e 's/[^a-z0-9][^a-z0-9]*/-/g' -e 's/^-*//' -e 's/-*$//')"
  if [ "$docs_mode" = declared ] && [ -n "$docs_cell" ]; then
    if ! plain_md_path "$docs_cell"; then
      warn "system '$name': its Docs cell '$docs_cell' is not a plain local .md path; write the page's path from the project root, like docs/systems/${slug:-name}.md"
      MISSING=$((MISSING + 1))
    elif [ ! -f "$PROJECT_DIR/${docs_cell#./}" ]; then
      warn "system '$name' has no document at ${docs_cell#./}, the path its Docs column names$hint"
      MISSING=$((MISSING + 1))
    fi
    continue
  fi
  legacy="$(printf '%s' "$name" | awk '{ print tolower($0) }' | tr ' ' '-')"
  found=0
  for base in "$slug" "$legacy"; do
    [ -n "$base" ] || continue
    for ext in md markdown; do
      if [ -f "$DOCS_SYSTEMS/${base}.${ext}" ]; then found=1; break 2; fi
    done
  done
  if [ "$found" -eq 0 ]; then
    if [ -n "$slug" ]; then
      warn "system '$name' has no document at docs/systems/${slug}.md (named after the system, since its row names no Docs path)$hint"
    else
      warn "system '$name' has no letters or digits to name its page after, and its row names no Docs path; name the page in a Docs column$hint"
    fi
    MISSING=$((MISSING + 1))
  fi
done <<EOF
$SYSTEM_ROWS
EOF
[ "$DOCS_READY" -eq 1 ] && [ "$MISSING" -eq 0 ] && pass "every foundational system has a docs/systems/ entry"

# ----------------------------------------------------------------------
group 2 "Env validation at startup (not ad-hoc)"
# ----------------------------------------------------------------------
if [ -n "$SRC_DIR" ]; then
  # Look for a dedicated env validation file
  ENV_VALIDATOR=""
  for candidate in \
    "$SRC_DIR/shared/config/env.ts" \
    "$SRC_DIR/shared/config/env.js" \
    "$SRC_DIR/config/env.ts" \
    "$SRC_DIR/env.ts" \
    "$SRC_DIR/config.py" \
    "$SRC_DIR/shared/env.py"; do
    [ -f "$candidate" ] && ENV_VALIDATOR="$candidate" && break
  done

  if [ -z "$ENV_VALIDATOR" ]; then
    # Fallback: grep for a validation function
    if grep -rqE 'loadEnv|validateEnv|EnvSchema|EnvSettings' "$SRC_DIR" 2>/dev/null; then
      pass "env validation function detected in source"
    else
      warn "no dedicated env validator found (expected loadEnv / validateEnv / EnvSchema / EnvSettings pattern)"
    fi
  else
    pass "env validator at $ENV_VALIDATOR"
  fi
fi

# ----------------------------------------------------------------------
group 3 "No console-level output in source (categorical, dev-guarded exempt)"
# ----------------------------------------------------------------------
if [ -n "$SRC_DIR" ]; then
  # Heuristic: flag console.* lines UNLESS the file has a __DEV__ or NODE_ENV===development
  # guard within 5 lines above, OR the file is a known reporter/fallback that uses guarded
  # dev-only logging (detectable by an `if (__DEV__)` or `if (process.env.NODE_ENV === 'development')`
  # block somewhere in the file around the console call).
  HITS=0
  while IFS= read -r file; do
    case "$file" in *.test.* | *_test.* | */tests/* ) continue ;; esac
    case "$(basename "$file")" in index.ts|index.js|main.ts|main.py|main.go|cli.* ) continue ;; esac
    # Skip files that are entirely dev-only reporter fallbacks (common pattern: shared/errors/reporter, dev-only shims)
    if grep -qE 'if[[:space:]]*\([[:space:]]*__DEV__[[:space:]]*\)|if[[:space:]]*\([[:space:]]*process\.env\.NODE_ENV[[:space:]]*===[[:space:]]*[\x27"]development[\x27"][[:space:]]*\)' "$file" 2>/dev/null; then
      # File has a dev guard; check if all console.* calls are inside such a block
      # Simple heuristic: if console line is preceded by an if(__DEV__) { within 3 lines, treat as guarded
      UNGUARDED=$(awk '
        /if[[:space:]]*\([[:space:]]*(__DEV__|process\.env\.NODE_ENV[[:space:]]*===[[:space:]]*["\x27]development["\x27])[[:space:]]*\)/ { guard=NR }
        /console\.(log|error|warn|info|debug)/ {
          if (guard != "" && NR - guard <= 5) next
          print FILENAME":"NR": "$0
        }' "$file")
      if [ -n "$UNGUARDED" ]; then
        warn "console-level output (unguarded) in $file"
        HITS=$((HITS + 1))
      fi
    elif grep -qE 'console\.(log|error|warn|info|debug)' "$file" 2>/dev/null; then
      warn "console-level output in $file (use structured logger)"
      HITS=$((HITS + 1))
    fi
    if grep -qE '^[[:space:]]*print\(' "$file" 2>/dev/null && [[ "$file" == *.py ]]; then
      warn "print() in $file (use structured logger)"
      HITS=$((HITS + 1))
    fi
  done < <(find "$SRC_DIR" -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.py' -o -name '*.go' \) 2>/dev/null)
  [ "$HITS" -eq 0 ] && pass "no ungarded console-level output found in source"
fi

# ----------------------------------------------------------------------
group 4 "Audit log if regulated data"
# ----------------------------------------------------------------------
# Whether this unit must keep an audit log. PROFILE.md holds the project's regulated-data fact
# (#30), one per repository: an endpoint folder looks above itself, as validate-profile.sh does.
# - "no" settles it; a References.md that still names a regime is flagged as a contradiction.
# - "yes" or "unknown" (assume regulated until answered) in this folder's own PROFILE.md: this
#   unit is the project, so it keeps the audit log.
# - "yes" or "unknown" in a PROFILE.md above this folder: this unit's References.md says whether
#   it handles the data; silence is a warning, because the audit log belongs to the unit that does.
# - No PROFILE.md (an older project): References.md decides, as before.
# References.md counts only affirmative lines: a regime such as HIPAA, SOC 2 or PCI DSS, or
# "regulated data is/are/yes", on a line without a negation such as none, N/A or not applicable.
REGULATED=0
REG_SOURCE=""
PROFILE_FILE="$PROJECT_ROOT/PROFILE.md"
if [ ! -f "$PROFILE_FILE" ]; then
  TOP="$(cd "$PROJECT_ROOT" && git rev-parse --show-toplevel 2>/dev/null)"
  d="$PROJECT_ROOT"
  while [ -n "$TOP" ] && [ "$d" != "$TOP" ] && [ "$d" != "/" ]; do
    d="$(dirname "$d")"
    if [ -f "$d/PROFILE.md" ]; then PROFILE_FILE="$d/PROFILE.md"; break; fi
  done
  if [ ! -f "$PROFILE_FILE" ] && [ -f "$(dirname "$PROJECT_ROOT")/PROFILE.md" ]; then PROFILE_FILE="$(dirname "$PROJECT_ROOT")/PROFILE.md"; fi
fi
PROFILE_REGULATED=""
PROFILE_HERE=0
if [ -f "$PROFILE_FILE" ]; then
  PROFILE_REGULATED="$(tr -d '\r' < "$PROFILE_FILE" | awk '/^## / { exit } /^- Regulated data:/ { sub(/^- Regulated data:[ \t]*/, ""); print tolower($1); exit }')"
  [ "$PROFILE_FILE" = "$PROJECT_ROOT/PROFILE.md" ] && PROFILE_HERE=1
fi
# A regime counts when any clause of a line (split at ";" and ",") names it without a negation,
# so "HIPAA applies to the notes; PCI DSS does not apply" still declares HIPAA.
REFS_LINE="$(tr -d '\r' < "$REFS" | awk '
  { n = split($0, part, /[;,]/)
    for (i = 1; i <= n; i++) {
      c = tolower(part[i])
      if (c ~ /(none|n\/a|not applicable|not required|no regulated|not regulated|skipped|deferred|not apply|n.t apply)/) continue
      if (c ~ /(hipaa|soc ?2|pci( |-)?dss|pci compliance|gdpr compliance|regulated data (is|are|yes)|regulated data: *(yes|unknown)|compliance: (yes|required))/) {
        sub(/^[ \t]+/, ""); print; exit
      }
    } }')"
REFS_REGULATED=0
[ -n "$REFS_LINE" ] && REFS_REGULATED=1

# Where the audit log is kept: the first filled "- Audit log:" line of References.md § Compliance.
# A path in this unit (in backticks when it holds spaces; a note may follow), "kept by <unit or
# service>", or "not required" (or none, n/a) with the reason. Without the line the usual folders count.
AUDIT_RECORD="$(tr -d '\r' < "$REFS" | awk '
  /^## / { inside = ($0 ~ /^## Compliance[ \t]*$/); next }
  inside && /^- Audit log:/ { v = $0; sub(/^- Audit log:[ \t]*/, "", v); sub(/[ \t]+$/, "", v)
    if (v != "" && v !~ /^\[/) { print v; exit } }')"
AUDIT_ELSEWHERE=""
AUDIT_PATH=""
AUDIT_NONE=""
AUDIT_BAD=""
AUDIT_PLAIN="$(printf '%s' "$AUDIT_RECORD" | tr -d '`')"
case "$(printf '%s' "$AUDIT_PLAIN" | tr '[:upper:]' '[:lower:]')" in
  '') ;;
  'kept by this unit'*|'kept by itself'*|'kept by this service'*|'kept by here'*) ;;   # names no other keeper: the path decides
  'kept by '*) AUDIT_ELSEWHERE="${AUDIT_PLAIN#????????}" ;;
  'not required'*|'none'|'none '*|'none,'*|'n/a'*|'not applicable'*) AUDIT_NONE="$AUDIT_RECORD" ;;
  *)
    case "$AUDIT_RECORD" in
      '`'*'`'*) AUDIT_PATH="${AUDIT_RECORD#?}"; AUDIT_PATH="${AUDIT_PATH%%\`*}" ;;
      *) AUDIT_PATH="$(printf '%s' "$AUDIT_RECORD" | awk '{ print $1 }' | sed 's/[,;:.]*$//')" ;;
    esac
    AUDIT_PATH="${AUDIT_PATH%/}"
    case "$AUDIT_PATH" in
      /*|..|../*|*/..|*/../*) AUDIT_BAD="records the audit log at $AUDIT_PATH: record a path inside this unit" ;;
      ''|.|./) AUDIT_BAD="records the audit log as the whole unit: record the audit log's own folder or file" ;;
    esac
    if [ -z "$AUDIT_BAD" ] && [ -n "$SRC_DIR" ] && [ "$PROJECT_ROOT/$AUDIT_PATH" = "$SRC_DIR" ]; then
      AUDIT_BAD="records the audit log as the whole source folder ($AUDIT_PATH): record the audit log's own folder or file"
    fi
    [ -n "$AUDIT_BAD" ] && AUDIT_PATH="" ;;
esac
DEFAULT_AUDIT="src/shared/audit-log, src/shared/audit and src/audit (or the same under app/, lib/ or project/src/)"
LOCAL_AUDIT=""
if [ -n "$SRC_DIR" ]; then
  for candidate in "$SRC_DIR/shared/audit-log" "$SRC_DIR/shared/audit" "$SRC_DIR/audit"; do
    [ -d "$candidate" ] && LOCAL_AUDIT="$candidate" && break
  done
fi

case "$PROFILE_REGULATED" in
  no) ;;
  yes|unknown)
    if [ "$PROFILE_HERE" = 1 ]; then REGULATED=1; REG_SOURCE="PROFILE.md records regulated data: $PROFILE_REGULATED"
    elif [ "$REFS_REGULATED" = 1 ]; then REGULATED=1; REG_SOURCE="References.md declares regulated data"
    fi ;;
  *) [ "$REFS_REGULATED" = 1 ] && { REGULATED=1; REG_SOURCE="References.md declares regulated data"; } ;;
esac

# A unit that records its audit log's path keeps it, whatever else it declares.
if [ "$REGULATED" -eq 0 ] && [ -n "$AUDIT_PATH" ] && [ "$PROFILE_REGULATED" != "no" ]; then
  REGULATED=1; REG_SOURCE="References.md § Compliance records this unit's audit log"
fi
if [ -n "$AUDIT_BAD" ] && [ "$PROFILE_REGULATED" != "no" ]; then
  fail "References.md § Compliance $AUDIT_BAD"
elif [ "$REGULATED" -eq 1 ] && [ -n "$AUDIT_NONE" ]; then
  warn "References.md § Compliance records the audit log as \"$AUDIT_NONE\" while $REG_SOURCE: that holds only if no regime that applies requires one; the owner's regime decides"
elif [ "$REGULATED" -eq 1 ] && [ -n "$AUDIT_ELSEWHERE" ]; then
  pass "audit log kept by $AUDIT_ELSEWHERE (References.md § Compliance; $REG_SOURCE)"
elif [ "$REGULATED" -eq 1 ] && [ -n "$AUDIT_PATH" ]; then
  if [ -e "$PROJECT_ROOT/$AUDIT_PATH" ]; then
    pass "audit log path exists: $AUDIT_PATH ($REG_SOURCE)"
  else
    fail "$REG_SOURCE, and References.md § Compliance records the audit log at $AUDIT_PATH, which does not exist (audit log must be SEPARATE from app log — see B4)"
  fi
elif [ "$REGULATED" -eq 1 ]; then
  if [ -n "$LOCAL_AUDIT" ]; then
    pass "audit log path exists ($REG_SOURCE)"
  else
    fail "$REG_SOURCE but no audit log found: record where this unit keeps it on the Audit log line of References.md § Compliance (a path, or kept by <unit or service>); without it the check looks in $DEFAULT_AUDIT (audit log must be SEPARATE from app log — see B4)"
  fi
elif [ -n "$AUDIT_ELSEWHERE" ] && [ "$PROFILE_REGULATED" != "no" ]; then
  pass "audit log kept by $AUDIT_ELSEWHERE (References.md § Compliance)"
elif [ -n "$AUDIT_NONE" ] && [ "$PROFILE_REGULATED" != "no" ]; then
  pass "References.md § Compliance records no audit log in this unit: $AUDIT_NONE"
elif [ "$PROFILE_REGULATED" = "no" ] && [ "$REFS_REGULATED" = 1 ]; then
  warn "PROFILE.md records no regulated data, but References.md names it: \"$REFS_LINE\". Correct whichever record is wrong"
elif [ "$PROFILE_REGULATED" = "no" ]; then
  pass "PROFILE.md records no regulated data — audit log check skipped"
elif [ "$PROFILE_REGULATED" = "yes" ] || [ "$PROFILE_REGULATED" = "unknown" ]; then
  warn "PROFILE.md above this folder records regulated data: $PROFILE_REGULATED, and this unit's References.md does not say where the audit log is kept. Record it on the Audit log line of References.md § Compliance: this unit's path when it keeps the log, or kept by <unit>"
else
  pass "no regulated data declared (or explicitly N/A) — audit log check skipped"
fi

# ----------------------------------------------------------------------
group 4b "In-memory audit store not shipped to regulated production"
# ----------------------------------------------------------------------
# A unit that has its own audit-log folder, in a project that handles regulated data, must not
# rely on a test-only in-memory store. PROFILE.md "no" settles it; "yes" or "unknown" applies to
# every unit (only a unit with an audit-log folder is checked); without PROFILE.md, as before,
# any mention of a regime or of regulated data in References.md applies it.
RUN_4B=0
case "$PROFILE_REGULATED" in
  no) ;;
  yes|unknown) RUN_4B=1; [ -n "$REG_SOURCE" ] || REG_SOURCE="PROFILE.md records regulated data: $PROFILE_REGULATED" ;;
  *) if [ "$REGULATED" -eq 1 ] || grep -qiE '(HIPAA|SOC ?2|PCI|GDPR|regulated data)' "$REFS"; then
       RUN_4B=1; [ -n "$REG_SOURCE" ] || REG_SOURCE="References.md mentions regulated data"
     fi ;;
esac
if [ "$RUN_4B" -eq 1 ]; then
  # The recorded path, or this unit's own audit folder: a store in this unit is checked even when
  # the record says another unit or service keeps the log.
  AUDIT_DIR=""
  if [ -n "$AUDIT_PATH" ] && [ -e "$PROJECT_ROOT/$AUDIT_PATH" ]; then
    AUDIT_DIR="$PROJECT_ROOT/$AUDIT_PATH"
  else
    AUDIT_DIR="$LOCAL_AUDIT"
  fi
  if [ -n "$AUDIT_DIR" ]; then
    # In-memory store pattern: class name or variable names suggesting ephemeral storage
    if grep -rqE '(InMemoryAuditStore|MemoryAuditStore|inMemoryStore|this\.records[[:space:]]*=[[:space:]]*\[\]|records:[[:space:]]*Array|push\(record\))' "$AUDIT_DIR" 2>/dev/null; then
      # Check if there's ALSO a real backing store adapter
      if grep -rqE '(PostgresAuditStore|PrismaAuditStore|DatabaseAuditStore|S3AuditStore|AppendOnlyStore|WORMStore|CloudAuditStore)' "$AUDIT_DIR" 2>/dev/null; then
        pass "audit log has both in-memory (test) and backing store (production) implementations"
      else
        fail "audit log uses in-memory store only ($REG_SOURCE). Ship to production = compliance failure. Add a real backing-store adapter (append-only table, WORM storage, or audit-log platform)."
      fi
    else
      pass "audit log implementation does not rely on in-memory-only storage"
    fi
  fi
fi

# ----------------------------------------------------------------------
group 5 "Smoke-test feature exists"
# ----------------------------------------------------------------------
if [ -n "$SRC_DIR" ]; then
  # Look for a smoke-test feature path
  SMOKE_FOUND=0
  for candidate in \
    "$SRC_DIR/features/health" \
    "$SRC_DIR/features/ping" \
    "$SRC_DIR/features/smoke" \
    "$SRC_DIR/features/_health" \
    "$SRC_DIR/features/_smoke" \
    "$SRC_DIR/routes/health.ts"; do
    [ -e "$candidate" ] && SMOKE_FOUND=1 && break
  done
  # Also accept any test file whose name hints at smoke-test
  if [ "$SMOKE_FOUND" -eq 0 ]; then
    if find "$SRC_DIR" -type f \( -name '*smoke*' -o -name '*.integration.test.*' \) 2>/dev/null | grep -q .; then
      SMOKE_FOUND=1
    fi
  fi
  if [ "$SMOKE_FOUND" -eq 1 ]; then
    pass "smoke-test feature detected"
  else
    warn "no smoke-test feature detected — scaffold lacks end-to-end integration proof"
  fi
fi

# ----------------------------------------------------------------------
group 6 "CI does not auto-run migrations on prod deploy"
# ----------------------------------------------------------------------
CI_FILES=$(find "$PROJECT_DIR/.github/workflows" "$PROJECT_DIR/.gitlab-ci.yml" "$PROJECT_DIR/.circleci" "$PROJECT_DIR/Jenkinsfile" 2>/dev/null -type f 2>/dev/null)
if [ -n "$CI_FILES" ]; then
  HITS_FAIL=0
  HITS_OK=0
  for f in $CI_FILES; do
    # Only check files that actually run migrations
    if grep -qE '(prisma migrate deploy|alembic upgrade head|knex migrate:latest|rake db:migrate|flyway migrate|sea-orm-cli migrate|atlas migrate apply)' "$f"; then
      # SAFE patterns: workflow_dispatch (manual) as actual trigger, staging/dev environment gate.
      # Anchor workflow_dispatch to YAML trigger position: either "workflow_dispatch:" at logical line start,
      # or within an "on:" block. A bare "workflow_dispatch" in a comment should NOT match.
      if grep -qE '^[[:space:]]*workflow_dispatch:' "$f" || awk '/^on:/,/^[a-zA-Z]/' "$f" | grep -qE 'workflow_dispatch'; then
        pass "CI migration in $(basename "$f") is manual (workflow_dispatch trigger) — safe"
        HITS_OK=$((HITS_OK + 1))
      elif grep -qE '(if:[^)]*(staging|dev|development)|only:[^)]*(staging|dev|development)|environment:[^)]*(staging|dev|development))' "$f"; then
        pass "CI migration in $(basename "$f") gated to non-prod — safe"
        HITS_OK=$((HITS_OK + 1))
      # UNSAFE pattern: on push to main/master WITHOUT a gate
      elif grep -qE 'on:[[:space:]]*$|branches:.*(main|master)' "$f"; then
        fail "CI file $(basename "$f") auto-runs migrations on push to main/master without a manual gate — violates B1. Move to a separate workflow_dispatch workflow."
        HITS_FAIL=$((HITS_FAIL + 1))
      else
        warn "CI file $(basename "$f") runs migrations — verify gating (workflow_dispatch OR environment:staging)"
      fi
    fi
  done
  [ "$HITS_FAIL" -eq 0 ] && [ "$HITS_OK" -gt 0 ] && pass "all CI migration patterns are safe"
  [ "$HITS_FAIL" -eq 0 ] && [ "$HITS_OK" -eq 0 ] && pass "no migration execution detected in CI"
else
  warn "no CI workflow files detected — scaffold may be incomplete"
fi

# ----------------------------------------------------------------------
group 6b "Pre-commit hook present"
# ----------------------------------------------------------------------
PRECOMMIT_FOUND=0
for candidate in \
  "$PROJECT_DIR/.husky/pre-commit" \
  "$PROJECT_DIR/.pre-commit-config.yaml" \
  "$PROJECT_DIR/lefthook.yml" \
  "$PROJECT_DIR/.lefthook.yml" \
  "$PROJECT_DIR/hooks/pre-commit.sh"; do
  if [ -f "$candidate" ]; then
    PRECOMMIT_FOUND=1
    # Husky hook should be executable
    if [[ "$candidate" == *.husky/pre-commit ]] || [[ "$candidate" == */hooks/pre-commit.sh ]]; then
      if [ ! -x "$candidate" ]; then
        fail "pre-commit hook exists at $candidate but is not executable (run chmod +x)"
      else
        pass "pre-commit hook at $candidate (executable)"
      fi
    else
      pass "pre-commit config at $candidate"
    fi
    break
  fi
done
if [ "$PRECOMMIT_FOUND" -eq 0 ]; then
  fail "no pre-commit hook found (.husky/pre-commit, .pre-commit-config.yaml, lefthook.yml, or hooks/pre-commit.sh). Missing pre-commit = silent-shipping-without-discipline."
fi

# ----------------------------------------------------------------------
group 6c "Persisted queries for mobile/public GraphQL clients"
# ----------------------------------------------------------------------
# Only applies if References.md mentions mobile/public clients AND the project has GraphQL setup
if grep -qiE '(mobile|public|external clients|third.?party)' "$REFS" && [ -n "$SRC_DIR" ]; then
  GQL_DIRS=$(find "$SRC_DIR" -type d \( -iname 'graphql' -o -iname 'gql' \) 2>/dev/null)
  if [ -n "$GQL_DIRS" ]; then
    PERSISTED_FOUND=0
    for dir in $GQL_DIRS; do
      if grep -rqE '(persistedQuer|persistedDocument|usePersistedQueries|APQ)' "$dir" 2>/dev/null; then
        PERSISTED_FOUND=1
        break
      fi
    done
    if [ "$PERSISTED_FOUND" -eq 1 ]; then
      pass "persisted queries configured (mobile/public clients detected)"
    else
      fail "References.md mentions mobile/public GraphQL clients but no persisted-queries configuration found. Arbitrary query execution is a production attack surface."
    fi
  fi
fi

# ----------------------------------------------------------------------
group 6d "OpenTelemetry exporter configured (if OTel in References)"
# ----------------------------------------------------------------------
if grep -qiE '(opentelemetry|otel|otlp)' "$REFS" && [ -n "$SRC_DIR" ]; then
  OTEL_FOUND=0
  # Look for OTel SDK startup OR OTLP exporter configuration
  if grep -rqE '(@opentelemetry/sdk|NodeSDK|BatchSpanProcessor|OTLPTraceExporter|OTLPMetricExporter|TracerProvider|MeterProvider|openTelemetry\.trace\.getTracer)' "$SRC_DIR" 2>/dev/null; then
    OTEL_FOUND=1
  fi
  # Python / Go variants
  if grep -rqE '(opentelemetry\.sdk|OTLPSpanExporter|opentelemetry/contrib|otelhttp|otel\.GetTracerProvider)' "$SRC_DIR" 2>/dev/null; then
    OTEL_FOUND=1
  fi
  if [ "$OTEL_FOUND" -eq 1 ]; then
    pass "OpenTelemetry exporter configured"
  else
    fail "References.md names OpenTelemetry/OTLP but no SDK startup or exporter configuration found in source. OTel env vars defined-but-unused = silent failure."
  fi
fi

# ----------------------------------------------------------------------
group 7 "VERSION-LOG has scaffold entry"
# ----------------------------------------------------------------------
VLOG="$PROJECT_DIR/VERSION-LOG.md"
if [ -f "$VLOG" ]; then
  if grep -qiE '^## Scaffold|^### Scaffold|Phase 2' "$VLOG"; then
    pass "VERSION-LOG.md has a Scaffold entry"
  else
    warn "VERSION-LOG.md exists but no Scaffold entry found"
  fi
else
  warn "VERSION-LOG.md not found"
fi

# ----------------------------------------------------------------------
group 8 "Design Artifact section filled in (conv #27)"
# ----------------------------------------------------------------------
VD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/validate-design.sh"
if [ ! -f "$VD" ]; then
  fail "scripts/validate-design.sh missing beside this script"
elif [ "$DESIGN_REQUIRED" = "known-screen" ]; then
  if DESIGN_OUT="$(cd "$PROJECT_ROOT" && bash "$VD" --required known-screen 2>&1)"; then
    pass "References.md has one complete live Design Artifact section for the known-screen scaffold"
  else
    printf '%s\n' "$DESIGN_OUT" | sed 's/^/  /'
    fail "validate-design.sh --required known-screen reported errors (see lines above)"
  fi
elif DESIGN_OUT="$(cd "$PROJECT_ROOT" && bash "$VD" 2>&1)"; then
  pass "References.md Design Artifact section passes validate-design.sh (or the project has none)"
else
  printf '%s\n' "$DESIGN_OUT" | sed 's/^/  /'
  fail "validate-design.sh reported errors (see lines above)"
fi

# ----------------------------------------------------------------------
echo ""
echo "==="
[ "$BLOCKED" -gt 0 ] && echo "Not complete, blocked on the owner: $BLOCKED foundational system(s); group 1 names each owner action."
if [ "$ERRORS" -gt 0 ]; then
  printf "${RED}%d errors${NC}, %d warnings\n" "$ERRORS" "$WARNINGS"
  echo "Fix errors before committing."
  exit 1
else
  printf "${GREEN}Pass${NC}: 0 errors, %d warnings\n" "$WARNINGS"
  [ "$WARNINGS" -gt 0 ] && echo "Warnings are advisory. Review each — a warning may indicate a silent failure (see scaffolding/RED-FLAGS.md)."
  exit 0
fi
