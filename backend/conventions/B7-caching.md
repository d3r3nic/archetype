# Convention B7: Server-Side Caching

## Principle

Caching reduces database load and response times for read-heavy, infrequently-changing data. But caching the wrong data creates stale reads worse than no caching. Caching without user isolation leaks data between users. Cache invalidation is hard — start with the simplest approach (TTL) and only add complexity when needed. Prevent cache stampedes (thundering herd) when hot keys expire.

## Reusable System

Create a caching foundation that establishes:
- A cache service interface that wraps the cache provider (Redis, Memcached, in-memory)
- Consistent key naming convention: service:entity:id (e.g., api:user:123)
- TTL-based expiration as the default strategy
- Stampede prevention for hot keys (per-key locking or stale-while-revalidate)

## Rules

- Cache read-heavy endpoints with data that changes infrequently: user profiles, product catalogs, configuration, permission lookups.
- Do NOT cache data that must be real-time consistent: account balances, inventory during checkout, live auction bids.
- Do NOT cache user-specific data in shared caches without proper key isolation. User A must never see user B's cached data.
- Start with TTL-based expiration. If the business tolerates 5-minute staleness, set a 300-second TTL. Do NOT build complex invalidation when a short TTL suffices.
- For stronger consistency, use event-driven invalidation: when data changes, publish an event that invalidates the cache entry.
- Prevent cache stampedes: when a hot key expires and hundreds of requests simultaneously miss the cache, only one request should regenerate the cache. Others wait or receive stale data. Use per-key locking or stale-while-revalidate.
- Use appropriate cache layers: in-memory for hot configuration and lookup tables (per-instance, fastest), distributed cache (Redis) for shared session data and API responses (cross-instance), CDN for static assets and public API responses (edge).

## Violations

- Caching account balances. User deposits money. Cache returns the old balance for 5 minutes.
- Shared cache with keys like "user-profile" without the user ID. All users see the same cached profile.
- Complex cache invalidation pipeline when a 60-second TTL would be fine.
- Hot key expires. 500 concurrent requests all miss the cache and all hit the database simultaneously. Database overloads.

## Wrong vs Right

- WRONG: cache everything with a 1-hour TTL. Product price changes. Customers see the old price for up to an hour. Orders placed at wrong price.
- RIGHT: cache product catalogs with a 5-minute TTL (business accepts this delay). Cache account balances with zero TTL (never cached — always fresh from database).
- WRONG: popular endpoint's cache expires. 500 requests arrive in the same second. All 500 query the database to regenerate the cache. Database CPU spikes to 100%.
- RIGHT: first request acquires a lock and regenerates the cache. Other 499 requests wait for the lock (or receive stale data if using stale-while-revalidate). Database handles 1 query, not 500.

## Research Notes

When bootstrapping this convention:
- Research caching libraries for the framework (ioredis for Node, redis-py for Python, StackExchange.Redis for .NET).
- Research the framework's patterns for cache-aside (check cache → miss → query DB → populate cache).
- Research stampede prevention patterns for the chosen cache provider.
- Research CDN configuration for the deployment platform if caching public API responses at the edge.
- Document the cache provider, key naming convention, TTL defaults, and invalidation strategy in References.md.
