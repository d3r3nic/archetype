# Convention #13: Performance & Optimization

## Principle

Performance is designed in from the start, not optimized after. Code splitting, lazy loading, and caching are configured at the architecture level during scaffolding. Performance budgets are enforced in CI so the project never silently degrades. Optimization decisions are based on measurement, not assumption.

## Reusable System

Create a performance foundation that establishes:
- Code splitting configured at the route level so each page loads only what it needs, not the entire application
- Lazy loading wrappers for heavy components that are only loaded when the user actually needs them (modals, charts, editors, rich text)
- An optimized image component or pattern that handles modern formats, responsive sizing, lazy loading, and explicit dimensions to prevent layout shift
- Bundle size budgets enforced in the CI pipeline so the bundle never grows unchecked
- Performance monitoring that tracks real user metrics (page load times, interaction responsiveness, visual stability)

## Rules

- Split code at route boundaries. Each page or major section loads as a separate bundle.
- Lazy load heavy components on demand. Large charts, editors, and modals should not be in the initial bundle.
- Show content-shaped skeleton placeholders while loading, not generic spinners. Skeletons show the user what's coming, spinners show nothing useful.
- Set explicit width and height on all images and media to prevent layout shift.
- Use modern image formats with appropriate fallbacks.
- Enforce bundle size budgets in CI. If a change makes the bundle exceed the budget, the build fails.
- Never optimize without profiling first. Premature memoization and optimization add complexity without measured benefit.
- Watch for N+1 query patterns in data access code. A loop that makes one database or API call per item is the most common performance mistake AI makes. Use batch queries, joins, or includes instead.

## Violations

- Entire application in one bundle with no code splitting
- Generic spinners instead of content-shaped skeleton placeholders
- Images without width and height attributes, causing layout shift
- Bundle growing unchecked with no size budget or monitoring
- Premature memoization everywhere without profiling data showing it helps
- N+1 queries: a loop that makes a separate database or API call for each item in a list instead of fetching them all in one query
- Heavy libraries loaded eagerly when they're only needed for one rarely-used feature

## Wrong vs Right

- WRONG: every page, every component, every library loads upfront. The initial bundle is 2MB. The user waits 5 seconds before seeing anything.
- RIGHT: the initial page loads its own bundle. Other pages load when navigated to. Heavy components load when opened. The initial bundle is 200KB.
- WRONG: while data loads, a spinning circle in the center of the screen. The user has no idea what's about to appear or how long it will take.
- RIGHT: while data loads, skeleton placeholders shaped like the content that's coming. The user can see the layout immediately and knows content is loading.
- WRONG: a function that takes a list of 100 orders and fetches the products for each order one at a time. 100 sequential database queries.
- RIGHT: a function that fetches all orders with their products in a single query using a join or include. One query, same result.
- WRONG: every component wrapped in memoization because "it can't hurt." It adds complexity, makes debugging harder, and provides no measurable benefit for most components.
- RIGHT: profiling reveals a specific component re-renders excessively and causes visible lag. That specific component is memoized. The fix is targeted and measured.

## Research Notes

When bootstrapping this convention:
- Research the framework's code splitting configuration. How do you split at route boundaries? How do you lazy-load heavy components?
- Research the framework's image optimization patterns. Is there a built-in optimized image component, or does the project need one?
- Research bundle analysis tools for the framework's build tool. Set up bundle size budgets in CI.
- Research the framework's skeleton/placeholder patterns for loading states
- Research real user monitoring options for the framework (performance metrics collection)
- Document the code splitting config, bundle budget, image approach, and monitoring in References.md
