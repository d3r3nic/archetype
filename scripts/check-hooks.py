#!/usr/bin/env python3
"""Check the framework's destructive-command guard as this project installed it.

Run from the project root:  python3 archetype/scripts/check-hooks.py [--settings PATH]
(in the older full-clone layout: python3 scripts/check-hooks.py)

Reads the settings file (default .claude/settings.json) and finds each before-tool-call
registration that runs the guard (bootstrap/hooks/pre-destructive-warn.sh). Runs that command
the way the host runs a command hook: through /bin/sh (or directly, for a registration with
"args"), with the project folder exported as CLAUDE_PROJECT_DIR and used as the working
directory, and a synthetic event on stdin. Expects a destructive sample to be blocked (exit 2)
and a harmless one to be allowed (exit 0). The sample commands are only read by the guard;
nothing here runs them. Also reports an unquoted path placeholder, a registration of the
retired turn-end reminder, and a settings file that git ignores or does not track.

It shows what the configured command does when run this way. It does not show that the host
loaded these settings, or that another settings layer has not turned hooks off.
Exit 0 when every guard registration blocked and allowed as expected; 1 otherwise.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

GUARD = 'pre-destructive-warn.sh'
RETIRED = 'post-task-verify.sh'
SHELL_TOOL = 'Bash'
PLACEHOLDER = re.compile(r'\$\{?CLAUDE_PROJECT_DIR\}?')
TIMEOUT = 10


def event(command):
    return json.dumps({'hook_event_name': 'PreToolUse', 'tool_name': SHELL_TOOL,
                       'tool_input': {'command': command}})


def registrations(settings):
    """Yield (event name, matcher, hook) for every command hook in the settings."""
    hooks = settings.get('hooks')
    if not isinstance(hooks, dict):
        return
    for name, groups in hooks.items():
        if not isinstance(groups, list):
            continue
        for group in groups:
            if not isinstance(group, dict):
                continue
            for hook in group.get('hooks') or []:
                if isinstance(hook, dict) and hook.get('type') == 'command':
                    yield name, group.get('matcher', ''), hook


def text(hook):
    words = [str(hook.get('command', ''))]
    if isinstance(hook.get('args'), list):
        words += [str(a) for a in hook['args']]
    return ' '.join(words)


# How the host reads a matcher (its hooks documentation, 2026-09-24): empty or "*" matches every
# tool; a matcher of only letters, digits, "_", "-", spaces, "," and "|" is an exact name or a list
# of exact names separated by "|" or ","; anything else is a JavaScript regular expression tested
# unanchored. Python and JavaScript read some constructs differently; those are refused here.
EXACT = re.compile(r'[A-Za-z0-9_\- ,|]*')
NOT_JAVASCRIPT = re.compile(r'\(\?[A-Za-z<>#]|\\[AZz]|\{,|[*+?}]\+')


def covers_shell(matcher):
    """(covers the shell tool, reason when it does not or cannot be told)."""
    if matcher in ('', '*', None):
        return True, ''
    matcher = str(matcher)
    if EXACT.fullmatch(matcher):
        names = [name.strip() for name in re.split(r'[|,]', matcher)]
        return SHELL_TOOL in names, ''
    if NOT_JAVASCRIPT.search(matcher):
        return False, 'it uses syntax a JavaScript regular expression reads differently, so what the host matches is unknown'
    try:
        return re.search(matcher, SHELL_TOOL) is not None, ''
    except re.error:
        return False, 'it is not a valid regular expression'


def unquoted_placeholder(command):
    """True when a path placeholder in a shell-form command sits outside double quotes."""
    for match in PLACEHOLDER.finditer(command):
        before = command[:match.start()]
        quotes = len(re.findall(r'(?<!\\)"', before))
        if quotes % 2 == 0:
            return True
    return False


BRACED = re.compile(r'\$\{CLAUDE_PROJECT_DIR\}')


def run(hook, root, payload):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(root))
    if isinstance(hook.get('args'), list):
        # Without a shell the host substitutes only the braced placeholder; "$" passes verbatim.
        expand = lambda value: BRACED.sub(lambda _: str(root), str(value))
        argv = [expand(hook.get('command', ''))] + [expand(a) for a in hook['args']]
    else:
        argv = ['/bin/sh', '-c', str(hook.get('command', ''))]
    return subprocess.run(argv, input=payload, cwd=str(root), env=env, capture_output=True,
                          text=True, timeout=TIMEOUT)


def first_line(output):
    lines = [line for line in (output or '').splitlines() if line.strip()]
    return lines[0].strip() if lines else ''


def git(root, *args):
    return subprocess.run(['git', '-C', str(root)] + list(args), capture_output=True, text=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--settings', default='.claude/settings.json',
                        help='settings file, relative to the project root (default .claude/settings.json)')
    options = parser.parse_args()
    root = Path.cwd()
    path = root / options.settings
    failures = []

    def fail(message):
        failures.append(message)
        print('FAIL: ' + message)

    if not path.is_file():
        fail('%s not found: the framework\'s guard is not installed in this project' % options.settings)
        return 1
    try:
        settings = json.loads(path.read_text())
    except (OSError, ValueError) as error:
        fail('%s is not readable JSON: %s' % (options.settings, error))
        return 1
    if not isinstance(settings, dict):
        fail('%s does not hold a settings object' % options.settings)
        return 1

    if settings.get('disableAllHooks') is True:
        fail('%s sets disableAllHooks, which turns every hook off, the guard included' % options.settings)

    found = False
    for name, matcher, hook in registrations(settings):
        if RETIRED in text(hook):
            print('NOTE: a %s registration still runs the retired turn-end reminder (%s), which now '
                  'does nothing: remove that registration' % (name, RETIRED))
        if GUARD not in text(hook):
            continue
        if name != 'PreToolUse':
            fail('the guard is registered for %s; it only blocks as a before-tool-call (PreToolUse) hook' % name)
            continue
        found = True
        covered, why = covers_shell(matcher)
        if not covered:
            fail('the guard is registered for the tools "%s", which %s' % (matcher, why or
                 'do not include the shell tool (%s)' % SHELL_TOOL))
            continue
        if hook.get('async') is True or hook.get('asyncRewake') is True:
            fail('the guard runs in the background ("async" or "asyncRewake"), so it cannot block a command')
            continue
        if hook.get('if'):
            fail('the guard runs only for tool calls matching "%s", so it cannot block other commands' % hook['if'])
            continue
        command = str(hook.get('command', ''))
        script = next((word.strip('"\'') for word in text(hook).split() if GUARD in word), '')
        if script and not script.startswith('/') and not PLACEHOLDER.search(script):
            print('WARN: the guard\'s command uses a relative path; the host runs hooks from the session\'s '
                  'current folder, which is not always the project root. Name it through the project-folder '
                  'placeholder as the settings templates do.')
        if hook.get('shell') not in (None, '', 'sh', 'bash', '/bin/sh', '/bin/bash'):
            print('WARN: the registration asks the host to run the guard under "%s"; this check ran it through '
                  '/bin/sh, so what that shell does with it is not shown here.' % hook['shell'])
        loose = not isinstance(hook.get('args'), list) and unquoted_placeholder(command)
        if loose:
            print('WARN: the guard\'s command leaves the project-folder placeholder unquoted; a project '
                  'path with a space stops it from starting, and the host then lets the command run. '
                  'Quote it as the settings templates do.')
        for label, payload, expected in (('a destructive sample', event('rm -rf /'), 2),
                                         ('a harmless sample', event('ls'), 0)):
            try:
                result = run(hook, root, payload)
            except subprocess.TimeoutExpired:
                fail('the guard did not finish within %d seconds on %s' % (TIMEOUT, label))
                break
            except OSError as error:
                fail('the guard\'s command could not start: %s' % error)
                break
            if result.returncode == expected:
                print('OK: the guard %s %s (exit %d)' % ('blocked' if expected == 2 else 'allowed',
                                                        label, expected))
                continue
            if result.returncode in (126, 127):
                hint = (' The unquoted placeholder splits at the space in this project\'s path.'
                        if loose and ' ' in str(root) else '')
                fail('the guard\'s command could not start (exit %d: %s). The host treats that as a '
                     'non-blocking error and lets the command run.%s'
                     % (result.returncode, first_line(result.stderr), hint))
                break
            fail('the guard returned exit %d on %s, expected %d' % (result.returncode, label, expected))
    if not found and not failures:
        fail('no before-tool-call registration in %s runs the guard (%s)' % (options.settings, GUARD))

    inside = git(root, 'rev-parse', '--is-inside-work-tree')
    if inside.returncode == 0 and inside.stdout.strip() == 'true':
        # -q decides (a negation such as !.claude/settings.json un-ignores it); -v only names the rule.
        if git(root, 'check-ignore', '-q', '--', options.settings).returncode == 0:
            rule = git(root, 'check-ignore', '-v', '--', options.settings).stdout.strip()
            print('WARN: git ignores %s (%s); add !%s to the project\'s .gitignore so the guard is '
                  'committed with the project' % (options.settings, rule, options.settings))
        elif git(root, 'ls-files', '--error-unmatch', '--', options.settings).returncode != 0:
            print('NOTE: %s is not committed yet' % options.settings)

    if failures:
        print('Result: the guard is not working as installed; fix what failed above.')
        return 1
    print('Result: the guard blocked the destructive sample and allowed the harmless one when run as '
          'configured. This does not show that the host loaded these settings.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
