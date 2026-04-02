# Convention #4: Component Design & API

## Principle

UI components expose consistent, predictable APIs across the entire project. Every component follows the same conventions for sizing, variants, and state props. Components are composable - complex UIs are built from small focused pieces, not monolithic blocks. The component foundation (base components, wrappers around the UI library) is built once at scaffolding and used everywhere.

## Reusable System

Create a component foundation that establishes:
- Base wrapper components around the UI library. Features never import from the UI library directly - they import from the project's wrapper layer. This ensures consistent styling and makes it possible to switch UI libraries without touching feature code.
- A consistent component API convention: all components use the same prop names for the same concepts. Size uses the same scale everywhere. Variant uses the same vocabulary everywhere. State props use the same naming pattern everywhere.
- Layout components for common spatial arrangements (stacks, grids, page containers) so features don't reinvent layout patterns.

## Rules

- Never import directly from the UI library. Always use project wrappers. If a wrapper doesn't exist, create it first.
- Consistent sizing across all components. Every component that accepts size uses the same scale (for example xs, sm, md, lg, xl).
- Consistent variants across all components. Every component that accepts variant uses the same vocabulary (for example primary, secondary, outline, ghost).
- Consistent state props. Every component uses the same names for disabled, loading, read-only, required, and invalid states.
- Components render UI. They do not fetch data, compute business logic, or manage complex state. That belongs in hooks or services.
- Forward refs on all reusable components so parent components can access the underlying element for focus management and library interop.
- Keep components focused. If a component grows beyond 200 lines, it's doing too much. Break it into composed smaller components.
- Before building a new component, check feature-tree.md and the shared component directory. The component may already exist.

## Violations

- Importing directly from the UI library instead of project wrappers
- Inconsistent sizing: one component uses small/medium/large, another uses xs/sm/md, another uses compact/regular
- God components: a single 500+ line component that fetches data, manages state, handles events, and renders everything
- Missing ref forwarding on reusable components
- Building a new component without checking if one already exists in the project
- Props that accept wildly different types for one value (a prop that takes string or number or function or element)

## Wrong vs Right

- WRONG: Button uses size="small", Input uses size="sm", Card uses sizing="compact". Three components, three different APIs for the same concept.
- RIGHT: Button, Input, and Card all accept size with the same values. Learn one API, use everywhere.
- WRONG: UserDashboard is a 500-line component with 15 state variables, 8 effects, 10 event handlers, and a massive render function.
- RIGHT: UserDashboard composes UserProfile, RecentOrders, and NotificationFeed. Each focused component handles one concern. The dashboard just arranges them.
- WRONG: AI builds a ConfirmDialog component in a feature without checking shared components. The project already has a ConfirmDialog.
- RIGHT: AI reads feature-tree.md, sees ConfirmDialog already exists in shared, uses it with appropriate configuration.

## Research Notes

When bootstrapping this convention:
- Research the UI library's component wrapping patterns. Understand how to create thin wrappers that enforce theme usage while passing through all original props.
- Research the framework's ref forwarding pattern for reusable components
- Research compound component patterns for the framework (components that share implicit state, like tabs, accordions, selects)
- Research the framework's recommended approach for component composition vs configuration
- Document the wrapper location, import rules, and API conventions in References.md
