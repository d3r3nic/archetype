# Scaffold Red Flags — Silent-Failure Patterns

Routed from `scaffolding/SCAFFOLD.md` and the shape-specific playbooks. These are the failure modes where an agent can produce a "scaffold complete" claim while leaving a system broken or absent. Read this before scaffolding; consult it during each step.

Silent-failure means no error, no warning, no build break — but the system is wrong. The autonomous outcome is incorrect. Human review may or may not catch it.

## 1. Skipped-by-interpretation (project-shape tag)

A step tagged `[backend]` or `[frontend]` or `[if applicable]` gets skipped by an agent that reads the tag as permission to skip rather than as a routing hint. Tag strength matters.

**Defense:** SCAFFOLD.md routes by project shape first (SCAFFOLD-BACKEND vs FRONTEND vs MOBILE vs PLATFORM). Within a shape-specific playbook a step is skipped by its listed condition, a fact the project records, or set aside with the reason when it does not fit how this application works (development/STEPS.md). Never silently: an unrecorded skip is the failure this entry names.

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
- validate-scaffold.sh checks for a dedicated audit log, separate from the app logger and not an in-memory-only store, wherever the unit handles regulated data (PROFILE.md, or the unit's References.md), at the location References.md § Compliance records on its Audit log line.

## 4. Middleware pipeline in wrong order

Convention `B3` specifies an exact order. If middleware is built inline in multiple steps, the order is accidental. Wrong order → wrong behavior:
- Auth before CORS → preflight OPTIONS fails with 401.
- Rate-limit after auth → unauthenticated attacker burns rate-limit counters via failed auth attempts.
- Error handler not outermost → unhandled exceptions leak internal error details to clients.

**Defense:** SCAFFOLD-BACKEND Step 13 owns middleware pipeline explicitly with the exact order from B3.

## 5. Rate limiting and idempotency forgotten

Both are listed in feature-tree.md. Neither has historically had a dedicated SCAFFOLD step. Agents skip by omission.

**Defense:** SCAFFOLD-BACKEND has dedicated steps (Step 10 idempotency, Step 11 rate limiting), each with its own verify line. validate-scaffold.sh checks neither system, so the defense is the dedicated step plus the Step 0 handoff check, which inventories every system listed in References.md against the playbook's steps.

## 6. Tenant isolation in schema but not queries (CRITICAL for multi-tenant B2B)

The ORM schema has `org_id` columns. Agent marks "tenant isolation: done." But the query layer has no enforcement — features can write queries without `org_id` filters, reading across tenants. This is the #1 data-leak cause in B2B multi-tenant systems.

**Defense:** SCAFFOLD-BACKEND Step 8 explicitly distinguishes schema-level column existence from query-level enforcement. Must enforce at the query/repository layer via where-clause defaults, RLS policies, or a wrapper that rejects unfiltered queries. A multi-tenant test case verifies cross-tenant reads fail.

## 7. Env validation at runtime, not startup

`process.env.X` read ad-hoc across the code vs a `loadEnv()` function called once from `main()`. Ad-hoc reads mean a missing env var triggers an error mid-request, not at startup — production deploy succeeds, first user hits the error.

**Defense:** SCAFFOLD Step 1 (both shapes) mandates startup validation. validate-scaffold.sh looks for a dedicated env-validation module or a named validation function in source; that the call sits at startup is the step's own verify line (delete a required env var, the process must fail to start).

## 8. Frontend step titles applied to backend (or vice versa)

Literal-minded agent generates `src/theme/tokens.ts` for a GraphQL-only backend because Step 2 says "Theme System." Or generates `src/controllers/users.ts` for a browser-only SPA because Step 5 says "Database." Wrong-shape artifacts proliferate.

**Defense:** SCAFFOLD.md routes by project shape BEFORE any step lists. A backend agent reads SCAFFOLD-BACKEND which has no theme step. No cross-contamination.

## 9. GraphQL persisted queries forgotten

References.md says "persisted queries for mobile." Agent builds a standard GraphQL endpoint that accepts arbitrary queries. Mobile clients hit this with custom queries. Production attack surface: arbitrary query execution.

**Defense:** SCAFFOLD-BACKEND Step 12 GraphQL branch names persisted queries explicitly when mobile/public clients are in scope.

## 10. Migrations auto-run in CI/deploy

B1 is explicit: migrations are a separate gated step in production. But typical CI templates run the migration-deploy command on every push to main. A bad migration breaks production before anyone reviews it.

**Defense:** SCAFFOLD-BACKEND Step 17 CI step explicitly flags this. validate-scaffold.sh checks the CI workflow files for auto-migrate-on-deploy patterns.

## 11. Scaffold-complete without integration proof

Every system individually looks built. But nobody tried to USE them together. First real feature (Phase 3) hits `undefined is not a function` because the auth middleware and the GraphQL server plugin were never wired through the same request.

**Defense:** Every shape-specific playbook has a "Smoke-test feature" step at the end. A minimal feature that exercises every shared system. Integration test must pass. No scaffold-complete without the smoke test passing.

## 12. Implicit "skip if not regulated" treated as "skip because I don't want to build it"

Audit log, rate limiting, tenant isolation: the agent rationalizes skipping because "this is just a scaffold, the project can add it later." References.md had the system listed. A system the project's facts require is built; one the operating stage lets wait is a recorded deferral (#30); one that does not fit is set aside with its reason. "Later" with no record is the failure, and the #30 floor is never postponed.

**Defense:** Handoff check (Step 0 of each shape playbook) requires reading References.md Foundational Systems list and inventorying every system against the playbook before building. Missed systems surfaced at inventory time, not after the scaffold claims complete.

## 13. Package versions pinned with expirable specifics

Agent pins SDK versions based on training-data knowledge. Versions are stale by scaffold time. First `install` either fails or installs deprecated packages.

**Defense:** Every convention's Research Notes says "research current tooling for the chosen language." Agent resolves package versions at scaffold time, not from memory. validate-scaffold.sh does not inspect version strings at all: the whole defense rests on the research-at-scaffold rule plus each step's install-and-verify gate, which fails loudly on a bad pin.

## 14. Provider composition order (frontend/mobile)

Frontend/mobile apps mount multiple providers at the root (ErrorBoundary, server-state provider, Theme, Auth, Router, Store). Wrong order silently breaks behavior: no error, no warning, just subtly wrong runtime:
- Router mounted ABOVE AuthProvider → route guards calling `useAuth()` read undefined context; all guards silently pass.
- server-state provider mounted BELOW a component that uses `useQuery` → "No server-state provider set" errors at runtime, not catchable by typecheck.
- ThemeProvider mounted BELOW a component that reads theme tokens → FOUC or undefined tokens.

**Defense:** SCAFFOLD-FRONTEND Step 8 specifies the composition order explicitly (ErrorBoundary → server-state providerProvider → ThemeProvider → AuthProvider → Router). Integration tests with the custom render wrapper catch regressions (the wrapper must match the production order).

## 15. Route guards forgotten on protected routes

Developer adds a new route that should require auth but forgets to wrap it in `<RequireAuth>` or equivalent. No error, no warning — the unauthenticated user sees the page, data may leak, privileged actions may succeed.

**Defense:** SCAFFOLD-FRONTEND Step 8 demands the pattern: every route definition explicitly declares `public: true` or wraps the element in a guard. A lint rule or a custom check can flag routes without an explicit auth decision. Integration tests for protected features MUST include a 401-when-unauthenticated test.

## 16. Env-inlining breaks runtime env mutation in tests

Mobile-specific, but applicable to any project whose bundler or transpiler substitutes public env variables at build time: the transform rewrites every read of the public env prefix to a LITERAL VALUE at transform time. A test that assigns to that variable at runtime has NO effect — the module was compiled with the value present when the test environment loaded. Tests silently run against the wrong config and pass spuriously.

**Defense:** Bracket-notation access or an explicit runtime lookup for values that must be mutable in tests. Document which env vars are build-time (inlined) vs runtime (mutable) in References.md § Commands / Environment. SCAFFOLD-MOBILE Step M6 and SCAFFOLD-FRONTEND Step 10 call this out in the testing context.

## 17. Class prototype broken on transpiled Error subclasses

When a TypeScript project's output target is ES5 or lower (common on mobile when the transpiler targets an older device JS engine, and on older browsers), the transpiler emits `_this = _super.call(this) || this` for class extension. This breaks the prototype chain for Error subclasses — `instanceof AppError` returns `false` for instances that ARE AppError. Silent: code compiles, errors throw, the catch block in the error middleware never matches, every error falls through to the generic 500 handler.

**Defense:** the rule in #8: when the build target transpiles class inheritance, verify custom error subclasses still pass runtime type checks and record the required constructor fix in References.md; convention #8 carries the rule. For this target the fix is `Object.setPrototypeOf(this, new.target.prototype)` in the constructor (dated example; verify against the current transpiler). Test: assert `new SomeSubclass() instanceof AppError === true`.

## 18. Package peers drift from SDK expectations

Mobile-specific: a managed mobile SDK pins the native runtime and several peers to exact versions. Installing one of those peers by name with the generic package manager (or pinning from training data) misses the SDK-intended version. The SDK's own doctor command catches it; the generic installer does not. First native build breaks or behaves unpredictably.

**Defense:** SCAFFOLD-MOBILE installs SDK-peer packages through the SDK's own installer, which reads its compatibility matrix. The generic installer is only for explicitly-non-SDK packages. The SDK's doctor command, run as part of verify, is the safety net.

---

## Handling a fired red flag

If one of these fires during or after scaffolding:
1. Resolve it before the step closes: fix the cause, or, when the flag does not fit how this application works, set the step aside with the reason (development/STEPS.md).
2. Record the red flag and its resolution in the `VERSION-LOG.md` scaffold entry.
3. Never paper it over with a `// TODO` comment.
4. Re-run `scripts/validate-scaffold.sh`.

Silent failure is worse than loud failure. A loud failure blocks the merge; a silent failure ships to production.
