# Development Red Flags — Phase 3 Silent-Failure Patterns

Routed from `development/DEVELOP.md`. Parallels `bootstrap/RED-FLAGS.md` and `scaffolding/RED-FLAGS.md`. These are failure modes where a feature can ship "working" while silently violating conventions or skipping critical artifacts. Read before building; consult during each step.

Silent-failure in Phase 3 means: the feature passes tests, the build succeeds, but a framework convention was violated invisibly. Technical debt accumulates; future features built on the same drift compound the damage.

## 1. Rebuild a shared system instead of using it

Agent writes its own PrismaClient instance, its own error class, its own token parser — when `src/shared/db/`, `src/shared/errors/`, `src/shared/auth/` already exist. Root CLAUDE.md says "Read feature-tree.md before building anything new" — but DEVELOP.md's system-inventory step is the operational gate.

**Defense:** DEVELOP.md Step 1 mandates an explicit inventory: enumerate every shared system from feature-tree.md, map to "will use / not needed." If "will use," note the import. `validate-develop.sh` greps features/ for direct library imports that bypass shared wrappers.

## 2. Bypass a shared getter by instantiating the class directly

Most insidious form of #1. Agent imports `PrismaClient` from `@prisma/client` and news-up its own instance because "just for this one query." Violates convention #0 (single source of truth) silently — code typechecks, tests pass, but two Prisma instances now exist in the process and transactions won't compose.

**Defense:** CLAUDE.md rule: *"Never instantiate a shared getter's underlying class. Type imports and namespace imports are OK."* `validate-develop.sh` fails on `new PrismaClient(` outside `src/shared/db/`. Similar checks for other shared classes as the framework discovers them.

## 3. Zero tests because DEVELOP.md is vague about minimums

Old DEVELOP.md said "run tests after every significant change." A lazy agent writes zero new tests, runs the existing ones, and claims conformance. Convention #18 is about VERIFICATION, not test COVERAGE.

**Defense:** DEVELOP.md Step 4 sets a minimum test baseline by endpoint type. For auth-protected HTTP endpoints: at least one each of auth-fail (401), validation-fail (400), happy-path (2xx), and an edge case matching the feature's domain (not-found, conflict, etc.). Feature-specific extensions per sensible judgment.

## 4. Skip the feature doc

Feature docs end up buried at Step 5 of DEVELOP.md. An agent building to completion-deadline skips "docs can come later." Silent: code ships, doc never gets written, next agent has no feature-level onboarding context.

**Defense:** DEVELOP.md step ordering revised — feature doc is a completion gate, not a trailing step. `validate-develop.sh` fails if a feature directory exists without a corresponding `docs/features/{name}.md`. feature-tree.md update is the same gate.

## 5. Skip the References.md update when new top-level paths emerge

First time a feature introduces a new top-level folder (`docs/features/` when `docs/` was empty, a new `src/features/` pattern, a new shared module), References.md § Folder Structure goes stale. Silent: build works; next agent reading References.md gets an outdated folder structure and builds in the wrong place.

**Defense:** DEVELOP.md Step 7 added: "If your feature introduced a new top-level path, update References.md § Folder Structure. Do not silently let References.md drift from reality."

## 6. Partial commits with no granularity rule

DEVELOP.md Step 6 said "commit as a save point." No trigger. Agent commits mid-feature with failing tests, or never commits, or commits the whole feature in one giant commit that hides bugs. Convention #2 has rules; DEVELOP.md didn't operationalize them.

**Defense:** DEVELOP.md Step 6 rewritten: commit trigger is "a verification gate just passed cleanly." Never commit with failing typecheck / tests / build. Each feature's commits form a rollback ladder aligned with the verification gates.

## 7. Feature doc and route file drift

Feature doc describes API shape X; the route handler implements X'. Both "work." Future agent reading the doc believes X, writes client code against X, and hits X' at runtime. No framework mechanism detects this.

**Defense:** DEVELOP.md feature-doc template now requires API shape (request schema, response schema, errors) to be documented by reference to the source file, not copy-pasted. Cross-link recommendation: a one-line header comment in the route file pointing at the feature doc. Not a validator gate (hard to detect drift automatically) but the convention reduces copy-paste risk.

## 8. Integration tests share state without isolation

Multiple feature test files run against the same DB (typical for SQLite integration testing). Test A leaves rows, Test B runs an unfiltered query and sees Test A's data. Each test passes in isolation; the combined test suite is flaky or wrong.

The common failure mode: a list/aggregate endpoint's test asserts row count or empty result without a feature-scoped filter. Sibling tests seed rows that the assertion doesn't account for. Symptom: `npm test` green on first run after a DB wipe, red on second run.

**Defense:** pick one of these isolation strategies at scaffold time and document it in References.md:
- **Set-membership with a unique test-scoped prefix** — each test's fixtures use a namespace (e.g., player name prefixed with test ID). Assertions match by prefix, not total counts.
- **Transaction rollback per test** — each test runs inside a transaction that rolls back in `afterEach`. Requires the test runner and ORM to support nested transactions or rollback.
- **Separate DATABASE_URL per test file** — each `.test.ts` gets its own ephemeral DB (e.g., `dev.{feature}.db` for SQLite, separate schemas for Postgres). Highest isolation, slowest.
- **Test containers with reset between suites** — for real-DB-like fidelity with cleaner isolation than a shared file DB.

If none of these is in place, assertions must be isolation-resilient (scoped lookups, not total-count assertions). A list-endpoint test that says "returned rows contain my test's fixtures" rather than "returned rows.length === N" will survive sibling contamination.

## 9. Escape-hatch on type errors (casts, re-instantiation)

When the language's strict type config fights a library's generic signatures (e.g., `exactOptionalPropertyTypes` vs. an ORM's optional-property types), the tempting fix is `as any`, `// @ts-ignore`, or instantiating a fresh client with a laxer config. All three silently violate framework conventions (#7 types, #0 reusability).

**Defense:** refactor the call site, don't escape-hatch the type system. If `where: condition ? {...} : undefined` fights `exactOptionalPropertyTypes`, use a conditional spread (`where: { ...(condition && { ... }) }`) or build the args object imperatively. Never `as any`. Never `new` a fresh client to dodge one call's type friction.

CLAUDE.md rule: *"Never escape-hatch the type system with casts, ignore comments, or re-instantiation to dodge a single call site. Refactor the call site."* Type friction is a signal that the API surface is wrong for the data, not a signal that the type system is wrong.

---

## How to use this file

Read before starting a feature. If you notice yourself heading toward one of these patterns (e.g., about to import PrismaClient directly because it's "just one call"), STOP — that IS red flag #2. Resolve by using the shared getter before proceeding.

If `validate-develop.sh` flags a violation, FIX the violation. Do not paper over with a `// eslint-disable` or a comment. Silent failure is worse than loud failure.
