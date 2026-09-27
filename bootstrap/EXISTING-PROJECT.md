# Existing Project Bootstrap

Routed from `ONBOARD.md` Step 4.1 when the framework is installed into a project that already has code or guidance of its own. Adoption records what exists, where each of the owner's rules now lives, and what the framework's later steps still need. It keeps everything the owner wrote and changes no code.

## Rules that hold throughout

- **Lose nothing the owner wrote.** Every existing rule, protocol and lesson gets a home, and `MIGRATION-NOTES.md` maps each original to it.
- **One home per rule.** A rule stays where it is and is linked, or it moves with its original wording; it is never copied into a second place that can drift (#0).
- **Originals untouched.** `inject.sh` kept the earlier entry files as `.pre-archetype` copies; every other file stays where it is.
- **No code changes during adoption.** A problem found in the code is recorded in `MIGRATION-NOTES.md` for later work, not fixed now.
- **Ask when unsure.** A document or rule whose status is unclear goes to the owner. With no owner available, decide from evidence (dates, self-labels such as "superseded", contradictions with the code) and record the decision so it can be reversed.
- **Read per step.** Read the project's own records first, and a convention when mapping the concern it covers; do not read the whole framework up front.

## Part A: What exists

1. Read the project's manifests, its top-level structure, its build and pipeline configuration, and its existing instruction files and documents, to learn the stack, the commands, the shared systems and the features.
2. Record each shared system the project has (errors, the API client, authentication, data access, configuration and so on) in References.md § Foundational Systems and as a feature-tree.md row with its real location. A system the project's facts call for but does not have gets a row marked `not started`; one its facts do not call for gets no row (each convention's Applies when decides).
3. Record each feature as a feature-tree.md row with its location and its record: an existing document when one describes it, or a new record from templates/feature-doc-template.md.
4. Record the commands in References.md § Commands.
5. For each shared system, record in § Boundaries what only it may use, as the code already works. A place that already goes around it is a finding for `MIGRATION-NOTES.md`, not something to fix now.

## Part B: The owner's rules

Read every existing instruction file in full: the `.pre-archetype` copies (not only the new managed entry points), an entry file not yet replaced, any rules or commands folder of an AI tool, documents that carry guidance, debt and handoff notes, and the external files these point to.

Give each rule one home:
- a standing rule for every session goes to project-root `CLAUDE.md.additions`, which the managed AGENTS.md reads first;
- a project rule for one concern, one that adds to or departs from a convention, goes to `conventions/overrides/{N}-{name}.md`, with its original wording and its source;
- a workflow protocol stays in its document when it has one, or moves to `protocols/{name}.md`;
- a reference catalog (a feature directory, a helper list) stays where it is and is listed in References.md § Project-Specific Documentation;
- a production lesson goes to References.md § Critical Lessons, or to the override for its concern.

Keep the original wording when a rule moves. Never summarize a rule into something weaker, and never keep the same rule in two places.

Write `MIGRATION-NOTES.md`: each original file and section, and where it lives now. Then walk each original from top to bottom and find every section in the map; a section with no home is a gap to close before the step does.

## Part C: The project's documents

Find the documents under any name: documentation folders, READMEs anywhere in the tree, decision-record folders, handoff and migration notes, links to an outside wiki. Leave them where they are. List each in References.md § Project-Specific Documentation with one line on what it holds, and link a system's or feature's existing document from its feature-tree.md row rather than writing a second one. Note in `MIGRATION-NOTES.md` each document that looks stale (it describes removed code or tools the project no longer uses), with why, for later cleanup; the document itself stays untouched.

## What adoption produces

- `References.md` from the matching template, filled from what was found: the project, the stack, the commands, § Boundaries, compliance, the foundational systems, critical lessons, departures from the conventions, and the project's own documentation.
- `References.md § Design Artifact` for a project with a screen, from what exists, with `unknown` where it could not be established and the direction of truth recorded as a decision (#27, #29). A back end alone records the section as not applicable in one line. A product whose `Brand decided` is not yes runs the design interview (`bootstrap/DESIGN-INTERVIEW.md`) with its owner, with what adoption found already filled in.
- `feature-tree.md` with the systems and features found and their real locations.
- In `References.md` § Project, the `Peer coding` line from the owner's Step 2.6 answer: `none`, or `peer-coding/SETTINGS.md`, set up with the engine's `scripts/peer-coding.py setup` and filled with the owner's answers and what adoption verified (`development/PEER-CODING.md`, Setting it up).
- `PROFILE.md` from `templates/profile.md`: the operating stage the evidence supports, every fact adoption could not establish marked `unknown`, the decision-authority setting the owner stated (`Authority source: owner-stated`), and today's date as Observed-on (#30, #29). If the owner was not asked or answered vaguely, record `owner-decides` with `Authority source: defaulted`: the team worked under approval rules until now, and nobody asked to change that.
- `CLAUDE.md.additions`, the override files and the protocol files that rules moved into, and only those.
- `MIGRATION-NOTES.md`: where each original rule lives now, the stale documents, and the findings to act on later.

Run the installed `scripts/validate-migration.sh` from the project root before committing. It checks that References.md, feature-tree.md and the map exist and that the owner's peer-coding answer is recorded, reports whether earlier entry files were preserved, and, for an adoption made under an earlier version that copied documents into `docs/migrated/`, that those copies still match their originals. It cannot tell whether every rule found a home; the walk through each original above does that, and the independent review reads the map.
