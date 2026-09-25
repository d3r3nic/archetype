#!/usr/bin/env python3
"""Regression tests for the shipped hook guard, its settings templates, and scripts/check-hooks.py."""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent
CHECK = ENGINE / 'scripts' / 'check-hooks.py'
GUARD = 'bootstrap/hooks/pre-destructive-warn.sh'
STUB = 'bootstrap/hooks/post-task-verify.sh'
# The settings the templates shipped before the placeholder was quoted, with the retired reminder.
OLD_SETTINGS = {'hooks': {
    'PreToolUse': [{'matcher': 'Bash', 'hooks': [{'type': 'command', 'command': '$CLAUDE_PROJECT_DIR/archetype/' + GUARD}]}],
    'Stop': [{'hooks': [{'type': 'command', 'command': '$CLAUDE_PROJECT_DIR/archetype/' + STUB}]}]}}


class Hooks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        home = Path(self.temp.name) / 'home'
        home.mkdir()
        # Keep the machine's git configuration and ignore rules out of the results.
        self.env = dict(os.environ, HOME=str(home), XDG_CONFIG_HOME=str(home / '.config'),
                        GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1')
        self.project = Path(self.temp.name) / 'a folder' / 'my project'
        self.project.mkdir(parents=True)

    def inject(self):
        result = subprocess.run(['bash', str(ENGINE / 'inject.sh'), str(self.project)], capture_output=True,
                                text=True, env=self.env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def settings(self, data):
        (self.project / '.claude').mkdir(exist_ok=True)
        (self.project / '.claude' / 'settings.json').write_text(json.dumps(data))

    def check(self, script=None):
        script = script or (self.project / 'archetype' / 'scripts' / 'check-hooks.py')
        return subprocess.run(['python3', str(script)], cwd=self.project, capture_output=True, text=True,
                              env=self.env)

    def guard_only(self, command, matcher='Bash', **extra):
        hook = dict({'type': 'command', 'command': command}, **extra)
        return {'hooks': {'PreToolUse': [{'matcher': matcher, 'hooks': [hook]}]}}

    def test_the_templates_register_only_the_guard_with_a_quoted_placeholder(self):
        for name, prefix in (('injected', 'archetype/'), ('root', '')):
            data = json.loads((ENGINE / 'templates' / ('claude-settings.%s.json' % name)).read_text())
            self.assertEqual(list(data['hooks']), ['PreToolUse'], name)
            [group] = data['hooks']['PreToolUse']
            self.assertEqual(group['matcher'], 'Bash')
            self.assertEqual([h['command'] for h in group['hooks']], ['"$CLAUDE_PROJECT_DIR"/' + prefix + GUARD])

    def test_the_installed_guard_blocks_and_allows_in_a_path_with_a_space(self):
        self.inject()
        (self.project / '.claude').mkdir()
        shutil.copy(self.project / 'archetype' / 'templates' / 'claude-settings.injected.json',
                    self.project / '.claude' / 'settings.json')
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('OK: the guard blocked a destructive sample (exit 2)', result.stdout)
        self.assertIn('OK: the guard allowed a harmless sample (exit 0)', result.stdout)
        self.assertNotIn('WARN', result.stdout)
        self.assertIn('does not show that the host loaded these settings', result.stdout)

    def test_the_old_unquoted_command_cannot_start_in_such_a_path_and_is_named(self):
        self.inject()
        self.settings(OLD_SETTINGS)
        result = self.check()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('WARN: the guard\'s command leaves the project-folder placeholder unquoted', result.stdout)
        self.assertIn('could not start (exit 127', result.stdout)
        self.assertIn('lets the command run', result.stdout)
        self.assertIn('splits at the space', result.stdout)
        self.assertIn('NOTE: a Stop registration still runs the retired turn-end reminder', result.stdout)

    def test_the_full_clone_layout_uses_the_root_template(self):
        (self.project / 'bootstrap' / 'hooks').mkdir(parents=True)
        shutil.copy(ENGINE / GUARD, self.project / GUARD)
        (self.project / '.claude').mkdir()
        shutil.copy(ENGINE / 'templates' / 'claude-settings.root.json', self.project / '.claude' / 'settings.json')
        result = self.check(CHECK)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_the_argument_form_runs_without_a_shell(self):
        self.inject()
        self.settings(self.guard_only('${CLAUDE_PROJECT_DIR}/archetype/' + GUARD, args=[]))
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn('unquoted', result.stdout)

    def test_a_guard_that_does_not_block_fails(self):
        self.inject()
        self.settings(self.guard_only('"$CLAUDE_PROJECT_DIR"/archetype/' + STUB + ' # ' + GUARD))
        result = self.check()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('returned exit 0 on a destructive sample, expected 2', result.stdout)

    def test_a_matcher_without_the_shell_tool_fails(self):
        self.inject()
        self.settings(self.guard_only('"$CLAUDE_PROJECT_DIR"/archetype/' + GUARD, matcher='Edit|Write'))
        result = self.check()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('do not include the shell tool', result.stdout)
        self.settings(self.guard_only('"$CLAUDE_PROJECT_DIR"/archetype/' + GUARD, matcher='Bash|Edit'))
        self.assertEqual(self.check().returncode, 0)

    def test_no_guard_registration_and_unreadable_settings_fail(self):
        self.inject()
        self.settings({'hooks': {}})
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn('no before-tool-call registration', result.stdout)
        (self.project / '.claude' / 'settings.json').write_text('{ not json')
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn('is not readable JSON', result.stdout)
        (self.project / '.claude' / 'settings.json').unlink()
        self.assertIn('not found', self.check().stdout)

    def test_settings_that_git_ignores_or_has_not_committed_are_reported(self):
        self.inject()
        self.settings(self.guard_only('"$CLAUDE_PROJECT_DIR"/archetype/' + GUARD))
        subprocess.run(['git', 'init', '-q'], cwd=self.project, env=self.env, check=True)
        self.assertIn('NOTE: .claude/settings.json is not committed yet', self.check().stdout)
        (self.project / '.gitignore').write_text('settings.json\n')
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('WARN: git ignores .claude/settings.json (.gitignore:1:settings.json', result.stdout)

    def test_a_negation_rule_that_un_ignores_the_settings_ends_the_warning(self):
        self.inject()
        self.settings(self.guard_only('"$CLAUDE_PROJECT_DIR"/archetype/' + GUARD))
        subprocess.run(['git', 'init', '-q'], cwd=self.project, env=self.env, check=True)
        (self.project / '.gitignore').write_text('settings.json\n!.claude/settings.json\n')
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn('WARN: git ignores', result.stdout)

    def test_settings_under_which_the_guard_never_blocks_fail(self):
        self.inject()
        guard = '"$CLAUDE_PROJECT_DIR"/archetype/' + GUARD
        cases = {
            'turned off': (dict(self.guard_only(guard), disableAllHooks=True), 'disableAllHooks'),
            'async': (self.guard_only(guard, **{'async': True}), 'runs in the background'),
            'asyncRewake': (self.guard_only(guard, asyncRewake=True), 'runs in the background'),
            'if': (self.guard_only(guard, **{'if': 'Bash(git *)'}), 'runs only for tool calls matching "Bash(git *)"'),
        }
        for name, (data, message) in cases.items():
            with self.subTest(name):
                self.settings(data)
                result = self.check()
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn(message, result.stdout)

    def test_matchers_are_read_as_the_host_reads_them(self):
        self.inject()
        guard = '"$CLAUDE_PROJECT_DIR"/archetype/' + GUARD
        for matcher, covered in (('Edit, Bash', True), ('Edit | Bash', True), ('Bash ', True), ('^Ba', True),
                                 ('.*', True), ('Edit|Write', False), ('Bas', False), ('(?i)bash', False),
                                 ('\\ABash\\Z', False), ('Bash{,1}', False), ('(?#c)Bash', False),
                                 ('(?>Bash)', False), ('Bas*+h', False)):
            with self.subTest(matcher=matcher):
                self.settings(self.guard_only(guard, matcher=matcher))
                result = self.check()
                self.assertEqual(result.returncode, 0 if covered else 1, result.stdout)

    def test_the_argument_form_substitutes_only_the_braced_placeholder(self):
        self.inject()
        self.settings(self.guard_only('$CLAUDE_PROJECT_DIR/archetype/' + GUARD, args=[]))
        result = self.check()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('could not start', result.stdout)

    def test_a_relative_command_path_is_named(self):
        self.inject()
        self.settings(self.guard_only('archetype/' + GUARD))
        result = self.check()
        self.assertIn('WARN: the guard\'s command uses a relative path', result.stdout)

    def test_a_relative_guard_after_an_interpreter_and_another_shell_are_named(self):
        self.inject()
        self.settings(self.guard_only('/bin/bash archetype/' + GUARD))
        self.assertIn("WARN: the guard's command uses a relative path", self.check().stdout)
        self.settings(self.guard_only('"$CLAUDE_PROJECT_DIR"/archetype/' + GUARD, shell='powershell'))
        self.assertIn('run the guard under "powershell"', self.check().stdout)

    def test_absolute_or_project_anchored_guard_paths_are_not_called_relative(self):
        self.inject()
        absolute = '"%s/archetype/%s"' % (self.project, GUARD)
        for command in (absolute, 'cd "$CLAUDE_PROJECT_DIR" && archetype/' + GUARD):
            with self.subTest(command=command):
                self.settings(self.guard_only(command))
                result = self.check()
                self.assertEqual(result.returncode, 0, result.stdout)
                self.assertNotIn('relative path', result.stdout)

    def test_the_argument_form_is_not_split_again(self):
        self.inject()
        self.settings(self.guard_only('/bin/bash', args=['%s/archetype/%s' % (self.project, GUARD)]))
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn('relative path', result.stdout)

    def test_the_retired_reminder_reads_its_input_and_says_nothing(self):
        result = subprocess.run(['bash', str(ENGINE / STUB)], input='{"hook_event_name": "Stop"}',
                                capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, '', ''))


if __name__ == '__main__':
    unittest.main()
