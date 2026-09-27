# Convention #3: Code Architecture & Patterns

## Applies when

Every project. What varies is the shape: a small local tool, a client talking to a service, a long-lived service with many consumers, a simulation, a library. The boundaries worth drawing follow the domain, the runtime, and how the product is expected to change.

## Principle

Every important responsibility has one owner, and every consumer reaches it through that owner's contract. Architecture exists to make responsibilities, dependencies and effects understandable and safe to change. Draw the boundaries this product needs, and no others: a layer that only forwards calls is bloat, and a responsibility with no clear owner is a defect.

## Reusable System

The map of owners: which part of the system owns each important piece of state, invariant and external effect, and how consumers reach it. References.md records the owners and their locations; the decision location records a consequential boundary and its reason; § Boundaries records what only an owner may use, so the checks keep other code from going around it.

## Rules

- Inspect current behavior and dependencies before choosing or replacing a structure. Compare alternatives on fit, complexity, testability and change cost, and research what you are unsure of (#0).
- Give each responsibility one owner. Separate transport, domain behavior and persistence where those boundaries protect this product; do not add layers that only pass calls through.
- Keep contracts between parts explicit. A consumer uses another part's public contract, never its private details or storage.
- Share invariants that must stay consistent: one owner, used everywhere. Keep apart what only looks alike and changes for different reasons, and record why.
- Resolve dependency cycles; choose a dependency graph the runtime and the team can reason about, and test the lifecycle behavior that matters.
- Build the requested behavior. Do not add capabilities to justify a preferred architecture.
- Verify that the functions and interfaces you call exist. Changing an accepted contract needs its consumers identified and verified (#19, #29, development/STEPS.md).

## Violations

- An architecture chosen before the required behavior is understood.
- Two owners for one responsibility, or a responsibility no one owns.
- A consumer reaching into another part's private storage or internals.
- A consumer broken by a silent change to an accepted interface.
- Layers or services that exist only because an example had them.

## Wrong vs Right

- WRONG: give a small local tool and a long-lived multi-service product the same service and data layers. RIGHT: choose each one's boundaries from its state, lifecycle and change needs.
- WRONG: two features each keep their own copy of the rule for who may edit an order. RIGHT: one owner holds the rule; both features call it.
- WRONG: couple two features through one's private storage to save a few lines. RIGHT: if they share an invariant, give it an owner with a contract; if they do not, keep them separate.
- WRONG: add batch processing because the chosen architecture makes it easy. RIGHT: build the operation the owner asked for, and record a demonstrated future need separately.

## Research Notes

Research the runtime's maintained architectural guidance and real experience with the options, including cases where the first choice failed. When a boundary is uncertain, a small experiment that could change the decision is worth more than more reading. Record the chosen owners in References.md, the reasons at the decision location, and the boundaries in § Boundaries.
