# Steps: read, do, and check one step at a time

Framework-managed in downstream installations. Local AI must not edit this file; the next framework update overwrites it.

A playbook is a list of steps. A session holds one step at a time: it reads what that step names, does it, leaves what it produces, and closes it on a check. The rulebook can be any size, because no session is asked to hold it; the full text of a convention is read at the step that uses it, never earlier and never as a summary.

Telling a session not to read everything does not work; a session that does not know what it will need reads widely to be safe, and has lost the relevant part by the time it matters. The step names the reading, so there is nothing to guess.

## A step in a playbook

A playbook that works this way carries one line near its top, `Step ledger: <id>`, a short lower-case name for its steps in a project's ledger (`Step ledger: <id> (per feature)` when the steps run again for every feature). Each step is a heading, `## Step 3: Title` or `### Step 2.4: Title`, and directly under it:

- `Read:` what to read for this step, separated by semicolons: a convention by number (`#8`, or `#8 § Rules` for one section), an engine file by its path, a project file as `project: References.md § Commands`, or `none`. Only these. A convention another step needs is that step's reading.
- `Produces:` the files and the labelled lines the step leaves behind.
- `Check:` how the step closes. `run scripts/<script> [arguments]` for a check a script performs, run from the project root; otherwise `evidence:` and what is recorded, in whose words (`evidence: the owner's answers to this group, quoted`).
- `Required: yes` on a step that may not be skipped. Without it, a step that does not apply is skipped with its reason recorded.

The body under those lines is the doing, written as fully as it needs. A step with sub-steps (2 with 2.1 and 2.2) is a container: only its sub-steps open and close.

## The ledger

A project carries `PROGRESS.md`, from templates/progress.md: the playbooks it follows, in order, and one line per closed step with the date, the revision, and the check that passed or the evidence given. It is where a session starts, where it resumes after losing its context, and what one session hands the next.

`scripts/next-step.sh`, run from the project root:

- with no arguments, names the first open step, its playbook and line, its reading, what it produces, and its check;
- `--close <id>` closes that step: it runs the step's check and writes the line only when the check passes; a step that closes on evidence needs `--evidence` with the text; steps close in order;
- `--skip <id> --reason <text>` records a step that does not apply, and refuses a required one;
- `--unit <name>` selects one run of a repeating playbook (one feature);
- `--list` shows every step with its state.

Every run first re-runs the checks of the steps the ledger says are closed. If one fails, the script says which step is reopened and names no next step until it passes again. A tick is a check that passes now, not a claim made once.

Work that began before the ledger existed closes its finished steps one at a time, oldest first; each check still has to pass, and the evidence says the step predates the ledger.

## Evidence, where no script can check

A conversation cannot be checked by a script. A step that turns on one (a group of discovery questions, the owner's pick of a direction) closes on the owner's own words, quoted, or on "declined" with what was assumed in its place. That does not prove a question was asked. It leaves something an owner or a reviewer can read in a minute and recognize or not, which a session's paraphrase does not.

## What the framework checks, and what it cannot

`scripts/next-step.sh --lint`, which the framework self-test runs, checks every playbook that declares a step ledger: each step has exactly one `Read:`, `Produces:`, and `Check:` line, every engine path and convention number under `Read:` exists, every `run` check names an engine script that exists and nothing else, and no step id repeats. It does not check a playbook that has not declared a ledger, and no script checks that a session read what a step named, that a step was done well, that quoted evidence is what the owner said, or that nobody edited the ledger by hand. The independent review reads the ledger (#29).
