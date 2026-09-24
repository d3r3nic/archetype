# Hooks Specification

Hooks enforce rules that must be followed every time. Instruction files are advisory: an AI can miss or misread a rule. Hooks are deterministic — they run on every trigger.

## What ships with the framework

One hook ships, at `bootstrap/hooks/pre-destructive-warn.sh`: the destructive-command guard, which runs before a shell tool call and blocks known-destructive commands.

Two ready-to-copy settings files are included for Claude Code, the host the guard was written against: `templates/claude-settings.injected.json` (the engine in a subfolder, paths include `archetype/`) and `templates/claude-settings.root.json` (the older full-clone layout, paths from the project root). See `bootstrap/hooks/README.md` for which to use, and `scripts/check-hooks.py` to check an install.

A turn-end reminder used to ship. It printed a checklist on stderr and exited 0, which the host does not give the agent, and the completion rule in AGENTS.md already says it; it is retired, and its script remains only as a silent stand-in for settings that still register it.

The rest of this file is the conceptual spec: hooks a project may add. Each new hook is noise until it fires on something high-value.

## Host tool hook contract

Dated notes: verified against Claude Code's hooks documentation on 2026-09-24. Other hosts differ; re-verify the event names, what reaches the agent, and the blocking rules for the host in use at bootstrap.

- The host exposes lifecycle events, among them before a tool call (PreToolUse), after a tool call (PostToolUse), on stop (Stop), and session start and end (SessionStart, SessionEnd).
- Event data arrives as JSON on stdin. The guard parses it with `jq` when available; any JSON tool works.
- A hook blocks by exiting 2 with the reason on stderr, which the agent then sees. Which events a block can stop is event-specific; check the host's table before relying on it.
- The stderr of a hook that exits 0 goes to the host's debug log, not to the agent. A reminder written that way reaches no one.
- A hook command that cannot start (a missing path, or an unquoted path placeholder split at a space) is a non-blocking error: the tool call proceeds. Double-quote path placeholders in shell-form commands, or use the host's argument form.
- Keep scripts fast (sub-second). Hooks run on every trigger.

## Additional hook ideas (not included)

These were considered and not included. They can be added per project if the signal-to-noise ratio holds.

### After a file edit — feature doc freshness

Trigger: after a file write in a feature directory.
Action: if the feature's `docs/features/{name}.md` wasn't modified in the same session, remind.
Risk of noise: fires constantly during feature work where doc updates come at the end. A session-end sweep, or the develop gate, covers it better.

### After creating a feature directory

Trigger: after creating `src/features/{name}/`.
Action: remind to add the feature to `feature-tree.md`.
Risk of noise: low, but rare trigger; the develop gate already fails a feature folder with no row.

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
