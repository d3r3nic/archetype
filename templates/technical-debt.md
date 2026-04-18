# Technical Debt Log

Append-only log of known issues, shortcuts, and convention violations deferred rather than fixed immediately. See `development/MAINTAIN.md` for when to review + prune.

## Entry format

```
## TD-{N} — {one-line title}

- **Logged:** YYYY-MM-DD by {author or agent}
- **What:** one-sentence description of the issue
- **Where:** file path(s) and line range if specific
- **Convention:** which convention(s) this violates (#N, BN, or "none — general debt")
- **Severity:** high / medium / low
- **Proposed fix:** one-sentence recommended resolution
- **Status:** open / in-progress / fixed / won't-fix
- **Related:** links to other TD entries, feature docs, or session reviews if applicable
```

## Severity guidance

- **high** — production risk, compliance issue, data integrity risk, security concern. Fix within current or next cycle.
- **medium** — correctness issue or maintainability burden. Fix when touching the affected area OR within 1-2 cycles.
- **low** — cosmetic, consistency, or minor improvement. Fix opportunistically.

## Rules

- **Append-only during the log's lifetime.** Never edit past entries except to update `Status` or add notes in a `Follow-up` subsection.
- **Status transitions:** open → in-progress (when someone starts work) → fixed (when verified) OR won't-fix (with justification in a `Rationale` note).
- **Pruning:** remove `fixed` entries only during explicit maintenance cycles; keep them at least one cycle for history. Never remove `open` or `in-progress` entries.
- **Escalation:** entries in `open` status for more than N cycles (project-specific threshold, typically 3-6 months) either get severity bumped OR explicitly force-fixed. See `development/MAINTAIN-RED-FLAGS.md` #2 for why.
- **One entry per issue.** If an issue spans multiple locations, list them under `Where`; do not split into N entries.

## Example entry

```
## TD-007 — Test-env bootstrap boilerplate duplicated across test files

- **Logged:** 2026-04-17 by phase-4-agent
- **What:** Every *.test.ts file repeats the same `beforeAll` + env setup + `afterAll` cleanup pattern.
- **Where:** src/features/*/test files (3 files currently).
- **Convention:** #0 (Reusability) — violates "built once, configured for context."
- **Severity:** medium
- **Proposed fix:** Extract into `src/shared/test-utils/` with `buildTestApp()` and `cleanupTestApp()` helpers. Each test file becomes a single import + two hooks.
- **Status:** open
- **Related:** —
```

## Entries

(Start appending below. First entry gets TD-001; numbers are sequential.)
