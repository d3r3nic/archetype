# Maintain Red Flags — Phase 4 Silent-Failure Patterns

Routed from `development/MAINTAIN.md`. Parallels `bootstrap/RED-FLAGS.md`, `scaffolding/RED-FLAGS.md`, and `development/RED-FLAGS.md`. These are failure modes where audits claim "all clean" while drift accumulates invisibly.

Silent-failure in Phase 4 looks different from Phases 1-3: there's no failing test or broken build to surface the problem. The project keeps working; the debt compounds; future features built on drifted state inherit the rot.

## 1. Audit done once then forgotten

MAINTAIN.md says "run every 2-4 weeks." No hook, no CI check, no trigger event. An agent runs the audit once, logs findings, moves on. Three months later nobody has looked again. Tech-debt log is stale; feature-tree has drifted; doc freshness has drifted; no one has noticed.

**Defense:** MAINTAIN.md now has explicit triggers beyond calendar:
- After every N commits (N defined at scaffold time per project pace).
- Before any `update.sh` pull from the framework (audit current state before adopting changes).
- After any failed deploy / flaky test / convention violation surfaced in development.
- Before any feature-tree or References.md edit that touches an existing row.
- `scripts/validate-maintain.sh` runs the machine-verifiable subset on demand; human audit runs the judgment-requiring subset.

## 2. Tech-debt log grows forever without pruning or escalation

Entries accumulate. None escalate to `high`. None get force-fixed. None get `won't-fix` with justification. The log becomes a graveyard of someday-maybes.

**Defense:** `templates/technical-debt.md` prescribes a pruning rule: entries in `open` status for more than N cycles either bump severity or force-fix. `validate-maintain.sh` flags entries older than the project's threshold without a severity change or status transition. MAINTAIN.md pruning checklist: every audit cycle, review every `open` entry; either escalate, force-fix, or note continued deferral with a fresh reason.

## 3. Convention evolution captured in a session review but never promoted

Session reviews document a finding ("we keep hitting this pattern — convention should cover it"). Nobody reads the review later. The finding dies in `docs/reviews/YYYY-MM-DD-topic.md`. Next project hits the same pattern. Framework learns nothing.

**Defense:** MAINTAIN.md explicit "Convention evolution" section:
- After every session review, check the "Suggested Convention Improvements" section.
- If any item is marked for framework promotion: open an issue in the framework repo (not just the project repo). Include a link to the session review.
- Framework maintainer (or agent running framework audit) aggregates issues across projects into the next step's scope.
- Loop closes when framework edit lands → project pulls via `update.sh` → next session review confirms the finding is addressed.

The feedback loop is the whole point. A session review with no promotion path is just a journal.

## 4. Doc freshness drift accumulates invisibly

MAINTAIN.md used to say "hooks handle this automatically." The shipped hooks (`pre-destructive-warn.sh`, `post-task-verify.sh`) do NOT check doc freshness. The defense was name-only.

Real pattern: a feature's code changes, its `docs/features/{name}.md` does not. Both "work." Future agent reads the doc, writes client code against the documented shape, hits the actual shape at runtime.

**Defense:**
- `validate-develop.sh` already catches the coarse case (feature missing doc entirely). Phase 4 catches drift between existing doc and code.
- `validate-maintain.sh` check: for every `docs/features/*.md`, grep for schema type names referenced in the doc, verify those names still exist in the feature's source. If a referenced type is gone, the doc is stale.
- Doc freshness is a manual audit for content beyond type names (narrative, key decisions) — catalog this in the audit checklist.

## 5. Two audits disagreeing on the same repo

This fired during the first Phase 4 agent run. The inline bash script in MAINTAIN.md and the separate `validate-develop.sh` checked overlapping concerns with different logic. They produced different answers. An agent relying on one sees "clean"; the other sees "broken." Neither is trustworthy when the other contradicts.

**Defense:** MAINTAIN.md NO LONGER contains an inline audit script. Routes to `scripts/validate-maintain.sh` + `scripts/validate-develop.sh` as the single source of audit truth. Two audits must never overlap with different logic. Shared logic lives in one validator, consumed by both phases.

---

## Handling a fired red flag

Same as the other RED-FLAGS docs:
1. STOP. Log the finding in TECHNICAL-DEBT.md if not already there.
2. Fix at the source (not at the audit level — don't change the audit to silence the finding unless the audit itself is wrong).
3. Re-run the relevant validator to confirm clean.
4. If the pattern is repeatable across projects, add it to the session review's "Suggested Convention Improvements" for framework promotion (see #3 above).
