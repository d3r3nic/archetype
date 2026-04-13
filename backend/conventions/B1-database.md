# Convention B1: Database

## Principle

The database is the foundation of every backend. Queries must be efficient, migrations must be safe, writes must be transactional, and connections must be pooled. AI generates code that works with 10 rows in tests but collapses under production data volumes. Every database operation must be designed for scale.

## Reusable System

Create a database foundation that establishes:
- A single connection pool initialized at application startup, shared across all requests
- A query pattern library (or ORM configuration) that prevents N+1 queries by default
- A migration workflow with safety checks: never destructive without approval, always reversible
- Transaction utilities for wrapping related writes
- Seed data separated into reference data (runs in production) and dev data (never runs in production)

## Rules

- Never fetch related data inside a loop. If you need orders for 100 users, fetch all orders in one query with a batch or join. Not 100 separate queries.
- Never use SELECT * or fetch entire entities when you only need specific fields. Select what the feature requires.
- Never auto-run migrations in production. Migrations require explicit human approval. Separate destructive changes (drop column) from additive ones (add column). Add first, deploy, migrate data, then remove old column in a later release.
- Name migrations descriptively with date prefix: 20260329_add_status_to_orders, not migration_42.
- Add indexes based on actual query patterns (WHERE, JOIN, ORDER BY), not guesses. Use EXPLAIN to verify indexes are used. Remove unused indexes (they slow writes).
- Use database-level constraints (NOT NULL, UNIQUE, CHECK, FOREIGN KEY) in addition to application validation. The database is the last line of defense.
- When using soft delete, every query against that table must filter by deleted_at IS NULL. Use a default scope or global filter to enforce this. Forgetting the filter is a data leak.
- Wrap multiple related writes in a transaction. If any write fails, all roll back. Never leave transactions open longer than necessary.
- Initialize one connection pool at application startup. Never create connections per request. Size the pool based on app instances, threads, and time in DB operations. Always release connections in a finally block.
- Review ORM-generated SQL regularly. Use query logging in development. Watch for lazy loading traps where accessing a relationship property inside a loop silently triggers N+1 queries.

## Violations

- A loop that queries the database per item (N+1). AI does this at an extremely high rate.
- SELECT * when only 3 fields are needed. Wastes bandwidth and leaks internal fields.
- A migration that drops a column with existing data and no backup.
- New database client created inside a request handler instead of using the shared pool.
- Multiple writes to different tables without a transaction. Partial failure leaves inconsistent data.
- Soft-deleted records appearing in query results because the filter was forgotten.
- Indexes on columns that are 97% one value (should be partial index on the 3% edge case).

## Wrong vs Right

- WRONG: loop through 100 orders, for each order query its products separately. 101 database round trips.
- RIGHT: one query that fetches all 100 orders with their products included. 1 database round trip.
- WRONG: migration drops a column in production. 10 million rows need rewriting, table locked for 5 minutes, all reads blocked.
- RIGHT: migration adds the new column first (additive, fast). Next deploy migrates data. Final deploy drops the old column after verifying no code references it.
- WRONG: new database connection created in every request handler. At 10K requests per second, 10K connections attempted against a database with a 100 connection limit.
- RIGHT: one pool of 20 connections shared across all requests. Connections reused, overhead eliminated.

## Research Notes

When bootstrapping this convention:
- Research the ORM's eager loading and batch loading patterns. Find how to prevent N+1 by default.
- Research the database's migration tooling. Find how to run migrations safely with approval gates.
- Research connection pool configuration for the database driver. Find recommended pool sizes.
- Research the ORM's transaction API. Find how to wrap multiple writes.
- Document the pool configuration, migration commands, and query patterns in References.md.
