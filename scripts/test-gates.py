#!/usr/bin/env python3
"""Exercise the gates that read feature-tree.md (validate-develop.sh, validate-scaffold.sh,
pulse-inspect.sh) against projects built in a temporary folder, and the shipped template."""

from pathlib import Path
import json
import re
import subprocess
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]
DEVELOP = SOURCE / 'scripts' / 'validate-develop.sh'
SCAFFOLD = SOURCE / 'scripts' / 'validate-scaffold.sh'
PULSE = SOURCE / 'scripts' / 'pulse-inspect.sh'
TEMPLATE = SOURCE / 'templates' / 'feature-tree.md'
BASH = '/bin/bash'
ANSI = re.compile(r'\x1b\[[0-9;]*m')

PLACEHOLDER_ROW = '| 01 | [name] | [location] | [routes] | [systems] | [status] | docs/features/[name].md |'
SYSTEMS_HEADER = '| # | Name | Convention | Location | Status | Docs |'
FEATURES_HEADER = '| # | Feature | Location | Routes | Systems Used | Status | Docs |'
# Explanatory lines with pipes, as the template once carried them. A parser must ignore them
# on its own: the cleaned template no longer holds any, so it cannot prove the rule alone.
PIPE_PROSE = (
    '**Column order is contract.** Pulse reads: `# | Feature | Location | Routes | Systems Used`.\n'
    '\n'
    'Status values: not started | in progress | implemented | needs audit\n'
)


def group(stdout, gid):
    """The non-empty lines a validator printed under its group gid."""
    text = ANSI.sub('', stdout)
    match = re.search(r'^\[%s\] [^\n]*\n(.*?)(?=^\[|^===|\Z)' % re.escape(gid), text, re.M | re.S)
    if match is None:
        raise AssertionError('group %s was not printed:\n%s' % (gid, text))
    return [line for line in match.group(1).splitlines() if line.strip()]


def section(text, heading):
    """Lines of one level-two section of a markdown text."""
    lines, inside = [], False
    for line in text.splitlines():
        if line.startswith('## '):
            inside = line == '## ' + heading
            continue
        if inside:
            lines.append(line)
    return lines


def features_tree(rows, prose=''):
    return (
        '# Feature Tree\n\n## Features\n\n' + prose + '\n'
        + FEATURES_HEADER + '\n|---|---|---|---|---|---|---|\n'
        + ''.join(row + '\n' for row in rows)
        + '\n## Audit Log\n\n| Date | Scope | Findings |\n|---|---|---|\n'
    )


def systems_tree(rows, header=SYSTEMS_HEADER, prose=''):
    cells = header.count('|') - 1
    return (
        '# Feature Tree\n\n## Foundational Systems\n\n' + prose + '\n'
        + header + '\n' + '|---' * cells + '|\n'
        + ''.join(row + '\n' for row in rows)
        + '\n## Features\n\n' + FEATURES_HEADER + '\n|---|---|---|---|---|---|---|\n'
    )


class TemplateText(unittest.TestCase):
    def setUp(self):
        self.text = TEMPLATE.read_text()

    def test_explanatory_lines_in_both_tables_carry_no_pipes(self):
        for heading in ('Foundational Systems', 'Features'):
            with self.subTest(section=heading):
                lines = section(self.text, heading)
                self.assertTrue(any(line.startswith('|') for line in lines), heading)
                for line in lines:
                    if not line.startswith('|'):
                        self.assertNotIn('|', line)

    def test_table_headers_are_the_parse_contract(self):
        lines = self.text.splitlines()
        self.assertIn(SYSTEMS_HEADER, lines)
        self.assertIn(FEATURES_HEADER, lines)
        self.assertIn(PLACEHOLDER_ROW, lines)

    def test_status_vocabulary_names_the_blocked_state(self):
        status = [line for line in section(self.text, 'Features') if line.startswith('Status values:')]
        self.assertEqual(len(status), 1, status)
        self.assertIn('`blocked (owner: <action>)`', status[0])

    def test_systems_notes_record_the_blocked_state(self):
        notes = [line for line in section(self.text, 'Foundational Systems') if 'blocked (owner: <action>)' in line]
        self.assertEqual(len(notes), 1, notes)
        for phrase in ('opening an account', 'approving a recurring cost', 'accepting terms',
                       'names the action and what was built meanwhile', '(#29)'):
            self.assertIn(phrase, notes[0])


