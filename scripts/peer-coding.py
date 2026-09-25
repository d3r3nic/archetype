#!/usr/bin/env python3
"""Peer coding: two AI assistants taking turns on a branch (development/PEER-CODING.md).

Run with python3 from anywhere inside the repository's worktree:
  peer-coding.py setup                 create peer-coding/SETTINGS.md, the project's choices, to fill in
  peer-coding.py start --as NAME       open this branch's folder
  peer-coding.py packet --as NAME      open your next packet, rounds/R<n>/NAME.md, marked WIP
  peer-coding.py check [--as NAME]     check the settings, the branch folder, recorded commits, links
  peer-coding.py which                 print this branch's folder and whether it is active, done or none
  peer-coding.py cue --as NAME         print the line the owner pastes into the other chat
  peer-coding.py close --as NAME (--merged REF | --abandoned REASON | --reopen REASON) [--folder FOLDER]
                                       close the folder as <folder>--done before the merge, record
                                       abandoned work, or reopen a folder whose merge did not happen

NAME is one of the two short names on the Peers line of peer-coding/SETTINGS.md. A branch's folder is
the branch name with slashes and other unusual characters as dashes, with a short code added when
another branch already uses that name; `which` prints it.

What it cannot do: judge whether a review was good, or know which assistant made a commit.

Exit 0: done, or the check passed. 1: a check failed or the command refused. 2: usage.
3: start found this branch's folder already open (resume it).
"""
import argparse
import datetime
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ENGINE = Path(__file__).resolve().parent.parent
TEMPLATES = ENGINE / 'templates' / 'peer-coding'
PLAYBOOK = Path('development') / 'PEER-CODING.md'
RECORD = 'peer-coding'
SETTINGS = 'SETTINGS.md'
DONE = '--done'
# Names in peer-coding/ that are not branch folders: this project's settings, and the shared
# files an earlier copy of these rules put there.
RESERVED = ('SETTINGS.md', 'README.md', 'PROTOCOL.md', 'templates')
SETTINGS_KEYS = ('Peers', 'Who writes', 'Checks each turn', 'Branch names', 'Push', 'Merge', 'Project rules')
PEERS_FORMAT = 'name the two assistants as "<name> (<tool>), <name> (<tool>)"'


class Refusal(Exception):
    pass


def git(top, *args, check=True, timeout=None):
    result = subprocess.run(['git', '-C', str(top)] + list(args), stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, universal_newlines=True, timeout=timeout)
    if check and result.returncode != 0:
        raise Refusal('git %s failed: %s' % (' '.join(args), result.stderr.strip()))
    return result


def out(top, *args):
    return git(top, *args).stdout.strip()


def succeeds(top, *args):
    return git(top, *args, check=False).returncode == 0


def read(path):
    return path.read_text(encoding='utf-8') if path.is_file() else ''


def write(path, text):
    path.write_text(text, encoding='utf-8')


def plain(value):
    return re.sub(r'[*_`]', '', value or '').strip()


def filled(value):
    # A bracketed template prompt is not filled; a value that starts with a Markdown link is.
    text = plain(value)
    return bool(text) and not (text.startswith('[') and not re.match(r'^\[[^\]]+\]\([^)]+\)', text))


def live_lines(text):
    fence = None
    for line in text.splitlines():
        mark = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if mark:
            token, tail = mark.groups()
            if fence is None:
                fence = (token[0], len(token))
            elif token[0] == fence[0] and len(token) >= fence[1] and not tail.strip():
                fence = None
            continue
        if fence is None:
            yield line


# ---------------------------------------------------------------- the project and the branch

class Project:
    def __init__(self, where):
        probe = git(where, 'rev-parse', '--show-toplevel', check=False)
        if probe.returncode != 0:
            raise Refusal('%s is not inside a git worktree; peer coding keeps its record in the '
                          'repository' % where)
        self.top = Path(probe.stdout.strip()).resolve()
        head = git(self.top, 'symbolic-ref', '-q', 'HEAD', check=False).stdout.strip()
        self.branch = head[len('refs/heads/'):] if head.startswith('refs/heads/') else ''
        self.default = self._default_branch()
        self.engine = self._engine_here()

    def _default_branch(self):
        head = git(self.top, 'symbolic-ref', '-q', '--short', 'refs/remotes/origin/HEAD',
                   check=False).stdout.strip()
        if head.startswith('origin/'):
            return head[len('origin/'):]
        configured = git(self.top, 'config', '--get', 'init.defaultBranch', check=False).stdout.strip()
        for name in [configured, 'main', 'master']:
            if name and (self.ref_exists('refs/heads/' + name) or self.ref_exists('refs/remotes/origin/' + name)):
                return name
        return ''

    def ref_exists(self, ref):
        return succeeds(self.top, 'show-ref', '-q', '--verify', ref)

    def default_refs(self):
        """The default branch here, on origin, and on the remote the local default branch tracks. Another remote's
        branch of the same name (a deploy target, a fork) is not the project's default branch."""
        if not self.default:
            return []
        refs = ['refs/heads/' + self.default, 'refs/remotes/origin/' + self.default]
        tracked = git(self.top, 'config', '--get', 'branch.%s.remote' % self.default, check=False).stdout.strip()
        merge = git(self.top, 'config', '--get', 'branch.%s.merge' % self.default, check=False).stdout.strip()
        if tracked and tracked != '.' and merge.startswith('refs/heads/'):
            refs.append('refs/remotes/%s/%s' % (tracked, merge[len('refs/heads/'):]))
        seen = []
        for ref in refs:
            if ref not in seen and self.ref_exists(ref):
                seen.append(ref)
        return seen

    def _engine_here(self):
        # The engine as this worktree carries it: the same place relative to the repository top as
        # the engine this script ran from, so another checkout's script reads this branch's files.
        engine_top = git(ENGINE, 'rev-parse', '--show-toplevel', check=False)
        if engine_top.returncode == 0:
            relative = os.path.relpath(str(ENGINE), str(Path(engine_top.stdout.strip()).resolve()))
            candidate = (self.top / relative).resolve() if relative != '.' else self.top
            if (candidate / PLAYBOOK).is_file():
                return candidate
        return ENGINE

    def record(self):
        return self.top / RECORD

    def version(self):
        """The framework revision this engine was installed from, when the project's log records it."""
        for log in (self.engine.parent / 'VERSION-LOG.md', self.engine / 'VERSION-LOG.md', self.engine / 'VERSION'):
            commits = re.findall(r'^(?:Commit:\s*)?([0-9a-f]{7,40})\s*$', read(log), re.M)
            if commits:
                return commits[-1][:12]
        return ''


def agents_file(project):
    """The AGENTS.md a session in this worktree reads: the unit's, in a repository with one engine per unit."""
    for folder in (project.engine.parent, project.engine, project.top):
        candidate = folder / 'AGENTS.md'
        try:
            candidate.relative_to(project.top)
        except ValueError:
            continue
        if candidate.is_file():
            return display(project, candidate)
    return 'AGENTS.md'


def references_line(project):
    """References.md's Peer coding value for this engine's project, or None when there is no such line."""
    for path in (project.engine / 'References.md', project.engine.parent / 'References.md'):
        if path.is_file():
            inside = False
            for line in live_lines(read(path)):
                if line.startswith('## '):
                    inside = line.strip() == '## Project'
                match = re.match(r'^- Peer coding:\s*(.*)$', line) if inside else None
                if match:
                    return plain(match.group(1))
            return None
    return None


def display(project, path):
    try:
        return str(Path(path).resolve().relative_to(project.top))
    except ValueError:
        return str(path)


def slug(branch):
    name = re.sub(r'[^A-Za-z0-9._-]', '-', branch.replace('/', '-'))
    return name if re.match(r'[A-Za-z0-9]', name) else 'branch-' + name


def short_hash(branch):
    return hashlib.sha1(branch.encode('utf-8')).hexdigest()[:6]


def recorded_branch(text):
    match = re.search(r'^Branch `([^`]+)`', text, re.M)
    return match.group(1) if match else ''


