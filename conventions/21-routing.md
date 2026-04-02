# Convention #21: Routing & Navigation

## Principle

Routes define the application's URL structure and map to pages. Layouts persist across child routes so shared UI (navigation, sidebars) doesn't remount on every navigation. Route guards protect authenticated content at the routing level, not inside individual pages. URL parameters encode state that should survive refresh and sharing.

## Reusable System

Create a routing foundation that establishes:
- Route guard components that protect authenticated or role-restricted routes at the routing level. Every protected route goes through the guard. Individual pages never check auth themselves.
- Layout components that persist across child routes (navigation bars, sidebars, headers). When the user navigates between pages that share a layout, only the content area changes.
- Typed route definitions so route paths are constants or functions, not strings scattered across the codebase. Changing a route path means changing one definition, not finding and replacing strings everywhere.
- URL state utilities for encoding filters, pagination, and sort order in URL parameters so they survive page refresh and can be shared via URL.

## Rules

- Protect routes at the routing level using a guard component. Never duplicate auth checks in individual page components.
- Use layout routes for persistent UI. Navigation bars and sidebars should not remount on every page change.
- Every route should have its own loading and error state. The user should never see a blank screen while data loads.
- Route paths are defined as typed constants or functions in one location. Never hardcode route strings throughout the codebase.
- Filters, pagination, and sort order belong in URL parameters, not component state. They must survive page refresh and be shareable.
- Client-side route guards are not security. They're user experience. The server must also verify authorization on every request.

## Violations

- Auth checks duplicated in every page component instead of one route guard
- Hardcoded route path strings scattered throughout the codebase
- No loading state on routes (blank screen while data fetches)
- Filters and pagination in component state (lost on refresh, not shareable)
- Relying solely on client-side route guards for security without server-side authorization

## Wrong vs Right

- WRONG: every page component starts with "if not authenticated, redirect to login." The same check duplicated in 20 pages. Change the login route and you update 20 files.
- RIGHT: one route guard component at the routing level. All protected routes pass through it. Change the redirect once, it applies everywhere.
- WRONG: route paths hardcoded as strings: "/dashboard/users/123/edit" written directly in navigation code, link components, and programmatic navigation. A route restructure means finding every string.
- RIGHT: route paths defined as typed constants or builder functions in one file. Navigation uses the constants. A route restructure means changing one definition.
- WRONG: user applies search and filter. Results show. User copies URL and sends to colleague. Colleague opens it, sees unfiltered default view because filters were in component state.
- RIGHT: filters are URL parameters. User copies URL, colleague sees the exact same filtered view.

## Research Notes

When bootstrapping this convention:
- Research the framework's routing library and its patterns for nested routes, layout routes, and route guards
- Research typed routing solutions for the framework (how to define routes as constants with type safety)
- Research the framework's patterns for per-route loading and error states
- Research URL state management patterns for the framework (encoding and reading filters/pagination from URL parameters)
- Document the router setup, route guard location, layout components, and route definitions in References.md
