# {Screen or flow name}

One entry per screen or flow in the design artifact (#27). Under `repository-first` this file lives with the specifications; under `workspace-first` the same fields sit beside the artboard. A session that designs a gap writes this entry in the same change as the code (#27 "The session").

- Purpose: [one sentence: what a person came here to do (#31)]
- Primary action: [the action hierarchy that fits this purpose and context; one action, several concurrent actions, or none, with the reason]
- Decided by: [owner pick / owner-delegated / session-decided], [date], [artifact revision or decision record]
- Decision basis: [DEC-NNN IDs for the current direction and committed contexts/schemes, from the one decision location]
- Reading order: [how attention and reading should move through the information and controls]
- Components: [native elements, direct library use, adapters, wrappers, or project-owned components selected under #22; record any missing pattern that needs a decision]
- Words: [the vocabulary terms this screen uses (#31); labels for its actions and destinations]
- Contexts: [the committed contexts this screen is composed for, and what changes between them (#6)]

## States

Only the states that apply to this screen, from the state list in #27. For each: what it tells the person.

| State | What happened | What they can do | What was kept |
|---|---|---|---|
| [empty] | [nothing here yet: what this will hold] | [an appropriate way to begin] | [n/a] |
| [error] | [what failed, in plain words] | [retry / fix / go back] | [what they typed is still there] |

States that do not apply, and why: [each state of the #27 list left out of the table, with its reason: "offline: the screen is server-rendered and never opens without a connection"; disabled and overflow may live in component or interaction-pattern evidence unless they change this screen; none left unexplained]

## Captures

[this screen's folder under the `Captures` line of References.md; one per applicable state per scheme per committed context (#27 "Design review"); disabled and overflow may use the project's component or interaction-pattern evidence surface unless they change screen composition]

A changed decision basis makes the dependent entry and its review due for revalidation (development/STEPS.md). Preserve the previous decision and review in version history; refresh the current capture set only after the new basis is implemented.
