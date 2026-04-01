# Convention #5: State Management & Data Flow

## Principle

State lives as close to where it's used as possible. Local state is the default. Server state (API data) uses a dedicated library with automatic caching. Global state is reserved for truly app-wide concerns (auth, theme, locale). Data flows in one direction: down through props, up through callbacks.

## Reusable System

- Store configuration: centralized store setup with feature slice registration
- Server state library: configured data fetching with cache management
- State slice pattern: template for how features create and register state

## Rules

- Default to local state (useState). Lift only when genuinely needed.
- Server state (API data) uses the data fetching library, not client state.
- Global state only for: auth, theme, locale, and truly app-wide concerns.
- State tree is flat. Component tree can be hierarchical.
- One state slice per feature.
- Data flows down via props. Events flow up via callbacks.
- If props pass through more than 2-3 intermediary components, use context or state management.
- URL is state for navigation, filters, and pagination.
- Derived state is computed through selectors, not stored separately.

## Violations

- Storing API response in Redux/Zustand instead of using the server-state library
- Global state for feature-specific data
- Props drilling through 5+ levels instead of using context
- Storing derived values when they could be computed from existing state
- Mutable state updates instead of immutable patterns

## References.md Section

- State library: which one (Redux, Zustand, Context, etc.)
- Store location: path to store configuration
- Slice pattern: how features create and register slices
- Server state: which library (React Query, RTK Query, SWR)
- Cache strategy: Network-First, SWR, etc.
