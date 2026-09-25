#!/usr/bin/env python3
"""Regression tests for scripts/peer-coding.py and the Peer coding line validate-bootstrap.py reads."""
import importlib.util
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('peer_coding', str(ENGINE / 'scripts' / 'peer-coding.py'))
PEER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PEER)

REFERENCES = """# References

## Project

- Name: Garden
- Purpose: plots and a waitlist for a community garden
- Stage: development
- Owner channel: chat, same day
- Decision location: DECISIONS.md
- Reporting pace: every session
{peer}
## Commands

- test: `true`
"""
ON = '- Peer coding: peer-coding/SETTINGS.md\n'
SETTINGS = """# Peer coding settings

- Peers: claude (Claude Code), codex (Codex)
- Who writes: claude writes, codex reviews and fixes what it finds
- Checks each turn: test
- Branch names: any name except the default branch
- Push: {push}
- Merge: nothing more under PROFILE.md
- Project rules: none
"""


class Base(unittest.TestCase):
    push = 'yes'

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        home = root / 'home'
        home.mkdir()
        # Keep the machine's git configuration, identity and ignore rules out of the results.
        self.env = dict(os.environ, HOME=str(home), XDG_CONFIG_HOME=str(home / '.config'),
                        GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1',
                        GIT_AUTHOR_NAME='Tester', GIT_AUTHOR_EMAIL='tester@example.com',
                        GIT_COMMITTER_NAME='Tester', GIT_COMMITTER_EMAIL='tester@example.com')
        self.root = root / 'a folder'
        self.project = self.root / 'my project'
        self.project.mkdir(parents=True)
        self.git(self.root, 'init', '-q', '--bare', 'remote.git')
        result = subprocess.run(['bash', str(ENGINE / 'inject.sh'), str(self.project)], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, universal_newlines=True, env=self.env)
        self.assertEqual(result.returncode, 0, result.stdout)
        (self.project / 'References.md').write_text(REFERENCES.format(peer=ON))
        (self.project / 'peer-coding').mkdir()
        (self.project / 'peer-coding' / 'SETTINGS.md').write_text(SETTINGS.format(push=self.push))
        (self.project / 'app.py').write_text('print("garden")\n')
        self.git(self.project, 'init', '-q', '-b', 'main')
        self.git(self.project, 'add', '-A')
        self.git(self.project, 'commit', '-q', '-m', 'init')
        self.git(self.project, 'remote', 'add', 'origin', str(self.root / 'remote.git'))
        self.git(self.project, 'push', '-q', '-u', 'origin', 'main')
        self.git(self.project, 'remote', 'set-head', 'origin', 'main')

    def git(self, where, *args, check=True):
        result = subprocess.run(['git', '-C', str(where)] + list(args), stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, universal_newlines=True, env=self.env)
        if check:
            self.assertEqual(result.returncode, 0, 'git %s: %s' % (' '.join(args), result.stderr))
        return result.stdout.strip()

    def pc(self, where, *args):
        return subprocess.run(['python3', str(where / 'archetype' / 'scripts' / 'peer-coding.py')] + list(args),
                              cwd=str(where), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              universal_newlines=True, env=self.env)

    def worktree(self, branch, base='main'):
        path = self.root / ('wt ' + branch.replace('/', '-'))
        self.git(self.project, 'worktree', 'add', '-q', str(path), '-b', branch, base)
        return path

    def commit(self, where, message, *paths):
        self.git(where, 'add', '--', *(paths or ('.',)))
        self.git(where, 'commit', '-q', '-m', message, '--', *(paths or ('.',)))
        return self.git(where, 'rev-parse', 'HEAD')

    def folder(self, where, branch):
        return where / 'peer-coding' / re.sub(r'[^A-Za-z0-9._-]', '-', branch.replace('/', '-'))

    def edit(self, path, pattern, replacement):
        text = path.read_text()
        new, count = re.subn(pattern, replacement, text, count=1, flags=re.M)
        self.assertEqual(count, 1, 'no match for %s in %s' % (pattern, path))
        path.write_text(new)

    def confirm(self, where, branch, holder='claude', receiver='codex', writer='claude'):
        folder = self.folder(where, branch)
        self.edit(folder / 'ALIGNMENT.md', r'^Status: .*$', 'Status: CONFIRMED')
        self.edit(folder / 'ALIGNMENT.md', r'^Context holder: .*$', 'Context holder: %s · Receiver: %s' % (holder, receiver))
        self.edit(folder / 'ALIGNMENT.md', r'^Receiver verdict: .*$', 'Receiver verdict: CONFIRMED by %s after checking every claim.' % receiver)
        self.edit(folder / 'CURRENT.md', r'^- \*\*Alignment:\*\*.*$', '- **Alignment:** CONFIRMED, see [ALIGNMENT.md](ALIGNMENT.md).')
        self.edit(folder / 'CURRENT.md', r'^- \*\*Product writing turn:\*\*.*$', '- **Product writing turn:** %s' % writer)
        return folder

    def set_head(self, folder, branch, commit):
        self.edit(folder / 'CURRENT.md', r'^\| `%s` \| [^|]* \|' % re.escape(branch), '| `%s` | %s |' % (branch, commit))

    def started(self, branch='feature/plots', you='claude'):
        where = self.worktree(branch)
        result = self.pc(where, 'start', '--as', you)
        self.assertEqual(result.returncode, 0, result.stdout)
        return where, self.folder(where, branch)


class PeerLine(unittest.TestCase):
    def test_the_peers_line_is_read_as_two_short_names(self):
        self.assertEqual(PEER.parse_peers('claude (Claude Code), codex (Codex)'), ['claude', 'codex'])
        self.assertEqual(PEER.parse_peers('Claude and Codex'), ['claude', 'codex'])
        self.assertEqual(PEER.parse_peers('`claude` (a tool with, commas and words), codex'), ['claude', 'codex'])
        for bad in ('', 'none', '[the two AI assistants]', 'claude', 'claude, claude', 'claude, codex, third',
                    'claude writes, codex reviews', 'x--done, codex', 'none, codex'):
            with self.assertRaises(ValueError, msg=bad):
                PEER.parse_peers(bad)

    def test_folder_names_carry_the_same_short_code_as_the_shell_tools(self):
        for branch in ('feature-a/b', 'fix/über-long name'):
            shell = subprocess.run(['sh', '-c', 'printf "%s" "$1" | shasum | cut -c1-6', 'sh', branch],
                                   stdout=subprocess.PIPE, universal_newlines=True).stdout.strip()
            if not shell:
                self.skipTest('shasum is not available')
            self.assertEqual(PEER.short_hash(branch), shell)


class Setup(Base):
    def test_setup_creates_a_settings_file_to_fill_and_start_waits_for_it(self):
        where = self.worktree('feature/plots')
        (where / 'peer-coding' / 'SETTINGS.md').unlink()
        result = self.pc(where, 'start', '--as', 'claude')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('peer coding is not set up in this repository', result.stdout)
        result = self.pc(where, 'setup')
        self.assertEqual(result.returncode, 0, result.stdout)
        text = (where / 'peer-coding' / 'SETTINGS.md').read_text()
        self.assertIn('[development/PEER-CODING.md](../archetype/development/PEER-CODING.md)', text)
        self.assertNotIn('{{', text)
        for key in PEER.SETTINGS_KEYS:
            self.assertIn('- %s: [' % key, text)
        again = self.pc(where, 'setup')
        self.assertEqual(again.returncode, 1, again.stdout)
        self.assertIn('already exists: the Peers line is not filled in', again.stdout)
        self.assertIn('the Peers line is not filled in', self.pc(where, 'start', '--as', 'claude').stdout)
        (where / 'peer-coding' / 'SETTINGS.md').write_text(
            SETTINGS.format(push='yes').replace('- Merge: nothing more under PROFILE.md\n', '- Merge: [what]\n'))
        result = self.pc(where, 'start', '--as', 'claude')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('fill in: Merge', result.stdout)
        (where / 'peer-coding' / 'SETTINGS.md').write_text(SETTINGS.format(push='yes'))
        self.assertEqual(self.pc(where, 'setup').returncode, 0)
        self.assertIn('not one of the peers', self.pc(where, 'start', '--as', 'gemini').stdout)
        self.assertEqual(self.pc(where, 'start', '--as', 'claude').returncode, 0)

    def test_setup_refuses_a_settings_file_the_repository_would_ignore(self):
        where = self.worktree('feature/plots')
        (where / 'peer-coding' / 'SETTINGS.md').unlink()
        (where / '.gitignore').write_text('*.md\n!References.md\n')
        result = self.pc(where, 'setup')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("excluded by the repository's ignore rules (.gitignore:1:", result.stdout)


