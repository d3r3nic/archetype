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

    def test_update_does_not_replace_unmanaged_agent_instructions(self):
        self.inject()
        (self.project / 'AGENTS.md').write_text('Unmanaged local guidance\n')
        before = {p.relative_to(self.project): p.read_bytes() for p in self.project.rglob('*') if p.is_file()}
        _, env = self.update_source()
        result = self.run_command(['bash', str(self.project / 'archetype/update.sh')], input='y\n', env=env, cwd=self.project)
        self.assertNotEqual(result.returncode, 0)
        after = {p.relative_to(self.project): p.read_bytes() for p in self.project.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

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
        (self.project / 'AGENTS.md').unlink()  # Previous product had no AGENTS entry point.
        result = self.run_command(['bash', str(Path(LEGACY_SOURCE) / 'inject.sh'), str(self.project)])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        remote, env = self.update_source()
        command = ['bash', str(self.project / 'archetype/update.sh')]
        result = self.run_command(command, input='y\n', env=env, cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((self.project / 'AGENTS.md').exists())
        result = self.run_command(command, input='y\n', env=env, cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.project / 'AGENTS.md').read_bytes(), (remote / 'AGENTS.md').read_bytes())
        self.assertEqual((self.project / 'CLAUDE.md.pre-archetype').read_bytes(), self.local['CLAUDE.md'])
        self.assertEqual((self.project / 'References.md').read_bytes(), self.local['References.md'])


if __name__ == '__main__':
    unittest.main()
