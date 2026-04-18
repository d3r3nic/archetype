#!/bin/bash
# Validates Phase 3 (Develop) discipline: features use shared systems, have tests,
# have docs. Machine-verifiable gates replacing AI-discipline-only defenses.
# Run from project root before committing a feature.
#
# Checks:
#   1. No direct shared-class instantiation in features/ (bypassing getters)
#   2. No console-level output in features/ (use shared logger)
#   3. Every features/{name}/ has a matching test file
#   4. Every feature in feature-tree.md has docs/features/{name}.md
#   5. No `throw new Error(` in features (use AppError subclasses)

PROJECT_ROOT="$(pwd)"

# Find src directory (tolerant of layout variations)
SRC_DIR=""
for candidate in "$PROJECT_ROOT/src" "$PROJECT_ROOT/app" "$PROJECT_ROOT/lib"; do
  if [ -d "$candidate" ]; then SRC_DIR="$candidate"; break; fi
done

if [ -z "$SRC_DIR" ] || [ ! -d "$SRC_DIR/features" ]; then
  echo "Error: no src/features/ directory. Run from a project root with a features/ tree."
  exit 1
fi

FEATURES_DIR="$SRC_DIR/features"
TREE="$PROJECT_ROOT/feature-tree.md"
DOCS_FEATURES="$PROJECT_ROOT/docs/features"

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

echo "Develop Self-Test"
echo "Project: $PROJECT_ROOT"
echo "Features: $FEATURES_DIR"

# ----------------------------------------------------------------------
group 1 "No direct shared-class instantiation in features/"
# ----------------------------------------------------------------------
# Known shared-class getters: PrismaClient (db), Redis/IORedis, pino (logger)
# The pattern to flag: `new PrismaClient(` outside src/shared/
HITS=0
while IFS= read -r file; do
  # Skip test files — mocks may legitimately new up clients for fakes
  case "$file" in *.test.* | *_test.* | */tests/* | */__tests__/* ) continue ;; esac
  if grep -HnE 'new[[:space:]]+PrismaClient[[:space:]]*\(' "$file" 2>/dev/null; then
    fail "direct PrismaClient instantiation in feature code — use getDb() from src/shared/db/"
    HITS=$((HITS + 1))
  fi
  if grep -HnE 'new[[:space:]]+Redis[[:space:]]*\(|new[[:space:]]+IORedis[[:space:]]*\(' "$file" 2>/dev/null; then
    fail "direct Redis/IORedis instantiation in feature code — use the shared cache/redis wrapper"
    HITS=$((HITS + 1))
  fi
done < <(find "$FEATURES_DIR" -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.py' -o -name '*.go' \) 2>/dev/null)
[ "$HITS" -eq 0 ] && pass "no direct shared-class instantiation in features/"

# ----------------------------------------------------------------------
group 2 "No console-level output in features/"
# ----------------------------------------------------------------------
HITS=0
while IFS= read -r file; do
  case "$file" in *.test.* | *_test.* | */tests/* | */__tests__/* ) continue ;; esac
  if grep -qE 'console\.(log|error|warn|info|debug)' "$file" 2>/dev/null; then
    fail "console-level output in $(basename "$file") — use the shared logger (req.log or getLogger())"
    HITS=$((HITS + 1))
  fi
  # Python: print( outside entry points
  if [[ "$file" == *.py ]] && grep -qE '^[[:space:]]*print\(' "$file" 2>/dev/null; then
    fail "print() in $(basename "$file") — use the shared logger"
    HITS=$((HITS + 1))
  fi
done < <(find "$FEATURES_DIR" -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.py' \) 2>/dev/null)
[ "$HITS" -eq 0 ] && pass "no console-level output in features/"

# ----------------------------------------------------------------------
group 3 "Every feature has a test file"
# ----------------------------------------------------------------------
MISSING=0
for dir in "$FEATURES_DIR"/*/; do
  [ -d "$dir" ] || continue
  feature=$(basename "$dir")
  # Skip smoke-test-only features (health, _health, ping)
  case "$feature" in health|_health|ping|smoke) continue ;; esac
  # Find any test file in the feature directory
  if ! find "$dir" -maxdepth 2 -type f \( -name '*.test.*' -o -name '*_test.*' \) 2>/dev/null | grep -q .; then
    fail "feature '$feature' has no test file (expected $dir${feature}.test.*)"
    MISSING=$((MISSING + 1))
  fi
done
[ "$MISSING" -eq 0 ] && pass "every feature has at least one test file"

# ----------------------------------------------------------------------
group 4 "Every feature has a docs/features/ entry"
# ----------------------------------------------------------------------
if [ -f "$TREE" ] && [ -d "$DOCS_FEATURES" ]; then
  MISSING=0
  # Extract feature names from feature-tree.md's Features section
  # Pattern: rows with `| N | name | ...` under the Features section
  in_features=0
  while IFS= read -r line; do
    if echo "$line" | grep -qE '^## Features'; then in_features=1; continue; fi
    if [ "$in_features" -eq 1 ] && echo "$line" | grep -qE '^## '; then in_features=0; continue; fi
    [ "$in_features" -eq 0 ] && continue
    # Extract feature name (column 3 of markdown table)
    name=$(echo "$line" | awk -F'|' 'NF>=3 {gsub(/^[ \t]+|[ \t]+$/, "", $3); print $3}' | tr -d ' ')
    [ -z "$name" ] && continue
    case "$name" in Feature|-*|'') continue ;; esac
    # Skip smoke/health features
    case "$name" in health|_health|ping|smoke) continue ;; esac
    if [ ! -f "$DOCS_FEATURES/${name}.md" ]; then
      fail "feature '$name' in feature-tree.md but no docs/features/${name}.md"
      MISSING=$((MISSING + 1))
    fi
  done < "$TREE"
  [ "$MISSING" -eq 0 ] && pass "every feature in feature-tree.md has a docs/features/ entry"
elif [ ! -f "$TREE" ]; then
  warn "no feature-tree.md at project root — cannot cross-check features→docs"
elif [ ! -d "$DOCS_FEATURES" ]; then
  # No features documented yet is OK if the project is young
  warn "no docs/features/ directory yet — create one when you document your first feature"
fi

# ----------------------------------------------------------------------
group 5 "No 'throw new Error' in features (use AppError subclasses)"
# ----------------------------------------------------------------------
HITS=0
while IFS= read -r file; do
  case "$file" in *.test.* | *_test.* | */tests/* | */__tests__/* ) continue ;; esac
  if grep -qE 'throw[[:space:]]+new[[:space:]]+Error[[:space:]]*\(' "$file" 2>/dev/null; then
    warn "raw 'throw new Error(' in $(basename "$file") — use AppError subclass from src/shared/errors/"
    HITS=$((HITS + 1))
  fi
done < <(find "$FEATURES_DIR" -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' \) 2>/dev/null)
[ "$HITS" -eq 0 ] && pass "features use typed AppError subclasses (no raw Errors)"

# ----------------------------------------------------------------------
echo ""
echo "==="
if [ "$ERRORS" -gt 0 ]; then
  printf "${RED}%d errors${NC}, %d warnings\n" "$ERRORS" "$WARNINGS"
  echo "Fix errors before committing. See development/RED-FLAGS.md for context."
  exit 1
else
  printf "${GREEN}Pass${NC}: 0 errors, %d warnings\n" "$WARNINGS"
  exit 0
fi
