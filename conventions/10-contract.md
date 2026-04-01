# Convention #10: Frontend-Backend Contract

## Principle

Frontend and backend agree on data shapes through a single source of truth. This contract is enforced through generated clients, shared schemas, or type-safe RPC. Changes to the contract are detected automatically in CI before they break production.

## Reusable System

- Contract definition: OpenAPI spec, GraphQL schema, tRPC router, or shared Zod schemas
- Generated client: TypeScript client auto-generated from contract
- Contract tests: automated verification that both sides conform
- Response envelope: consistent response format across all endpoints

## Rules

- One source of truth for API types. Never manually duplicate types between frontend and backend.
- Generate TypeScript clients from the contract when possible.
- Breaking changes to the contract are detected in CI.
- Response format is consistent across all endpoints (envelope pattern).
- Transform data at the boundary, not in feature code.

## Violations

- Manually writing the same interface in both frontend and backend
- No detection mechanism for breaking API changes
- Different response formats across different endpoints
- Frontend making assumptions about response shape without types

## References.md Section

- Contract type: OpenAPI, GraphQL, tRPC, shared Zod, or manual
- Generated client: how it's generated and where it lives
- Response format: the project's response envelope structure
- Breaking change detection: how it works in CI
