# Frontend scaffold: API layer (client side)

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 6: API layer (client side)
Read: #9; #10; scaffolding/_preamble.md § Convention-mapping rule
Produces: the one client for each remote service, with its translation at the boundary and the contract's types, and the network line in References.md § Boundaries
Check: run project: typecheck, lint, build; evidence: what was seen when this was tried: a test call against a faked endpoint, through the translation, the cache, and the state of Step 5
Skip when: the product calls no remote service

Apply #9 and #10 through the recorded decisions:
- The client for each service: address, identity attached in one place, requests by domain action.
- Translation at the boundary: the service's naming, dates and nesting become the project's shapes, validated on arrival (#7).
- Errors become the kinds of Step 3's error system.
- The data caching of Step 5, when the product has it.
- The contract's types, when the service publishes a contract (#10); never hand-written copies.
- Record `` - Network: `<the network call pattern>` only in `<the client's path>` `` in References.md § Boundaries, so no feature calls the network around the client.

**Verify:** a test call reaches a faked endpoint and returns translated, validated data through the cache and state of Step 5, and a failing call surfaces as Step 3's error.
