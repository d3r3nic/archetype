# Scaffold Red Flags — Silent-Failure Patterns

Routed from `scaffolding/SCAFFOLD.md` and the shape-specific playbooks. These are the failure modes where an agent can produce a "scaffold complete" claim while leaving a system broken or absent. Read this before scaffolding; consult it during each step.

Silent-failure means no error, no warning, no build break — but the system is wrong. The autonomous outcome is incorrect. Human review may or may not catch it.

## 1. Skipped-by-interpretation (project-shape tag)

A step tagged `[backend]` or `[frontend]` or `[if applicable]` gets skipped by an agent that reads the tag as permission to skip rather than as a routing hint. Tag strength matters.

**Defense:** SCAFFOLD.md routes by project shape first (SCAFFOLD-BACKEND vs FRONTEND vs MOBILE vs PLATFORM). Within a shape-specific playbook, every step applies unless explicitly marked "skip if X" with X being a REFERENCES.md fact, not an agent judgment.

## 2. Checklist-only verification (no execution)

An agent ticks "Build passes / tests pass / typecheck passes" without actually running the commands. Visual-only compliance.

**Defense:**
- Each step has operational verification with a specific command and exit criterion, not "verify it works."
- `scripts/validate-scaffold.sh` runs at the end with machine-verifiable gates.
- The scaffold exit checklist requires command output, not boolean claims (see `VERSION-LOG.md` scaffold entry template).

## 3. Audit log conflated with app log

Regulated projects need TWO separate logging systems. An agent uses the app logger with a `type: "audit"` field and calls it done. Fails compliance (SOC 2 CC7.2, HIPAA audit controls) — different storage, retention, mutability, access controls required.

**Defense:**
- SCAFFOLD-BACKEND Step 5 is an explicit separate step from Step 4.
- Convention `B4` has a "Two distinct logging systems" callout at the top.
- Convention `#23` cross-references B4 for the distinction.
- validate-scaffold.sh checks for a dedicated audit-log path separate from the app logger.

## 4. Middleware pipeline in wrong order

Convention `B3` specifies an exact order. If middleware is built inline in multiple steps, the order is accidental. Wrong order → wrong behavior:
- Auth before CORS → preflight OPTIONS fails with 401.
- Rate-limit after auth → unauthenticated attacker burns rate-limit counters via failed auth attempts.
- Error handler not outermost → unhandled exceptions leak internal error details to clients.

**Defense:** SCAFFOLD-BACKEND Step 13 owns middleware pipeline explicitly with the exact order from B3.

## 5. Rate limiting and idempotency forgotten

Both are listed in feature-tree.md. Neither has historically had a dedicated SCAFFOLD step. Agents skip by omission.

**Defense:** SCAFFOLD-BACKEND has dedicated steps (10 idempotency, 11 rate limiting). Both named in validate-scaffold.sh expected-paths check.

## 6. Tenant isolation in schema but not queries (CRITICAL for multi-tenant B2B)

The Prisma/ORM schema has `org_id` columns. Agent marks "tenant isolation: done." But the query layer has no enforcement — features can write queries without `org_id` filters, reading across tenants. This is the #1 data-leak cause in B2B multi-tenant systems.

**Defense:** SCAFFOLD-BACKEND Step 8 explicitly distinguishes schema-level column existence from query-level enforcement. Must enforce at the query/repository layer via where-clause defaults, RLS policies, or a wrapper that rejects unfiltered queries. A multi-tenant test case verifies cross-tenant reads fail.

## 7. Env validation at runtime, not startup

`process.env.X` read ad-hoc across the code vs a `loadEnv()` function called once from `main()`. Ad-hoc reads mean a missing env var triggers an error mid-request, not at startup — production deploy succeeds, first user hits the error.

**Defense:** SCAFFOLD Step 1 (both shapes) mandates startup validation. validate-scaffold.sh greps for a startup-level env validation call.

## 8. Frontend step titles applied to backend (or vice versa)

Literal-minded agent generates `src/theme/tokens.ts` for a GraphQL-only backend because Step 2 says "Theme System." Or generates `src/controllers/users.ts` for a React SPA because Step 5 says "Database." Wrong-shape artifacts proliferate.

**Defense:** SCAFFOLD.md routes by project shape BEFORE any step lists. A backend agent reads SCAFFOLD-BACKEND which has no theme step. No cross-contamination.

## 9. GraphQL persisted queries forgotten

References.md says "persisted queries for mobile." Agent builds a standard GraphQL endpoint that accepts arbitrary queries. Mobile clients hit this with custom queries. Production attack surface: arbitrary query execution.

**Defense:** SCAFFOLD-BACKEND Step 12 GraphQL branch names persisted queries explicitly when mobile/public clients are in scope.

## 10. Migrations auto-run in CI/deploy

B1 is explicit: migrations are a separate gated step in production. But typical CI templates `prisma migrate deploy` on every push to main. A bad migration breaks production before anyone reviews it.

**Defense:** SCAFFOLD-BACKEND Step 17 CI step explicitly flags this. validate-scaffold.sh checks the CI workflow files for auto-migrate-on-deploy patterns.

## 11. Scaffold-complete without integration proof

Every system individually looks built. But nobody tried to USE them together. First real feature (Phase 3) hits `undefined is not a function` because the auth middleware and the GraphQL yoga plugin were never wired through the same request.

**Defense:** Every shape-specific playbook has a "Smoke-test feature" step at the end. A minimal feature that exercises every shared system. Integration test must pass. No scaffold-complete without the smoke test passing.

## 12. Implicit "skip if not regulated" treated as "skip because I don't want to build it"

Audit log, rate limiting, tenant isolation — agent rationalizes skipping because "this is just a scaffold, the project can add it later." References.md had the system listed. Skipping is NOT a decision the agent gets to make autonomously.

**Defense:** Handoff check (Step 0 of each shape playbook) requires reading References.md Foundational Systems list and inventorying every system against the playbook before building. Missed systems surfaced at inventory time, not after the scaffold claims complete.

## 13. Package versions pinned with expirable specifics

Agent pins SDK versions based on training-data knowledge. Versions are stale by scaffold time. First `install` either fails or installs deprecated packages.

**Defense:** Every convention's Research Notes says "research current tooling for the chosen language." Agent resolves package versions at scaffold time, not from memory. validate-scaffold.sh can grep for obviously-stale version strings but is best-effort here — the real defense is the research-at-scaffold rule.

---

## Handling a fired red flag

If one of these fires during or after scaffolding:
1. STOP. Do not continue to the next step until resolved.
2. Document the red flag in `VERSION-LOG.md` scaffold entry.
3. Fix the underlying issue (do not paper over with a `// TODO` comment).
4. Re-run `scripts/validate-scaffold.sh`.
5. Only then proceed.

Silent failure is worse than loud failure. A loud failure blocks the merge; a silent failure ships to production.
