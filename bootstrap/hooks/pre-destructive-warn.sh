#!/bin/bash
# Archetype hook: PreToolUse (Bash matcher)
# Blocks destructive shell commands by matching the proposed command against
# known-dangerous patterns. Exits 2 to block with an explanation visible to Claude.
#
# Claude Code contract (2026):
#   - Event JSON arrives on stdin
#   - Exit 0: allow silently
#   - Exit 2: block the tool call; stderr is passed back to Claude as context
#   - Other non-zero: advisory warning, does not block

INPUT=$(cat)

# Parse the tool name and command. Use jq if available; fall back to grep.
if command -v jq >/dev/null 2>&1; then
  TOOL=$(printf '%s' "$INPUT" | jq -r '.tool_name // ""')
  COMMAND=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // ""')
else
  TOOL=$(printf '%s' "$INPUT" | sed -n 's/.*"tool_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
  COMMAND=$(printf '%s' "$INPUT" | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
fi

# Only inspect Bash tool calls
[ "$TOOL" = "Bash" ] || exit 0
[ -n "$COMMAND" ] || exit 0

# Destructive patterns. Order matters — most specific first.
PATTERNS=(
  'rm[[:space:]]+-[rRfd]*[rR][rRfd]*f[rRfd]*[[:space:]]+/($|[^a-zA-Z])'
  'rm[[:space:]]+-[rRfd]*[rR][rRfd]*f[rRfd]*[[:space:]]+~'
  'rm[[:space:]]+-[rRfd]*[rR][rRfd]*f[rRfd]*[[:space:]]+\*'
  'rm[[:space:]]+-[rRfd]*[rR][rRfd]*f[rRfd]*[[:space:]]+\.\*'
  'git[[:space:]]+reset[[:space:]]+--hard'
  'git[[:space:]]+push[[:space:]]+.*--force'
  'git[[:space:]]+push[[:space:]]+.*-f($|[[:space:]])'
  'git[[:space:]]+clean[[:space:]]+-[fdx]+'
  'git[[:space:]]+branch[[:space:]]+-D'
  'git[[:space:]]+checkout[[:space:]]+--[[:space:]]+\.'
  'DROP[[:space:]]+TABLE'
  'DROP[[:space:]]+DATABASE'
  'DROP[[:space:]]+SCHEMA'
  'TRUNCATE[[:space:]]+TABLE'
  'DELETE[[:space:]]+FROM[[:space:]]+[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]*;'
  'chmod[[:space:]]+-R[[:space:]]+777'
  'dd[[:space:]]+if='
  'mkfs\.'
  '>[[:space:]]*/dev/sd[a-z]'
  ':[[:space:]]*\(\)[[:space:]]*\{[[:space:]]*:[[:space:]]*\|'
)

for pattern in "${PATTERNS[@]}"; do
  if printf '%s' "$COMMAND" | grep -qE "$pattern"; then
    {
      echo "archetype hook blocked destructive command."
      echo "Pattern matched: $pattern"
      echo "Command: $COMMAND"
      echo ""
      echo "If this is intentional and scoped narrowly, state the scope and reason, then retry."
      echo "If not, stop and reconsider. Prefer safer alternatives:"
      echo "  - rm -rf X       → use trash/recycle bin or a narrower path"
      echo "  - git reset --hard → git stash, or a new branch from HEAD"
      echo "  - git push --force → git push --force-with-lease, and never on shared branches"
      echo "  - DROP / TRUNCATE → a reversible migration or a soft delete"
    } >&2
    exit 2
  fi
done

exit 0