class DevelopGate(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='archetype-develop-')
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        (self.project / 'src' / 'features').mkdir(parents=True)
        (self.project / 'docs' / 'features').mkdir(parents=True)

    def check(self, tree):
        (self.project / 'feature-tree.md').write_text(tree)
        return subprocess.run([BASH, str(DEVELOP)], cwd=self.project, text=True, capture_output=True)

    def document(self, name):
        (self.project / 'docs' / 'features' / (name + '.md')).write_text('# %s\n' % name)

    def test_shipped_template_fails_on_its_placeholder_row_only(self):
        result = self.check(TEMPLATE.read_text())
        self.assertEqual(result.returncode, 1, result.stdout)
        lines = group(result.stdout, '4')
        self.assertEqual(lines, [
            'FAIL: feature row 01 is the placeholder row left from the template (name [name]); '
            'replace it with a real feature or delete it',
        ])
        for word in ('Location', 'implemented', 'no docs/features/[name].md'):
            self.assertNotIn(word, ANSI.sub('', result.stdout))
        self.assertIn('1 errors, 0 warnings', ANSI.sub('', result.stdout))

    def test_template_with_one_real_row_passes(self):
        text = TEMPLATE.read_text()
        self.assertIn(PLACEHOLDER_ROW, text)
        text = text.replace(PLACEHOLDER_ROW, '| 01 | sign-in | src/features/sign-in | /sign-in | Auth & Security | implemented | docs/features/sign-in.md |')
        feature = self.project / 'src' / 'features' / 'sign-in'
        feature.mkdir()
        (feature / 'sign-in.test.ts').write_text('// behavior test\n')
        self.document('sign-in')
        result = self.check(text)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(group(result.stdout, '4'), ['OK: every feature in feature-tree.md has a docs/features/ entry'])

    def test_real_row_without_its_document_is_named(self):
        text = TEMPLATE.read_text().replace(PLACEHOLDER_ROW, '| 01 | sign-in | src/features/sign-in | /sign-in | Auth & Security | in progress | docs/features/sign-in.md |')
        result = self.check(text)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(group(result.stdout, '4'), ["FAIL: feature 'sign-in' in feature-tree.md but no docs/features/sign-in.md"])

    def test_pipe_prose_in_the_features_section_is_not_a_feature(self):
        self.document('sign-in')
        result = self.check(features_tree(['| 01 | sign-in | src/features/sign-in | /sign-in | Auth | implemented | docs/features/sign-in.md |'], PIPE_PROSE))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn('Location', result.stdout)
        self.assertNotIn("'implemented'", result.stdout)

    def test_pipe_line_whose_first_cell_is_not_a_number_is_not_a_feature(self):
        self.document('sign-in')
        result = self.check(features_tree([
            '| 01 | sign-in | src/features/sign-in | /sign-in | Auth | implemented | docs/features/sign-in.md |',
            '| F2 | stray | src/features/stray | /stray | Auth | implemented | docs/features/stray.md |',
        ]))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn('stray', result.stdout)

    def test_bold_number_row_is_still_a_feature(self):
        result = self.check(features_tree(['| **02** | reports | src/features/reports | /reports | Auth | implemented | docs/features/reports.md |']))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(group(result.stdout, '4'), ["FAIL: feature 'reports' in feature-tree.md but no docs/features/reports.md"])

    def test_last_row_without_a_final_newline_is_read(self):
        tree = ('# Feature Tree\n\n## Features\n\n' + FEATURES_HEADER + '\n|---|---|---|---|---|---|---|\n'
                '| 01 | reports | src/features/reports | /reports | Auth | implemented | docs/features/reports.md |')
        result = self.check(tree)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("feature 'reports' in feature-tree.md but no docs/features/reports.md", result.stdout)

    def test_placeholder_row_is_reported_whatever_its_other_cells_hold(self):
        result = self.check(features_tree(['| 03 | [feature name] | src/features/x | /x | Auth | implemented | docs/features/x.md |']))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(group(result.stdout, '4'), [
            'FAIL: feature row 03 is the placeholder row left from the template (name [feature name]); '
            'replace it with a real feature or delete it',
        ])


