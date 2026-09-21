# Convention #0: Reusability & Composition (META)

## Principle

Start from the owner's purpose and the work that already exists. Reuse can reduce effort and prevent inconsistent behavior; abstraction can also create coupling and maintenance that the project does not need. Choose between reuse, adaptation and a focused implementation using the actual requirements and evidence. This lens applies across the conventions without requiring a foundational system for every concern.

## Reusable System

Look for capabilities and invariants with more than one real consumer. A shared implementation is valuable when those consumers should change together. Keep separately evolving behavior separate. Record where accepted shared capabilities live so later work can find them; do not create speculative consumers to justify an abstraction.

## Rules

- Understand whether the owner is seeking a shipped outcome, learning, experimentation or another goal. Evaluate success against that purpose.
- Inspect the relevant project code and records before building. Evaluate existing products, libraries and services when they could materially meet the need.
- Research uncertain or changing facts, including current support, limitations, integration, ownership and lifetime cost. Compare alternatives against important requirements, not a coverage percentage or market ranking.
- Use a shared capability when its contract fits. If it does not, examine adaptation, composition and a separate implementation, including the cost of coupling and duplicated invariants.
- Choose an abstraction when current uses or a concrete commitment justify it. Similar code is evidence to inspect, not an automatic instruction to extract or forbid duplication.
- Respect the project's accepted boundaries and ownership. Replacing a shared capability is a consequential decision, with affected consumers and verification identified (#16, #29).
- Record a material choice once at the project's decision location, including its reason and conditions for revisiting it. A routine use of that choice needs no new decision record.

## Violations

- Rebuilding a capability without checking whether the existing contract fits
- Forcing a platform because it satisfies many minor requirements while missing the owner's central purpose
- Creating an unused framework of services for a small experiment
- Sharing behavior that only looks similar but has different reasons to change
- Copying a critical invariant into multiple places with no ownership or consistency check

## Wrong vs Right

- WRONG: choose the market leader before checking the required workflow. RIGHT: verify its relevant capabilities and compare the unmet need, integration, control and maintenance costs with viable alternatives.
- WRONG: extract a shared service because any code might someday be reused. RIGHT: inspect current consumers and expected change; keep a focused implementation when extraction adds no demonstrated value.
- WRONG: use a different error path in each feature despite an accepted shared recovery contract. RIGHT: reuse that contract, or deliberately revise it with affected consumers and evidence.

## Research Notes

Dated notes: anything named in this section is an example from the time of writing and expires. Verify current options at bootstrap.

Use the project's language, runtime and purpose to find relevant current practice. Look for evidence that challenges the initial option as well as supports it. Place selected tools and implementation details in References.md. Bootstrap's research step and conventions #3, #16 and #29 carry the related architecture, record and authority concerns.
