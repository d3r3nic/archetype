#!/usr/bin/env python3
"""Exercise the gates that read feature-tree.md (validate-develop.sh, validate-scaffold.sh,
pulse-inspect.sh) against projects built in a temporary folder, and the shipped template."""

from pathlib import Path
import json
import os
import re
import shutil
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
                       'names the action, what exists, and what stays unavailable', '(#29)'):
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

    def test_numbered_rows_named_like_header_cells_are_features(self):
        rows = [
            '| 01 | Feature | src/features/feature | /f | Auth | implemented | docs/features/Feature.md |',
            '| 02 | Name | src/features/name | /n | Auth | implemented | docs/features/Name.md |',
            '| 03 | -beta | src/features/beta | /b | Auth | implemented | docs/features/-beta.md |',
        ]
        missing = self.check(features_tree(rows))
        self.assertEqual(missing.returncode, 1, missing.stdout)
        self.assertEqual(group(missing.stdout, '4'), [
            "FAIL: feature 'Feature' in feature-tree.md but no docs/features/Feature.md",
            "FAIL: feature 'Name' in feature-tree.md but no docs/features/Name.md",
            "FAIL: feature '-beta' in feature-tree.md but no docs/features/-beta.md",
        ])
        for name in ('Feature', 'Name', '-beta'):
            self.document(name)
        present = self.check(features_tree(rows))
        self.assertEqual(present.returncode, 0, present.stdout)
        self.assertEqual(group(present.stdout, '4'), ['OK: every feature in feature-tree.md has a docs/features/ entry'])

    def test_numbered_row_with_an_empty_name_is_named(self):
        result = self.check(features_tree(['| 04 |  | src/features/x | /x | Auth | implemented | docs/features/x.md |']))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(group(result.stdout, '4'), [
            'FAIL: feature row 04 has no name (its Feature cell is empty); name the feature or delete the row',
        ])

    def test_smoke_test_names_stay_exempt(self):
        rows = ['| %02d | %s | src/features/%s | /%s | Auth | implemented | docs/features/%s.md |' % (i, n, n, n, n)
                for i, n in enumerate(('health', '_health', 'ping', 'smoke'), 1)]
        result = self.check(features_tree(rows))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(group(result.stdout, '4'), ['OK: every feature in feature-tree.md has a docs/features/ entry'])


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
            "WARN: system 'Payments' is blocked on the owner: open the payments account. It is not complete; features that need it wait (#29)",
            "WARN: system 'Payments' has no document at docs/systems/payments.md, the path its Docs column names; "
            "a system blocked on the owner keeps a page that names the owner action, what exists, and what stays unavailable (#29)",
        ])
        self.page('docs/systems/payments.md')
        present = self.check(systems_tree([row]))
        self.assertEqual(present.returncode, 0, present.stdout)
        self.assertEqual(group(present.stdout, '1'), [
            "WARN: system 'Payments' is blocked on the owner: open the payments account. It is not complete; features that need it wait (#29)",
            'OK: every foundational system has a docs/systems/ entry',
        ])
        self.assertIn('Not complete, blocked on the owner: 1 foundational system(s); group 1 names each owner action.', present.stdout)

    def test_blocked_status_written_in_code_quotes_or_bold_is_read(self):
        self.page('docs/systems/mail.md')
        for status in ('`blocked (owner: approve the mail plan)`', '**blocked (owner: approve the mail plan)**'):
            with self.subTest(status=status):
                result = self.check(systems_tree(['| **18** | Mail | #9 | src/shared/mail | %s |  |' % status]))
                self.assertEqual(group(result.stdout, '1'), [
                    "WARN: system 'Mail' is blocked on the owner: approve the mail plan. It is not complete; features that need it wait (#29)",
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
                self.assertIn('Not complete, blocked on the owner: 1 foundational system(s)', result.stdout)

    def test_blocked_system_is_reported_even_without_a_docs_folder(self):
        (self.project / 'docs' / 'systems').rmdir()
        result = self.check(systems_tree(['| 17 | Payments | #9 | src/shared/payments | blocked (owner: open the payments account) | docs/systems/payments.md |']))
        lines = group(result.stdout, '1')
        self.assertEqual(len(lines), 2, lines)
        self.assertTrue(lines[0].startswith('WARN: docs/systems/ directory does not exist'), lines)
        self.assertEqual(lines[1], "WARN: system 'Payments' is blocked on the owner: open the payments account. It is not complete; features that need it wait (#29)")

    def test_name_without_letters_or_digits_needs_a_docs_path(self):
        result = self.check(systems_tree(['| 09 | && | #1 | x | implemented |'], '| # | Name | Convention | Location | Status |'))
        self.assertEqual(group(result.stdout, '1'), [
            "WARN: system '&&' has no letters or digits to name its page after, and its row names no Docs path; name the page in a Docs column",
        ])

    def test_numbered_row_with_an_empty_name_is_named(self):
        self.page('docs/systems/x.md')
        result = self.check(systems_tree(['| 10 |  | #1 | x | implemented | docs/systems/x.md |']))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(group(result.stdout, '1'), [
            'WARN: system row 10 has no name (its Name cell is empty); name the system or delete the row',
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


class RegulatedDataGate(unittest.TestCase):
    """validate-scaffold.sh groups 4 and 4b: PROFILE.md's regulated-data fact, and a References.md
    Compliance section that names regulated data to say it does not apply."""

    COMPLIANCE = ('\n## Compliance\n\n- Regulated data: PROFILE.md holds the fact\n'
                  '- Regimes: none, the project keeps no regulated data\n- Obligations: none\n'
                  '- Promises to users: only coordinators see contact details\n')
    TREE = systems_tree(['| 01 | Git & Hooks | #2 | hooks/ | implemented | docs/systems/git.md |'])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='archetype-regulated-')
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.unit(self.project)

    def unit(self, folder):
        """A scaffolded unit that passes every group but 4 and 4b on its own."""
        (folder / 'VERSION-LOG.md').write_text('# Version Log\n\n## Scaffold\n\nComplete.\n')
        hook = folder / 'hooks' / 'pre-commit.sh'
        hook.parent.mkdir(parents=True, exist_ok=True)
        hook.write_text('#!/bin/sh\nexit 0\n')
        hook.chmod(0o755)
        page = folder / 'docs' / 'systems' / 'git.md'
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text('# page\n')
        (folder / 'feature-tree.md').write_text(self.TREE)

    def check(self, tree=None, folder=None):
        return subprocess.run([BASH, str(SCAFFOLD)], cwd=folder or self.project, text=True, capture_output=True)

    def references(self, extra):
        (self.project / 'References.md').write_text('# References\n\n## Tech Stack\n\n- Language: recorded\n' + extra)

    def profile(self, value, where=None):
        (where or self.project).joinpath('PROFILE.md').write_text('# Profile\n\n- Regulated data: %s\n\n## Notes\n' % value)

    def audit_store(self, backing=False):
        store = self.project / 'src' / 'shared' / 'audit-log'
        store.mkdir(parents=True, exist_ok=True)
        (store / 'store.ts').write_text('export class InMemoryAuditStore { records: Array<string> = [] }\n'
                                        + ('export class DatabaseAuditStore {}\n' if backing else ''))

    def test_a_compliance_section_that_says_no_does_not_trigger_the_audit_store_check(self):
        self.references(self.COMPLIANCE)
        self.audit_store()
        self.profile('no')
        result = self.check(self.TREE)
        self.assertEqual(group(result.stdout, '4'), ['OK: PROFILE.md records no regulated data — audit log check skipped'])
        self.assertNotIn('in-memory store only', result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_without_a_profile_any_mention_still_applies_the_audit_store_check(self):
        # An older project without PROFILE.md keeps the earlier reading: a mention is enough.
        self.references(self.COMPLIANCE)
        self.audit_store()
        result = self.check(self.TREE)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('in-memory store only (References.md mentions regulated data)', result.stdout)

    def test_a_profile_that_says_no_flags_a_references_md_that_names_a_regime(self):
        self.references('\n## Compliance\n\n- Regimes: HIPAA applies to intake notes\n')
        self.profile('no')
        result = self.check(self.TREE)
        self.assertEqual(group(result.stdout, '4'), [
            'WARN: PROFILE.md records no regulated data, but References.md names it: '
            '"- Regimes: HIPAA applies to intake notes". Correct whichever record is wrong'])
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_a_single_unit_whose_profile_says_yes_or_unknown_keeps_the_audit_log(self):
        for regimes in ('- Regimes: GDPR, because most members live in Germany',
                        '- Regimes: PCI, card numbers pass through the checkout',
                        '- Regimes: HIPAA (patient records); PCI DSS none, payments go through a hosted checkout'):
            for value in ('yes', 'unknown'):
                with self.subTest(regimes=regimes, value=value):
                    self.references('\n## Compliance\n\n' + regimes + '\n')
                    self.profile(value)
                    store = self.project / 'src'
                    if store.exists():
                        shutil.rmtree(store)
                    missing = self.check(self.TREE)
                    self.assertEqual(missing.returncode, 1, missing.stdout)
                    self.assertIn('PROFILE.md records regulated data: %s but no audit log found: record where this unit keeps it on the Audit log line' % value, missing.stdout)
                    self.audit_store()
                    memory_only = self.check(self.TREE)
                    self.assertEqual(memory_only.returncode, 1, memory_only.stdout)
                    self.assertIn('in-memory store only (PROFILE.md records regulated data: %s)' % value, memory_only.stdout)
                    self.audit_store(backing=True)
                    self.assertEqual(self.check(self.TREE).returncode, 0)

    def endpoint(self, references):
        subprocess.run(['git', 'init', '-q'], cwd=self.project, check=True)
        unit = self.project / 'frontend'
        unit.mkdir()
        self.unit(unit)
        (unit / 'References.md').write_text('# References\n\n' + references)
        return unit

    def test_an_endpoint_reads_the_profile_above_it(self):
        unit = self.endpoint('- Regimes: HIPAA applies to intake notes\n')
        self.profile('no')
        result = self.check(folder=unit)
        self.assertIn('WARN: PROFILE.md records no regulated data, but References.md names it', group(result.stdout, '4')[0])

    def test_an_endpoint_of_a_regulated_project_warns_when_its_references_are_silent(self):
        unit = self.endpoint('## Tech Stack\n\n- Language: recorded\n')
        self.profile('yes')
        result = self.check(folder=unit)
        self.assertEqual(result.returncode, 0, result.stdout)
        [line] = group(result.stdout, '4')
        self.assertTrue(line.startswith('WARN: PROFILE.md above this folder records regulated data: yes'), line)
        store = unit / 'src' / 'shared' / 'audit-log'
        store.mkdir(parents=True)
        (store / 'store.ts').write_text('export class InMemoryAuditStore {}\n')
        result = self.check(folder=unit)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('in-memory store only (PROFILE.md records regulated data: yes)', result.stdout)

    def test_the_label_form_regulated_data_yes_counts_as_declared(self):
        self.references('\n## Compliance\n\n- Regulated data: yes (patient records)\n')
        result = self.check(self.TREE)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('References.md declares regulated data but no audit log found', result.stdout)

    def test_a_recorded_audit_log_path_is_checked_where_it_says(self):
        self.profile('yes')
        self.references('\n## Compliance\n\n- Regimes: GDPR, members in Germany\n'
                        '- Audit log: `src/server/audit-log` (append-only table)\n')
        missing = self.check(self.TREE)
        self.assertEqual(missing.returncode, 1, missing.stdout)
        self.assertIn('records the audit log at src/server/audit-log, which does not exist', missing.stdout)
        store = self.project / 'src' / 'server' / 'audit-log'
        store.mkdir(parents=True)
        (store / 'store.ts').write_text('export class InMemoryAuditStore { records: Array<string> = [] }\n')
        memory_only = self.check(self.TREE)
        self.assertEqual(memory_only.returncode, 1, memory_only.stdout)
        self.assertIn('in-memory store only', memory_only.stdout)
        (store / 'store.ts').write_text('export class PostgresAuditStore {}\n')
        result = self.check(self.TREE)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(group(result.stdout, '4'), [
            'OK: audit log path exists: src/server/audit-log (PROFILE.md records regulated data: yes)'])

    def test_a_recorded_path_outside_src_counts(self):
        self.profile('yes')
        self.references('\n## Compliance\n\n- Audit log: gardenapp/audit\n')
        (self.project / 'gardenapp' / 'audit').mkdir(parents=True)
        result = self.check(self.TREE)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_an_endpoint_whose_log_another_unit_keeps_passes_and_one_that_keeps_it_is_held_to_it(self):
        unit = self.endpoint('## Compliance\n\n- Regulated data: see PROFILE.md\n- Audit log: kept by backend\n')
        self.profile('yes')
        result = self.check(folder=unit)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(group(result.stdout, '4'), ['OK: audit log kept by backend (References.md § Compliance)'])
        backend = self.project / 'backend'
        backend.mkdir()
        self.unit(backend)
        (backend / 'References.md').write_text('# References\n\n## Compliance\n\n- Regimes: GDPR, members in Germany\n'
                                               '- Audit log: src/audit\n')
        result = self.check(folder=backend)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('records the audit log at src/audit, which does not exist', result.stdout)

    def test_a_regime_that_does_not_apply_is_not_a_contradiction(self):
        self.profile('no')
        self.references('\n## Compliance\n\n- Regimes: HIPAA does not apply: no health data\n')
        result = self.check(self.TREE)
        self.assertEqual(group(result.stdout, '4'), ['OK: PROFILE.md records no regulated data — audit log check skipped'])

    def run_unit(self, references, profile=None, above=None):
        """Run the gate on a fresh unit: its References.md, optional PROFILE.md here or above it."""
        root = Path(tempfile.mkdtemp(prefix='archetype-regulated-case-'))
        self.addCleanup(shutil.rmtree, root, True)
        unit = root / 'unit' if above else root
        unit.mkdir(exist_ok=True)
        if above:
            subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
            (root / 'PROFILE.md').write_text('# Profile\n\n- Regulated data: %s\n' % above)
        if profile:
            (unit / 'PROFILE.md').write_text('# Profile\n\n- Regulated data: %s\n' % profile)
        self.unit(unit)
        (unit / 'References.md').write_text('# References\n\n' + references)
        return unit, lambda: self.check(folder=unit)

    def test_the_audit_log_line_reads_as_the_template_offers_it(self):
        compliance = '## Compliance\n\n'
        cases = [
            # (References.md, profile here, profile above, exit code, text in group 4 or 4b output)
            (compliance + '- Audit log: not required, no regime here needs one\n', None, None, 0,
             'OK: References.md § Compliance records no audit log in this unit: not required, no regime here needs one'),
            (compliance + '- Audit log: not required, the backend service keeps it\n', None, 'yes', 0,
             'OK: References.md § Compliance records no audit log in this unit: not required, the backend service keeps it'),
            (compliance + '- Audit log: none\n', None, 'unknown', 0, 'OK: References.md § Compliance records no audit log in this unit: none'),
            (compliance + '- Audit log: `kept by the backend`\n', None, 'yes', 0, 'OK: audit log kept by the backend'),
            (compliance + '- Audit log: not required, GDPR asks for none here\n', 'yes', None, 0,
             'WARN: References.md § Compliance records the audit log as "not required, GDPR asks for none here" while PROFILE.md records regulated data: yes'),
            ('## Logging\n\n- Audit log: append-only table, see B4\n', None, None, 0, 'OK: no regulated data declared'),
            (compliance + '- Audit log: /var/log/audit\n', 'yes', None, 1, 'records the audit log at /var/log/audit: record a path inside this unit'),
            (compliance + '- Audit log: ../frontend/src\n', 'yes', None, 1, 'records the audit log at ../frontend/src: record a path inside this unit'),
            (compliance + '- Audit log: src\n', 'yes', None, 1, 'records the audit log as the whole source folder (src)'),
            (compliance + '- Audit log: `src/audit trail` (append-only)\n', 'yes', None, 1, 'records the audit log at src/audit trail, which does not exist'),
            (compliance + '- Audit log: [where this unit keeps it]\n- Audit log: src/server/audit\n', 'yes', None, 1,
             'records the audit log at src/server/audit, which does not exist'),
        ]
        for references, here, above, code, text in cases:
            with self.subTest(references=references, here=here, above=above):
                unit, run = self.run_unit(references, here, above)
                (unit / 'src').mkdir(exist_ok=True)
                result = run()
                self.assertEqual(result.returncode, code, result.stdout)
                self.assertIn(text, ANSI.sub('', result.stdout))

    def test_kept_by_this_unit_is_not_another_keeper_and_trailing_punctuation_is_trimmed(self):
        unit, run = self.run_unit('## Compliance\n\n- Audit log: kept by this unit; the path is recorded when scaffold builds it\n', 'yes')
        (unit / 'src').mkdir()
        result = run()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('no audit log found: record where this unit keeps it on the Audit log line', result.stdout)
        unit, run = self.run_unit('## Compliance\n\n- Audit log: src/server/audit-log/, an append-only table\n', 'yes')
        (unit / 'src' / 'server' / 'audit-log').mkdir(parents=True)
        result = run()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('audit log path exists: src/server/audit-log', result.stdout)

    def test_not_required_beside_a_regime_that_requires_an_audit_trail_fails(self):
        for here in ('yes', 'unknown'):
            with self.subTest(here=here):
                unit, run = self.run_unit('## Compliance\n\n- Regimes: HIPAA (patient records, Step 2.5)\n'
                                          '- Audit log: not required, we only store appointment times\n', here)
                (unit / 'src').mkdir()
                result = run()
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn('but names a regime that requires one', result.stdout)

    def test_none_with_punctuation_dot_src_and_kept_by_this_unit_on_an_endpoint(self):
        for value in ('None.', 'none; the backend keeps it', 'None: this unit stores nothing'):
            with self.subTest(value=value):
                unit, run = self.run_unit('## Compliance\n\n- Audit log: %s\n' % value, None, 'yes')
                (unit / 'src').mkdir()
                result = run()
                self.assertEqual(result.returncode, 0, result.stdout)
                self.assertIn('records no audit log in this unit', result.stdout)
        unit, run = self.run_unit('## Compliance\n\n- Audit log: ./src\n', 'yes')
        (unit / 'src').mkdir()
        self.assertIn('records the audit log as the whole source folder (src)', run().stdout)
        unit, run = self.run_unit('## Compliance\n\n- Audit log: .//src/shared/audit-log\n', 'yes')
        (unit / 'src' / 'shared' / 'audit-log').mkdir(parents=True)
        self.assertIn('audit log path exists: src/shared/audit-log', run().stdout)
        unit, run = self.run_unit('## Compliance\n\n- Audit log: kept by this unit\n', None, 'yes')
        (unit / 'src').mkdir()
        result = run()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("References.md § Compliance says this unit keeps its audit log but no audit log found", result.stdout)

    def test_a_regime_that_applies_counts_beside_one_that_does_not(self):
        unit, run = self.run_unit('- Regimes: HIPAA applies to the patient notes; PCI DSS does not apply (hosted checkout)\n')
        (unit / 'src').mkdir()
        result = run()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('References.md declares regulated data but no audit log found', result.stdout)

    def test_a_store_in_this_unit_is_checked_even_when_another_keeps_the_log(self):
        unit, run = self.run_unit('## Compliance\n\n- Audit log: kept by the audit service\n', 'yes')
        store = unit / 'src' / 'shared' / 'audit-log'
        store.mkdir(parents=True)
        (store / 'store.ts').write_text('export class InMemoryAuditStore { records: Array<string> = [] }\n')
        result = run()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('in-memory store only', result.stdout)

    def test_a_regulated_unit_still_needs_its_audit_log_and_a_real_store(self):
        self.references('\n## Compliance\n\n- Regimes: HIPAA applies to intake notes\n')
        for profile in ('yes', 'unknown', None):
            (self.project / 'PROFILE.md').unlink() if (self.project / 'PROFILE.md').exists() else None
            if profile:
                self.profile(profile)
            missing = self.check(self.TREE)
            self.assertEqual(missing.returncode, 1, profile)
            self.assertIn('no audit log found', missing.stdout)
        self.audit_store()
        memory_only = self.check(self.TREE)
        self.assertEqual(memory_only.returncode, 1)
        self.assertIn('in-memory store only', memory_only.stdout)
        self.audit_store(backing=True)
        self.assertEqual(self.check(self.TREE).returncode, 0)


class PulseInspect(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='archetype-pulse-')
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        (self.project / 'References.md').write_text('# References\n\n## Project\n\n- Name: Trial\n')
        (self.project / 'feature-tree.md').write_text(TEMPLATE.read_text())

    def inspect(self, *args):
        return subprocess.run([BASH, str(PULSE), *args], cwd=self.project, text=True, capture_output=True)

    def assert_plain_failure(self, result, *phrases):
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stdout, '')
        for phrase in phrases:
            self.assertIn(phrase, result.stderr)
        self.assertEqual(len(result.stderr.strip().splitlines()), 1, result.stderr)
        self.assertNotRegex(result.stderr, r'line [0-9]+:|No such file|Not a directory|Is a directory|Permission denied')

    def test_stdout_is_the_snapshot_without_out(self):
        result = self.inspect()
        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads(result.stdout)
        self.assertEqual(len(state['foundationalSystems']), 16)
        self.assertEqual([f['name'] for f in state['features']], ['[name]'])

    def test_out_creates_a_missing_nested_folder(self):
        result = self.inspect('--out', 'dev/pulse/state/.pulse-state.json')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertIn('pulse state written to dev/pulse/state/.pulse-state.json', result.stderr)
        state = json.loads((self.project / 'dev' / 'pulse' / 'state' / '.pulse-state.json').read_text())
        self.assertEqual(state['dataContractVersion'], 'v2')

    def test_out_under_a_regular_file_fails_plainly(self):
        (self.project / 'blocker').write_text('a file, not a folder\n')
        result = self.inspect('--out', 'blocker/state.json')
        self.assert_plain_failure(result, 'cannot create the folder blocker', 'blocker/state.json')

    def test_out_that_is_a_folder_fails_plainly(self):
        (self.project / 'snapshots').mkdir()
        result = self.inspect('--out', 'snapshots')
        self.assert_plain_failure(result, 'cannot write the snapshot to snapshots')

    @unittest.skipIf(hasattr(os, 'geteuid') and os.geteuid() == 0, 'folder permissions do not bind the superuser')
    def test_out_in_a_read_only_folder_fails_plainly(self):
        locked = self.project / 'locked'
        locked.mkdir()
        locked.chmod(0o555)
        self.addCleanup(locked.chmod, 0o755)
        result = self.inspect('--out', 'locked/state.json')
        self.assert_plain_failure(result, 'cannot write the snapshot to locked/state.json')

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

    def test_numbered_rows_named_like_header_cells_are_features(self):
        # systems_tree ends with the Features header and separator, so feature rows follow it.
        (self.project / 'feature-tree.md').write_text(
            systems_tree(['| 01 | Payments | #9 | src/shared/payments | implemented | docs/systems/payments.md |'])
            + '| 01 | Feature | src/features/feature | /f | Payments | not started | docs/features/Feature.md |\n'
            + '| 02 | Name | src/features/name | /n | Payments | not started | docs/features/Name.md |\n'
        )
        (self.project / 'src' / 'features' / 'feature').mkdir(parents=True)
        result = self.inspect()
        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads(result.stdout)
        self.assertEqual([f['name'] for f in state['features']], ['Feature', 'Name'])
        diagram = state['architectureDiagram']
        for line in ('feat_feature["Feature"]', 'feat_name["Name"]', 'feat_feature --> sys_payments', 'feat_name --> sys_payments'):
            self.assertIn(line, diagram)
        self.assertEqual(state['drift']['features'], {'declaredButMissing': ['Name'], 'actualButUndeclared': []})

    def test_numbered_row_with_an_empty_name_is_left_out(self):
        (self.project / 'feature-tree.md').write_text(features_tree([
            '| 01 | checkout | src/features/checkout | /checkout | Payments | not started | docs/features/checkout.md |',
            '| 02 |  | src/features/x | /x | Payments | not started | docs/features/x.md |',
        ]))
        state = json.loads(self.inspect().stdout)
        self.assertEqual([f['name'] for f in state['features']], ['checkout'])
        self.assertNotRegex(state['architectureDiagram'], r'feat_[\[ ]')
        self.assertEqual(state['drift']['features'], {'declaredButMissing': ['checkout'], 'actualButUndeclared': []})


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
                '| 04 | Feature | src/features/feature | /f | Auth | implemented | docs/features/Feature.md |',
                '| 05 | Name | src/features/name | /n | Auth | implemented | docs/features/Name.md |',
                '| 06 |  | src/features/x | /x | Auth | implemented | docs/features/x.md |',
            ], PIPE_PROSE))
            gate = subprocess.run([BASH, str(DEVELOP)], cwd=project, text=True, capture_output=True)
            monitor = subprocess.run([BASH, str(PULSE)], cwd=project, text=True, capture_output=True)
        flagged = set(re.findall(r"feature '([^']+)' in feature-tree\.md", ANSI.sub('', gate.stdout)))
        shown = {f['name'] for f in json.loads(monitor.stdout)['features']}
        self.assertEqual(flagged, {'alpha', 'beta', 'Feature', 'Name'}, gate.stdout)
        self.assertEqual(shown, flagged)
        # The nameless row has nothing to show; the gate names it by its number instead.
        self.assertIn('feature row 06 has no name', gate.stdout)


if __name__ == '__main__':
    unittest.main()
