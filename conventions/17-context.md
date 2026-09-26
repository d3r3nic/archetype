# Convention #17: Context Management

## Applies when

Every session in which an AI works on the project. Code structure is #1; this convention is about how a session keeps and restores what it needs to know.

## Principle

The project's records, not a conversation's memory, carry what the next session needs. A session works on one scope at a time, reads what its step or task routes it to, and leaves what it learned where the next session will find it. When attempts keep failing, the session stops and re-examines the approach from the evidence instead of retrying variations.

## Rules

- Work on one scope at a time. Unrelated work gets its own session, or at least its own plan and records.
- Restore context from the project's records: References.md, PROFILE.md, the ledger, the decision location, feature records and the implementer plan. Do not rely on what an earlier conversation said.
- Read what the current step or task routes to (development/STEPS.md, Conventions.md). Reading everything up front is reading that is gone by the time it is needed.
- Before a session ends or its context is reset, write down what the next session needs: decisions, open questions, the next action.
- When the same problem survives repeated attempts, stop. Re-read the evidence, question the approach, and start again from what was learned, in a fresh session if the current one is crowded with failed attempts.
- In documents written for AI readers, put what matters most first.

## Violations

- A decision or finding that exists only in a past conversation.
- Several unrelated tasks tangled in one session and one record.
- Retrying small variations of a failing approach without re-examining it.
- Reading the whole framework before the first step.

## Wrong vs Right

- WRONG: a new session asks the owner again for facts an earlier session already learned. RIGHT: the earlier session recorded them, and the new one reads them.
- WRONG: after two failed fixes, a third variation of the same idea. RIGHT: stop, re-read the evidence, find what the first two missed, and record it.
- WRONG: one session fixes a defect, adds a feature and refactors something unrelated, with one summary for all three. RIGHT: each scope gets its own plan, checks and record.

## Research Notes

Research how the AI host in use stores instructions, restores sessions and limits context, and which of its features help a session restore from the project's records. Record any project-specific practice in CLAUDE.md.additions or References.md.
