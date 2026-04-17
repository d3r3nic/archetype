#!/bin/bash
# Archetype hook: Stop (or PostToolUse)
# Advisory verification checklist after Claude finishes a task turn.
# Non-blocking. Stderr is visible to Claude, which can respond to the reminder.
#
# Claude Code contract (2026): stdin receives event JSON, exit 0 = proceed silently,
# stderr is forwarded to Claude. This hook always exits 0 (advisory only).

INPUT=$(cat)
_=${INPUT:-}

{
  echo "archetype verification checklist:"
  echo "  [ ] Build / typecheck passes"
  echo "  [ ] Tests pass (or new tests added and passing)"
  echo "  [ ] feature-tree.md updated if features were added, renamed, or removed"
  echo "  [ ] docs/features/*.md updated if feature behavior changed"
  echo "  [ ] docs/systems/*.md updated if foundational systems changed"
  echo "  [ ] References.md updated if paths, stack, or commands changed"
  echo "  [ ] Commit created per convention #2 (each verified change is a rollback point)"
  echo ""
  echo "Per convention #18 (verification), run the checks explicitly. Do not assume green."
} >&2

exit 0
