# Convention #16: Documentation & Decisions

## Principle

Documentation captures what code cannot express: intent, constraints, business reasoning, and architectural decisions. Comments explain WHY, never WHAT. Specifications are written for machine consumption - explicit, with examples, file paths, and concrete patterns. Over-commenting is as harmful as under-commenting.

AI-era reasoning: AI over-comments 90-100% of generated code with obvious descriptions. The convention shifts from "document everything" to "document only what isn't self-evident." But architectural decisions, constraints, and business reasoning must be explicit because AI cannot infer them.

## Reusable System

- ADR template: standard format for architecture decisions
- Feature README template: what/why/how for each feature
- Spec template: format for feature specifications

## Rules

- Comments explain WHY or provide context. Never explain WHAT the code does.
- If code is self-explanatory, no comment needed.
- Feature README: what it does, why it exists, how it works.
- Update documentation after code changes. Stale docs are worse than no docs.
- Architecture Decision Records for significant decisions (framework choices, patterns, trade-offs).
- Structured TODOs: // TODO(scope): description [ticket]
- Descriptive naming over brevity. calculateMonthlyRevenue not calcRev.
- Explicit over implicit. No magic strings or convention-based wiring AI cannot infer.
- No abbreviations in domain terms. Spell them out.

## Violations

- // Increment counter by 1 (commenting the obvious)
- Stale README that describes a different version of the code
- Magic strings or numbers without explanation
- Domain abbreviations that only insiders understand
- Feature with no README explaining why it exists
- Magic numbers with no reasoning (TIMEOUT = 3000 - why 3000?)

## Right vs Wrong

Examples are illustrative.

```
WRONG (commenting the obvious - 90-100% of AI code does this):
// Initialize the user array
const users: User[] = [];
// Loop through each order
for (const order of orders) {
  // Get the order total
  const total = order.getTotal();
  // Check if total is greater than 100
  if (total > 100) {
    order.applyDiscount(0.1);
  }
}

RIGHT (comment only the WHY):
for (const order of orders) {
  const total = order.getTotal();
  // Business rule: orders over $100 qualify for loyalty discount (JIRA-1234)
  if (total > 100) {
    order.applyDiscount(0.1);
  }
}
```

```
WRONG (magic numbers with no explanation):
const TIMEOUT = 3000;
const MAX_RETRIES = 5;
const BATCH_SIZE = 50;

RIGHT (explain the reasoning):
// Payment gateway SLA requires response within 3s; timeout triggers fallback
const PAYMENT_TIMEOUT_MS = 3000;
// 5 retries with exponential backoff covers typical network blips (p99 recovery)
const MAX_RETRIES = 5;
// DynamoDB batch write limit is 25; we use 50 items chunked into 2 batches
const BATCH_SIZE = 50;
```

## References.md Section

- ADR location: where architecture decisions are stored
- Feature README: expected sections and format
- Comment convention: any project-specific comment patterns
