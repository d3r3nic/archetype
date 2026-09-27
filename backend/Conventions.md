# Backend Conventions

This is a lookup index for backend conventions. They supplement the universal conventions; read both. Each opens with when it applies, by how the service works.

Universal conventions: ../Conventions.md (the universal conventions for any project)
Backend conventions: this file (7 conventions for backend projects)

## Quick Lookup: Which backend conventions to read per task type

| Task type | Read these | Also read (universal) |
|-----------|-----------|----------------------|
| Database / models / queries | B1 | #3 (architecture), #7 (types) |
| New API endpoint | B2, B3 | #3 (architecture), #7 (types), #8 (errors) |
| Auth / middleware | B3 | #11 (authentication) |
| Logging / monitoring | B4 | #8 (errors) |
| Background jobs / queues | B5 | #0 (reusability) |
| File upload / storage | B6 | #23 (security) |
| Caching | B7 | |
| Migrations | B1 | #2 (one reviewable change per migration) |

## Backend Convention Index

- B1 Database — one pool, no queries in loops, related writes together, migrations additive and never auto-applied to production, tenant scoping in one place → backend/conventions/B1-database.md
- B2 API Design — one style applied consistently, one response format, validation at the boundary, bounded lists, deliberate evolution → backend/conventions/B2-api-design.md
- B3 Middleware — cross-cutting concerns once, in a recorded order that fails safe → backend/conventions/B3-middleware.md
- B4 Logging & Observability — one logger, no secrets in logs, requests traceable, health and signals sized to reliance, audit trail separate → backend/conventions/B4-logging.md
- B5 Background Jobs — work people should not wait for, idempotent handlers, bounded retries, failures kept visible → backend/conventions/B5-background-jobs.md
- B6 File Handling — one storage service, server-generated keys, content checked not trusted, the transfer path chosen for the files → backend/conventions/B6-file-handling.md
- B7 Caching — cache only a measured need, with an invalidation rule and a stampede guard → backend/conventions/B7-caching.md
