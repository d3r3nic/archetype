# Updating the installed framework

Read when a project pulls a newer framework. It says who owns which file, what the updater does to each, and what the session does before and after. The engine folder is `archetype/` by default; the updater prints its real path.

## Who owns what

- Framework-owned, replaced by every update: the engine folder, and the two root entry files. Root `AGENTS.md` holds the framework's rules. Root `CLAUDE.md` imports it, so a host that loads only that name loads the rules too. Both carry the managed marker on their first line.
- Project-owned, never replaced: `CLAUDE.md.additions` (this project's own standing rules; `AGENTS.md` routes every session to it first), `References.md`, `PROFILE.md`, `feature-tree.md`, `PROGRESS.md`, the project-root `conventions/` folder with `conventions/overrides/`, `protocols/`, `catalogs/`, `docs/`. The framework's conventions live only in the engine folder.

A project's own rule goes in `CLAUDE.md.additions`, never in a root entry file.

## Before

Commit or stash the project's work so the update is one reviewable change. Run the engine's `scripts/validate-framework.sh`; a failure now is not the update's fault.

## Run it

`./archetype/update.sh` from the project root. It shows what will change and waits for a yes; nothing is written before the answer. An install older than the behaviour below is updated by its old updater on the first run, which replaces itself last: run it a second time, and before that first run protect the project's files yourself (see "Older installs").

## What the updater does

Each root entry file is compared with a baseline: the engine's copy from before the update, or, in a full clone (the engine folder is the project root) or where the engine never carried the file, the file at the framework revision `VERSION-LOG.md` records, when that entry holds a full revision id (an older install recorded a short one, which cannot be fetched, and gets the no-baseline case below). Carriage returns and blank lines do not count as changes.

- Root file that matches the baseline: replaced, nothing else happens.
- Root file with lines the project added: those lines are appended to `CLAUDE.md.additions` under a dated heading, the whole previous file is kept as `<name>.pre-update-<date>`, then the file is replaced. The preview says `CARRIED` with the line count. A line the additions file already holds is not carried again.
- Root file with framework lines removed, reordered, or repeated and nothing new to carry: the previous file is kept as `<name>.pre-update-<date>` and a dated block in `CLAUDE.md.additions` asks for a review of that change. The preview says `KEPT`.
- No baseline can be found: the previous file is kept whole and `CLAUDE.md.additions` names it; the lines are not separated for you. The preview says `KEPT`.
- Root `AGENTS.md` without the managed marker (the project wrote its own): kept whole and named the same way. The preview says `KEPT`.
- A missing root `AGENTS.md` or `CLAUDE.md` is created. The preview says `NEW`.
- Legacy records the engine folder still holds: an engine `VERSION-LOG.md` with no project log beside it moves to the project root. When both exist, an engine copy with the same text (carriage returns ignored) is removed, and a different one is added to the project's log under a dated heading, indented, then removed. An engine `FRAMEWORK-SOURCE.md` is removed only when the same text is already at the project root; otherwise it is kept there first as `FRAMEWORK-SOURCE.md.pre-update-<date>`. The preview says `MOVE`, `REMOVE`, or `KEPT`.
- `VERSION-LOG.md`: update entries inside a Bootstrap section (older setup instructions put a second Bootstrap section after Updates, where later entries landed), each a dated heading followed by exactly its `Commit`, `Source` and `Updated by: update.sh` lines, move unchanged and in order to the end of the log under `## Updates`; nothing else in the log moves or changes, and the preview says `MOVE` with the count. The new entry goes under `## Updates`, after a new heading when the log ends in another section. A heading inside a fenced block or on an indented line does not count; a fenced block that never closes stops the update before the prompt, with nothing written.
- The project-root `conventions/` folder: earlier updates copied the framework's conventions into it, where nothing reads them. Each copy whose content matches the framework's, before or after this update, is removed; the preview says `REMOVE` with the count. A file with a framework convention's name but other content looks like a project edit: it stays, the preview says `KEPT`, and a dated block in `CLAUDE.md.additions` names it once. Every other file there, and all of `conventions/overrides/`, is left alone. The framework's conventions are never copied there.

Everything the project keeps or carries is written before anything is replaced; if it cannot be written the update stops with nothing replaced. A listing, hashing, or history step that fails stops the update before the prompt, with nothing written (the optional lookup of the recorded revision aside, described below); so does a legacy record (an engine `VERSION-LOG.md` or `FRAMEWORK-SOURCE.md`, or a project-root file used to prove one a duplicate) that is a symbolic link or not a regular file.

In a full clone (an older layout, where the framework's own files and folders sit at the project root):

- A root `README.md` that differs from the framework's is kept as `README.md.pre-update-<date>` before it is replaced; the preview says `KEPT`. It is not a rule, so nothing goes to `CLAUDE.md.additions`.
- The framework folders (conventions, backend, frontend, bootstrap, scaffolding, development, templates, scripts), the root `Conventions.md`, and `inject.sh` are replaced. A file there belongs to the framework only if the framework shipped exactly that content at that path in some revision of its history, which the updater fetches; a copy that differs only by carriage returns before line feeds, as some checkouts store files, counts as the same content. Any other file stops the update before the prompt, named, with nothing written: a project file, a file at a path the framework has started shipping, an edited framework file (still shipped or retired), or a symbolic link. `conventions/overrides/` and operating-system or interpreter caches do not count. Move project files out; move an edit into `conventions/overrides/`, `CLAUDE.md.additions`, or a project-owned file and undo it (a file inside a framework folder may be deleted instead, and the update restores it); or move the project to the engine-folder layout. If the framework's branch and tag history cannot be fetched, the update stops; the revision `VERSION-LOG.md` records is fetched too when it can be, and when it cannot, a file only it would have vouched for stops the update like any unmatched file. Hashing reads each file's raw bytes (line endings aside) and never runs the project's git filters. A full-clone update needs network access to the framework's history.

Never restore a root entry file from version control after an update: that puts old rules over a new engine. The project's words are in `CLAUDE.md.additions` or in the kept `.pre-update` copy it names.

## After

1. Review what the update added to `CLAUDE.md.additions`. For each carried line: keep it there, move it to `References.md` or `conventions/overrides/`, or retire it because the current rules cover it, and record the reason for a retirement at the decision location. For a kept reshaped file: decide whether what the project removed or reordered still matters, and record it the same way. For an edited convention named there: move what the project still needs into `conventions/overrides/` with the reason, then delete the file. Remove each dated heading when done; delete a `.pre-update` copy once nothing in it is still needed. In a full clone, bring the project's text back from a kept `README.md` copy. Read a dated heading the update added to `VERSION-LOG.md` and any kept `FRAMEWORK-SOURCE.md` copy, and keep what the project's history needs.
2. Run the engine's `scripts/validate-framework.sh`, `scripts/validate-profile.sh`, and for a project with a screen `scripts/validate-design.sh`. A newer release can add lines a project record must carry; the check names them. A project that installed the framework's hook guard also runs `scripts/check-hooks.py`: it names a guard command that no longer starts (quote its path placeholder as the settings templates do), a registration of the retired turn-end reminder (remove it), and a settings file git ignores; change only those entries of the project's settings.
3. A release can change how a project record is written, and the check that reads it names the change. Since the release that made recorded commands explicit, References.md § Commands holds each command in backticks: the step runner refuses an unmarked value and says how to write it. Run the project's own verification commands. Commit the update as one change, with the installed revision from `VERSION-LOG.md` in the message.

## Older installs

An updater from before this behaviour runs first on the next update and replaces itself last. It overwrites both root entry files without carrying anything, and it replaces the project-root `conventions/` folder with the framework's conventions, keeping only `conventions/overrides/`. Before that first run: compare root `CLAUDE.md` and root `AGENTS.md` with the engine's copies and move every line only the root file has into `CLAUDE.md.additions`; move any file of the project's own out of the project-root `conventions/` folder, and any edit of a framework convention into `conventions/overrides/`; copy an engine `VERSION-LOG.md` or `FRAMEWORK-SOURCE.md`, if the engine folder still has one, to the project root under a name of its own, because the older updater deletes both. Then run the updater twice; the second run removes the convention copies the first one put back.