def branch_folder(project, branch):
    """This branch's folder and its state: active, done, or none (not opened yet, and the name it would get)."""
    record = project.record()
    base = slug(branch)
    hashed = '%s-%s' % (base, short_hash(branch))
    for name in (base, hashed):
        if recorded_branch(read(record / name / 'CURRENT.md')) == branch:
            return record / name, 'active'
        if recorded_branch(read(record / (name + DONE) / 'CURRENT.md')) == branch:
            return record / (name + DONE), 'done'
    if base in RESERVED:
        return record / hashed, 'none'
    for name in (base, base + DONE):
        other = recorded_branch(read(record / name / 'CURRENT.md'))
        if (other and other != branch) or ((record / name).exists() and not other):
            return record / hashed, 'none'
    # A branch not merged here yet, or a folder already on the default branch, may hold the name.
    refs = git(project.top, 'for-each-ref', '--format=%(refname)', 'refs/heads', 'refs/remotes').stdout.split()
    for ref in refs:
        name = ref[len('refs/heads/'):] if ref.startswith('refs/heads/') else ref.split('/', 3)[-1]
        if name not in ('HEAD', branch) and slug(name) == base:
            return record / hashed, 'none'
    for ref in project.default_refs():
        for name in (base, base + DONE, hashed + DONE):
            shown = git(project.top, 'show', '%s:%s/%s/CURRENT.md' % (ref, RECORD, name), check=False)
            other = recorded_branch(shown.stdout) if shown.returncode == 0 else ''
            if other == branch and name.endswith(DONE):
                return record / name, 'done'  # a merged branch's name, used again
            if other and other != branch:
                return record / hashed, 'none'
    return record / base, 'none'


# ---------------------------------------------------------------- the project's settings

def settings_fields(text):
    fields = {}
    for line in live_lines(text):
        if line.startswith('#'):
            continue
        match = re.match(r'^- ([^:]+):\s*(.*)$', line)
        if match and match.group(1).strip() not in fields:
            fields[match.group(1).strip()] = match.group(2).strip()
    return fields


def parse_peers(value):
    """The two short names on a Peers line; ValueError when the line cannot be read that way."""
    text = plain(value)
    if not text or text.startswith('['):
        raise ValueError('the Peers line is not filled in: ' + PEERS_FORMAT)
    text = re.sub(r'\([^)]*\)', ' ', text)
    names = []
    for part in re.split(r',|;|&|\band\b', text):
        part = part.strip()
        if not part:
            continue
        match = re.match(r'^([A-Za-z][A-Za-z0-9-]*)$', part)
        if not match:
            raise ValueError('cannot read "%s" on the Peers line: %s' % (part, PEERS_FORMAT))
        names.append(match.group(1).lower())
    if len(names) != 2 or names[0] == names[1] or any(name.endswith(DONE) or name == 'none' for name in names):
        raise ValueError('the Peers line must name two different assistants: ' + PEERS_FORMAT)
    return names


def settings_problems(path, complete=True):
    """What keeps a settings file from being usable: an empty list when it is."""
    if not path.is_file():
        return ['%s does not exist' % path.name]
    fields = settings_fields(read(path))
    problems = []
    try:
        parse_peers(fields.get('Peers', ''))
    except ValueError as error:
        problems.append(str(error))
    keys = SETTINGS_KEYS if complete else ('Who writes',)
    missing = [key for key in keys if key != 'Peers' and not filled(fields.get(key, ''))]
    if missing:
        problems.append('fill in: %s' % ', '.join(missing))
    push = plain(fields.get('Push', ''))
    if re.match(r'^no\b', push, re.I) and not re.sub(r'^no\b[\s:,.;-]*', '', push, flags=re.I).strip():
        problems.append('Push: no needs its reason (a push to a work branch would itself start a deploy or release '
                        'build, or there is no remote)')
    return problems


def settings_of(project):
    path = project.record() / SETTINGS
    if not path.is_file():
        raise Refusal('peer coding is not set up in this repository: there is no %s/%s. When the owner has '
                      'chosen peer coding (the questions are in bootstrap/ONBOARD-2.6-CARE-AND-AUTHORITY.md), '
                      'run setup and fill it with the owner\'s answers' % (RECORD, SETTINGS))
    problems = settings_problems(path)
    if problems:
        raise Refusal('%s/%s: %s' % (RECORD, SETTINGS, '; '.join(problems)))
    fields = settings_fields(read(path))
    return parse_peers(fields['Peers']), fields


def pushes(fields):
    return not re.match(r'^no\b', plain(fields.get('Push', '')), re.I)


# ---------------------------------------------------------------- a branch folder's files

