# Convention #6: Styling, Theming & Responsive Design

## Principle

Visual implementation follows the accepted design commitments and the needs of the medium. Research the platform's current styling and theming mechanisms, then choose a source of truth that keeps repeated decisions coherent without forcing an unnecessary token architecture. Values used in code must be traceable to the accepted artifact or the recorded styling decision. Once the project selects a token, theme, native-style, or other contract, code follows it consistently.

The project records the schemes it commits to and why. It implements and verifies those schemes without implying that every product needs light and dark, a manual switch, one accent, or a framework-defined semantic role set.

## Reusable System

Establish a styling system fitted to the project:
- A recorded source of truth for repeated visual decisions and any intentional direct values required by the medium.
- A role vocabulary derived from the interface's actual needs, including focus and status meanings where they apply.
- Scales or named values where they improve consistency and changeability. The project chooses their shape from the content, interactions, contexts, and access needs.
- Every committed scheme and context, with the mapping or adaptation each requires.
- A documented way for features to consume styling decisions without silently creating a competing source.

## Rules

- Trace visual choices in code to the accepted artifact, the recorded styling source, or a documented platform requirement.
- Avoid scattered repeated literals whose relationship should survive a change. A direct value is valid when the selected medium or styling contract calls for it and its purpose remains discoverable.
- Name shared values by purpose where roles are stable. Define only the roles the product needs, and add or revise a role when evidence justifies it.
- Keep status, brand, data, and interaction meanings distinguishable. Do not rely on color alone.
- Meet the project's recorded accessibility target in every committed scheme and on every surface where a value is used. A failing pair is fixed before acceptance.
- Implement every committed scheme. Detect platform preference, offer an override, or persist a choice only when the project's context and accepted design require that behavior.
- Design for the primary context and verify every committed context. Pointer, touch, keyboard, controller, assistive technology, or other inputs apply according to the project and accessibility target.
- Honor reduced motion and other applicable user or platform preferences without removing required meaning or control.
- Design content may carry literal values. Code adopts them through the project's selected styling contract rather than copying them without provenance.

## Violations

- Repeated visual values drift because the project has no discoverable source of truth.
- Code contradicts an accepted scheme, context, brand, or accessibility decision.
- A shared token keeps a misleading name after its purpose changes.
- A status or interaction meaning is conveyed by color alone.
- A feature creates a competing styling source without recording why the existing approach no longer fits.
- An uncommitted scheme or interaction is presented as supported.

## Wrong vs Right

- WRONG: copy a mockup's values into several components with no link to the accepted direction.
- RIGHT: adopt the values through the project's recorded styling mechanism and verify them in the committed contexts.
- WRONG: require one accent and a fixed status palette before learning what the product communicates.
- RIGHT: derive a coherent role set from the actual interface, preserve distinctions people need, and test the combinations in use.
- WRONG: build a scheme switch because user-facing products are assumed to need one.
- RIGHT: implement the committed scheme set and the platform behavior the project chose, with evidence for each.

## Template vs product: tokens in each

A template records the styling boundary and ships neutral, replaceable values appropriate to its medium. It does not prescribe a downstream product's palette, role names, density, typography, or number of schemes. A product adopts its accepted brand and interaction decisions into that boundary. If the downstream product changes the boundary, it records the reason and migrates consumers rather than maintaining two silent sources of truth.

## Research Notes

Dated notes: anything named in this section is an example from the time of writing and expires. Verify current options when scaffolding the styling system.

- Research the chosen runtime's styling, theming, adaptation, user-preference, and accessibility mechanisms.
- Inspect the accepted artifact, actual content, interaction patterns, committed contexts, and existing project styles before proposing scales or roles.
- Test contrast, focus, reflow, target sizing, reduced motion, and scheme behavior that the project commits to.
- Document the source, consumption pattern, committed schemes and contexts, and verification commands in References.md.
