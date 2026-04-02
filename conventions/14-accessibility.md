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
- Placeholder alt text never replaced: alt="image" or alt="placeholder"
- Images without alt attribute at all

## Right vs Wrong

Examples are illustrative.

```
WRONG (div as button):
<div onClick={handleSubmit} className="btn">Submit</div>

RIGHT (semantic HTML):
<button onClick={handleSubmit} type="submit">Submit</button>
```

```
WRONG (input without proper label):
<input placeholder="Email" value={email} onChange={setEmail} />

RIGHT (visible label associated with input):
<label htmlFor="email">Email</label>
<input id="email" type="email" value={email} onChange={setEmail}
       aria-describedby={error ? 'email-error' : undefined} />
{error && <span id="email-error" role="alert">{error}</span>}
```

```
WRONG (placeholder alt text):
<img src="/hero.jpg" />
<img src="/chart.png" alt="image" />

RIGHT (meaningful alt text + dimensions):
<img src="/hero.webp" alt="Team collaboration in the new office"
     width={1200} height={600} loading="lazy" />
<img src="/chart.png" alt="Revenue grew 32% from Q1 to Q2" />
```

## References.md Section

- A11y testing: which tools (jest-axe, axe-core, keyboard testing)
- WCAG target: which level (AA or AAA)
- Base components: which accessible components exist in shared/ui
