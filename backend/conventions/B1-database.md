# Convention B1: Database

## Applies when

The service stores data in a database it owns. What varies: the kind of store, the volume the facts describe, whether one deployment serves several customers, and how the schema changes over time. A service that only calls other services skips this convention.

## Principle

Data access has one owner: one connection pool, one data-access layer, and one place that scopes every query to what the caller may see. Queries are shaped for the volume the facts describe, related writes succeed or fail together, and schema changes never put production data at risk. Code that works with ten rows in a test can collapse under production volume, so it is designed and checked against realistic data.

## Reusable System

The database foundation: one connection pool created at startup and shared by every request; the data-access layer, with loading patterns that avoid a query per item; the transaction helper for related writes; the migration workflow; seed data split into reference data (safe in production) and development data (never in production); and, when one deployment serves several customers, the tenant scoping every query passes through. References.md records the pool, the migration commands and the query patterns; § Boundaries keeps other code from creating its own connections.

## Rules

- Never query inside a loop. Fetch related data in one batched or joined query.
- Fetch the fields a feature needs, and never send internal fields to callers.
- Never apply migrations to production automatically. A production migration runs only through the recorded manual or gated path, with the owner's authority where it is destructive (#29).
- Change the schema additively: add first, move the data, deploy the code that uses it, then remove the old structure in a later release after checking that nothing still uses it.
- Name migrations so they sort in the order they apply and say what they change.
- Add indexes from actual query patterns, verify the database uses them, and remove the ones nothing uses.
- Enforce integrity in the database too: required values, uniqueness, references and checks back up the application's validation.
- With soft delete, every query filters deleted records through a default scope in the data-access layer, never by remembering in each query.
- Wrap related writes in one transaction, and keep transactions short.
- Create one connection pool at startup, size it from the instances, concurrency and time spent in the database, and always release connections.
- When one deployment serves several customers, scope every query to the caller's tenant in the data-access layer, never in each handler (#24).
- Read the queries the data-access layer generates, in development, and watch for loading that quietly queries once per item.

## Violations

- A query per item in a loop.
- A migration that drops data with no backup and no additive path.
- A migration applied to production automatically on a push.
- A connection created per request instead of taken from the pool.
- Related writes without a transaction, leaving partial data on failure.
- Soft-deleted records appearing because one query forgot the filter.
- A query that can return another tenant's records.

## Wrong vs Right

- WRONG: loop through a hundred orders and query each one's products: a hundred and one round trips. RIGHT: one query fetches the orders with their products.
- WRONG: drop a column in one release while ten million rows need rewriting and reads block. RIGHT: add the new column, migrate the data in the next release, and drop the old column in a later one after checking that no code uses it.
- WRONG: every request opens its own connection, and at peak the database refuses them. RIGHT: one pool, sized from measured load, shared by every request.
- WRONG: each handler remembers to add the tenant condition, and one forgets. RIGHT: the data-access layer adds it to every query.

## Research Notes

Research the chosen store's data-access options: batched and eager loading, transactions, connection pooling and its sizing, migration tooling with a manual production path, default scopes, and row-level protection for multi-tenant data. Record the pool, the migration commands and production path, and the query patterns in References.md, and the connection boundary in § Boundaries.
