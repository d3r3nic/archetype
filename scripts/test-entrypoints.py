#!/usr/bin/env python3
"""Exercise instruction installation and updates using an isolated local Git source."""

from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]
MARKER = '<!-- archetype-managed-entrypoint -->'
LEGACY_SOURCE = os.environ.get('ARCHETYPE_LEGACY_SOURCE')


class Entrypoints(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='archetype-entrypoints-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / 'project'
        self.project.mkdir()
        (self.project / 'AGENTS.md').write_text('Local instructions to preserve\n')
        (self.project / 'CLAUDE.md').write_text('Existing Claude instructions\n')
        (self.project / 'References.md').write_text('Local context\n')
        self.local = {
            name: (self.project / name).read_bytes()
            for name in ('AGENTS.md', 'CLAUDE.md', 'References.md')
        }

    def run_command(self, args, **kwargs):
        return subprocess.run(args, text=True, capture_output=True, **kwargs)

    def inject(self):
        result = self.run_command(['bash', str(SOURCE / 'inject.sh'), str(self.project)])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_install_preserves_guidance_and_validates_engine(self):
        self.inject()
        self.assertIn(MARKER, (self.project / 'AGENTS.md').read_text())
        for name in ('AGENTS.md', 'CLAUDE.md'):
            self.assertEqual((self.project / (name + '.pre-archetype')).read_bytes(), self.local[name])
        self.assertEqual((self.project / 'References.md').read_bytes(), self.local['References.md'])
        result = self.run_command(['bash', str(self.project / 'archetype/scripts/validate-framework.sh')], cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_backup_collision_refuses_before_changing_anything(self):
        (self.project / 'AGENTS.md.pre-archetype').write_text('Older preserved guidance\n')
        before = {p.relative_to(self.project): p.read_bytes() for p in self.project.rglob('*') if p.is_file()}
        result = self.run_command(['bash', str(SOURCE / 'inject.sh'), str(self.project)])
        self.assertNotEqual(result.returncode, 0)
        after = {p.relative_to(self.project): p.read_bytes() for p in self.project.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_install_refuses_instruction_symlinks_without_writes(self):
        outside = self.root / 'shared-guidance.md'
        outside.write_text('Shared guidance must survive\n')
        (self.project / 'AGENTS.md').unlink()
        (self.project / 'AGENTS.md').symlink_to(outside)
        result = self.run_command(['bash', str(SOURCE / 'inject.sh'), str(self.project)])
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(outside.read_text(), 'Shared guidance must survive\n')
        self.assertTrue((self.project / 'AGENTS.md').is_symlink())
        self.assertEqual((self.project / 'CLAUDE.md').read_bytes(), self.local['CLAUDE.md'])
        self.assertFalse((self.project / 'archetype').exists())

    def test_install_refuses_backup_symlink_and_legacy_collision(self):
        (self.project / 'CLAUDE.md').rename(self.project / 'Claude.md')
        backup = self.project / 'CLAUDE.md.pre-archetype'
        backup.symlink_to(self.root / 'nonexistent-backup')
        result = self.run_command(['bash', str(SOURCE / 'inject.sh'), str(self.project)])
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(backup.is_symlink())
        self.assertFalse((self.root / 'nonexistent-backup').exists())
        self.assertFalse((self.project / 'archetype').exists())

    def test_install_refuses_subfolder_escape(self):
        result = self.run_command(['bash', str(SOURCE / 'inject.sh'), str(self.project), '../escaped'])
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / 'escaped').exists())
        self.assertEqual((self.project / 'AGENTS.md').read_bytes(), self.local['AGENTS.md'])

    def update_source(self):
        remote = self.root / 'framework-source'
        shutil.copytree(SOURCE, remote, ignore=shutil.ignore_patterns('.git'))
        (remote / 'AGENTS.md').write_text(MARKER + '\nUpdated managed entry point\n')
        (remote / 'CLAUDE.md').write_text((remote / 'CLAUDE.md').read_text() + '\nUpdated shared rule\n')
        for command in (['git', 'init', '-b', 'main'], ['git', 'add', '.'],
                        ['git', '-c', 'user.name=Archetype Tests', '-c', 'user.email=tests@example.invalid',
                         'commit', '-m', 'test: prepare local update source']):
            result = self.run_command(command, cwd=remote)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        # Rewrite only this subprocess's transport; no global configuration or network.
        env = os.environ.copy()
        count = int(env.get('GIT_CONFIG_COUNT', '0'))
        env.update({
            'GIT_CONFIG_COUNT': str(count + 1),
            f'GIT_CONFIG_KEY_{count}': f'url.{remote.as_uri()}.insteadOf',
            f'GIT_CONFIG_VALUE_{count}': 'https://github.com/d3r3nic/archetype.git',
        })
        return remote, env

    def test_update_replaces_managed_files_and_preserves_local_context(self):
        self.inject()
        (self.project / 'CLAUDE.md.additions').write_text('Project-only rules\n')
        remote, env = self.update_source()
        result = self.run_command(['bash', str(self.project / 'archetype/update.sh')], input='y\n', env=env, cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name in ('AGENTS.md', 'CLAUDE.md'):
            self.assertEqual((self.project / name).read_bytes(), (remote / name).read_bytes())
        self.assertEqual((self.project / 'References.md').read_bytes(), self.local['References.md'])
        self.assertEqual((self.project / 'CLAUDE.md.additions').read_text(), 'Project-only rules\n')

    def run_update(self, env):
        return self.run_command(['bash', str(self.project / 'archetype/update.sh')], input='y\n', env=env, cwd=self.project)

    def kept_copies(self, name):
        return sorted(self.project.glob(name + '.pre-update-*'))

    def test_update_keeps_unmanaged_agent_instructions_whole_and_proceeds(self):
        self.inject()
        (self.project / 'AGENTS.md').write_text('Unmanaged local guidance\n')
        _, env = self.update_source()
        result = self.run_update(env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('KEPT: root AGENTS.md', result.stdout)
        kept = self.kept_copies('AGENTS.md')
        self.assertEqual(len(kept), 1)
        self.assertEqual(kept[0].read_text(), 'Unmanaged local guidance\n')
        self.assertIn(MARKER, (self.project / 'AGENTS.md').read_text())
        self.assertIn(kept[0].name, (self.project / 'CLAUDE.md.additions').read_text())

    def test_update_carries_lines_the_project_added_to_the_root_rules_file(self):
        self.inject()
        rule = '- Never let a system path touch protected records unaudited.'
        root = self.project / 'CLAUDE.md'
        original = root.read_text()
        root.write_text(original + rule + '\n')
        (self.project / 'CLAUDE.md.additions').write_text('Existing local guidance\n')
        remote, env = self.update_source()
        source = remote / 'CLAUDE.md'
        source.write_text(source.read_text() + 'A later framework line.\n')
        self.run_command(['git', '-C', str(remote), 'commit', '-qam', 'later'])
        result = self.run_update(env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('CARRIED: 1 line(s)', result.stdout)
        additions = (self.project / 'CLAUDE.md.additions').read_text()
        self.assertTrue(additions.startswith('Existing local guidance\n'))
        self.assertIn(rule, additions)
        self.assertIn('audit each line', additions)
        kept = self.kept_copies('CLAUDE.md')
        self.assertEqual(len(kept), 1)
        self.assertEqual(kept[0].read_text(), original + rule + '\n')
        self.assertNotIn(rule, root.read_text())
        self.assertIn('A later framework line.', root.read_text())
        again = self.run_update(env)
        self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
        self.assertEqual((self.project / 'CLAUDE.md.additions').read_text().count(rule), 1)
        self.assertEqual(len(self.kept_copies('CLAUDE.md')), 1)
        # The same rule put back into the root file is already in the additions file:
        # nothing is carried, no empty audit block is written, no second copy is kept.
        root.write_text(root.read_text() + rule + '\n')
        before = (self.project / 'CLAUDE.md.additions').read_text()
        third = self.run_update(env)
        self.assertEqual(third.returncode, 0, third.stdout + third.stderr)
        self.assertNotIn('CARRIED', third.stdout)
        self.assertEqual((self.project / 'CLAUDE.md.additions').read_text(), before)
        self.assertEqual(len(self.kept_copies('CLAUDE.md')), 1)

    def test_update_ignores_carriage_returns_when_finding_added_lines(self):
        self.inject()
        rule = '- A project rule.'
        root = self.project / 'CLAUDE.md'
        root.write_bytes(root.read_bytes().replace(b'\n', b'\r\n') + rule.encode() + b'\r\n')
        _, env = self.update_source()
        result = self.run_update(env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('CARRIED: 1 line(s)', result.stdout)
        self.assertNotIn(MARKER, (self.project / 'CLAUDE.md.additions').read_text())

    def test_update_stops_with_nothing_replaced_when_the_carry_cannot_be_written(self):
        self.inject()
        root = self.project / 'CLAUDE.md'
        root.write_text(root.read_text() + '- A project rule.\n')
        additions = self.project / 'CLAUDE.md.additions'
        additions.write_text('Existing\n')
        additions.chmod(0o444)
        self.addCleanup(additions.chmod, 0o644)
        _, env = self.update_source()
        before = root.read_text()
        result = self.run_update(env)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(root.read_text(), before)

    def test_full_clone_update_keeps_a_changed_root_file(self):
        remote, env = self.update_source()
        clone = self.root / 'full-clone-carry'
        result = self.run_command(['git', 'clone', str(remote), str(clone)])
        self.assertEqual(result.returncode, 0, result.stderr)
        rule = '- A full-clone project rule.'
        (clone / 'CLAUDE.md').write_text((clone / 'CLAUDE.md').read_text() + rule + '\n')
        source = remote / 'CLAUDE.md'
        source.write_text(source.read_text() + 'A later framework line.\n')
        self.run_command(['git', '-C', str(remote), 'commit', '-qam', 'later'])
        result = self.run_command(['bash', str(clone / 'update.sh')], input='y\n', env=env, cwd=clone)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        kept = sorted(clone.glob('CLAUDE.md.pre-update-*'))
        self.assertEqual(len(kept), 1)
        self.assertIn(rule, kept[0].read_text())
        self.assertIn(kept[0].name, (clone / 'CLAUDE.md.additions').read_text())

    def test_update_finds_added_lines_from_the_recorded_revision_without_an_engine_copy(self):
        self.inject()
        remote, env = self.update_source()
        recorded = self.run_command(['git', '-C', str(remote), 'rev-parse', 'HEAD']).stdout.strip()
        self.assertEqual(len(recorded), 40)
        (self.project / 'VERSION-LOG.md').write_text('## Updates\n\nCommit: ' + recorded + '\n')
        rule = '- A rule with only the recorded revision as its baseline.'
        (self.project / 'CLAUDE.md').write_text((remote / 'CLAUDE.md').read_text() + rule + '\n')
        (self.project / 'archetype/CLAUDE.md').unlink()
        source = remote / 'CLAUDE.md'
        source.write_text(source.read_text() + 'A later framework line.\n')
        self.run_command(['git', '-C', str(remote), 'commit', '-qam', 'later'])
        result = self.run_update(env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('CARRIED: 1 line(s)', result.stdout)
        self.assertIn(rule, (self.project / 'CLAUDE.md.additions').read_text())

    def test_update_installs_the_pointer_and_the_rules(self):
        self.inject()
        (self.project / 'CLAUDE.md').write_text(MARKER + '\nold pointer\n')
        (self.project / 'archetype/CLAUDE.md').write_text(MARKER + '\nold pointer\n')
        remote, env = self.update_source()
        for name in ('AGENTS.md', 'CLAUDE.md'):
            (remote / name).write_bytes((SOURCE / name).read_bytes())
        self.run_command(['git', '-C', str(remote), 'commit', '-qam', 'real entry files'])
        result = self.run_update(env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('## Find the relevant work', (self.project / 'AGENTS.md').read_text())
        self.assertNotIn('## Find the relevant work', (self.project / 'CLAUDE.md').read_text())
        self.assertIn('AGENTS.md', (self.project / 'CLAUDE.md').read_text())

    def test_update_of_an_untouched_root_file_carries_nothing(self):
        self.inject()
        remote, env = self.update_source()
        source = remote / 'CLAUDE.md'
        source.write_text(source.read_text() + 'A later framework line.\n')
        self.run_command(['git', '-C', str(remote), 'commit', '-qam', 'later'])
        result = self.run_update(env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn('CARRIED', result.stdout)
        self.assertFalse((self.project / 'CLAUDE.md.additions').exists())
        self.assertEqual(self.kept_copies('CLAUDE.md'), [])

    def test_rules_live_in_agents_and_claude_points_to_it(self):
        self.inject()
        agents = (self.project / 'AGENTS.md').read_text()
        claude = (self.project / 'CLAUDE.md').read_text()
        self.assertIn('## Find the relevant work', agents)
        self.assertIn(MARKER, claude)
        self.assertIn('AGENTS.md', claude)
        self.assertNotIn('## Find the relevant work', claude)

    def test_full_clone_update_keeps_parent_unchanged(self):
        remote, env = self.update_source()
        clone = self.root / 'full-clone'
        result = self.run_command(['git', 'clone', str(remote), str(clone)])
        self.assertEqual(result.returncode, 0, result.stderr)
        (clone / 'AGENTS.md').write_text(MARKER + '\nOld managed rules\n')
        (self.root / 'CLAUDE.md').write_text('Parent-owned guidance\n')
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.iterdir() if p.is_file()}
        result = self.run_command(['bash', str(clone / 'update.sh')], input='y\n', env=env, cwd=clone)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.iterdir() if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual((clone / 'AGENTS.md').read_bytes(), (remote / 'AGENTS.md').read_bytes())
        self.assertTrue((clone / 'VERSION-LOG.md').is_file())

    def update_project(self, env):
        return self.run_command(['bash', str(self.project / 'archetype/update.sh')],
                                input='y\n', env=env, cwd=self.project)

    def full_clone(self, remote, name):
        clone = self.root / name
        result = self.run_command(['git', 'clone', str(remote), str(clone)])
        self.assertEqual(result.returncode, 0, result.stderr)
        (clone / 'AGENTS.md').write_text(MARKER + '\nOld managed rules\n')
        return clone

    def test_install_carries_license_and_notice_into_the_engine(self):
        self.inject()
        engine = self.project / 'archetype'
        for name in ('LICENSE', 'NOTICE'):
            self.assertEqual((engine / name).read_bytes(), (SOURCE / name).read_bytes())

    def test_update_installs_license_pair_when_both_are_missing(self):
        self.inject()
        engine = self.project / 'archetype'
        (engine / 'LICENSE').unlink()
        (engine / 'NOTICE').unlink()
        remote, env = self.update_source()
        result = self.update_project(env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name in ('LICENSE', 'NOTICE'):
            self.assertEqual((engine / name).read_bytes(), (remote / name).read_bytes())
        self.assertNotIn('LICENSE and NOTICE you already had', result.stdout)

    def test_update_keeps_an_owned_license_and_skips_its_pair(self):
        self.inject()
        engine = self.project / 'archetype'
        (engine / 'LICENSE').write_text('Project-owned license\n')
        (engine / 'NOTICE').unlink()
        _, env = self.update_source()
        result = self.update_project(env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((engine / 'LICENSE').read_text(), 'Project-owned license\n')
        self.assertFalse((engine / 'NOTICE').exists())
        self.assertIn('KEPT', result.stdout)
        self.assertIn('not added while the other file of the pair is present', result.stdout)
        self.assertIn('LICENSE and NOTICE you already had', result.stdout)

    def test_update_says_nothing_about_a_license_that_already_matches(self):
        self.inject()
        _, env = self.update_source()
        result = self.update_project(env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn('KEPT:', result.stdout)
        self.assertNotIn('NEW: archetype/LICENSE', result.stdout)
        self.assertNotIn('SKIPPED:', result.stdout)

    def test_update_leaves_a_non_regular_license_path_alone(self):
        self.inject()
        engine = self.project / 'archetype'
        outside = self.root / 'outside-license'
        (engine / 'LICENSE').unlink()
        (engine / 'LICENSE').symlink_to(outside)
        (engine / 'NOTICE').unlink()
        _, env = self.update_source()
        result = self.update_project(env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((engine / 'LICENSE').is_symlink())
        self.assertFalse(outside.exists())
        self.assertFalse((engine / 'NOTICE').exists())

    def test_full_clone_update_adds_nothing_when_the_license_came_with_the_clone(self):
        remote, env = self.update_source()
        clone = self.full_clone(remote, 'full-clone-licensed')
        result = self.run_command(['bash', str(clone / 'update.sh')], input='y\n', env=env, cwd=clone)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((clone / 'LICENSE').read_bytes(), (remote / 'LICENSE').read_bytes())
        self.assertFalse((clone / 'LICENSE-ARCHETYPE').exists())
        self.assertFalse((clone / 'NOTICE-ARCHETYPE').exists())

    def test_full_clone_update_never_touches_the_project_license(self):
        remote, env = self.update_source()
        clone = self.full_clone(remote, 'full-clone-owned-license')
        (clone / 'LICENSE').write_text('Project-owned license\n')
        (clone / 'NOTICE').unlink()
        result = self.run_command(['bash', str(clone / 'update.sh')], input='y\n', env=env, cwd=clone)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((clone / 'LICENSE').read_text(), 'Project-owned license\n')
        self.assertFalse((clone / 'NOTICE').exists())
        self.assertEqual((clone / 'LICENSE-ARCHETYPE').read_bytes(), (remote / 'LICENSE').read_bytes())
        self.assertEqual((clone / 'NOTICE-ARCHETYPE').read_bytes(), (remote / 'NOTICE').read_bytes())

    def test_update_refuses_symlink_before_any_project_changes(self):
        self.inject()
        outside = self.root / 'shared-guidance.md'
        outside.write_text(MARKER + '\nShared managed guidance\n')
        (self.project / 'AGENTS.md').unlink()
        (self.project / 'AGENTS.md').symlink_to(outside)
        before = {p.relative_to(self.project): p.read_bytes() for p in self.project.rglob('*') if p.is_file()}
        _, env = self.update_source()
        result = self.run_command(['bash', str(self.project / 'archetype/update.sh')], input='y\n', env=env)
        self.assertNotEqual(result.returncode, 0)
        after = {p.relative_to(self.project): p.read_bytes() for p in self.project.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
        self.assertTrue((self.project / 'AGENTS.md').is_symlink())

    def test_update_refuses_unrelated_explicit_root(self):
        self.inject()
        _, env = self.update_source()
        result = self.run_command(['bash', str(self.project / 'archetype/update.sh'),
                                   '--project-root', str(self.root)], input='y\n', env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / 'AGENTS.md').exists())

    def test_custom_engine_and_repeated_install(self):
        result = self.run_command(['bash', str(SOURCE / 'inject.sh'), str(self.project), 'shared-rules'])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        before = {p.relative_to(self.project): p.read_bytes() for p in self.project.rglob('*') if p.is_file()}
        result = self.run_command(['bash', str(SOURCE / 'inject.sh'), str(self.project), 'shared-rules'])
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(before, {p.relative_to(self.project): p.read_bytes() for p in self.project.rglob('*') if p.is_file()})
        remote, env = self.update_source()
        result = self.run_command(['bash', str(self.project / 'shared-rules/update.sh')], input='y\n', env=env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.project / 'AGENTS.md').read_bytes(), (remote / 'AGENTS.md').read_bytes())

    def test_root_migration_outputs_are_checked_in_custom_install(self):
        result = self.run_command(['bash', str(SOURCE / 'inject.sh'), str(self.project), 'shared-rules'])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        (self.project / 'feature-tree.md').write_text('# Feature Tree\n')
        (self.project / 'INDEX.md').write_text('# Local index\n' + 'Preserved source pointer\n' * 10)
        copied = self.project / 'docs/migrated/docs'
        copied.mkdir(parents=True)
        (self.project / 'docs/old.md').write_text('Original project knowledge\n')
        (copied / 'old.md').write_text('Original project knowledge\n')
        command = ['bash', str(self.project / 'shared-rules/scripts/validate-migration.sh')]
        result = self.run_command(command, cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        (copied / 'old.md').write_text('Accidentally changed knowledge\n')
        result = self.run_command(command, cwd=self.project)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('migrated doc drifted', result.stdout)

    def test_missing_task_routes_fail_self_test(self):
        engine = self.root / 'checked-engine'
        shutil.copytree(SOURCE, engine, ignore=shutil.ignore_patterns('.git'))
        for name in ('bootstrap/REPOSITORIES.md', 'development/TASKS.md',
                     'development/FRESHNESS.md', 'templates/task-context.md'):
            with self.subTest(name=name):
                content = (engine / name).read_bytes()
                (engine / name).unlink()
                result = self.run_command(['bash', str(engine / 'scripts/validate-framework.sh')])
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(name, result.stdout)
                (engine / name).write_bytes(content)

    @unittest.skipUnless(LEGACY_SOURCE, 'set ARCHETYPE_LEGACY_SOURCE for release-to-release verification')
    def test_previous_injected_release_upgrades_in_two_steps(self):
        (self.project / 'AGENTS.md').unlink()  # A previous release may have had no root AGENTS entry point.
        result = self.run_command(['bash', str(Path(LEGACY_SOURCE) / 'inject.sh'), str(self.project)])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        root_agents = self.project / 'AGENTS.md'
        legacy_root_agents = root_agents.read_bytes() if root_agents.exists() else None
        legacy_license = {name: (self.project / 'archetype' / name).exists() for name in ('LICENSE', 'NOTICE')}
        remote, env = self.update_source()
        command = ['bash', str(self.project / 'archetype/update.sh')]
        result = self.run_command(command, input='y\n', env=env, cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        # Step one only replaces the updater itself; what the new updater adds waits for step two.
        self.assertEqual((self.project / 'archetype/update.sh').read_bytes(), (remote / 'update.sh').read_bytes())
        if legacy_root_agents is None:
            self.assertFalse(root_agents.exists())
        for name in ('LICENSE', 'NOTICE'):
            if not legacy_license[name]:
                self.assertFalse((self.project / 'archetype' / name).exists())
        result = self.run_command(command, input='y\n', env=env, cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.project / 'AGENTS.md').read_bytes(), (remote / 'AGENTS.md').read_bytes())
        for name in ('LICENSE', 'NOTICE'):
            self.assertEqual((self.project / 'archetype' / name).read_bytes(), (remote / name).read_bytes())
        self.assertEqual((self.project / 'CLAUDE.md.pre-archetype').read_bytes(), self.local['CLAUDE.md'])
        self.assertEqual((self.project / 'References.md').read_bytes(), self.local['References.md'])


if __name__ == '__main__':
    unittest.main()
