# Backend Conventions

This is a LOOKUP INDEX for backend-specific conventions. These supplement the universal conventions — read both.

Universal conventions: ../Conventions.md (23 conventions for any project)
Backend conventions: this file (7 conventions for backend projects)

## Quick Lookup: Which backend conventions to read per task type

| Task type | Read these | Also read (universal) |
|-----------|-----------|----------------------|
| Database / models / queries | B1 | #3 (architecture), #7 (types) |
| New API endpoint | B2, B3 | #3 (architecture), #7 (types), #8 (errors) |
| Auth / middleware | B3 | #11 (auth/security) |
| Logging / monitoring | B4 | #8 (errors) |
| Background jobs / queues | B5 | #0 (reusability) |
| File upload / storage | B6 | #11 (security) |
| Caching | B7 | |
| Migrations | B1 | #2 (git - commit each migration) |

## Backend Convention Index

- B1 Database — queries, migrations, transactions, pooling, indexes, soft delete, ORM patterns → backend/conventions/B1-database.md
- B2 API Design — URL design, methods, status codes, pagination, validation, response envelope → backend/conventions/B2-api-design.md
- B3 Middleware — ordering, request lifecycle, cross-cutting concerns → backend/conventions/B3-middleware.md
- B4 Logging & Observability — structured logging, levels, sensitive data, correlation IDs, health checks, metrics → backend/conventions/B4-logging.md
- B5 Background Jobs — async vs sync, idempotency, retry/DLQ, job design → backend/conventions/B5-background-jobs.md
- B6 File Handling — presigned URLs server-side, magic byte validation, storage abstraction → backend/conventions/B6-file-handling.md
- B7 Caching — when to cache, invalidation, layers, stampede prevention → backend/conventions/B7-caching.md
