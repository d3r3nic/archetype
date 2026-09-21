# Frontend scaffold: state management

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

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
