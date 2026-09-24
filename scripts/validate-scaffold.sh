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
#   4.  Audit log path exists if References.md mentions regulated data
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
# Only trigger on affirmative regulated-data declarations, not negative phrasing.
# Matches: "HIPAA" (standalone regime), "SOC 2 Type 2", "PCI compliance".
# Does NOT match: "Regulated data: none", "HIPAA: N/A", "no regulated data",
# "audit log: not applicable", etc.
REGULATED=0
# PROFILE.md holds the project's regulated-data fact (#30), one per repository: an endpoint
# folder looks above itself, as validate-profile.sh does. When it records "no", that settles it
# and no References.md wording can trigger these checks. Otherwise this folder's References.md
# decides, because an audit log lives in the unit that handles the data, not in every endpoint.
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
[ -f "$PROFILE_FILE" ] && PROFILE_REGULATED="$(tr -d '\r' < "$PROFILE_FILE" | awk '/^## / { exit } /^- Regulated data:/ { sub(/^- Regulated data:[ \t]*/, ""); print tolower($1); exit }')"
# Match regimes + require the line to NOT contain a negation after them
[ "$PROFILE_REGULATED" = "no" ] || while IFS= read -r line; do
  # Skip if the line looks like a negation
  if echo "$line" | grep -qiE '(none|N/A|not applicable|not required|no regulated|not regulated|skipped|deferred)'; then
    continue
  fi
  # Affirmative match: a regulated-data regime appears without negation on the same line
  if echo "$line" | grep -qiE '(HIPAA|SOC ?2|PCI( |-)?DSS|PCI compliance|GDPR compliance|regulated data (is|are|yes)|compliance: (yes|required))'; then
    REGULATED=1
    break
  fi
done < "$REFS"

if [ "$REGULATED" -eq 1 ]; then
  FOUND=0
  for candidate in \
    "$SRC_DIR/shared/audit-log" \
    "$SRC_DIR/shared/audit" \
    "$SRC_DIR/audit"; do
    [ -d "$candidate" ] && FOUND=1 && break
  done
  if [ "$FOUND" -eq 1 ]; then
    pass "audit log path exists (regulated data detected)"
  else
    fail "References.md declares regulated data but no audit-log path found (audit log must be SEPARATE from app log — see B4)"
  fi
elif [ "$PROFILE_REGULATED" = "no" ]; then
  pass "PROFILE.md records no regulated data — audit log check skipped"
else
  pass "no regulated data declared (or explicitly N/A) — audit log check skipped"
fi

# ----------------------------------------------------------------------
group 4b "In-memory audit store not shipped to regulated production"
# ----------------------------------------------------------------------
# If group 4 found regulated data AND the project has an audit-log path, check that it's
# not a test-only in-memory store. The same finding as group 4, not any mention of a regime
# or of the words "regulated data" (a Compliance section names them to say "no").
if [ "$REGULATED" -eq 1 ]; then
  if [ -n "$SRC_DIR" ]; then
    AUDIT_DIR=""
    for candidate in "$SRC_DIR/shared/audit-log" "$SRC_DIR/shared/audit" "$SRC_DIR/audit"; do
      [ -d "$candidate" ] && AUDIT_DIR="$candidate" && break
    done
    if [ -n "$AUDIT_DIR" ]; then
      # In-memory store pattern: class name or variable names suggesting ephemeral storage
      if grep -rqE '(InMemoryAuditStore|MemoryAuditStore|inMemoryStore|this\.records[[:space:]]*=[[:space:]]*\[\]|records:[[:space:]]*Array|push\(record\))' "$AUDIT_DIR" 2>/dev/null; then
        # Check if there's ALSO a real backing store adapter
        if grep -rqE '(PostgresAuditStore|PrismaAuditStore|DatabaseAuditStore|S3AuditStore|AppendOnlyStore|WORMStore|CloudAuditStore)' "$AUDIT_DIR" 2>/dev/null; then
          pass "audit log has both in-memory (test) and backing store (production) implementations"
        else
          fail "audit log uses in-memory store only but References.md declares regulated data. Ship to production = compliance failure. Add a real backing-store adapter (append-only table, WORM storage, or audit-log platform)."
        fi
      else
        pass "audit log implementation does not rely on in-memory-only storage"
      fi
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
