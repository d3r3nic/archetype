#!/usr/bin/env python3
"""Check bootstrap facts and handoff content, not the truth of recorded answers."""
from pathlib import Path
import argparse
import datetime
import importlib.util
import re
import sys


def peer_names(value):
    # One reading of the Peer coding line, shared with the peer-coding script.
    spec = importlib.util.spec_from_file_location('peer_coding', Path(__file__).with_name('peer-coding.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse_peers(value)


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


def section(path, title, latest=False):
    if not path.is_file():
        raise ValueError(f'{path.name} is missing')
    groups, current = [], None
    for line in live_lines(path.read_text()):
        if line.startswith('## '):
            current = [] if line.strip() == '## ' + title else None
            if current is not None:
                groups.append(current)
        elif current is not None:
            current.append(line)
    if not groups or (not latest and len(groups) != 1):
        raise ValueError(f'{path.name}: requires {"a" if latest else "exactly one"} live {title} section')
    return groups[-1]


def fields(lines, bullet=False):
    result = {}
    pattern = r'^- ([^:]+):\s*(.*)$' if bullet else r'^([^:]+):\s*(.*)$'
    for line in lines:
        match = re.match(pattern, line)
        if match:
            key, value = match.groups()
            if key in result:
                raise ValueError(f'duplicate field: {key}')
            result[key] = value
    return result


def normalized(value):
    return re.sub(r'[*_`]', '', value).strip()


def filled(value):
    plain = normalized(value)
    if not plain or re.match(r'^(?:pending|tbd|todo)(?:\b|$)', plain, re.I):
        return False
    # A Markdown link is a value; an unfilled template prompt is not.
    return not (plain.startswith('[') and not re.match(r'^\[[^\]]+\]\([^)]+\)', plain))


def require(data, keys):
    for key in keys:
        if not filled(data.get(key, '')):
            raise ValueError(f'{key}: fill the required bootstrap fact, not a template placeholder')


def check_context():
    data = fields(section(Path('References.md'), 'Project'), bullet=True)
    if 'Purpose (one sentence)' in data and 'Purpose' not in data:
        data['Purpose'] = data['Purpose (one sentence)']
    require(data, ('Name', 'Purpose', 'Stage', 'Owner channel', 'Decision location', 'Reporting pace'))
    for key in ('Name', 'Purpose', 'Stage', 'Decision location'):
        if re.match(r'^(unknown|none|n/a)\b', normalized(data[key]), re.I):
            raise ValueError(f'{key}: a resolved bootstrap fact is required')
    if 'Peer coding' not in data:
        raise ValueError('Peer coding: ask the owner whether another AI assistant will take turns on this '
                         'project and who writes new work (bootstrap/ONBOARD-2.6-CARE-AND-AUTHORITY.md), then '
                         'record none or both assistants on this line and the preference on Peer roles')
    try:
        peers = peer_names(data['Peer coding'])
    except ValueError as error:
        raise ValueError(f'Peer coding: {error}') from None
    if peers and (not filled(data.get('Peer roles', ''))
                  or re.match(r'^(unknown|none|n/a)\b', normalized(data.get('Peer roles', '')), re.I)):
        raise ValueError('Peer roles: record who writes new work and who reviews it, in the owner\'s words')
    tree = Path('feature-tree.md')
    if not tree.is_file() or not tree.read_text().strip():
        raise ValueError('feature-tree.md is missing or empty')
    print('OK: required project facts recorded; scaffold implementation fields are left to scaffold')


def check_log():
    lines = section(Path('VERSION-LOG.md'), 'Bootstrap', latest=True)
    data = fields(lines)
    require(data, ('Date', 'Type', 'Tech stack', 'Profile', 'Discovery',
                   'Key decisions made', 'Open pre-production gates'))
    try:
        datetime.date.fromisoformat(data['Date'])
    except ValueError:
        raise ValueError('Date: record the bootstrap date in year-month-day form') from None
    if not re.match(r'^(template|product|existing-project-migration|platform)(?:\s|/|$)', data['Type']):
        raise ValueError('Type: name template, product, existing-project-migration, or platform')
    try:
        start = lines.index('Files generated:') + 1
    except ValueError:
        raise ValueError('Files generated: record the generated project files') from None
    generated = []
    for line in lines[start:]:
        if line.startswith('- '):
            generated.append(line[2:])
        elif line.strip():
            break
    if not generated or not all(filled(item) for item in generated):
        raise ValueError('Files generated: requires filled file entries')
    named = {Path(item.split()[0]).name for item in generated}
    for name in ('References.md', 'PROFILE.md', 'feature-tree.md'):
        if name not in named:
            raise ValueError(f'Files generated: missing required {name} entry')
    print('OK: bootstrap handoff records discovery and open gates; reviewer must verify the claims')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('context', 'log'))
    args = parser.parse_args()
    try:
        (check_context if args.mode == 'context' else check_log)()
    except (ValueError, OSError) as error:
        print(f'FAIL: {error}')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