def current_state(folder):
    text = read(folder / 'CURRENT.md')
    state = {'text': text, 'branch': recorded_branch(text)}
    status = re.search(r'^- \*\*Status:\*\*\s*([A-Za-z]+)', text, re.M)
    state['status'] = status.group(1).upper() if status else ''
    alignment = re.search(r'^- \*\*Alignment:\*\*(.*)$', text, re.M)
    line = alignment.group(1) if alignment else ''
    word = re.search(r'\b(REQUESTED|BRIEFED|CONFIRMED)\b', line)
    state['alignment'] = word.group(1) if word else ''
    move = re.search(r'Next move:\s*\**`?([A-Za-z][A-Za-z0-9-]*)', line)
    state['next_move'] = move.group(1).lower() if move else ''
    turn = re.search(r'^- \*\*Product writing turn:\*\*\s*(.*)$', text, re.M)
    first = re.match(r'[`*_]*([A-Za-z][A-Za-z0-9-]*)', turn.group(1).strip()) if turn else None
    state['turn'] = first.group(1).lower() if first else ''
    accepted = re.search(r'^- \*\*Accepted head:\*\*\s*(.*)$', text, re.M)
    state['accepted_line'] = accepted is not None
    value = plain(accepted.group(1)) if accepted else ''
    # Only a commit id at the start of the value is an acceptance; "none yet, ... on 6c777d4" is not.
    commit = re.match(r'^([0-9a-f]{7,40})\b', value)
    state['accepted'] = commit.group(1) if commit else ''
    state['accepted_unreadable'] = bool(value) and not commit and not re.match(r'^none\b', value, re.I)
    state['head'] = ''
    if state['branch']:
        row = re.search(r'^\|\s*`%s`\s*\|\s*([^|]*)\|' % re.escape(state['branch']), text, re.M)
        commit = re.match(r'^([0-9a-f]{7,40})\b', plain(row.group(1))) if row else None
        state['head'] = commit.group(1) if commit else ''
    state['closed_for_merge'] = bool(re.search(r'^- \*\*Status:\*\*\s*DONE, closed for merge\b', text, re.M))
    state['waiting'] = ''
    section = re.search(r'^## Next action\s*\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    first = next((line for line in (section.group(1).splitlines() if section else []) if line.strip()), '')
    waiting = re.match(r'^\s*(?:[0-9]+\.|[-*])?\s*[`*_]*(NEEDS USER|SCOPE CLOSED)\b', first)
    if waiting:
        state['waiting'] = waiting.group(1)
    return state


def alignment_state(folder):
    return alignment_of(read(folder / 'ALIGNMENT.md'))


def alignment_of(text):
    status = re.search(r'^Status:\s*(.*)$', text, re.M)
    value = plain(status.group(1)) if status else ''
    word = re.match(r'(REQUESTED|BRIEFED|CONFIRMED)\b', value)
    roles = re.search(r'^Context holder:\s*(.*?)\s*·\s*Receiver:\s*(.*)$', text, re.M)
    names = []
    if roles:
        for raw in roles.groups():
            # "claude" or "claude (its tool)"; a placeholder such as "<claude | codex>" names no one.
            match = re.match(r'^([A-Za-z][A-Za-z0-9-]*)\s*(\([^)]*\))?\s*$', plain(raw))
            names.append(match.group(1).lower() if match else '')
    verdict = re.search(r'^Receiver verdict:\s*(.*)$', text, re.M)
    return {'status': word.group(1) if word else '', 'raw': value,
            'holder': names[0] if names else '', 'receiver': names[1] if len(names) > 1 else '',
            'verdict': bool(verdict) and bool(re.match(r'^CONFIRMED\b', plain(verdict.group(1))))}


def open_findings(folder):
    """Rows in every table of FINDINGS.md whose first column is ID."""
    rows, table, header = 0, False, False
    for line in live_lines(read(folder / 'FINDINGS.md')):
        if not line.strip().startswith('|'):
            table = header = False
            continue
        cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
        if not header:
            header, table = True, bool(cells) and plain(cells[0]) == 'ID'
            continue
        if not table or all(re.match(r'^:?-+:?$', cell) for cell in cells if cell):
            continue
        if cells and cells[0]:
            rows += 1
    return rows


def rounds(folder):
    found = []
    base = folder / 'rounds'
    if base.is_dir():
        for entry in base.iterdir():
            match = re.match(r'^R([0-9]+)$', entry.name)
            if match and entry.is_dir():
                found.append((int(match.group(1)), entry))
    return sorted(found)


def packets(folder):
    for number, directory in rounds(folder):
        for entry in sorted(directory.iterdir()):
            if entry.is_file() and entry.suffix == '.md':
                yield number, entry.stem, entry


def is_wip(packet):
    return re.search(r'^Status:\s*WIP\b', read(packet), re.M) is not None


# ---------------------------------------------------------------- links

def anchors(path):
    found, counts = set(), {}
    for line in live_lines(read(path)):
        heading = re.match(r'^#{1,6}\s+(.+?)\s*#*\s*$', line)
        if heading:
            name = re.sub(r'[^\w\- ]', '', heading.group(1).lower()).replace(' ', '-')
            count = counts.get(name, 0)
            found.add(name if not count else '%s-%d' % (name, count))
            counts[name] = count + 1
    return found


def exists_exactly(top, parts):
    """The path exists with exactly this spelling, also on a disk that ignores letter case."""
    here = top
    for part in parts:
        if part not in os.listdir(str(here)):
            return False
        here = here / part
    return True


def link_targets(line):
    for match in re.finditer(r'!?\[[^\]\n]*\]\(([^)\n]*)\)', line):
        yield match.group(1)
    for match in re.finditer(r'<([A-Za-z][A-Za-z0-9+.-]*:[^>\s]+)>', line):
        yield match.group(1)
    for match in re.finditer(r'<(?:a|img|source|link|video|audio)\b[^>]*?\b(?:href|src)\s*=\s*["\']([^"\']*)["\']',
                             line, re.I):
        yield match.group(1)
    # A reference definition: a destination, an optional quoted title, nothing else (not a footnote).
    definition = re.match(r'^ {0,3}\[(?!\^)[^\]]+\]:\s*(<[^>]*>|\S+)\s*(?:"[^"]*"|\'[^\']*\'|\([^)]*\))?\s*$', line)
    if definition:
        yield definition.group(1)


def link_problems(project, folder):
    problems = []
    record = project.record()
    top = Path(os.path.realpath(str(project.top)))
    for path in sorted(folder.rglob('*.md')):
        where = display(project, path)
        for line in live_lines(read(path)):
            line = re.sub(r'`[^`\n]*`', '', line)
            for raw in link_targets(line):
                target = raw.strip()
                if target.startswith('<') and '>' in target:
                    target = target[1:target.index('>')]
                elif target:
                    target = target.split()[0]
                if not target:
                    problems.append('%s: a link with no target' % where)
                    continue
                if re.match(r'^file:', target, re.I):
                    problems.append('%s: link %s points into this machine\'s files; link inside the repository, '
                                    'relative to the file' % (where, target))
                    continue
                # A web or mail address is not checked; "notes.md:12" is a file name with a line number, not an address.
                if re.match(r'^(https?://|mailto:|tel:|data:)', target, re.I):
                    continue
                if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*://', target):
                    problems.append('%s: link %s opens something on this machine that another clone cannot follow'
                                    % (where, target))
                    continue
                local, _, fragment = target.partition('#')
                local = local.split('?')[0]
                if local.startswith('/'):
                    problems.append('%s: link %s uses an absolute path; link inside the repository, relative '
                                    'to the file' % (where, target))
                    continue
                resolved = Path(os.path.normpath(str(path.parent / unquote(local)))) if local else path
                try:
                    inside = resolved.relative_to(project.top)
                except ValueError:
                    problems.append('%s: link %s leaves the repository' % (where, target))
                    continue
                if not resolved.exists() or not exists_exactly(project.top, inside.parts):
                    problems.append('%s: link %s points to nothing (check the spelling and letter case; a line '
                                    'number belongs after the link, not inside it)' % (where, target))
                    continue
                try:
                    Path(os.path.realpath(str(resolved))).relative_to(top)
                except ValueError:
                    problems.append('%s: link %s leaves the repository through a symbolic link' % (where, target))
                    continue
                if inside.parts and git(project.top, 'check-ignore', '-q', '--', inside.as_posix(), check=False).returncode == 0:
                    problems.append('%s: link %s points to a file the repository ignores, which another clone does '
                                    'not have' % (where, target))
                    continue
                pieces = inside.parts
                if (len(pieces) > 1 and pieces[0] == RECORD and pieces[1] != folder.name
                        and not pieces[1].endswith(DONE) and (record / pieces[1] / 'CURRENT.md').is_file()):
                    problems.append('%s: link %s points into the open folder of another branch, which closing '
                                    'renames; name it in text instead' % (where, target))
                if fragment and resolved.suffix == '.md' and unquote(fragment) not in anchors(resolved):
                    problems.append('%s: link %s names a heading that does not exist' % (where, target))
    return problems


# ---------------------------------------------------------------- check

class Report:
    def __init__(self):
        self.fails, self.warns, self.notes = [], [], []

    def fail(self, text):
        self.fails.append(text)

    def warn(self, text):
        self.warns.append(text)

    def note(self, text):
        self.notes.append(text)

    def show(self):
        for text in self.notes:
            print('OK: ' + text)
        for text in self.warns:
            print('WARN: ' + text)
        for text in self.fails:
            print('FAIL: ' + text)
        print('Result: %d failure%s, %d warning%s.' % (len(self.fails), '' if len(self.fails) == 1 else 's',
                                                      len(self.warns), '' if len(self.warns) == 1 else 's'))
        return 1 if self.fails else 0


def listed(items):
    return ', '.join(items[:8]) + (' ...' if len(items) > 8 else '')


def product_changes(project, since):
    return [line for line in out(project.top, 'diff', '--name-only', since, 'HEAD', '--', '.',
                                 ':(exclude)%s' % RECORD).splitlines() if line]


def uncommitted_product(project):
    return [line[3:] for line in git(project.top, 'status', '--porcelain', '-uall', '--', '.',
                                     ':(exclude)%s' % RECORD).stdout.splitlines() if line]


def last_product_commit(project):
    return out(project.top, 'rev-list', '-1', 'HEAD', '--', '.', ':(exclude)%s' % RECORD)


def resolve_commit(project, commit):
    probe = git(project.top, 'rev-parse', '-q', '--verify', commit + '^{commit}', check=False)
    return probe.stdout.strip() if probe.returncode == 0 else ''


def is_ancestor(project, older, newer):
    return succeeds(project.top, 'merge-base', '--is-ancestor', older, newer)


def opening_head(project, folder):
    """The commit the branch stood at when its folder was opened (start records it in CURRENT.md's first
    line); failing that, where the branch left the default branch; '' when neither is known."""
    match = re.search(r'^Branch `[^`]+` · opened [^\n]*? at `?([0-9a-f]{7,40})\b', read(folder / 'CURRENT.md'), re.M)
    commit = resolve_commit(project, match.group(1)) if match else ''
    if commit and is_ancestor(project, commit, 'HEAD'):
        return commit
    # A rebase gave the branch new commit ids: peer coding began just before the commit that added the folder.
    added = git(project.top, 'log', '--no-show-signature', '--format=%H', '--reverse', '--no-renames',
                '--diff-filter=A', 'HEAD', '--', '%s/%s/CURRENT.md' % (RECORD, folder.name), check=False).stdout.split()
    if added:
        return resolve_commit(project, added[0] + '^') or added[0]
    for ref in project.default_refs():
        base = git(project.top, 'merge-base', 'HEAD', ref, check=False).stdout.strip()
        if base:
            return base
    return ''


def aligned_in(project, commit, relative):
    shown = git(project.top, 'show', '%s:%s' % (commit, relative), check=False)
    return confirmed(alignment_of(shown.stdout)) if shown.returncode == 0 else None


def unconfirmed_since(project, folder):
    """The commit from which ALIGNMENT.md has not been CONFIRMED: where it last left CONFIRMED in the
    branch's history, or where the branch stood when the folder was opened; HEAD when the change is not
    committed yet."""
    relative = '%s/%s/ALIGNMENT.md' % (RECORD, folder.name)
    history = git(project.top, 'rev-list', 'HEAD', '--', relative, check=False).stdout.split()
    left = ''
    for commit in history:  # newest first
        state = aligned_in(project, commit, relative)
        if state:
            # Measured from just before the commit that left CONFIRMED, so its own product changes count.
            return (resolve_commit(project, left + '^') or left) if left else out(project.top, 'rev-parse', 'HEAD')
        if state is False:
            left = commit
    return opening_head(project, folder)


def own_product_changes(project, since):
    """Product files changed by this branch's own commits after `since`, leaving out a merge of the default branch."""
    if not is_ancestor(project, since, 'HEAD'):
        return []
    # The branch's own commits: since `since`, and not on the project's default branch (here, on origin, or on
    # the remote the local default branch tracks). Both assistants' commits count, whichever way they arrived.
    files = set(out(project.top, 'log', '--no-show-signature', '--no-merges', '--format=', '--name-only',
                    '%s..HEAD' % since, *(not_default(project) + ['--', '.', ':(exclude)%s' % RECORD])).splitlines())
    for merge in out(project.top, 'rev-list', '--merges', '%s..HEAD' % since, *not_default(project)).split():
        files.update(line for line in merge_changes(project, merge) if not line.startswith(RECORD + '/'))
    return sorted(line for line in files if line)


def not_default(project):
    refs = project.default_refs()
    return ['--not'] + refs if refs else []


def elsewhere_default(project, commit):
    """Another remote's branch named like the default branch that holds the commit, or ''."""
    if not project.default:
        return ''
    for ref in git(project.top, 'for-each-ref', '--format=%(refname)', 'refs/remotes', check=False).stdout.split():
        if ref.endswith('/' + project.default) and ref not in project.default_refs() and is_ancestor(project, commit, ref):
            return ref[len('refs/remotes/'):]
    return ''


def merge_changes(project, merge):
    """A merge commit's own changes: what differs from git's automatic merge (a conflict resolution, or an edit
    made in the merge). An older git without that comparison counts every file that differs from all parents."""
    own = git(project.top, 'show', '--no-show-signature', '--remerge-diff', '--format=', '--name-only', merge,
              check=False)
    if own.returncode != 0:
        own = git(project.top, 'diff-tree', '-r', '--cc', '--name-only', '--no-commit-id', merge)
    return [line for line in own.stdout.splitlines() if line]


def attributed(folder, commit, names):
    """Whether a packet of this folder says who made the commit: a line with its id (7 or more characters) and
    "made by <name>", the name one of the peers or owner."""
    ids = re.compile(r'\b([0-9a-f]{7,40})\b')
    for _, _, packet in packets(folder):
        for line in read(packet).splitlines():
            maker = re.search(r'\bmade by\s+`?([A-Za-z][A-Za-z0-9-]*)', line, re.I)
            if maker and maker.group(1).lower() in names and any(commit.startswith(found) for found in ids.findall(line)):
                return True
    return False


def peer_line_names(message):
    """The names on a commit message's Peer lines: `Peer: claude`, `Peer: claude (its tool)`, `Peer: claude, codex`."""
    names = []
    for value in re.findall(r'^peer:[ \t]*(.*)$', message, re.M | re.I):
        value = re.sub(r'\([^)]*\)', ' ', value)
        for part in re.split(r',|;|&|\band\b', value):
            part = part.strip()
            if part:
                names.append(part.lower() if re.match(r'^[A-Za-z][A-Za-z0-9-]*$', part) else '?' + part)
    return names


def unnamed_commits(project, folder, peers):
    """This branch's own commits since its folder was opened whose message names no assistant with a Peer line:
    (commit, the names it gives, whether it is already on the branch's own remote branch)."""
    since = opening_head(project, folder)
    if not since or not is_ancestor(project, since, 'HEAD'):
        return []
    remote, tracked = upstream_of(project)
    pushed = 'refs/remotes/%s/%s' % (remote, tracked) if remote and remote != '.' and tracked == project.branch else ''
    pushed = pushed if pushed and project.ref_exists(pushed) else ''
    raw = git(project.top, 'log', '--no-show-signature', '--format=%H%x00%P%x00%B%x1e', '%s..HEAD' % since,
              *not_default(project)).stdout
    found = []
    for entry in raw.split('\x1e'):
        fields = entry.strip('\n').split('\x00')
        if len(fields) < 3 or not fields[0]:
            continue
        commit, parents, message = fields[0], fields[1].split(), fields[2]
        names = peer_line_names(message)
        if names and all(name in peers + ['owner'] for name in names):
            continue
        if len(parents) > 1 and not merge_changes(project, commit):
            continue  # a merge that only brings in the default branch's work
        found.append((commit, names, bool(pushed) and is_ancestor(project, commit, pushed)))
    return found


def confirmed(alignment):
    """CONFIRMED by a named receiver of a named holder, with the receiver's verdict written."""
    return (alignment['status'] == 'CONFIRMED' and bool(alignment['holder']) and bool(alignment['receiver'])
            and alignment['verdict'])


def upstream_of(project):
    """The branch's remote and the remote branch it tracks, or ('', '') when it tracks nothing."""
    remote = git(project.top, 'config', '--get', 'branch.%s.remote' % project.branch, check=False).stdout.strip()
    merge = git(project.top, 'config', '--get', 'branch.%s.merge' % project.branch, check=False).stdout.strip()
    return remote, merge[len('refs/heads/'):] if merge.startswith('refs/heads/') else merge


def check_folder(project, folder, peers, report, you=''):
    name = display(project, folder)
    for required in ('CURRENT.md', 'ALIGNMENT.md', 'FINDINGS.md'):
        if not (folder / required).is_file():
            report.fail('%s has no %s' % (name, required))
    if report.fails:
        return
    current, alignment = current_state(folder), alignment_state(folder)
    if current['status'] != 'ACTIVE':
        report.fail('%s: CURRENT.md Status is %s; an open folder is ACTIVE, and a finished one is closed '
                    'with close' % (name, current['status'] or 'missing'))
    if alignment['status'] == '' and not alignment['raw'].startswith('<'):
        report.fail('%s: ALIGNMENT.md Status must be REQUESTED, BRIEFED or CONFIRMED' % name)
    for role in ('holder', 'receiver'):
        if alignment[role] and alignment[role] not in peers:
            report.fail('%s: ALIGNMENT.md names %s as %s; the peers are %s' % (name, alignment[role], role, ' and '.join(peers)))
    if alignment['holder'] and alignment['holder'] == alignment['receiver']:
        report.fail('%s: ALIGNMENT.md names the same assistant as holder and receiver' % name)
    if alignment['status'] == 'CONFIRMED' and not (alignment['holder'] and alignment['receiver'] and alignment['verdict']):
        report.fail('%s: ALIGNMENT.md is CONFIRMED without both roles named and a Receiver verdict that begins '
                    'CONFIRMED; only the receiver confirms, after verifying the brief' % name)
    if current['accepted_unreadable']:
        report.fail('%s: the Accepted head line must start with the accepted commit id, or say none' % name)
    if alignment['status'] and current['alignment'] and alignment['status'] != current['alignment']:
        report.warn('%s: CURRENT.md says alignment %s, ALIGNMENT.md says %s' % (name, current['alignment'], alignment['status']))
    if current['turn'] and current['turn'] != 'none':
        if current['turn'] not in peers:
            report.fail('%s: CURRENT.md gives the writing turn to %s; the peers are %s' % (name, current['turn'], ' and '.join(peers)))
        elif not confirmed(alignment):
            report.fail('%s: CURRENT.md gives %s the writing turn before ALIGNMENT.md is CONFIRMED' % (name, current['turn']))
    if current['next_move'] and current['next_move'] not in peers + ['none']:
        report.fail('%s: CURRENT.md gives the next move to %s; the peers are %s' % (name, current['next_move'], ' and '.join(peers)))
    if not current['accepted_line']:
        report.warn('%s: CURRENT.md has no Accepted head line; closing for a merge needs one (the accepted '
                    'commit and who accepted it)' % name)

    head = resolve_commit(project, current['head']) if current['head'] else ''
    if not current['head']:
        report.fail('%s: CURRENT.md records no last product commit for `%s` in its Heads table' % (name, current['branch']))
    elif not head:
        report.fail('%s: the recorded last product commit %s does not exist here; pull, or correct CURRENT.md' % (name, current['head']))
    elif not succeeds(project.top, 'merge-base', '--is-ancestor', head, 'HEAD'):
        report.fail('%s: the recorded last product commit %s is not in this branch\'s history' % (name, current['head']))
    else:
        changed = product_changes(project, head)
        if changed:
            report.fail('%s: product files changed after the recorded last product commit %s, and no hand-over '
                        'recorded them: %s' % (name, current['head'], listed(changed)))
    if not confirmed(alignment):
        since = unconfirmed_since(project, folder)
        early = own_product_changes(project, since) if since else []
        if early:
            report.fail('%s: product files changed while ALIGNMENT.md is not CONFIRMED: %s. Product work waits for '
                        'the receiver\'s confirmation; a merge of the default branch is not counted'
                        % (name, listed(early)))
    dirty = uncommitted_product(project)
    if dirty:
        report.fail('uncommitted product changes in this worktree: %s. Commit them on your writing turn, '
                    'or leave them out; never hand them over' % listed(dirty))
    for commit, names, pushed in unnamed_commits(project, folder, peers):
        wrong = [value.lstrip('?') for value in names if value not in peers + ['owner']]
        given = ('its Peer line names %s, which is not %s or owner' % (', '.join(wrong), ' or '.join(peers))) if names \
            else 'it has no Peer: line'
        if pushed and attributed(folder, commit, peers + ['owner']):
            report.warn('%s: commit %s does not name who made it (%s); a packet says who did' % (name, commit[:12], given))
        elif pushed:
            report.fail('%s: commit %s does not name who made it (%s). It is already pushed and history is never '
                        'rewritten, so write in your packet: Commit %s made by <name>' % (name, commit[:12], given, commit[:12]))
        else:
            hint = ''
            other = elsewhere_default(project, commit)
            if other:
                hint = (' If it came to this branch from the default branch on %s, bring your local %s up to date '
                        'with it and check again.' % (other, project.default))
            report.fail('%s: commit %s does not name who made it (%s). Add a line Peer: <name> to its message before '
                        'it is pushed: git commit --amend for the last commit, otherwise reword it.%s'
                        % (name, commit[:12], given, hint))

    for number, peer, packet in packets(folder):
        if peer not in peers:
            report.fail('%s is named for %s; packets are named for a peer: %s' % (display(project, packet), peer, ' or '.join(peers)))
        elif is_wip(packet):
            report.note('%s is still WIP' % display(project, packet))
    for number, directory in rounds(folder):
        for entry in directory.iterdir():
            if entry.name == 'evidence' and entry.is_dir():
                for owner in entry.iterdir():
                    if owner.name not in peers:
                        report.fail('%s: evidence belongs under evidence/<peer>/' % display(project, owner))
            elif not (entry.is_file() and entry.suffix == '.md'):
                report.warn('%s is not a packet or an evidence folder' % display(project, entry))

    for problem in link_problems(project, folder):
        report.fail(problem)
    for path in sorted(folder.rglob('*')):
        if path.is_symlink():
            report.fail('%s is a symbolic link; the record keeps the file itself, which every clone can read'
                        % path.relative_to(project.top).as_posix())
    files = [str(path.relative_to(project.top)) for path in folder.rglob('*') if path.is_file()]
    if files:
        ignored = git(project.top, 'check-ignore', '--', *files, check=False).stdout.split('\n')
        for path in [line for line in ignored if line]:
            report.fail('%s is excluded by the repository\'s ignore rules, so it would never be committed; '
                        'rename it' % path)
    if you and you not in peers:
        report.fail('--as %s is not one of the peers: %s' % (you, ' and '.join(peers)))

    summary = 'alignment %s' % (alignment['status'] or 'not started')
    if current['turn'] and current['turn'] != 'none':
        summary += ', writing turn: %s' % current['turn']
    elif current['next_move']:
        summary += ', next move: %s' % current['next_move']
    latest = rounds(folder)
    summary += ', latest round R%d' % latest[-1][0] if latest else ', no rounds yet'
    if head:
        summary += ', last product commit %s' % head[:12]
    report.note('%s (%s)' % (name, summary))


def check_closed(project, folder, report, peers):
    name = display(project, folder)
    report.note('%s is closed: its branch finished. New work gets a new branch' % name)
    if git(project.top, 'status', '--porcelain', '-uall', '--', RECORD).stdout.strip():
        report.fail('%s/ has uncommitted changes: commit the close (with your Peer line) before the merge' % RECORD)
    for commit, names, pushed in unnamed_commits(project, folder, peers):
        if not (pushed and attributed(folder, commit, peers + ['owner'])):
            report.fail('%s: commit %s does not name who made it; add a Peer line before it is pushed, or name it in '
                        'a packet if it already is' % (name, commit[:12]))
    current = current_state(folder)
    if not current['closed_for_merge']:
        return
    accepted = resolve_commit(project, current['accepted']) if current['accepted'] else ''
    if not accepted:
        report.fail('%s is closed for merge without an accepted head' % name)
    elif not is_ancestor(project, accepted, 'HEAD'):
        report.fail('%s: its accepted head %s is not in this branch\'s history' % (name, current['accepted']))
    else:
        changed = product_changes(project, accepted)
        if changed:
            report.fail('%s: product files changed after the accepted head of the close: %s. Reopen it (close --reopen), '
                        'have the change reviewed, and close again' % (name, listed(changed)))
    dirty = uncommitted_product(project)
    if dirty:
        report.fail('uncommitted product changes in this worktree: %s' % listed(dirty))


def other_entries(project, report, own):
    record = project.record()
    if not record.is_dir():
        return
    leftovers = [entry.name for entry in sorted(record.iterdir())
                 if entry.name in ('README.md', 'PROTOCOL.md', 'templates')]
    if leftovers:
        report.warn('%s/: %s hold an earlier copy of peer-coding rules; the framework\'s playbook is the one '
                    'that applies, so remove them in a change of their own' % (RECORD, ', '.join(leftovers)))
    for entry in sorted(record.iterdir()):
        if not entry.is_dir() or entry.name.endswith(DONE) or entry == own or entry.name in RESERVED:
            continue
        branch = recorded_branch(read(entry / 'CURRENT.md'))
        if not branch or branch.startswith('<'):
            continue
        tip = next((ref for ref in ('refs/heads/' + branch, 'refs/remotes/origin/' + branch) if project.ref_exists(ref)), '')
        if not tip:
            report.warn('%s: its branch %s no longer exists here. If it merged or was abandoned, close the '
                        'folder from this branch: close --folder %s' % (display(project, entry), branch, entry.name))
            continue
        target = next(iter(project.default_refs()), '')
        if target and branch != project.default and succeeds(project.top, 'merge-base', '--is-ancestor', tip, target):
            report.warn('%s: its branch %s is merged into %s but the folder is still open; close it from this '
                        'branch: close --folder %s --merged <ref>' % (display(project, entry), branch, project.default, entry.name))


def command_check(project, args):
    report = Report()
    line = references_line(project)
    has_settings = (project.record() / SETTINGS).is_file()
    if line is not None and has_settings and re.match(r'^none\b', line, re.I):
        report.warn('References.md says Peer coding: %s while %s/%s exists; the owner\'s decision settles which, so '
                    'remove the file or record it on the line' % (line, RECORD, SETTINGS))
    try:
        peers, _ = settings_of(project)
    except Refusal as refusal:
        report.fail(str(refusal))
        other_entries(project, report, None)
        return report.show()
    report.note('%s/%s: peers %s' % (RECORD, SETTINGS, ' and '.join(peers)))
    you = (args.you or '').lower()
    own = None
    if not project.branch:
        report.fail('detached HEAD: check out the branch for this work')
    elif project.branch == project.default:
        report.note('%s is the default branch; branch folders live on their own branches' % project.branch)
    else:
        own, state = branch_folder(project, project.branch)
        if state == 'done' and own.is_dir():
            check_closed(project, own, report, peers)
        elif state == 'done':
            report.note('the closed folder of branch %s is on %s: this branch already merged' % (project.branch, project.default))
        elif state == 'none':
            report.fail('no peer-coding folder for branch %s; open one with start' % project.branch)
        else:
            check_folder(project, own, peers, report, you)
    other_entries(project, report, own)
    return report.show()


def command_which(project, args):
    if not project.branch:
        raise Refusal('detached HEAD: check out the branch for this work')
    folder, state = branch_folder(project, project.branch)
    print('%s %s' % (display(project, folder), state))
    return 0


# ---------------------------------------------------------------- setup and start

def render(template, destination, values):
    if not (TEMPLATES / template).is_file():
        raise Refusal('the engine\'s templates/peer-coding/%s is missing; update or reinstall the framework' % template)
    text = read(TEMPLATES / template)
    for key, value in values.items():
        text = text.replace('{{%s}}' % key, value)
    if destination.exists():
        raise Refusal('refusing to overwrite %s' % destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    write(destination, text)


def playbook_link(project, source_dir):
    target = project.engine / PLAYBOOK
    try:
        target.relative_to(project.top)
    except ValueError:
        return "the framework's %s" % PLAYBOOK.as_posix()
    return '[%s](%s)' % (PLAYBOOK.as_posix(), Path(os.path.relpath(str(target), str(source_dir))).as_posix())


def ignored_by(project, path):
    rule = git(project.top, 'check-ignore', '-v', '--no-index', '--', path, check=False)
    return rule.stdout.split('\t')[0] if rule.returncode == 0 else ''


def command_setup(project, args):
    record = project.record()
    if record.is_symlink() or (record.exists() and not record.is_dir()):
        raise Refusal('%s exists and is not a plain folder' % record)
    path = record / SETTINGS
    if path.exists():
        problems = settings_problems(path)
        print('%s/%s already exists%s' % (RECORD, SETTINGS, ': ' + '; '.join(problems) if problems else ' and is complete'))
        return 1 if problems else 0
    rule = ignored_by(project, '%s/%s' % (RECORD, SETTINGS))
    if rule:
        raise Refusal('%s/%s would be excluded by the repository\'s ignore rules (%s); change that rule first' % (RECORD, SETTINGS, rule))
    render(SETTINGS, path, {'PLAYBOOK': playbook_link(project, record)})
    print('Created %s/%s. Fill each line with the owner\'s answers and what you verified about this project, '
          'record it on References.md\'s Peer coding line when the project has one, and commit it.' % (RECORD, SETTINGS))
    return 0


def command_start(project, args):
    peers, fields = settings_of(project)
    you = args.you.lower()
    if you not in peers:
        raise Refusal('--as %s is not one of the peers: %s' % (you, ' and '.join(peers)))
    if not project.branch:
        raise Refusal('detached HEAD: check out the branch for this work')
    if project.default and project.branch == project.default:
        raise Refusal('%s is the default branch. Peer work runs on a branch of its own, for example in a new '
                      'worktree: git worktree add ../<folder> -b <branch>' % project.branch)
    if not project.default:
        print('WARN: the default branch could not be determined (no origin HEAD, main or master); '
              'make sure %s is not the branch releases come from' % project.branch)
    if project.branch.endswith(DONE):
        raise Refusal('the branch name ends in %s, which marks closed folders; use another branch name' % DONE)
    if re.search(r'[`|]', project.branch):
        raise Refusal('the branch name contains ` or |, which the record\'s tables cannot hold; rename the branch')
    record = project.record()
    if record.is_symlink() or (record.exists() and not record.is_dir()):
        raise Refusal('%s exists and is not a plain folder' % record)
    folder, state = branch_folder(project, project.branch)
    if state == 'active':
        print('%s is already open for branch %s: resume it (development/PEER-CODING.md, Resume)' % (display(project, folder), project.branch))
        return 3
    if state == 'done':
        if folder.is_dir():
            raise Refusal('%s is closed; new work gets a new branch (or reopen it with close --reopen when its '
                          'merge did not happen)' % display(project, folder))
        raise Refusal('%s is closed on %s: this branch name was used for work that merged; new work gets a new '
                      'branch' % (display(project, folder), project.default))
    if folder.name.endswith(DONE):
        raise Refusal('the branch name gives the folder name %s, which marks closed folders; use another branch name' % folder.name)
    if len(folder.name.encode('utf-8')) > 200:
        raise Refusal('the branch name is too long for a folder name; use a shorter branch name')
    for probe in ('CURRENT.md', 'rounds/R1/%s.md' % you, 'rounds/R1/evidence/%s/output.txt' % you):
        path = '%s/%s/%s' % (RECORD, folder.name, probe)
        rule = ignored_by(project, path)
        if rule:
            raise Refusal('%s would be excluded by the repository\'s ignore rules (%s), so the record could '
                          'not be committed; change that rule first' % (path, rule))
    rule = ignored_by(project, '%s/%s%s/CURRENT.md' % (RECORD, folder.name, DONE))
    if rule:
        raise Refusal('%s/%s%s would be excluded by the repository\'s ignore rules (%s); change that rule first'
                      % (RECORD, folder.name, DONE, rule))
    version = project.version()
    values = {
        'FOLDER': '%s/%s' % (RECORD, folder.name),
        'BRANCH': project.branch,
        'DATE': datetime.date.today().isoformat(),
        'BY': you,
        'PEERS': ' | '.join(peers),
        'PLAYBOOK': playbook_link(project, folder) + (' (framework revision %s)' % version if version else ''),
        'HEAD': out(project.top, 'rev-parse', 'HEAD'),
        'OPENED': out(project.top, 'rev-parse', '--short=12', 'HEAD'),
        'ROLES': plain(fields['Who writes']),
    }
    for template in ('CURRENT.md', 'ALIGNMENT.md', 'FINDINGS.md'):
        render(template, folder / template, values)
    remote, tracked = upstream_of(project)
    if remote and tracked != project.branch:
        print('WARN: the branch tracks %s/%s; set its own upstream when you first push: git push -u %s %s'
              % (remote, tracked, remote if remote != '.' else '<remote>', project.branch))
    print('Created %s for branch %s.' % (display(project, folder), project.branch))
    print('Who writes new work (%s/%s): %s' % (RECORD, SETTINGS, values['ROLES']))
    print('Every commit names its assistant: git add -- %s && git commit -m "<message>" -m "Peer: %s" -- %s'
          % (RECORD, you, RECORD))
    print('Next: decide whether you hold the context for this work and fill ALIGNMENT.md '
          '(development/PEER-CODING.md, Start a branch).')
    return 0


def own_folder(project, required=True):
    if not project.branch:
        raise Refusal('detached HEAD: check out the branch for this work')
    folder, state = branch_folder(project, project.branch)
    if required and state != 'active':
        raise Refusal('no open peer-coding folder for branch %s%s' % (project.branch, '' if state == 'none' else
                      ' (%s is closed)' % display(project, folder)))
    return folder


# ---------------------------------------------------------------- packet

def relative_link(source, target, label):
    return '[%s](%s)' % (label, Path(os.path.relpath(str(target), str(source.parent))).as_posix())


def peer_names(project, you):
    peers, fields = settings_of(project)
    you = you.lower()
    if you not in peers:
        raise Refusal('--as %s is not one of the peers: %s' % (you, ' and '.join(peers)))
    return peers, fields, you, [peer for peer in peers if peer != you][0]


def command_packet(project, args):
    peers, _, you, other = peer_names(project, args.you)
    folder = own_folder(project)
    if not confirmed(alignment_state(folder)):
        raise Refusal('ALIGNMENT.md is not CONFIRMED (by the receiver, with both roles named and its verdict '
                      'written); alignment moves happen in ALIGNMENT.md, not in packets')
    existing = rounds(folder)
    number = existing[-1][0] if existing else 1
    if existing and (existing[-1][1] / (you + '.md')).is_file():
        mine = existing[-1][1] / (you + '.md')
        if is_wip(mine):
            print('Your packet %s is still WIP: continue it.' % display(project, mine))
            return 0
        number += 1
    path = folder / 'rounds' / ('R%d' % number) / (you + '.md')
    incoming = None
    for round_number, directory in reversed(rounds(folder)):
        if round_number <= number and (directory / (other + '.md')).is_file():
            incoming = (directory / (other + '.md'), 'R%d/%s.md' % (round_number, other))
            break
    values = {
        'FOLDER': '%s/%s' % (RECORD, folder.name),
        'ROUND': str(number),
        'BY': you,
        'OTHER': other,
        'BRANCH': project.branch,
        'INCOMING': relative_link(path, *incoming) if incoming else 'none: the first packet of this branch',
        'CURRENT': relative_link(path, folder / 'CURRENT.md', 'CURRENT.md'),
    }
    render('PACKET.md', path, values)
    print('Opened %s (WIP). Save command output under %s/.' % (display(project, path),
          display(project, path.parent / 'evidence' / you)))
    return 0


# ---------------------------------------------------------------- cue

def command_cue(project, args):
    peers, fields, you, other = peer_names(project, args.you)
    folder = own_folder(project)
    report = Report()
    check_folder(project, folder, peers, report, you)
    if report.fails:
        report.show()
        raise Refusal('the checks above must pass before handing over')
    for text in report.warns:
        print('WARN: ' + text)
    relative = '%s/%s' % (RECORD, folder.name)
    if git(project.top, 'status', '--porcelain', '-uall', '--', RECORD).stdout.strip():
        raise Refusal('%s/ has uncommitted changes; commit it first: git add -- %s && git commit -m '
                      '"<message>" -m "Peer: %s" -- %s' % (RECORD, RECORD, you, RECORD))
    wip = [display(project, packet) for _, _, packet in packets(folder) if is_wip(packet)]
    if wip:
        raise Refusal('a packet is still WIP: %s' % ', '.join(wip))
    current, alignment = current_state(folder), alignment_state(folder)
    opened = opening_head(project, folder)
    note = ''
    if confirmed(alignment) and opened and product_changes(project, opened) and not current['waiting']:
        mine = [packet for _, peer, packet in packets(folder) if peer == you]
        written = out(project.top, 'rev-list', '-1', 'HEAD', '--', display(project, mine[-1])) if mine else ''
        if not written or not is_ancestor(project, last_product_commit(project), written):
            # Returning the move after recording the owner's answer needs no packet; a turn that reviewed or
            # changed product work does.
            note = ('NOTE: no packet of yours was written after the last product commit. If this turn reviewed or '
                    'changed product work, write it first (packet --as %s).' % you)
    if current['waiting']:
        recipient = label = ''
    elif not confirmed(alignment):
        recipient, label = current['next_move'], 'ALIGN %s' % (alignment['status'] or 'started')
    else:
        recipient = current['turn'] if current['turn'] != 'none' else ''
        mine = [number for number, peer, _ in packets(folder) if peer == you]
        label = 'no packet' if note else ('R%d' % mine[-1] if mine else 'ALIGN CONFIRMED')
    if not current['waiting'] and recipient != other:
        raise Refusal('CURRENT.md gives the next move to %s. Before handing over, give it to %s; or write NEEDS USER '
                      'or SCOPE CLOSED as the Next action instead' % (recipient or 'no one', other))
    remote, tracked = upstream_of(project)
    if not pushes(fields):
        print('NOTE: %s/%s says Push: no, so the other assistant must work in this same repository.' % (RECORD, SETTINGS))
    elif not out(project.top, 'remote'):
        raise Refusal('%s/%s says Push: yes, but this repository has no remote. Add the remote, or set Push: no '
                      '(a technical choice under PROFILE.md\'s decision authority, recorded at the decision location)'
                      % (RECORD, SETTINGS))
    elif not remote or remote == '.' or tracked != project.branch:
        raise Refusal('the branch does not track its own remote branch%s: push it with git push -u <remote> %s'
                      % (' (it tracks %s/%s)' % (remote, tracked) if remote else '', project.branch))
    elif not project.ref_exists('refs/remotes/%s/%s' % (remote, tracked)) or \
            not is_ancestor(project, 'HEAD', 'refs/remotes/%s/%s' % (remote, tracked)):
        raise Refusal('push the branch first: %s/%s does not have this commit yet (git push %s %s)'
                      % (remote, tracked, remote, project.branch))
    if current['waiting'] == 'SCOPE CLOSED' and opened and own_product_changes(project, opened):
        accepted = resolve_commit(project, current['accepted']) if current['accepted'] else ''
        if not accepted or not is_ancestor(project, accepted, 'HEAD') or product_changes(project, accepted):
            raise Refusal('SCOPE CLOSED needs the other assistant\'s acceptance of the product changes: the Accepted '
                          'head must cover the last product commit %s' % last_product_commit(project)[:12])
    if note:
        print(note)
    commit = out(project.top, 'rev-parse', '--short=12', 'HEAD')
    if current['waiting'] == 'NEEDS USER':
        print('NEEDS USER · %s · %s@%s' % (relative, project.branch, commit))
    elif current['waiting'] == 'SCOPE CLOSED':
        print('SCOPE CLOSED · %s · %s@%s · awaiting the owner' % (relative, project.branch, commit))
    else:
        print('READY FOR %s · %s %s · %s@%s' % (other.upper(), relative, label, project.branch, commit))
    print('Continue peer coding on branch %s (worktree: %s): read %s there, then %s/CURRENT.md.'
          % (project.branch, project.top, agents_file(project), relative))
    return 0


# ---------------------------------------------------------------- close

def set_status(path, line, turn):
    text = read(path)
    text, count = re.subn(r'^- \*\*Status:\*\*.*$', lambda _: line, text, count=1, flags=re.M)
    if not count:
        text = re.sub(r'\A(# [^\n]*\n)', lambda match: match.group(1) + '\n' + line + '\n', text, count=1)
    text = re.sub(r'^- \*\*Product writing turn:\*\*.*$', lambda _: '- **Product writing turn:** ' + turn, text, count=1, flags=re.M)
    write(path, text)


def command_reopen(project, you, reason):
    folder, state = branch_folder(project, project.branch) if project.branch else (None, 'none')
    if state != 'done':
        raise Refusal('no closed folder for branch %s to reopen' % (project.branch or '(detached HEAD)'))
    if not folder.is_dir():
        raise Refusal('the closed folder of branch %s is on %s: the work merged, and new work gets a new branch'
                      % (project.branch, project.default))
    tip = out(project.top, 'rev-parse', 'HEAD')
    for ref in project.default_refs():
        shown = git(project.top, 'show', '%s:%s/%s/CURRENT.md' % (ref, RECORD, folder.name), check=False)
        if is_ancestor(project, tip, ref) or (shown.returncode == 0 and recorded_branch(shown.stdout) == project.branch):
            raise Refusal('branch %s is already merged into %s: its folder stays closed, and new work gets a new '
                          'branch' % (project.branch, project.default))
    relative = '%s/%s' % (RECORD, folder.name)
    if git(project.top, 'status', '--porcelain', '-uall', '--', relative).stdout.strip():
        raise Refusal('%s has uncommitted changes; commit them first' % relative)
    opened = relative[:-len(DONE)]
    if (project.top / opened).exists():
        raise Refusal('%s already exists' % opened)
    git(project.top, 'mv', '--', relative, opened)
    set_status(project.top / opened / 'CURRENT.md',
               '- **Status:** ACTIVE (reopened %s by %s: %s)' % (datetime.date.today().isoformat(), you, reason),
               'none until the assistants agree who continues')
    git(project.top, 'add', '--', opened + '/CURRENT.md')
    print('Reopened %s -> %s. Record who continues in CURRENT.md, then commit and push it.' % (relative, opened))
    return 0


def command_close(project, args):
    peers, _, you, _ = peer_names(project, args.you)
    if args.reopen is not None:
        if args.folder:
            raise Refusal('--reopen works on this branch\'s own closed folder')
        return command_reopen(project, you, args.reopen)
    record = project.record()
    if not project.branch:
        raise Refusal('detached HEAD: check out the branch the close is committed on')
    if args.folder:
        if '/' in args.folder or args.folder in ('.', '..') or args.folder in RESERVED:
            raise Refusal('--folder takes the name of a branch folder under %s/' % RECORD)
        folder = record / args.folder
        recorded = recorded_branch(read(folder / 'CURRENT.md'))
        if folder == branch_folder(project, project.branch)[0] or recorded == project.branch:
            raise Refusal('%s is this branch\'s own folder: close it without --folder' % display(project, folder))
        tip = next((ref for ref in ('refs/heads/' + recorded, 'refs/remotes/origin/' + recorded)
                    if recorded and project.ref_exists(ref)), '')
        merged = tip and any(is_ancestor(project, tip, ref) for ref in project.default_refs())
        if args.merged is not None and tip and not merged:
            raise Refusal('branch %s still exists and is not merged into %s, so its folder is not left over from a '
                          'merge. After a merge that squashed its commits, delete the branch (here and on the '
                          'remote) and close the folder then' % (recorded, project.default or 'the default branch'))
        own = False
    else:
        folder, own = own_folder(project), True
    name = display(project, folder)
    if folder.name.endswith(DONE):
        raise Refusal('%s is already closed' % name)
    if (record / (folder.name + DONE)).exists():
        raise Refusal('%s%s already exists' % (name, DONE))
    if not (folder / 'CURRENT.md').is_file():
        raise Refusal('no open folder %s' % name)
    relative = '%s/%s' % (RECORD, folder.name)
    if not succeeds(project.top, 'ls-files', '--error-unmatch', '--', relative + '/CURRENT.md'):
        raise Refusal('%s is not committed yet; commit it before closing' % name)
    if git(project.top, 'status', '--porcelain', '-uall', '--', relative).stdout.strip():
        raise Refusal('%s has uncommitted changes; commit them first' % name)
    wip = [display(project, packet) for _, _, packet in packets(folder) if is_wip(packet)]
    if wip:
        raise Refusal('a packet is still WIP: %s' % ', '.join(wip))
    if open_findings(folder):
        raise Refusal('%s/FINDINGS.md still lists %d unresolved item(s). Carry each to the project\'s own records '
                      '(the canonical task source development/TASKS.md names, or TECHNICAL-DEBT.md), note where in '
                      'your packet, and remove the row' % (name, open_findings(folder)))
    today = datetime.date.today().isoformat()
    if args.merged is not None and own:
        report = Report()
        check_folder(project, folder, peers, report, you)
        if report.fails:
            report.show()
            raise Refusal('the checks above must pass before closing')
        for text in report.warns:
            print('WARN: ' + text)
        if not confirmed(alignment_state(folder)):
            raise Refusal('ALIGNMENT.md is not CONFIRMED; work that was never aligned closes as --abandoned, not for a merge')
        remote, tracked = upstream_of(project)
        if remote and remote != '.' and tracked == project.branch:
            try:
                fetched = git(project.top, 'fetch', '--quiet', remote, tracked, check=False, timeout=60).returncode == 0
            except subprocess.TimeoutExpired:
                fetched = False
            if not fetched:
                print('WARN: could not fetch %s/%s; make sure it holds no commits this checkout lacks' % (remote, tracked))
            ref = 'refs/remotes/%s/%s' % (remote, tracked)
            if project.ref_exists(ref):
                behind = out(project.top, 'rev-list', '--count', 'HEAD..' + ref)
                if behind != '0':
                    raise Refusal('%s/%s has %s commit(s) this checkout does not: pull them, have any product change '
                                  'reviewed, then close' % (remote, tracked, behind))
        current = current_state(folder)
        last = last_product_commit(project)
        accepted = resolve_commit(project, current['accepted']) if current['accepted'] else ''
        if not accepted:
            raise Refusal('CURRENT.md records no accepted head. A merge needs the other assistant\'s ACCEPTED '
                          'verdict on the final product commit %s, recorded on the Accepted head line' % last[:12])
        if not succeeds(project.top, 'merge-base', '--is-ancestor', accepted, 'HEAD'):
            raise Refusal('the accepted head %s is not in this branch\'s history' % current['accepted'])
        changed = product_changes(project, accepted)
        if changed:
            raise Refusal('product files changed after the accepted head %s (last product commit %s): that change '
                          'needs the other assistant\'s review first' % (accepted[:12], last[:12]))
        outcome = 'closed for merge via %s' % args.merged
    elif args.merged is not None:
        outcome = 'closed after merge via %s, from branch %s' % (args.merged, project.branch)
    else:
        outcome = 'abandoned: %s' % args.abandoned
        if not own:
            outcome += ', closed from branch %s' % project.branch
    git(project.top, 'mv', '--', relative, relative + DONE)
    set_status(record / (folder.name + DONE) / 'CURRENT.md',
               '- **Status:** DONE, %s (%s, %s)' % (outcome, today, you), 'none (closed)')
    git(project.top, 'add', '--', relative + DONE + '/CURRENT.md')
    print('Closed %s -> %s%s (%s).' % (name, name, DONE, outcome))
    print('Commit and push it as its own change: git add -- %s && git commit -m "<message>" -m "Peer: %s" -- %s'
          % (RECORD, you, RECORD))
    if args.merged is not None and own:
        print('If the merge then does not happen, reopen the folder with: close --as %s --reopen "<reason>"' % you)
    return 0


# ---------------------------------------------------------------- main

def main(argv=None):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(errors='replace')
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest='command')
    commands.add_parser('setup')
    commands.add_parser('which')
    for name in ('start', 'packet', 'cue', 'close'):
        sub = commands.add_parser(name)
        sub.add_argument('--as', dest='you', required=True)
        if name == 'close':
            outcome = sub.add_mutually_exclusive_group(required=True)
            outcome.add_argument('--merged')
            outcome.add_argument('--abandoned')
            outcome.add_argument('--reopen')
            sub.add_argument('--folder')
    sub = commands.add_parser('check')
    sub.add_argument('--as', dest='you')
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_usage()
        return 2
    for key in ('merged', 'abandoned', 'reopen', 'folder'):
        value = getattr(args, key, None)
        if value is not None and (not value.strip() or re.search(r'[\x00-\x1f]', value)):
            print('FAIL: --%s needs a value without control characters' % key, file=sys.stderr)
            return 2
    try:
        project = Project(Path.cwd())
        handler = {'setup': command_setup, 'which': command_which, 'start': command_start,
                   'packet': command_packet, 'check': command_check, 'cue': command_cue,
                   'close': command_close}[args.command]
        return handler(project, args)
    except Refusal as refusal:
        print('FAIL: %s' % refusal)
        return 1
    except OSError as error:
        print('FAIL: %s' % error)
        return 1


if __name__ == '__main__':
    sys.exit(main())
