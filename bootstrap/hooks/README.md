# Archetype Hooks

Hooks enforce rules that must be followed every time. The CLAUDE.md enforcer achieves about 80% compliance. Hooks are deterministic — they run every time the AI reaches a trigger point.

This directory contains two starter hooks for use with Claude Code (and adaptable to other AI tools). More hooks can be added as project needs emerge, but keep the count low: every advisory hook is noise until it fires on something real.

## Scripts

- `pre-destructive-warn.sh` — PreToolUse hook on Bash. Blocks `rm -rf /`, `git reset --hard`, `git push --force`, `DROP TABLE`, `TRUNCATE`, `chmod -R 777`, `dd if=`, `mkfs.`, fork bombs, and similar. Exits 2 with an explanatory message that Claude sees and reasons about.
- `post-task-verify.sh` — Stop hook. Advisory checklist after Claude finishes a turn: build, tests, feature-tree, docs, commit. Non-blocking. Claude sees the reminder and can respond.

Both scripts read Claude Code's event JSON from stdin (the only way to access event data in a command hook).

## Install — Claude Code

1. Copy `templates/claude-settings.json` to `.claude/settings.json` at your project root (or merge with existing settings).
2. Verify the paths in `.claude/settings.json` point to the real scripts. If the framework is in an `archetype/` subfolder, paths should be `$CLAUDE_PROJECT_DIR/archetype/bootstrap/hooks/<script>.sh`. If the framework is at project root, remove the `archetype/` segment.
3. Make the scripts executable: `chmod +x archetype/bootstrap/hooks/*.sh`
4. Restart Claude Code so hooks are loaded.

Test: have Claude run `echo "rm -rf /"` — the destructive hook should block. Have Claude complete a simple task — the verify hook should print the checklist.

## Install — Cursor and others

Cursor and other tools have different hook mechanisms. The shell scripts still work; adapt the configuration format to your tool's convention. Check the tool's docs for a "run a script before a tool call" feature.

If your AI tool has no hook system, skip this directory. The CLAUDE.md enforcer carries the load. Without hooks, compliance drops from ~100% on covered patterns to ~80% overall.

## Writing new hooks

Claude Code exposes 21 lifecycle events as of 2026. Common ones:
- `PreToolUse` — before a tool call. Can block by exiting 2.
- `PostToolUse` — after a tool call. Advisory only.
- `Stop` — after Claude finishes responding. Good for turn-end reminders.
- `SessionStart`, `SessionEnd` — session boundaries.

Each hook receives event JSON on stdin. Output stderr to speak back to Claude. Output stdout for structured JSON responses if needed.

Guidance when adding hooks:
- Advisory hooks: echo a reminder, exit 0. Keep the message short — it becomes part of Claude's context.
- Blocking hooks: exit 2 and put the reason on stderr. Only block when the cost of proceeding wrong is high.
- Keep scripts fast (sub-second). Hooks run on every trigger.
- Never add a hook that fires on every edit or every bash call without a specific, high-value trigger. Noise wears down attention.

## Bypass

If a hook is wrong for a specific case:
- Blocking hook: explain the scoped, safe intent and retry. The hook blocks on patterns; Claude can restructure the command.
- Advisory hook: ignore the reminder if it doesn't apply. Review the hook if it fires on cases it shouldn't.

Never disable the hook system globally to push a commit through. If a hook is broken, fix the script.

## See also

- `../../templates/claude-settings.json` — Claude Code configuration template
- `../../templates/hooks-spec.md` — conceptual spec, behind these scripts
- Conventions #18 (verification) and #25 (automated enforcement) — rationale for this directory