class Start(Base):
    def test_start_refuses_the_default_branch(self):
        result = self.pc(self.project, 'start', '--as', 'claude')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('main is the default branch', result.stdout)

    def test_start_opens_the_branch_folder_once(self):
        where, folder = self.started('feature/plots')
        self.assertEqual(folder.name, 'feature-plots')
        current = (folder / 'CURRENT.md').read_text()
        self.assertIn('Branch `feature/plots`', current)
        self.assertIn('| `feature/plots` | %s |' % self.git(where, 'rev-parse', 'HEAD'), current)
        self.assertIn('[development/PEER-CODING.md](../../archetype/development/PEER-CODING.md)', current)
        logged = re.findall(r'^Commit: ([0-9a-f]+)', (where / 'VERSION-LOG.md').read_text(), re.M)
        self.assertIn('(framework revision %s)' % logged[-1][:12], current)
        self.assertIn('claude writes, codex reviews and fixes what it finds', current)
        self.assertIn('Context holder: <claude | codex> · Receiver: <claude | codex>', (folder / 'ALIGNMENT.md').read_text())
        self.assertNotIn('{{', current + (folder / 'ALIGNMENT.md').read_text() + (folder / 'FINDINGS.md').read_text())
        self.assertEqual(self.pc(where, 'which').stdout.strip(), 'peer-coding/feature-plots active')
        again = self.pc(where, 'start', '--as', 'codex')
        self.assertEqual(again.returncode, 3, again.stdout)
        self.assertIn('already open', again.stdout)
        check = self.pc(where, 'check', '--as', 'claude')
        self.assertEqual(check.returncode, 0, check.stdout)
        self.assertIn('alignment not started, next move: claude', check.stdout)

    def test_start_refuses_closed_folders_and_done_branch_names(self):
        where = self.worktree('feature/plots')
        closed = where / 'peer-coding' / 'feature-plots--done'
        closed.mkdir(parents=True)
        (closed / 'CURRENT.md').write_text('# closed\n\nBranch `feature/plots` · opened 2026-01-01 by claude.\n')
        self.assertEqual(self.pc(where, 'which').stdout.strip(), 'peer-coding/feature-plots--done done')
        result = self.pc(where, 'start', '--as', 'claude')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('is closed; new work gets a new branch', result.stdout)
        other = self.worktree('try--done')
        result = self.pc(other, 'start', '--as', 'claude')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('ends in --done', result.stdout)

    def test_a_merged_branch_name_used_again_is_refused_from_the_default_branch_record(self):
        where, folder = self.started('feature/plots')
        self.commit(where, 'open', 'peer-coding')
        old_base = self.git(self.project, 'rev-parse', 'main')
        self.git(where, 'mv', 'peer-coding/feature-plots', 'peer-coding/feature-plots--done')
        self.commit(where, 'close', 'peer-coding')
        self.git(self.project, 'merge', '-q', '--no-ff', '-m', 'merge', 'feature/plots')
        self.git(self.project, 'push', '-q')
        self.git(self.project, 'worktree', 'remove', '--force', str(where))
        self.git(self.project, 'branch', '-q', '-D', 'feature/plots')
        again = self.root / 'again'
        self.git(self.project, 'worktree', 'add', '-q', str(again), '-b', 'feature/plots', old_base)
        result = self.pc(again, 'start', '--as', 'claude')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('is closed on main: this branch name was used for work that merged', result.stdout)
        self.assertIn('is on main: this branch already merged', self.pc(again, 'check').stdout)

    def test_start_refuses_a_record_the_repository_would_ignore(self):
        where = self.worktree('feature/plots')
        for rule in ('peer-coding/*/\n', '*.txt\n', '*--done/\n'):
            (where / '.gitignore').write_text(rule)
            result = self.pc(where, 'start', '--as', 'claude')
            self.assertEqual(result.returncode, 1, rule + result.stdout)
            self.assertIn("excluded by the repository's ignore rules (.gitignore:1:", result.stdout)
            self.assertFalse(self.folder(where, 'feature/plots').exists(), rule)

    def test_branch_names_that_give_one_folder_name_get_a_short_code(self):
        where, folder = self.started('feature/a-b')
        self.commit(where, 'open peer-coding folder', 'peer-coding')
        self.git(where, 'branch', 'feature-a/b')
        self.git(where, 'checkout', '-q', 'feature-a/b')
        result = self.pc(where, 'start', '--as', 'claude')
        self.assertEqual(result.returncode, 0, result.stdout)
        coded = 'feature-a-b-' + PEER.short_hash('feature-a/b')
        self.assertIn('Created peer-coding/%s for branch feature-a/b' % coded, result.stdout)
        self.assertEqual(self.pc(where, 'which').stdout.strip(), 'peer-coding/%s active' % coded)
        check = self.pc(where, 'check')
        self.assertEqual(check.returncode, 0, check.stdout)
        # Two branches that exist before either opens a folder both get a code.
        self.git(self.project, 'branch', 'x/y')
        self.git(self.project, 'branch', 'x-y')
        first = self.root / 'first'
        self.git(self.project, 'worktree', 'add', '-q', str(first), 'x/y')
        self.assertEqual(self.pc(first, 'which').stdout.strip(), 'peer-coding/x-y-%s none' % PEER.short_hash('x/y'))

    def test_the_script_of_another_checkout_reads_this_branch(self):
        where = self.worktree('feature/plots')
        (where / 'peer-coding' / 'SETTINGS.md').write_text(
            SETTINGS.format(push='yes').replace('claude (Claude Code), codex (Codex)', 'alpha (tool one), beta (tool two)'))
        result = subprocess.run(['python3', str(self.project / 'archetype' / 'scripts' / 'peer-coding.py'), 'start', '--as', 'alpha'],
                                cwd=str(where), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, env=self.env)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue((self.folder(where, 'feature/plots') / 'CURRENT.md').is_file())
        self.assertFalse(self.folder(self.project, 'feature/plots').exists())


