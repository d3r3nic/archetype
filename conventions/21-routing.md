# Convention #21: Routing & Navigation

## Principle

Routes define the application's URL structure and map to pages. Layouts persist across child routes. Route guards protect authenticated content. URL parameters encode state that should survive refresh and sharing. Loading and error states are defined per route segment.

## Reusable System

- Route guard component: auth check that redirects unauthenticated users
- Layout components: persistent shells (sidebar, header) across child routes
- URL state utilities: helpers for reading/writing filters and pagination to URL params

## Rules

- Nested layouts for persistent UI across child routes.
- Route guards protect authenticated routes at the routing level.
- Every route has its own loading and error state.
- Filters, pagination, and view state live in URL search params.
- Typed routes prevent broken links at compile time when possible.
- Prefetch route data on link hover for perceived instant navigation.

## Violations

- Auth check in every page component instead of route guard
- Filters stored in component state instead of URL (lost on refresh)
- Route without loading state (blank screen during data fetch)
- Hardcoded route paths as strings scattered across the codebase

## References.md Section

- Router: which one (React Router, TanStack Router, Next.js, etc.)
- Route guard: path to auth route wrapper
- Layout: where layout components live
- Route definitions: where routes are defined
