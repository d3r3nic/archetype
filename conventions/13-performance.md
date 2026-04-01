# Convention #13: Performance & Optimization

## Principle

Performance is designed in, not optimized after. Code splitting, lazy loading, and caching are configured at the architecture level. Performance budgets are enforced in CI. Optimization is based on measurement, not assumption.

## Reusable System

- Code splitting: route-based and component-based splitting configured in bundler
- Lazy loading: wrapper components with Suspense boundaries
- Image component: optimized image loading (modern formats, responsive, CDN)
- Bundle budget: CI check that fails on oversized bundles
- Performance monitoring: Core Web Vitals tracking

## Rules

- Split code at route boundaries. Each route is a separate chunk.
- Lazy load heavy components (modals, charts, editors) on demand.
- Show skeleton screens while loading, not spinners.
- Set explicit width and height on images and media to prevent layout shift.
- Use modern image formats (WebP, AVIF) with fallbacks.
- Memoize only where profiling shows benefit. Don't memoize everything.
- Virtual scroll lists with 1000+ items.
- Bundle budgets are enforced in CI.

## Violations

- Entire app in one bundle (no code splitting)
- Spinners instead of skeleton screens
- Images without width/height causing layout shift
- Premature optimization without profiling data
- Bundle growing unchecked with no budget

## References.md Section

- Bundler: which one and code splitting config
- Image handling: CDN, component, optimization pipeline
- Performance targets: LCP, INP, CLS thresholds
- Bundle budget: size limits and enforcement
