# Convention #0: Reusability & Composition (META)

## Applies when

Every project. Which concerns are shared depends on how the application works: a client that calls a service has one place that talks to it, and a command-line tool with no network has no such place; a product with many screens shares components that a one-screen tool does not have.

## Principle

Build each capability once and reuse it. This is the standard the other conventions apply to their own concerns:
- **One owner per concern.** One place holds each rule, contract, component and integration, and everything else uses it.
- **No duplicated logic, components or contracts.** When the same shape is needed in a second place, it moves to one owner instead of being copied.
- **No bloat.** Build what the product needs now: no layer, option or abstraction without a present consumer.
- **Sized to real usage.** Speed, capacity and cost follow the workload the project's facts describe, measured rather than guessed (#13).

Separation is the exception, and it is recorded. Code that looks alike but changes for different reasons stays separate, with the reason written where the project records decisions.

## Reusable System

The project's shared systems: each concern the application has, its one owner, and the rule that keeps other code from going around it. References.md records each owner and its location. Its `## Boundaries` section records what only that owner may use, one line per concern, and `scripts/validate-develop.sh` enforces those lines. A concern gets its owner the first time a second place needs it.

## Rules

- Before building, look for what already exists: in the project first, then in the stack's standard library and maintained packages, then in services that fit the need. Reuse what fits and adapt what nearly fits. Build new only for a reason you can state.
- When the same logic, component, rule or contract is needed a second time, give it one owner and make both places use it. Never keep two copies that can drift.
- Keep one source of truth across boundaries too: between client and server, between packages, between a template and the products made from it. When a copy is the price of separation, a sync step keeps it in step (#10).
- Do not merge what only looks alike. Two things that change for different reasons stay separate; record the reason in one line.
- Build for the uses that exist or are committed. A speculative abstraction is bloat, and copying code is not the way to avoid one.
- Respect the owner of a shared capability. Changing or replacing it is a consequential decision, made with its consumers identified and verified (#16, #29).
- Record a material choice once, at the project's decision location, with its reason. A routine use of that choice needs no new record.

## Violations

- A second implementation of something the project already owns: another client, error path, validation, component, or copy of a rule.
- Two copies of one contract that drift, such as a shape defined on both sides of an API with nothing keeping them in step.
- A shared system that features route around.
- An abstraction, layer or option no current feature uses.
- Two things that change for different reasons merged into one, so that every change to one breaks the other.
- Capacity, caching or infrastructure far beyond the workload the facts describe.

## Wrong vs Right

- WRONG: a second feature copies the first feature's request code and adjusts it. RIGHT: both use the one place the project calls that service from.
- WRONG: two screens each build their own confirmation dialog. RIGHT: one dialog component, configured by each screen.
- WRONG: merge an invoice total and a cart total into one function because the arithmetic looks the same, although their tax rules change separately. RIGHT: keep them apart and record why.
- WRONG: build a plugin system for a tool with one known use. RIGHT: build the one use, and extract when the second arrives.
- WRONG: choose the most popular option before checking the owner's workflow. RIGHT: compare fit, integration and the cost of owning it against the alternatives.

## Research Notes

Before building a shared system, research what the chosen stack already provides: the standard library, maintained packages, and the platform's own services. Compare fit, maintenance and lifetime cost, and look for evidence against the first option as well as for it. Record each shared system's owner in References.md and its boundary in § Boundaries.
