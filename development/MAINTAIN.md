# Phase 4: Maintain

Audit, update, and evolve the project. Runs for the life of the project, on specific triggers.

Phase 4 has three distinct modes, each with its own trigger. Don't conflate them.

## Mode 1 — Routine audit (scheduled)

**When:** after every N commits (project-specific threshold, typically 50-100), OR every 2-4 calendar weeks, OR before any `update.sh` pull from the framework.

**What to audit:**
- Feature tree accuracy (code vs `feature-tree.md` match)
- Doc freshness (`docs/features/*.md`, `docs/systems/*.md`, `References.md` vs current code)
- Convention violations in features/
- Tech-debt log pruning (entries to escalate, fix, or close)
- Framework version currency (run `./archetype/update.sh` status)

**How:**
1. Run the automated gates first — `scripts/validate-develop.sh` + `scripts/validate-maintain.sh` + `scripts/validate-framework.sh`.
2. For anything they don't catch (judgment calls, doc narrative drift, architecture fit), manually audit per the checklist below.
3. Log findings in `TECHNICAL-DEBT.md` using `templates/technical-debt.md` format.
4. Append a row to `feature-tree.md` § Audit Log with date, scope, findings count, and pointer to the tech-debt entries.

**Audit checklist:**
- [ ] `scripts/validate-develop.sh` — 0 errors
- [ ] `scripts/validate-maintain.sh` — 0 errors
- [ ] `scripts/validate-framework.sh` — 0 errors (framework itself OK)
- [ ] `npm test` / equivalent — all green
- [ ] Every feature directory has matching `feature-tree.md` row and `docs/features/{name}.md` entry (names align)
- [ ] Every doc's referenced types still exist in source
- [ ] Convention Overrides in `References.md` still apply
- [ ] Critical Lessons in `References.md` still apply
- [ ] Tech-debt entries older than threshold: escalated OR force-fixed OR explicitly continue-deferred with fresh reason

## Mode 2 — Incident response (event-triggered)

**When:** after a failed deploy, flaky test suite, production bug traced to a convention violation, or any session where something went notably wrong.

**What to do:**
1. Open `templates/session-review.md` and fill it out. Save to `docs/reviews/YYYY-MM-DD-topic.md`.
2. Identify whether the root cause is project-local (fix in project + log in tech-debt) or framework-wide (fix in framework + promote to a framework issue).
3. If project-local: log as a tech-debt entry with appropriate severity; plan fix for current or next cycle.
4. If framework-wide: open an issue in the framework repo referencing the session review. The next framework step incorporates it. Loop closes when `update.sh` pulls the fix and a follow-up session review confirms.

**Never:** silently fix a framework drift in-project without also reporting it to the framework. That's the "convention evolution never promoted" silent-failure pattern (see `development/MAINTAIN-RED-FLAGS.md` #3).

## Mode 3 — Convention evolution (signal-triggered)

**When:** when accumulated session reviews surface a recurring pattern (3+ reviews name the same gap), OR when a session review explicitly proposes a convention edit.

**What to do:**
1. Review the accumulated session reviews — look for repeated "Suggested Convention Improvements."
2. If a pattern is clear, draft the framework change:
   - Is it a new convention? Expand Conventions.md index + write a convention doc.
   - Is it a change to an existing convention? Edit the convention doc.
   - Is it a RED-FLAGS.md entry? Add to the appropriate phase's RED-FLAGS doc.
   - Is it a validator check? Update the relevant `scripts/validate-*.sh`.
3. Factory first, per the framework's meta-rule: PLAN.md + CHANGELOG.md entry → dist/ changes → deploy via update.sh.
4. Close the loop: run a follow-up session review after the framework change lands to confirm the pattern is addressed.

## Tech-debt pruning policy

Applied during Mode 1 audits. Per entry in `open` status:

- Age < threshold: leave alone unless severity changed.
- Age ≥ threshold AND no severity change since logged: ESCALATE severity one tier OR force-fix OR mark `won't-fix` with rationale. Do not silently re-leave at the same state — that's the "tech-debt log grows forever" silent-failure pattern (see MAINTAIN-RED-FLAGS.md #2).
- Age ≥ 2× threshold: MUST be force-fixed or marked `won't-fix`. No more deferral.

Threshold is project-specific — 180 days is a reasonable default for mid-velocity projects. `scripts/validate-maintain.sh` flags stale entries.

## Documentation Maintenance

What the agent is accountable for (no hooks rely on this):

- After a feature's code changes, update `docs/features/{name}.md` if behavior, API shape, errors, or key decisions changed.
- After a shared system's code changes, update `docs/systems/{name}.md`.
- After any top-level structural change (new folder, new conventions override, new protocol), update `References.md § Folder Structure`.
- `feature-tree.md` rows stay accurate — `systems used` column reflects the actual imports, `routes` column reflects the real routes, `status` column reflects reality.

The `post-task-verify.sh` hook (if installed) reminds to update docs after a task — but it's advisory. The validator gates (`validate-develop.sh` group 4) check that docs exist but do NOT check content freshness beyond coarse type-reference presence (see `validate-maintain.sh` group 5). Content drift is on the agent + human review.

## Convention Evolution signal-collection

During the life of the project, session reviews accumulate in `docs/reviews/`. Quarterly (or at the project's audit cadence), scan the `## Suggested Convention Improvements` section across all recent reviews. Count repeat themes. Any theme appearing in 3+ reviews is a promotion candidate (Mode 3).

If the project is team-sized, maintain a `docs/convention-evolution-log.md` that aggregates these signals. Solo projects can skip this — the `grep Suggested Convention Improvements docs/reviews/*.md` one-liner does the job.

## Framework Self-Test

Run `./archetype/scripts/validate-framework.sh` before pulling framework updates via `update.sh`. Catches framework-internal drift (file paths broken, convention count out of sync with actual files, etc.). If this fails, either the framework was pulled mid-edit or a local modification was made that violates the framework's own consistency rules.

Run `./archetype/scripts/validate-maintain.sh` during Mode 1 routine audits. Catches Phase 4 artifacts drift (missing tech-debt log, missing audit log entry, feature-directory-name drift, stale open entries).

Run `./archetype/scripts/validate-develop.sh` during Mode 1 and before every commit. Catches Phase 3 feature-code drift.

Run `./archetype/scripts/validate-scaffold.sh` only if you added or materially changed foundational systems post-scaffold.

## Final gate for Mode 1 audit

Before closing an audit cycle, verify:
- All 4 validators (framework, develop, maintain, scaffold-as-needed) exit 0.
- `feature-tree.md` § Audit Log has a new row for this cycle.
- Any new tech-debt entries are logged with severity + proposed fix.
- Any escalated or closed tech-debt entries have updated Status.
- If the cycle found framework drift: framework issue opened (not just logged in-project).

The audit is NOT complete until these all pass. Don't leave a cycle half-done — that's the "audit done once then forgotten" silent-failure pattern.
