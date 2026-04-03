# Convention #5: State Management & Data Flow

## Principle

State lives as close to where it's used as possible. Local component state is the default. Server data (anything from an API) uses a dedicated data fetching layer that handles caching, deduplication, and revalidation automatically. Global state is reserved for truly app-wide concerns only. Data flows in one direction.

## Reusable System

Create a state management setup that establishes:
- A configured store for global state with a clear pattern for how features register their own state slices
- Integration with a server-state layer that manages API data with automatic caching, background refetching, and deduplication. Features declare what data they need, the layer handles how to get it, cache it, and keep it fresh.
- A clear rule for which state goes where: local state for UI-only concerns, server state for API data, global state only for auth/theme/locale

## Rules

- Default to local state. Only lift state when genuinely needed by multiple components.
- Server data always goes through the data fetching layer. Never store API responses in the global client state. The data fetching layer handles caching, deduplication, and revalidation automatically.
- Global state only for truly app-wide concerns: authentication status, theme preference, locale. Nothing else.
- State tree is flat. Each feature registers one slice at the top level, not nested inside other slices.
- Data flows in one direction: down through props, up through callbacks.
- Never store derived state separately. If filteredItems can be computed from items + filterCriteria, compute it, don't store it as a separate piece of state.
- Filters, pagination, sort order, and view state belong in the URL, not component state. They must survive page refresh and be shareable via URL.

## Violations

- Storing API response data in the global store instead of using the data fetching layer
- Putting everything in global state (modal open/close, tooltip visibility, form input values)
- Storing derived values (filteredItems, sortedItems) as separate state and keeping them in sync with effects
- Props drilling through 5+ intermediary components without introducing context or state management
- Filters and pagination in component state instead of URL parameters (lost on refresh, not shareable)

## Wrong vs Right

- WRONG: a Redux slice that stores users list, loading boolean, and error string, with a thunk that manually fetches, sets loading, stores data, catches errors. Manual cache management.
- RIGHT: a server-state hook that declares "I need the users list." The data fetching layer handles loading state, error state, caching, deduplication, and background revalidation automatically.
- WRONG: three separate pieces of state - items, filteredItems, sortedItems - with effects to keep them synchronized. When items changes, filteredItems updates, then sortedItems updates. Complex, fragile chain.
- RIGHT: one piece of state (items) and two computed values derived from it. filteredItems and sortedItems are calculated on the fly, not stored.
- WRONG: user applies a search filter. It's stored in component state. User copies the URL and sends it to a colleague. Colleague opens it, sees no filter applied.
- RIGHT: search filter is in the URL query parameters. User copies the URL, colleague sees the same filtered view.

## Offline Support

If the project needs to work without network connectivity (mobile apps, field-use applications, progressive web apps), offline support is a state management concern. Build one reusable offline system, not per-feature offline handling.

Create a reusable offline system that:
- Detects network status and exposes it as state the entire app can read
- Queues mutations (form submissions, data changes) made while offline and replays them when connectivity returns
- Persists critical data locally so the app can display cached content without a network connection
- Handles conflict resolution when offline changes conflict with server-side changes made by other users
- Shows clear UI indicators for offline status, pending sync, and sync failures

Rules:
- One offline system, not per-feature. Features declare what data should be available offline and what mutations should be queued.
- Forms that need offline support integrate with the offline queue through configuration, not custom code per form.
- Always show the user what's pending sync and whether sync succeeded or failed.

## Research Notes

When bootstrapping this convention:
- Research the framework's latest state management options. Find the recommended server-state library for the framework (handles API data caching and revalidation). Find the recommended client-state library if global state is needed.
- Research the framework's patterns for computing derived state without storing it separately
- Research URL state management patterns for the framework (how to sync filters, pagination, sort with URL parameters)
- Research the framework's data flow patterns (one-way data flow, props, callbacks, context)
- If the project needs offline support: research the framework's offline data persistence patterns, background sync APIs, and queue-based mutation replay strategies
- Document the state management choices, patterns, offline approach (if applicable), and conventions in References.md
