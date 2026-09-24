# Frontend scaffold: pulse monitor (dev-only project visibility)

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 11b: Pulse Monitor (dev-only project visibility)
Read: #26; templates/pulse-monitor-spec.md; scaffolding/_preamble.md § Convention-mapping rule
Produces: the dev-only pulse route and docs/systems/pulse-monitor.md; nothing of it in a production build
Check: run project: typecheck, lint, test, build; evidence: what was seen when this was tried: every section of the pulse route with real data, the production build output's files listed, hidden files included, with no snapshot and no pulse UI file, its contents searched for `Archetype pulse UI` with no match, and the production server not answering the pulse route

Serve the framework's base UI and the snapshot through a dev-only route, from paths outside every folder the production build copies; a dev server's public static folder is one of those on common stacks. Production builds contain neither (#26, and the location note in templates/pulse-monitor-spec.md).

Build:
- Dev-only route (e.g., `/dev/pulse`), registered only when the runtime's environment flag says development, that serves the starter UI from `archetype/templates/pulse-ui/` through the stack's development middleware.
- `.pulse-state.json` served by the same dev route, from a project-owned, git-ignored path outside every published folder.
- A project task (the package manager's script runner, or equivalent) that runs `archetype/scripts/pulse-inspect.sh --out <project-owned path>/.pulse-state.json`.
- Create `docs/systems/pulse-monitor.md` from `archetype/templates/pulse-monitor-spec.md`; fill in the project-specific "Where it's served" section, and read that spec's implementation notes before wiring the serve path.

**Verify:** start the dev server, open the pulse route, confirm every section renders with real data. List the production build output's files, hidden files included, and search its contents for `Archetype pulse UI`; a snapshot, a pulse UI file, or a match means the build publishes the monitor. The route answers only in development, at a trailing-slash address (templates/pulse-monitor-spec.md).
