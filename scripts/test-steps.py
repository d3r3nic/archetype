#!/usr/bin/env python3
"""Exercise scripts/next-step.sh against a small engine and project built in a temporary folder."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


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
        (self.engine / 'scripts' / 'check-flag.sh').write_text(CHECK_FLAG)
        (self.engine / 'conventions' / '08-errors.md').write_text('# Errors\n')
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
        self.assertRegex(self.closed()[-1], r'^- \[-\] boot\.2\.2 \| \d{4}-\d\d-\d\d \| rev \S+ \| skipped \(allowed when: the project has no extras\): no extras on this project$')

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
        self.assertIn('not an engine script', result.stdout)
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


if __name__ == '__main__':
    unittest.main()
