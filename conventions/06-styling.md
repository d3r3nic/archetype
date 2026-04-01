# Convention #6: Styling, Theming & Responsive Design

## Principle

All visual values flow from a single theme system. No color, spacing, shadow, typography, or dimension value is ever written directly in component code. A design token hierarchy (primitive → semantic → component) ensures consistency and enables theming, dark mode, and responsive behavior from one source of truth.

AI-era reasoning: AI hardcodes colors and dimensions constantly. This is one of the most violated conventions. Without explicit rules, every AI session introduces new hex values and magic numbers.

## Reusable System

- Theme object: single source of truth for all visual values
- Design tokens: primitive (raw values) → semantic (role-based) → component (scoped)
- UI library wrappers: components that enforce theme usage
- Spacing scale: consistent spacing values (e.g., 4px base)
- Typography scale: consistent font sizes with paired line heights
- Z-index scale: named constants (dropdown=100, modal=400, toast=600)
- Breakpoint scale: consistent responsive breakpoints
- Dark mode: theme swap via data attribute or class, semantic tokens only

## Rules

- Never hardcode colors (hex, rgb, rgba). Always use theme tokens.
- Never hardcode spacing or dimensions in JSX. Extract to named constants or config.
- Never use magic numbers. Every number has a name explaining what it is.
- Use the theme's spacing scale for all spacing.
- Use the theme's typography scale for all text.
- Use the theme's shadow scale for all elevation.
- Name tokens by role, not value: color-text-primary, not color-gray-900.
- Mobile-first: base styles for small screens, add with min-width queries.
- Respect prefers-reduced-motion for animations.
- Respect prefers-color-scheme for dark mode default.

## Violations

- `color: '#333'` or `color: 'red'` anywhere in component code
- `width: 320` or `padding: 16` as inline values without named constants
- `z-index: 9999` instead of using the z-index scale
- Different spacing values across components (12px here, 14px there, 15px elsewhere)
- Building dark mode by duplicating color values instead of swapping semantic tokens
- Fixed breakpoint values scattered across files instead of using the breakpoint scale

## Right vs Wrong

```
WRONG:
<Box sx={{ color: '#333', padding: '16px', marginTop: '24px' }}>
<Box sx={{ backgroundColor: '#f5f5f5', borderRadius: '8px' }}>

RIGHT:
<Box sx={{ color: colors.textPrimary, p: 2, mt: 3 }}>
<Box sx={{ bgcolor: colors.bgDefault, borderRadius: 1 }}>
```

```
WRONG (magic numbers):
<Drawer sx={{ width: 320, maxHeight: '80vh' }}>

RIGHT (named config):
const DRAWER_CONFIG = {
  width: { xs: '90%', md: 320 },
  maxHeight: { xs: '45vh', md: '80vh' },
}
<Drawer sx={DRAWER_CONFIG}>
```

```
WRONG (z-index chaos):
z-index: 9999
z-index: 10000
z-index: 99999

RIGHT (z-index scale):
z-index: zIndex.dropdown   // 100
z-index: zIndex.modal      // 400
z-index: zIndex.toast       // 600
```

## References.md Section

- Theme location: path to theme definition file
- Token file: path to design tokens
- UI wrappers: path to wrapper components and import convention
- Color helpers: how to access theme colors (e.g., colors.*, theme.palette.*)
- Spacing: which scale is used and how to apply it
- Breakpoints: project's breakpoint values
