# Convention #5: State Management & Data Flow

## Applies when

The product holds state that changes while it runs: an interface, a service with sessions or caches, a simulation, a synchronizing client. What varies is where state lives and how long: a single screen, a whole application, a server, a device that goes offline.

## Principle

Choose state ownership, lifetime and propagation from the behavior the project promises. Every important fact has one authoritative owner; everything else reads it or derives from it, and updates are understandable. Component-local state, shared stores, server caches, persistent models and simulation worlds solve different needs. Preserve an accepted contract until a justified change identifies its affected consumers.

## Reusable System

Record the state responsibilities the project actually needs:
- Which part of the system owns each important fact and which parts consume it.
- How updates propagate, persist, synchronize or expire.
- Where derived views are computed and how cached views stay consistent.
- Which boundaries require shared coordination and which state can remain local.

Do not add a global store, network cache or synchronization layer solely because this convention lists it.

## Rules

- Keep state ownership as narrow as its consumers and lifetime allow. Shared state is justified by shared responsibility, not a fixed list of approved categories.
- For remote data, investigate consistency, freshness, cancellation, cache invalidation and failure behavior. Use a maintained fetching or synchronization layer when its contract fits; do not assume every runtime needs automatic refetching or a separate client cache.
- Choose state structure and update flow for the domain and concurrency model. Features, entities, scenes, transactions or another structure may provide the useful boundary.
- Avoid competing writable copies of the same fact. Compute derived views when practical; materialize or cache them when cost justifies it and define how they stay consistent.
- Decide whether filters, sorting and view state should survive refresh, navigation, sharing or restart. In a web interface, URL state can serve shareable non-sensitive views. Local, session or persistent project state may fit other behavior. Preserve the existing contract for a scoped edit.
- Keep sensitive state out of URLs, logs and storage that would expose it beyond its intended boundary.
- Verify transitions, stale inputs, concurrent updates and recovery where they affect promised behavior.

## Violations

- A shared store or cache added without a responsibility that needs it.
- Independent writable copies drift while each claims to be authoritative.
- A narrow filter change silently alters navigation or persistence behavior.
- A cached or materialized view has no defined update or invalidation policy.
- Consumers cannot identify where a state change originates or who owns it.

## Wrong vs Right

- WRONG: move every filter into a URL because a general rule says so. RIGHT: establish the expected sharing and persistence behavior, then choose storage that meets it without exposing sensitive values.
- WRONG: maintain items, filtered items and sorted items as unrelated writable stores. RIGHT: derive views from the authoritative items, or maintain a justified materialized view with verified consistency.
- WRONG: impose component-local state on a simulation whose world owns the shared rules. RIGHT: choose ownership from the domain and measure the representative update workload.

## Offline Support

Establish what offline use means for this project. A fully local application may need durable storage and recovery without any network queue. A synchronized application also needs defined mutation ownership, ordering, retry, duplicate prevention and conflict behavior.

Share coordination where features must honor the same invariants; keep separately evolving responsibilities separate (#0). Preserve critical data, make pending or failed synchronization visible when it exists, and exercise interruption and recovery. Do not promise that a request succeeded before its actual commitment point.

## Research Notes

Research the runtime's maintained state, persistence and concurrency approaches where they affect the project. Compare freshness and ownership requirements before selecting caching or synchronization tools. For shareable web views, check URL and privacy behavior; for local or synchronized data, check durability, migration and recovery. Record the chosen contracts and verification in the existing project context.