class ScaffoldGate(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='archetype-scaffold-')
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        (self.project / 'References.md').write_text('# References\n\n## Tech Stack\n\n- Language: recorded\n')
        (self.project / 'VERSION-LOG.md').write_text('# Version Log\n\n## Scaffold\n\nComplete.\n')
        hooks = self.project / 'hooks'
        hooks.mkdir()
        hook = hooks / 'pre-commit.sh'
        hook.write_text('#!/bin/sh\nexit 0\n')
        hook.chmod(0o755)
        (self.project / 'docs' / 'systems').mkdir(parents=True)

    def check(self, tree, newline='\n'):
        (self.project / 'feature-tree.md').write_bytes(tree.replace('\n', newline).encode())
        return subprocess.run([BASH, str(SCAFFOLD)], cwd=self.project, text=True, capture_output=True)

    def page(self, relative):
        path = self.project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('# page\n')

    def template_pages(self):
        pages = re.findall(r'docs/systems/[a-z0-9-]+\.md', '\n'.join(section(TEMPLATE.read_text(), 'Foundational Systems')))
        self.assertEqual(len(pages), 16, pages)
        return pages

    def test_template_pages_named_in_the_docs_column_are_found(self):
        for page in self.template_pages():
            self.page(page)
        result = self.check(TEMPLATE.read_text())
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(group(result.stdout, '1'), ['OK: every foundational system has a docs/systems/ entry'])
        self.assertNotIn('&', '\n'.join(group(result.stdout, '1')))

    def test_missing_declared_page_is_reported_by_its_exact_path(self):
        for page in self.template_pages():
            if page != 'docs/systems/git.md':
                self.page(page)
        self.page('docs/systems/git-hooks.md')  # a page under the derived name must not stand in
        result = self.check(TEMPLATE.read_text())
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(group(result.stdout, '1'), [
            "WARN: system 'Git & Hooks' has no document at docs/systems/git.md, the path its Docs column names",
        ])

    def test_docs_column_is_found_by_its_header(self):
        layouts = {
            'notes before docs': ('| # | Name | Convention | Location | Status | Notes | Docs |',
                                  '| 01 | Git & Hooks | #2 | hooks/ | implemented | docs/notes/none.md | docs/systems/git.md |'),
            'docs before notes': ('| # | Name | Convention | Location | Status | Docs | Notes |',
                                  '| 01 | Git & Hooks | #2 | hooks/ | implemented | docs/systems/git.md | docs/notes/none.md |'),
        }
        self.page('docs/systems/git.md')
        for label, (header, row) in layouts.items():
            with self.subTest(layout=label):
                result = self.check(systems_tree([row], header))
                self.assertEqual(group(result.stdout, '1'), ['OK: every foundational system has a docs/systems/ entry'])

    def test_slug_drops_punctuation_when_no_path_is_declared(self):
        header = '| # | Name | Convention | Location | Status |'
        rows = [
            '| 01 | Git & Hooks | #2 | hooks/ | implemented |',
            '| 02 | CI/CD & Performance | #15 | ci/ | implemented |',
            '| 03 | Design Foundation & Interface Craft | #27 | design/ | implemented |',
        ]
        missing = self.check(systems_tree(rows, header))
        self.assertEqual(group(missing.stdout, '1'), [
            "WARN: system 'Git & Hooks' has no document at docs/systems/git-hooks.md (named after the system, since its row names no Docs path)",
            "WARN: system 'CI/CD & Performance' has no document at docs/systems/ci-cd-performance.md (named after the system, since its row names no Docs path)",
            "WARN: system 'Design Foundation & Interface Craft' has no document at docs/systems/design-foundation-interface-craft.md (named after the system, since its row names no Docs path)",
        ])
        for page in ('git-hooks', 'ci-cd-performance', 'design-foundation-interface-craft'):
            self.page('docs/systems/%s.md' % page)
        found = self.check(systems_tree(rows, header))
        self.assertEqual(group(found.stdout, '1'), ['OK: every foundational system has a docs/systems/ entry'])

    def test_empty_docs_cell_falls_back_to_the_slug(self):
        self.page('docs/systems/file-storage.md')
        result = self.check(systems_tree(['| 07 | File Storage | #9 | storage/ | implemented |  |']))
        self.assertEqual(group(result.stdout, '1'), ['OK: every foundational system has a docs/systems/ entry'])

    def test_older_page_name_is_still_accepted(self):
        header = '| # | Name | Convention | Location | Status |'
        self.page('docs/systems/git-&-hooks.md')
        result = self.check(systems_tree(['| 01 | Git & Hooks | #2 | hooks/ | implemented |'], header))
        self.assertEqual(group(result.stdout, '1'), ['OK: every foundational system has a docs/systems/ entry'])

    def test_docs_cell_that_is_not_a_plain_local_path_gets_a_diagnostic(self):
        self.page('docs/systems/git.md')
        self.page('docs/systems/git-hooks.md')
        for cell in ('[git](docs/systems/git.md)', '`docs/systems/git.md`', 'https://example.com/git.md',
                     '/docs/systems/git.md', 'docs/systems/git.md docs/systems/ci.md', '[path]', 'docs/systems/git'):
            with self.subTest(cell=cell):
                result = self.check(systems_tree(['| 01 | Git & Hooks | #2 | hooks/ | implemented | %s |' % cell]))
                self.assertEqual(result.returncode, 0, result.stdout)
                self.assertEqual(group(result.stdout, '1'), [
                    "WARN: system 'Git & Hooks': its Docs cell '%s' is not a plain local .md path; "
                    "write the page's path from the project root, like docs/systems/git-hooks.md" % cell,
                ])

    def test_blocked_system_is_reported_with_its_owner_action_and_its_page_is_read(self):
        row = '| 17 | Payments | #9 | src/shared/payments | blocked (owner: open the payments account) | docs/systems/payments.md |'
        missing = self.check(systems_tree([row]))
        self.assertEqual(missing.returncode, 0, missing.stdout)
        self.assertEqual(group(missing.stdout, '1'), [
            "WARN: system 'Payments' is blocked on the owner: open the payments account. It is not built; features that need it wait (#29)",
            "WARN: system 'Payments' has no document at docs/systems/payments.md, the path its Docs column names; "
            "a system blocked on the owner keeps a page that names the owner action and what was built meanwhile (#29)",
        ])
        self.page('docs/systems/payments.md')
        present = self.check(systems_tree([row]))
        self.assertEqual(present.returncode, 0, present.stdout)
        self.assertEqual(group(present.stdout, '1'), [
            "WARN: system 'Payments' is blocked on the owner: open the payments account. It is not built; features that need it wait (#29)",
            'OK: every foundational system has a docs/systems/ entry',
        ])
        self.assertIn('Not built, blocked on the owner: 1 foundational system(s); group 1 names each owner action.', present.stdout)

    def test_blocked_status_written_in_code_quotes_or_bold_is_read(self):
        self.page('docs/systems/mail.md')
        for status in ('`blocked (owner: approve the mail plan)`', '**blocked (owner: approve the mail plan)**'):
            with self.subTest(status=status):
                result = self.check(systems_tree(['| **18** | Mail | #9 | src/shared/mail | %s |  |' % status]))
                self.assertEqual(group(result.stdout, '1'), [
                    "WARN: system 'Mail' is blocked on the owner: approve the mail plan. It is not built; features that need it wait (#29)",
                    'OK: every foundational system has a docs/systems/ entry',
                ])

    def test_blocked_without_an_owner_action_is_named(self):
        self.page('docs/systems/search.md')
        for status, line in (
            ('blocked', "WARN: system 'Search' has Status 'blocked', which is not the recorded form blocked (owner: <action>); name the owner action there (#29)"),
            ('blocked (owner: )', "WARN: system 'Search' is blocked (Status 'blocked (owner: )') but names no owner action; write blocked (owner: <action>) (#29)"),
        ):
            with self.subTest(status=status):
                result = self.check(systems_tree(['| 19 | Search | #9 | src/shared/search | %s | docs/systems/search.md |' % status]))
                self.assertEqual(group(result.stdout, '1'), [line, 'OK: every foundational system has a docs/systems/ entry'])
                self.assertIn('Not built, blocked on the owner: 1 foundational system(s)', result.stdout)

    def test_blocked_system_is_reported_even_without_a_docs_folder(self):
        (self.project / 'docs' / 'systems').rmdir()
        result = self.check(systems_tree(['| 17 | Payments | #9 | src/shared/payments | blocked (owner: open the payments account) | docs/systems/payments.md |']))
        lines = group(result.stdout, '1')
        self.assertEqual(len(lines), 2, lines)
        self.assertTrue(lines[0].startswith('WARN: docs/systems/ directory does not exist'), lines)
        self.assertEqual(lines[1], "WARN: system 'Payments' is blocked on the owner: open the payments account. It is not built; features that need it wait (#29)")

    def test_name_without_letters_or_digits_needs_a_docs_path(self):
        result = self.check(systems_tree(['| 09 | && | #1 | x | implemented |'], '| # | Name | Convention | Location | Status |'))
        self.assertEqual(group(result.stdout, '1'), [
            "WARN: system '&&' has no letters or digits to name its page after, and its row names no Docs path; name the page in a Docs column",
        ])

    def test_blocked_system_does_not_quiet_unrelated_checks(self):
        (self.project / 'hooks' / 'pre-commit.sh').unlink()
        self.page('docs/systems/payments.md')
        result = self.check(systems_tree(['| 17 | Payments | #9 | src/shared/payments | blocked (owner: open the payments account) | docs/systems/payments.md |']))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('FAIL: no pre-commit hook found', ANSI.sub('', result.stdout))

    def test_deferred_system_keeps_its_page_like_any_other(self):
        row = '| 20 | Queue | #9 | src/shared/queue | deferred (TD-3) | docs/systems/queue.md |'
        missing = self.check(systems_tree([row]))
        self.assertEqual(group(missing.stdout, '1'), [
            "WARN: system 'Queue' has no document at docs/systems/queue.md, the path its Docs column names; "
            "a deferred system keeps a page that says what is deferred and until which trigger (#30)",
        ])
        self.page('docs/systems/queue.md')
        present = self.check(systems_tree([row]))
        self.assertEqual(group(present.stdout, '1'), ['OK: every foundational system has a docs/systems/ entry'])
        self.assertNotIn('blocked on the owner', present.stdout)

    def test_windows_line_endings_and_rows_without_a_closing_pipe(self):
        self.page('docs/systems/git.md')
        tree = systems_tree(['| 01 | Git & Hooks | #2 | hooks/ | implemented | docs/systems/git.md'],
                            header='| # | Name | Convention | Location | Status | Docs')
        result = self.check(tree, newline='\r\n')
        self.assertEqual(group(result.stdout, '1'), ['OK: every foundational system has a docs/systems/ entry'])

    def test_pipe_prose_in_the_systems_section_is_not_a_system(self):
        self.page('docs/systems/git.md')
        result = self.check(systems_tree(['| 01 | Git & Hooks | #2 | hooks/ | implemented | docs/systems/git.md |'],
                                         prose='Pulse reads: `# | Name | Convention | Location | Status`.\n'))
        self.assertEqual(group(result.stdout, '1'), ['OK: every foundational system has a docs/systems/ entry'])


