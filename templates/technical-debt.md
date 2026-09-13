# Technical Debt Log

Append-only log of known issues, shortcuts, and convention violations deferred rather than fixed immediately. Deferrals allowed by the operating profile (#30) are entries with `Kind: deferral` and a trigger. See `development/MAINTAIN.md` for when to review + prune.

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
- **Kind:** shortcut / deferral (a deferral is work the operating profile allows to wait; see #30)
- **Control:** the convention, backend rule, or floor item concerned (#N with the obligation named, BN, or floor: secrets / trust-boundary / irreversible-effects / personal-data / authorized-reuse / honest-completion). A floor item is never a deferral; name the obligation after the number ("#23 rate limiting") so a review can see that it is not one.
- **Due-before:** a named trigger from PROFILE.md (first-outside-participant, public-access, real-data, personal-data, real-money-or-external-action, operational-reliance, valuable-records, second-contributor, regulated-data-or-commitment, trial-stage, operational-stage) or a date YYYY-MM-DD, inclusive. Required when Kind is deferral.
- **Review-by:** YYYY-MM-DD. Required when Kind is deferral.
- **Closure-evidence:** what will prove it closed (a passing check, a file, a review). Required when Kind is deferral.
```

## Severity guidance

- **high** — production risk, compliance issue, data integrity risk, security concern. Fix within current or next cycle.
- **medium** — correctness issue or maintainability burden. Fix when touching the affected area OR within 1-2 cycles.
- **low** — cosmetic, consistency, or minor improvement. Fix opportunistically.

## Rules

- **Append-only during the log's lifetime.** Never edit past entries except to update `Status` or add notes in a `### Follow-up` subsection. An entry runs from its `## TD-` heading to the next `## TD-` heading; a level-two heading other than `## TD-` stays part of the entry, and only a level-one heading ends it, so anything written after the last entry that is not part of it (an audit history, notes) starts with a level-one heading.
- **Status transitions:** open → in-progress (when someone starts work) → fixed (when verified) OR won't-fix (with justification in a `Rationale` note).
- **Pruning:** remove `fixed` entries only during explicit maintenance cycles; keep them at least one cycle for history. Never remove `open` or `in-progress` entries.
- **Escalation:** entries in `open` status for more than N cycles (project-specific threshold, typically 3-6 months) either get severity bumped OR explicitly force-fixed. See `development/MAINTAIN-RED-FLAGS.md` #2 for why.
- **One entry per issue.** If an issue spans multiple locations, list them under `Where`; do not split into N entries.
- **Field labels are exact.** `Status`, `Kind`, `Control`, `Due-before`, `Review-by`, and `Closure-evidence` are read by `scripts/validate-profile.sh`; write each as a list item with the bold label and the value on the same line. Other labels are free, but must not contain one of those six words (`Control plane` would be read as a misspelled `Control` and fail).
- **Triggered deferrals block.** When the facts in PROFILE.md make a `Due-before` trigger true, every deferral due before it is blocking until fixed: `scripts/validate-profile.sh` fails, and renewing the date, relabeling the stage, or `won't-fix` does not clear it. Downgrading a stage needs a recorded reason and a review of the deferrals that survive it.

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
- **Kind:** shortcut
```

## Example deferral

```
## TD-012 — Rate limiting on the public endpoints deferred while the experiment is private

- **Logged:** 2026-04-20 by scaffold-agent
- **What:** No rate limiting on the two public endpoints; the app is an isolated experiment with no outside users.
- **Where:** src/api/ (both public routes)
- **Convention:** #23 (Application Security)
- **Severity:** medium
- **Proposed fix:** Add the shared rate-limit middleware per #23 and B3 before anyone outside the team can reach the app.
- **Status:** open
- **Related:** —
- **Kind:** deferral
- **Control:** #23 rate limiting on public endpoints
- **Due-before:** first-outside-participant
- **Review-by:** 2026-07-01
- **Closure-evidence:** the middleware-order test in the API layer passes with the limiter present
```

## Entries

(Start appending below. First entry gets TD-001; numbers are sequential.)
