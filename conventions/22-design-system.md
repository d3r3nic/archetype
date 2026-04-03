# Convention #22: Design System

## Principle

Do not reinvent the wheel. Use an established, production-grade UI component library as the foundation (MUI, Chakra, Radix, Ant Design, FluentUI, or the framework's equivalent). Configure it with the project's theme (light + dark mode, design tokens, spacing scale). Wrap the components and export them. Features import from the project's wrapper layer, never directly from the UI library.

The design system is not built from scratch with raw HTML and CSS classes. It's an established library, configured per project, wrapped for consistency, and exported as the project's component foundation.

## Reusable System

Create a design system foundation that establishes:
- An established UI component library installed and configured with the project's theme (light and dark mode, design tokens, spacing, typography)
- Wrapper components around the UI library. The wrappers import from the library, apply theme configuration, enforce consistent API, and re-export. Features only import from the wrappers.
- The wrapper layer is thin. It configures and re-exports. It does not rebuild components from scratch. The UI library already handles accessibility, keyboard navigation, focus management, responsive behavior, and visual consistency.
- A component catalog showing all available wrapped components so developers and AI can see what exists before building anything new
- A deprecation process for components being replaced

## Rules

- Start with an established UI library. Do not build buttons, inputs, modals, dropdowns, tables, or other standard UI components from scratch. These libraries have years of accessibility work, browser testing, and edge case handling built in.
- Configure the library's theme with the project's design tokens: light mode colors, dark mode colors, spacing scale, typography scale, shadows, border radius. Both themes must work.
- Wrap every component the project uses. The wrapper imports from the UI library, applies any project-specific defaults, and re-exports. Features import from the wrapper, never from the library directly.
- The wrapper layer is where theme enforcement happens. If a component needs project-specific styling or defaults, that goes in the wrapper. Features get a clean, consistent API.
- Before building any new component, check feature-tree.md and the shared component directory. AI builds duplicate components at a very high rate because it doesn't check what exists.
- Never install a second UI library for a single widget. Find a component within the existing library or find a standalone one that integrates with the project's theme.

## Violations

- Building buttons, inputs, modals, or other standard components from scratch with raw HTML and CSS when an established library is available
- Importing components directly from the UI library in feature code instead of from project wrappers
- Building a new component without checking if one already exists
- UI library-specific API patterns leaking into feature code
- No dark mode support in the UI library configuration
- Components using hardcoded colors instead of the configured theme

## Wrong vs Right

- WRONG: building a Button component from scratch with Tailwind classes, manually handling focus states, hover states, disabled states, keyboard interaction. Reinventing what MUI/Chakra already provides.
- RIGHT: installing MUI (or equivalent), configuring its theme with the project's design tokens (light + dark), wrapping MUI Button with project defaults, exporting it. One line of config vs 50 lines of custom code.
- WRONG: feature code imports Button directly from the UI library. 50 features import directly. Switching libraries means rewriting 50 features.
- RIGHT: feature code imports Button from the project's wrapper layer. Switching libraries means updating the wrappers only. Zero feature code changes.
- WRONG: the UI library is configured with light mode only. Someone asks for dark mode later. Every component needs manual dark mode colors added.
- RIGHT: the UI library is configured with light AND dark themes from day one. The theme system handles switching. Components adapt automatically.

## Research Notes

When bootstrapping this convention:
- Research the most established, production-grade UI component library for the chosen framework. Pick one with: built-in accessibility, theme customization (light + dark), comprehensive component set, active maintenance, large community.
- Research how to configure the library's theme system with custom design tokens. Set up both light and dark themes.
- Research the library's recommended wrapping patterns. How do you create thin wrappers that pass through all props while applying project defaults?
- Research the library's tree-shaking support so only used components are included in the bundle.
- Configure both light and dark themes before wrapping any components. The theme must work end-to-end before features start.
- Document the UI library choice, wrapper location, import conventions, available components, and theme configuration in References.md.
