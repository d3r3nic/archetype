# Convention #4: Component Design & API

## Applies when

The product has an interface built from parts: screens, pages, views, panels, or a terminal interface. What varies: the platform's own elements, whether a component foundation was chosen (#22), and how many screens reuse the same parts. A product with no interface skips this convention.

## Principle

Every interface part has one implementation that every screen reuses. A part needed in a second place becomes one shared component, configured by each use; features never build their own copy. Components make the chosen interaction model easy to understand, test and change, and keep the accessibility target and the design's promised behavior whatever the architecture.

## Reusable System

The project's component set: the platform elements, foundation, adapters or project-owned components the project chose (#22), where they are discovered, and the import boundary that keeps screens from bypassing them. References.md records the choice and its reason; § Boundaries records the import rule when there is one.

## Rules

- Before building a component, look at what exists: the project's components, the chosen foundation and the platform's own elements.
- When choosing or materially changing the component approach, research the platform's current composition patterns. Choose direct use, adapters, wrappers or project-owned components for a stated reason, and keep to the recorded boundary.
- Do not add a wrapper that only renames an existing interface.
- Use one name for one concept across the component family. Unlike components keep their own interfaces; do not force them into one set of sizes or variants.
- Keep behavior together when that makes it clearer. Separate data access, business rules or interaction state when that yields a clearer contract, safer reuse or better tests.
- Expose an element handle or equivalent only for focus, measurement or platform behavior that needs it.
- Judge a component's size by its responsibility and how easily it is understood, not by a line count.

## Violations

- A second implementation of a component the project already has.
- A screen bypassing the recorded component boundary with no recorded reason.
- A wrapper or layout helper with no consumer or responsibility.
- One concept under two incompatible names.
- Business rules or access decisions hidden inside presentation code where they cannot be verified.
- Keyboard, focus, semantic or state behavior lost when a component is restructured.

## Wrong vs Right

- WRONG: each screen builds its own date picker. RIGHT: one date picker, configured by each screen.
- WRONG: wrap every library control because wrappers are assumed safer. RIGHT: compare direct use and selective adapters against the change risk, access needs and library stability, then record and keep to the chosen boundary.
- WRONG: force a button, a chart and a map into the same size and variant properties. RIGHT: share vocabulary where the concepts match and let different responsibilities have different interfaces.

## Research Notes

Research the platform's native elements, maintained foundations, accessibility behavior, composition model and testing support, and how the project already uses them. Exercise a chosen pattern with real interaction, including focus and every committed state. Record the approach, the discovery surface and the reasons in References.md and the import rule in § Boundaries.