class Check(Base):
    def test_no_writing_turn_before_alignment_is_confirmed(self):
        where, folder = self.started()
        self.edit(folder / 'CURRENT.md', r'^- \*\*Product writing turn:\*\*.*$', '- **Product writing turn:** codex')
        result = self.pc(where, 'check')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('gives codex the writing turn before ALIGNMENT.md is CONFIRMED', result.stdout)
        self.edit(folder / 'ALIGNMENT.md', r'^Status: .*$', 'Status: BRIEFED')
        self.edit(folder / 'ALIGNMENT.md', r'^Context holder: .*$', 'Context holder: claude · Receiver: claude')
        self.assertIn('the same assistant as holder and receiver', self.pc(where, 'check').stdout)
        self.confirm(where, 'feature/plots')
        result = self.pc(where, 'check')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('alignment CONFIRMED, writing turn: claude', result.stdout)

    def test_product_changes_must_be_committed_and_recorded(self):
        where, folder = self.started()
        self.confirm(where, 'feature/plots')
        (where / 'app.py').write_text('print("plots")\n')
        result = self.pc(where, 'check')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('uncommitted product changes in this worktree: app.py', result.stdout)
        product = self.commit(where, 'plots', 'app.py')
        result = self.pc(where, 'check')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('product files changed after the recorded last product commit', result.stdout)
        self.set_head(folder, 'feature/plots', product)
        result = self.pc(where, 'check')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.set_head(folder, 'feature/plots', '0' * 40)
        self.assertIn('does not exist here', self.pc(where, 'check').stdout)

    def test_links_stay_inside_the_repository_and_out_of_other_open_folders(self):
        other, other_folder = self.started('feature/other')
        self.commit(other, 'open other', 'peer-coding')
        self.git(self.project, 'merge', '-q', '--no-ff', '-m', 'merge other', 'feature/other')
        where = self.worktree('feature/plots')
        self.assertEqual(self.pc(where, 'start', '--as', 'claude').returncode, 0)
        folder = self.folder(where, 'feature/plots')
        (where / 'peer-coding' / 'old--done').mkdir()
        (where / 'peer-coding' / 'old--done' / 'ALIGNMENT.md').write_text('# Old\n')
        with open(folder / 'FINDINGS.md', 'a') as notes:
            notes.write('\nSee [gone](nothing.md), [abs](/etc/hosts), [up](../../../outside.md), '
                        '[theirs](../feature-other/CURRENT.md), [heading](ALIGNMENT.md#no-such-heading), '
                        '[line](ALIGNMENT.md:12), [fine](ALIGNMENT.md#3-verification-receiver), '
                        '[closed](../old--done/ALIGNMENT.md), [web](https://example.com/x), `[code](not-a-link.md)`.\n')
        result = self.pc(where, 'check')
        self.assertEqual(result.returncode, 1, result.stdout)
        for expected in ('link nothing.md points to nothing', 'link /etc/hosts uses an absolute path',
                         'link ../../../outside.md leaves the repository',
                         'link ../feature-other/CURRENT.md points into the open folder of another branch',
                         'link ALIGNMENT.md#no-such-heading names a heading that does not exist',
                         'link ALIGNMENT.md:12 points to nothing (check the spelling and letter case; a line number belongs after the link'):
            self.assertIn(expected, result.stdout)
        for quiet in ('3-verification-receiver', 'old--done/ALIGNMENT', 'example.com', 'not-a-link'):
            self.assertNotIn(quiet, result.stdout)

    def test_evidence_the_repository_ignores_fails(self):
        where, folder = self.started()
        (where / '.gitignore').write_text('*.log\n')
        self.commit(where, 'ignore logs', '.gitignore')
        self.set_head(folder, 'feature/plots', self.git(where, 'rev-parse', 'HEAD'))
        self.confirm(where, 'feature/plots')
        evidence = folder / 'rounds' / 'R1' / 'evidence' / 'claude'
        evidence.mkdir(parents=True)
        (evidence / 'tests.log').write_text('ok\n')
        (evidence / 'tests.txt').write_text('ok\n')
        result = self.pc(where, 'check')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('evidence/claude/tests.log is excluded by the repository\'s ignore rules', result.stdout)
        self.assertNotIn('tests.txt is excluded', result.stdout)

    def test_an_earlier_copy_of_the_rules_is_named_for_removal(self):
        where, folder = self.started()
        (where / 'peer-coding' / 'README.md').write_text('# Peer coding\n')
        (where / 'peer-coding' / 'templates').mkdir()
        (where / 'peer-coding' / 'templates' / 'CURRENT.md').write_text(
            '# peer-coding/<branch>: current state\n\nBranch `<branch>` · opened <date> by <peer>.\n')
        result = self.pc(where, 'check')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('WARN: peer-coding/: README.md, templates hold an earlier copy of peer-coding rules', result.stdout)
        self.assertEqual(result.stdout.count('WARN'), 1, result.stdout)


class Turns(Base):
    def test_packets_follow_the_round_rule_and_link_the_incoming_one(self):
        where, folder = self.started()
        refused = self.pc(where, 'packet', '--as', 'claude')
        self.assertEqual(refused.returncode, 1, refused.stdout)
        self.assertIn('not CONFIRMED', refused.stdout)
        self.confirm(where, 'feature/plots')
        self.assertEqual(self.pc(where, 'packet', '--as', 'claude').returncode, 0)
        mine = folder / 'rounds' / 'R1' / 'claude.md'
        self.assertIn('none: the first packet of this branch', mine.read_text())
        self.assertIn('[CURRENT.md](../../CURRENT.md)', mine.read_text())
        self.assertIn('still WIP', self.pc(where, 'packet', '--as', 'claude').stdout)
        self.edit(mine, r'^Status: WIP.*\n', '')
        self.assertEqual(self.pc(where, 'packet', '--as', 'codex').returncode, 0)
        theirs = folder / 'rounds' / 'R1' / 'codex.md'
        self.assertIn('[R1/claude.md](claude.md)', theirs.read_text())
        self.edit(theirs, r'^Status: WIP.*\n', '')
        self.assertEqual(self.pc(where, 'packet', '--as', 'claude').returncode, 0)
        second = folder / 'rounds' / 'R2' / 'claude.md'
        self.assertIn('[R1/codex.md](../R1/codex.md)', second.read_text())
        self.assertIn('# peer-coding/feature-plots R2: claude to codex', second.read_text())
        check = self.pc(where, 'check')
        self.assertEqual(check.returncode, 0, check.stdout)
        self.assertIn('R2/claude.md is still WIP', check.stdout)
        (folder / 'rounds' / 'R2' / 'gemini.md').write_text('# stray\n')
        self.assertIn('is named for gemini', self.pc(where, 'check').stdout)

    def test_the_relay_line_needs_a_committed_pushed_hand_over_to_the_other(self):
        where, folder = self.started()
        self.assertIn('peer-coding/ has uncommitted changes', self.pc(where, 'cue', '--as', 'claude').stdout)
        self.edit(folder / 'ALIGNMENT.md', r'^Status: .*$', 'Status: BRIEFED')
        self.edit(folder / 'ALIGNMENT.md', r'^Context holder: .*$', 'Context holder: claude · Receiver: codex')
        self.edit(folder / 'CURRENT.md', r'^- \*\*Alignment:\*\*.*$', '- **Alignment:** BRIEFED, see [ALIGNMENT.md](ALIGNMENT.md). Next move: codex.')
        self.commit(where, 'brief', 'peer-coding')
        result = self.pc(where, 'cue', '--as', 'claude')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('the branch does not track its own remote branch: push it with git push -u <remote> feature/plots', result.stdout)
        self.git(where, 'push', '-q', '-u', 'origin', 'feature/plots')
        result = self.pc(where, 'cue', '--as', 'claude')
        self.assertEqual(result.returncode, 0, result.stdout)
        sha = self.git(where, 'rev-parse', '--short=12', 'HEAD')
        self.assertIn('READY FOR CODEX · peer-coding/feature-plots ALIGN BRIEFED · feature/plots@%s' % sha, result.stdout)
        self.assertIn('Continue peer coding on branch feature/plots (worktree: %s)' % where.resolve(), result.stdout)
        refused = self.pc(where, 'cue', '--as', 'codex')
        self.assertEqual(refused.returncode, 1, refused.stdout)
        self.assertIn('gives the next move to codex', refused.stdout)
        self.confirm(where, 'feature/plots', writer='claude')
        (where / 'app.py').write_text('print("plots")\n')
        product = self.commit(where, 'plots', 'app.py')
        self.set_head(folder, 'feature/plots', product)
        self.assertEqual(self.pc(where, 'packet', '--as', 'claude').returncode, 0)
        self.commit(where, 'R1 wip', 'peer-coding')
        self.git(where, 'push', '-q')
        self.assertIn('a packet is still WIP', self.pc(where, 'cue', '--as', 'claude').stdout)
        self.edit(folder / 'rounds' / 'R1' / 'claude.md', r'^Status: WIP.*\n', '')
        self.commit(where, 'R1', 'peer-coding')
        self.git(where, 'push', '-q')
        self.assertIn('gives the next move to claude', self.pc(where, 'cue', '--as', 'claude').stdout)
        self.edit(folder / 'CURRENT.md', r'^- \*\*Product writing turn:\*\*.*$', '- **Product writing turn:** codex')
        self.commit(where, 'hand R1 to codex', 'peer-coding')
        self.assertIn('push the branch first', self.pc(where, 'cue', '--as', 'claude').stdout)
        self.git(where, 'push', '-q')
        result = self.pc(where, 'cue', '--as', 'claude')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('READY FOR CODEX · peer-coding/feature-plots R1 · feature/plots@', result.stdout)