class PulseInspect(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='archetype-pulse-')
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        (self.project / 'References.md').write_text('# References\n\n## Project\n\n- Name: Trial\n')
        (self.project / 'feature-tree.md').write_text(TEMPLATE.read_text())

    def inspect(self, *args):
        return subprocess.run([BASH, str(PULSE), *args], cwd=self.project, text=True, capture_output=True)

    def test_stdout_is_the_snapshot_without_out(self):
        result = self.inspect()
        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads(result.stdout)
        self.assertEqual(len(state['foundationalSystems']), 16)
        self.assertEqual([f['name'] for f in state['features']], ['[name]'])

    def test_blocked_status_passes_through_with_its_action(self):
        (self.project / 'feature-tree.md').write_text(systems_tree([
            '| 17 | Payments | #9 | src/shared/payments | blocked (owner: open the "payments" account) | docs/systems/payments.md |',
        ]))
        result = self.inspect()
        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads(result.stdout)
        self.assertEqual(state['foundationalSystems'][0]['status'], 'blocked (owner: open the "payments" account)')
        # The record says a boundary and a stand-in were built: with no code at all, drift says so.
        self.assertEqual(state['drift']['foundationalSystems']['declaredButMissing'], ['Payments'])
        (self.project / 'src' / 'shared' / 'payments').mkdir(parents=True)
        state = json.loads(self.inspect().stdout)
        self.assertEqual(state['drift']['foundationalSystems'], {'declaredButMissing': [], 'actualButUndeclared': []})

    def test_features_follow_the_numeric_row_rule(self):
        (self.project / 'feature-tree.md').write_text(features_tree([
            '| 01 | checkout | src/features/checkout | /checkout | Payments | not started | docs/features/checkout.md |',
            '| F2 | stray | src/features/stray | /stray | Payments | not started | docs/features/stray.md |',
        ], PIPE_PROSE))
        for name in ('checkout', 'stray'):
            (self.project / 'src' / 'features' / name).mkdir(parents=True)
        result = self.inspect()
        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads(result.stdout)
        self.assertEqual([f['name'] for f in state['features']], ['checkout'])
        self.assertIn('feat_checkout', state['architectureDiagram'])
        self.assertNotIn('stray', state['architectureDiagram'])
        self.assertNotIn('Location', state['architectureDiagram'])
        self.assertEqual(state['drift']['features'], {'declaredButMissing': [], 'actualButUndeclared': ['stray']})


