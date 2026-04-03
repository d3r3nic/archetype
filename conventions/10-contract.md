# Convention #10: Frontend-Backend Contract

## Principle

Frontend and backend agree on data shapes through a single source of truth. This contract is enforced through generated clients, shared schemas, or type-safe communication. Changes to the contract are detected automatically before they reach production. Types are never manually duplicated between frontend and backend.

## Reusable System

Create a contract system that establishes:
- A single source of truth for API data shapes (API specification, shared schema package, or type-safe RPC layer)
- Generated type definitions from the contract so frontend types always match backend types without manual synchronization
- A consistent response format across all endpoints (same envelope structure for data, metadata, and errors)
- Breaking change detection that catches contract violations in CI before they ship

## Rules

- One source of truth for API types. Never manually write the same type in both frontend and backend.
- Generate type definitions from the contract whenever possible. Manual type synchronization always drifts.
- Response format is consistent across all endpoints. Same structure for data, metadata, and errors everywhere.
- Transform data at the API boundary. Components never traverse raw API response structures. The API layer provides clean, flat shapes.
- Breaking changes to the contract must be detected before deployment. Set up schema diffing or contract testing in CI.

## Violations

- Manually writing the same type definition in both frontend and backend code
- No mechanism for detecting breaking API changes before deployment
- Different response formats across different endpoints (one returns {data, error}, another returns {result, message})
- Raw API response shape leaking through to UI components
- API contract changes deployed without frontend awareness

## Wrong vs Right

- WRONG: a User type defined in the backend and separately defined in the frontend with the same fields. A field is added on the backend. The frontend type is not updated. Data arrives that the frontend doesn't expect.
- RIGHT: one schema definition (API spec, shared package, or type-safe RPC). Types are generated or shared automatically. Backend adds a field, frontend types update through the generation pipeline.
- WRONG: one endpoint returns {users, total}, another returns {data, count}, another returns {results, pagination}. Every feature parses a different format.
- RIGHT: every endpoint returns {data, meta}. One parsing pattern across the entire project.
- WRONG: a component accesses response.data.attributes.profile.displayName deep in its render logic. The API restructures the response. The component breaks.
- RIGHT: the API layer transforms the response at the boundary. The component receives a flat user.name. API changes only affect the transformation layer.

## Research Notes

When bootstrapping this convention:
- Research contract definition options for the project's stack: API specification formats, shared schema packages, type-safe RPC layers, or code generation tools that produce typed clients from API definitions
- Research breaking change detection tools that can be integrated into the CI pipeline
- Research the framework's patterns for generating typed API clients from contracts (code generation from OpenAPI, GraphQL codegen, or equivalent for the language)
- Establish the response envelope format and document it in References.md