class NoPush(Base):
    push = 'no: both assistants work in this one repository'

    def test_a_project_that_does_not_push_hands_over_in_place(self):
        where, folder = self.started()
        self.edit(folder / 'ALIGNMENT.md', r'^Status: .*$', 'Status: BRIEFED')
        self.edit(folder / 'CURRENT.md', r'^- \*\*Alignment:\*\*.*$', '- **Alignment:** BRIEFED. Next move: codex.')
        self.commit(where, 'brief', 'peer-coding')
        result = self.pc(where, 'cue', '--as', 'claude')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('says Push: no', result.stdout)
        self.assertIn('READY FOR CODEX · peer-coding/feature-plots ALIGN BRIEFED', result.stdout)


class Close(Base):
    def reviewed(self, branch='feature/plots'):
        where, folder = self.started(branch)
        self.confirm(where, branch)
        work = where / (folder.name + '.py')
        work.write_text('print("%s")\n' % branch)
        product = self.commit(where, 'work on ' + branch, work.name)
        self.set_head(folder, branch, product)
        self.commit(where, 'hand over', 'peer-coding')
        return where, folder, product

    def accept(self, where, folder, commit, note='by codex, R1'):
        self.edit(folder / 'CURRENT.md', r'^- \*\*Accepted head:\*\*.*$', '- **Accepted head:** %s %s' % (commit, note))
        self.commit(where, 'accepted', 'peer-coding')

    def test_close_needs_acceptance_of_the_last_product_change(self):
        where, folder, product = self.reviewed()
        refused = self.pc(where, 'close', '--as', 'claude', '--merged', 'PR 7')
        self.assertEqual(refused.returncode, 1, refused.stdout)
        self.assertIn('records no accepted head', refused.stdout)
        self.accept(where, folder, product[:12])
        (where / 'feature-plots.py').write_text('print("later")\n')
        later = self.commit(where, 'unreviewed change', 'feature-plots.py')
        self.set_head(folder, 'feature/plots', later)
        self.commit(where, 'record later head', 'peer-coding')
        refused = self.pc(where, 'close', '--as', 'claude', '--merged', 'PR 7')
        self.assertEqual(refused.returncode, 1, refused.stdout)
        self.assertIn('product files changed after the accepted head', refused.stdout)
        self.accept(where, folder, later, 'by codex, R2')
        closed = self.pc(where, 'close', '--as', 'claude', '--merged', 'PR 7')
        self.assertEqual(closed.returncode, 0, closed.stdout)
        text = (folder.parent / 'feature-plots--done' / 'CURRENT.md').read_text()
        self.assertRegex(text, r'- \*\*Status:\*\* DONE, closed for merge via PR 7 \(\d{4}-\d\d-\d\d, claude\)')
        self.assertNotIn('merged via', text)

    def test_close_refuses_open_findings_wip_packets_and_uncommitted_changes(self):
        where, folder, product = self.reviewed()
        self.edit(folder / 'CURRENT.md', r'^- \*\*Accepted head:\*\*.*$', '- **Accepted head:** %s by codex' % product)
        self.assertIn('has uncommitted changes', self.pc(where, 'close', '--as', 'claude', '--merged', '12').stdout)
        with open(folder / 'FINDINGS.md', 'a') as findings:
            findings.write('| F1 | medium | the waitlist order resets | codex | R1 |\n')
        self.commit(where, 'finding', 'peer-coding')
        self.assertIn('still lists 1 unresolved item', self.pc(where, 'close', '--as', 'claude', '--merged', '12').stdout)
        self.edit(folder / 'FINDINGS.md', r'^\| F1 .*\n', '')
        self.assertEqual(self.pc(where, 'packet', '--as', 'codex').returncode, 0)
        self.commit(where, 'wip packet', 'peer-coding')
        self.assertIn('a packet is still WIP', self.pc(where, 'close', '--as', 'claude', '--merged', '12').stdout)
        self.assertTrue(folder.is_dir())

    def test_a_close_whose_merge_did_not_happen_reopens_and_a_merged_one_does_not(self):
        where, folder, product = self.reviewed()
        self.accept(where, folder, product)
        self.assertEqual(self.pc(where, 'close', '--as', 'codex', '--merged', 'PR 9').returncode, 0)
        self.git(where, 'commit', '-q', '-m', 'close', '--', 'peer-coding')
        reopened = self.pc(where, 'close', '--as', 'codex', '--reopen', 'a check failed after the close')
        self.assertEqual(reopened.returncode, 0, reopened.stdout)
        text = (folder / 'CURRENT.md').read_text()
        self.assertRegex(text, r'- \*\*Status:\*\* ACTIVE \(reopened \d{4}-\d\d-\d\d by codex: a check failed after the close\)')
        self.assertIn('- **Product writing turn:** none until the assistants agree who continues', text)
        self.git(where, 'commit', '-q', '-m', 'reopen', '--', 'peer-coding')
        check = self.pc(where, 'check')
        self.assertEqual(check.returncode, 0, check.stdout)
        self.assertEqual(self.pc(where, 'close', '--as', 'codex', '--merged', 'PR 9').returncode, 0)
        self.git(where, 'commit', '-q', '-m', 'close again', '--', 'peer-coding')
        self.git(self.project, 'merge', '-q', '--no-ff', '-m', 'merge', 'feature/plots')
        refused = self.pc(where, 'close', '--as', 'codex', '--reopen', 'more work')
        self.assertEqual(refused.returncode, 1, refused.stdout)
        self.assertIn('is already merged into main', refused.stdout)

    def test_a_full_cycle_closes_as_done_and_parallel_branches_merge_cleanly(self):
        closed_folders = []
        for branch in ('feature/plots', 'fix/waitlist'):
            where, folder, product = self.reviewed(branch)
            self.accept(where, folder, product)
            result = self.pc(where, 'close', '--as', 'codex', '--merged', 'PR %s' % branch)
            self.assertEqual(result.returncode, 0, result.stdout)
            done = folder.parent / (folder.name + '--done')
            self.assertFalse(folder.exists())
            self.assertIn('- **Product writing turn:** none (closed)', (done / 'CURRENT.md').read_text())
            self.git(where, 'add', '--', 'peer-coding')
            self.git(where, 'commit', '-q', '-m', 'close', '--', 'peer-coding')
            self.assertEqual(self.git(where, 'status', '--porcelain'), '')
            after = self.pc(where, 'check')
            self.assertEqual(after.returncode, 0, after.stdout)
            self.assertIn('is closed: its branch finished', after.stdout)
            self.assertIn('is closed; new work gets a new branch', self.pc(where, 'start', '--as', 'claude').stdout)
            closed_folders.append(done.name)
        for branch in ('feature/plots', 'fix/waitlist'):
            merge = subprocess.run(['git', '-C', str(self.project), 'merge', '--no-ff', '-q', '-m', 'merge ' + branch, branch],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, env=self.env)
            self.assertEqual(merge.returncode, 0, merge.stdout)
        on_main = sorted(p.name for p in (self.project / 'peer-coding').iterdir())
        self.assertEqual(on_main, sorted(closed_folders + ['SETTINGS.md']))
        check = self.pc(self.project, 'check')
        self.assertEqual(check.returncode, 0, check.stdout)
        self.assertNotIn('WARN', check.stdout)

    def test_a_folder_left_open_after_its_merge_is_reported_and_closed_from_the_next_branch(self):
        where, folder, product = self.reviewed('feature/plots')
        self.git(self.project, 'merge', '-q', '--no-ff', '-m', 'merge without closing', 'feature/plots')
        nxt = self.worktree('feature/next')
        check = self.pc(nxt, 'check')
        self.assertIn('WARN: peer-coding/feature-plots: its branch feature/plots is merged into main but the folder is still open', check.stdout)
        closed = self.pc(nxt, 'close', '--as', 'claude', '--folder', 'feature-plots', '--merged', 'the merge on main')
        self.assertEqual(closed.returncode, 0, closed.stdout)
        text = (nxt / 'peer-coding' / 'feature-plots--done' / 'CURRENT.md').read_text()
        self.assertIn('DONE, closed after merge via the merge on main, from branch feature/next', text)
        self.git(nxt, 'commit', '-q', '-m', 'close stale folder', '--', 'peer-coding')
        self.git(self.project, 'worktree', 'remove', '--force', str(where))
        self.git(self.project, 'branch', '-q', '-D', 'feature/plots')
        gone = self.worktree('feature/later', base='main')
        self.assertIn('its branch feature/plots no longer exists here', self.pc(gone, 'check').stdout)

    def test_abandoned_work_closes_without_acceptance(self):
        where, folder, product = self.reviewed()
        result = self.pc(where, 'close', '--as', 'claude', '--abandoned', 'owner dropped the feature')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('DONE, abandoned: owner dropped the feature', (folder.parent / 'feature-plots--done' / 'CURRENT.md').read_text())


