# Design review: {screen or flow}

Copy this file per screen review (for example into `docs/reviews/design/`), or keep the checks inside the feature record. What the review covers is convention #27 "Design review"; the checks read #31. The reviewer did not build the screen (#29).

- Reviewer: [name]
- Date: [date]
- Artifact entry and revision: [entry, revision]
- Decision basis: [the same current DEC-NNN IDs as the artifact entry]
- Code revision: [the revision reviewed; record changed inputs when work is uncommitted]
- Purpose sentence (from the artifact): [one sentence: what a person came here to do]
- Session-decided entries covered: [list, or none]

## Checks

1. Purpose: can a person do what the purpose sentence says, without help? [finding]
2. Hierarchy: the action hierarchy fits the purpose, context, and actual activity; the reading and attention order leads to the relevant actions (#31). [finding]
3. States: every applicable state present and telling what happened, what to do, and what was kept (the state list in #27); every state the entry records as not applying has a reason that holds. [finding]
4. Words: the vocabulary, outcome verbs for actions and vocabulary names for destinations, errors that say what happened and what to do (#31). [finding]
5. System fidelity: the selected styling and interface contracts are followed, accepted artifact values remain traceable, and mockup values or controls were not copied without provenance (#6, #22). [finding]
6. Accessibility floor: focus visible on every surface, keyboard reaches everything, contrast per scheme, targets, reflow at the target's zoom level, reduced motion (#14). [finding]
7. Each committed scheme and context the change affects, with its captures. [finding]
8. Aesthetics, last: the tells of a generated interface (#31 "The default is not a decision"). [finding]

## Interaction evidence

Record the observed task completion, keyboard order, visible focus and focus return, reduced-motion behavior, and reflow, with the command or interaction performed and its result. A still capture proves none of these behaviors by itself. Name justified non-applicability.

## Captures

Captures of the states the change affects, in the schemes and contexts they affect, from the recorded `capture:` command. The capture set uses the decision basis, artifact revision and code revision above. Revalidate it after any of these inputs change. Component-only states stay with the project's recorded component or interaction-pattern evidence unless they change screen composition. Open every capture and write what it shows: a blank frame, the wrong language, or the wrong state is a finding, not evidence.

| State | Scheme | Context | Capture | Shows |
|---|---|---|---|---|
| [empty] | [light] | [desk] | [path or link] | [what the reviewer saw, in a few words] |
| [loading] | [dark] | [phone] | [path or link] | [what the reviewer saw, in a few words] |

## Done

- [ ] The checks pass with evidence, and the Shows column is filled for every capture.
- [ ] The artifact entry, the code, and the captures agree on the current decision basis.
- [ ] Interaction findings are backed by observations or test results.
- [ ] A decision the review changed is recorded at the decision location with its reason.
