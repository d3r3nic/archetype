# Updating the installed framework

Read when a project pulls a newer framework. It says who owns which file, what the updater does to each, and what the session does before and after.

## Who owns what

- Framework-owned, replaced by every update: the engine folder, and the two root entry files. Root `AGENTS.md` holds the framework's rules. Root `CLAUDE.md` is a short pointer to it, kept because some hosts load only that name. Both carry the managed marker on their first line.
- Project-owned, never replaced: `CLAUDE.md.additions` (this project's own standing rules, read right after `AGENTS.md`), `References.md`, `PROFILE.md`, `feature-tree.md`, `PROGRESS.md`, `conventions/overrides/`, `protocols/`, `catalogs/`, `docs/`.

A project's own rule goes in `CLAUDE.md.additions`, never in a root entry file.

## Before

Commit or stash the project's work so the update is one reviewable change. Run `archetype/scripts/validate-framework.sh`; a failure now is not the update's fault.

## Run it

`./archetype/update.sh` from the project root. It shows what will change and waits for a yes. An install older than the carry-forward behaviour below is updated by its old updater on the first run, which replaces itself last: run it a second time, and on that first run protect the root files yourself (see "Older installs").

## What the updater does to the root entry files

- Root file identical to the engine's previous copy: replaced, nothing else happens.
- Root file with lines the project added: those lines are appended to `CLAUDE.md.additions` under a dated heading, the whole previous file is kept as `<name>.pre-update-<date>`, then the file is replaced. The preview says `CARRIED` with the line count.
- Root `AGENTS.md` without the managed marker (the project wrote its own): kept whole as `AGENTS.md.pre-update-<date>` and named in `CLAUDE.md.additions`, then the managed file is installed. The preview says `KEPT`.
- No root `AGENTS.md` at all (an install from before it existed): it is created. Nothing is done by hand.

Never restore a root entry file from version control after an update: that puts old rules over a new engine. The project's words are already in `CLAUDE.md.additions`.

## After

1. Audit every carried-over line in `CLAUDE.md.additions`: keep it there, move it to `References.md` or `conventions/overrides/`, or retire it because the current rules cover it. Record the reason for a retirement at the decision location. Remove the dated heading when done; delete the `.pre-update` copy once nothing in it is still needed.
2. Run `archetype/scripts/validate-framework.sh`, `scripts/validate-profile.sh`, and for a project with a screen `scripts/validate-design.sh`. A newer release can add lines a project record must carry; the check names them.
3. Run the project's own verification commands. Commit the update as one change, with the installed revision from `VERSION-LOG.md` in the message.

## Older installs

An updater from before this behaviour overwrites root `CLAUDE.md` without carrying anything. Before its first run, compare root `CLAUDE.md` with `archetype/CLAUDE.md`; move any line only the root has into `CLAUDE.md.additions` by hand. Then run the updater twice.
