# Convention #22: Design System

## Principle

A shared component library is the single source of truth for UI. Components are built on top of the UI library through wrappers that enforce theming. Features never interact with the UI library directly. The design system is token-first: visual decisions are encoded in tokens before component implementation begins.

## Reusable System

- UI library wrappers: components that wrap MUI/Chakra/Radix with theme enforcement
- Token system: design tokens as the foundation for all visual values
- Component catalog: Storybook or equivalent showing all components and variants
- Contribution process: how new components are proposed, built, and added

## Rules

- Never import directly from the UI library. Always use project wrappers.
- Exception: icons can often be imported directly (project-specific).
- If a wrapper doesn't exist for a UI library component, create it first.
- Token-first: define tokens before building components.
- Every component in the design system has documentation showing all variants.
- Deprecation: announce, mark @deprecated, provide migration path, then remove.

## Violations

- `import { Button } from '@mui/material'` instead of `import { Button } from '@/shared/ui'`
- Building a component without checking if it exists in the design system
- UI library updates breaking the app because features import directly
- Components with no documentation or variant examples

## References.md Section

- UI library: which one and version
- Wrapper location: path to project wrappers
- Import rule: exact import path to use
- Icon exception: whether icons can be imported directly
- Storybook: URL or command to access component catalog