class OneRowRule(unittest.TestCase):
    """The docs gate and the monitor read the same feature rows."""

    def test_gate_and_monitor_agree_on_the_feature_rows(self):
        with tempfile.TemporaryDirectory(prefix='archetype-rows-') as temp:
            project = Path(temp)
            (project / 'src' / 'features').mkdir(parents=True)
            (project / 'docs' / 'features').mkdir(parents=True)
            (project / 'References.md').write_text('# References\n')
            (project / 'feature-tree.md').write_text(features_tree([
                '| 01 | alpha | src/features/alpha | /a | Auth | implemented | docs/features/alpha.md |',
                '| **02** | beta | src/features/beta | /b | Auth | implemented | docs/features/beta.md |',
                '| F3 | gamma | src/features/gamma | /c | Auth | implemented | docs/features/gamma.md |',
            ], PIPE_PROSE))
            gate = subprocess.run([BASH, str(DEVELOP)], cwd=project, text=True, capture_output=True)
            monitor = subprocess.run([BASH, str(PULSE)], cwd=project, text=True, capture_output=True)
        flagged = set(re.findall(r"feature '([^']+)' in feature-tree\.md", ANSI.sub('', gate.stdout)))
        shown = {f['name'] for f in json.loads(monitor.stdout)['features']}
        self.assertEqual(flagged, {'alpha', 'beta'}, gate.stdout)
        self.assertEqual(shown, flagged)


if __name__ == '__main__':
    unittest.main()
