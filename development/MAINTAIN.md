# Phase 4: Maintain

Keep the project's records true and its debt honest for the life of the project. Maintenance follows change, not the calendar: look again whenever something changes that the records describe. Carry the work in the implementer plan (development/TASKS.md); completing another route does not close it.

## When to look again

- Before a framework update, and after it.
- After a feature or a shared system changes.
- When a fact in PROFILE.md changes, and before any action that increases exposure (#30).
- After an incident, a failed release, a flaky suite, or a session that went notably wrong.
- When review keeps finding the same kind of problem.
- When the owner asks.

A project that people depend on may also set a regular review in References.md; its facts and pace decide how often, not a number from this file.

## What to check

Check what applies to this project:
- **The map.** feature-tree.md matches the code: every row's location exists, every system and feature that exists has a row, and every status is true. `scripts/validate-maintain.sh` reads the rows against the project.
- **The records.** Feature records, system pages and References.md describe the current code. The § Boundaries lines still name the real owners, and `scripts/validate-develop.sh` shows they hold.
- **The debt.** TECHNICAL-DEBT.md is current. Triggered deferrals are fixed: run `scripts/validate-profile.sh`, with `--strict` for an operational project and before exposure grows. An entry that nobody will act on is closed with its reason rather than kept as noise.
- **The design**, for a project with screens: code follows the recorded styling source; every implemented screen has its artifact entry; the published view or the working files are not behind the source of truth; the capture sets match the shipped screens; the interface's words match the vocabulary (#27, #31). Run `scripts/validate-design.sh --required known-screen`.
- **Discovery.** Shared components stay discoverable through the project's chosen method, and every deprecated shared contract has its removal trigger (#22).
- **Standing choices.** Convention departures and critical lessons in References.md still apply.
- **The framework's consistency**, before pulling an update: `./archetype/scripts/validate-framework.sh`.

Record what the look found where the project records it: TECHNICAL-DEBT.md for what stays open, the decision location for changed decisions, and a line in feature-tree.md's Audit Log when the project keeps one. A failing check is fixed, or set aside openly with its reason (AGENTS.md); it is never left failing unremarked.

## Incidents

After a failed release, a production defect traced to a broken rule, or a session that went notably wrong:
1. Fill in `templates/session-review.md` and save it as `docs/reviews/YYYY-MM-DD-topic.md`.
2. Decide whether the cause is the project's or the framework's.
3. The project's: fix it now, or log it in TECHNICAL-DEBT.md with its severity.
4. The framework's: report it upstream (development/FEEDBACK.md), written out rather than linked to a project file. The loop closes when an update brings the fix and a later session review confirms it.

**Never** fix a framework problem silently in the project without also reporting it (development/MAINTAIN-RED-FLAGS.md, section 3).

## Convention evolution

When session reviews name the same gap again and again, or a review proposes a change to the guidance:
1. Read the reviews' "Suggested Convention Improvements" and "Where did the framework get in the way?" together.
2. Report the pattern upstream (development/FEEDBACK.md) with the change you propose: guidance to add, soften, merge or remove, a red flag, or a check. Guidance that got in the way counts as much as a gap.
3. After an update brings the change, confirm in a later session review that the pattern is gone.

## Debt

- An open entry is revisited when its area changes or its cost does. An entry that has sat unchanged through several looks gets a decision: fix it, raise its severity, or close it as won't-fix with the reason. The project may record in References.md how long an entry may wait before that decision.
- Deferrals (`Kind: deferral`, #30) follow their trigger, not an age: when the facts in PROFILE.md make the `Due-before` trigger true, the entry blocks, and `scripts/validate-profile.sh` fails until it is fixed. Renewing a date, relabeling the stage or won't-fix does not clear it. A deferral whose review date passes without its trigger firing gets a fresh review and a new date, with the reason.

## Keeping documents current

- When a feature's behavior, contract, errors or key decisions change, update its record.
- When a shared system changes, update its page in `docs/systems/`.
- When the structure changes (a new top-level folder, a new override or protocol), update References.md.
- Keep feature-tree.md's rows true: the systems each feature uses, its entry points and its status.

The checks confirm that records exist and that their paths are real. They do not read whether a record's content is still true; the session and the review do.

## The checks

- `./archetype/scripts/validate-framework.sh`, before pulling a framework update.
- `./archetype/scripts/validate-maintain.sh`, during a look: the map and the debt log against the project.
- `./archetype/scripts/validate-develop.sh`, before merging feature work: the boundaries and the feature records.
- `./archetype/scripts/validate-profile.sh`, as #30 says.
- `./archetype/scripts/validate-scaffold.sh`, after adding or materially changing a foundational system.
- `./archetype/scripts/validate-design.sh --required known-screen`, for a project with screens.