class AuditFindings(Close):
    """Cases found by the independent audit: each would have let wrong work through, or blocked right work."""

    def test_only_a_leading_commit_id_is_an_acceptance(self):
        where, folder, product = self.reviewed()
        self.accept(where, folder, 'none', 'yet; codex returned CHANGES REQUESTED on %s (R1)' % product[:12])
        refused = self.pc(where, 'close', '--as', 'claude', '--merged', 'PR 4')
        self.assertEqual(refused.returncode, 1, refused.stdout)
        self.assertIn('records no accepted head', refused.stdout)
        self.accept(where, folder, 'approved', product[:12])
        check = self.pc(where, 'check')
        self.assertEqual(check.returncode, 1, check.stdout)
        self.assertIn('the Accepted head line must start with the accepted commit id, or say none', check.stdout)

    def test_close_folder_is_only_for_a_folder_left_over_from_a_merge(self):
        where, folder, product = self.reviewed()
        refused = self.pc(where, 'close', '--as', 'claude', '--folder', 'feature-plots', '--merged', 'PR 5')
        self.assertIn("is this branch's own folder: close it without --folder", refused.stdout)
        self.git(where, 'checkout', '-q', '--detach')
        refused = self.pc(where, 'close', '--as', 'claude', '--folder', 'feature-plots', '--merged', 'PR 5')
        self.assertIn('detached HEAD', refused.stdout)
        self.git(where, 'checkout', '-q', '-b', 'helper')
        refused = self.pc(where, 'close', '--as', 'claude', '--folder', 'feature-plots', '--merged', 'PR 5')
        self.assertEqual(refused.returncode, 1, refused.stdout)
        self.assertIn('branch feature/plots still exists and is not merged into main', refused.stdout)
        for bad in ('../x', 'SETTINGS.md', '.'):
            self.assertIn('--folder takes the name of a branch folder', self.pc(where, 'close', '--as', 'claude', '--folder', bad, '--merged', 'x').stdout)
        self.assertTrue((where / 'peer-coding' / 'feature-plots').is_dir())

    def test_no_product_change_before_the_first_confirmation(self):
        where, folder = self.started()
        self.edit(folder / 'ALIGNMENT.md', r'^Status: .*$', 'Status: REQUESTED')
        self.commit(where, 'open', 'peer-coding')
        (where / 'app.py').write_text('print("too early")\n')
        early = self.commit(where, 'code before alignment', 'app.py')
        self.set_head(folder, 'feature/plots', early)
        self.edit(folder / 'CURRENT.md', r'^- \*\*Alignment:\*\*.*$', '- **Alignment:** REQUESTED. Next move: codex.')
        self.commit(where, 'record it', 'peer-coding')
        check = self.pc(where, 'check')
        self.assertEqual(check.returncode, 1, check.stdout)
        self.assertIn('product files changed while ALIGNMENT.md is not CONFIRMED: app.py', check.stdout)
        self.git(where, 'push', '-q', '-u', 'origin', 'feature/plots')
        self.assertIn('the checks above must pass', self.pc(where, 'cue', '--as', 'claude').stdout)
        self.edit(folder / 'CURRENT.md', r'^- \*\*Accepted head:\*\*.*$', '- **Accepted head:** %s by codex' % early)
        self.commit(where, 'claim acceptance', 'peer-coding')
        refused = self.pc(where, 'close', '--as', 'claude', '--merged', 'PR 1')
        self.assertEqual(refused.returncode, 1, refused.stdout)

    def test_confirmed_needs_named_roles_and_the_receivers_verdict(self):
        where, folder = self.started()
        self.edit(folder / 'ALIGNMENT.md', r'^Status: .*$', 'Status: CONFIRMED')
        check = self.pc(where, 'check')
        self.assertEqual(check.returncode, 1, check.stdout)
        self.assertIn('CONFIRMED without both roles named and a Receiver verdict that begins CONFIRMED', check.stdout)
        self.assertIn('not CONFIRMED', self.pc(where, 'packet', '--as', 'claude').stdout.replace('is CONFIRMED without', ''))

    def test_close_refuses_while_the_remote_branch_has_commits_this_checkout_lacks(self):
        where, folder, product = self.reviewed()
        self.accept(where, folder, product)
        self.git(where, 'push', '-q', '-u', 'origin', 'feature/plots')
        other = self.root / 'other clone'
        self.git(self.root, 'clone', '-q', '-b', 'feature/plots', str(self.root / 'remote.git'), str(other))
        (other / 'app.py').write_text('print("v2")\n')
        self.commit(other, 'v2 from the other clone', 'app.py')
        self.git(other, 'push', '-q')
        refused = self.pc(where, 'close', '--as', 'claude', '--merged', 'PR 3')
        self.assertEqual(refused.returncode, 1, refused.stdout)
        self.assertIn('origin/feature/plots has 1 commit(s) this checkout does not', refused.stdout)

    def test_a_closed_folder_is_rechecked_against_later_product_changes(self):
        where, folder, product = self.reviewed()
        self.accept(where, folder, product)
        self.assertEqual(self.pc(where, 'close', '--as', 'claude', '--merged', 'PR 3').returncode, 0)
        self.git(where, 'commit', '-q', '-m', 'close', '--', 'peer-coding')
        self.assertEqual(self.pc(where, 'check').returncode, 0)
        (where / 'app.py').write_text('print("after the close")\n')
        self.commit(where, 'after the close', 'app.py')
        check = self.pc(where, 'check')
        self.assertEqual(check.returncode, 1, check.stdout)
        self.assertIn('product files changed after the accepted head of the close: app.py', check.stdout)

    def test_reopen_refuses_after_a_squash_merge_and_when_the_open_name_is_taken(self):
        where, folder, product = self.reviewed()
        self.accept(where, folder, product)
        self.assertEqual(self.pc(where, 'close', '--as', 'claude', '--merged', 'PR 3').returncode, 0)
        self.git(where, 'commit', '-q', '-m', 'close', '--', 'peer-coding')
        (where / 'peer-coding' / 'feature-plots').mkdir()
        taken = self.pc(where, 'close', '--as', 'claude', '--reopen', 'retry')
        self.assertIn('peer-coding/feature-plots already exists', taken.stdout)
        (where / 'peer-coding' / 'feature-plots').rmdir()
        self.git(self.project, 'merge', '-q', '--squash', 'feature/plots')
        self.git(self.project, 'commit', '-q', '-m', 'squash-merge feature/plots')
        refused = self.pc(where, 'close', '--as', 'claude', '--reopen', 'more work')
        self.assertEqual(refused.returncode, 1, refused.stdout)
        self.assertIn('is already merged into main', refused.stdout)

    def test_links_that_would_break_in_another_clone(self):
        where, folder = self.started()
        (where / '.gitignore').write_text('.env\n')
        (where / '.env').write_text('SECRET=1\n')
        self.commit(where, 'ignore env', '.gitignore')
        self.set_head(folder, 'feature/plots', self.git(where, 'rev-parse', 'HEAD'))
        evidence = folder / 'rounds' / 'R1' / 'evidence' / 'claude'
        evidence.mkdir(parents=True)
        os.symlink(tempfile.gettempdir(), str(evidence / 'ext'))
        with open(folder / 'FINDINGS.md', 'a') as notes:
            notes.write('\nSee [f](file:///etc/hosts), [env](../../.env), [case](alignment.md), [out](rounds/R1/evidence/claude/ext), '
                        '[empty]( ), and [r1].\n\n[r1]: ../../../../outside-the-repo.md\n')
        check = self.pc(where, 'check')
        self.assertEqual(check.returncode, 1, check.stdout)
        for expected in ("link file:///etc/hosts points into this machine's files",
                         'link ../../.env points to a file the repository ignores',
                         'link alignment.md points to nothing (check the spelling and letter case',
                         'link rounds/R1/evidence/claude/ext leaves the repository through a symbolic link',
                         'a link with no target',
                         'link ../../../../outside-the-repo.md leaves the repository'):
            self.assertIn(expected, check.stdout)

    def test_the_relay_line_needs_the_branchs_own_upstream_and_a_packet_for_new_work(self):
        where, folder = self.started()
        self.confirm(where, 'feature/plots', writer='codex')
        (where / 'app.py').write_text('print("r1")\n')
        product = self.commit(where, 'r1', 'app.py')
        self.set_head(folder, 'feature/plots', product)
        self.commit(where, 'hand over without a packet', 'peer-coding')
        self.git(where, 'push', '-q', 'origin', 'feature/plots')
        self.git(where, 'branch', '-q', '--set-upstream-to', 'origin/main')
        refused = self.pc(where, 'cue', '--as', 'claude')
        self.assertIn('does not track its own remote branch (it tracks origin/main)', refused.stdout)
        self.git(where, 'push', '-q', '-u', 'origin', 'feature/plots')
        noted = self.pc(where, 'cue', '--as', 'claude')
        self.assertEqual(noted.returncode, 0, noted.stdout)
        self.assertIn('NOTE: no packet of yours was written after the last product commit', noted.stdout)
        self.git(where, 'branch', '-q', '--set-upstream-to', 'origin/main')
        self.assertEqual(self.pc(where, 'packet', '--as', 'claude').returncode, 0)
        self.edit(folder / 'rounds' / 'R1' / 'claude.md', r'^Status: WIP.*\n', '')
        self.commit(where, 'R1 packet', 'peer-coding')
        refused = self.pc(where, 'cue', '--as', 'claude')
        self.assertIn('does not track its own remote branch (it tracks origin/main)', refused.stdout)
        self.git(where, 'push', '-q', '-u', 'origin', 'feature/plots')
        (where / 'peer-coding' / 'SETTINGS.md').write_text(SETTINGS.format(push='no'))
        self.assertIn('peer-coding/ has uncommitted changes', self.pc(where, 'cue', '--as', 'claude').stdout)
        self.git(where, 'checkout', '--', 'peer-coding/SETTINGS.md')
        result = self.pc(where, 'cue', '--as', 'claude')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('READY FOR CODEX · peer-coding/feature-plots R1', result.stdout)

    def test_push_yes_without_a_remote_is_refused(self):
        where, folder = self.started()
        self.edit(folder / 'ALIGNMENT.md', r'^Status: .*$', 'Status: BRIEFED')
        self.edit(folder / 'CURRENT.md', r'^- \*\*Alignment:\*\*.*$', '- **Alignment:** BRIEFED. Next move: codex.')
        self.commit(where, 'brief', 'peer-coding')
        self.git(where, 'remote', 'remove', 'origin')
        refused = self.pc(where, 'cue', '--as', 'claude')
        self.assertIn('says Push: yes, but this repository has no remote', refused.stdout)

    def test_odd_branch_names(self):
        for branch, expected in (('x-/done', 'which marks closed folders'), ('tick`name', 'cannot hold'),
                                 ('pipe|name', 'cannot hold'), ('b' * 230, 'too long for a folder name')):
            if subprocess.run(['git', 'check-ref-format', '--branch', branch], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).returncode != 0:
                continue
            where = self.root / ('odd %s' % PEER.short_hash(branch))
            self.git(self.project, 'worktree', 'add', '-q', str(where), '-b', branch, 'main')
            result = self.pc(where, 'start', '--as', 'claude')
            self.assertEqual(result.returncode, 1, branch + result.stdout)
            self.assertIn(expected, result.stdout, branch)

    def test_a_tag_named_like_the_branch_does_not_change_the_branch_name(self):
        self.git(self.project, 'tag', 'release-1')
        where = self.worktree('release-1')
        self.assertEqual(self.pc(where, 'start', '--as', 'claude').returncode, 0)
        self.assertIn('Branch `release-1`', (where / 'peer-coding' / 'release-1' / 'CURRENT.md').read_text())

    def test_a_remote_only_branch_with_the_same_folder_name_gives_a_code(self):
        self.git(self.project, 'push', '-q', 'origin', 'main:refs/heads/feature-plots')
        self.git(self.project, 'fetch', '-q', 'origin')
        where = self.worktree('feature/plots')
        self.assertEqual(self.pc(where, 'which').stdout.strip(), 'peer-coding/feature-plots-%s none' % PEER.short_hash('feature/plots'))

    def test_a_missing_template_is_refused_not_written_empty(self):
        copy = self.root / 'engine copy'
        subprocess.run(['cp', '-R', str(self.project / 'archetype'), str(copy)], check=True)
        subprocess.run(['rm', '-r', str(copy / 'templates' / 'peer-coding')], check=True)
        where = self.worktree('feature/plots')
        result = subprocess.run(['python3', str(copy / 'scripts' / 'peer-coding.py'), 'start', '--as', 'claude'], cwd=str(where),
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, env=self.env)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('templates/peer-coding/CURRENT.md is missing', result.stdout)
        self.assertFalse(self.folder(where, 'feature/plots').exists())

    def test_every_findings_table_counts_and_a_linked_setting_is_filled(self):
        where, folder, product = self.reviewed()
        self.accept(where, folder, product)
        with open(folder / 'FINDINGS.md', 'a') as findings:
            findings.write('\n## Later\n\n| ID | Severity | Remaining work | Owner | Evidence |\n|---|---|---|---|---|\n| F7 | low | x | codex | R1 |\n')
        self.commit(where, 'second table', 'peer-coding')
        self.assertIn('still lists 1 unresolved item', self.pc(where, 'close', '--as', 'claude', '--merged', 'PR 2').stdout)
        linked = SETTINGS.format(push='yes').replace('- Checks each turn: test', '- Checks each turn: [the test command](../References.md), before each hand-over')
        self.assertEqual(PEER.settings_problems(self._write(linked)), [])

    def _write(self, text):
        path = Path(self.temp.name) / 'SETTINGS.md'
        path.write_text(text)
        return path

    def test_the_checks_inside_cue_and_close_hold_on_their_own(self):
        where, folder, product = self.reviewed()
        self.accept(where, folder, product)
        self.git(where, 'push', '-q', '-u', 'origin', 'feature/plots')
        (where / 'app.py').write_text('print("uncommitted")\n')
        self.assertIn('uncommitted product changes', self.pc(where, 'cue', '--as', 'claude').stdout)
        self.assertIn('uncommitted product changes', self.pc(where, 'close', '--as', 'claude', '--merged', 'PR 1').stdout)
        self.git(where, 'checkout', '--', 'app.py')
        side = self.git(where, 'rev-parse', 'main')
        self.git(self.project, 'commit', '-q', '--allow-empty', '-m', 'elsewhere on main')
        elsewhere = self.git(self.project, 'rev-parse', 'main')
        self.accept(where, folder, elsewhere)
        refused = self.pc(where, 'close', '--as', 'claude', '--merged', 'PR 1')
        self.assertIn('is not in this branch\'s history', refused.stdout)
        self.set_head(folder, 'feature/plots', elsewhere)
        self.assertIn("the recorded last product commit %s is not in this branch's history" % elsewhere, self.pc(where, 'check').stdout)
        self.assertTrue(side)


