# Convention #22: Design System

## Principle

A shared component library is the single source of truth for UI. Features never interact with the underlying UI library directly. All interaction goes through project wrappers that enforce theming and provide a consistent API. The design system is token-first: visual decisions are encoded in tokens before component implementation begins. If the project ever switches UI libraries, only the wrappers change - features don't.

## Reusable System

Create a design system foundation that establishes:
- Wrapper components around the UI library that enforce theme token usage, provide a consistent API, and can be swapped without changing feature code
- A token system as the foundation for all visual values (colors, spacing, typography, shadows, borders) that feeds into the wrapper components
- A component catalog (documentation site or tool) showing all available components with their variants, sizes, and states so developers and AI can see what already exists before building
- A deprecation process: when a component is being replaced, mark it deprecated with a migration path and a removal date

## Rules

- Never import directly from the UI library in feature code. Always use the project's wrapper components. If a wrapper doesn't exist for something you need, create the wrapper first, then use it.
- Before building any new component, check feature-tree.md and the shared component directory. The component may already exist. AI builds duplicate components at a very high rate because it doesn't check what exists.
- Token-first: all visual values come from the token system. No hardcoded colors, spacing, or typography in wrapper components.
- Never install a second UI library for a single widget. If you need a date picker, find one that integrates with the existing UI library or build a wrapper around a standalone one that uses the project's token system. Mixing UI libraries creates visual inconsistency and bundle bloat.
- When a component is deprecated, announce it, mark it with the language's deprecation annotation, provide a migration path, and remove it after the migration period.

## Violations

- Importing components directly from the UI library in feature code
- Building a new component without checking if one already exists in the project
- UI library-specific API patterns leaking into feature code (features should use wrapper APIs, not library-specific APIs)
- Installing a different UI library for a single component
- Hardcoded visual values in wrapper components instead of tokens
- Components in the design system with no documentation showing their variants and usage

## Wrong vs Right

- WRONG: feature code imports Button directly from the UI library. 50 features import directly. The project wants to switch UI libraries. 50 features need rewriting.
- RIGHT: feature code imports Button from the project's wrapper layer. The wrapper imports from the UI library internally. Switching libraries means updating the wrappers only. Zero feature code changes.
- WRONG: AI is asked to build a feature with a modal. It creates a new Modal component in the feature directory without checking. The project already has a Modal in the shared component library.
- RIGHT: AI reads feature-tree.md, sees Modal exists in the shared components. Uses the existing Modal with appropriate configuration.
- WRONG: the project uses one UI library for everything, but a developer installs a different library for a date picker. Now the date picker looks slightly different from everything else, and the bundle is bigger.
- RIGHT: the developer finds a date picker that works with the existing UI library, or wraps a standalone date picker in the project's token system so it matches visually.

## Research Notes

When bootstrapping this convention:
- Research the UI library's wrapping patterns. How do you create thin wrappers that pass through all props while enforcing theme tokens?
- Research component catalog tools for the framework (tools that display all components with their variants for browsing and testing)
- Research the UI library's token/theming integration for building token-first wrappers
- Research the framework's approach to tree-shaking UI library components (importing only what's used)
- Document the wrapper location, import conventions, available components, and catalog URL in References.md
