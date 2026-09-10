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


if __name__ == '__main__':
    unittest.main()