class Waiting(Base):
    def test_needs_user_and_scope_closed_lines_carry_the_commit(self):
        where, folder = self.started()
        self.edit(folder / 'CURRENT.md', r'^1\. claude: .*$', '1. NEEDS USER: does a swap keep the watering rota?')
        self.commit(where, 'ask the owner', 'peer-coding')
        self.git(where, 'push', '-q', '-u', 'origin', 'feature/plots')
        result = self.pc(where, 'cue', '--as', 'claude')
        self.assertEqual(result.returncode, 0, result.stdout)
        sha = self.git(where, 'rev-parse', '--short=12', 'HEAD')
        self.assertIn('NEEDS USER · peer-coding/feature-plots · feature/plots@%s' % sha, result.stdout)
        self.assertIn('read AGENTS.md there', result.stdout)
        self.edit(folder / 'CURRENT.md', r'^1\. NEEDS USER: .*$', '1. SCOPE CLOSED: awaiting the owner')
        self.commit(where, 'scope closed', 'peer-coding')
        self.git(where, 'push', '-q')
        result = self.pc(where, 'cue', '--as', 'claude')
        self.assertIn('SCOPE CLOSED · peer-coding/feature-plots · feature/plots@', result.stdout)

    def test_check_names_leftovers_without_settings_and_a_line_that_disagrees(self):
        where = self.worktree('feature/plots')
        (where / 'peer-coding' / 'README.md').write_text('# Peer coding\n')
        (where / 'References.md').write_text(REFERENCES.format(peer='- Peer coding: none\n'))
        result = self.pc(where, 'check')
        self.assertIn('WARN: References.md says Peer coding: none while peer-coding/SETTINGS.md exists', result.stdout)
        (where / 'peer-coding' / 'SETTINGS.md').unlink()
        result = self.pc(where, 'check')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('peer coding is not set up', result.stdout)
        self.assertIn('README.md hold an earlier copy of peer-coding rules', result.stdout)


