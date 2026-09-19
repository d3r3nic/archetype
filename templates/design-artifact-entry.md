# {Screen or flow name}

One entry per screen or flow in the design artifact (#27). Under `repository-first` this file lives with the specifications; under `workspace-first` the same fields sit beside the artboard. A session that designs a gap writes this entry in the same change as the code (#27 "The session").

- Purpose: [one sentence: what a person came here to do (#31)]
- Primary action: [the one action the screen leads to; none for a read-only screen]
- Decided by: [owner pick / owner-delegated / session-decided], [date], [artifact revision or decision record]
- Reading order: [what the eye lands on first, second, third]
- Components: [cataloged components used (#22); a component the catalog lacks is named here as a wrapper to add]
- Words: [the vocabulary terms this screen uses (#31); the primary action's label]
- Contexts: [the committed contexts this screen is composed for, and what changes between them (#6)]

## States

Only the states that apply to this screen, from the state list in #27. For each: what it tells the person.

| State | What happened | What they can do | What was kept |
|---|---|---|---|
| [empty] | [nothing here yet: what this will hold] | [the one action to start] | [n/a] |
| [error] | [what failed, in plain words] | [retry / fix / go back] | [what they typed is still there] |

States that do not apply, and why: [each state of the #27 list left out of the table, other than disabled and overflow, which are designed on the component, with its reason: "offline: the screen is server-rendered and never opens without a connection"; none left unexplained]

## Captures

[this screen's folder under the `Captures` line of References.md; one per applicable state per scheme per committed context (#27 "Design review")]
