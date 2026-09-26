#!/usr/bin/env python3
"""Structural recovery support for next-step.sh. No prose is interpreted."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import tempfile
from pathlib import Path


# The fields the recovery contract reads (#16). Status, Decision, Reason and Authority are required
# of a decision cited as a basis; Depends on and Supersedes are read when present; the template's
# other fields are the project's own.
DECISION_STATUSES = {"proposed", "accepted", "superseded", "retired"}
DECISION_ID = re.compile(r"DEC-[0-9]{3,}")
STEP_ID = re.compile(r"[a-z][a-z0-9-]*\.[A-Za-z0-9][A-Za-z0-9.]*")
EVENT = re.compile(r"^- \[([x~ -])\] (.+?) \|")


class ContractError(Exception):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def within(root: Path, value: str) -> Path:
    if (not value or value.startswith(("/", "~")) or ".." in Path(value).parts
            or any(character in value for character in (",", ";", "|", "\n", "\r", "\x1f"))
            or "@sha256:" in value):
        raise ContractError(f"input path must stay below the project: {value}")
    path = (root / value).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise ContractError(f"input path must stay below the project: {value}") from exc
    if not path.is_file():
        raise ContractError(f"declared input is not a file: {value}")
    return path


def references(project: Path, cwd: Path) -> Path:
    current = cwd.resolve()
    root = project.resolve()
    while current == root or root in current.parents:
        candidate = current / "References.md"
        if candidate.is_file():
            return candidate
        if current == root:
            break
        current = current.parent
    for value in (root / "project" / "References.md", root / "archetype" / "References.md"):
        if value.is_file():
            return value
    raise ContractError("no References.md declares the canonical decision location")


def decision_source(project: Path, cwd: Path) -> tuple[Path, str | None]:
    refs = references(project, cwd)
    match = re.search(r"(?m)^- Decision location:\s*(.+?)\s*$", refs.read_text())
    if not match or match.group(1).startswith("["):
        raise ContractError(f"{refs.relative_to(project)} has no filled '- Decision location:'")
    value = match.group(1).strip()
    if value == "References.md § Decisions":
        return refs, "Decisions"
    path = within(project, value)
    return path, None


def field_value(block: str, label: str) -> list[str]:
    """Every value of one field in a decision block: a line with the label, optionally as a list
    item and optionally in bold or italic, then a colon."""
    pattern = rf"(?mi)^[ \t]*(?:[-*+][ \t]+)?[*_]*{re.escape(label)}[*_]*[ \t]*:[*_]*[ \t]*(.*?)[ \t]*$"
    return [value for value in re.findall(pattern, block)]


def decision_records(project: Path, cwd: Path) -> dict[str, bytes]:
    """Every decision block at the decision location, read leniently. Problems are recorded per
    decision in decision_records.problems and raised only when a cited decision, or one it depends
    on or is superseded by, carries one, so a malformed decision elsewhere blocks nothing."""
    path, section = decision_source(project, cwd)
    text = path.read_text()
    if section:
        found = re.search(r"(?ms)^## Decisions\s*$\n(.*?)(?=^## |\Z)", text)
        if not found:
            raise ContractError(f"{path.relative_to(project)} has no Decisions section")
        text = found.group(1)
    visible = []
    fenced = False
    for line in text.splitlines(keepends=True):
        if line.startswith(("```", "~~~")):
            fenced = not fenced
            visible.append("\n")
        elif fenced:
            visible.append("\n")
        else:
            visible.append(line)
    text = "".join(visible)
    headings = list(re.finditer(r"(?m)^###[ \t]+(DEC-[0-9]{3,})(?:[ \t]*[: -].*)?$", text))
    records: dict[str, bytes] = {}
    relationships: dict[str, dict] = {}
    problems: dict[str, list[str]] = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        block = text[heading.start():end]
        decision_id = heading.group(1)
        if decision_id in records:
            problems.setdefault(decision_id, []).append(f"duplicate decision id: {decision_id}")
            continue
        issues: list[str] = []
        values: dict[str, str] = {}
        for label in ("Status", "Decision", "Reason", "Authority", "Date", "Depends on", "Supersedes"):
            hits = [hit for hit in field_value(block, label)]
            distinct = {hit.strip() for hit in hits}
            if len(distinct) > 1:
                issues.append(f"{decision_id} gives {label} more than one value")
            values[label] = hits[0].strip() if hits else ""
        status_words = re.findall(r"[a-z]+", values["Status"].lower())
        status = status_words[0] if status_words else ""
        if status not in DECISION_STATUSES:
            issues.append(f"{decision_id} has no readable Status (proposed, accepted, superseded or retired)" if not status
                          else f"{decision_id} has unsupported Status: {values['Status']}")
        if status == "accepted":
            for label in ("Decision", "Reason", "Authority"):
                value = values[label]
                plain = re.sub(r"[*_`]", "", value).strip().lower()
                if (value.startswith("[") and value.endswith("]")) or plain in {"pending", "todo", "tbd"}:
                    issues.append(f"{decision_id} {label} is still a template placeholder")
        links: dict[str, list[str]] = {}
        for label in ("Depends on", "Supersedes"):
            raw = values[label]
            if not raw or raw.lower() in {"none", "n/a", "-"}:
                links[label] = []
                continue
            items = [item.strip().strip("`*_") for item in re.split(r"[;,]", raw) if item.strip()]
            bad = [item for item in items if not DECISION_ID.fullmatch(item)]
            if bad:
                issues.append(f"{decision_id} {label} names invalid decision '{bad[0]}'")
            links[label] = [item for item in items if DECISION_ID.fullmatch(item)]
        records[decision_id] = (block.strip() + "\n").encode()
        relationships[decision_id] = {
            "status": status,
            "depends": links["Depends on"],
            "supersedes": links["Supersedes"],
            "values": values,
        }
        if issues:
            problems[decision_id] = issues
    decision_records.relationships = relationships  # type: ignore[attr-defined]
    decision_records.problems = problems  # type: ignore[attr-defined]
    return records


def decision_closure(records: dict[str, bytes], decision_id: str) -> set[str]:
    """The cited decision, the decisions it depends on, and every accepted decision that supersedes
    one of them, transitively. Raises on a problem, an unknown reference or a cycle inside it."""
    relationships = decision_records.relationships  # type: ignore[attr-defined]
    problems = decision_records.problems  # type: ignore[attr-defined]
    if decision_id not in records:
        raise ContractError(f"unknown decision: {decision_id}")
    included: set[str] = set()
    def dependencies(value: str, trail: tuple[str, ...]) -> None:
        if value in trail:
            raise ContractError(f"decision dependency cycle includes {value}")
        if value not in records:
            raise ContractError(f"{trail[-1] if trail else decision_id} Depends on names unknown decision {value}")
        if value in problems:
            raise ContractError(problems[value][0])
        if value in included:
            return
        included.add(value)
        for target in relationships[value]["depends"]:
            dependencies(str(target), trail + (value,))
    dependencies(decision_id, ())
    changed = True
    while changed:
        changed = False
        for value, relation in relationships.items():
            if value in included or not any(target in included for target in relation["supersedes"]):
                continue
            if value in problems:
                raise ContractError(problems[value][0])
            if relation["status"] == "accepted":
                dependencies(value, ()); changed = True
    for value in list(included):
        for target in relationships[value]["supersedes"]:
            if target not in records:
                raise ContractError(f"{value} Supersedes names unknown decision {target}")
    return included


def decision_fingerprint(records: dict[str, bytes], decision_id: str) -> str:
    included = decision_closure(records, decision_id)
    payload = b"".join(value.encode() + b"\0" + records[value] for value in sorted(included))
    return digest(payload)


def basis(project: Path, cwd: Path, decisions: list[str], inputs: list[str]) -> str:
    fields = []
    if decisions:
        records = decision_records(project, cwd)
        seen = set()
        encoded = []
        for decision_id in decisions:
            if not DECISION_ID.fullmatch(decision_id) or decision_id in seen:
                raise ContractError(f"invalid or repeated decision basis: {decision_id}")
            if decision_id not in records:
                raise ContractError(f"unknown decision basis: {decision_id}")
            decision_closure(records, decision_id)
            relationships = decision_records.relationships  # type: ignore[attr-defined]
            if relationships[decision_id]["status"] != "accepted":
                raise ContractError(f"decision basis is not active and accepted: {decision_id}")
            values = relationships[decision_id]["values"]
            for label in ("Decision", "Reason", "Authority"):
                value = values[label].strip()
                plain = re.sub(r"[*_`]", "", value).strip().lower()
                if not value or plain in {"unknown", "pending", "todo", "tbd"} or (value.startswith("[") and value.endswith("]")):
                    raise ContractError(f"accepted decision basis {decision_id} needs a {label} line that says what it records, not {value or 'nothing'}")
            if any(relation["status"] == "accepted" and decision_id in relation["supersedes"] for relation in relationships.values()):
                raise ContractError(f"decision basis has been superseded: {decision_id}")
            seen.add(decision_id)
            encoded.append(f"{decision_id}@sha256:{decision_fingerprint(records, decision_id)}")
        fields.append("decisions=" + ",".join(encoded))
    if inputs:
        seen = set()
        encoded = []
        for value in inputs:
            if value in seen:
                raise ContractError(f"repeated input basis: {value}")
            seen.add(value)
            path = within(project, value)
            if path.suffix.lower() == ".md":
                labels = re.findall(r"(?m)^- Decision basis:\s*(.+?)\s*$", path.read_text())
                if labels:
                    declared = {item.strip() for item in labels[-1].split(",")}
                    supplied = set(decisions)
                    if declared != supplied:
                        raise ContractError(
                            f"{value} declares decision basis {sorted(declared)}, "
                            f"but --basis supplied {sorted(supplied)}"
                        )
            encoded.append(f"{value}@sha256:{digest(path.read_bytes())}")
        fields.append("inputs=" + ",".join(encoded))
    return ";".join(fields) if fields else "none"


def parse_steps(engine: Path) -> tuple[dict[str, list[str]], set[str]]:
    graph: dict[str, list[str]] = {}
    steps: set[str] = set()
    modes: dict[str, str] = {}
    for folder in ("bootstrap", "scaffolding", "development"):
        for entry in sorted((engine / folder).glob("*.md")):
            text = entry.read_text()
            ledger = re.search(r"(?m)^Step ledger: ([a-z][a-z0-9-]*)", text)
            if not ledger:
                continue
            mode = "unit" if re.search(r"(?m)^Step ledger: .*\(per [a-z]+\)", text) else "once"
            files = [entry]
            listed = re.search(r"(?m)^Step files: (.+)$", text)
            if listed:
                files.extend(engine / item.strip() for item in listed.group(1).split(";"))
            for path in files:
                fenced = False
                current = None
                dependency_seen: set[str] = set()
                basis_seen: set[str] = set()
                for line in path.read_text().splitlines():
                    if line.startswith(("```", "~~~")):
                        fenced = not fenced
                        continue
                    if fenced:
                        continue
                    heading = re.match(r"^###? Step ([A-Za-z0-9][A-Za-z0-9.]*)(?::| )", line)
                    if heading:
                        current = f"{ledger.group(1)}.{heading.group(1)}"
                        steps.add(current)
                        modes[current] = mode
                        graph.setdefault(current, [])
                    elif line.startswith("#"):
                        current = None
                    elif current and line.startswith("Depends on: "):
                        if current in dependency_seen:
                            raise ContractError(f"{current} has more than one Depends on line")
                        dependency_seen.add(current)
                        value = line[12:].strip()
                        graph[current] = [] if value == "none" else [v.strip() for v in value.split(";")]
                    elif current and line.startswith("Basis: "):
                        if current in basis_seen:
                            raise ContractError(f"{current} has more than one Basis line")
                        basis_seen.add(current)
                        value = line[7:].strip()
                        if value not in {"none", "decisions required", "inputs required", "decisions and inputs required"}:
                            raise ContractError(f"{current} has unsupported Basis: {value}")
    for step, dependencies in graph.items():
        for dependency in dependencies:
            if not STEP_ID.fullmatch(dependency) or dependency not in steps:
                raise ContractError(f"{step} has unknown or invalid dependency '{dependency}'")
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(node: str) -> None:
        if node in visiting:
            raise ContractError(f"step dependency cycle includes {node}")
        if node in visited:
            return
        visiting.add(node)
        for dependency in graph[node]:
            visit(dependency)
        visiting.remove(node)
        visited.add(node)
    for node in graph:
        visit(node)
    parse_steps.modes = modes  # type: ignore[attr-defined]
    return graph, steps


def basis_requirement(engine: Path, target: str) -> str:
    for folder in ("bootstrap", "scaffolding", "development"):
        for path in sorted((engine / folder).glob("*.md")):
            text = path.read_text()
            ledger = re.search(r"(?m)^Step ledger: ([a-z][a-z0-9-]*)", text)
            if not ledger:
                continue
            files = [path]
            listed = re.search(r"(?m)^Step files: (.+)$", text)
            if listed:
                files.extend(engine / item.strip() for item in listed.group(1).split(";"))
            for step_file in files:
                current = None
                fenced = False
                for line in step_file.read_text().splitlines():
                    if line.startswith(("```", "~~~")):
                        fenced = not fenced
                        continue
                    if fenced:
                        continue
                    heading = re.match(r"^###? Step ([A-Za-z0-9][A-Za-z0-9.]*)(?::| )", line)
                    if heading:
                        current = f"{ledger.group(1)}.{heading.group(1)}"
                    elif line.startswith("#"):
                        current = None
                    elif current == target and line.startswith("Basis: "):
                        value = line[7:].strip()
                        if value not in {"none", "decisions required", "inputs required", "decisions and inputs required"}:
                            raise ContractError(f"{target} has unsupported Basis: {value}")
                        return value
    return "none"


def latest_events(ledger: Path) -> dict[str, tuple[str, str]]:
    latest = {}
    for line in ledger.read_text().splitlines():
        match = EVENT.match(line)
        if match:
            latest[match.group(2)] = (match.group(1), line)
    return latest


def reopen_plan(engine: Path, project: Path, ledger: Path, target: str, unit: str) -> list[str]:
    graph, steps = parse_steps(engine)
    events = latest_events(ledger)
    seed_keys: set[str] = set()
    if DECISION_ID.fullmatch(target):
        for key, (_, line) in events.items():
            selected = re.findall(r"(DEC-[0-9]{3,})@sha256:", line)
            if not selected:
                continue
            context_match = re.search(r" \| cwd ([^|]+?) \| (?:owner [^|]+? \| )?basis ", line)
            context = context_match.group(1).strip() if context_match else "."
            records = decision_records(project, project / context)
            relationships = decision_records.relationships  # type: ignore[attr-defined]
            relevant = set(selected)
            changed = True
            while changed:
                changed = False
                for value in list(relevant):
                    for dependency in relationships.get(value, {}).get("depends", []):
                        if dependency not in relevant:
                            relevant.add(str(dependency)); changed = True
                for value, relation in relationships.items():
                    if (relation.get("status") == "accepted" and any(item in relevant for item in relation.get("supersedes", []))
                            and value not in relevant):
                        relevant.add(value); changed = True
            if target in relevant:
                seed_keys.add(key)
        if not seed_keys:
            raise ContractError(f"no current ledger event declares decision basis {target}")
    elif target in steps:
        for key in events:
            step, _, event_unit = key.partition(" @")
            if step == target and (not unit or event_unit == unit):
                seed_keys.add(key)
    else:
        raise ContractError(f"unknown reopen target: {target}")
    if not seed_keys:
        raise ContractError(f"reopen target has no current ledger event: {target}")
    affected = set(seed_keys)
    modes = parse_steps.modes  # type: ignore[attr-defined]
    changed = True
    while changed:
        changed = False
        for key in events:
            step, _, event_unit = key.partition(" @")
            if key in affected:
                continue
            for dependency in graph.get(step, []):
                dependency_key = f"{dependency} @{event_unit}" if modes.get(dependency) == "unit" and event_unit else dependency
                if dependency_key in affected:
                    affected.add(key); changed = True; break
    result = []
    for key, (state, _) in events.items():
        step, _, event_unit = key.partition(" @")
        if key in affected and state in {"x", "-"}:
            if event_unit and unit and event_unit != unit:
                continue
            result.append(key)
    if not result:
        raise ContractError(f"reopen target has no closed or skipped current work: {target}")
    return result


def validate_prerequisites(engine: Path, ledger: Path, target: str, unit: str) -> None:
    graph, steps = parse_steps(engine)
    if target not in steps:
        raise ContractError(f"unknown step: {target}")
    events = latest_events(ledger)
    for dependency in graph[target]:
        unit_key = f"{dependency} @{unit}" if unit else dependency
        key = unit_key if unit_key in events else dependency
        if key not in events:
            raise ContractError(
                f"{target} depends on {dependency}, which has no current ledger event; "
                "include its playbook and close or validly skip it"
            )
        if events[key][0] not in {"x", "-"}:
            raise ContractError(f"{target} depends on {key}, which is reopened")


def stale(engine: Path, project: Path, ledger: Path) -> list[str]:
    stale_keys = []
    for key, (state, line) in latest_events(ledger).items():
        if state not in {"x", "-"}:
            continue
        step = key.split(" @", 1)[0]
        requirement = basis_requirement(engine, step)
        if " | basis " not in line:
            if requirement != "none":
                stale_keys.append(key)
            continue
        payload = line.split(" | basis ", 1)[1].split(" |", 1)[0]
        if requirement != "none" and payload == "none":
            stale_keys.append(key); continue
        try:
            for field in payload.split(";"):
                if field.startswith("inputs="):
                    for item in field[7:].split(","):
                        value, expected = item.rsplit("@sha256:", 1)
                        if digest(within(project, value).read_bytes()) != expected:
                            stale_keys.append(key)
                elif field.startswith("decisions="):
                    context_match = re.search(r" \| cwd ([^|]+?) \| (?:owner [^|]+? \| )?basis ", line)
                    context = context_match.group(1).strip() if context_match else "."
                    if context.startswith("/") or ".." in Path(context).parts:
                        stale_keys.append(key); continue
                    records = decision_records(project, project / context)
                    for item in field[10:].split(","):
                        value, expected = item.rsplit("@sha256:", 1)
                        if value not in records or decision_fingerprint(records, value) != expected:
                            stale_keys.append(key)
        except (ContractError, ValueError):
            stale_keys.append(key)
    return sorted(set(stale_keys))


def append_reopen_events(ledger: Path, target: str, reason: str, date: str, keys: list[str]) -> None:
    if not keys or any(not key or "\n" in key or "|" in key for key in keys):
        raise ContractError("reopen event batch contains an invalid key")
    original = ledger.read_bytes()
    separator = b"" if not original or original.endswith(b"\n") else b"\n"
    events = "".join(f"- [~] {key} | {date} | reopened from {target}: {reason}\n" for key in keys).encode()
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{ledger.name}.", dir=ledger.parent)
    try:
        os.fchmod(descriptor, ledger.stat().st_mode)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(original); stream.write(separator); stream.write(events); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary_name, ledger)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    basis_parser = sub.add_parser("basis")
    basis_parser.add_argument("--project", required=True); basis_parser.add_argument("--cwd", required=True)
    basis_parser.add_argument("--decision", action="append", default=[]); basis_parser.add_argument("--input", action="append", default=[])
    reopen_parser = sub.add_parser("reopen")
    reopen_parser.add_argument("--engine", required=True); reopen_parser.add_argument("--project", required=True); reopen_parser.add_argument("--ledger", required=True)
    reopen_parser.add_argument("--target", required=True); reopen_parser.add_argument("--unit", default="")
    stale_parser = sub.add_parser("stale")
    stale_parser.add_argument("--engine", required=True); stale_parser.add_argument("--project", required=True); stale_parser.add_argument("--ledger", required=True)
    validate_parser = sub.add_parser("validate-decisions")
    validate_parser.add_argument("--project", required=True); validate_parser.add_argument("--cwd")
    graph_parser = sub.add_parser("validate-graph"); graph_parser.add_argument("--engine", required=True)
    requirement_parser = sub.add_parser("requirement"); requirement_parser.add_argument("--engine", required=True); requirement_parser.add_argument("--step", required=True)
    prerequisites_parser = sub.add_parser("prerequisites"); prerequisites_parser.add_argument("--engine", required=True); prerequisites_parser.add_argument("--ledger", required=True); prerequisites_parser.add_argument("--step", required=True); prerequisites_parser.add_argument("--unit", default="")
    dependencies_parser = sub.add_parser("dependencies"); dependencies_parser.add_argument("--engine", required=True); dependencies_parser.add_argument("--step", required=True)
    append_parser = sub.add_parser("append-reopen"); append_parser.add_argument("--ledger", required=True); append_parser.add_argument("--target", required=True); append_parser.add_argument("--reason", required=True); append_parser.add_argument("--date", required=True)
    args = parser.parse_args()
    try:
        if args.command == "basis":
            print(basis(Path(args.project), Path(args.cwd), args.decision, args.input))
        elif args.command == "reopen":
            print("\n".join(reopen_plan(Path(args.engine), Path(args.project), Path(args.ledger), args.target, args.unit)))
        elif args.command == "stale":
            print("\n".join(stale(Path(args.engine), Path(args.project), Path(args.ledger))))
        elif args.command == "validate-decisions":
            records = decision_records(Path(args.project), Path(args.cwd or args.project))
            problems = decision_records.problems  # type: ignore[attr-defined]
            for decision_id in records:
                try:
                    decision_closure(records, decision_id)
                except ContractError as exc:
                    problems.setdefault(decision_id, []).append(str(exc))
            if problems:
                for decision_id in sorted(problems):
                    for problem in dict.fromkeys(problems[decision_id]):
                        print(f"FAIL: {problem}")
                print("Only a decision a step cites, and the ones it depends on or is superseded by, block that step.")
                return 1
            print(f"OK: {len(records)} decision record(s) follow the recovery contract")
        elif args.command == "validate-graph":
            graph, _ = parse_steps(Path(args.engine))
            print(f"OK: {sum(len(value) for value in graph.values())} declared step dependency edge(s) are acyclic")
        elif args.command == "prerequisites":
            validate_prerequisites(Path(args.engine), Path(args.ledger), args.step, args.unit)
        elif args.command == "dependencies":
            graph, _ = parse_steps(Path(args.engine)); print("; ".join(graph.get(args.step, [])) or "none")
        elif args.command == "append-reopen":
            keys = [line for line in sys.stdin.read().splitlines() if line]
            append_reopen_events(Path(args.ledger), args.target, args.reason, args.date, keys)
        else:
            print(basis_requirement(Path(args.engine), args.step))
    except (ContractError, OSError) as exc:
        print(f"FAIL: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
