#!/usr/bin/env python3
"""Exercise scripts/validate-design.sh against projects built in a temporary folder."""

from pathlib import Path
import re
import subprocess
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]
SCRIPT = SOURCE / 'scripts' / 'validate-design.sh'
SCAFFOLD_SCRIPT = SOURCE / 'scripts' / 'validate-scaffold.sh'
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
        default = 'not yet, directions pending' if label == 'Brand decided' else 'recorded value for ' + label.lower()
        lines.append('- %s: %s' % (label, values.get(label, default)))
    lines.extend(extra)
    return '\n'.join(lines) + '\n\n## Foundational Systems\n\n- Not a design line: [placeholder outside the section]\n'


class DesignGate(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='archetype-design-')
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)

    def check(self, references, *args):
        if references is not None:
            (self.project / 'References.md').write_text('# References\n\n' + references)
        return subprocess.run(['bash', str(SCRIPT), *args], cwd=self.project, text=True, capture_output=True)

    def scaffold_check(self, references, *args):
        (self.project / 'References.md').write_text('# References\n\n' + references)
        (self.project / 'feature-tree.md').write_text(
            '# Feature Tree\n\n## Foundational Systems\n\n'
            '| # | Name | Convention | Location | Status | Docs |\n'
            '|---|---|---|---|---|---|\n\n## Features\n'
        )
        (self.project / 'VERSION-LOG.md').write_text('# Version Log\n\n## Scaffold\n\nComplete.\n')
        hooks = self.project / 'hooks'
        hooks.mkdir()
        hook = hooks / 'pre-commit.sh'
        hook.write_text('#!/bin/sh\nexit 0\n')
        hook.chmod(0o755)
        return subprocess.run(
            ['bash', str(SCAFFOLD_SCRIPT), *args],
            cwd=self.project,
            text=True,
            capture_output=True,
        )

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

    def test_only_the_lines_the_check_reads_are_required(self):
        result = self.check(section(drop=('Density', 'Captures', 'Sync')))
        self.assertEqual(result.returncode, 0, result.stdout)
        result = self.check(section(drop=('Brand decided',)))
        self.assertEqual(result.returncode, 1)
        self.assertIn('has no Brand decided line', result.stdout)
        result = self.check(section({'Brand decided': 'yes'}, drop=('Return tasks',)))
        self.assertEqual(result.returncode, 1)
        self.assertIn('Brand decided is yes, but unknown: Return tasks', result.stdout)

    def test_a_read_line_given_twice_is_named(self):
        result = self.check(section(extra=('- Density: dense, again',)))
        self.assertEqual(result.returncode, 0, result.stdout)
        result = self.check(section(extra=('- Brand decided: yes',)))
        self.assertEqual(result.returncode, 1)
        self.assertIn('repeats "Brand decided"', result.stdout)

    def test_template_placeholder_fails(self):
        result = self.check(section({'First task': '[the one thing a person should be able to do]'}))
        self.assertEqual(result.returncode, 1)
        self.assertRegex(result.stdout, r'placeholder or no value: First task')

    def test_empty_value_fails(self):
        result = self.check(section({'Captures': ''}))
        self.assertEqual(result.returncode, 1)
        self.assertRegex(result.stdout, r'placeholder or no value: Captures')

    def test_a_line_in_the_projects_own_words_is_its_record(self):
        for value in ('pending Step 4.5', 'Pending', 'TBD', 'to be decided with the owner', 'todo', '**pending**', 'awaiting owner'):
            with self.subTest(value=value):
                result = self.check(section({'Tokens source': value}))
                self.assertEqual(result.returncode, 0, result.stdout)
        still_fine = self.check(section({'Brand decided': 'not yet, directions pending the owner\'s pick'}))
        self.assertEqual(still_fine.returncode, 0, still_fine.stdout)

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
        for value in ('**yes**, the brand book records all six', 'YES.'):
            with self.subTest(value=value):
                result = self.check(section({'Brand decided': value, 'First task': 'unknown; never answered'}))
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn('Brand decided is yes, but unknown: First task.', result.stdout)

    def test_yes_later_in_brand_prose_does_not_override_the_leading_state(self):
        result = self.check(section({
            'Brand decided': 'no, the owner has not said yes',
            'First task': 'unknown; assumed list',
        }))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_noncanonical_brand_synonym_fails(self):
        result = self.check(section({'Brand decided': 'settled and owner-approved'}))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('must start with a canonical state', result.stdout)

    def test_not_yet_is_not_yes(self):
        result = self.check(section({'Brand decided': 'not yet, directions pending', 'First task': 'unknown; never answered'}))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_a_note_in_the_section_is_left_alone(self):
        result = self.check(section(extra=('- Note on the direction: [the owner picked direction two]',)))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_project_root_wins_over_a_copy_in_the_engine_folder(self):
        (self.project / 'archetype').mkdir()
        (self.project / 'archetype' / 'References.md').write_text(section())
        result = self.check(section(drop=('Brand decided',)))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('has no Brand decided line', result.stdout)

    def test_engine_in_a_subfolder_is_found(self):
        (self.project / 'archetype').mkdir()
        (self.project / 'archetype' / 'References.md').write_text(section(drop=('Brand decided',)))
        result = self.check(None)
        self.assertEqual(result.returncode, 1)
        self.assertIn('has no Brand decided line', result.stdout)

    def test_shipped_templates_fail_until_filled(self):
        # The templates are all placeholders: a bootstrap that copies one and fills nothing must fail.
        for name in ('references-frontend.md', 'references-mobile.md'):
            with self.subTest(template=name):
                (self.project / 'References.md').write_text((SOURCE / 'templates' / name).read_text())
                result = self.check(None)
                self.assertEqual(result.returncode, 1)
                self.assertNotIn('lacks label', result.stdout)
                self.assertIn('placeholder or no value', result.stdout)

    def test_required_known_screen_rejects_a_missing_section(self):
        result = self.check('## Tech Stack\n\n- Language: recorded\n', '--required', 'known-screen')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("found 0", result.stdout)

    def test_required_known_screen_accepts_one_filled_live_section(self):
        result = self.check(section(), '--required', 'known-screen')
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_duplicate_live_sections_fail(self):
        result = self.check(section() + '\n' + section())
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('found 2', result.stdout)

    def test_heading_suffix_is_not_the_contract_section(self):
        text = section().replace('## Design Artifact', '## Design Artifact Notes', 1)
        optional = self.check(text)
        self.assertEqual(optional.returncode, 0, optional.stdout)
        required = self.check(text, '--required', 'known-screen')
        self.assertEqual(required.returncode, 1, required.stdout)
        self.assertIn('found 0', required.stdout)

    def test_fenced_section_is_not_live_for_either_fence_style(self):
        for fence in ('```', '~~~'):
            with self.subTest(fence=fence):
                result = self.check(f'{fence}\n{section()}{fence}\n', '--required', 'known-screen')
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn('found 0', result.stdout)

    def test_fenced_labels_do_not_fill_a_live_section(self):
        labels = '\n'.join(f'- {label}: example only' for label in LABELS)
        for fence in ('```', '~~~~'):
            with self.subTest(fence=fence):
                result = self.check(f'## Design Artifact\n\n{fence}\n{labels}\n{fence}\n')
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn('has no Brand decided line', result.stdout)

    def test_bold_labels_are_normalized(self):
        text = section()
        for label in LABELS:
            text = text.replace(f'- {label}:', f'- **{label}:**')
        result = self.check(text)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_decorated_unknown_task_fails_for_decided_brand(self):
        result = self.check(section({
            'Brand decided': 'yes, recorded in the brand book',
            'First task': '**unknown**; assumed list',
        }))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('Brand decided is yes, but unknown: First task.', result.stdout)

    def test_genuine_none_na_and_unknown_values_pass(self):
        result = self.check(section({
            'Published view': 'none',
            'Complementary tools': 'N/A',
            'Tokens source': 'unknown',
        }))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_template_brand_deferral_passes(self):
        result = self.check(section({'Brand decided': 'deferred to downstream projects'}))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_unknown_required_mode_is_usage_error(self):
        result = self.check(section(), '--required', 'maybe')
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn('unknown required mode', result.stdout)

    def test_scaffold_default_preserves_the_no_screen_path(self):
        result = self.scaffold_check('## Tech Stack\n\n- Language: recorded\n')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('or the project has none', result.stdout)

    def test_scaffold_required_mode_rejects_a_missing_design_section(self):
        result = self.scaffold_check(
            '## Tech Stack\n\n- Language: recorded\n',
            '--required',
            'known-screen',
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('needs exactly one live', result.stdout)


if __name__ == '__main__':
    unittest.main()
