# Archetype Hooks

Configured hooks can check specific tool events. A blocking hook only enforces the patterns it recognizes when the host actually invokes it. It does not establish universal compliance or runtime task authorization.

The framework ships one hook, the destructive-command guard, for the agent host the settings files target; the script adapts to any host with a before-tool-call hook. Add hooks when a project needs them, and only for a specific, high-value trigger.

Dated example: the shipped settings files target Claude Code and its `PreToolUse` event; verify the host's current event names and output rules in its own documentation before adapting them.

## Scripts

- `pre-destructive-warn.sh`: the guard, a before-tool-call hook on the shell tool. Blocks `rm -rf /`, `git reset --hard`, `git push --force`, `DROP TABLE`, `TRUNCATE`, `chmod -R 777`, `dd if=`, `mkfs.`, fork bombs, and similar. Exits 2 with the reason on stderr, which the host gives the agent.
- `post-task-verify.sh`: retired. It was a turn-end reminder written to stderr with exit 0, which the host does not give the agent. It stays only so settings that still register it do not fail on every turn; it reads its input and exits 0 without output. Remove such a registration.

The guard reads the host's event JSON from stdin.

## Install on the host these settings files target

Pick the settings file for the layout. The wrong one points at a path that does not exist, and the host then skips the hook without stopping the command.

### Path A: the engine in a subfolder (inject.sh)

```bash
mkdir -p .claude
cp archetype/templates/claude-settings.injected.json .claude/settings.json
chmod +x archetype/bootstrap/hooks/*.sh
```

### Path B: the older full-clone layout (the project root is the framework)

```bash
mkdir -p .claude
cp templates/claude-settings.root.json .claude/settings.json
chmod +x bootstrap/hooks/*.sh
```

The settings quote the project-folder placeholder. Keep it quoted when editing: unquoted, a project path with a space stops the command from starting, and the host lets the tool call run.

### Verify the install

From the project root: `python3 archetype/scripts/check-hooks.py` (Path B: `python3 scripts/check-hooks.py`). It runs the configured guard command as the host does, against a destructive and a harmless sample event, and expects block and allow. It also reports an unquoted placeholder, a registration of the retired reminder, and a settings file that git ignores (a machine-wide ignore rule can catch `settings.json`; the check names the rule) or has not committed. It proves what the command does when run that way, not that the host loaded the settings.

Restart the host so the settings load. Then ask the agent to run `echo "rm -rf /"`: the guard should block it.

## Install on other hosts

Other agent hosts have different hook mechanisms. The script still works; adapt the configuration to that host's convention for running a script before a tool call.

If the host has no hook system, the guard does not run. Record that enforcement gap; use service-side checks for controls that must not depend on agent behavior.

## Writing new hooks

Read the host's current lifecycle events and output rules before writing a hook; the names, the set, and what reaches the agent change. A hook reaches the agent only through the channel the host documents for that event.

Dated example: on 2026-09-24 the host these settings target documented that a hook blocks by exiting 2 with the reason on stderr; that the stderr of a hook that exits 0 goes to its debug log, not to the agent; that a hook command which cannot start is a non-blocking error, so the tool call proceeds; and that path placeholders in a shell-form command must be double-quoted.

Guidance when adding hooks:
- Block only when the cost of proceeding wrong is high, and put the reason where the agent sees it.
- A reminder the agent should act on belongs in the rules or in a gate that fails, not in output the host does not deliver.
- Keep scripts fast (sub-second). Hooks run on every trigger.
- Never add a hook that fires on every edit or every shell call without a specific, high-value trigger.
- Give each hook a sample input that makes it fire, and check it the way `scripts/check-hooks.py` checks the guard.

## Bypass

If the guard is wrong for a specific case, explain the scoped, safe intent and retry: it blocks on patterns, and the agent can restructure the command. Never disable the hook system globally to push a change through. If a hook is broken, fix the script.

## See also

- `../../templates/claude-settings.injected.json`: settings file for the engine-in-a-subfolder layout (paths include `archetype/`)
- `../../templates/claude-settings.root.json`: settings file for the older full-clone layout (paths from the root)
- `../../templates/hooks-spec.md`: the conceptual spec behind the guard
- Conventions #18 (verification) and #25 (automated enforcement): rationale for this directory
