# Frontend scaffold: pulse monitor (dev-only project visibility)

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 11b: Pulse Monitor (dev-only project visibility)
Read: #26; templates/pulse-monitor-spec.md; scaffolding/_preamble.md § Convention-mapping rule
Produces: the dev-only pulse route and docs/systems/pulse-monitor.md; nothing of it in a production build
Check: run project: typecheck, lint, test, build; evidence: what was seen when this was tried: every section of the pulse route with real data, and the production build searched for the pulse files

Copy the framework's base UI into the project's dev-static path. Serve via a dev-only route. Production builds MUST exclude the pulse UI (tree-shaken out or route-guarded).

Build:
- Dev-only route (e.g., `/dev/pulse`), registered only when the runtime's environment flag says development, that serves the starter UI from `archetype/templates/pulse-ui/` via the stack's static or dev-middleware path.
- `.pulse-state.json` served as a sibling static file in the same dev route, from a project-owned path.
- A project task (the package manager's script runner, or equivalent) that runs `archetype/scripts/pulse-inspect.sh --out <project-owned path>/.pulse-state.json`.
- Create `docs/systems/pulse-monitor.md` from `archetype/templates/pulse-monitor-spec.md`; fill in the project-specific "Where it's served" section, and read that spec's implementation notes before wiring the serve path.

**Verify:** start the dev server, open the pulse route, confirm every section renders with real data. Verify the production build excludes the pulse UI.
