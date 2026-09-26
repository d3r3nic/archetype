# Scaffold Red Flags — Silent-Failure Patterns

Routed from `scaffolding/SCAFFOLD.md` and the shape-specific playbooks. These are the ways a scaffold can be called complete while a system is broken or absent. A stepped playbook names the sections each step reads; an unstepped one reads the catalogue before scaffolding.

Silent failure means no error, no warning, no broken build, and the system is still wrong.

## 1. Skipped-by-interpretation (project-shape tag)

A step marked for one shape, or "if applicable", gets skipped by a session that reads the mark as permission to skip rather than as a routing hint.

**Defense:** SCAFFOLD.md routes by project shape first. Within a playbook a step is skipped by its listed condition, a fact the project records, or set aside with the reason when it does not fit how this application works (development/STEPS.md). Never silently: an unrecorded skip is the failure this entry names.

## 2. Checklist-only verification (no execution)

A session ticks "build passes, tests pass, types check" without running the commands.

**Defense:**
- Each step has operational verification with a specific command and exit criterion.
- `scripts/validate-scaffold.sh` runs at the end.
- The scaffold record asks for what was run and seen, not for yes or no (the VERSION-LOG.md scaffold entry template).

## 3. Audit log conflated with app log

A project with regulated data needs two logging systems. A session writes audit events through the application logger with an "audit" field and calls it done. That fails the regime's audit requirements, which ask for different storage, retention, mutability and access.

