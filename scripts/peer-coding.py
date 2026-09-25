#!/usr/bin/env python3
"""Peer coding: two AI assistants taking turns on a branch (development/PEER-CODING.md).

Run with python3 from anywhere inside the branch's worktree:
  peer-coding.py start --as NAME       open this branch's folder, peer-coding/<branch>/
  peer-coding.py packet --as NAME      open your next packet, rounds/R<n>/NAME.md, marked WIP
  peer-coding.py check [--as NAME]     check the folder, the recorded commits, links, other folders
  peer-coding.py cue --as NAME         print the line the owner pastes into the other chat
  peer-coding.py close --as NAME (--merged REF | --abandoned REASON) [--folder FOLDER]
                                       rename the folder to <folder>--done and mark it done

NAME is one of the two short names on the Peer coding line of References.md, section Project.
The folder name is the branch name with slashes and other unusual characters as dashes.

What it cannot do: judge whether a review was good, or know which assistant made a commit.

Exit 0: done, or the check passed. 1: a check failed or the command refused. 2: usage.
3: start found this branch's folder already open (resume it).
"""
import argparse
import datetime
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ENGINE = Path(__file__).resolve().parent.parent
TEMPLATES = ENGINE / 'templates' / 'peer-coding'
PLAYBOOK = Path('development') / 'PEER-CODING.md'
RECORD = 'peer-coding'
DONE = '--done'
PEERS_FORMAT = ('name the two assistants as "<name> (<tool>), <name> (<tool>)", '
                'or write none when no second assistant works on the project')


class Refusal(Exception):
    pass


def git(top, *args, check=True):
    result = subprocess.run(['git', '-C', str(top)] + list(args), stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, universal_newlines=True)
    if check and result.returncode != 0:
        raise Refusal('git %s failed: %s' % (' '.join(args), result.stderr.strip()))
    return result


def out(top, *args):
    return git(top, *args).stdout.strip()


def succeeds(top, *args):
    return git(top, *args, check=False).returncode == 0


# ---------------------------------------------------------------- the project and the branch

class Project:
    def __init__(self, where):
        probe = git(where, 'rev-parse', '--show-toplevel', check=False)
        if probe.returncode != 0:
            raise Refusal('%s is not inside a git worktree; peer coding keeps its record in the '
                          'repository' % where)
        self.top = Path(probe.stdout.strip()).resolve()
        self.branch = git(self.top, 'symbolic-ref', '-q', '--short', 'HEAD', check=False).stdout.strip()
        self.default = self._default_branch()
        self.engine = self._engine_here()
        self.references = self._references()

    def _default_branch(self):
        head = git(self.top, 'symbolic-ref', '-q', '--short', 'refs/remotes/origin/HEAD',
                   check=False).stdout.strip()
        if head.startswith('origin/'):
            return head[len('origin/'):]
        configured = git(self.top, 'config', '--get', 'init.defaultBranch', check=False).stdout.strip()
        for name in [configured, 'main', 'master']:
            if name and (succeeds(self.top, 'show-ref', '-q', '--verify', 'refs/heads/' + name) or
                         succeeds(self.top, 'show-ref', '-q', '--verify', 'refs/remotes/origin/' + name)):
                return name
        return ''

    def _engine_here(self):
        # The engine as this worktree carries it: the same place relative to the repository top
        # as the engine this script ran from, so another checkout's script reads this branch.
        engine_top = git(ENGINE, 'rev-parse', '--show-toplevel', check=False)
        if engine_top.returncode == 0:
            relative = os.path.relpath(str(ENGINE), str(Path(engine_top.stdout.strip()).resolve()))
            candidate = (self.top / relative).resolve() if relative != '.' else self.top
            if (candidate / PLAYBOOK).is_file():
                return candidate
        return ENGINE

    def _references(self):
        if (self.engine / 'References.md').is_file():
            return self.engine / 'References.md'
        return self.engine.parent / 'References.md'

    def slug(self, branch=None):
        name = branch if branch is not None else self.branch
        slug = re.sub(r'[^A-Za-z0-9._-]', '-', name.replace('/', '-'))
        return slug if re.match(r'[A-Za-z0-9]', slug) else 'branch-' + slug

    def record(self):
        return self.top / RECORD


