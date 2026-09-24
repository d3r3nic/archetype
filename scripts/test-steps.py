#!/usr/bin/env python3
"""Exercise scripts/next-step.sh against a small engine and project built in a temporary folder."""

from pathlib import Path
import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock


SOURCE = Path(__file__).resolve().parents[1]

BOOT = '''# Bootstrap

Step ledger: boot

## Prerequisites

Read: this line is outside any step and is ignored

## Step 1: Start
Read: none
Produces: the project folder
Check: evidence: the folder's path

Body of step one.

## Step 2: Discovery

### Step 2.1: Who it is for
Read: #8 § Principle; templates/thing.md; project: References.md
Produces: the audience answers
Check: evidence: the owner's answers to this group, quoted

### Step 2.2 — Optional extras
Read: none
Produces: nothing when it does not apply
Check: evidence: what was set up
Skip when: the project has no extras

```
## Step 99: a heading inside a code fence is not a step
```

## Step 3 - Generate
Read: conventions/08-errors.md
Produces: flag.txt
Check: run scripts/check-flag.sh

## Checklist

Check: this line is after a plain heading and belongs to no step
'''

FEATURE = '''# Develop

Step ledger: dev (per feature)

### Step 1: Inventory
Read: project: feature-tree.md
Produces: the inventory
Check: evidence: the systems the feature will use

### Step 2: Build
Read: none
Produces: the feature
Check: run scripts/check-flag.sh --strict
'''

CHECK_FLAG = '''#!/bin/bash
if [ -f flag.txt ]; then echo "OK"; exit 0; fi
echo "FAIL: flag.txt is missing"
exit 1
'''


