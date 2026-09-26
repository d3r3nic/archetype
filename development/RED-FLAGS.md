# Development Red Flags — Phase 3 Silent-Failure Patterns

Routed from `development/DEVELOP.md`. Parallels `bootstrap/RED-FLAGS.md` and `scaffolding/RED-FLAGS.md`. These are failure modes where a feature can ship "working" while silently violating conventions or skipping critical artifacts. Read before building; consult during each step.

Silent-failure in Phase 3 means: the feature passes tests, the build succeeds, but a framework convention was violated invisibly. Technical debt accumulates; future features built on the same drift compound the damage.

## 1. Rebuild a shared system instead of using it

A session writes its own database client, its own error type, its own token parser, when the project already has an owner for each. Root AGENTS.md says to check what exists before building; DEVELOP.md Step 1 is where that happens.

**Defense:** DEVELOP.md Step 1 inspects the affected behavior and the shared systems it can reuse. Reuse a fitting owner; revise a mismatch deliberately instead of silently creating a competing one (#0). The project's § Boundaries lines make the common cases machine-checked: `scripts/validate-develop.sh` fails when code outside an owner's paths uses what only that owner may use. A duplicated rule that no line describes is caught only by review.

## 2. Bypass a shared owner by creating its client directly

The most insidious form of #1. A session creates its own instance of a shared client "just for this one query". The code checks and the tests pass, but two instances now exist, with different configuration and transactions that do not compose.

**Defense:** the rule (#0, #7): never create a shared owner's underlying client outside the owner; type-only references are fine. Record the owner's § Boundaries line, such as `` - Database: `<the pattern that creates a connection>` only in `<the data-access path>`, `*.test.*` ``, and `scripts/validate-develop.sh` fails every construction outside those paths. The check reads the patterns the project recorded, so its reach is exactly the lines the project wrote: a client with no line is caught only by review.

## 3. Zero tests because DEVELOP.md is vague about minimums

A playbook that says only "run tests after every significant change" leaves the minimum unstated, and a session writes no new tests, runs the old ones, and claims conformance.

**Defense:** DEVELOP.md Step 5 chooses coverage from behavior and risk: unauthorized access, invalid input, success and the relevant domain failures where they apply. Each feature record's Tests line names where its tests are, and `scripts/validate-develop.sh` checks that those paths exist (or that the record says none, with the reason). It cannot see what the tests cover; review the tests and their results rather than counting files.

## 4. Skip the feature doc

The feature record comes late in the workflow (DEVELOP.md Step 7), and a session racing to finish decides "docs can come later". The code ships, the record never does, and the next session has no feature-level context.

**Defense:** DEVELOP.md Step 7 makes the record part of completion. `scripts/validate-develop.sh` checks every feature row in feature-tree.md: its record (the path in its Docs column, or `docs/features/{name}.md`) must exist. A feature that never reached the feature tree is caught by neither, so the feature-tree row is part of the same completion.

## 5. Skip the References.md update when new top-level paths emerge

First time a feature introduces a new top-level folder (`docs/features/` when `docs/` was empty, a new `src/features/` pattern, a new shared module), References.md § Folder Structure goes stale. Silent: build works; next agent reading References.md gets an outdated folder structure and builds in the wrong place.

**Defense:** DEVELOP.md Step 7 updates References.md when a command, system entry point or accepted convention changes. Current facts have one authoritative location; other readers link there. No check compares every References.md fact against source, so review affected links and facts.

## 6. Partial commits with no granularity rule

A playbook that says only "commit as a save point" gives no trigger. Agent commits mid-feature with failing tests, or never commits, or commits the whole feature in one giant commit that hides bugs. Convention #2 has the rules; a playbook that doesn't operationalize them leaves them unused.

**Defense:** DEVELOP.md Step 8 preserves coherent verified changes as recovery points within repository authorization. Granularity follows the changed contract and review needs; it is not machine-checked. State what was actually verified and committed.

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

## 9. Escape-hatch on type errors (casts, suppressions, a second client)

When the language's strict checking fights a library's signatures, the tempting fix is an untyped escape, a suppression comment, or a fresh client created with looser settings. All three hide a real mismatch (#7, #0).

**Defense:** fix the call site: build the arguments so their shape is what the signature expects, narrow the value, or change the contract. Never cast or suppress to make one call pass, and never create a second client to get around a type. Type friction says the interface does not fit the data, not that the checker is wrong.

## 10. Undesigned screen shipped

Agent codes a screen or a state (an error, an empty list, a confirm dialog) the artifact never showed, because the artifact was silent and the feature was due. Tests pass, the build succeeds, and the interface has one more improvised pattern; the next feature copies it. Convention #27 exists to prevent exactly this, and a design tool run without the artifact as its brief produces the same drift one step earlier.

**Defense:** DEVELOP.md Step 1 reads the current artifact and relevant states before implementing a screen. The session records missing composition within the agreed direction and respects owner authority for identity or purpose. The canonical feature template links the basis, artifact, code and reviewed captures. No script establishes the truth of the review; independent inspection and interaction evidence remain necessary.

---

## How to use this file

Read before starting a feature. If you notice yourself heading toward one of these patterns (e.g., about to import a shared client class directly because it's "just one call"), STOP — that IS red flag #2. Resolve by using the shared getter before proceeding.

If `validate-develop.sh` flags a violation, as an error or as a warning, fix it; when the finding misreads a justified approach, reproduce the mismatch and record it as DEVELOP.md Step 6 says. Never paper it over with a lint-suppression comment. Most of these patterns have no check at all, so a clean validator run is not evidence that none of them fired. Silent failure is worse than loud failure.