# ---------------------------------------------------------------- References.md

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


def project_facts(references):
    if not references.is_file():
        return {}
    facts, inside = {}, False
    for line in live_lines(read(references)):
        if line.startswith('## '):
            inside = line.strip() == '## Project'
            continue
        match = re.match(r'^- ([^:]+):\s*(.*)$', line) if inside else None
        if match and match.group(1).strip() not in facts:
            facts[match.group(1).strip()] = match.group(2).strip()
    return facts


def plain(value):
    return re.sub(r'[*_`]', '', value or '').strip()


def parse_peers(value):
    """The two short names on a Peer coding line: [] when none, ValueError when unreadable."""
    text = plain(value)
    if not text or text.startswith('['):
        raise ValueError('the Peer coding line is not answered: ' + PEERS_FORMAT)
    if re.match(r'^(none|no|n/a)\b', text, re.I):
        return []
    text = re.sub(r'\([^)]*\)', ' ', text)
    names = []
    for part in re.split(r',|;|&|\band\b', text):
        part = part.strip()
        if not part:
            continue
        match = re.match(r'^([A-Za-z][A-Za-z0-9-]*)$', part)
        if not match:
            raise ValueError('cannot read "%s" on the Peer coding line: %s' % (part, PEERS_FORMAT))
        names.append(match.group(1).lower())
    if len(names) != 2 or names[0] == names[1] or DONE in ''.join(names):
        raise ValueError('the Peer coding line must name two different assistants: ' + PEERS_FORMAT)
    return names


def peers_of(project):
    facts = project_facts(project.references)
    if 'Peer coding' not in facts:
        raise Refusal('%s records no Peer coding line in its Project section. Ask the owner whether '
                      'another AI assistant will take turns on this project and who writes new work, '
                      'then record the answers (bootstrap/ONBOARD-2.6-CARE-AND-AUTHORITY.md)'
                      % display(project, project.references))
    try:
        names = parse_peers(facts['Peer coding'])
    except ValueError as error:
        raise Refusal('%s: %s' % (display(project, project.references), error))
    if not names:
        raise Refusal('%s says Peer coding: none. Peer coding starts only when the owner asks for it; '
                      'record the owner\'s words on that line first' % display(project, project.references))
    return names, facts.get('Peer roles', '').strip()


def display(project, path):
    try:
        return str(Path(path).resolve().relative_to(project.top))
    except ValueError:
        return str(path)


# ---------------------------------------------------------------- the branch folder's files

def read(path):
    return path.read_text(encoding='utf-8') if path.is_file() else ''


def write(path, text):
    path.write_text(text, encoding='utf-8')


def current_state(folder):
    text = read(folder / 'CURRENT.md')
    state = {'text': text}
    branch = re.search(r'^Branch `([^`]+)`', text, re.M)
    state['branch'] = branch.group(1) if branch else ''
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
    commit = re.search(r'\b([0-9a-f]{7,40})\b', accepted.group(1)) if accepted else None
    state['accepted'] = commit.group(1) if commit else ''
    state['head'] = ''
    if state['branch']:
        row = re.search(r'^\|\s*`%s`\s*\|\s*([^|]*)\|' % re.escape(state['branch']), text, re.M)
        commit = re.search(r'\b([0-9a-f]{7,40})\b', row.group(1)) if row else None
        state['head'] = commit.group(1) if commit else ''
    return state


def alignment_state(folder):
    text = read(folder / 'ALIGNMENT.md')
    status = re.search(r'^Status:\s*(.*)$', text, re.M)
    value = plain(status.group(1)) if status else ''
    word = re.match(r'(REQUESTED|BRIEFED|CONFIRMED)\b', value)
    roles = re.search(r'^Context holder:\s*(.*?)\s*·\s*Receiver:\s*(.*)$', text, re.M)
    names = []
    if roles:
        for raw in roles.groups():
            match = re.match(r'^([A-Za-z][A-Za-z0-9-]*)$', plain(raw))
            names.append(match.group(1).lower() if match else '')
    return {'status': word.group(1) if word else '', 'raw': value,
            'holder': names[0] if names else '', 'receiver': names[1] if len(names) > 1 else ''}


