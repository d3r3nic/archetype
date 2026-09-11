# Pulse Monitor — Project Spec

This doc is the DURABLE spec of the project's pulse monitor. The UI is the expirable/replaceable layer; this doc is the contract. If the UI is redesigned, the data contract below stays the same.

## What it shows

Read-only snapshot of the scaffolded state. Five sections plus drift:

1. **Project overview** — name, purpose, stage. Sourced from `References.md § Project`.
2. **Tech stack** — framework, language, database, libraries. Sourced from `References.md § Tech Stack`.
3. **Foundational systems** — each scaffolded system with convention number, location, status. Sourced from `feature-tree.md § Foundational Systems`.
4. **Features** — each feature with routes, location, status. Sourced from `feature-tree.md § Features`.
5. **Architecture** — folder structure. Sourced from `References.md § Folder Structure`.
6. **Drift** — declared state compared with the actual filesystem. See "Drift detection" below.

## How to use it

### Generate the state snapshot

Run the inspector from the project root:

```
./archetype/scripts/pulse-inspect.sh --out .pulse-state.json
```

This reads `References.md` and `feature-tree.md`, scans the source tree, and emits `.pulse-state.json` conforming to the data contract below.

### View the UI

The starter UI is in `archetype/templates/pulse-ui/` (framework source: plain HTML, CSS, and JS). The scaffold copied or served it at a project-specific path — see "Where it's served" below.

Open the UI in a browser; click Refresh to re-fetch `.pulse-state.json`. If state is stale, re-run the inspector.

### Refresh model

Manual: re-run `pulse-inspect.sh` then click Refresh. Chaining the inspector to the dev-server start command means every session begins with fresh state. A file watcher is a project choice, not a default.

### Where it's served

Fill in during scaffold:

- **Backend projects:** a dev-only route that serves the UI and the snapshot. The route is registered only when the runtime is in development mode; production builds never register it.
- **Frontend projects:** a dev-server-only route or static path. Production builds exclude the pulse UI.
- **Mobile projects:** runs as a local web page on the developer's machine, served by any static file server. Not bundled into the mobile app itself.
- **Platform projects:** N/A — no dev environment in the code sense. Skip.

Document the exact serve path for this project here:

```
(fill in after scaffold: actual dev-only path, how to start it, how to stop it)
```

## Implementation notes

Read before wiring the serve path:

- **Bundlers that refuse to follow external symlinks.** If the framework folder is symlinked to a sibling location (for example one framework checkout shared across several templates), a bundler with strict asset tracing may reject paths that escape the project root. Consequence: a server-rendered page cannot read the framework's UI files from the symlinked folder at build time. Signal: do not embed the starter UI by reading it from the framework folder. Either render a project-local page that fetches a static `.pulse-state.json` asset, or serve the starter UI via a separate static server. Either preserves the data-contract-is-stable rule (the UI is replaceable).
- **Snapshot location.** Store `.pulse-state.json` where the project's dev server serves static assets (wherever that is for the chosen stack). Git-ignore it — it's generated.
- **Monorepo layouts.** The inspector scans both a single-app layout (`src/features/*/`, `src/shared/*/`) and a multi-app layout (`apps/*/src/features/*/`, `apps/*/src/shared/*/`, union across apps). Declared rows in feature-tree.md are matched against the union.

## Data contract (`.pulse-state.json`)

`dataContractVersion` identifies the shape. The inspector and the UI must agree on it; bump it whenever the shape changes, and update this section in the same change.

```json
{
  "generatedAt": "2026-04-17T23:00:00Z",
  "dataContractVersion": "v2",
  "project": {
    "name": "string",
    "purpose": "string",
    "stage": "string"
  },
  "techStack": [
    { "key": "Runtime", "value": "string" },
    { "key": "Language", "value": "string" }
  ],
  "foundationalSystems": [
    {
      "num": "1",
      "name": "project-structure",
      "convention": "#1, #7",
      "location": "src/",
      "status": "configured"
    }
  ],
  "features": [
    {
      "name": "record-session",
      "location": "src/features/sessions/",
      "routes": "POST /sessions"
    }
  ],
  "architecture": "multi-line string with the folder-tree code block from References.md",
  "drift": {
    "features": {
      "declaredButMissing": ["record-session"],
      "actualButUndeclared": ["health", "sessions"]
    },
    "foundationalSystems": {
      "declaredButMissing": [],
      "actualButUndeclared": []
    }
  }
}
```

## Drift detection

The inspector scans the actual filesystem against declared state:
- **Features:** feature directories vs the feature-tree.md Features table.
- **Foundational systems:** shared-module directories vs the feature-tree.md Systems table.

Matching is fuzzy (case-insensitive, non-alphanumeric characters normalized, substring-tolerant) to reduce false positives from naming-style differences. The UI renders a dedicated Drift section when any issues exist and hides it when clean.

Not covered, by design: dependency drift (manifest vs actual imports), env-var drift (schema vs runtime reads), route drift (router config vs handlers), migration drift. Each would extend the scanner the same way. Add one when real use demands it; extend the contract first.

## Redesigning the UI

The starter UI is deliberately minimal. Redesign freely:

- Swap the UI for your project's stack.
- Change the layout, typography, theming.
- Add sections — extend the data contract first, then the UI.

Rules for the redesign:
- **Keep the data contract stable** — the inspector is the source of truth for the snapshot shape. If the UI needs new data, extend the inspector + contract first.
- **Stay read-only** — the pulse monitor never writes to declared state.
- **Stay dev-only** — never ship the pulse UI to production builds. Auth leaks and internal-layout leaks are the risk.

## How to audit the pulse (developer workflow)

The framework does NOT ship a separate AI audit service. You audit ad-hoc with your own developer AI when:
- A major feature just landed
- You just ran `update.sh` to pull framework changes
- The drift section shows unexpected items
- Something feels off and you want a second opinion

Sample prompt to paste into your AI:

```
Read /path/to/project/.pulse-state.json. Compare it to the actual state of
/path/to/project/src/ and the dependency manifest. Tell me what the
pulse is misrepresenting — what's wrong, missing, or misleading. Read-only;
do not modify files. Report findings, then I decide what to fix.
```

The AI interprets stack-specific context, judges whether naming differences are cosmetic or structural, and flags issues the static scanner can't see. Human reviews, decides, fixes.

Audits are optional. The static scanner and drift surface cover the common case; the AI audit covers the cases where context matters.

## Known limitations

- Manual refresh only unless the project adds a watcher.
- Inspector assumes convention-compliant markdown structure. Projects that deviate from the convention (e.g., rename section headers) need to either align or customize the inspector locally.
- No historical snapshots. Each run overwrites `.pulse-state.json`.
- Drift matching is structural, not semantic; the ad-hoc AI audit covers judgment calls.
