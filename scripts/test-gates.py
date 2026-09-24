#!/usr/bin/env python3
"""Exercise the gates that read feature-tree.md (validate-develop.sh, pulse-inspect.sh)
against projects built in a temporary folder, and the shipped template."""

from pathlib import Path
import json
import re
import subprocess
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]
DEVELOP = SOURCE / 'scripts' / 'validate-develop.sh'
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
