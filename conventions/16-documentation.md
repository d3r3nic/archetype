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

## References.md Section

- ADR location: where architecture decisions are stored
- Feature README: expected sections and format
- Comment convention: any project-specific comment patterns
