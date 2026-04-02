# Convention #6: Styling, Theming & Responsive Design

## Principle

All visual values flow from a single theme system. No color, spacing, shadow, typography, or dimension value is ever written directly in code. A design token hierarchy ensures consistency and enables theming, dark mode, and responsive behavior from one source of truth. AI hardcodes visual values constantly - this convention prevents it.

## Reusable System

Create a theme system that establishes:
- Design tokens organized in layers: primitive tokens (raw values like specific hex colors), semantic tokens (role-based names like "text-primary" that reference primitives), and component tokens (scoped to specific components)
- A theme object or token file as the single source of truth for all visual values: colors, spacing scale, typography scale, shadow scale, z-index scale, breakpoint scale
- Wrapper components or utilities that enforce theme usage so features cannot bypass the theme
- Dark mode support through semantic tokens that swap values based on theme, not through duplicated color definitions
- A consistent spacing scale based on a base unit (typically 4px: 4, 8, 12, 16, 24, 32, 48, 64)
- A consistent typography scale with paired line heights for each size
- A z-index scale with named levels (dropdown, sticky, overlay, modal, popover, toast, tooltip) so z-index values are never arbitrary numbers

## Rules

- Never hardcode colors anywhere. Always reference theme tokens.
- Never hardcode spacing or dimensions in component code. Extract to named constants or use the theme's spacing scale.
- Never use arbitrary z-index values. Always use the named z-index scale.
- Name tokens by role, not by value. "text-primary" not "gray-900." Roles stay the same across themes, values change.
- Mobile-first responsive design: base styles for small screens, progressively enhance for larger screens.
- Respect user preferences: honor system dark mode preference and reduced motion preference.
- All interactive elements must have adequate touch target size for mobile (minimum 44x44 points).

## Violations

- Any hardcoded color value (hex, rgb, rgba, hsl) anywhere in component or style code
- Hardcoded pixel values for spacing (padding: 16px) instead of using the spacing scale
- Arbitrary z-index values (z-index: 9999) instead of using the named scale
- Different spacing values used inconsistently across components (12px here, 14px there, 15px elsewhere)
- Dark mode implemented by duplicating color values instead of swapping semantic tokens
- Fixed breakpoint values scattered across files instead of using the breakpoint scale

## Wrong vs Right

- WRONG: a component with color "#333", padding "16px", z-index "9999" hardcoded directly in it. Change the theme and this component doesn't update.
- RIGHT: the component references "text-primary" for color, spacing scale value "4" for padding, and "modal" from the z-index scale. Change the theme and everything updates.
- WRONG: dark mode implemented by adding separate dark color values throughout the codebase. Every new component needs both light and dark colors manually added.
- RIGHT: dark mode implemented by swapping semantic token values. "text-primary" maps to dark gray in light mode and light gray in dark mode. Components don't know or care which mode is active.
- WRONG: z-index chaos. A dropdown uses 100, then a modal needs 9999, then a toast needs 99999. Numbers keep escalating.
- RIGHT: a defined z-index scale. Dropdown is level "dropdown" (100), modal is level "modal" (400), toast is level "toast" (600). Clear hierarchy, no escalation.

## Research Notes

When bootstrapping this convention:
- Research the framework's recommended theming approach. How does the framework handle design tokens, theme objects, and dynamic theming?
- Research CSS methodology options that work with the framework (utility-first, CSS-in-JS, CSS modules, CSS custom properties). Pick one that integrates well with the framework's component model.
- Research the framework's responsive design patterns. How are breakpoints defined and used? What is the recommended approach for mobile-first styles?
- Research dark mode implementation patterns for the framework. How do you switch themes without duplicating values?
- Research the framework's approach to spacing and typography scales
- Document the theme system location, token structure, wrapper components, and usage patterns in References.md
