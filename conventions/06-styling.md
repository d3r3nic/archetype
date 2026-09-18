# Convention #6: Styling, Theming & Responsive Design

## Principle

All visual values flow from a single theme system. No color, spacing, shadow, typography, or dimension value is ever written directly in code. A design token hierarchy ensures consistency and enables theming, dark mode, and responsive behavior from one source of truth. The theme is the only place a visual value is written; the lint rule the project configures under #25 catches a literal value in code, and review reads the rest.

The theme is built to swap color schemes from day one, because a scheme cannot be bolted on later without touching every component. Light and dark are the default pair for user-facing products; the project records its committed scheme set in References.md. A project that commits to a single scheme records why and still builds the semantic layer, so a second scheme costs configuration, not a rewrite. The theme system detects the user's platform preference and allows manual override.

## Reusable System

Create a production-grade theme system that establishes:
- Design tokens organized in layers: primitive tokens (raw values), semantic tokens (roles that reference primitives), and component tokens (scoped to specific components). The semantic layer's role set is fixed by this convention and filled by the project: surface levels, ink levels, one accent, the signals (success, warning, danger, info), focus, and the on-color for text placed on each of them. A feature adds no role. Semantic tokens swap between schemes; components reference only semantic and component tokens.
- A theme object as the single source of truth: colors per scheme, the spacing scale, the type scale with its measure, radius, shadow and z-index scales that name the same elevation levels, motion (durations and easings), the focus style, container widths, breakpoints
- Light and dark themes defined through semantic token swapping. Components never reference light or dark values directly. They reference semantic tokens ("text-primary", "bg-surface") that resolve differently based on the active theme.
- Detection of the platform's color-scheme preference for the initial scheme, with the person's override stored persistently
- A spacing scale built from one base step and its multiples, used as a ladder of relationship (#31)
- A short closed type scale: each step with its size, line height, weight set, and job, plus a measure token (#31)
- A z-index scale with named levels (dropdown, sticky, overlay, modal, popover, toast, tooltip)

## Rules

- Never hardcode colors anywhere. Always reference semantic theme tokens.
- Never hardcode spacing or dimensions in component code. Use the theme's spacing scale.
- Never use arbitrary z-index values. Use the named z-index scale.
- Name tokens by role, not by value. "text-primary" not "gray-900." Roles stay the same across themes, values change.
- One accent, one meaning: here is where you act, or this is what is selected. The accent is not decoration and never marks a destructive action.
- Signal colors mean only their signal; a signal color as brand, chart, or decoration is a violation; charts get their own recorded categorical set.
- Contrast is a floor from the project's accessibility target, checked for each ink role on each surface its usage note names, in every committed scheme; a pair that misses is recorded, never silently re-tinted.
- Every scheme the project commits to is implemented from day one through semantic-token swapping, never bolted on later. Detect the platform preference, allow user override, persist the choice.
- Primary context first: the product is designed for the primary context recorded in References.md § Design Artifact and verified in every committed context, each with its own composition where the primary one does not fit; pointer, touch, and keyboard each reach every action; hover is an enhancement. On a native platform the platform's conventions win; one design everywhere is a recorded decision, never a default.
- Respect user preferences: honor system dark mode preference and reduced motion preference.
- Touch targets follow #14: the platform's minimum, recorded in References.md, with space between adjacent targets.
- These rules govern code. Design content a design tool produces (a mockup, an artboard, a preview) carries literal values by nature and follows #27; a value it introduces reaches code only through the token source.

## Violations

- Any hardcoded color value (hex, rgb, rgba, hsl) anywhere in component or style code
- Hardcoded pixel values for spacing instead of using the spacing scale
- Arbitrary z-index values instead of using the named scale
- A single-scheme theme with no recorded decision, or any theme without a semantic layer to swap
- Dark mode implemented by duplicating color values instead of swapping semantic tokens
- Components referencing "gray-50" or "red-600" directly instead of semantic tokens like "bg-surface" or "color-error"
- A mockup's literal value copied into component code instead of a token added to the theme first
- The accent on a destructive action, or a signal color used as brand or decoration

## Wrong vs Right

- WRONG: a component with color "#333", padding "16px", z-index "9999" hardcoded. Change the theme and this component doesn't update.
- RIGHT: the component references "text-primary" for color, spacing scale for padding, "modal" from z-index scale. Change the theme and everything updates. Switch to dark mode and the component adapts automatically.
- WRONG: dark mode implemented by adding separate dark color values throughout the codebase. Every new component needs both light and dark colors manually.
- RIGHT: dark mode implemented by swapping semantic token values at the theme level. "text-primary" maps to dark gray in light mode and light gray in dark mode. Components don't know or care which mode is active.
- WRONG: components use a utility framework's default palette names (gray-50, red-600) or raw color values. These don't change when the theme changes.
- RIGHT: components use semantic tokens (bg-surface, text-primary, color-error) that are defined in the theme and resolve to different values in light vs dark mode.

## Template vs product — tokens in each

Token responsibility splits by project shape:

- **Template projects** ship the STRUCTURE: a primitive layer with system-neutral placeholder values (platform color keywords, current-color inheritance, relative sizing) and a semantic layer that references primitives. Zero literal color values, zero brand commitment. The template's token file is a shell: layer boundaries and semantic role names are the contract, primitive VALUES are placeholders.
- **Product projects** (customer sites spawned from templates, or one-off custom builds) commit brand values by overriding the primitives in their own layer loaded AFTER the template's token file. Semantic names stay stable — feature code consumes semantics, never primitives.

The template ships a primitive such as "accent = the platform's accent keyword" and a semantic "surface background = the primitive background". The customer site overrides only the primitive with its brand value. Semantic tokens do not change, so customer-site components keep consuming them and pick up the brand value automatically. The token naming scheme itself is the project's choice, recorded in References.md. Brand fills the primitives, the voice, the imagery, and the motion signature; the semantic roles, the state list (#27), the vocabulary discipline and the composition rules (#31) are the neutral layer every brand shares, and a brand never changes a role's meaning.

## Research Notes

Dated notes: anything named in this section is an example from the time of writing and expires. Verify current options at bootstrap.

When bootstrapping this convention:
- Research the framework's recommended theming approach. How does the framework handle design tokens, theme objects, and dynamic theming?
- Research the latest and most production-grade approach to theming. Do not reinvent the wheel - prefer an established component foundation's theme system when one fits the product (see #22).
- Research multi-scheme implementation for the framework. Every committed scheme must be swappable from day one. Detect the platform preference, allow manual toggle, persist user choice.
- Research the framework's responsive patterns for the recorded primary context and every committed context.
- Research the latest loading indicator patterns (skeleton screens, shimmer effects, or current best practice - not just spinners)
- Document the theme system location, token structure, light/dark setup, and usage patterns in References.md