def open_findings(folder):
    rows, table = 0, False
    for line in read(folder / 'FINDINGS.md').splitlines():
        cells = [cell.strip() for cell in line.strip().strip('|').split('|')] if line.strip().startswith('|') else None
        if cells is None:
            if table:
                break
            continue
        if not table:
            table = bool(cells) and cells[0] == 'ID'
            continue
        if all(re.match(r'^:?-+:?$', cell) for cell in cells if cell):
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
            slug = re.sub(r'[^\w\- ]', '', heading.group(1).lower()).replace(' ', '-')
            count = counts.get(slug, 0)
            found.add(slug if not count else '%s-%d' % (slug, count))
            counts[slug] = count + 1
    return found


def link_problems(project, folder):
    problems = []
    record = project.record()
    for path in sorted(folder.rglob('*.md')):
        for line in live_lines(read(path)):
            line = re.sub(r'`[^`\n]*`', '', line)
            for match in re.finditer(r'!?\[[^\]\n]*\]\(([^)\n]+)\)', line):
                target = match.group(1).strip()
                target = target[1:target.index('>')] if target.startswith('<') and '>' in target else target.split()[0]
                where = display(project, path)
                parts = urlsplit(target)
                if parts.scheme or parts.netloc:
                    continue
                if parts.path.startswith('/'):
                    problems.append('%s: link %s uses an absolute path; link inside the repository, relative to the file' % (where, target))
                    continue
                resolved = Path(os.path.normpath(str(path.parent / unquote(parts.path)))) if parts.path else path
                try:
                    inside = resolved.relative_to(project.top)
                except ValueError:
                    problems.append('%s: link %s leaves the repository' % (where, target))
                    continue
                if not resolved.exists():
                    problems.append('%s: link %s points to nothing' % (where, target))
                    continue
                pieces = inside.parts
                if (len(pieces) > 1 and pieces[0] == RECORD and pieces[1] != folder.name
                        and not pieces[1].endswith(DONE) and (record / pieces[1] / 'CURRENT.md').is_file()):
                    problems.append('%s: link %s points into the open folder of another branch, which closing '
                                    'renames; name it in text instead' % (where, target))
                if parts.fragment and resolved.suffix == '.md' and unquote(parts.fragment) not in anchors(resolved):
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


def product_changes(project, since):
    return [line for line in out(project.top, 'diff', '--name-only', since, 'HEAD', '--', '.',
                                 ':(exclude)%s' % RECORD).splitlines() if line]


def uncommitted_product(project):
    return [line[3:] for line in git(project.top, 'status', '--porcelain', '-uall', '--', '.',
                                     ':(exclude)%s' % RECORD).stdout.splitlines() if line]


def last_product_commit(project):
    return out(project.top, 'log', '-1', '--format=%H', 'HEAD', '--', '.', ':(exclude)%s' % RECORD)


def resolve_commit(project, commit):
    probe = git(project.top, 'rev-parse', '-q', '--verify', commit + '^{commit}', check=False)
    return probe.stdout.strip() if probe.returncode == 0 else ''


