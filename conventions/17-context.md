# Convention #17: Context Management

## Principle

AI performance degrades as context fills. Code structure, file size, and session management directly affect AI output quality. Critical information goes at the start and end of documents (the middle gets lost). Sessions are scoped to one task. Context is cleared between unrelated work. This convention governs how AI sessions are managed, not how code is structured (that's convention #1).

## Rules

- Keep files under 300 lines. Split when they grow beyond this. Small files load fully into AI context.
- One responsibility per file. AI loads exactly what it needs for the task at hand.
- Colocate related code. Minimize the number of files AI needs to read to understand one feature.
- Place critical instructions and important information at the start and end of documents, not in the middle. AI models lose accuracy on information buried in the middle of long context.
- Clear context between unrelated tasks. Never mix unrelated work in one AI session.
- Start fresh after two failed corrections on the same issue. If the AI fails twice and you correct it twice, the context is now polluted with failed approaches. Start a new session with a better initial prompt incorporating what you learned.
- Use scoped instruction files for feature-specific context. A feature can have its own instruction file with context relevant only to that feature, keeping the main instruction file lean.
- Compact context proactively during long sessions (every 25-30 minutes). Don't wait until the context window is full.

## Violations

- Files with 800+ lines mixing multiple concerns
- An AI session with 5 unrelated tasks without clearing context between them
- Correcting the same issue 4 times instead of starting fresh (context pollution)
- Critical rules or constraints buried in the middle of a long document
- Loading entire large files when only a specific section is needed

## Wrong vs Right

- WRONG: one AI session that starts with fixing a bug, then adds a feature, then refactors something unrelated, then reviews code. The context is full of mixed concerns. Quality degrades on every subsequent task.
- RIGHT: fix the bug, clear context. Add the feature, clear context. Each task gets fresh context and full attention.
- WRONG: the AI makes a mistake. You correct it. It makes the same mistake differently. You correct again. It tries a third approach, still wrong. The context now has three failed attempts polluting every future response.
- RIGHT: the AI makes a mistake. You correct it. It makes the same mistake differently. You start a fresh session with a better prompt that incorporates what you learned from the first attempt. Fresh context, better result.
- WRONG: a 1000-line convention document where the most critical rule is on line 500. The AI reads the whole document but the rule in the middle gets the least attention.
- RIGHT: the most critical rules are at the top and bottom. The middle contains supporting detail that's less critical.

## Research Notes

This convention is about AI session management, not framework-specific implementation. No framework research needed. Apply these principles to every AI-assisted development session regardless of framework.
