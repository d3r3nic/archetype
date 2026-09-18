#!/usr/bin/env python3
"""Exercise scripts/validate-design.sh against projects built in a temporary folder."""

from pathlib import Path
import re
import subprocess
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]
SCRIPT = SOURCE / 'scripts' / 'validate-design.sh'
LABELS = [
    line for line in (SOURCE / 'scripts' / 'design-artifact-labels.txt').read_text().splitlines()
    if line.strip() and not line.startswith('#')
]


def section(values=None, drop=(), extra=()):
    """A filled Design Artifact section; values override a label, drop removes it."""
    values = values or {}
    lines = ['## Design Artifact', '', 'Convention #27 anchor: the brief.', '']
    for label in LABELS:
        if label in drop:
            continue
        lines.append('- %s: %s' % (label, values.get(label, 'recorded value for ' + label.lower())))
    lines.extend(extra)
    return '\n'.join(lines) + '\n\n## Foundational Systems\n\n- Not a design line: [placeholder outside the section]\n'


class DesignGate(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='archetype-design-')
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)

    def check(self, references):
        if references is not None:
            (self.project / 'References.md').write_text('# References\n\n' + references)
        return subprocess.run(['bash', str(SCRIPT)], cwd=self.project, text=True, capture_output=True)

    def test_filled_section_passes(self):
        result = self.check(section())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_project_without_a_screen_passes(self):
        result = self.check('## Tech Stack\n\n- Language: recorded\n')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('nothing to check', result.stdout)

    def test_no_references_file_is_an_error(self):
        result = self.check(None)
        self.assertEqual(result.returncode, 1)
        self.assertIn('References.md not found', result.stdout)

    def test_missing_label_is_named(self):
        result = self.check(section(drop=('Return tasks',)))
        self.assertEqual(result.returncode, 1)
        self.assertRegex(result.stdout, r'lacks label\(s\): Return tasks')

    def test_repeated_label_is_named(self):
        result = self.check(section(extra=('- Density: dense, again',)))
        self.assertEqual(result.returncode, 1)
        self.assertRegex(result.stdout, r'repeats label\(s\): Density')

    def test_template_placeholder_fails(self):
        result = self.check(section({'First task': '[the one thing a person should be able to do]'}))
        self.assertEqual(result.returncode, 1)
        self.assertRegex(result.stdout, r'placeholder or no value: First task')

    def test_empty_value_fails(self):
        result = self.check(section({'Captures': ''}))
        self.assertEqual(result.returncode, 1)
        self.assertRegex(result.stdout, r'placeholder or no value: Captures')

    def test_to_be_created_is_legal_only_on_artifact_location(self):
        allowed = self.check(section({'Artifact location': '[to be created]'}))
        self.assertEqual(allowed.returncode, 0, allowed.stdout)
        refused = self.check(section({'Tokens source': '[to be created]'}))
        self.assertEqual(refused.returncode, 1)
        self.assertRegex(refused.stdout, r'placeholder or no value: Tokens source')

    def test_placeholder_on_an_extra_line_of_the_section_fails(self):
        result = self.check(section(extra=('- Platform parity: [how the two platforms are kept aligned]',)))
        self.assertEqual(result.returncode, 1)
        self.assertRegex(result.stdout, r'placeholder or no value: Platform parity')

    def test_placeholder_outside_the_section_is_not_read(self):
        # section() always carries one under the next heading.
        result = self.check(section())
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_settled_look_needs_the_tasks(self):
        for label in ('First task', 'Return tasks'):
            with self.subTest(label=label):
                result = self.check(section({
                    'Brand decided': 'yes, the brand book records all six',
                    label: 'unknown; the owner did not answer, assumed a booking list',
                }))
                self.assertEqual(result.returncode, 1)
                self.assertRegex(result.stdout, r'Brand decided is yes, but unknown: %s\.' % re.escape(label))

    def test_unknown_task_is_allowed_while_the_look_is_open(self):
        result = self.check(section({
            'Brand decided': 'not yet, directions pending the owner',
            'Return tasks': 'unknown; the owner did not answer, assumed a booking list',
        }))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_settled_look_with_tasks_on_record_passes(self):
        result = self.check(section({'Brand decided': 'Yes', 'Return tasks': 'claim an open shift; post a shift'}))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('tasks the direction was composed for are on record', result.stdout)

    def test_carriage_returns_do_not_hide_an_empty_value(self):
        text = '# References\n\n' + section({'Captures': ''})
        (self.project / 'References.md').write_bytes(text.replace('\n', '\r\n').encode())
        result = self.check(None)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertRegex(result.stdout, r'placeholder or no value: Captures')

    def test_filled_section_with_carriage_returns_passes(self):
        text = '# References\n\n' + section()
        (self.project / 'References.md').write_bytes(text.replace('\n', '\r\n').encode())
        result = self.check(None)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_yes_is_read_however_it_is_written(self):
        for value in ('**yes**, the brand book records all six', 'Decided: yes', 'YES.'):
            with self.subTest(value=value):
                result = self.check(section({'Brand decided': value, 'First task': 'unknown; never answered'}))
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn('Brand decided is yes, but unknown: First task.', result.stdout)

    def test_not_yet_is_not_yes(self):
        result = self.check(section({'Brand decided': 'not yet, directions pending', 'First task': 'unknown; never answered'}))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_a_note_in_the_section_is_left_alone(self):
        result = self.check(section(extra=('- Note on the direction: [the owner picked direction two]',)))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_project_root_wins_over_a_copy_in_the_engine_folder(self):
        (self.project / 'archetype').mkdir()
        (self.project / 'archetype' / 'References.md').write_text(section())
        result = self.check(section(drop=('Density',)))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertRegex(result.stdout, r'lacks label\(s\): Density')

    def test_engine_in_a_subfolder_is_found(self):
        (self.project / 'archetype').mkdir()
        (self.project / 'archetype' / 'References.md').write_text(section(drop=('Density',)))
        result = self.check(None)
        self.assertEqual(result.returncode, 1)
        self.assertRegex(result.stdout, r'lacks label\(s\): Density')

    def test_shipped_templates_fail_until_filled(self):
        # The templates are all placeholders: a bootstrap that copies one and fills nothing must fail.
        for name in ('references-frontend.md', 'references-mobile.md'):
            with self.subTest(template=name):
                (self.project / 'References.md').write_text((SOURCE / 'templates' / name).read_text())
                result = self.check(None)
                self.assertEqual(result.returncode, 1)
                self.assertNotIn('lacks label', result.stdout)
                self.assertIn('placeholder or no value', result.stdout)


if __name__ == '__main__':
    unittest.main()
