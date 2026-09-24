#!/usr/bin/env python3
"""Regression tests for actual bootstrap facts, distinct from scaffold placeholders."""
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('validate-bootstrap.py')
PROJECT = '''## Project
- Name: Shift board
- Purpose: Coordinate shifts
- Stage: development
- Owner channel: project owner
- Decision location: DECISIONS.md
- Reporting pace: every session

## Foundational Systems
Location: [filled during scaffold]
'''
LOG = '''## Bootstrap
Date: 2026-09-19
Type: product
Tech stack: recorded in References.md
Profile: isolated, owner-stated
Files generated:
- References.md
- PROFILE.md
- feature-tree.md
Discovery: PROGRESS.md, unanswered hosting question
Key decisions made: DECISIONS.md
Open pre-production gates: hosting choice before deployment
'''
INSTALLED = '''# Version Log

The Bootstrap section records the installation and what setup decided. update.sh appends each framework update under Updates.

## Bootstrap

Date: 2026-09-19
Source: https://github.com/d3r3nic/archetype
Commit: 1538b8c28d9bced68266c3c87fe2d84bbd804739
Method: inject.sh
'''
SETUP = LOG.split('\n', 2)[2]  # the setup lines, without the heading and the date


def update(day, commit):
    return ('\n### 2026-09-%02d\nCommit: %s\nSource: https://github.com/d3r3nic/archetype.git\n'
            'Updated by: update.sh\n' % (day, commit))


class Bootstrap(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'feature-tree.md').write_text('# Feature tree\n')

    def run_gate(self, mode, body):
        name = 'References.md' if mode == 'context' else 'VERSION-LOG.md'
        (self.root / name).write_text(body)
        return subprocess.run(['python3', str(SCRIPT), mode], cwd=self.root, capture_output=True, text=True)

    def test_facts_pass_with_future_scaffold_placeholder(self):
        result = self.run_gate('context', PROJECT)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_required_facts_reject_templates_empty_and_pending(self):
        for value in ('[project name]', '', '**pending**', 'unknown', '**unknown**', '`none`', '_n/a_'):
            with self.subTest(value=value):
                result = self.run_gate('context', PROJECT.replace('Name: Shift board', 'Name: ' + value))
                self.assertEqual(result.returncode, 1, result.stdout)

    def test_duplicate_and_fenced_project_sections_fail(self):
        for body in (PROJECT + PROJECT, '```\n' + PROJECT + '```', '~~~\n' + PROJECT + '~~~'):
            with self.subTest(body=body):
                self.assertEqual(self.run_gate('context', body).returncode, 1)

    def test_platform_purpose_label_passes(self):
        self.assertEqual(self.run_gate('context', PROJECT.replace('Purpose:', 'Purpose (one sentence):')).returncode, 0)

    def test_missing_tree_fails(self):
        (self.root / 'feature-tree.md').unlink()
        self.assertEqual(self.run_gate('context', PROJECT).returncode, 1)

    def test_installer_log_is_not_a_bootstrap_record(self):
        self.assertEqual(self.run_gate('log', '## Installed\nDate: 2026-09-19\n').returncode, 1)

    def test_filled_handoff_passes(self):
        result = self.run_gate('log', LOG)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_open_gates_must_be_recorded_even_when_none(self):
        self.assertEqual(self.run_gate('log', LOG.replace('Open pre-production gates: hosting choice before deployment', '')).returncode, 1)
        self.assertEqual(self.run_gate('log', LOG.replace('hosting choice before deployment', 'none')).returncode, 0)

    def test_latest_bootstrap_is_checked_without_erasing_history(self):
        result = self.run_gate('log', LOG + '\n' + LOG.replace('Discovery: PROGRESS.md, unanswered hosting question', 'Discovery: [answers]'))
        self.assertEqual(result.returncode, 1, result.stdout)

    def test_example_cannot_supply_handoff(self):
        for fence in ('```', '~~~'):
            self.assertEqual(self.run_gate('log', fence + '\n' + LOG + fence).returncode, 1)

    def test_bad_date_and_missing_file_entries_fail(self):
        for body in (LOG.replace('2026-09-19', 'not dated'), LOG.replace('- References.md\n- PROFILE.md', '')):
            self.assertEqual(self.run_gate('log', body).returncode, 1)

    def test_generated_files_cannot_be_none_or_incomplete(self):
        for replacement in ('- none', '- References.md'):
            body = LOG.replace('- References.md\n- PROFILE.md\n- feature-tree.md', replacement)
            self.assertEqual(self.run_gate('log', body).returncode, 1)

    def test_markdown_link_is_a_value(self):
        self.assertEqual(self.run_gate('log', LOG.replace('Key decisions made: DECISIONS.md', 'Key decisions made: [decisions](DECISIONS.md)')).returncode, 0)

    def test_installed_section_completed_by_setup_passes_with_updates_after_it(self):
        body = INSTALLED + SETUP + '\n## Updates\n' + update(20, 'a' * 40) + update(21, 'b' * 40)
        result = self.run_gate('log', body)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_update_entries_inside_a_bootstrap_section_are_read_as_its_fields(self):
        # A second Bootstrap section after Updates takes in every entry appended after it; the
        # updater moves those entries under Updates.
        entries = update(20, 'a' * 40) + update(21, 'b' * 40)
        result = self.run_gate('log', INSTALLED + '\n## Updates\n\n' + LOG + entries)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('duplicate field: Commit', result.stdout)
        result = self.run_gate('log', INSTALLED + '\n## Updates\n\n' + LOG + '\n## Updates\n' + entries)
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == '__main__':
    unittest.main()
