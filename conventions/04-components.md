# Convention #4: Component Design & API

## Principle

Components expose consistent, predictable APIs. Size, variant, and state props follow project-wide conventions. Components are composable - complex UIs are built from small pieces, not monolithic blocks. The component foundation (base components, wrappers) is built once and used everywhere.

## Reusable System

- Base components: wrappers around UI library with theme enforcement
- Component API conventions: consistent size/variant/state prop patterns
- Compound components: related components sharing implicit state
- Layout components: spatial arrangement primitives (Stack, Grid, Flex)

## Rules

- Never import directly from the UI library. Use project wrappers.
- Consistent sizing: size prop uses xs, sm, md, lg, xl across all components.
- Consistent variants: variant prop uses primary, secondary, outline, ghost.
- Consistent state: isDisabled, isLoading, isReadOnly, isRequired, isInvalid.
- Components accept and merge className and style for customization.
- Forward refs on all reusable components.
- Props are minimal. Expose only what consumers need. Derive internally when possible.
- Components render UI. They do not contain business logic.

## Violations

- Importing Button from @mui/material instead of from project wrappers
- Inconsistent sizing (one component uses small/medium/large, another uses xs/sm/md)
- Components that fetch data, compute business logic, AND render UI
- Props that accept string | number | ReactNode | Function for one value

## References.md Section

- Component foundation: path to base/wrapper components
- Import rule: exact import path (e.g., @/shared/ui/mui)
- UI library: which one and version
- Icon exception: if icons can be imported directly
- Existing components: where to find what already exists