def check_folder(project, folder, peers, report, you=''):
    name = display(project, folder)
    for required in ('CURRENT.md', 'ALIGNMENT.md', 'FINDINGS.md'):
        if not (folder / required).is_file():
            report.fail('%s has no %s' % (name, required))
    if report.fails:
        return
    current, alignment = current_state(folder), alignment_state(folder)
    if current['branch'] != project.branch:
        report.fail('%s belongs to branch %s, not %s: two branch names give one folder name, so '
                    'rename this branch' % (name, current['branch'] or '(none recorded)', project.branch))
        return
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
    if alignment['status'] and current['alignment'] and alignment['status'] != current['alignment']:
        report.warn('%s: CURRENT.md says alignment %s, ALIGNMENT.md says %s' % (name, current['alignment'], alignment['status']))
    if current['turn'] and current['turn'] != 'none':
        if current['turn'] not in peers:
            report.fail('%s: CURRENT.md gives the writing turn to %s; the peers are %s' % (name, current['turn'], ' and '.join(peers)))
        elif alignment['status'] != 'CONFIRMED':
            report.fail('%s: CURRENT.md gives %s the writing turn before ALIGNMENT.md is CONFIRMED' % (name, current['turn']))
    if current['next_move'] and current['next_move'] not in peers:
        report.fail('%s: CURRENT.md gives the next move to %s; the peers are %s' % (name, current['next_move'], ' and '.join(peers)))
    if not current['accepted_line']:
        report.fail('%s: CURRENT.md has no Accepted head line (none yet, or the accepted commit and who accepted it)' % name)

    head = resolve_commit(project, current['head']) if current['head'] else ''
    if not current['head']:
        report.fail('%s: CURRENT.md records no last product commit for `%s` in its Heads table' % (name, project.branch))
    elif not head:
        report.fail('%s: the recorded last product commit %s does not exist here; pull, or correct CURRENT.md' % (name, current['head']))
    elif not succeeds(project.top, 'merge-base', '--is-ancestor', head, 'HEAD'):
        report.fail('%s: the recorded last product commit %s is not in this branch\'s history' % (name, current['head']))
    else:
        changed = product_changes(project, head)
        if changed:
            listed = ', '.join(changed[:8]) + (' ...' if len(changed) > 8 else '')
            report.fail('%s: product files changed after the recorded last product commit %s, and no hand-over '
                        'recorded them: %s' % (name, current['head'], listed))
    dirty = uncommitted_product(project)
    if dirty:
        listed = ', '.join(dirty[:8]) + (' ...' if len(dirty) > 8 else '')
        report.fail('uncommitted product changes in this worktree: %s. Commit them on your writing turn, '
                    'or leave them out; never hand them over' % listed)

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


def stale_folders(project, report):
    record = project.record()
    if not record.is_dir():
        return
    own = project.slug() if project.branch else None
    for entry in sorted(record.iterdir()):
        if not entry.is_dir() or entry.name.endswith(DONE) or entry.name == own:
            continue
        if not (entry / 'CURRENT.md').is_file():
            continue
        branch = current_state(entry)['branch']
        if not branch:
            report.warn('%s records no branch' % display(project, entry))
            continue
        tip = ''
        for ref in ('refs/heads/' + branch, 'refs/remotes/origin/' + branch):
            if succeeds(project.top, 'show-ref', '-q', '--verify', ref):
                tip = ref
                break
        if not tip:
            report.warn('%s: its branch %s no longer exists here. If it merged or was abandoned, close the '
                        'folder from this branch: close --folder %s' % (display(project, entry), branch, entry.name))
            continue
        target = project.default and next((ref for ref in ('refs/heads/' + project.default, 'refs/remotes/origin/' + project.default)
                                           if succeeds(project.top, 'show-ref', '-q', '--verify', ref)), '')
        if target and branch != project.default and succeeds(project.top, 'merge-base', '--is-ancestor', tip, target):
            report.warn('%s: its branch %s is merged into %s but the folder is still open; close it from this '
                        'branch: close --folder %s --merged <ref>' % (display(project, entry), branch, project.default, entry.name))


def own_folder(project):
    if not project.branch:
        raise Refusal('detached HEAD: check out the branch for this work')
    return project.record() / project.slug()


