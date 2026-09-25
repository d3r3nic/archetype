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
        self.assertIn("fill in, with the owner's decisions: Merge", result.stdout)
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
        self.assertIn('is closed; new work gets a new branch', result.stdout)

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
                         'link ALIGNMENT.md:12 points to nothing (a line number belongs after the link'):
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
        self.assertIn('the folder has uncommitted changes', self.pc(where, 'cue', '--as', 'claude').stdout)
        self.edit(folder / 'ALIGNMENT.md', r'^Status: .*$', 'Status: BRIEFED')
        self.edit(folder / 'ALIGNMENT.md', r'^Context holder: .*$', 'Context holder: claude · Receiver: codex')
        self.edit(folder / 'CURRENT.md', r'^- \*\*Alignment:\*\*.*$', '- **Alignment:** BRIEFED, see [ALIGNMENT.md](ALIGNMENT.md). Next move: codex.')
        self.commit(where, 'brief', 'peer-coding')
        result = self.pc(where, 'cue', '--as', 'claude')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('push the branch and set its upstream first', result.stdout)
        self.git(where, 'push', '-q', '-u', 'origin', 'feature/plots')
        result = self.pc(where, 'cue', '--as', 'claude')
        self.assertEqual(result.returncode, 0, result.stdout)
        sha = self.git(where, 'rev-parse', '--short=12', 'HEAD')
        self.assertIn('READY FOR CODEX · peer-coding/feature-plots ALIGN · feature/plots@%s' % sha, result.stdout)
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
        self.assertIn('READY FOR CODEX · peer-coding/feature-plots ALIGN', result.stdout)


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
                (ON, complete.replace('- Push: yes\n', '- Push: [yes or no]\n'), 1, "fill in, with the owner's decisions: Push"),
                (ON, complete, 0, 'OK')):
            result = self.check(peer, settings)
            self.assertEqual(result.returncode, code, peer + result.stdout)
            self.assertIn(expected, result.stdout)


if __name__ == '__main__':
    unittest.main()
