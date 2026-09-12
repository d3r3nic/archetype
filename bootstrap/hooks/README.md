# Archetype Hooks

Configured hooks can check specific tool events. A blocking hook only enforces the patterns it recognizes when the host actually invokes it; an advisory hook only reminds. Neither establishes universal compliance or runtime task authorization.

This directory contains two starter hooks for the agent host the shipped settings files target, adaptable to any host with a hook system. More hooks can be added as project needs emerge, but keep the count low: every advisory hook is noise until it fires on something real.

Dated example: the shipped configs target Claude Code and its `PreToolUse` and `Stop` events; verify the host's current event names in its own documentation before adapting them.

## Scripts

- `pre-destructive-warn.sh` — pre-tool-call hook on the shell tool. Blocks `rm -rf /`, `git reset --hard`, `git push --force`, `DROP TABLE`, `TRUNCATE`, `chmod -R 777`, `dd if=`, `mkfs.`, fork bombs, and similar. Exits 2 with an explanatory message the agent sees and reasons about.
- `post-task-verify.sh` — turn-end hook. Advisory checklist after the agent finishes a turn: build, tests, feature-tree, docs, commit. Non-blocking. The agent sees the reminder and can respond.

Both scripts read the host's event JSON from stdin (the only way to access event data in a command hook).

## Install — the host these settings files target

Two install paths exist depending on how the framework lives in your project. Pick the right settings file — the wrong one makes the host silently skip the hooks (no error, just no enforcement).

### Path A — framework injected as a subfolder (after running `./inject.sh`)

Your project has an `archetype/` subfolder containing the framework. Use this settings file:

```bash
mkdir -p .claude
cp archetype/templates/claude-settings.injected.json .claude/settings.json
chmod +x archetype/bootstrap/hooks/*.sh
```

### Path B — framework cloned as the project root (new-project clone)

Your project root IS the framework (no `archetype/` subfolder). Use this settings file:

```bash
mkdir -p .claude
cp templates/claude-settings.root.json .claude/settings.json
chmod +x bootstrap/hooks/*.sh
```

### Verify the install

Before trusting hooks are running, verify the path resolves:

```bash
ls $(jq -r '.hooks.PreToolUse[0].hooks[0].command' .claude/settings.json | sed "s|\$CLAUDE_PROJECT_DIR|$PWD|")
```

This should print the script path. If it errors with "No such file or directory," you picked the wrong settings file — the host will NOT warn you, hooks will silently no-op. Switch to the other variant.

Restart the host so hooks are loaded.

Test: have the agent try to run `echo "rm -rf /"` — the destructive hook should block. Have the agent complete a simple task — the verify hook should print the checklist.

## Install — other hosts

Other agent hosts have different hook mechanisms. The shell scripts still work; adapt the configuration format to that host's convention. Check its docs for a "run a script before a tool call" feature.

If the host has no hook system, these hooks do not run. Record that enforcement gap; use service-side checks for controls that must not depend on agent behavior.

## Writing new hooks

Read the host's current lifecycle-event list before writing a hook; the names and the set change. The kinds worth knowing: before a tool call (can block by exiting 2), after a tool call (advisory only), turn end after the agent finishes responding (good for verification reminders), and session boundaries at start and end.

Dated example: the host these configs target named those events `PreToolUse`, `PostToolUse`, `Stop`, `SessionStart` and `SessionEnd`.

Each hook receives event JSON on stdin. Output stderr to speak back to the agent. Output stdout for structured JSON responses if needed.

Guidance when adding hooks:
- Advisory hooks: echo a reminder, exit 0. Keep the message short — it becomes part of the agent's context.
- Blocking hooks: exit 2 and put the reason on stderr. Only block when the cost of proceeding wrong is high.
- Keep scripts fast (sub-second). Hooks run on every trigger.
- Never add a hook that fires on every edit or every bash call without a specific, high-value trigger. Noise wears down attention.

## Bypass

If a hook is wrong for a specific case:
- Blocking hook: explain the scoped, safe intent and retry. The hook blocks on patterns; the agent can restructure the command.
- Advisory hook: ignore the reminder if it doesn't apply. Review the hook if it fires on cases it shouldn't.

Never disable the hook system globally to push a commit through. If a hook is broken, fix the script.

## See also

- `../../templates/claude-settings.injected.json` — host settings file for `inject.sh` installs (paths include `archetype/`)
- `../../templates/claude-settings.root.json` — host settings file for new-project clone installs (paths from root)
- `../../templates/hooks-spec.md` — conceptual spec, behind these scripts
- Conventions #18 (verification) and #25 (automated enforcement) — rationale for this directory