class TwoUnits(unittest.TestCase):
    """One repository with an engine per unit: the record sits at the top, the relay line names the unit's AGENTS.md."""

    def test_the_relay_line_names_the_units_agents_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            env = dict(os.environ, HOME=str(root), GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1',
                       GIT_AUTHOR_NAME='T', GIT_AUTHOR_EMAIL='t@example.com', GIT_COMMITTER_NAME='T',
                       GIT_COMMITTER_EMAIL='t@example.com')
            repo = root / 'repo'
            for unit in ('frontend', 'backend'):
                (repo / unit).mkdir(parents=True)
                subprocess.run(['bash', str(ENGINE / 'inject.sh'), str(repo / unit)], stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, env=env, check=True)
            (repo / 'peer-coding').mkdir()
            (repo / 'peer-coding' / 'SETTINGS.md').write_text(SETTINGS.format(push='no'))
            run = lambda *args: subprocess.run(list(args), cwd=str(repo), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                               universal_newlines=True, env=env)
            for command in (['git', 'init', '-q', '-b', 'main'], ['git', 'add', '-A'], ['git', 'commit', '-q', '-m', 'init'],
                            ['git', 'checkout', '-q', '-b', 'feature/both']):
                self.assertEqual(run(*command).returncode, 0)
            script = str(repo / 'frontend' / 'archetype' / 'scripts' / 'peer-coding.py')
            self.assertEqual(run('python3', script, 'start', '--as', 'claude').returncode, 0)
            folder = repo / 'peer-coding' / 'feature-both'
            self.assertIn('../../frontend/archetype/development/PEER-CODING.md', (folder / 'CURRENT.md').read_text())
            text = (folder / 'ALIGNMENT.md').read_text().replace('Status: <REQUESTED | BRIEFED | CONFIRMED>', 'Status: BRIEFED')
            (folder / 'ALIGNMENT.md').write_text(text)
            current = (folder / 'CURRENT.md').read_text()
            (folder / 'CURRENT.md').write_text(re.sub(r'^- \*\*Alignment:\*\*.*$', '- **Alignment:** BRIEFED. Next move: codex.', current, flags=re.M))
            self.assertEqual(run('git', 'add', '-A').returncode, 0)
            self.assertEqual(run('git', 'commit', '-q', '-m', 'brief').returncode, 0)
            result = run('python3', script, 'cue', '--as', 'claude')
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn('read frontend/AGENTS.md there, then peer-coding/feature-both/CURRENT.md', result.stdout)


