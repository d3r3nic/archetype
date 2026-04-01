# Convention #14: Accessibility

## Principle

The app works for everyone. Semantic HTML is the foundation. Interactive elements are keyboard-navigable. Screen readers can interpret the UI. Focus is managed intentionally. Color is never the only way to communicate information. Accessibility is built into components at the foundation level, not added after.

## Reusable System

- Accessible base components: Modal, Dialog, Dropdown built with proper ARIA from day one
- Focus management utilities: trap, return, announce
- Skip link component: first focusable element on every page
- Screen reader utilities: visually hidden text, live regions

## Rules

- Use semantic HTML. button for actions, a for navigation. Never div onClick.
- Every interactive element is keyboard accessible.
- Every form input has a visible label.
- Focus is trapped in modals and returned to trigger on close.
- Heading hierarchy is logical (h1→h6, no skipping).
- Color contrast meets 4.5:1 for normal text, 3:1 for large text.
- No color-only communication. Pair with icons, patterns, or text.
- Visible focus indicators on all interactive elements.
- prefers-reduced-motion is respected.

## Violations

- `<div onClick>` instead of `<button>`
- Input without a label (or only placeholder as label)
- Modal that doesn't trap focus or return it on close
- Skipping heading levels (h1 → h3)
- Removing focus outline without replacement
- Color as the only indicator of state (red = error, with no icon or text)

## References.md Section

- A11y testing: which tools (jest-axe, axe-core, keyboard testing)
- WCAG target: which level (AA or AAA)
- Base components: which accessible components exist in shared/ui
