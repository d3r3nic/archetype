# Frontend scaffold: api layer (client side)

Part of the frontend scaffold playbook (scaffolding/SCAFFOLD-FRONTEND.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step. Before building, read the conventions it names and write how the system will be built in its References.md section (scaffolding/_preamble.md); when it lands, update its feature-tree.md row and its docs/systems/ page.

## Step 6: API layer (client side)
Read: #9; #10; scaffolding/_preamble.md § Convention-mapping rule
Produces: the API client, the transforms, and the contract types, behind the project API layer
Check: run project: typecheck, lint, build; evidence: what was seen when this was tried: a test call against a mocked endpoint, through the transform, the cache, and the state of Step 5

Build:
- Configured HTTP client with base URL, auth header injection, request/response interceptors.
- Data transformation at the boundary (snake_case↔camelCase, date parsing).
- Integration with server-state library from Step 5.
- Consistent error handling (API errors throw Step 3 error classes).
- Contract typing: if the backend ships typed contracts (OpenAPI, GraphQL codegen, a typed RPC layer), wire that in.

**Verify:** a test API call hits a mocked endpoint, returns transformed data, caches via server-state, and displays through Step 5 state.
