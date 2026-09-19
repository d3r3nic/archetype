# Frontend scaffold: state management

Part of the frontend scaffold playbook (scaffolding/SCAFFOLD-FRONTEND.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step. Before building, read the conventions it names and write how the system will be built in its References.md section (scaffolding/_preamble.md); when it lands, update its feature-tree.md row and its docs/systems/ page.

## Step 5: State management
Read: #5; #9; scaffolding/_preamble.md § Convention-mapping rule
Produces: the client-state and server-state setup the conventions describe
Check: run project: typecheck, lint, build; evidence: what was seen when this was tried: a test slice dispatching and reading, and a server-state fetch caching and deduplicating

Build:
- Global store configured (for global-state needs — auth, theme, app-level UI state).
- Server-state library configured (a caching query client for the chosen stack — research current options).
- Slice/module pattern per feature (each feature owns its store slice).
- Pattern for syncing server state with cache invalidation.

**Verify:** a test slice dispatches and reads correctly. Server-state fetch caches and dedupes.
