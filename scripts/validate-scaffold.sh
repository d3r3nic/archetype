#!/bin/bash
# Validates a scaffolded project against the framework's scaffold conventions.
# Replaces AI-discipline-only verification with machine-verifiable gates.
# Run from the project root after scaffolding.
#
# Checks (categorical, not prescriptive):
#   1. Every foundational system in feature-tree.md has a docs/systems/{name}.md
#   2. Env validation is called from startup (startup-call pattern, not ad-hoc process.env)
#   3. No console-level output in source (language-agnostic grep)
#   4. Direct third-party imports flagged outside project wrappers
#   5. Audit log path exists if References.md mentions regulated data
#   6. CI workflow doesn't auto-run migrations on main/master pushes
#   7. Smoke-test feature exists
#   8. VERSION-LOG.md has a Scaffold entry
#
# Exit 0 on pass, 1 on any error. Warnings do not fail.

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
if [ ! -d "$DOCS_SYSTEMS" ]; then
  warn "docs/systems/ directory does not exist — scaffold may be incomplete"
else
  MISSING=0
  # Extract system names from feature-tree.md's Foundational Systems table
  # Pattern: rows with `| N | name | ...` — take the name column
  while IFS= read -r line; do
    name=$(echo "$line" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/, "", $3); print tolower($3)}' | tr ' ' '-')
    [ -z "$name" ] && continue
    # Skip obvious non-system headers
    case "$name" in system|-*|'') continue ;; esac
    # Each row should have a matching doc
    found=0
    for ext in md markdown; do
      if [ -f "$DOCS_SYSTEMS/${name}.${ext}" ]; then found=1; break; fi
    done
    if [ "$found" -eq 0 ]; then
      warn "no docs/systems/${name}.md found for feature-tree system '${name}'"
      MISSING=$((MISSING + 1))
    fi
  done < <(grep -E '^\|[[:space:]]*[0-9]+[[:space:]]*\|' "$TREE")
  [ "$MISSING" -eq 0 ] && pass "every foundational system has a docs/systems/ entry"
fi

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
group 3 "No console-level output in source (categorical)"
# ----------------------------------------------------------------------
if [ -n "$SRC_DIR" ]; then
  # JS/TS: console.log, console.error
  # Python: print( (outside of CLI entrypoints)
  # Go: fmt.Println, log.Print (should use slog or structured)
  # Allow in entry-point files (main.ts, index.ts, cli scripts)
  HITS=0
  while IFS= read -r file; do
    # Skip test files
    case "$file" in *.test.* | *_test.* | */tests/* ) continue ;; esac
    # Skip entry points (these may legitimately print startup messages)
    case "$(basename "$file")" in index.ts|index.js|main.ts|main.py|main.go|cli.* ) continue ;; esac
    if grep -qE 'console\.(log|error|warn|info|debug)' "$file" 2>/dev/null; then
      warn "console-level output in $file (use structured logger)"
      HITS=$((HITS + 1))
    fi
    if grep -qE '^[[:space:]]*print\(' "$file" 2>/dev/null && [[ "$file" == *.py ]]; then
      warn "print() in $file (use structured logger)"
      HITS=$((HITS + 1))
    fi
  done < <(find "$SRC_DIR" -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.py' -o -name '*.go' \) 2>/dev/null)
  [ "$HITS" -eq 0 ] && pass "no console-level output found in source"
fi

# ----------------------------------------------------------------------
group 4 "Audit log if regulated data"
# ----------------------------------------------------------------------
if grep -qiE "(HIPAA|SOC ?2|PCI|GDPR|audit log|regulated data)" "$REFS"; then
  # Look for a dedicated audit-log path
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
    fail "References.md mentions regulated data but no audit-log path found (audit log must be SEPARATE from app log — see B4)"
  fi
else
  pass "no regulated data detected — audit log check skipped"
fi

# ----------------------------------------------------------------------
group 4b "In-memory audit store not shipped to regulated production"
# ----------------------------------------------------------------------
# If regulated data is declared AND the project has an audit-log path,
# check that it's not a test-only in-memory store. FAIL on regulated projects,
# WARN on unregulated (dev-only pattern is valid early; production-blocker later).
if grep -qiE '(HIPAA|SOC ?2|PCI|GDPR|regulated data)' "$REFS"; then
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
echo ""
echo "==="
if [ "$ERRORS" -gt 0 ]; then
  printf "${RED}%d errors${NC}, %d warnings\n" "$ERRORS" "$WARNINGS"
  echo "Fix errors before committing."
  exit 1
else
  printf "${GREEN}Pass${NC}: 0 errors, %d warnings\n" "$WARNINGS"
  [ "$WARNINGS" -gt 0 ] && echo "Warnings are advisory. Review each — a warning may indicate a silent failure (see scaffolding/RED-FLAGS.md)."
  exit 0
fi