class RoundThree(Close):
    """Cases from the second round of the independent script audit."""

    def test_no_product_change_while_realigning_even_after_rounds(self):
        where, folder, product = self.reviewed()
        self.assertEqual(self.pc(where, 'packet', '--as', 'claude').returncode, 0)
        self.edit(folder / 'rounds' / 'R1' / 'claude.md', r'^Status: WIP.*\n', '')
        self.commit(where, 'R1', 'peer-coding')
        self.edit(folder / 'ALIGNMENT.md', r'^Status: .*$', 'Status: BRIEFED')
        self.edit(folder / 'CURRENT.md', r'^- \*\*Alignment:\*\*.*$', '- **Alignment:** BRIEFED. Next move: codex.')
        self.edit(folder / 'CURRENT.md', r'^- \*\*Product writing turn:\*\*.*$', '- **Product writing turn:** none')
        self.commit(where, 're-brief', 'peer-coding')
        (where / 'app.py').write_text('print("v2 during the re-brief")\n')
        v2 = self.commit(where, 'v2', 'app.py')
        self.set_head(folder, 'feature/plots', v2)
        self.commit(where, 'record v2', 'peer-coding')
        check = self.pc(where, 'check')
        self.assertEqual(check.returncode, 1, check.stdout)
        self.assertIn('product files changed while ALIGNMENT.md is not CONFIRMED: app.py', check.stdout)

    def test_a_merge_of_the_default_branch_during_alignment_is_allowed(self):
        where, folder = self.started()
        self.commit(where, 'open', 'peer-coding')
        (self.project / 'other.txt').write_text('from main\n')
        self.commit(self.project, 'main moves on', 'other.txt')
        self.git(where, 'merge', '-q', '--no-edit', 'main')
        self.set_head(folder, 'feature/plots', self.git(where, 'rev-parse', 'HEAD'))
        self.commit(where, 'record the merge', 'peer-coding')
        check = self.pc(where, 'check')
        self.assertEqual(check.returncode, 0, check.stdout)

    def test_a_hand_written_packet_does_not_open_the_way_before_confirmation(self):
        where, folder = self.started()
        (folder / 'rounds' / 'R1').mkdir(parents=True)
        (folder / 'rounds' / 'R1' / 'claude.md').write_text('# packet\n')
        self.commit(where, 'open with a packet', 'peer-coding')
        (where / 'app.py').write_text('print("early")\n')
        early = self.commit(where, 'early', 'app.py')
        self.set_head(folder, 'feature/plots', early)
        self.commit(where, 'record it', 'peer-coding')
        self.assertIn('product files changed while ALIGNMENT.md is not CONFIRMED', self.pc(where, 'check').stdout)

    def test_scope_closed_needs_the_acceptance_of_the_product_changes(self):
        where, folder, product = self.reviewed()
        self.git(where, 'push', '-q', '-u', 'origin', 'feature/plots')
        self.edit(folder / 'CURRENT.md', r'^1\. .*$', '1. SCOPE CLOSED: awaiting the owner')
        self.commit(where, 'scope closed', 'peer-coding')
        self.git(where, 'push', '-q')
        refused = self.pc(where, 'cue', '--as', 'claude')
        self.assertEqual(refused.returncode, 1, refused.stdout)
        self.assertIn("SCOPE CLOSED needs the other assistant's acceptance", refused.stdout)
        self.accept(where, folder, product)
        self.git(where, 'push', '-q')
        self.assertIn('SCOPE CLOSED · peer-coding/feature-plots', self.pc(where, 'cue', '--as', 'claude').stdout)

    def test_close_for_merge_needs_a_confirmed_alignment(self):
        where, folder = self.started()
        self.edit(folder / 'ALIGNMENT.md', r'^Status: .*$', 'Status: BRIEFED')
        self.edit(folder / 'CURRENT.md', r'^- \*\*Alignment:\*\*.*$', '- **Alignment:** BRIEFED. Next move: codex.')
        head = self.git(where, 'rev-parse', 'HEAD')
        self.edit(folder / 'CURRENT.md', r'^- \*\*Accepted head:\*\*.*$', '- **Accepted head:** %s by codex' % head)
        self.commit(where, 'brief', 'peer-coding')
        refused = self.pc(where, 'close', '--as', 'claude', '--merged', 'PR 1')
        self.assertEqual(refused.returncode, 1, refused.stdout)
        self.assertIn('ALIGNMENT.md is not CONFIRMED', refused.stdout)

    def test_the_verdict_must_say_confirmed_and_roles_may_name_their_tools(self):
        where, folder = self.started()
        self.confirm(where, 'feature/plots')
        self.edit(folder / 'ALIGNMENT.md', r'^Receiver verdict: .*$', 'Receiver verdict: REQUESTED; claim 2 is a DISCREPANCY')
        check = self.pc(where, 'check')
        self.assertEqual(check.returncode, 1, check.stdout)
        self.assertIn('a Receiver verdict that begins CONFIRMED', check.stdout)
        self.assertIn('not CONFIRMED', self.pc(where, 'packet', '--as', 'claude').stdout)
        self.edit(folder / 'ALIGNMENT.md', r'^Receiver verdict: .*$', 'Receiver verdict: CONFIRMED by codex.')
        self.edit(folder / 'ALIGNMENT.md', r'^Context holder: .*$', 'Context holder: claude (Claude Code) · Receiver: codex (Codex)')
        self.assertEqual(self.pc(where, 'check').returncode, 0)

    def test_close_compares_only_with_the_branchs_own_remote_branch(self):
        where, folder, product = self.reviewed()
        self.accept(where, folder, product)
        self.git(where, 'branch', '-q', '--set-upstream-to', 'origin/main')
        (self.project / 'other.txt').write_text('main moved\n')
        self.commit(self.project, 'main moves on', 'other.txt')
        self.git(self.project, 'push', '-q')
        self.git(where, 'fetch', '-q', 'origin')
        closed = self.pc(where, 'close', '--as', 'claude', '--merged', 'PR 2')
        self.assertEqual(closed.returncode, 0, closed.stdout)

    def test_more_links_a_clone_cannot_follow_and_things_that_are_not_links(self):
        where, folder = self.started()
        evidence = folder / 'rounds' / 'R1' / 'evidence' / 'claude'
        evidence.mkdir(parents=True)
        (evidence / 'real.txt').write_text('ok\n')
        os.symlink('real.txt', str(evidence / 'alias.txt'))
        with open(folder / 'FINDINGS.md', 'a') as notes:
            notes.write('\nSee <file:///etc/hosts>, <a href="../../../../o.md">here</a>, [ed](vscode://file/x), '
                        '<https://example.com/fine>.\n\n[^1]: Seen twice in logs.\n[unverified]: this claim was not checked.\n')
        check = self.pc(where, 'check')
        self.assertEqual(check.returncode, 1, check.stdout)
        for expected in ("link file:///etc/hosts points into this machine's files", 'link ../../../../o.md leaves the repository',
                         'link vscode://file/x opens something on this machine', 'alias.txt is a symbolic link'):
            self.assertIn(expected, check.stdout)
        for quiet in ('Seen', 'this claim', 'example.com'):
            self.assertNotIn(quiet, check.stdout)

    def test_commit_signatures_shown_by_git_log_do_not_break_the_hand_over(self):
        where, folder = self.started()
        self.git(where, 'config', 'log.showSignature', 'true')
        self.confirm(where, 'feature/plots', writer='codex')
        (where / 'app.py').write_text('print("r1")\n')
        product = self.commit(where, 'r1', 'app.py')
        self.set_head(folder, 'feature/plots', product)
        self.assertEqual(self.pc(where, 'packet', '--as', 'claude').returncode, 0)
        self.edit(folder / 'rounds' / 'R1' / 'claude.md', r'^Status: WIP.*\n', '')
        self.commit(where, 'R1', 'peer-coding')
        self.git(where, 'push', '-q', '-u', 'origin', 'feature/plots')
        result = self.pc(where, 'cue', '--as', 'claude')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn('NOTE: no packet', result.stdout)

    def test_a_file_system_error_is_a_refusal_not_a_traceback(self):
        where = self.worktree('feature/plots')
        record = where / 'peer-coding'
        os.chmod(str(record), 0o500)
        self.addCleanup(os.chmod, str(record), 0o700)
        result = self.pc(where, 'start', '--as', 'claude')
        if os.geteuid() == 0:
            self.skipTest('root ignores folder permissions')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('FAIL:', result.stdout)
        self.assertNotIn('Traceback', result.stdout)


class Bootstrap(unittest.TestCase):
    def check(self, peer, settings=None):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / 'References.md').write_text(REFERENCES.format(peer=peer))
            (Path(temp) / 'feature-tree.md').write_text('# Features\n')
            if settings is not None:
                (Path(temp) / 'peer-coding').mkdir()
                (Path(temp) / 'peer-coding' / 'SETTINGS.md').write_text(settings)
            return subprocess.run(['python3', str(ENGINE / 'scripts' / 'validate-bootstrap.py'), 'context'], cwd=temp,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    def test_setup_records_the_owners_peer_answer(self):
        complete = SETTINGS.format(push='yes')
        for peer, settings, code, expected in (
                ('', None, 1, 'Peer coding: ask the owner whether another AI assistant'),
                ('- Peer coding: [none; or peer-coding/SETTINGS.md]\n', None, 1, 'Peer coding: ask the owner'),
                ('- Peer coding: none\n', None, 0, 'OK'),
                ('- Peer coding: claude and codex\n', None, 1, 'record none, or peer-coding/SETTINGS.md'),
                (ON, None, 1, 'SETTINGS.md does not exist'),
                (ON, complete.replace('- Push: yes\n', '- Push: [yes or no]\n'), 1, 'fill in: Push'),
                (ON, complete, 0, 'OK')):
            result = self.check(peer, settings)
            self.assertEqual(result.returncode, code, peer + result.stdout)
            self.assertIn(expected, result.stdout)

    def test_a_project_inside_another_repository_reads_its_own_settings(self):
        with tempfile.TemporaryDirectory() as temp:
            outer = Path(temp)
            subprocess.run(['git', 'init', '-q', str(outer)], check=True)
            project = outer / 'app'
            (project / 'peer-coding').mkdir(parents=True)
            (project / 'References.md').write_text(REFERENCES.format(peer=ON))
            (project / 'feature-tree.md').write_text('# Features\n')
            (project / 'peer-coding' / 'SETTINGS.md').write_text(SETTINGS.format(push='yes'))
            result = subprocess.run(['python3', str(ENGINE / 'scripts' / 'validate-bootstrap.py'), 'context'], cwd=str(project),
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == '__main__':
    unittest.main()
