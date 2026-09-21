# Frontend scaffold: data resolution layer

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 10b: Data resolution layer
Read: #0; #9; scaffolding/_preamble.md § Convention-mapping rule
Produces: one resolver that pages call by function name, the only place data objects are named
Check: run project: typecheck, lint, test, build; evidence: what was seen when this was tried: the search for data object names outside the resolver
Skip when: the codebase holds no data of its own and every value arrives through the API layer

A feature's `data.ts` (or equivalent) is a **resolution function**, not a fixed data source. Pages call `listX()` / `findX(id)`; the function decides whether the data comes from hardcoded fixtures, a YAML file, a database, or a live API. When the real source lands, only `data.ts` changes — every page and component keeps working.

Rules:
- Pages and components NEVER import a data source directly. They import the resolution function.
- The resolution function is allowed to be async (most real sources are).
- Fallback behavior is explicit in the function (not magic): prefer real source when configured; else return a safe default (empty list, hardcoded fixture) for dev.
- Swapping the source is an isolated change. A PR that replaces hardcoded → real source should touch one file, not many.

**Verify:** grep for the names of data objects in the codebase. Only `data.ts` (or its named resolver) should appear; pages should only reference the function name.
