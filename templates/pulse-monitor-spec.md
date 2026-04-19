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

## v2 — static drift detection (shipped)

Inspector scans actual filesystem against declared state. Current coverage:
- **Features:** `src/features/*/` dirs vs feature-tree.md Features table.
- **Foundational systems:** `src/shared/*/` dirs vs feature-tree.md Systems table.

Drift surfaces in `.pulse-state.json` as:

```json
"drift": {
  "features": {
    "declaredButMissing": ["record-session"],
    "actualButUndeclared": ["health", "sessions"]
  },
  "foundationalSystems": { ... }
}
```

UI renders a dedicated "Drift" section when any issues exist (hidden when clean). Declared-but-missing + actual-but-undeclared lists with tight visual treatment.

Future (v3+, add when real use demands): dependency drift, env-var drift, route drift, migration drift.

## How to audit the pulse (developer workflow)

The framework does NOT ship a separate AI audit service. You audit ad-hoc with your own developer AI when:
- A major feature just shipped
- You just ran `update.sh` to pull framework changes
- The drift section shows unexpected items
- Something feels off and you want a second opinion

Sample prompt to paste into your AI:

```
Read /path/to/project/.pulse-state.json. Compare it to the actual state of
/path/to/project/src/ and /path/to/project/package.json. Tell me what the
pulse is misrepresenting — what's wrong, missing, or misleading. Read-only;
do not modify files. Report findings, then I decide what to fix.
```

The AI interprets stack-specific context (Python vs TypeScript vs Go), judges whether naming differences are cosmetic or structural, and flags issues the static scanner can't see. Human reviews, decides, fixes.

Audits are optional. The static scanner + drift surface cover the 80% case. The AI audit covers the 20% where context matters.

## Known limitations (v1)

- No drift detection — pulse is a snapshot of DECLARED state, not actual.
- Manual refresh only (no watch mode).
- Inspector assumes convention-compliant markdown structure. Projects that deviate from the convention (e.g., rename section headers) need to either align or customize the inspector locally.
- No historical snapshots. Each run overwrites `.pulse-state.json`.
