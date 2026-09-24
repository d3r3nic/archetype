#!/usr/bin/env python3
"""Exercise instruction installation and updates using an isolated local Git source."""

from pathlib import Path
import os
import shlex
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

    def test_install_says_guidance_was_preserved_only_when_it_kept_a_copy(self):
        result = self.run_command(['bash', str(SOURCE / 'inject.sh'), str(self.project)])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('  copied: AGENTS.md → project root (original guidance preserved)\n', result.stdout)
        self.assertEqual((self.project / 'AGENTS.md.pre-archetype').read_bytes(), self.local['AGENTS.md'])
        fresh = self.root / 'fresh'
        fresh.mkdir()
        result = self.run_command(['bash', str(SOURCE / 'inject.sh'), str(fresh)])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('  copied: AGENTS.md → project root\n', result.stdout)
        self.assertNotIn('preserved', result.stdout)
        self.assertFalse((fresh / 'AGENTS.md.pre-archetype').exists())

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

    def commit(self, repo, message):
        for command in (['git', 'add', '-A'],
                        ['git', '-c', 'user.name=Archetype Tests', '-c', 'user.email=tests@example.invalid',
                         'commit', '-qm', message]):
            result = self.run_command(command, cwd=repo)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

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

    def test_full_clone_update_keeps_a_changed_readme(self):
        remote, env = self.update_source()
        clone = self.root / 'full-clone-readme'
        result = self.run_command(['git', 'clone', str(remote), str(clone)])
        self.assertEqual(result.returncode, 0, result.stderr)
        readme = clone / 'README.md'
        update = ['bash', str(clone / 'update.sh')]
        # No recorded revision yet: a README that differs from the incoming copy is kept.
        readme.write_text('# A product built on the framework\n')
        result = self.run_command(update, input='y\n', env=env, cwd=clone)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('KEPT: README.md', result.stdout)
        kept = sorted(clone.glob('README.md.pre-update-*'))
        self.assertEqual([p.read_text() for p in kept], ['# A product built on the framework\n'])
        self.assertEqual(readme.read_bytes(), (remote / 'README.md').read_bytes())
        # Here the engine folder is the project root, so engine paths carry no folder name.
        self.assertIn('Next: follow development/UPDATE.md', result.stdout)
        self.assertNotIn('archetype/', result.stdout)
        # The recorded revision is the baseline: a README left as the framework shipped it is
        # replaced without a copy, one this project changed is kept.
        (remote / 'README.md').write_text((remote / 'README.md').read_text() + 'A later framework line.\n')
        self.commit(remote, 'later readme')
        result = self.run_command(update, input='y\n', env=env, cwd=clone)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn('KEPT: README.md', result.stdout)
        self.assertEqual(len(sorted(clone.glob('README.md.pre-update-*'))), 1)
        readme.write_text('# The product, second edition\n')
        (remote / 'README.md').write_text((remote / 'README.md').read_text() + 'Another framework line.\n')
        self.commit(remote, 'another readme change')
        result = self.run_command(update, input='y\n', env=env, cwd=clone)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('KEPT: README.md', result.stdout)
        kept = sorted(clone.glob('README.md.pre-update-*'))
        self.assertEqual(len(kept), 2)
        self.assertIn('# The product, second edition\n', [p.read_text() for p in kept])
        self.assertEqual(readme.read_bytes(), (remote / 'README.md').read_bytes())
        # A README is not a rule: nothing of it goes to the additions file.
        self.assertFalse((clone / 'CLAUDE.md.additions').exists())

    def snapshot(self, folder):
        return {p.relative_to(folder): p.read_bytes() for p in folder.rglob('*') if p.is_file()}

    def git_shim(self, match, really_fail):
        """A git that fails whenever its arguments include `match`: after doing the real work,
        or instead of it. Every other call goes to the real git."""
        shim = Path(tempfile.mkdtemp(prefix='shim-', dir=self.root))
        real = shutil.which('git')
        work = 'echo "simulated failure" >&2' if really_fail else '"%s" "$@"' % real
        (shim / 'git').write_text('#!/bin/sh\nfor arg in "$@"; do\n  if [ "$arg" = "%s" ]; then\n    %s\n    exit 1\n'
                                  '  fi\ndone\nexec "%s" "$@"\n' % (match, work, real))
        (shim / 'git').chmod(0o755)
        return shim

    def test_full_clone_update_stops_on_files_the_framework_never_shipped_as_they_are(self):
        remote, env = self.update_source()
        (remote / 'scripts/retired-pristine.sh').write_text('#!/bin/bash\necho framework\n')
        (remote / 'scripts/retired-edited.sh').write_text('#!/bin/bash\necho framework\n')
        self.commit(remote, 'helpers the framework later retires')
        clone = self.root / 'full-clone-ownership'
        result = self.run_command(['git', 'clone', str(remote), str(clone)])
        self.assertEqual(result.returncode, 0, result.stderr)
        # The next framework revision retires both helpers and starts shipping a new gate.
        for name in ('retired-pristine.sh', 'retired-edited.sh'):
            (remote / 'scripts' / name).unlink()
        (remote / 'scripts/new-gate.py').write_text('# the framework gate\n')
        self.commit(remote, 'retire the helpers, ship a gate')
        # No recorded revision: the rule reads the framework's history instead.
        (clone / 'scripts/new-gate.py').write_text('# the project gate\n')
        tree = clone / 'templates/feature-tree.md'
        tree.write_text(tree.read_text() + 'A project edit.\n')
        (clone / 'scripts/retired-edited.sh').write_text('#!/bin/bash\necho project edit\n')
        (clone / 'scripts/deploy.sh').write_text('#!/bin/bash\necho deploy\n')
        (clone / 'scripts/deploy-link').symlink_to('deploy.sh')
        conventions_index = clone / 'Conventions.md'
        framework_index = conventions_index.read_bytes()
        conventions_index.write_text(conventions_index.read_text() + 'A project edit.\n')
        override = clone / 'conventions/overrides/02-git.md'
        override.parent.mkdir(exist_ok=True)
        override.write_text('A justified local choice\n')
        (clone / 'scripts/.DS_Store').write_bytes(b'\0')
        (clone / 'scripts/__pycache__').mkdir()
        (clone / 'scripts/__pycache__/helper.cpython-39.pyc').write_bytes(b'\0')
        update = ['bash', str(clone / 'update.sh')]
        before = self.snapshot(clone)
        result = self.run_command(update, input='y\n', env=env, cwd=clone)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        shipped_here = ' (differs from every version the framework shipped at this path)\n'
        never = ' (the framework never shipped this path)\n'
        for line in ('  scripts/new-gate.py' + shipped_here, '  templates/feature-tree.md' + shipped_here,
                     '  scripts/retired-edited.sh' + shipped_here, '  Conventions.md' + shipped_here,
                     '  scripts/deploy.sh' + never, '  scripts/deploy-link' + never):
            self.assertIn(line, result.stdout)
        for name in ('retired-pristine.sh', '02-git.md', '.DS_Store', '__pycache__'):
            self.assertNotIn(name, result.stdout)
        self.assertEqual(self.snapshot(clone), before)
        # Put right as the message says: project files out, edits undone or deleted.
        (clone / 'scripts/new-gate.py').rename(clone / 'project-gate.py')
        (clone / 'scripts/deploy.sh').rename(clone / 'deploy.sh')
        (clone / 'scripts/deploy-link').unlink()
        tree.unlink()
        (clone / 'scripts/retired-edited.sh').unlink()
        conventions_index.write_bytes(framework_index)
        result = self.run_command(update, input='y\n', env=env, cwd=clone)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((clone / 'scripts/retired-pristine.sh').exists())
        self.assertEqual((clone / 'scripts/new-gate.py').read_text(), '# the framework gate\n')
        self.assertEqual(tree.read_bytes(), (remote / 'templates/feature-tree.md').read_bytes())
        self.assertEqual(override.read_text(), 'A justified local choice\n')
        self.assertEqual((clone / 'project-gate.py').read_text(), '# the project gate\n')
        self.assertEqual((clone / 'deploy.sh').read_text(), '#!/bin/bash\necho deploy\n')

    def test_full_clone_update_hashes_bytes_without_any_git_filter(self):
        remote, env = self.update_source()
        clone = self.root / 'full-clone-filters'
        result = self.run_command(['git', 'clone', str(remote), str(clone)])
        self.assertEqual(result.returncode, 0, result.stderr)
        # The project's git drops a LOCAL-ONLY line when it cleans a file, the user's global
        # git configuration drops a GLOBAL-ONLY line, and each filter leaves a canary when it runs.
        canaries = {name: self.root / (name + '-filter-ran') for name in ('local', 'global')}

        def clean(name, marker):
            return 'sh -c ' + shlex.quote('touch ' + shlex.quote(str(canaries[name])) + '; grep -v ' + marker)

        global_config = self.root / 'global-gitconfig'
        global_attributes = self.root / 'global-attributes'
        global_attributes.write_text('*.md filter=global\n')
        (clone / '.gitattributes').write_text('feature-tree.md filter=local\n')
        for command in (['git', '-C', str(clone), 'config', 'filter.local.clean', clean('local', 'LOCAL-ONLY')],
                        ['git', 'config', '--file', str(global_config), 'core.attributesFile', str(global_attributes)],
                        ['git', 'config', '--file', str(global_config), 'filter.global.clean', clean('global', 'GLOBAL-ONLY')]):
            result = self.run_command(command)
            self.assertEqual(result.returncode, 0, result.stderr)
        env = dict(env, GIT_CONFIG_GLOBAL=str(global_config))
        tree = clone / 'templates/feature-tree.md'
        guide = clone / 'templates/progress.md'
        debt = clone / 'templates/technical-debt.md'
        task = clone / 'templates/task-context.md'
        framework = {path: path.read_bytes() for path in (tree, guide, debt, task)}
        tree.write_text(tree.read_text() + 'LOCAL-ONLY: a project edit the project filter hides\n')
        guide.write_text(guide.read_text() + 'GLOBAL-ONLY: a project edit the global filter hides\n')
        # Each filter would hide its edit from a plain hash-object, the global one even in another
        # repository (given the physical path, as the updater gives it).
        for path, where in ((tree, clone), (guide, remote)):
            name = str(path.relative_to(clone))
            shipped = self.run_command(['git', '-C', str(clone), 'rev-parse', 'HEAD:' + name]).stdout
            hidden = self.run_command(['git', '-C', str(where), 'hash-object', '--stdin-paths'],
                                      input=str(path.resolve()) + '\n', env=env).stdout
            self.assertEqual(hidden, shipped, name + ' is not hidden by its filter')
        for canary in canaries.values():
            canary.unlink()
        # Line endings converted by a checkout pass; a carriage return anywhere else does not.
        crlf = clone / 'templates/pulse-monitor-spec.md'
        crlf.write_bytes(crlf.read_bytes().replace(b'\n', b'\r\n'))
        debt.write_bytes(framework[debt][:12] + b'\r' + framework[debt][12:])
        task.write_bytes(framework[task] + b'\r')
        update = ['bash', str(clone / 'update.sh')]
        before = self.snapshot(clone)
        result = self.run_command(update, input='y\n', env=env, cwd=clone)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for path in (tree, guide, debt, task):
            self.assertIn('  ' + str(path.relative_to(clone)) +
                          ' (differs from every version the framework shipped at this path)\n', result.stdout)
        self.assertNotIn('pulse-monitor-spec.md', result.stdout)
        for name, canary in canaries.items():
            self.assertFalse(canary.exists(), 'the ' + name + ' filter ran')
        self.assertEqual(self.snapshot(clone), before)
        for path, content in framework.items():
            path.write_bytes(content)
        result = self.run_command(update, input='y\n', env=env, cwd=clone)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name, canary in canaries.items():
            self.assertFalse(canary.exists(), 'the ' + name + ' filter ran')
        self.assertEqual(crlf.read_bytes(), (remote / 'templates/pulse-monitor-spec.md').read_bytes())

    def test_full_clone_update_knows_files_from_every_framework_branch(self):
        remote, env = self.update_source()
        self.run_command(['git', '-C', str(remote), 'checkout', '-qb', 'release'])
        (remote / 'scripts/release-helper.sh').write_text('#!/bin/bash\necho release\n')
        self.commit(remote, 'a helper only the release branch ships')
        clone = self.root / 'full-clone-branch'
        result = self.run_command(['git', 'clone', '-b', 'release', str(remote), str(clone)])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.run_command(['git', '-C', str(remote), 'checkout', '-q', 'main'])
        result = self.run_command(['bash', str(clone / 'update.sh')], input='y\n', env=env, cwd=clone)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((clone / 'scripts/release-helper.sh').exists())

    def test_full_clone_update_stops_when_a_history_or_inventory_step_fails(self):
        remote, env = self.update_source()
        clone = self.root / 'full-clone-failures'
        result = self.run_command(['git', 'clone', str(remote), str(clone)])
        self.assertEqual(result.returncode, 0, result.stderr)
        update = ['bash', str(clone / 'update.sh')]
        before = self.snapshot(clone)
        # A true fetch failure, then steps that do their work but report failure: the update
        # must stop on the status, never go on with what it happens to have.
        cases = (('--unshallow', True, "could not fetch the framework's history"),
                 ('+refs/heads/*:refs/remotes/origin/*', False, "could not fetch the framework's history"),
                 ('log', False, "could not read the framework's history"),
                 ('hash-object', False, "could not read every file in the framework's folders"))
        for match, really_fail, message in cases:
            with self.subTest(step=match):
                shimmed = dict(env, PATH=str(self.git_shim(match, really_fail)) + os.pathsep + env['PATH'])
                result = self.run_command(update, input='y\n', env=shimmed, cwd=clone)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn(message, result.stdout)
                self.assertIn('Nothing was changed.', result.stdout)
                self.assertEqual(self.snapshot(clone), before)

    def test_full_clone_update_stops_when_a_line_ending_read_fails(self):
        remote, env = self.update_source()
        clone = self.root / 'full-clone-tail-failure'
        result = self.run_command(['git', 'clone', str(remote), str(clone)])
        self.assertEqual(result.returncode, 0, result.stderr)
        # A pristine framework file stored with converted line endings reaches the second match,
        # which reads the file's last byte. That read does its work but reports failure: the
        # update must stop on the status, not go on with the normalised copy.
        target = clone / 'templates/feature-tree.md'
        target.write_bytes(target.read_bytes().replace(b'\n', b'\r\n'))
        shim = Path(tempfile.mkdtemp(prefix='shim-', dir=self.root))
        real = shutil.which('tail')
        (shim / 'tail').write_text('#!/bin/sh\nfor arg in "$@"; do\n  if [ "$arg" = "-c" ]; then\n'
                                   '    "%s" "$@"\n    exit 1\n  fi\ndone\nexec "%s" "$@"\n' % (real, real))
        (shim / 'tail').chmod(0o755)
        before = self.snapshot(clone)
        shimmed = dict(env, PATH=str(shim) + os.pathsep + env['PATH'])
        result = self.run_command(['bash', str(clone / 'update.sh')], input='y\n', env=shimmed, cwd=clone)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("could not read every file in the framework's folders", result.stdout)
        self.assertIn('Nothing was changed.', result.stdout)
        self.assertEqual(self.snapshot(clone), before)
        # Without the failing read the same converted file is recognised as the framework's.
        again = self.run_command(['bash', str(clone / 'update.sh')], input='n\n', env=env, cwd=clone)
        self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
        self.assertNotIn("not the framework's as it shipped them", again.stdout)
        self.assertEqual(self.snapshot(clone), before)

    @unittest.skipIf(os.geteuid() == 0, 'permissions do not stop the superuser')
    def test_full_clone_update_stops_when_a_framework_folder_cannot_be_listed(self):
        remote, env = self.update_source()
        clone = self.root / 'full-clone-unreadable'
        result = self.run_command(['git', 'clone', str(remote), str(clone)])
        self.assertEqual(result.returncode, 0, result.stderr)
        private = clone / 'scripts/private'
        private.mkdir()
        (private / 'notes.md').write_text('A project file the listing cannot see\n')
        before = self.snapshot(clone)
        private.chmod(0)
        self.addCleanup(private.chmod, 0o755)
        result = self.run_command(['bash', str(clone / 'update.sh')], input='y\n', env=env, cwd=clone)
        private.chmod(0o755)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('could not list every file in scripts/', result.stdout)
        self.assertEqual(self.snapshot(clone), before)

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
        self.assertIn('@AGENTS.md', (self.project / 'CLAUDE.md').read_text().splitlines())

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

    def test_update_keeps_a_root_file_whose_framework_lines_were_removed_or_reordered(self):
        self.inject()
        claude = self.project / 'CLAUDE.md'
        claude.write_text(''.join(line for line in claude.read_text().splitlines(True) if line.strip() != '@AGENTS.md'))
        agents = self.project / 'AGENTS.md'
        lines = agents.read_text().splitlines(True)
        first, second = [i for i, line in enumerate(lines) if line.startswith('## ')][:2]
        lines[first], lines[second] = lines[second], lines[first]
        agents.write_text(''.join(lines))
        previous = {name: (self.project / name).read_bytes() for name in ('CLAUDE.md', 'AGENTS.md')}
        _, env = self.update_source()
        result = self.run_update(env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn('CARRIED', result.stdout)
        for name in ('CLAUDE.md', 'AGENTS.md'):
            self.assertIn('KEPT: root ' + name + ' had framework lines removed, reordered or repeated', result.stdout)
        additions = (self.project / 'CLAUDE.md.additions').read_text()
        self.assertEqual(additions.count('removed or reordered'), 2)
        for name in ('CLAUDE.md', 'AGENTS.md'):
            kept = self.kept_copies(name)
            self.assertEqual(len(kept), 1)
            self.assertEqual(kept[0].read_bytes(), previous[name])
            self.assertIn(kept[0].name, additions)
        self.assertIn('@AGENTS.md', claude.read_text().splitlines())
        again = self.run_update(env)
        self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
        self.assertNotIn('KEPT: root', again.stdout)
        self.assertEqual((self.project / 'CLAUDE.md.additions').read_text(), additions)
        for name in ('CLAUDE.md', 'AGENTS.md'):
            self.assertEqual(len(self.kept_copies(name)), 1)

    def test_update_reshape_check_ignores_blank_lines_and_lines_already_carried(self):
        self.inject()
        rule = '- A project rule carried by an earlier update.'
        additions = self.project / 'CLAUDE.md.additions'
        additions.write_text(rule + '\n')
        claude = self.project / 'CLAUDE.md'
        # Blank lines are not words: a root file that differs only by them is simply replaced.
        claude.write_text(claude.read_text().replace('\n\n', '\n\n\n') + '\n')
        _, env = self.update_source()
        result = self.run_update(env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn('KEPT: root', result.stdout)
        self.assertEqual(self.kept_copies('CLAUDE.md'), [])
        self.assertEqual(additions.read_text(), rule + '\n')
        # A removed framework line beside a rule the additions file already holds: nothing is
        # carried, and the file is still kept for review of the removal.
        claude.write_text(''.join(line for line in claude.read_text().splitlines(True)
                                  if line.strip() != '@AGENTS.md') + rule + '\n')
        result = self.run_update(env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn('CARRIED', result.stdout)
        self.assertIn('KEPT: root CLAUDE.md had framework lines removed, reordered or repeated', result.stdout)
        self.assertEqual(len(self.kept_copies('CLAUDE.md')), 1)
        self.assertEqual(additions.read_text().count(rule), 1)

    def test_update_creates_a_missing_root_claude_file_that_imports_the_rules(self):
        self.inject()
        (self.project / 'CLAUDE.md').unlink()
        remote, env = self.update_source()
        result = self.run_update(env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('NEW: CLAUDE.md (project root)', result.stdout)
        claude = self.project / 'CLAUDE.md'
        self.assertTrue(claude.is_file(), result.stdout)
        self.assertEqual(claude.read_bytes(), (remote / 'CLAUDE.md').read_bytes())
        self.assertIn('@AGENTS.md', claude.read_text().splitlines())
        self.assertTrue((self.project / 'AGENTS.md').is_file())

    def test_update_removes_only_framework_copies_from_the_root_conventions_folder(self):
        result = self.run_command(['bash', str(SOURCE / 'inject.sh'), str(self.project), 'shared-rules'])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        engine = self.project / 'shared-rules'
        remote, env = self.update_source()
        for name in ('02-git.md', '03-architecture.md'):
            path = remote / 'conventions' / name
            path.write_text(path.read_text() + 'A later framework line.\n')
        self.commit(remote, 'later conventions')
        folder = self.project / 'conventions'
        (folder / 'overrides').mkdir(parents=True)
        # Copies earlier updates left: as the engine has them (one with carriage returns), and
        # as the framework ships one next. All three go; everything else stays.
        shutil.copyfile(engine / 'conventions/02-git.md', folder / '02-git.md')
        (folder / '12-testing.md').write_bytes((engine / 'conventions/12-testing.md').read_bytes().replace(b'\n', b'\r\n'))
        shutil.copyfile(remote / 'conventions/03-architecture.md', folder / '03-architecture.md')
        edited = folder / '16-documentation.md'
        edited.write_text((engine / 'conventions/16-documentation.md').read_text() + '- A project edit.\n')
        override = folder / 'overrides/02-git.md'
        override.write_text('A justified local choice\n')
        notes = folder / 'notes.md'
        notes.write_text('Project notes beside the overrides\n')
        kept = {path: path.read_bytes() for path in (edited, override, notes)}
        update = ['bash', str(engine / 'update.sh')]
        result = self.run_command(update, input='y\n', env=env, cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('REMOVE: 3 unchanged copies of framework conventions from conventions/ at the project root', result.stdout)
        self.assertIn('KEPT: conventions/16-documentation.md', result.stdout)
        self.assertEqual(sorted(p.name for p in folder.iterdir()), ['16-documentation.md', 'notes.md', 'overrides'])
        for path, content in kept.items():
            self.assertEqual(path.read_bytes(), content)
        self.assertTrue((self.project / 'CLAUDE.md.additions').is_file(), result.stdout)
        additions = (self.project / 'CLAUDE.md.additions').read_text()
        self.assertIn('- conventions/16-documentation.md', additions.splitlines())
        self.assertIn('move them to conventions/overrides/', additions)
        self.assertIn('shared-rules/conventions/', additions)
        self.assertNotIn('notes.md', result.stdout + additions)
        # Engine paths are shown under the engine folder's own name.
        self.assertIn('updated: shared-rules/conventions/', result.stdout)
        self.assertIn('Next: follow shared-rules/development/UPDATE.md', result.stdout)
        self.assertNotIn('archetype/', result.stdout)

        def snapshot():
            return {p.relative_to(self.project): p.read_bytes() for p in self.project.rglob('*')
                    if p.is_file() and p.name != 'VERSION-LOG.md'}

        # A second run changes nothing (the version log records every run).
        before = snapshot()
        again = self.run_command(update, input='y\n', env=env, cwd=self.project)
        self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
        self.assertNotIn('REMOVE:', again.stdout)
        self.assertNotIn('KEPT:', again.stdout)
        self.assertEqual(snapshot(), before)

    def test_update_keeps_the_engine_records_it_cannot_prove_are_duplicates(self):
        self.inject()
        engine = self.project / 'archetype'
        root_log = self.project / 'VERSION-LOG.md'
        older_log = '# Version Log\n\n## Updates\n\n### 2026-01-02\nCommit: 1234567\n'
        (engine / 'VERSION-LOG.md').write_text(older_log)
        source_note = 'Installed from an older framework location\n'
        (engine / 'FRAMEWORK-SOURCE.md').write_text(source_note)
        remote, env = self.update_source()
        head = self.run_command(['git', '-C', str(remote), 'rev-parse', 'HEAD']).stdout.strip()
        project_log = root_log.read_text()
        result = self.run_update(env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("KEPT: archetype/VERSION-LOG.md differs from the project's VERSION-LOG.md", result.stdout)
        self.assertIn('KEPT: archetype/FRAMEWORK-SOURCE.md is kept as a dated', result.stdout)
        for name in ('VERSION-LOG.md', 'FRAMEWORK-SOURCE.md'):
            self.assertFalse((engine / name).exists())
        log = root_log.read_text()
        self.assertTrue(log.startswith(project_log))
        self.assertIn('## Kept from archetype/VERSION-LOG.md by the framework update of', log)
        self.assertIn(''.join('    ' + line + '\n' for line in older_log.splitlines()), log)
        # The kept entries are indented, so the log's latest revision is still this update's.
        commits = [line for line in log.splitlines() if line.startswith('Commit: ')]
        self.assertEqual(commits[-1], 'Commit: ' + head)
        self.assertNotIn('Commit: 1234567', commits)
        kept = self.kept_copies('FRAMEWORK-SOURCE.md')
        self.assertEqual([p.read_text() for p in kept], [source_note])
        # Proven duplicates (carriage returns aside) leave the engine without another copy.
        (engine / 'VERSION-LOG.md').write_bytes(root_log.read_bytes().replace(b'\n', b'\r\n'))
        (engine / 'FRAMEWORK-SOURCE.md').write_text(source_note)
        again = self.run_update(env)
        self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
        self.assertIn('REMOVE: archetype/VERSION-LOG.md', again.stdout)
        self.assertIn('REMOVE: archetype/FRAMEWORK-SOURCE.md', again.stdout)
        for name in ('VERSION-LOG.md', 'FRAMEWORK-SOURCE.md'):
            self.assertFalse((engine / name).exists())
        self.assertEqual(root_log.read_text().count('## Kept from archetype/VERSION-LOG.md'), 1)
        self.assertEqual(len(self.kept_copies('FRAMEWORK-SOURCE.md')), 1)

    def test_update_stops_on_a_record_proof_that_is_not_a_regular_file(self):
        self.inject()
        source = self.project / 'archetype/FRAMEWORK-SOURCE.md'
        source.write_text('Installed from an older framework location\n')
        _, env = self.update_source()
        proof = self.project / 'FRAMEWORK-SOURCE.md'
        # A root link to the engine copy would pass as a duplicate and leave nothing once the
        # engine copy is removed; a dangling link proves nothing either.
        for target in (source, self.root / 'nowhere.md'):
            with self.subTest(target=target.name):
                proof.symlink_to(target)
                try:
                    before = self.snapshot(self.project)
                    result = self.run_update(env)
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertIn('FRAMEWORK-SOURCE.md at the project root is a symbolic link or not a regular file',
                                  result.stdout)
                    self.assertIn('Nothing was changed.', result.stdout)
                    self.assertEqual(self.snapshot(self.project), before)
                    self.assertTrue(proof.is_symlink())
                    self.assertEqual(source.read_text(), 'Installed from an older framework location\n')
                finally:
                    proof.unlink()
                    source.write_text('Installed from an older framework location\n')

    def test_update_stops_on_an_engine_record_that_is_a_symbolic_link(self):
        self.inject()
        engine = self.project / 'archetype'
        outside = self.root / 'outside-log.md'
        outside.write_text('A file outside the project\n')
        (engine / 'VERSION-LOG.md').symlink_to(outside)
        (self.project / 'VERSION-LOG.md').unlink()
        _, env = self.update_source()
        before = self.snapshot(self.project)
        command = ['bash', str(engine / 'update.sh'), '--project-root', str(self.project)]
        result = self.run_command(command, input='y\n', env=env, cwd=self.project)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('archetype/VERSION-LOG.md is a symbolic link or not a regular file', result.stdout)
        self.assertEqual(self.snapshot(self.project), before)
        self.assertEqual(outside.read_text(), 'A file outside the project\n')
        self.assertFalse((self.project / 'VERSION-LOG.md').exists())

    def test_rules_live_in_agents_and_claude_points_to_it(self):
        self.inject()
        agents = (self.project / 'AGENTS.md').read_text()
        claude = (self.project / 'CLAUDE.md').read_text()
        self.assertIn('## Find the relevant work', agents)
        self.assertIn(MARKER, claude)
        self.assertIn('AGENTS.md', claude)
        self.assertNotIn('## Find the relevant work', claude)
        self.assertIn('@AGENTS.md', claude.splitlines())

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

    @unittest.skipUnless(LEGACY_SOURCE, 'set ARCHETYPE_LEGACY_SOURCE for release-to-release verification')
    def test_previous_injected_release_keeps_project_lines_in_both_root_files(self):
        result = self.run_command(['bash', str(Path(LEGACY_SOURCE) / 'inject.sh'), str(self.project)])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        remote, env = self.update_source()
        # The old updater replaces itself last on its first run. Here the new updater sits in
        # the legacy engine, so the legacy engine's copies are the baselines it measures against.
        shutil.copyfile(remote / 'update.sh', self.project / 'archetype/update.sh')
        rules = {'CLAUDE.md': '- A project rule added to root CLAUDE.md.',
                 'AGENTS.md': '- A project rule added to root AGENTS.md.'}
        previous = {}
        for name, rule in rules.items():
            root = self.project / name
            root.write_text(root.read_text() + rule + '\n')
            previous[name] = root.read_bytes()
        earlier = 'Project-only rules from before the update\n'
        (self.project / 'CLAUDE.md.additions').write_text(earlier)
        doc = self.project / 'docs/systems/sign-in.md'
        doc.parent.mkdir(parents=True, exist_ok=True)
        doc.write_text('How sign-in works in this project\n')
        artifacts = {path: path.read_bytes() for path in (self.project / 'References.md', doc)}
        result = self.run_update(env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name in rules:
            self.assertIn('CARRIED: 1 line(s) this project added to root ' + name, result.stdout)
        again = self.run_update(env)
        self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
        self.assertNotIn('CARRIED', again.stdout)
        self.assertNotIn('KEPT: root', again.stdout)
        additions = (self.project / 'CLAUDE.md.additions').read_text()
        self.assertTrue(additions.startswith(earlier))
        for name, rule in rules.items():
            self.assertEqual(additions.count(rule), 1)
            kept = self.kept_copies(name)
            self.assertEqual(len(kept), 1)
            self.assertEqual(kept[0].read_bytes(), previous[name])
            self.assertEqual((self.project / name).read_bytes(), (remote / name).read_bytes())
        for path, content in artifacts.items():
            self.assertEqual(path.read_bytes(), content)


    @unittest.skipUnless(LEGACY_SOURCE, 'set ARCHETYPE_LEGACY_SOURCE for release-to-release verification')
    def test_previous_injected_release_prepared_as_documented_loses_nothing(self):
        result = self.run_command(['bash', str(Path(LEGACY_SOURCE) / 'inject.sh'), str(self.project)])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        engine = self.project / 'archetype'
        rules = {'CLAUDE.md': '- A project rule added to root CLAUDE.md.',
                 'AGENTS.md': '- A project rule added to root AGENTS.md.'}
        for name, rule in rules.items():
            root = self.project / name
            root.write_text(root.read_text() + rule + '\n')
        additions = self.project / 'CLAUDE.md.additions'
        additions.write_text('Project-only rules from before the update\n')
        folder = self.project / 'conventions'
        (folder / 'overrides').mkdir(parents=True)
        override = folder / 'overrides/02-git.md'
        override.write_text('A justified local choice\n')
        notes = folder / 'notes.md'
        notes.write_text('Project notes kept beside the overrides\n')
        doc = self.project / 'docs/systems/sign-in.md'
        doc.parent.mkdir(parents=True, exist_ok=True)
        doc.write_text('How sign-in works in this project\n')
        # The preparation development/UPDATE.md gives for older installs: each line only a root
        # entry file has moves into the additions file, and project files leave conventions/.
        for name in rules:
            framework_lines = set((engine / name).read_text().splitlines())
            root = self.project / name
            own = [line for line in root.read_text().splitlines() if line not in framework_lines]
            additions.write_text(additions.read_text() + ''.join(line + '\n' for line in own))
            root.write_bytes((engine / name).read_bytes())
        moved = self.project / 'docs/notes.md'
        notes.rename(moved)
        prepared = additions.read_text()
        for rule in rules.values():
            self.assertEqual(prepared.count(rule), 1)
        kept = {path: path.read_bytes() for path in (override, moved, doc, self.project / 'References.md')}
        remote, env = self.update_source()
        command = ['bash', str(engine / 'update.sh')]
        # The old updater runs first and replaces itself last.
        first = self.run_command(command, input='y\n', env=env, cwd=self.project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertEqual((engine / 'update.sh').read_bytes(), (remote / 'update.sh').read_bytes())
        self.assertTrue((folder / '02-git.md').is_file(), 'the old updater copies the conventions back')
        second = self.run_command(command, input='y\n', env=env, cwd=self.project)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertIn('REMOVE:', second.stdout)
        self.assertEqual(sorted(p.name for p in folder.iterdir()), ['overrides'])
        self.assertEqual(sorted(p.name for p in (folder / 'overrides').iterdir()), ['02-git.md'])
        for path, content in kept.items():
            self.assertEqual(path.read_bytes(), content)
        self.assertEqual(additions.read_text(), prepared)
        for name in rules:
            self.assertEqual((self.project / name).read_bytes(), (remote / name).read_bytes())


if __name__ == '__main__':
    unittest.main()
