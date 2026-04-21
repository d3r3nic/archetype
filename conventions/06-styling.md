# Convention #6: Styling, Theming & Responsive Design

## Principle

All visual values flow from a single theme system. No color, spacing, shadow, typography, or dimension value is ever written directly in code. A design token hierarchy ensures consistency and enables theming, dark mode, and responsive behavior from one source of truth. AI hardcodes visual values constantly - this convention prevents it.

The theme ALWAYS supports light and dark mode. This is not optional. Dark mode is a production requirement, not a nice-to-have. The theme system detects the user's system preference and allows manual override.

## Reusable System

Create a production-grade theme system that establishes:
- Design tokens organized in layers: primitive tokens (raw values like specific hex colors), semantic tokens (role-based names like "text-primary" that reference primitives), and component tokens (scoped to specific components). Semantic tokens swap between light and dark mode automatically.
- A theme object as the single source of truth: colors (with light and dark variants), spacing scale, typography scale, shadow scale, z-index scale, breakpoint scale
- Light and dark themes defined through semantic token swapping. Components never reference light or dark values directly. They reference semantic tokens ("text-primary", "bg-surface") that resolve differently based on the active theme.
- System preference detection for initial theme (prefers-color-scheme) with user override stored persistently
- A consistent spacing scale based on a base unit (typically 4px: 4, 8, 12, 16, 24, 32, 48, 64)
- A consistent typography scale with paired line heights for each size
- A z-index scale with named levels (dropdown, sticky, overlay, modal, popover, toast, tooltip)

## Rules

- Never hardcode colors anywhere. Always reference semantic theme tokens.
- Never hardcode spacing or dimensions in component code. Use the theme's spacing scale.
- Never use arbitrary z-index values. Use the named z-index scale.
- Name tokens by role, not by value. "text-primary" not "gray-900." Roles stay the same across themes, values change.
- Dark mode is always implemented. Not optional. Detect system preference, allow user override, persist the choice.
- Mobile-first responsive design: base styles for small screens, progressively enhance for larger screens.
- Respect user preferences: honor system dark mode preference and reduced motion preference.
- All interactive elements must have adequate touch target size for mobile (minimum 44x44 points).

## Violations

- Any hardcoded color value (hex, rgb, rgba, hsl) anywhere in component or style code
- Hardcoded pixel values for spacing instead of using the spacing scale
- Arbitrary z-index values instead of using the named scale
- No dark mode support (light-only theme)
- Dark mode implemented by duplicating color values instead of swapping semantic tokens
- Components referencing "gray-50" or "red-600" directly instead of semantic tokens like "bg-surface" or "color-error"

## Wrong vs Right

- WRONG: a component with color "#333", padding "16px", z-index "9999" hardcoded. Change the theme and this component doesn't update.
- RIGHT: the component references "text-primary" for color, spacing scale for padding, "modal" from z-index scale. Change the theme and everything updates. Switch to dark mode and the component adapts automatically.
- WRONG: dark mode implemented by adding separate dark color values throughout the codebase. Every new component needs both light and dark colors manually.
- RIGHT: dark mode implemented by swapping semantic token values at the theme level. "text-primary" maps to dark gray in light mode and light gray in dark mode. Components don't know or care which mode is active.
- WRONG: components use Tailwind defaults (gray-50, red-600) or raw color values. These don't change when the theme changes.
- RIGHT: components use semantic tokens (bg-surface, text-primary, color-error) that are defined in the theme and resolve to different values in light vs dark mode.

## Template vs product — tokens in each

Per framework Step 49, token responsibility splits by project shape:

- **Template projects** ship the STRUCTURE: primitive layer (`--t-*`) with system-neutral values (`Canvas`/`CanvasText` keywords, `currentColor`, rem-based sizing) and semantic layer (`--bg-surface`, `--text-primary`, etc.) referencing primitives. Zero hex literals, zero brand commitment. The template's token file is a shell: layer boundaries and semantic role names are the contract, primitive VALUES are placeholders.
- **Product projects** (customer sites spawned from templates, or one-off custom builds) commit brand values by overriding `--t-*` primitives in their own stylesheet loaded AFTER the template's token file. Semantic names stay stable — feature code consumes semantics, never primitives.

Example — template file ships:
```css
:root { --t-color-accent: AccentColor; --bg-surface: var(--t-color-bg); }
```
Customer site overrides:
```css
:root { --t-color-accent: oklch(0.55 0.2 260); }
```

Semantic tokens (`--bg-surface`, `--color-accent` if declared) don't change — customer-site components keep consuming them and pick up the brand value automatically.

## Research Notes

When bootstrapping this convention:
- Research the framework's recommended theming approach. How does the framework handle design tokens, theme objects, and dynamic theming?
- Research the latest and most production-grade approach to theming. Do not reinvent the wheel - use an established UI library's theme system as the foundation.
- Research dark mode implementation. The theme must support light and dark mode from day one. Detect system preference (prefers-color-scheme), allow manual toggle, persist user choice.
- Research the framework's responsive design patterns. Mobile-first.
- Research the latest loading indicator patterns (skeleton screens, shimmer effects, or current best practice - not just spinners)
- Document the theme system location, token structure, light/dark setup, and usage patterns in References.md
