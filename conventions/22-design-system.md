# Convention #22: Design System

## Principle

Do not reinvent the wheel. Prefer an established, production-grade component foundation when one fits the product: a library with built-in accessibility, keyboard handling, focus management, and theming. Configure it with the project's theme (every committed color scheme, design tokens, spacing scale). Wrap the components and export them. Features import from the project's wrapper layer, never directly from the library.

A project may rule otherwise — no fitting library exists for its platform, the product IS the component library, or a real constraint outweighs the reuse — and records that decision and its reason in References.md. Whatever the foundation, the wrapper layer, the token wiring, and the component catalog are not optional.

## Reusable System

Create a design system foundation that establishes:
- A component foundation configured with the project's theme (every committed color scheme, design tokens, spacing, typography): an established library where one fits, or a project-owned base layer where the project ruled otherwise
- Wrapper components around the foundation. The wrappers import from the library, apply theme configuration, enforce consistent API, and re-export. Features only import from the wrappers.
- The wrapper layer is thin. It configures and re-exports. It does not rebuild components from scratch. The foundation already handles accessibility, keyboard navigation, focus management, responsive behavior, and visual consistency.
- A component catalog showing all available wrapped components so developers and AI can see what exists before building anything new
- A deprecation process for components being replaced

## Rules

- Prefer an established component foundation. Do not build buttons, inputs, modals, dropdowns, tables, or other standard components from scratch when the foundation already provides them. Established libraries carry years of accessibility work, browser testing, and edge-case handling.
- A project that rules otherwise records the decision and its reason in References.md before scaffolding components. The wrapper layer, token wiring, and catalog still apply.
- Configure the foundation's theme with the project's design tokens: colors per scheme, spacing scale, typography scale, shadows, border radius. Every committed scheme must work.
- Wrap every component the project uses. The wrapper imports from the foundation, applies any project-specific defaults, and re-exports. Features import from the wrapper, never from the library directly.
- The wrapper layer is where theme enforcement happens. If a component needs project-specific styling or defaults, that goes in the wrapper. Features get a clean, consistent API.
- Before building any new component, check feature-tree.md and the shared component directory. AI builds duplicate components at a very high rate because it doesn't check what exists.
- Never install a second component library for a single widget. Find a component within the existing foundation or find a standalone one that integrates with the project's theme. Build from scratch only when neither exists, and then inside the wrapper layer with the same API conventions.
- These rules govern code. A canvas or artboard format that cannot import the foundation draws its controls as markup; that is design content under #27, not a hand-built component. A preview built from the repository's own components is code and imports the wrapper layer like any other. The code that implements a mockup uses the foundation, and a control the mockup shows that the foundation lacks is a wrapper to add, not a one-off.

## Violations

- Building buttons, inputs, modals, or other standard components from scratch when the foundation provides them, or before searching for a standalone one that integrates with the theme, with no recorded decision saying otherwise
- Importing components directly from the library in feature code instead of from project wrappers
- Building a new component without checking if one already exists
- Library-specific API patterns leaking into feature code
- A foundation configured for one color scheme when the project committed to more
- Components using hardcoded colors instead of the configured theme

## Wrong vs Right

- WRONG: building a Button component from scratch with utility classes, manually handling focus states, hover states, disabled states, keyboard interaction. Reinventing what the chosen library already provides.
- RIGHT: installing the chosen library, configuring its theme with the project's design tokens for every committed scheme, wrapping its Button with project defaults, exporting it. One line of config instead of a page of custom code.
- WRONG: feature code imports Button directly from the library. 50 features import directly. Switching libraries means rewriting 50 features.
- RIGHT: feature code imports Button from the project's wrapper layer. Switching libraries means updating the wrappers only. Zero feature code changes.
- WRONG: the foundation is configured with one scheme only. Someone asks for a second scheme later. Every component needs manual colors added.
- RIGHT: the foundation is configured with every committed scheme from day one. The theme system handles switching. Components adapt automatically.

## Research Notes

Dated notes: anything named in this section is an example from the time of writing and expires. Verify current options at bootstrap.

When bootstrapping this convention:
- Research the most established, production-grade component library for the chosen framework and platform. Pick one with: built-in accessibility, theme customization for every committed scheme, comprehensive component set, active maintenance, large community. If none fits, record the decision to build a project-owned base layer in References.md, with the reason.
- Research how to configure the library's theme system with custom design tokens. Set up every committed scheme.
- Research the library's recommended wrapping patterns. How do you create thin wrappers that pass through all props while applying project defaults?
- Research the library's tree-shaking support so only used components are included in the bundle.
- Configure every committed scheme before wrapping any components. The theme must work end-to-end before features start.
- Document the foundation choice (or the decision to rule otherwise), wrapper location, import conventions, available components, and theme configuration in References.md.
