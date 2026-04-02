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
- Building a new component without checking feature-tree.md for existing ones
- UI library updates breaking the app because features import directly
- Components with no documentation or variant examples
- Library-specific APIs (sx prop, Chakra style props) leaking into feature code
- Installing a different UI library for one widget (visual inconsistency, bundle bloat)

## Right vs Wrong

Examples are illustrative.

```
WRONG (direct UI library import):
import { Button, TextField, Dialog } from '@mui/material';

RIGHT (project wrapper imports):
import { Button, TextField, Dialog } from '@/shared/ui';
// If wrapper doesn't exist, create it first
```

```
WRONG (library-specific API leaking into features):
<Box sx={{ display: 'flex', gap: 2, bgcolor: 'primary.main', p: 3 }}>
  <Button variant="contained" sx={{ borderRadius: '8px' }}>Save</Button>
</Box>

RIGHT (wrapper abstracts the library):
<Stack direction="row" gap="md" bg="primary" padding="lg">
  <Button variant="primary">Save</Button>
</Stack>
// If you switch from MUI to Radix, only wrapper internals change
```

```
WRONG (not checking what exists - building redundant component):
// Creates ConfirmDialog.tsx without checking feature-tree.md
// Project already has a ConfirmDialog in shared/ui

RIGHT (check first):
// 1. Read feature-tree.md
// 2. Search shared/ui for existing components
// 3. If exists: use it. If not: build it in shared/ui as reusable.
```

## References.md Section

- UI library: which one and version
- Wrapper location: path to project wrappers
- Import rule: exact import path to use
- Icon exception: whether icons can be imported directly
- Storybook: URL or command to access component catalog