**Defense:**
- SCAFFOLD-BACKEND builds the audit trail as its own step, separate from the application logger.
- B4 opens with the two systems; #23 points to it.
- validate-scaffold.sh checks, wherever the unit handles regulated data (PROFILE.md, or the unit's References.md), that an audit log exists at the location References.md § Compliance records on its Audit log line and is not a memory-only store. That it is separate from the application logger is the review's to read.

## 4. Middleware pipeline in wrong order

When pipeline steps are added one at a time in different places, their order is an accident. A wrong order fails silently:
- identity checked before the browser's cross-origin preflight is answered: the preflight fails;
- rate limiting after identity: failed sign-in attempts spend the limit meant to stop them;
- error handling not outermost: unhandled failures leak internal details.

**Defense:** SCAFFOLD-BACKEND builds the pipeline in one step, in the order the project records with its reasons (B3).

## 5. Rate limiting and idempotency forgotten

Both are easy to leave out because nothing fails without them until someone abuses an endpoint or a client retries.

**Defense:** SCAFFOLD-BACKEND has a step for each, applying when the facts call for it, and the Step 0 handoff check inventories every system References.md lists against the playbook's steps. validate-scaffold.sh checks neither.

## 6. Tenant isolation in schema but not queries (CRITICAL for multi-tenant products)

The schema has tenant columns, so tenant isolation is marked done. But nothing enforces it where queries are made: a feature can read across tenants by leaving the condition out. This is the most common data leak in multi-tenant systems.

**Defense:** SCAFFOLD-BACKEND distinguishes the column existing from the query layer enforcing it. Enforce it in the data-access layer (a default scope, row-level protection, or a wrapper that refuses an unscoped query), and prove it with a test in which a cross-tenant read fails.

## 7. Env validation at runtime, not startup

Configuration read ad hoc across the code means a missing value fails in the middle of a request, after a deploy has succeeded, when the first person hits it.

**Defense:** Step 1 of each shape builds configuration's one owner, which validates every required value at startup, and records its § Boundaries line so nothing else reads the environment (`scripts/validate-develop.sh` enforces it). The step's verify line proves it: remove a required value and the start fails.

## 8. Frontend step titles applied to backend (or vice versa)

A literal-minded session builds a theme for an API-only service because a step says "theme system", or a data layer for a browser-only app because a step says "database".

**Defense:** SCAFFOLD.md routes by project shape before any step, and each step says when it applies.

## 9. Client-composed queries open to public clients

References.md says public or device clients call an API that lets clients compose their own queries, and the service accepts any query. Arbitrary queries are a production attack surface.

**Defense:** SCAFFOLD-BACKEND's API step allow-lists the queries public and device clients may run, and References.md records where the allow-list lives, which validate-scaffold.sh checks exists.

## 10. Migrations auto-run in CI/deploy

B1 keeps production migrations behind a manual or gated path. Many pipeline templates run the migration command on every push to the main branch, so a bad migration reaches production before anyone reviews it.

**Defense:** SCAFFOLD-BACKEND records the migration command in References.md § Commands and bounds it to its production path in § Boundaries. Once § Boundaries exists, validate-scaffold.sh fails a recorded migration command no line bounds, and the boundary check fails the command anywhere else; while the section is absent the gate warns, and validate-develop.sh requires the section.

## 11. Scaffold-complete without integration proof

Every system looks built on its own, but nobody used them together, and the first real feature fails because two of them were never wired through the same request.

**Defense:** every playbook ends with a smoke-test feature that goes through every shared system that was built; its integration test must pass before the scaffold is complete.

## 12. Implicit "skip if not regulated" treated as "skip because I don't want to build it"

Audit log, rate limiting, tenant isolation: the session skips them because "this is just a scaffold, the project can add it later". A system the project's facts require is built; one the operating stage lets wait is a recorded deferral (#30); one that does not fit is set aside with its reason. "Later" with no record is the failure, and the #30 floor is never postponed.

**Defense:** the handoff check (Step 0 of each playbook) inventories every system References.md lists against the playbook before building, so a missed system surfaces then, not after the scaffold claims to be complete.

## 13. Package versions pinned with expirable specifics

A session pins versions from memory, which are stale by the time it scaffolds, and the first install fails or installs deprecated packages.

**Defense:** research current versions at scaffold time (every convention's Research Notes). validate-scaffold.sh does not read versions; each step's install-and-verify line fails loudly on a bad pin.

## 14. Root composition order (frontend/mobile)

When the stack composes shared contexts at the root (error handling, data cache, theme, identity, navigation, shared state), the order decides what each can see, and a wrong order fails quietly: guards that read an identity context mounted below them see nothing and let everyone through; a component that needs the data cache fails at run time; a theme mounted too low flashes unstyled content.

**Defense:** SCAFFOLD-FRONTEND Step 8 records the order once, as one composition, and the test setup of SCAFFOLD-FRONTEND Step 10 reuses that composition instead of copying it, so tests cannot run with a different order than production.

## 15. Route guards forgotten on protected routes

A new route that should require a session is added without the guard. No error: a visitor sees the page, data may leak, and privileged actions may work.

**Defense:** Step 8 protects routes by default: every route goes through the guard unless its definition declares it public. A check can flag a route with no explicit decision, and each protected feature's tests include a refusal for a visitor without a session.

## 16. Env-inlining breaks runtime env mutation in tests

When the build replaces public configuration reads with their literal values at build time, a test that changes such a value at run time changes nothing: the code was compiled with the old value, and tests pass against the wrong configuration.

**Defense:** read values that tests must change through a runtime lookup the build cannot inline, and record in References.md which values are fixed at build time and which are read at run time. SCAFFOLD-MOBILE and Step 10 of the frontend route call this out.

## 17. Custom error types broken by the build target

When the build target rewrites class inheritance for an older runtime, a custom error type can stop being recognized as its parent type: errors are thrown, but the handler that should match them never does, and every error falls through to the generic failure.

**Defense:** #8's rule: verify on the real build target that each custom error type is still recognized as its parent, with a test that asserts it, and record any fix the target requires in References.md.

## 18. Companion packages installed around the platform's own tooling

When the chosen platform's toolkit fixes the versions of its companion packages, installing one of them with the generic package manager, or pinning it from memory, can pick a version the toolkit does not expect, and the first native build breaks or behaves unpredictably.

**Defense:** SCAFFOLD-MOBILE installs the toolkit's companion packages through the toolkit's own installer, which knows its compatibility rules, and runs the toolkit's own health check as part of verification.

---

## Handling a fired red flag

If one of these fires during or after scaffolding:
1. Resolve it before the step closes: fix the cause, or, when the flag does not fit how this application works, set the step aside with the reason (development/STEPS.md).
2. Record the red flag and its resolution in the `VERSION-LOG.md` scaffold entry.
3. Never paper it over with a reminder comment.
4. Re-run `scripts/validate-scaffold.sh`.

Silent failure is worse than loud failure. A loud failure blocks the merge; a silent failure ships to production.