def command_check(project, args):
    report = Report()
    peers, _ = peers_of(project)
    you = (args.you or '').lower()
    if project.branch and project.branch != project.default:
        folder = own_folder(project)
        if (project.record() / (folder.name + DONE)).is_dir() and not folder.exists():
            report.note('%s%s is closed: its branch finished. New work gets a new branch' % (display(project, folder), DONE))
        elif not (folder / 'CURRENT.md').is_file():
            report.fail('no peer-coding folder for branch %s; open one with start' % project.branch)
        else:
            check_folder(project, folder, peers, report, you)
    elif not project.branch:
        report.fail('detached HEAD: check out the branch for this work')
    else:
        report.note('%s is the default branch; branch folders live on their own branches' % project.branch)
    stale_folders(project, report)
    return report.show()


# ---------------------------------------------------------------- start

def render(template, destination, values):
    text = read(TEMPLATES / template)
    for key, value in values.items():
        text = text.replace('{{%s}}' % key, value)
    if destination.exists():
        raise Refusal('refusing to overwrite %s' % destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    write(destination, text)


def playbook_link(project, folder):
    target = project.engine / PLAYBOOK
    try:
        target.relative_to(project.top)
    except ValueError:
        return '`%s`' % target
    relative = os.path.relpath(str(target), str(folder))
    return '[%s](%s)' % (PLAYBOOK.as_posix(), Path(relative).as_posix())


def command_start(project, args):
    peers, roles = peers_of(project)
    you = args.you.lower()
    if you not in peers:
        raise Refusal('--as %s is not one of the peers on the Peer coding line: %s' % (you, ' and '.join(peers)))
    folder = own_folder(project)
    if project.default and project.branch == project.default:
        raise Refusal('%s is the default branch. Peer work runs on a branch of its own, for example in a new '
                      'worktree: git worktree add ../<folder> -b <branch>' % project.branch)
    if not project.default:
        print('WARN: the default branch could not be determined (no origin HEAD, main or master); '
              'make sure %s is not the branch releases come from' % project.branch)
    if folder.name.endswith(DONE):
        raise Refusal('the branch name ends in %s, which marks closed folders; use another branch name' % DONE)
    if re.search(r'[`|]', project.branch):
        raise Refusal('the branch name contains ` or |, which the record\'s tables cannot hold; rename the branch')
    record = project.record()
    if record.is_symlink() or (record.exists() and not record.is_dir()):
        raise Refusal('%s exists and is not a plain folder' % record)
    if (folder / 'CURRENT.md').is_file():
        recorded = current_state(folder)['branch']
        if recorded != project.branch:
            raise Refusal('%s already belongs to branch %s: two branch names give one folder name, so rename '
                          'this branch' % (display(project, folder), recorded))
        print('%s is already open for branch %s: resume it (development/PEER-CODING.md, Each turn)' % (display(project, folder), project.branch))
        return 3
    if folder.exists():
        raise Refusal('%s exists but is not a branch folder' % display(project, folder))
    if (record / (folder.name + DONE)).exists():
        raise Refusal('%s%s is closed; start new work on a new branch' % (display(project, folder), DONE))
    for probe in ('CURRENT.md', 'rounds/R1/%s.md' % you, 'rounds/R1/evidence/%s/output.txt' % you):
        path = '%s/%s/%s' % (RECORD, folder.name, probe)
        rule = git(project.top, 'check-ignore', '-v', '--no-index', '--', path, check=False)
        if rule.returncode == 0:
            raise Refusal('%s would be excluded by the repository\'s ignore rules (%s), so the record could '
                          'not be committed; change that rule first' % (path, rule.stdout.split('\t')[0]))
    closed = '%s/%s%s/CURRENT.md' % (RECORD, folder.name, DONE)
    rule = git(project.top, 'check-ignore', '-v', '--no-index', '--', closed, check=False)
    if rule.returncode == 0:
        raise Refusal('%s would be excluded by the repository\'s ignore rules (%s); change that rule first'
                      % (closed, rule.stdout.split('\t')[0]))
    values = {
        'FOLDER': '%s/%s' % (RECORD, folder.name),
        'BRANCH': project.branch,
        'DATE': datetime.date.today().isoformat(),
        'BY': you,
        'PEERS': ' | '.join(peers),
        'PLAYBOOK': playbook_link(project, folder),
        'HEAD': out(project.top, 'rev-parse', 'HEAD'),
        'ROLES': plain(roles) or 'not recorded; ask the owner',
    }
    for template in ('CURRENT.md', 'ALIGNMENT.md', 'FINDINGS.md'):
        render(template, folder / template, values)
    print('Created %s for branch %s.' % (display(project, folder), project.branch))
    print('Who writes new work (References.md, Peer roles): %s' % values['ROLES'])
    print('Next: decide whether you hold the context for this work and fill ALIGNMENT.md '
          '(development/PEER-CODING.md, Start a branch).')
    return 0


# ---------------------------------------------------------------- packet

def relative_link(source, target):
    relative = Path(os.path.relpath(str(target), str(source.parent))).as_posix()
    return '[%s](%s)' % (relative, relative)


def command_packet(project, args):
    peers, _ = peers_of(project)
    you = args.you.lower()
    if you not in peers:
        raise Refusal('--as %s is not one of the peers: %s' % (you, ' and '.join(peers)))
    other = [peer for peer in peers if peer != you][0]
    folder = own_folder(project)
    if not (folder / 'CURRENT.md').is_file():
        raise Refusal('no peer-coding folder for branch %s; open one with start' % project.branch)
    if alignment_state(folder)['status'] != 'CONFIRMED':
        raise Refusal('ALIGNMENT.md is not CONFIRMED; alignment moves happen in ALIGNMENT.md, not in packets')
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
            incoming = directory / (other + '.md')
            break
    values = {
        'FOLDER': '%s/%s' % (RECORD, folder.name),
        'ROUND': str(number),
        'BY': you,
        'OTHER': other,
        'BRANCH': project.branch,
        'INCOMING': relative_link(path, incoming) if incoming else 'none: the first packet of this branch',
        'CURRENT': relative_link(path, folder / 'CURRENT.md'),
    }
    render('PACKET.md', path, values)
    print('Opened %s (WIP). Save command output under %s/.' % (display(project, path),
          display(project, path.parent / 'evidence' / you)))
    return 0


# ---------------------------------------------------------------- cue

def command_cue(project, args):
    peers, _ = peers_of(project)
    you = args.you.lower()
    if you not in peers:
        raise Refusal('--as %s is not one of the peers: %s' % (you, ' and '.join(peers)))
    other = [peer for peer in peers if peer != you][0]
    folder = own_folder(project)
    if not (folder / 'CURRENT.md').is_file():
        raise Refusal('no peer-coding folder for branch %s' % project.branch)
    report = Report()
    check_folder(project, folder, peers, report, you)
    if report.fails:
        report.show()
        raise Refusal('the checks above must pass before handing over')
    status = git(project.top, 'status', '--porcelain', '-uall', '--', '%s/%s' % (RECORD, folder.name)).stdout.strip()
    if status:
        raise Refusal('the folder has uncommitted changes; commit it first: git add -- %s && git commit -m '
                      '"<message>" -- %s' % (RECORD, RECORD))
    wip = [display(project, packet) for _, _, packet in packets(folder) if is_wip(packet)]
    if wip:
        raise Refusal('a packet is still WIP: %s' % ', '.join(wip))
    current, alignment = current_state(folder), alignment_state(folder)
    if alignment['status'] != 'CONFIRMED':
        recipient, label = current['next_move'], 'ALIGN'
    else:
        recipient = current['turn'] if current['turn'] != 'none' else ''
        mine = [number for number, peer, _ in packets(folder) if peer == you]
        label = 'R%d' % mine[-1] if mine else 'ALIGN'
    if recipient != other:
        raise Refusal('CURRENT.md gives the next move to %s. Before handing over, give it to %s; or end with '
                      'NEEDS USER or SCOPE CLOSED instead' % (recipient or 'no one', other))
    upstream = git(project.top, 'rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}', check=False)
    if upstream.returncode == 0:
        if not succeeds(project.top, 'merge-base', '--is-ancestor', 'HEAD', '@{u}'):
            raise Refusal('push the branch first: %s does not have this commit yet' % upstream.stdout.strip())
    elif out(project.top, 'remote'):
        raise Refusal('push the branch and set its upstream first: git push -u <remote> %s' % project.branch)
    else:
        print('NOTE: this repository has no remote, so the other assistant must work in this same repository.')
    commit = out(project.top, 'rev-parse', '--short=12', 'HEAD')
    print('READY FOR %s · %s/%s %s · %s@%s' % (other.upper(), RECORD, folder.name, label, project.branch, commit))
    print('Continue peer coding on branch %s (worktree: %s): read AGENTS.md there, then %s/%s/CURRENT.md.'
          % (project.branch, project.top, RECORD, folder.name))
    return 0


# ---------------------------------------------------------------- close

def command_close(project, args):
    peers, _ = peers_of(project)
    you = args.you.lower()
    if you not in peers:
        raise Refusal('--as %s is not one of the peers: %s' % (you, ' and '.join(peers)))
    record = project.record()
    if args.folder:
        if '/' in args.folder or args.folder in ('.', '..'):
            raise Refusal('--folder takes a folder name under %s/' % RECORD)
        folder = record / args.folder
    else:
        folder = own_folder(project)
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
                      '(development/TASKS.md or its technical-debt record), note where in your packet, and '
                      'remove the row' % (name, open_findings(folder)))
    today = datetime.date.today().isoformat()
    if args.merged is not None:
        if not args.folder or folder.name == project.slug():
            report = Report()
            check_folder(project, folder, peers, report, you)
            if report.fails:
                report.show()
                raise Refusal('the checks above must pass before closing')
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
        outcome = 'merged via %s' % args.merged
    else:
        outcome = 'abandoned: %s' % args.abandoned
    if args.folder and folder.name != project.slug():
        outcome += ', closed from branch %s' % (project.branch or 'HEAD')
    git(project.top, 'mv', '--', relative, relative + DONE)
    closed = record / (folder.name + DONE) / 'CURRENT.md'
    text = read(closed)
    line = '- **Status:** DONE, %s (closed %s by %s)' % (outcome, today, you)
    text, count = re.subn(r'^- \*\*Status:\*\*.*$', lambda _: line, text, count=1, flags=re.M)
    if not count:
        text = re.sub(r'\A(# [^\n]*\n)', lambda match: match.group(1) + '\n' + line + '\n', text, count=1)
    text = re.sub(r'^- \*\*Product writing turn:\*\*.*$', '- **Product writing turn:** none (closed)', text, count=1, flags=re.M)
    write(closed, text)
    git(project.top, 'add', '--', relative + DONE + '/CURRENT.md')
    print('Closed %s -> %s%s (%s).' % (name, name, DONE, outcome))
    print('Commit and push it as its own change: git add -- %s && git commit -m "<message>" -- %s' % (RECORD, RECORD))
    return 0


# ---------------------------------------------------------------- main

def main(argv=None):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(errors='replace')
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest='command')
    for name in ('start', 'packet', 'cue', 'close'):
        sub = commands.add_parser(name)
        sub.add_argument('--as', dest='you', required=True)
        if name == 'close':
            outcome = sub.add_mutually_exclusive_group(required=True)
            outcome.add_argument('--merged')
            outcome.add_argument('--abandoned')
            sub.add_argument('--folder')
    sub = commands.add_parser('check')
    sub.add_argument('--as', dest='you')
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_usage()
        return 2
    for value in (getattr(args, 'merged', None), getattr(args, 'abandoned', None), getattr(args, 'folder', None)):
        if value is not None and (not value.strip() or re.search(r'[\x00-\x1f]', value)):
            print('FAIL: an empty value or a control character in the arguments', file=sys.stderr)
            return 2
    try:
        project = Project(Path.cwd())
        handler = {'start': command_start, 'packet': command_packet, 'check': command_check,
                   'cue': command_cue, 'close': command_close}[args.command]
        return handler(project, args)
    except Refusal as refusal:
        print('FAIL: %s' % refusal)
        return 1


if __name__ == '__main__':
    sys.exit(main())
