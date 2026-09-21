# Hooks Specification

Hooks enforce rules that must be followed every time. Instruction files are advisory: an AI can miss or misread a rule. Hooks are deterministic — they run on every trigger.

## What ships with the framework

Two working hook scripts live at `bootstrap/hooks/`:

- `pre-destructive-warn.sh` — blocks destructive shell commands (runs before a tool call)
- `post-task-verify.sh` — prints a verification checklist after the AI finishes a turn (runs on stop)

Two ready-to-copy configs are included for Claude Code, the host these scripts were written against: `templates/claude-settings.injected.json` (for the `inject.sh` install path — paths include the `archetype/` subfolder segment) and `templates/claude-settings.root.json` (for the new-project clone install — paths from project root, no `archetype/` prefix). See `bootstrap/hooks/README.md` for which to use.

The rest of this file is the conceptual spec — additional hooks you may want to add. The framework ships only two by design: each new hook is noise until it fires on something high-value.

## Host tool hook contract

Dated notes: verified against Claude Code at the time of writing. Other hosts differ; re-verify the event names and blocking semantics for the host in use at bootstrap.

- The host exposes lifecycle events. The most-used, with Claude Code's names (the shipped configs use PreToolUse and Stop): before a tool call (PreToolUse), after a tool call (PostToolUse), on stop (Stop), on session start (SessionStart), on session end (SessionEnd).
- Event data arrives as JSON on stdin. The shipped scripts parse it with `jq` when available; any JSON tool works.
- The before-tool-call event (PreToolUse) is the only one that can block. Exit 2 with a message on stderr to block; the AI sees the stderr and reasons about it.
- Advisory hooks write stderr and exit 0. The AI sees the reminder, does not get blocked.
- Keep scripts fast (sub-second). Hooks run on every trigger.

## Additional hook ideas (not included)

These were considered and not included. They can be added per project if the signal-to-noise ratio holds.

### After a file edit — feature doc freshness

Trigger: after a file write in a feature directory.
Action: if the feature's `docs/features/{name}.md` wasn't modified in the same session, remind.
Risk of noise: fires constantly during feature work where doc updates come at the end. Better to run as part of a stop hook or a session-end sweep.

### After creating a feature directory

Trigger: after creating `src/features/{name}/`.
Action: remind to add the feature to `feature-tree.md`.
Risk of noise: low, but rare trigger. Consider rolling into the stop hook.

### Feature tree audit (standalone)

Not a host hook — run manually or on a schedule (e.g., a weekly CI job).

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

### Session start: bootstrap gate

Trigger: host session start.
Action: if `References.md` doesn't exist, print a reminder to run bootstrap.
Redundant with the bootstrap gate already in AGENTS.md, but removes a class of failure where the AI starts coding before reading the enforcer. Consider adding if bootstrap gate violations appear in session reviews.

## Principles for adding new hooks

- Every hook costs attention. Before adding, ask: what failure does this actually prevent? How often would it fire?
- Blocking hooks only where the cost of proceeding wrong is high (destructive shell, production deploys, credential exposure).
- Advisory hooks should fire rarely. A hook that fires every turn becomes background noise and is ignored.
- Every hook must be testable: have a small input that makes it fire, and verify.
- Record new hooks in `bootstrap/hooks/README.md` with the trigger, action, and rationale.

## Install

See `bootstrap/hooks/README.md` for install on the hosts it covers.

Setting up hooks is optional during bootstrap — they can be added at any time. Without hooks, the guidance in AGENTS.md carries the load, and it is advisory only.