class Steps(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='archetype-steps-')
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.engine = root / 'engine'
        for folder in ('scripts', 'bootstrap', 'development', 'scaffolding', 'conventions', 'templates'):
            (self.engine / folder).mkdir(parents=True)
        shutil.copy(SOURCE / 'scripts' / 'next-step.sh', self.engine / 'scripts' / 'next-step.sh')
        shutil.copy(SOURCE / 'scripts' / 'step-recovery.py', self.engine / 'scripts' / 'step-recovery.py')
        (self.engine / 'scripts' / 'check-flag.sh').write_text(CHECK_FLAG)
        (self.engine / 'conventions' / '08-errors.md').write_text('# Errors\n\n## Principle\n\ntext\n\n## Rules\n\ntext\n')
        (self.engine / 'templates' / 'thing.md').write_text('# Thing\n')
        (self.engine / 'bootstrap' / 'BOOT.md').write_text(BOOT)
        (self.engine / 'development' / 'FEATURE.md').write_text(FEATURE)
        self.project = root / 'project'
        self.project.mkdir()

    def ledger(self, playbooks='boot, dev'):
        (self.project / 'PROGRESS.md').write_text('# Progress\n\n- Playbooks: %s\n\n## Closed steps\n\n' % playbooks)

    def run_tool(self, *args, cwd=None):
        return subprocess.run(['bash', str(self.engine / 'scripts' / 'next-step.sh'), *args],
                              cwd=cwd or self.project, text=True, capture_output=True)

    def closed(self):
        return [l for l in (self.project / 'PROGRESS.md').read_text().splitlines() if l.startswith('- [')]

    # --- the lint -----------------------------------------------------------------

    def test_lint_passes_on_well_formed_playbooks(self):
        result = self.run_tool('--lint', cwd=self.engine)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('OK: 6 steps', result.stdout)

    def lint_with(self, old, new):
        path = self.engine / 'bootstrap' / 'BOOT.md'
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1))
        return self.run_tool('--lint', cwd=self.engine)

    def test_lint_names_a_step_without_a_check(self):
        result = self.lint_with('Check: run scripts/check-flag.sh\n', '')
        self.assertEqual(result.returncode, 1)
        self.assertRegex(result.stdout, r"BOOT\.md:\d+ \(boot\.3\): needs exactly one 'Check:' line directly under the heading \(found 0\)")

    def test_lint_names_a_read_path_that_does_not_exist(self):
        result = self.lint_with('templates/thing.md', 'templates/gone.md')
        self.assertEqual(result.returncode, 1)
        self.assertRegex(result.stdout, r"\(boot\.2\.1\): Read names 'templates/gone\.md'")

    def test_lint_names_a_convention_number_with_no_file(self):
        result = self.lint_with('#8 § Principle', '#77')
        self.assertEqual(result.returncode, 1)
        self.assertRegex(result.stdout, r'Read names #77 and no convention file has that number')

    def test_lint_names_a_section_that_does_not_exist(self):
        (self.engine / 'conventions' / '08-errors.md').write_text('# Errors\n\n## Principle and more\n\ntext\n\n```\n## Fenced\n```\n')
        self.assertEqual(self.run_tool('--lint', cwd=self.engine).returncode, 0)  # "Principle" opens the heading
        for entry in ('#8 § Rules', 'conventions/08-errors.md § Fenced'):
            with self.subTest(entry=entry):
                self.setUp()
                (self.engine / 'conventions' / '08-errors.md').write_text('# Errors\n\n## Principle\n\n```\n## Fenced\n```\n')
                result = self.lint_with('#8 § Principle', entry)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn('has no heading that opens with', result.stdout)

    def test_lint_refuses_a_check_that_is_not_an_engine_script(self):
        for check in ('run rm -rf .', 'run scripts/../evil.sh', 'run scripts/check-flag.sh; echo x', 'run scripts/absent.sh', 'looks fine to me'):
            with self.subTest(check=check):
                self.setUp()
                result = self.lint_with('Check: run scripts/check-flag.sh\n', 'Check: %s\n' % check)
                self.assertEqual(result.returncode, 1, result.stdout)

    def test_lint_names_a_repeated_step_id(self):
        result = self.lint_with('## Step 3 - Generate', '## Step 1: Again')
        self.assertRegex(result.stdout, r'\(boot\.1\): the step id appears twice')

    def test_lint_fails_on_a_heading_that_looks_like_a_step_and_is_not(self):
        for heading in ('## Step : Missing id', '##  Step 4: Two spaces', '#### Step 5: Too deep', '## Step'):
            with self.subTest(heading=heading):
                self.setUp()
                result = self.lint_with('## Checklist', heading + '\nRead: none\nProduces: x\nCheck: evidence: x\n\n## Checklist')
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertRegex(result.stdout, r"BOOT\.md:\d+: a heading that opens with 'Step' is not a step")

    def test_lint_leaves_ordinary_headings_alone(self):
        result = self.lint_with('## Checklist', '## Next Step\n\n## Steps to take\n\n## Checklist')
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_lint_refuses_one_ledger_id_in_two_files(self):
        (self.engine / 'scaffolding' / 'SCAF.md').write_text('# S\n\nStep ledger: boot\n\n## Step 40: Other\nRead: none\nProduces: x\nCheck: evidence: x\n')
        result = self.run_tool('--lint', cwd=self.engine)
        self.assertEqual(result.returncode, 1)
        self.assertIn("ledger id 'boot' is also declared by", result.stdout)

    def test_a_ledger_line_shown_inside_a_code_fence_declares_nothing(self):
        (self.engine / 'development' / 'FORMAT.md').write_text('# Format\n\n```\nStep ledger: example\n```\n')
        result = self.run_tool('--lint', cwd=self.engine)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_playbook_with_carriage_returns_is_read(self):
        path = self.engine / 'bootstrap' / 'BOOT.md'
        path.write_bytes(path.read_text().replace('\n', '\r\n').encode())
        result = self.run_tool('--lint', cwd=self.engine)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('OK: 6 steps', result.stdout)

    # --- a playbook in several files ------------------------------------------------

    def split_playbook(self):
        (self.engine / 'bootstrap' / 'BOOT.md').write_text(
            '# Bootstrap\n\nStep ledger: boot\nStep files: bootstrap/BOOT-2.md; bootstrap/BOOT-3.md\n\n'
            '## Step 1: Start\nRead: none\nProduces: the folder\nCheck: evidence: the path\n\n## Step 2: Discovery\n')
        (self.engine / 'bootstrap' / 'BOOT-2.md').write_text(
            '# Discovery\n\n### Step 2.1: Who\nRead: bootstrap/BOOT-2.md\nProduces: answers\nCheck: evidence: quoted\n\n'
            '### Step 2.2: Where\nRead: none\nProduces: answers\nCheck: evidence: quoted\n')
        (self.engine / 'bootstrap' / 'BOOT-3.md').write_text(
            '# Generate\n\n## Step 3: Generate\nRead: none\nProduces: flag.txt\nCheck: run scripts/check-flag.sh\n')

    def test_steps_come_from_the_entry_file_then_its_step_files_in_order(self):
        self.split_playbook()
        lint = self.run_tool('--lint', cwd=self.engine)
        self.assertEqual(lint.returncode, 0, lint.stdout)
        self.assertIn('OK: 6 steps', lint.stdout)  # boot.1, 2.1, 2.2, 3 and the two dev steps
        self.ledger('boot')
        listing = self.run_tool('--list').stdout
        self.assertEqual([l.split()[1] for l in listing.splitlines()], ['boot.1', 'boot.2.1', 'boot.2.2', 'boot.3'])

    def test_the_next_step_points_at_the_file_that_holds_it(self):
        self.split_playbook()
        self.ledger('boot')
        self.run_tool('--close', 'boot.1', '--evidence', 'x')
        result = self.run_tool()
        self.assertIn('Next step: boot.2.1  Who', result.stdout)
        self.assertIn('Playbook:  bootstrap/BOOT-2.md, line 3', result.stdout)

    def test_lint_names_a_step_file_that_is_missing_listed_twice_or_self_declared(self):
        self.split_playbook()
        (self.engine / 'bootstrap' / 'BOOT-3.md').unlink()
        missing = self.run_tool('--lint', cwd=self.engine)
        self.assertEqual(missing.returncode, 1)
        self.assertIn("names bootstrap/BOOT-3.md, which is not a file in the engine", missing.stdout)

        self.setUp(); self.split_playbook()
        entry = self.engine / 'bootstrap' / 'BOOT.md'
        entry.write_text(entry.read_text().replace('bootstrap/BOOT-3.md', 'bootstrap/BOOT-3.md; bootstrap/BOOT-2.md'))
        twice = self.run_tool('--lint', cwd=self.engine)
        self.assertEqual(twice.returncode, 1)
        self.assertIn('step file bootstrap/BOOT-2.md is already listed', twice.stdout)

        self.setUp(); self.split_playbook()
        part = self.engine / 'bootstrap' / 'BOOT-3.md'
        part.write_text(part.read_text().replace('# Generate\n', '# Generate\n\nStep ledger: other\n'))
        declared = self.run_tool('--lint', cwd=self.engine)
        self.assertEqual(declared.returncode, 1)
        self.assertIn("a step file carries no 'Step ledger:' line of its own", declared.stdout)

    def test_a_step_file_that_lists_step_files_fails_the_lint(self):
        self.split_playbook()
        part = self.engine / 'bootstrap' / 'BOOT-2.md'
        (self.engine / 'bootstrap' / 'BOOT-4.md').write_text('# More\n\n## Step 4: Hidden\nRead: none\nProduces: x\nCheck: evidence: x\n')
        part.write_text(part.read_text().replace('# Discovery\n', '# Discovery\n\nStep files: bootstrap/BOOT-4.md\n'))
        result = self.run_tool('--lint', cwd=self.engine)
        self.assertEqual(result.returncode, 1)
        self.assertIn('a step file lists no step files of its own', result.stdout)

    def test_a_step_file_outside_the_engine_is_never_read(self):
        self.split_playbook()
        entry = self.engine / 'bootstrap' / 'BOOT.md'
        entry.write_text(entry.read_text().replace('bootstrap/BOOT-3.md', '../project/PROGRESS.md'))
        result = self.run_tool('--lint', cwd=self.engine)
        self.assertEqual(result.returncode, 1)
        self.assertIn('which is not a file in the engine', result.stdout)

    def test_a_step_id_repeated_across_files_is_named(self):
        self.split_playbook()
        part = self.engine / 'bootstrap' / 'BOOT-3.md'
        part.write_text(part.read_text().replace('## Step 3: Generate', '## Step 1: Again'))
        result = self.run_tool('--lint', cwd=self.engine)
        self.assertRegex(result.stdout, r'BOOT-3\.md:\d+ \(boot\.1\): the step id appears twice')

    def test_lint_of_the_real_engine_passes(self):
        result = subprocess.run(['bash', str(SOURCE / 'scripts' / 'next-step.sh'), '--lint'],
                                cwd=SOURCE, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    # --- a project ----------------------------------------------------------------

    def test_no_ledger_says_how_to_start(self):
        result = self.run_tool()
        self.assertEqual(result.returncode, 1)
        self.assertIn('templates/progress.md', result.stdout)

    def test_unfilled_or_unknown_playbooks_line_is_refused(self):
        self.ledger('[the playbooks this project follows]')
        self.assertEqual(self.run_tool().returncode, 1)
        self.ledger('boot, nonsense')
        result = self.run_tool()
        self.assertEqual(result.returncode, 1)
        self.assertIn("'nonsense'", result.stdout)

    def test_first_step_is_named_with_what_to_read(self):
        self.ledger()
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('Next step: boot.1  Start', result.stdout)
        self.assertIn('bootstrap/BOOT.md, line', result.stdout)
        self.assertIn('--close boot.1 --evidence', result.stdout)

    def test_a_container_is_never_the_next_step_and_reads_resolve(self):
        self.ledger()
        self.run_tool('--close', 'boot.1', '--evidence', 'the folder is /work/thing')
        result = self.run_tool()
        self.assertIn('Next step: boot.2.1  Who it is for', result.stdout)
        self.assertIn('  - conventions/08-errors.md § Principle', result.stdout)
        self.assertIn('  - templates/thing.md', result.stdout)
        self.assertIn('  - project: References.md', result.stdout)
        self.assertIn('Skip when: never', result.stdout)
        self.assertNotIn('Step 99', self.run_tool('--list').stdout)

    def test_evidence_step_needs_evidence(self):
        self.ledger()
        result = self.run_tool('--close', 'boot.1')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.closed(), [])

    def test_steps_close_in_order(self):
        self.ledger()
        result = self.run_tool('--close', 'boot.3', '--evidence', 'x')
        self.assertEqual(result.returncode, 1)
        self.assertIn('the next open step is boot.1', result.stdout)
        self.assertEqual(self.closed(), [])

    def test_a_step_is_skipped_only_where_its_playbook_allows_and_with_a_reason(self):
        self.ledger()
        self.run_tool('--close', 'boot.1', '--evidence', 'done')
        refused = self.run_tool('--skip', 'boot.2.1', '--reason', 'the owner was busy')
        self.assertEqual(refused.returncode, 1)
        self.assertIn('cannot be skipped', refused.stdout)
        self.run_tool('--close', 'boot.2.1', '--evidence', 'Owner: "line cooks and managers, about forty people"')
        self.assertEqual(self.run_tool('--skip', 'boot.2.2').returncode, 1)
        skipped = self.run_tool('--skip', 'boot.2.2', '--reason', 'no extras on this project')
        self.assertEqual(skipped.returncode, 0, skipped.stdout)
        self.assertRegex(self.closed()[-1], r'^- \[-\] boot\.2\.2 \| \d{4}-\d\d-\d\d \| rev \S+ \| cwd \. \| owner - \| basis none \| skipped \(allowed when: the project has no extras\): no extras on this project$')

    def close_up_to_three(self):
        self.ledger()
        self.run_tool('--close', 'boot.1', '--evidence', 'done')
        self.run_tool('--close', 'boot.2.1', '--evidence', 'quoted')
        self.run_tool('--skip', 'boot.2.2', '--reason', 'none')

    def test_command_step_stays_open_while_its_check_fails(self):
        self.close_up_to_three()
        result = self.run_tool('--close', 'boot.3')
        self.assertEqual(result.returncode, 1)
        self.assertIn('FAIL: flag.txt is missing', result.stdout)
        self.assertEqual(len(self.closed()), 3)

    def test_command_step_closes_when_its_check_passes(self):
        self.close_up_to_three()
        (self.project / 'flag.txt').write_text('x')
        result = self.run_tool('--close', 'boot.3')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertRegex(self.closed()[-1], r'^- \[x\] boot\.3 \| .* \| check passed: scripts/check-flag\.sh$')

    def test_a_tick_does_not_outlive_its_check(self):
        self.close_up_to_three()
        (self.project / 'flag.txt').write_text('x')
        self.run_tool('--close', 'boot.3')
        (self.project / 'flag.txt').unlink()
        result = self.run_tool()
        self.assertEqual(result.returncode, 1)
        self.assertIn('REOPENED: boot.3', result.stdout)
        self.assertNotIn('Next step', result.stdout)

    def test_a_hand_written_tick_is_caught_the_same_way(self):
        self.ledger()
        with open(self.project / 'PROGRESS.md', 'a') as f:
            f.write('- [x] boot.1 | 2026-01-01 | rev - | evidence: x\n- [x] boot.2.1 | 2026-01-01 | rev - | evidence: x\n'
                    '- [-] boot.2.2 | 2026-01-01 | rev - | skipped (allowed when: x): x\n- [x] boot.3 | 2026-01-01 | rev - | check passed: scripts/check-flag.sh\n')
        result = self.run_tool()
        self.assertEqual(result.returncode, 1)
        self.assertIn('REOPENED: boot.3', result.stdout)

    def test_evidence_is_kept_on_one_line(self):
        self.ledger()
        self.run_tool('--close', 'boot.1', '--evidence', 'first line\nsecond | third')
        self.assertEqual(len(self.closed()), 1)
        self.assertTrue(self.closed()[0].endswith('evidence: first line second third'))

    def test_repeating_playbook_runs_once_per_unit(self):
        self.close_up_to_three()
        (self.project / 'flag.txt').write_text('x')
        self.run_tool('--close', 'boot.3')
        bare = self.run_tool()
        self.assertEqual(bare.returncode, 0)
        self.assertIn("'dev' repeats", bare.stdout)
        first = self.run_tool('--unit', 'board')
        self.assertIn('Next step: dev.1 @board  Inventory', first.stdout)
        self.assertIn('--close dev.1 --unit board', first.stdout)
        self.run_tool('--close', 'dev.1', '--unit', 'board', '--evidence', 'errors, api')
        self.assertIn('Next step: dev.2 @board', self.run_tool('--unit', 'board').stdout)
        self.assertIn('Next step: dev.1 @profile', self.run_tool('--unit', 'profile').stdout)
        self.run_tool('--close', 'dev.2', '--unit', 'board')
        self.assertIn('Every step is closed', self.run_tool('--unit', 'board').stdout)

    def close_all_of_boot(self):
        self.close_up_to_three()
        (self.project / 'flag.txt').write_text('x')
        self.assertEqual(self.run_tool('--close', 'boot.3').returncode, 0)

    def test_nothing_closes_skips_or_lists_clean_over_a_failing_tick(self):
        self.ledger('boot, dev')
        (self.engine / 'bootstrap' / 'BOOT.md').write_text(BOOT.replace('Check: evidence: the folder\'s path', 'Check: run scripts/check-flag.sh'))
        (self.project / 'flag.txt').write_text('x')
        self.assertEqual(self.run_tool('--close', 'boot.1').returncode, 0)
        (self.project / 'flag.txt').unlink()
        closing = self.run_tool('--close', 'boot.2.1', '--evidence', 'quoted')
        self.assertEqual(closing.returncode, 1)
        self.assertIn('REOPENED: boot.1', closing.stdout)
        self.assertEqual(len(self.closed()), 1)
        listing = self.run_tool('--list')
        self.assertEqual(listing.returncode, 1)
        self.assertIn('REOPENED: boot.1', listing.stdout)

    def test_a_tick_of_any_unit_is_checked_whatever_unit_is_asked_for(self):
        self.close_all_of_boot()
        self.run_tool('--close', 'dev.1', '--unit', 'board', '--evidence', 'errors')
        self.assertEqual(self.run_tool('--close', 'dev.2', '--unit', 'board').returncode, 0)
        (self.project / 'flag.txt').unlink()
        for args in ((), ('--unit', 'profile'), ('--unit', 'board')):
            with self.subTest(args=args):
                result = self.run_tool(*args)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn('dev.2 @board', result.stdout)

    def test_a_check_that_is_not_an_engine_script_is_never_run(self):
        self.close_all_of_boot()
        outside = Path(self.temp.name) / 'outside.sh'
        outside.write_text('#!/bin/bash\ntouch "%s"\nexit 0\n' % (Path(self.temp.name) / 'ran'))
        path = self.engine / 'bootstrap' / 'BOOT.md'
        path.write_text(path.read_text().replace('Check: run scripts/check-flag.sh', 'Check: run ../outside.sh'))
        result = self.run_tool()
        self.assertEqual(result.returncode, 1)
        self.assertIn('is not a check that can be run', result.stdout)
        self.assertFalse((Path(self.temp.name) / 'ran').exists())

    def test_unit_names_are_plain(self):
        self.close_all_of_boot()
        for unit in ('board|x', 'board ', 'a\tb', 'a\nb', 'a b', '@x', '*'):
            with self.subTest(unit=unit):
                before = len(self.closed())
                result = self.run_tool('--close', 'dev.1', '--unit', unit, '--evidence', 'x')
                self.assertEqual(result.returncode, 1)
                self.assertEqual(len(self.closed()), before)

    def test_unit_that_is_a_prefix_of_another_keeps_its_own_ticks(self):
        self.close_all_of_boot()
        self.run_tool('--close', 'dev.1', '--unit', 'board-2', '--evidence', 'x')
        self.assertIn('Next step: dev.1 @board ', self.run_tool('--unit', 'board').stdout)

    def test_ledger_without_a_final_newline_keeps_the_new_line(self):
        (self.project / 'PROGRESS.md').write_text('# Progress\n\n- Playbooks: boot\n\n## Closed steps')
        self.assertEqual(self.run_tool('--close', 'boot.1', '--evidence', 'x').returncode, 0)
        self.assertEqual(len(self.closed()), 1)
        self.assertIn('Next step: boot.2.1', self.run_tool().stdout)

    def test_run_from_a_folder_under_the_project(self):
        self.ledger()
        (self.project / 'src' / 'deep').mkdir(parents=True)
        result = self.run_tool(cwd=self.project / 'src' / 'deep')
        self.assertIn('Next step: boot.1', result.stdout)

    def test_a_failing_check_that_prints_nothing_still_says_so(self):
        self.close_up_to_three()
        (self.engine / 'scripts' / 'check-flag.sh').write_text('#!/bin/bash\nexit 3\n')
        result = self.run_tool('--close', 'boot.3')
        self.assertEqual(result.returncode, 1)
        self.assertIn('printed nothing', result.stdout)

    def test_missing_argument_values_are_refused_not_looped(self):
        self.ledger()
        for args in (('--close',), ('--close', '--evidence', 'x'), ('--skip',), ('--unit',)):
            with self.subTest(args=args):
                result = subprocess.run(['bash', str(self.engine / 'scripts' / 'next-step.sh'), *args],
                                        cwd=self.project, text=True, capture_output=True, timeout=20)
                self.assertEqual(len(self.closed()), 0)
        self.assertEqual(self.run_tool('--close').returncode, 1)

    def test_a_playbook_named_twice_is_walked_once(self):
        self.ledger('boot, boot')
        listing = self.run_tool('--list').stdout
        self.assertEqual(listing.count('boot.1 '), 1)

    def test_list_says_reopened_not_closed_for_a_failing_tick(self):
        self.close_all_of_boot()
        (self.project / 'flag.txt').unlink()
        listing = self.run_tool('--list').stdout
        self.assertRegex(listing, r'(?m)^reopened\s+boot\.3\s')
        self.assertNotRegex(listing, r'(?m)^closed\s+boot\.3\s')
        self.assertRegex(listing, r'(?m)^closed\s+boot\.1\s')

    def test_a_unit_is_never_an_option(self):
        self.close_all_of_boot()
        result = self.run_tool('--close', 'dev.1', '--unit', '--close', '--evidence', 'x')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(len([l for l in self.closed() if 'dev.' in l]), 0)

    def test_a_read_entry_may_say_when_it_applies(self):
        path = self.engine / 'bootstrap' / 'BOOT.md'
        path.write_text(path.read_text().replace('Read: conventions/08-errors.md', 'Read: conventions/08-errors.md (when the build is custom); #8 § Rules (when errors matter)'))
        self.assertEqual(self.run_tool('--lint', cwd=self.engine).returncode, 0)
        path.write_text(path.read_text().replace('conventions/08-errors.md (when', 'conventions/gone.md (when'))
        lint = self.run_tool('--lint', cwd=self.engine)
        self.assertEqual(lint.returncode, 1)
        self.assertIn("Read names 'conventions/gone.md'", lint.stdout)

    def test_the_condition_is_shown_with_the_reading(self):
        path = self.engine / 'bootstrap' / 'BOOT.md'
        path.write_text(path.read_text().replace('Read: none\nProduces: the project folder', 'Read: templates/thing.md (when the project is new)\nProduces: the project folder'))
        self.ledger()
        self.assertIn('  - templates/thing.md (when the project is new)', self.run_tool().stdout)

    def test_check_arguments_may_name_project_paths_and_nothing_above(self):
        shutil.copy(SOURCE / 'scripts' / 'check-exists.sh', self.engine / 'scripts' / 'check-exists.sh')
        good = self.lint_with('Check: run scripts/check-flag.sh\n', 'Check: run scripts/check-exists.sh docs/systems flag.txt\n')
        self.assertEqual(good.returncode, 0, good.stdout)
        for args in ('../flag.txt', '/etc/passwd', 'docs/../../x'):
            with self.subTest(args=args):
                self.setUp()
                shutil.copy(SOURCE / 'scripts' / 'check-exists.sh', self.engine / 'scripts' / 'check-exists.sh')
                bad = self.lint_with('Check: run scripts/check-flag.sh\n', 'Check: run scripts/check-exists.sh %s\n' % args)
                self.assertEqual(bad.returncode, 1, bad.stdout)

    def test_check_exists(self):
        script = SOURCE / 'scripts' / 'check-exists.sh'
        run = lambda *a: subprocess.run(['bash', str(script), *a], cwd=self.project, text=True, capture_output=True)
        self.assertEqual(run().returncode, 1)
        self.assertEqual(run('References.md').returncode, 1)
        (self.project / 'References.md').write_text('')
        self.assertIn('is empty', run('References.md').stdout)
        (self.project / 'References.md').write_text('x')
        (self.project / 'docs').mkdir()
        self.assertEqual(run('References.md', 'docs').returncode, 0)
        self.assertEqual(run('References.md', 'gone.md').returncode, 1)
        self.assertEqual(run('../References.md').returncode, 1)
        self.assertEqual(run('/etc/hosts').returncode, 1)

    def test_one_failure_for_a_duplicated_ledger_id(self):
        (self.engine / 'scaffolding' / 'SCAF.md').write_text('# S\n\nStep ledger: boot\n\n## Step 40: A\nRead: none\nProduces: x\nCheck: evidence: x\n\n## Step 41: B\nRead: none\nProduces: x\nCheck: evidence: x\n')
        result = self.run_tool('--lint', cwd=self.engine)
        self.assertEqual(result.stdout.count('is also declared by'), 1)

    # --- the project's own commands, and a command with evidence -----------------------

    def project_playbook(self, check='run project: typecheck, test'):
        (self.engine / 'bootstrap' / 'BOOT.md').write_text(
            '# B\n\nStep ledger: boot\n\n## Step 1: Build\nRead: none\nProduces: code\nCheck: %s\n\n'
            '## Step 2: More\nRead: none\nProduces: more\nCheck: evidence: what was seen\n' % check)
        self.ledger('boot')

    def commands(self, typecheck='`true`', test='`test -f flag.txt`'):
        (self.project / 'References.md').write_text(
            '# References\n\n## Commands\n\n```\ndev:       `start`\ntypecheck: %s\ntest:      %s\n```\n\n## Next\n\ntest: `false` (not this one)\n' % (typecheck, test))

    def test_a_step_closes_on_the_projects_own_commands(self):
        self.project_playbook(); self.commands()
        refused = self.run_tool('--close', 'boot.1')
        self.assertEqual(refused.returncode, 1)
        self.assertIn("the project's test command failed: test -f flag.txt", refused.stdout)
        (self.project / 'flag.txt').write_text('x')
        closed = self.run_tool('--close', 'boot.1')
        self.assertEqual(closed.returncode, 0, closed.stdout)
        self.assertRegex(self.closed()[-1], r'check passed: project: typecheck, test$')

    def test_a_command_never_recorded_fails_and_none_is_not_applicable(self):
        self.project_playbook(); self.commands(typecheck='[command to run type checker]')
        (self.project / 'flag.txt').write_text('x')
        result = self.run_tool('--close', 'boot.1')
        self.assertEqual(result.returncode, 1)
        self.assertIn("records no command for 'typecheck'", result.stdout)
        self.commands(typecheck='none, the language is untyped')
        self.assertEqual(self.run_tool('--close', 'boot.1').returncode, 0)

    def test_no_references_file_fails_a_project_check(self):
        self.project_playbook()
        result = self.run_tool('--close', 'boot.1')
        self.assertEqual(result.returncode, 1)
        self.assertIn("records no command for 'typecheck'", result.stdout)

    def test_project_commands_are_rerun_when_a_step_closes_not_on_a_bare_run(self):
        self.project_playbook(); self.commands()
        (self.project / 'flag.txt').write_text('x')
        self.run_tool('--close', 'boot.1')
        (self.project / 'flag.txt').unlink()
        bare = self.run_tool()
        self.assertEqual(bare.returncode, 0, bare.stdout)
        self.assertIn('Next step: boot.2', bare.stdout)
        self.assertIn('--verify', bare.stdout)
        forced = self.run_tool('--verify')
        self.assertEqual(forced.returncode, 1)
        self.assertIn('REOPENED: boot.1', forced.stdout)
        closing = self.run_tool('--close', 'boot.2', '--evidence', 'x')
        self.assertEqual(closing.returncode, 1)
        self.assertIn('REOPENED: boot.1', closing.stdout)
        self.assertEqual(len(self.closed()), 1)

    def test_an_endpoint_folder_runs_its_own_recorded_commands_in_its_own_folder(self):
        self.project_playbook(check='run project: typecheck')
        endpoint = self.project / 'frontend'
        endpoint.mkdir()
        (endpoint / 'References.md').write_text('# R\n\n## Commands\n\n```\ntypecheck: `test -f here.txt`\n```\n')
        (endpoint / 'here.txt').write_text('x')
        from_root = self.run_tool('--close', 'boot.1')
        self.assertEqual(from_root.returncode, 1)  # the root records no commands
        closed = self.run_tool('--close', 'boot.1', cwd=endpoint)
        self.assertEqual(closed.returncode, 0, closed.stdout)

    def test_none_means_none_and_nothing_that_merely_starts_with_it(self):
        # The unmarked value is the probe of "none": it opens with those letters and is not passed over.
        self.project_playbook(check='run project: typecheck')
        for value, failure in (('nonexistent-tool --check', "records 'typecheck' without a command in backticks"),
                               ('`nonexistent-tool --check`', "the project's typecheck command failed: nonexistent-tool --check")):
            with self.subTest(value=value):
                self.commands(typecheck=value)
                result = self.run_tool('--close', 'boot.1')
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn(failure, result.stdout)
        self.commands(typecheck='None.')
        self.assertEqual(self.run_tool('--close', 'boot.1').returncode, 0)

    def test_a_listing_says_when_project_commands_were_not_rerun(self):
        self.project_playbook(); self.commands()
        (self.project / 'flag.txt').write_text('x')
        self.run_tool('--close', 'boot.1')
        (self.project / 'flag.txt').unlink()
        listing = self.run_tool('--list')
        self.assertIn('--verify', listing.stdout)
        verified = self.run_tool('--list', '--verify')
        self.assertEqual(verified.returncode, 1)
        self.assertRegex(verified.stdout, r'(?m)^reopened\s+boot\.1\s')

    def test_a_command_may_also_ask_for_evidence(self):
        self.project_playbook(check='run scripts/check-flag.sh; evidence: what the screen showed when the error was thrown')
        (self.project / 'flag.txt').write_text('x')
        refused = self.run_tool('--close', 'boot.1')
        self.assertEqual(refused.returncode, 1)
        self.assertIn('what the screen showed', refused.stdout)
        self.assertEqual(self.run_tool('--close', 'boot.1', '--evidence', 'the fallback page').returncode, 0)
        self.assertRegex(self.closed()[-1], r'check passed: scripts/check-flag\.sh \| evidence: the fallback page$')
        self.assertIn('--evidence', self.run_tool().stdout)  # step 2 closes on evidence

    def test_lint_knows_the_project_form_and_refuses_shell_in_it(self):
        for check, ok in (('run project: typecheck, lint, test', True), ('run project: test; evidence: what was seen', True),
                          ('run project: test; rm -rf .', False), ('run project: $(id)', False), ('run project:', False),
                          ('run project: test; evidence: ', False)):
            with self.subTest(check=check):
                self.setUp(); self.project_playbook(check=check)
                result = self.run_tool('--lint', cwd=self.engine)
                self.assertEqual(result.returncode == 0, ok, result.stdout)

    # --- a recorded command is the text in backticks; nothing else is run ---------------

    MIGRATION = ("records 'typecheck' without a command in backticks: %s (write the command in backticks right after "
                 "the label, for example typecheck: `<command>`; text after the closing backtick is a note; a value in "
                 "brackets means none is recorded yet; none means the project has no such command)")

    def close_with(self, typecheck, test='`true`'):
        """A fresh project whose boot.1 runs its typecheck and test commands, and an attempt to close it."""
        self.setUp(); self.project_playbook(); self.commands(typecheck=typecheck, test=test)
        (self.project / 'flag.txt').write_text('x')
        return self.run_tool('--close', 'boot.1')

    def test_a_prose_placeholder_never_passes_a_project_check(self):
        # Placeholders as a project setup wrote them, with no backticks. "set" is a shell builtin:
        # read by a shell, each of these sentences exits 0.
        for placeholder in ('set up during scaffold', 'set at scaffold'):
            with self.subTest(placeholder=placeholder):
                result = self.close_with(placeholder)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn('FAIL: References.md, section Commands, ' + self.MIGRATION % placeholder, result.stdout)
                self.assertEqual(self.closed(), [])

    def test_a_command_in_backticks_closes_the_step(self):
        # Read whole by a shell, the note in parentheses would be a syntax error.
        result = self.close_with('`true`', test='`test -f flag.txt`   (the flag the build leaves)')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertRegex(self.closed()[-1], r'^- \[x\] boot\.1 \| .* \| check passed: project: typecheck, test$')

    def test_a_note_after_the_backticks_never_runs(self):
        # Read whole by a shell, each value would create ran.txt and fail.
        for value in ('`true` && touch ran.txt && exit 3', '`true`; touch ran.txt; exit 3'):
            with self.subTest(value=value):
                result = self.close_with(value)
                self.assertEqual(result.returncode, 0, result.stdout)
                self.assertFalse((self.project / 'ran.txt').exists())
                self.assertEqual(len(self.closed()), 1)

    def test_a_shell_only_check_in_backticks_passes_when_true_and_fails_when_false(self):
        self.project_playbook(); self.commands(typecheck='`[ -d . ]`', test='`test -f flag.txt`')
        refused = self.run_tool('--close', 'boot.1')
        self.assertEqual(refused.returncode, 1, refused.stdout)
        self.assertIn("FAIL: the project's test command failed: test -f flag.txt", refused.stdout)
        self.assertEqual(self.closed(), [])
        (self.project / 'flag.txt').write_text('x')
        closed = self.run_tool('--close', 'boot.1')
        self.assertEqual(closed.returncode, 0, closed.stdout)
        self.assertEqual(len(self.closed()), 1)

    def test_an_unmarked_command_fails_with_the_migration_message_and_never_runs(self):
        # Each would pass if it were run: the flag is there, and touch succeeds.
        for value in ('test -f flag.txt', 'touch ran.txt', 'touch ran.txt   # the notes a project writes',
                      'use `touch ran.txt` here', '`touch ran.txt'):
            with self.subTest(value=value):
                result = self.close_with(value)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn('FAIL: References.md, section Commands, ' + self.MIGRATION % value, result.stdout)
                self.assertFalse((self.project / 'ran.txt').exists())
                self.assertEqual(self.closed(), [])

    def test_more_than_one_pair_of_backticks_fails_and_nothing_runs(self):
        for value in ('`touch one.txt` && `touch two.txt`', '`touch one.txt` then `touch two.txt`', '`touch one.txt` and a stray ` mark'):
            with self.subTest(value=value):
                result = self.close_with(value)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("FAIL: References.md, section Commands, records 'typecheck' with more than one pair of backticks: %s "
                              "(record one command: join its steps with && inside one pair of backticks" % value, result.stdout)
                self.assertFalse((self.project / 'one.txt').exists())
                self.assertFalse((self.project / 'two.txt').exists())
                self.assertEqual(self.closed(), [])

    def test_empty_backticks_count_as_not_recorded(self):
        for value in ('``', '` `', '`` until the scaffold picks one'):
            with self.subTest(value=value):
                result = self.close_with(value)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("FAIL: References.md, section Commands, records no command for 'typecheck' "
                              "(write the command in backticks, or none when the project has no such command)", result.stdout)
                self.assertEqual(self.closed(), [])

    def test_brackets_none_and_na_behave_as_before(self):
        for value in ('[command to run type checker]', '[`true` once the scaffold picks one]'):
            with self.subTest(value=value):
                result = self.close_with(value)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("records no command for 'typecheck'", result.stdout)
                self.assertEqual(self.closed(), [])
        for value in ('none', 'None.', 'none, the language is untyped', 'n/a', 'N/A: no type checker', 'none `touch ran.txt`'):
            with self.subTest(value=value):
                result = self.close_with(value)
                self.assertEqual(result.returncode, 0, result.stdout)
                self.assertFalse((self.project / 'ran.txt').exists())
                self.assertRegex(self.closed()[-1], r'check passed: project: typecheck, test$')

    def test_closed_project_checks_rerun_as_before_and_meet_the_contract(self):
        # A closed step whose recorded command is now a sentence: a bare run and a listing still
        # leave it alone; a close, a skip, and --verify re-run it and refuse it with the migration message.
        path = self.engine / 'bootstrap' / 'BOOT.md'
        self.project_playbook(); self.commands()
        path.write_text(path.read_text() + '\n## Step 3: Extra\nRead: none\nProduces: x\nCheck: evidence: x\nSkip when: nothing extra\n')
        (self.project / 'flag.txt').write_text('x')
        self.assertEqual(self.run_tool('--close', 'boot.1').returncode, 0)
        self.commands(typecheck='set up during scaffold')
        bare = self.run_tool()
        self.assertEqual(bare.returncode, 0, bare.stdout)
        self.assertIn('Next step: boot.2', bare.stdout)
        self.assertIn('--verify', bare.stdout)
        listing = self.run_tool('--list')
        self.assertEqual(listing.returncode, 0, listing.stdout)
        self.assertRegex(listing.stdout, r'(?m)^closed\s+boot\.1\s')
        self.assertIn('were not re-run for this listing', listing.stdout)
        for args in (('--verify',), ('--list', '--verify'), ('--close', 'boot.2', '--evidence', 'x')):
            with self.subTest(args=args):
                result = self.run_tool(*args)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn('REOPENED: boot.1', result.stdout)
                self.assertIn(self.MIGRATION % 'set up during scaffold', result.stdout)
        self.commands()
        self.assertEqual(self.run_tool('--close', 'boot.2', '--evidence', 'x').returncode, 0)
        self.commands(typecheck='set up during scaffold')
        skipping = self.run_tool('--skip', 'boot.3', '--reason', 'nothing extra here')
        self.assertEqual(skipping.returncode, 1, skipping.stdout)
        self.assertIn(self.MIGRATION % 'set up during scaffold', skipping.stdout)
        self.assertEqual(len(self.closed()), 2)

    # --- what follows once every step is closed -------------------------------------------

    def two_playbooks(self, order, boot_next=True, scaf_next=True):
        if boot_next:
            path = self.engine / 'bootstrap' / 'BOOT.md'
            path.write_text(path.read_text() + '\n## Next Step\n\nOn to the scaffold.\n')
        (self.engine / 'scaffolding' / 'SCAF.md').write_text(
            '# Scaffold\n\nStep ledger: scaf\n\n## Step 1: Build\nRead: none\nProduces: code\nCheck: evidence: what was built\n'
            + ('\n## Next Step\n\nOn to the features.\n' if scaf_next else ''))
        self.ledger(order)

    def close_boot(self, run=None):
        run = run or self.run_tool
        (self.project / 'flag.txt').write_text('x')
        for args in (('--close', 'boot.1', '--evidence', 'x'), ('--close', 'boot.2.1', '--evidence', 'x'),
                     ('--skip', 'boot.2.2', '--reason', 'no extras'), ('--close', 'boot.3')):
            result = run(*args)
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_every_step_closed_names_the_next_step_section_of_the_last_listed_playbook(self):
        self.two_playbooks('boot, scaf')
        self.close_boot()
        self.assertIn('Next step: scaf.1', self.run_tool().stdout)
        self.assertEqual(self.run_tool('--close', 'scaf.1', '--evidence', 'x').returncode, 0)
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout, 'Every step is closed. What follows: the Next Step section of %s/scaffolding/SCAF.md.\n' % self.engine)

        self.setUp(); self.two_playbooks('scaf, boot')
        self.assertEqual(self.run_tool('--close', 'scaf.1', '--evidence', 'x').returncode, 0)
        self.close_boot()
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout, 'Every step is closed. What follows: the Next Step section of %s/bootstrap/BOOT.md.\n' % self.engine)

    def test_every_step_closed_says_when_the_last_playbook_names_no_next_step(self):
        # A Next Step heading inside a code fence, or in another playbook, is not the last playbook's.
        self.two_playbooks('boot, scaf', scaf_next=False)
        scaf = self.engine / 'scaffolding' / 'SCAF.md'
        scaf.write_text(scaf.read_text() + '\n```\n## Next Step\n```\n')
        self.close_boot()
        self.assertEqual(self.run_tool('--close', 'scaf.1', '--evidence', 'x').returncode, 0)
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout, 'Every step is closed; %s/scaffolding/SCAF.md names no next step.\n' % self.engine)

        # Only the entry file counts: a step file's own Next Step heading is not the playbook's.
        self.setUp(); self.split_playbook(); self.ledger('boot')
        part = self.engine / 'bootstrap' / 'BOOT-3.md'
        part.write_text(part.read_text() + '\n## Next Step\n\nNot the entry file.\n')
        (self.project / 'flag.txt').write_text('x')
        for args in (('boot.1', '--evidence', 'x'), ('boot.2.1', '--evidence', 'x'), ('boot.2.2', '--evidence', 'x'), ('boot.3',)):
            closing = self.run_tool('--close', *args)
            self.assertEqual(closing.returncode, 0, closing.stdout)
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout, 'Every step is closed; %s/bootstrap/BOOT.md names no next step.\n' % self.engine)

    def test_the_pointer_names_the_engine_by_its_folder_in_the_project(self):
        # An engine installed under a folder name of the project's choosing is named by that folder,
        # as the "Close it:" line names the script. Resolved paths: a symlinked temporary folder
        # would otherwise place the engine outside the project the script finds.
        project = Path(self.temp.name).resolve() / 'owned'
        shutil.copytree(self.engine, project / 'house-rules')
        entry = project / 'house-rules' / 'bootstrap' / 'BOOT.md'
        entry.write_text(entry.read_text() + '\n## Next Step\n\nOn to the scaffold.\n')
        (project / 'PROGRESS.md').write_text('# Progress\n\n- Playbooks: boot\n\n## Step history\n\n')
        run = lambda *args: subprocess.run(['bash', str(project / 'house-rules' / 'scripts' / 'next-step.sh'), *args],
                                           cwd=project, text=True, capture_output=True)
        self.assertIn('Close it:  house-rules/scripts/next-step.sh --close boot.1 --evidence', run().stdout)
        self.project = project
        self.close_boot(run)
        result = run()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout, 'Every step is closed. What follows: the Next Step section of house-rules/bootstrap/BOOT.md.\n')

    def test_the_repeating_unit_prompt_is_unchanged(self):
        feature = self.engine / 'development' / 'FEATURE.md'
        feature.write_text(feature.read_text() + '\n## Next Step\n\nOn to the next feature.\n')
        self.close_all_of_boot()
        bare = self.run_tool()
        self.assertEqual(bare.returncode, 0, bare.stdout)
        self.assertEqual(bare.stdout, "Every one-time step is closed. The playbook 'dev' repeats: run with --unit NAME (the feature's name).\n")
        self.assertEqual(self.run_tool('--close', 'dev.1', '--unit', 'board', '--evidence', 'x').returncode, 0)
        self.assertEqual(self.run_tool('--close', 'dev.2', '--unit', 'board').returncode, 0)
        self.assertEqual(self.run_tool().stdout, bare.stdout)
        unit = self.run_tool('--unit', 'board')
        self.assertEqual(unit.returncode, 0, unit.stdout)
        self.assertEqual(unit.stdout, 'Every step is closed. What follows: the Next Step section of %s/development/FEATURE.md.\n' % self.engine)

    def test_every_step_closed_still_notes_project_commands_that_were_not_rerun(self):
        self.project_playbook(); self.commands()
        (self.project / 'flag.txt').write_text('x')
        self.assertEqual(self.run_tool('--close', 'boot.1').returncode, 0)
        self.assertEqual(self.run_tool('--close', 'boot.2', '--evidence', 'x').returncode, 0)
        (self.project / 'flag.txt').unlink()
        bare = self.run_tool()
        self.assertEqual(bare.returncode, 0, bare.stdout)
        self.assertEqual(bare.stdout, "Every step is closed; %s/bootstrap/BOOT.md names no next step.\n"
                         "Note:      closed steps that ran the project's own commands are re-run when a step closes, or now with --verify.\n" % self.engine)
        verified = self.run_tool('--verify')
        self.assertEqual(verified.returncode, 1, verified.stdout)
        self.assertIn('REOPENED: boot.1', verified.stdout)

    def test_the_unit_reaches_the_check(self):
        self.close_all_of_boot()
        (self.engine / 'scripts' / 'check-flag.sh').write_text('#!/bin/bash\necho "unit=$ARCHETYPE_STEP_UNIT" > seen.txt\nexit 0\n')
        self.run_tool('--close', 'dev.1', '--unit', 'board', '--evidence', 'x')
        self.run_tool('--close', 'dev.2', '--unit', 'board')
        self.assertEqual((self.project / 'seen.txt').read_text().strip(), 'unit=board')

    def test_list_shows_every_leaf_with_its_state(self):
        self.close_up_to_three()
        listing = self.run_tool('--list').stdout
        self.assertRegex(listing, r'closed\s+boot\.1\s+Start')
        self.assertRegex(listing, r'skipped\s+boot\.2\.2')
        self.assertRegex(listing, r'open\s+boot\.3\s+Generate')
        self.assertNotRegex(listing, r'boot\.2\s+Discovery')

    def test_ledger_with_carriage_returns_is_read(self):
        self.close_up_to_three()
        path = self.project / 'PROGRESS.md'
        path.write_bytes(path.read_text().replace('\n', '\r\n').encode())
        self.assertIn('Next step: boot.3', self.run_tool().stdout)

    def test_system_shell_gives_the_same_answer(self):
        self.ledger()
        result = subprocess.run(['/bin/bash', str(self.engine / 'scripts' / 'next-step.sh')],
                                cwd=self.project, text=True, capture_output=True)
        self.assertIn('Next step: boot.1  Start', result.stdout)

    # --- append-only recovery -----------------------------------------------------

    def decisions(self, reason='first direction'):
        (self.project / 'References.md').write_text('# References\n\n- Decision location: DECISIONS.md\n')
        (self.project / 'DECISIONS.md').write_text(
            '# Decisions\n\n### DEC-001: Direction\nDate: 2026-09-19\nStatus: accepted\n'
            'Decision: blue\nReason: %s\nAlternatives: red\nAuthority: owner\nEvidence: owner words\n'
            'Review: requirement-change\nDepends on: none\nSupersedes: none\nHistory: 2026-09-19 accepted\n' % reason)

    def test_reopen_follows_dependencies_including_a_skip_and_keeps_unrelated_work(self):
        path = self.engine / 'bootstrap' / 'BOOT.md'
        text = path.read_text().replace('Produces: the audience answers\nCheck:', 'Produces: the audience answers\nDepends on: boot.1\nCheck:')
        text = text.replace('Produces: nothing when it does not apply\nCheck:', 'Produces: nothing when it does not apply\nDepends on: boot.2.1\nCheck:')
        path.write_text(text)
        self.close_up_to_three()
        before = self.closed()[:]
        reopened = self.run_tool('--reopen', 'boot.1', '--reason', 'the premise changed')
        self.assertEqual(reopened.returncode, 0, reopened.stdout)
        self.assertIn('Reopened: boot.2.2', reopened.stdout)
        self.assertEqual(self.closed()[:len(before)], before)
        self.assertRegex(self.run_tool('--list').stdout, r'(?m)^reopened\s+boot\.2\.2\s')

    def test_invalid_cycle_and_repeated_reopen_leave_history_unchanged(self):
        self.close_up_to_three()
        ledger = self.project / 'PROGRESS.md'
        original = ledger.read_bytes()
        unknown = self.run_tool('--reopen', 'boot.404', '--reason', 'test')
        self.assertEqual(unknown.returncode, 1)
        self.assertEqual(ledger.read_bytes(), original)
        path = self.engine / 'bootstrap' / 'BOOT.md'
        path.write_text(path.read_text().replace('Produces: the project folder\nCheck:', 'Produces: the project folder\nDepends on: boot.2.1\nCheck:').replace('Produces: the audience answers\nCheck:', 'Produces: the audience answers\nDepends on: boot.1\nCheck:'))
        cycle = self.run_tool('--reopen', 'boot.1', '--reason', 'test')
        self.assertEqual(cycle.returncode, 1)
        self.assertEqual(ledger.read_bytes(), original)
        path.write_text(BOOT)
        self.assertEqual(self.run_tool('--reopen', 'boot.1', '--reason', 'test').returncode, 0)
        after = ledger.read_bytes()
        self.assertEqual(self.run_tool('--reopen', 'boot.1', '--reason', 'again').returncode, 1)
        self.assertEqual(ledger.read_bytes(), after)

    def test_interrupted_atomic_reopen_batch_leaves_the_ledger_unchanged(self):
        self.ledger('boot')
        ledger = self.project / 'PROGRESS.md'; before = ledger.read_bytes()
        spec = importlib.util.spec_from_file_location('step_recovery_under_test', SOURCE / 'scripts' / 'step-recovery.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        with mock.patch.object(module.os, 'replace', side_effect=OSError('interrupted')):
            with self.assertRaises(OSError):
                module.append_reopen_events(ledger, 'boot.1', 'changed', '2026-09-19', ['boot.1', 'boot.2.1'])
        self.assertEqual(ledger.read_bytes(), before)

    def test_changed_decision_or_dirty_input_makes_review_evidence_stale(self):
        path = self.engine / 'bootstrap' / 'BOOT.md'
        path.write_text(path.read_text().replace('Produces: the project folder\nCheck:', 'Produces: the project folder\nBasis: decisions and inputs required\nCheck:'))
        self.ledger('boot')
        self.decisions()
        artifact = self.project / 'review.md'
        artifact.write_text('# Review\n\n- Decision basis: DEC-001\n')
        closed = self.run_tool('--close', 'boot.1', '--evidence', 'reviewed', '--basis', 'DEC-001', '--input', 'review.md')
        self.assertEqual(closed.returncode, 0, closed.stdout)
        artifact.write_text('# Review changed\n\n- Decision basis: DEC-001\n')
        stale = self.run_tool()
        self.assertEqual(stale.returncode, 1, stale.stdout)
        self.assertIn('declared decision or input basis changed', stale.stdout)

    def test_markdown_input_cannot_claim_a_different_decision_basis(self):
        path = self.engine / 'bootstrap' / 'BOOT.md'
        path.write_text(path.read_text().replace('Produces: the project folder\nCheck:', 'Produces: the project folder\nBasis: decisions and inputs required\nCheck:'))
        self.ledger('boot'); self.decisions()
        (self.project / 'review.md').write_text('- Decision basis: DEC-002\n')
        before = (self.project / 'PROGRESS.md').read_bytes()
        result = self.run_tool('--close', 'boot.1', '--evidence', 'x', '--basis', 'DEC-001', '--input', 'review.md')
        self.assertEqual(result.returncode, 1)
        self.assertIn('declares decision basis', result.stdout)
        self.assertEqual((self.project / 'PROGRESS.md').read_bytes(), before)
        malicious = self.run_tool('--close', 'boot.1', '--evidence', 'x', '--basis', 'DEC-001', '--input', 'review.md;inputs=other')
        self.assertEqual(malicious.returncode, 1)
        self.assertEqual((self.project / 'PROGRESS.md').read_bytes(), before)

    def test_reopening_a_shared_prerequisite_reopens_every_dependent_unit(self):
        feature = self.engine / 'development' / 'FEATURE.md'
        feature.write_text(feature.read_text().replace('Produces: the inventory\nCheck:', 'Produces: the inventory\nDepends on: boot.1\nCheck:'))
        self.close_all_of_boot()
        for unit in ('phone', 'desktop'):
            self.assertEqual(self.run_tool('--close', 'dev.1', '--unit', unit, '--evidence', 'x').returncode, 0)
        result = self.run_tool('--reopen', 'boot.1', '--reason', 'audience changed')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('dev.1 @phone', result.stdout)
        self.assertIn('dev.1 @desktop', result.stdout)

    def test_missing_cross_playbook_prerequisite_requires_explicit_migration(self):
        path = self.engine / 'bootstrap' / 'BOOT.md'
        path.write_text(path.read_text().replace('Produces: the project folder\nCheck:', 'Produces: the project folder\nDepends on: dev.1\nCheck:'))
        self.ledger('boot')
        before = (self.project / 'PROGRESS.md').read_bytes()
        result = self.run_tool('--close', 'boot.1', '--evidence', 'x')
        self.assertEqual(result.returncode, 1)
        self.assertIn('include its playbook', result.stdout)
        self.assertEqual((self.project / 'PROGRESS.md').read_bytes(), before)

    def test_decision_validation_rejects_unknown_duplicate_and_cycles(self):
        self.decisions()
        validate = lambda: subprocess.run(
            ['python3', str(self.engine / 'scripts' / 'step-recovery.py'), 'validate-decisions', '--project', str(self.project)],
            text=True, capture_output=True)
        decision_path = self.project / 'DECISIONS.md'
        original = decision_path.read_text()
        decision_path.write_text(original.replace('Depends on: none', 'Depends on: DEC-999'))
        self.assertIn('unknown decision', validate().stdout)
        decision_path.write_text(original + original.split('### DEC-001', 1)[1].join(['\n### DEC-001', '']))
        self.assertNotEqual(validate().returncode, 0)
        second = original.replace('DEC-001', 'DEC-002').replace('Depends on: none', 'Depends on: DEC-001')
        decision_path.write_text(original.replace('Depends on: none', 'Depends on: DEC-002') + '\n' + second)
        self.assertIn('cycle', validate().stdout)
        decision_path.write_text(original.replace('Decision: blue', 'Decision: **pending**'))
        self.assertIn('template placeholder', validate().stdout)

    def test_parent_decision_change_and_new_superseder_stale_child_basis(self):
        self.ledger('boot')
        self.decisions()
        path = self.project / 'DECISIONS.md'
        parent = path.read_text().replace('DEC-001', 'DEC-000').replace('Decision: blue', 'Decision: web')
        child = path.read_text().replace('Depends on: none', 'Depends on: DEC-000')
        path.write_text(parent + '\n' + child)
        artifact = self.project / 'review.md'; artifact.write_text('- Decision basis: DEC-001\n')
        self.assertEqual(self.run_tool('--close', 'boot.1', '--evidence', 'x', '--basis', 'DEC-001', '--input', 'review.md').returncode, 0)
        path.write_text(path.read_text().replace('Decision: web', 'Decision: native'))
        self.assertIn('basis changed', self.run_tool().stdout)
        reopened = self.run_tool('--reopen', 'DEC-000', '--reason', 'platform changed')
        self.assertEqual(reopened.returncode, 0, reopened.stdout)
        self.assertIn('boot.1', reopened.stdout)

        self.setUp(); self.ledger('boot'); self.decisions(); artifact = self.project / 'review.md'; artifact.write_text('- Decision basis: DEC-001\n')
        self.assertEqual(self.run_tool('--close', 'boot.1', '--evidence', 'x', '--basis', 'DEC-001', '--input', 'review.md').returncode, 0)
        old = (self.project / 'DECISIONS.md').read_text()
        newer = old.replace('DEC-001', 'DEC-002').replace('Decision: blue', 'Decision: green').replace('Supersedes: none', 'Supersedes: DEC-001')
        (self.project / 'DECISIONS.md').write_text(old + '\n' + newer)
        self.assertIn('basis changed', self.run_tool().stdout)

    def test_appending_an_unrelated_decision_does_not_stale_the_previous_last_record(self):
        self.ledger('boot'); self.decisions()
        artifact = self.project / 'review.md'; artifact.write_text('- Decision basis: DEC-001\n')
        self.assertEqual(self.run_tool('--close', 'boot.1', '--evidence', 'x', '--basis', 'DEC-001', '--input', 'review.md').returncode, 0)
        old = (self.project / 'DECISIONS.md').read_text()
        unrelated = (old[old.index('### DEC-001'):].replace('DEC-001', 'DEC-005')
                     .replace('Status: accepted', 'Status: proposed')
                     .replace('Decision: blue', 'Decision: api pagination')
                     .replace('Supersedes: none', 'Supersedes: DEC-001'))
        (self.project / 'DECISIONS.md').write_text(old + '\n\n' + unrelated)
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('Next step: boot.2.1', result.stdout)

    def test_historical_checks_keep_each_units_endpoint_directory(self):
        self.project_playbook(check='run project: typecheck')
        playbook = self.engine / 'bootstrap' / 'BOOT.md'
        playbook.write_text(playbook.read_text().replace('Step ledger: boot', 'Step ledger: boot (per feature)'))
        endpoints = []
        for name in ('one', 'two'):
            endpoint = self.project / name; endpoint.mkdir(); endpoints.append(endpoint)
            nested = endpoint / 'nested'; nested.mkdir()
            (endpoint / 'References.md').write_text('# R\n\n## Commands\n\n```\ntypecheck: `test -f here.txt`\n```\n')
            (endpoint / 'here.txt').write_text(name)
            result = self.run_tool('--close', 'boot.1', '--unit', name, cwd=nested)
            self.assertEqual(result.returncode, 0, result.stdout)
        (endpoints[0] / 'here.txt').unlink()
        (endpoints[0] / 'nested' / 'References.md').write_text('# R\n\n## Commands\n\n```\ntypecheck: `true`\n```\n')
        verified = self.run_tool('--list', '--verify', '--unit', 'two', cwd=endpoints[1])
        self.assertEqual(verified.returncode, 1, verified.stdout)
        self.assertIn('boot.1 @one', verified.stdout)
        self.assertIn("project's typecheck command failed", verified.stdout)

    def test_historical_check_cache_keeps_distinct_command_owners(self):
        self.project_playbook(check='run project: typecheck')
        playbook = self.engine / 'bootstrap' / 'BOOT.md'
        playbook.write_text(playbook.read_text().replace(
            'Check: evidence: what was seen', 'Check: run project: typecheck'))
        endpoint = self.project / 'frontend'; endpoint.mkdir()
        nested = endpoint / 'nested'; nested.mkdir()
        (endpoint / 'References.md').write_text(
            '# R\n\n## Commands\n\n```\ntypecheck: `true`\n```\n')
        first = self.run_tool('--close', 'boot.1', cwd=nested)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        (nested / 'References.md').write_text(
            '# R\n\n## Commands\n\n```\ntypecheck: `test -f valid.txt`\n```\n')
        valid = nested / 'valid.txt'; valid.write_text('valid')
        second = self.run_tool('--close', 'boot.2', cwd=nested)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        valid.unlink()
        verified = self.run_tool('--list', '--verify', cwd=nested)
        self.assertEqual(verified.returncode, 1, verified.stdout + verified.stderr)
        self.assertRegex(verified.stdout, r'(?m)^closed\s+boot\.1\s')
        self.assertRegex(verified.stdout, r'(?m)^reopened\s+boot\.2\s')
        self.assertIn("the project's typecheck command failed", verified.stdout)

    def test_a_skips_decision_basis_becomes_stale_when_superseded(self):
        path = self.engine / 'bootstrap' / 'BOOT.md'
        path.write_text(path.read_text().replace('Produces: nothing when it does not apply\nCheck:', 'Produces: nothing when it does not apply\nBasis: decisions required\nCheck:'))
        self.ledger(); self.decisions()
        self.run_tool('--close', 'boot.1', '--evidence', 'x')
        self.run_tool('--close', 'boot.2.1', '--evidence', 'x')
        skipped = self.run_tool('--skip', 'boot.2.2', '--reason', 'none', '--basis', 'DEC-001')
        self.assertEqual(skipped.returncode, 0, skipped.stdout)
        old = (self.project / 'DECISIONS.md').read_text()
        newer = old.replace('DEC-001', 'DEC-002').replace('Supersedes: none', 'Supersedes: DEC-001')
        (self.project / 'DECISIONS.md').write_text(old + '\n' + newer)
        result = self.run_tool('--list')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertRegex(result.stdout, r'(?m)^reopened\s+boot\.2\.2\s')

    def test_legacy_closure_is_unverified_only_when_step_now_requires_basis(self):
        self.ledger('boot')
        ledger = self.project / 'PROGRESS.md'
        with ledger.open('a') as stream:
            stream.write('- [x] boot.1 | 2026-01-01 | rev old | evidence: old\n')
        self.assertIn('Next step: boot.2.1', self.run_tool().stdout)
        path = self.engine / 'bootstrap' / 'BOOT.md'
        path.write_text(path.read_text().replace('Produces: the project folder\nCheck:', 'Produces: the project folder\nBasis: decisions required\nCheck:'))
        result = self.run_tool()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('--reopen boot.1', result.stdout)


if __name__ == '__main__':
    unittest.main()
