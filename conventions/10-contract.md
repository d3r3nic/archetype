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
- Different response formats across different endpoints (data/error on one, result/message on another)
- Frontend making assumptions about response shape without types
- Raw API shape leaking into components instead of transforming at boundary

## Right vs Wrong

Examples are illustrative.

```
WRONG (manually duplicated types that will drift):
// backend/types.ts
interface User { id: string; name: string; role: 'admin' | 'user'; }

// frontend/types.ts (manually copied)
interface User { id: string; name: string; role: 'admin' | 'user'; }

RIGHT (generated from contract):
// openapi.yaml or shared Zod schema is the source of truth
// Types are auto-generated, always in sync
```

```
WRONG (inconsistent response shapes):
GET /users    → { users: User[], total: number }
GET /orders   → { data: Order[], count: number }
GET /products → { results: Product[], pagination: {...} }

RIGHT (consistent envelope):
GET /users    → { data: User[], meta: { total: 50, page: 1 } }
GET /orders   → { data: Order[], meta: { total: 12, page: 1 } }
GET /products → { data: Product[], meta: { total: 200, page: 1 } }
```

```
WRONG (raw API shape leaks into components):
function UserCard({ user }) {
  return <h2>{user.data.attributes.profile.displayName}</h2>;
}

RIGHT (transform at boundary, components get clean shapes):
// api/transforms.ts
function toUser(raw: ApiUser): User {
  return { id: raw.data.id, name: raw.data.attributes.profile.displayName };
}
function UserCard({ user }: { user: User }) {
  return <h2>{user.name}</h2>;
}
```

## References.md Section

- Contract type: OpenAPI, GraphQL, tRPC, shared Zod, or manual
- Generated client: how it's generated and where it lives
- Response format: the project's response envelope structure
- Breaking change detection: how it works in CI
