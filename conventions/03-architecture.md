# Convention #3: Code Architecture & Patterns

## Principle

Architecture makes responsibilities and dependencies understandable while supporting the product's actual behavior and expected change. Select boundaries from domain needs, runtime constraints and existing code. Services, layers, modules and runtime-native composition are possible answers, not a universal arrangement.

## Reusable System

Identify who owns important state, invariants and external effects, and how consumers reach them. Record consequential boundaries and the verification that protects them. Use the project's existing decision location and References.md rather than a second architecture inventory (#16).

## Rules

- Inspect current behavior and dependencies before selecting or replacing a structure. Research relevant uncertainty and compare alternatives on fit, complexity, testability and change cost (#0).
- Give each responsibility a clear owner. Separate transport, domain behavior or persistence when those boundaries help this project; do not manufacture layers that merely forward calls.
- Keep externally used contracts explicit. Consumers should not rely on another module's private details. Cross-feature use through an intentional public contract can be appropriate.
- Weigh extraction against coupling. Share invariants that must remain consistent; similar implementations with independent reasons to change may remain separate. Record a consequential tradeoff rather than treating either duplication or sharing as automatically correct.
- Examine dependency cycles for ownership and initialization problems. Choose a graph the runtime and team can reason about, with tests for important lifecycle behavior.
- Build the requested behavior. Do not add unrequested capabilities to justify a preferred architecture.
- Verify referenced functions and interfaces exist. Follow accepted project contracts; changing one requires impact review and dependent verification (#29, development/STEPS.md).

## Violations

- Choosing an architecture before understanding the required behavior
- Hiding shared state or external effects behind unclear ownership
- Breaking a consumer by silently changing an accepted interface
- Adding service layers or shared abstractions without a reason beyond the framework example

## Wrong vs Right

- WRONG: prescribe the same service/data layers to a small local tool and a long-lived multi-service product. RIGHT: compare their state, lifecycle and change needs, then select boundaries and tests appropriate to each.
- WRONG: couple two features through private storage merely to remove similar lines. RIGHT: determine whether they share an invariant; use an intentional contract if they do, and separate ownership if they do not.
- WRONG: add batch processing because it fits the chosen architecture. RIGHT: implement the owner's requested operation and record any demonstrated future need separately.

## Research Notes

Dated notes: anything named in this section is an example from the time of writing and expires. Verify current options at bootstrap.

Consult maintained runtime guidance and relevant architectural experience, including counterexamples to the initial choice. Validate uncertain boundaries with a small experiment when that will change the decision. Record the chosen pattern, alternatives and conditions for revision at the existing decision location.
