# Updating the installed framework

Read when a project pulls a newer framework. It says who owns which file, what the updater does to each, and what the session does before and after.

## Who owns what

- Framework-owned, replaced by every update: the engine folder, and the two root entry files. Root `AGENTS.md` holds the framework's rules. Root `CLAUDE.md` is a short pointer to it, kept because some hosts load only that name. Both carry the managed marker on their first line.
- Project-owned, never replaced: `CLAUDE.md.additions` (this project's own standing rules; `AGENTS.md` routes every session to it first), `References.md`, `PROFILE.md`, `feature-tree.md`, `PROGRESS.md`, `conventions/overrides/`, `protocols/`, `catalogs/`, `docs/`.

A project's own rule goes in `CLAUDE.md.additions`, never in a root entry file.

## Before

Commit or stash the project's work so the update is one reviewable change. Run `archetype/scripts/validate-framework.sh`; a failure now is not the update's fault.

## Run it

`./archetype/update.sh` from the project root. It shows what will change and waits for a yes. An install older than the carry-forward behaviour below is updated by its old updater on the first run, which replaces itself last: run it a second time, and on that first run protect the root files yourself (see "Older installs").

## What the updater does to the root entry files

Each root file is compared with a baseline: the engine's copy from before the update, or, in a full clone (the engine folder is the project root) or where the engine never carried the file, the file at the framework revision `VERSION-LOG.md` records.

- Root file with no project lines: replaced, nothing else happens.
- Root file with lines the project added: those lines are appended to `CLAUDE.md.additions` under a dated heading, the whole previous file is kept as `<name>.pre-update-<date>`, then the file is replaced. The preview says `CARRIED` with the line count. A line the additions file already holds is not carried again.
- No baseline can be found: the previous file is kept whole and `CLAUDE.md.additions` names it; the lines are not separated for you. The preview says `KEPT`.
- Root `AGENTS.md` without the managed marker (the project wrote its own): kept whole and named the same way. The preview says `KEPT`.
- No root `AGENTS.md` at all (an install from before it existed): it is created. Nothing is done by hand.

The carry is written before anything is replaced; if it cannot be written the update stops with nothing replaced.

Never restore a root entry file from version control after an update: that puts old rules over a new engine. The project's words are in `CLAUDE.md.additions` or in the kept `.pre-update` copy it names.

## After

1. Audit every carried-over line in `CLAUDE.md.additions`: keep it there, move it to `References.md` or `conventions/overrides/`, or retire it because the current rules cover it. Record the reason for a retirement at the decision location. Remove the dated heading when done; delete the `.pre-update` copy once nothing in it is still needed.
2. Run `archetype/scripts/validate-framework.sh`, `archetype/scripts/validate-profile.sh`, and for a project with a screen `archetype/scripts/validate-design.sh` (in a full clone the same scripts sit under `scripts/`). A newer release can add lines a project record must carry; the check names them.
3. Run the project's own verification commands. Commit the update as one change, with the installed revision from `VERSION-LOG.md` in the message.

## Older installs

An updater from before this behaviour overwrites root `CLAUDE.md` without carrying anything. Before its first run, compare root `CLAUDE.md` with `archetype/CLAUDE.md`; move any line only the root has into `CLAUDE.md.additions` by hand. Then run the updater twice.
