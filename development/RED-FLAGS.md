# Development Red Flags — Phase 3 Silent-Failure Patterns

Routed from `development/DEVELOP.md`. Parallels `bootstrap/RED-FLAGS.md` and `scaffolding/RED-FLAGS.md`. These are failure modes where a feature can ship "working" while silently violating conventions or skipping critical artifacts. Read before building; consult during each step.

Silent-failure in Phase 3 means: the feature passes tests, the build succeeds, but a framework convention was violated invisibly. Technical debt accumulates; future features built on the same drift compound the damage.

## 1. Rebuild a shared system instead of using it

Agent writes its own database client, its own error class, its own token parser — when `src/shared/db/`, `src/shared/errors/`, `src/shared/auth/` already exist. Root CLAUDE.md says "Read feature-tree.md before building anything new" — but DEVELOP.md's system-inventory step is the operational gate.

**Defense:** DEVELOP.md Step 1 mandates an explicit inventory: enumerate every shared system from feature-tree.md, map to "will use / not needed." If "will use," note the import. Nothing checks that the inventory happened — this defense rests on the agent following the playbook. `validate-develop.sh` catches only the narrow tail: direct construction of a shared database or cache client inside features, matched against a fixed list of client class names that ages as stacks change. It does not inspect imports, and a rebuilt error class or token parser passes it.

## 2. Bypass a shared getter by instantiating the class directly

Most insidious form of #1. Agent imports the database client class from its package and news-up its own instance because "just for this one query." Violates convention #0 (single source of truth) silently — code typechecks, tests pass, but two client instances now exist in the process and transactions won't compose.

**Defense:** CLAUDE.md rule: *"Never instantiate a shared getter's underlying class. Type imports and namespace imports are OK."* `validate-develop.sh` fails on direct construction of a shared database or cache client anywhere under features/. The pattern list is fixed and dated, and only non-test files under features/ are scanned: a client class the list does not name, the same bypass outside features/, and a bypass inside a test file all pass the check. The rule is wider than the gate.

- Dated example: the shapes the list carries today are `new PrismaClient(`, `new Redis(`, and `new IORedis(`; a project whose clients are not those gets no machine help here.

## 3. Zero tests because DEVELOP.md is vague about minimums

A playbook that says only "run tests after every significant change" leaves the minimum unstated. A lazy agent writes zero new tests, runs the existing ones, and claims conformance. Convention #18 is about VERIFICATION, not test COVERAGE.

**Defense:** DEVELOP.md Step 5 sets a minimum test baseline by endpoint type. For auth-protected HTTP endpoints: at least one each of auth-fail (401), validation-fail (400), happy-path (2xx), and an edge case matching the feature's domain (not-found, conflict, etc.). Feature-specific extensions per sensible judgment. `validate-develop.sh` checks that a feature has a test file at all, never which cases are in it — the baseline itself rests on the agent.

## 4. Skip the feature doc

Feature docs sit late in the workflow (DEVELOP.md Step 7). An agent building to completion-deadline skips "docs can come later." Silent: code ships, doc never gets written, next agent has no feature-level onboarding context.

**Defense:** DEVELOP.md Step 7 makes the feature doc a completion gate, not an optional trailing step. `validate-develop.sh` cross-checks in the other direction — every feature row in feature-tree.md must have a `docs/features/{name}.md` — and it warns and skips that check entirely when the project has no feature tree or no `docs/features/` directory. A feature that never reached the feature tree is caught by neither check, so the feature-tree update is the same gate and it rests on the agent.

## 5. Skip the References.md update when new top-level paths emerge

First time a feature introduces a new top-level folder (`docs/features/` when `docs/` was empty, a new `src/features/` pattern, a new shared module), References.md § Folder Structure goes stale. Silent: build works; next agent reading References.md gets an outdated folder structure and builds in the wrong place.

**Defense:** DEVELOP.md Step 7 requires: "If your feature introduced a new top-level path, update References.md § Folder Structure. Do not silently let References.md drift from reality." No check compares References.md against the tree; this one is the playbook step and nothing else.

## 6. Partial commits with no granularity rule

A playbook that says only "commit as a save point" gives no trigger. Agent commits mid-feature with failing tests, or never commits, or commits the whole feature in one giant commit that hides bugs. Convention #2 has the rules; a playbook that doesn't operationalize them leaves them unused.

