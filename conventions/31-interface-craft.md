# Convention #31: Interface Craft

## Principle

An interface is good when people can understand and complete the activity it exists to support. The design may have one focused action or many concurrent actions; it may be quiet or continuously changing. Judge it against the owner's intent, the accepted direction, the medium, actual use, relevant current evidence, and access needs. Type, space, color, motion, words, and interaction should help people perceive state and act with confidence.

The session makes composition decisions within the direction the owner picked or delegated (#27, #29). It preserves supplied constraints and accepted commitments, researches uncertainty, explains material tradeoffs, and records decisions that future work depends on. It does not turn the framework author's visual preferences into project requirements.

## Reusable System

Build only the shared design knowledge the project needs:
- A purpose and activity statement for each screen or flow, kept with its artifact entry.
- A vocabulary that preserves the owner's terms and makes actions and destinations understandable.
- A recorded type, spacing, color, motion, focus, and layout approach appropriate to the medium.
- Reusable state and interaction patterns where consistent behavior helps people.
- A density strategy that can vary by context, role, activity, or viewport when the reason is recorded.
- The design review in #27, grounded in observed task completion and committed evidence.

## Rules

### Hierarchy

- State what the screen or flow helps a person accomplish. If it supports several concurrent activities, name their relationship and priority instead of forcing one purpose.
- Emphasize actions according to consequence, frequency, time pressure, reversibility, and context. One primary action is useful when the activity has one clear next move; it is not a universal screen shape.
- Design an attention order. People should perceive the information and controls needed for the current activity without unrelated elements competing with them.
- Give first-time guidance when the activity requires it, and remove it when it no longer helps.
- Keep density coherent across comparable contexts. Vary it when content, device, role, session length, safety, or interaction mode makes another choice fit better, and verify each committed context.

### Type

- Choose a type system from the content, platform, language, brand, reading conditions, and accessibility target.
- Use enough hierarchy to make structure clear. Repeated roles use consistent treatment; different roles are distinguishable by more than size alone.
- Keep reading measures appropriate to the content and context. Data, labels, dialogue, and long prose may need different measures.
- Use the number and kind of type families the accepted direction can justify. More families increase coordination cost but are not automatically wrong.
- Align numbers and data in the way that makes comparison accurate for the chosen typeface and activity.

### Space and alignment

- Use proximity and separation to communicate relationships. Similar relationships should usually receive similar treatment.
- Align elements to support scanning and comparison. Break alignment when the change communicates a useful distinction.
- Choose a grid, free composition, spatial layout, or combination that fits the medium and activity; record consequential departures from the accepted system.
- Use elevation, layering, depth, or their platform equivalent only when they clarify interaction or state.

### Motion

- Give motion a job such as feedback, continuity, orientation, simulation, urgency, or expression within the accepted direction.
- Research the medium's current motion and input conventions, then test with the actual activity. Continuous or simultaneous motion is valid when the activity needs it and attention remains understandable.
- Prevent avoidable displacement of content people are reading or controls they are using. When movement is intrinsic to the activity, provide the cues and controls people need.
- Honor reduced-motion and other applicable preferences. Preserve meaning and control when motion is reduced.
- Do not use motion as the only carrier of meaning.

### Words

- Use the owner's vocabulary consistently where the same thing or action is meant. Introduce another term only when it communicates a real distinction.
- Label actions and destinations so their result is understandable in context. Short or symbolic controls are valid when the platform convention and accessible name make the result clear.
- An error communicates what happened, what can happen next, and what was preserved when those facts apply. Do not invent assurances the system cannot support.
- Remove copy that does not help the activity, comprehension, trust, or accepted voice.
- Apply the recorded brand voice without weakening clarity or accessibility.

### The default is not a decision

- Trace consequential visual choices to the artifact, the project's styling contract, relevant platform evidence, or a recorded reason.
- Evaluate defaults against the product rather than rejecting or accepting them automatically. A default that fits remains a choice once its fit is examined and recorded where consequential.
- Use decoration and containers when they support identity, grouping, atmosphere, feedback, or comprehension.
- Review generated-interface habits as possible failure modes, not as a forbidden style list.

## Violations

- A layout or interaction pattern chosen because the framework prefers it rather than because it fits the activity.
- Supplied owner constraints or accepted design commitments silently dropped.
- Important actions or state changes indistinguishable in actual use.
- Density, motion, type, or layout varies arbitrarily across comparable contexts with no useful reason.
- Motion, color, sound, or position carries essential meaning alone.
- An error blames the person, exposes an internal code without useful guidance, or promises that data was kept when that was not verified.
- A visual default ships without being evaluated against the accepted direction and platform.

## Wrong vs Right

- WRONG: force every screen to one action even when the activity requires coordinated controls.
- RIGHT: identify the activity's actual action structure, establish hierarchy for it, and verify that people can act without confusion.
- WRONG: ban simultaneous animation because two moving elements are assumed to compete.
- RIGHT: test attention and control in the real activity, coordinate motion that serves it, and remove motion that obscures it.
- WRONG: apply one density everywhere because consistency was treated as sameness.
- RIGHT: keep comparable contexts coherent and record justified changes for different devices, roles, or activities.
- WRONG: preserve a platform default without examining fit, or replace it only to appear distinctive.
- RIGHT: compare the default with the accepted direction and use or change it for an explicit reason.

## What the framework cannot check

A script can verify declared files, references, tokens under a selected token policy, and concrete accessibility checks. It cannot establish that hierarchy, density, motion, wording, or aesthetics fit the activity. The design review examines those judgments against the artifact and observed interaction. A clean automated result is evidence for the checks it ran, not proof of good design.

## Research Notes

Dated notes: anything named in this section is an example from the time of writing and expires. Verify current evidence when the interface system or a materially different activity is designed.

- Research the medium's current interaction, motion, typography, localization, input, and accessibility practices relevant to this product.
- Start from supplied constraints, accepted direction, actual tasks, primary and committed contexts, session conditions, and existing patterns.
- Compare materially different viable compositions when identity or a recognized product pattern is still open; do not manufacture alternatives after the decision is settled.
- Test task completion, focus and input behavior, reflow or spatial adaptation, reduced motion, and the states that apply.
- Record consequential choices and the evidence that could cause them to be revisited.
