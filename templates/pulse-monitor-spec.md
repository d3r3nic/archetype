# Pulse Monitor — Project Spec

This doc is the DURABLE spec of the project's pulse monitor. The UI is the expirable/replaceable layer; this doc is the contract. If the UI is redesigned, the data contract below stays the same.

## What it shows (v1)

Read-only snapshot of the scaffolded state. Five sections:

1. **Project overview** — name, purpose, stage. Sourced from `References.md § Project`.
2. **Tech stack** — framework, language, database, libraries. Sourced from `References.md § Tech Stack`.
3. **Foundational systems** — each scaffolded system with convention number, location, status. Sourced from `feature-tree.md § Foundational Systems`.
4. **Features** — each feature with routes, location, status. Sourced from `feature-tree.md § Features`.
5. **Architecture** — folder structure. Sourced from `References.md § Folder Structure`.

Drift detection (declared-vs-actual) is v2 — not yet implemented.

## How to use it

### Generate the state snapshot

Run the inspector from the project root:

```
./archetype/scripts/pulse-inspect.sh --out .pulse-state.json
```

This reads `References.md` and `feature-tree.md` and emits `.pulse-state.json` conforming to the data contract below.

### View the UI

The UI is in `archetype/templates/pulse-ui/` (framework source). The scaffold copied or served it at a project-specific path — see the "Where it's served" section below for this project's path.

Open the UI in a browser; click Refresh to re-fetch `.pulse-state.json`. If state is stale, re-run the inspector.

### Refresh model

Manual: re-run `pulse-inspect.sh` then click Refresh. No file watcher in v1.

### Where it's served

Fill in during scaffold:

- **Backend projects:** Dev-only route — `GET /dev/pulse` serves the UI; `GET /dev/pulse/.pulse-state.json` serves the state. Route is registered ONLY in dev mode (check `NODE_ENV !== 'production'`).
- **Frontend projects:** Vite dev-only route or static path — typically `http://localhost:5173/dev/pulse/`. Production build excludes the pulse UI.
- **Mobile projects:** Runs as a local web page on the developer's machine (serve via `npx http-server archetype/templates/pulse-ui/` or equivalent). Not bundled into the mobile app itself.
- **Platform projects:** N/A — no dev environment in the code sense. Skip.

Document the exact serve path for this project here:

```
(fill in after scaffold: actual dev-only path, how to start it, how to stop it)
```

## Data contract (`.pulse-state.json` v1)

```json
{
  "generatedAt": "2026-04-17T23:00:00Z",
  "dataContractVersion": "v1",
  "project": {
    "name": "string",
    "purpose": "string",
    "stage": "string"
  },
  "techStack": [
    { "key": "Runtime", "value": "Node.js 24" },
    { "key": "Language", "value": "TypeScript 5 strict" }
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
  "architecture": "multi-line string with the folder-tree code block from References.md"
}
```

## Redesigning the UI

The vanilla HTML + CSS + JS in `archetype/templates/pulse-ui/` is deliberately minimal. Redesign freely:

- Swap the UI for your project's stack (React, Vue, Svelte, etc.).
- Change the layout, typography, theming.
- Add sections (e.g., for v2 drift detection) — extend the data contract first, then the UI.

Rules for the redesign:
- **Keep the data contract stable** — the inspector is the source of truth for `.pulse-state.json` shape. If the UI needs new data, extend the inspector + contract first.
- **Stay read-only in v1** — writes are a v2 feature.
- **Stay dev-only** — never ship the pulse UI to production builds. Auth leaks and internal-layout leaks are the risk.

## v2 (deferred) — drift detection

Planned additions:
- Features: declared in feature-tree.md vs actual `src/features/*/` dirs. Surface undocumented features and stale rows.
- Systems: declared in References.md + feature-tree.md vs `src/shared/*/` dirs.
- Dependencies: declared in `package.json` vs actual imports across `src/`.
- Env vars: declared in env schema vs `process.env.*` references.
- Routes: declared in router config vs actual handler files.
- Migrations: declared in `prisma/migrations/` (or equivalent) vs current DB schema state.

Each adds a `drift` array to its section. UI surfaces drift visibly.

Not in v1. Ship v1 first; add v2 when adoption signals it.

## Known limitations (v1)

- No drift detection — pulse is a snapshot of DECLARED state, not actual.
- Manual refresh only (no watch mode).
- Inspector assumes convention-compliant markdown structure. Projects that deviate from the convention (e.g., rename section headers) need to either align or customize the inspector locally.
- No historical snapshots. Each run overwrites `.pulse-state.json`.
