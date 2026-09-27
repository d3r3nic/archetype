# Frontend scaffold: data resolution layer

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 10b: Data resolution layer
Read: #0; #9; scaffolding/_preamble.md § Convention-mapping rule
Produces: one resolver per kind of data the codebase holds itself, called by screens, the only place those data objects are named
Check: run project: typecheck, lint, test, build; evidence: what was seen when this was tried: the search for data object names outside the resolver
Skip when: the codebase holds no data of its own and every value arrives through the API layer

When the codebase holds data of its own (fixtures, content files, a local store) that may later come from somewhere else, each kind of data has one resolver (#0): screens ask it for what they need by name (list the items, find one), and it decides where the data comes from. When the real source arrives, only the resolver changes.

- Screens and components never read a data source directly; they call the resolver.
- The resolver may be asynchronous, since most real sources are.
- Its fallback is explicit: the real source when configured, otherwise a safe default for development.
- Replacing the source is one isolated change.

**Verify:** a search for the data objects' names finds them only in their resolver; screens use only the resolver's functions.
