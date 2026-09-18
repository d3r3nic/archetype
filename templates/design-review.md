# Design review: {screen or flow}

Copy this file per screen review (for example into `docs/reviews/design/`), or keep the checks inside the feature doc's Design line. The order is convention #27 "Design review"; the checks read #31. The reviewer did not build the screen (#29).

- Reviewer: [name]
- Date: [date]
- Artifact entry and revision: [entry, revision]
- Purpose sentence (from the artifact): [one sentence: what a person came here to do]
- Session-decided entries covered: [list, or none]

## Checks, in order

1. Purpose: can a person do what the purpose sentence says, without help? [finding]
2. Hierarchy: one primary action; the reading order leads to it (#31). [finding]
3. States: every applicable state present and telling what happened, what to do, and what was kept (the state list in #27); every state the entry records as not applying has a reason that holds. [finding]
4. Words: the vocabulary, verbs that name outcomes, errors that say what happened and what to do (#31). [finding]
5. System fidelity: tokens only, cataloged components only, no literal value copied from a mockup (#6, #22). [finding]
6. Accessibility floor: focus visible on every surface, keyboard reaches everything, contrast per scheme, targets, reflow at the target's zoom level, reduced motion (#14). [finding]
7. Every committed scheme and every committed context, each with its own captures. [finding]
8. Aesthetics, last: the tells of a generated interface (#31 "The default is not a design"). [finding]

## Captures

One capture per applicable state per scheme per committed context. An applicable state without a capture is not done. Open every capture and write what it shows: a blank frame, the wrong language, or the wrong state is a finding, not evidence.

| State | Scheme | Context | Capture | Shows |
|---|---|---|---|---|
| [empty] | [light] | [desk] | [path or link] | [what the reviewer saw, in a few words] |
| [loading] | [dark] | [phone] | [path or link] | [what the reviewer saw, in a few words] |

## Done

- [ ] The eight checks pass with evidence, and the Shows column is filled for every capture.
- [ ] The artifact entry, the code, and the captures agree.
- [ ] A decision the review changed is recorded at the decision location with its reason.
