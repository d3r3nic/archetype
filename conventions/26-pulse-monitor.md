# Convention #26: Pulse Monitor

## Principle

The developer's pulse on the project. A dev-only surface that shows the scaffolded state — what framework and stack were chosen, what foundational systems were built, what features exist, what architecture emerged — without context-switching between git, docs, and the filesystem.

Vibecoding creates silent drift. AI agents add deps, create utilities, generate migrations, touch env vars, wire routes — and the developer wakes up not knowing what got built. The pulse monitor closes that blind spot.

Visibility is a first-class concern, not a DevOps afterthought.

## Reusable System

One dev-only surface per project. Read-only. Dev-only (never in production). Structure:
- A language-agnostic inspector that reads convention-mandated paths (`References.md`, `feature-tree.md`, `package.json` or equivalent) and emits a standard `.pulse-state.json` conforming to the documented data contract.
- A minimal UI that fetches `.pulse-state.json` and renders the sections. UI is expirable — redesign freely. Data contract is durable — changes break the spec.
- A `docs/systems/pulse-monitor.md` per project that documents both layers.

## Rules

- The pulse monitor is dev-only. Never exposed in production. No auth leaks, no data leaks.
- The inspector reads ONLY convention-mandated paths. If a project deviates from conventions, document the deviation in References.md; the inspector should still read from the new location via project-level override.
- The data contract is documented per the spec template and stable. UI layers consume it. Breaking the contract requires a spec update.
- The UI layer is explicitly replaceable. Per-project redesign is encouraged. The framework ships a vanilla HTML/CSS/JS starter; projects swap it for their stack if desired.
- The pulse monitor is read-only. Writes (e.g., "promote this feature to prod") are out of scope.
- Drift is surfaced but not auto-fixed. Declared-but-missing and actual-but-undeclared items display; the developer resolves them.
- **Periodic AI audit is a developer workflow, not a framework service.** After a major feature ships, after a framework update, or when drift looks suspicious, the developer asks their AI (the same one that coded the feature) to audit `.pulse-state.json` against the actual project state. The audit is ad-hoc, human-triggered, read-only. The framework does NOT ship a separate audit service.

## v1 scope — scaffolded state visibility

Five sections, all read from declared state:

1. **Project overview** — name, purpose, stage. From References.md § Project.
2. **Tech stack** — framework, language, database, libraries. From References.md § Tech Stack.
3. **Foundational systems** — each system with its convention number, location, status. From feature-tree.md § Foundational Systems.
4. **Features** — each feature with routes, systems used, status, doc path. From feature-tree.md § Features.
5. **Architecture** — folder structure. From References.md § Folder Structure.

## v2 — static drift detection (shipped)

The inspector scans actual filesystem against declared state in both layouts:
- **Single-app:** `src/features/*/` + `src/shared/*/` vs feature-tree.md rows.
- **Monorepo:** `apps/*/src/features/*/` + `apps/*/src/shared/*/` (union across apps). Step 48 added this.

→ `declaredButMissing` + `actualButUndeclared` arrays per section.

Matching is fuzzy (case-insensitive, non-alphanumeric normalized, substring-tolerant) to reduce false positives from naming-style differences.

Drift is surfaced in `.pulse-state.json` under the `drift` field and rendered in a dedicated UI section.

No language-specific AST parsing. No stack-specific rules. Static scanner stays portable. AI-level reasoning (if needed for nuanced cases) happens via the developer's own AI during ad-hoc audit — see Rules.

## Implementation gotchas (signals from battle-testing)

- **Bundlers that refuse to follow external symlinks.** If the framework folder is symlinked to a sibling location (e.g. a shared framework shared across several templates), a bundler with strict asset tracing may reject paths that escape the project root. Consequence: a server-rendered page cannot read the framework's UI files from the symlinked folder at build time. **Signal:** do not embed the framework's vanilla HTML/CSS/JS pulse UI by reading it from the framework folder. Either render a project-local page that fetches a static `.pulse-state.json` asset, or serve the framework UI via a separate static server. Either preserves the data-contract-is-stable rule (the UI is replaceable).
- **Refresh model.** v1 refresh is manual — rerun the inspector before viewing. Chaining the inspector to the dev-server start command means every session begins with fresh state.
- **Pulse state file location.** Store it where the project's dev server serves static assets (wherever that is for the chosen stack). Git-ignore it — it's generated.

## Future (v3+, not planned)

- Dependency drift (package.json vs actual imports).
- Env-var drift (schema vs `process.env.*` reads).
- Route drift (router config vs actual handlers).
- Migration drift.

Each extends the scanner similarly. Add when real-use signals demand them.

## Violations

- Exposing the pulse monitor in production (auth leak, internal layout leak).
- Writing to declared state FROM the pulse monitor (v1 is read-only).
- Coupling the UI layer to the inspector implementation (breaks the replaceability intent).
- Building the inspector in a project-specific language that won't run in other projects (inspector is language-agnostic; bash + portable shell tools).
- Adding data to `.pulse-state.json` without updating the spec contract.

## Wrong vs Right

- WRONG: developer opens 4 tabs (GitHub, deployment dashboard, logs, IDE) to answer "what systems does this project have?"
- RIGHT: developer opens `/dev/pulse` and sees the project's declared scaffolded state in one place.
- WRONG: pulse UI is React-specific and can only run in React projects.
- RIGHT: UI layer is swappable. Data contract is portable. A Python backend's pulse UI can be a Jinja-rendered page; a React frontend's can be a React route; same `.pulse-state.json` feeds both.
- WRONG: inspector hard-codes paths that only make sense in one project's layout.
- RIGHT: inspector reads convention-mandated paths + respects References.md deviations.

## Research Notes

When bootstrapping this convention:
- Decide where the pulse monitor is served in the project's stack — a dev-only route, a static-served path, a separate CLI, or a local companion window. Depends on project shape.
- Research a simple JSON-reader/renderer for the chosen stack if not using the framework's vanilla HTML starter.
- Decide the refresh model — on-page-load, on-manual-button, or file-watcher triggers re-inspect. Manual refresh is simplest for v1.
- Document the chosen serve path, refresh model, and any data-contract extensions in the project's `docs/systems/pulse-monitor.md`.

## Project Overrides

If a file exists at `conventions/overrides/26-pulse-monitor.md`, read it. It contains project-specific rules extending this base.
