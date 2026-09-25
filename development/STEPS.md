# Steps: read, do, and check one step at a time

Framework-managed in downstream installations. Local AI must not edit this file; the next framework update overwrites it.

A declared playbook names the current step, relevant reading, intended outputs and closure checks. Use it within its declared scope and reuse context that is still current. Other work follows the implementer-plan procedure in development/TASKS.md; it does not acquire automated recovery merely by being written as a checklist.

Named reading helps a session locate relevant guidance. It does not prove the guidance was read, that all relevant concerns were named, or that the work was done well.

## A step in a playbook

A playbook that works this way carries one line near its top, `Step ledger: <id>`, a short lower-case name for its steps in a project's ledger (`Step ledger: <id> (per feature)` when the steps run again for every feature). A file is what a session opens, whatever line it is pointed at, so a step gets a file of its own, or shares one with a few small neighbours: the entry file keeps the opening and the first step, and lists the rest in order on one line, `Step files: bootstrap/ONBOARD-2.1-WHAT-IS-IT.md; bootstrap/ONBOARD-2.2-WHERE-IT-RUNS.md`. The step files carry no ledger line of their own. A long playbook in one file is read whole before its first step, and the point of the steps is lost.

Each step is a heading, `## Step 3: Title` or `### Step 2.4: Title`, and directly under it:

- `Read:` what to read for this step, separated by semicolons (so a section name holds none): a convention by number (`#8`, or `#8 § Rules` for one section), an engine file by its path, a project file as `project: References.md § Commands`, or `none`. An entry that applies only in some projects says when, in brackets at its end: `templates/references-mobile.md (when a custom build is a mobile app)`; the session reads it only then. Only these. A convention another step needs is that step's reading.
- `Produces:` the files and the labelled lines the step leaves behind.
- `Check:` how the step closes. `run scripts/<script> [arguments]` for a check an engine script performs, run from the project root, passing when it exits 0 (`scripts/check-exists.sh <paths>` where the check is that a file the step produces is there; arguments may name paths inside the project, never above it). `run project: typecheck, lint, test` for the project's own commands: each label is looked up in References.md § Commands, where its line (or its list item, after `- ` or `* `) holds the command in backticks, then any note (`` test: `<command>` what it covers ``); the command between the backticks is run as written, and the note never is. A value in brackets means no command is recorded yet and fails, as does a value that does not open with a command in backticks or holds more than one pair of them, so text outside the backticks is never run; `none` or `n/a`, plain or in backticks, recorded for a label the project has no use for is passed over. `evidence:` and what is recorded, in whose words, where no command can tell (`evidence: the owner's answers to this group, quoted`). A command and evidence together where a step needs both: `run project: typecheck, lint; evidence: what was seen when an error was thrown inside a component`.
- `Skip when:` the one condition under which the step does not apply (`Skip when: the build approach is a platform`). A step without this line cannot be skipped: skipping is the exception the playbook's author foresaw, never the session's own idea.
- `Depends on:` optional direct prerequisite step IDs, separated by semicolons. The recovery tool follows these edges transitively. The lint rejects unknown targets and cycles.
- `Basis:` optional enforcement for work whose evidence can become stale: `decisions required`, `inputs required`, or `decisions and inputs required`. Closing or skipping such a step supplies the named records with `--basis DEC-NNN` and project files with `--input PATH`.

These lines sit directly under the heading, before any sub-heading. The body under them is the doing, written as fully as it needs. A step with sub-steps (2 with 2.1 and 2.2) is a container: only its sub-steps open and close.

## The ledger

A project carries `PROGRESS.md`, from templates/progress.md: the playbooks it follows, in order, and append-only close, skip, and reopen events. A close or skip records the revision, project-relative working directory, original References.md command owner, unit, declared decision fingerprints, input content fingerprints, and evidence. The latest event for a step and unit is current. Git keeps file history; this ledger keeps execution history.

`scripts/next-step.sh`, run from the project root:

- with no arguments, names the first open step, the file that holds it and the line, its reading, what it produces, and its check;
- `--close <id>` closes that step: it runs the step's check and writes the line only when the check passes; a step that closes on evidence needs `--evidence` with the text; steps close in order;
- `--skip <id> --reason <text>` records a step that does not apply, with the playbook's condition and how it holds here; it refuses a step whose playbook names no condition. A skipped step's check is never run;
- `--unit <name>` selects one run of a repeating playbook (one feature; a plain name, the feature's folder name);
- `--reopen <step-id-or-DEC-NNN> --reason <text>` appends reopen events for current closed or skipped work and every transitive declared dependant. Unknown targets, dependency cycles, and invalid declarations change nothing;
- `--basis <DEC-NNN>` and `--input <project-relative-path>` may repeat on close or skip. The tool fingerprints the decision, its transitive decision dependencies and supersession state, plus the exact file content. A Markdown input with `- Decision basis:` must name exactly the supplied decision IDs. Input paths may contain spaces, but not ledger delimiters, control characters, `@sha256:`, absolute paths, tildes, or parent traversal;
- `--list` shows every step with its state: open, closed, skipped, or reopened.

It runs from the project root or any folder under it. Engine checks always run at the project root. A historical project command runs with the unit, project-relative directory, and command owner recorded by that closure. The cache key includes command, directory, command owner, unit, and basis. A missing or escaping directory fails. A legacy project-command closure with no recorded directory is unverified when rechecked and must be closed again. Project commands are re-run whenever a step closes or skips, and on `--verify`, not on a bare run. Nothing from the ledger, a title, unit, reason, or evidence is executed.

Work that began before the ledger existed closes its finished steps one at a time, oldest first; each check still has to pass, and the evidence says the step predates the ledger.

## Evidence, where no script can check

A conversation cannot be checked by a script. A step that turns on one (a group of discovery questions, the owner's pick of a direction) closes on the owner's own words, quoted, or on "declined" with what was assumed in its place. That does not prove a question was asked. It leaves something an owner or a reviewer can read in a minute and recognize or not, which a session's paraphrase does not.

## What the framework checks, and what it cannot

`scripts/next-step.sh --lint`, which the framework self-test runs, checks every playbook that declares a step ledger: each step has exactly one `Read:`, `Produces:`, and `Check:` line, every engine path and convention number under `Read:` exists and every section named after `§` opens a heading of that file, every `run` check names an engine script that exists, or the project form with plain labels, and nothing else, no step id repeats across a playbook's files, no ledger id is declared by two playbooks, every step file listed exists inside the engine, is listed once, and declares no ledger of its own, and no heading that opens with "Step" fails to parse as one. It does not check a playbook that has not declared a ledger, and no script checks that a session read what a step named, that a step was done well, that quoted evidence is what the owner said, that a skip's reason is true, or that nobody edited the ledger by hand. The independent review reads the ledger (#29).
