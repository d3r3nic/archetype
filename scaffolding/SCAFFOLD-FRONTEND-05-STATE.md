# Frontend scaffold: state management

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 5: State management
Read: #5; #9; scaffolding/_preamble.md § Convention-mapping rule
Produces: the state responsibilities this product needs, recorded in References.md, and only the shared state and data caching they call for
Check: run project: typecheck, lint, build; evidence: what was seen when this was tried: each shared piece of state updated and seen by its consumers, and a remote read cached and refreshed by its recorded rule
Skip when: no state is shared beyond a single screen and no remote data needs caching on the client

Apply #5: record which part of the product owns each fact that several screens use, and how remote data is cached and refreshed (#9). Build only what those responsibilities need, researching the chosen stack's options where the record is silent. A product whose screens keep their own state and read remote data through Step 6 adds no shared store; one whose screens share session, preferences or remote data gets one owner for each, never competing copies.

**Verify:** each shared piece of state, updated in one place, is seen by every consumer; a remote read is cached, deduplicated and refreshed by the rule the project recorded.
