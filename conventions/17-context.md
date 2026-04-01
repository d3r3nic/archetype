# Convention #17: Context Management

## Principle

AI performance degrades as context fills. Code structure, file size, and session management directly affect AI output quality. Critical information goes at the start and end of documents (lost-in-the-middle effect). Sessions are scoped to one task. Context is cleared between unrelated work.

AI-era reasoning: models claiming 200K tokens become unreliable around 130K. Performance drops 30%+ when relevant information is in the middle of context. Code organization optimized for context windows produces measurably better AI output.

## Rules

- Keep files under 300 lines. Split when they grow beyond this.
- One responsibility per file. AI loads exactly what it needs.
- Colocate related code. Minimize the number of files AI needs to read for one task.
- Place critical instructions at the start and end of documents, not the middle.
- /clear between unrelated tasks. Never mix work in one session.
- Start fresh after 2 failed corrections. Context is polluted with failed approaches.
- Use scoped instruction files (subdirectory CLAUDE.md) for feature-specific context.
- Compact proactively during long sessions (every 25-30 minutes).

## Violations

- 800-line files mixing multiple concerns
- Session with 5 unrelated tasks without clearing
- Correcting the same issue 4 times instead of starting fresh
- Critical rules buried in the middle of a long instruction file

## References.md Section

- Not applicable. This convention governs how AI sessions are managed, not project structure.