**Defense:** DEVELOP.md Step 8 sets the trigger: commit when "a verification gate just passed cleanly." Never commit with failing typecheck / tests / build. Each feature's commits form a rollback ladder aligned with the verification gates. Granularity is not machine-checkable — this is discipline, not a gate.

## 7. Feature doc and route file drift

Feature doc describes API shape X; the route handler implements X'. Both "work." Future agent reading the doc believes X, writes client code against X, and hits X' at runtime. No framework mechanism detects this.

**Defense:** DEVELOP.md's feature-doc template requires API shape (request schema, response schema, errors) to be documented by reference to the source file, not copy-pasted. Cross-link recommendation: a one-line header comment in the route file pointing at the feature doc. Not a validator gate (hard to detect drift automatically) but the convention reduces copy-paste risk.

## 8. Integration tests share state without isolation

Multiple feature test files run against the same DB (typical for a file-backed integration database). Test A leaves rows, Test B runs an unfiltered query and sees Test A's data. Each test passes in isolation; the combined test suite is flaky or wrong.

The common failure mode: a list/aggregate endpoint's test asserts row count or empty result without a feature-scoped filter. Sibling tests seed rows that the assertion doesn't account for. Symptom: the suite is green on the first run after a DB wipe, red on the second.

**Defense:** pick one of these isolation strategies at scaffold time and document it in References.md:
- **Set-membership with a unique test-scoped prefix** — each test's fixtures use a namespace (e.g., player name prefixed with test ID). Assertions match by prefix, not total counts.
- **Transaction rollback per test** — each test runs inside a transaction that rolls back in `afterEach`. Requires the test runner and ORM to support nested transactions or rollback.
- **Separate database URL per test file** — each test file gets its own ephemeral DB (a per-feature database file for a file-backed engine, a separate schema for a server engine). Highest isolation, slowest.
- **Test containers with reset between suites** — for real-DB-like fidelity with cleaner isolation than a shared file DB.

If none of these is in place, assertions must be isolation-resilient (scoped lookups, not total-count assertions). A list-endpoint test that says "returned rows contain my test's fixtures" rather than "returned rows.length === N" will survive sibling contamination.

## 9. Escape-hatch on type errors (casts, re-instantiation)

When the language's strict type config fights a library's generic signatures (e.g., `exactOptionalPropertyTypes` vs. an ORM's optional-property types), the tempting fix is `as any`, `// @ts-ignore`, or instantiating a fresh client with a laxer config. All three silently violate framework conventions (#7 types, #0 reusability).

**Defense:** refactor the call site, don't escape-hatch the type system. If `where: condition ? {...} : undefined` fights `exactOptionalPropertyTypes`, use a conditional spread (`where: { ...(condition && { ... }) }`) or build the args object imperatively. Never `as any`. Never `new` a fresh client to dodge one call's type friction. CLAUDE.md rule: *"Never escape-hatch the type system with casts, ignore comments, or re-instantiation to dodge a single call site. Refactor the call site."* Type friction is a signal that the API surface is wrong for the data, not a signal that the type system is wrong.

## 10. Undesigned screen shipped

Agent codes a screen or a state (an error, an empty list, a confirm dialog) the artifact never showed, because the artifact was silent and the feature was due. Tests pass, the build succeeds, and the interface has one more improvised pattern; the next feature copies it. Convention #27 exists to prevent exactly this, and a design tool run without the artifact as its brief produces the same drift one step earlier.

**Defense:** DEVELOP.md Step 1 names the artifact in the inventory and lists the screens and states it covers; a gap is designed first, with the owner's pick where a direction is open (#27, #29). The feature doc's Design line records which artifact entry and revision the code implements. Nothing checks that line's truth: `validate-develop.sh` does not read the artifact, and the maintain audit's drift item is the only later catch.

---

## How to use this file

Read before starting a feature. If you notice yourself heading toward one of these patterns (e.g., about to import a shared client class directly because it's "just one call"), STOP — that IS red flag #2. Resolve by using the shared getter before proceeding.

If `validate-develop.sh` flags a violation, as an error or as a warning, FIX the violation. Do not paper over with a lint-suppression comment. Most of these patterns have no check at all, so a clean validator run is not evidence that none of them fired. Silent failure is worse than loud failure.
