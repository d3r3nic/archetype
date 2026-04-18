# Hooks Specification

Hooks enforce rules that must be followed every time. CLAUDE.md rules achieve ~80% compliance. Hooks are deterministic — they run on every trigger.

## What ships with the framework

Two working hook scripts live at `bootstrap/hooks/`:

- `pre-destructive-warn.sh` — blocks destructive Bash commands (PreToolUse)
- `post-task-verify.sh` — prints a verification checklist after Claude finishes (Stop)

Two ready-to-copy Claude Code configs are shipped: `templates/claude-settings.injected.json` (for the `inject.sh` install path — paths include the `archetype/` subfolder segment) and `templates/claude-settings.root.json` (for the new-project clone install — paths from project root, no `archetype/` prefix). See `bootstrap/hooks/README.md` for which to use.

The rest of this file is the conceptual spec — additional hooks you may want to add. The framework ships only two by design: each new hook is noise until it fires on something high-value.

## Claude Code hook contract (2026)

- Claude Code exposes 21 lifecycle events. Most-used: `PreToolUse`, `PostToolUse`, `Stop`, `SessionStart`, `SessionEnd`.
- Event data arrives as JSON on stdin. Parse with `jq` if available.
- `PreToolUse` is the only hook that can block. Exit 2 with a message on stderr to block; Claude sees the stderr and reasons about it.
- Advisory hooks write stderr and exit 0. Claude sees the reminder, does not get blocked.
- Keep scripts fast (sub-second). Hooks run on every trigger.

## Additional hook ideas (not shipped)

These were considered and not shipped. They can be added per project if the signal-to-noise ratio holds.

### PostToolUse: after file edit — feature doc freshness

Trigger: after Write/Edit in a feature directory.
Action: if the feature's `docs/features/{name}.md` wasn't modified in the same session, remind.
Risk of noise: fires constantly during feature work where doc updates come at the end. Better to run as part of a Stop hook or a session-end sweep.

### PostToolUse: after create of feature directory

Trigger: after creating `src/features/{name}/`.
Action: remind to add the feature to `feature-tree.md`.
Risk of noise: low, but rare trigger. Consider rolling into Stop hook.

### Feature tree audit (standalone)

Not a Claude Code hook — run manually or on a schedule (e.g., weekly CI job).

```bash
#!/bin/bash
# Compare src/features/ directories against feature-tree.md and docs/features/
echo "=== Feature Tree Audit ==="
FEATURES_DIR="src/features"
TREE_FILE="feature-tree.md"
for dir in "$FEATURES_DIR"/*/; do
  feature=$(basename "$dir")
  if ! grep -q "$feature" "$TREE_FILE" 2>/dev/null; then
    echo "MISSING from tree: $feature"
  fi
  if [ ! -f "docs/features/$feature.md" ]; then
    echo "UNDOCUMENTED: $feature"
  fi
done
echo "=== Audit Complete ==="
```

### SessionStart: bootstrap gate

Trigger: Claude Code session start.
Action: if `References.md` doesn't exist, print a reminder to run bootstrap.
Redundant with the bootstrap gate already in CLAUDE.md, but removes a class of failure where Claude starts coding before reading the enforcer. Consider adding if bootstrap gate violations appear in session reviews.

## Principles for adding new hooks

- Every hook costs attention. Before adding, ask: what failure does this actually prevent? How often would it fire?
- Blocking hooks only where the cost of proceeding wrong is high (destructive shell, production deploys, credential exposure).
- Advisory hooks should fire rarely. A hook that fires every turn becomes background noise and is ignored.
- Every hook must be testable: have a small input that makes it fire, and verify.
- Record new hooks in `bootstrap/hooks/README.md` with the trigger, action, and rationale.

## Install

See `bootstrap/hooks/README.md` for install on Claude Code, Cursor, and other tools.

Setting up hooks is optional during bootstrap — they can be added at any time. Without hooks, CLAUDE.md enforcement carries the load (~80% compliance).
