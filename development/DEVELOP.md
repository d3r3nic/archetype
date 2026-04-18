# Phase 3: Develop

Build features on top of scaffolded foundational systems. Runs for the life of the project.

## Prerequisites

- Phase 2 (Scaffold) complete
- `feature-tree.md § Foundational Systems` populated
- `References.md § Foundational Systems` lists every shared system's location + import path
- Verification commands (`npm test` / pytest / equivalent) runnable and green

## Before starting a feature — read these in order

1. `CLAUDE.md` (the enforcer — universal rules)
2. `References.md` — tech stack, Commands, Foundational Systems, Convention Overrides, Critical Lessons
3. `feature-tree.md` — inventory of what exists (systems + other features)
4. `Conventions.md` — scan the lookup table for YOUR task type (it's an index, NOT a reading list)
5. `development/RED-FLAGS.md` — 7 Phase 3 silent-failure patterns

Note: if framework is in `archetype/` subfolder, conventions live at `archetype/Conventions.md` and `archetype/backend/Conventions.md` (for backend projects).

## Feature Development Workflow

### Step 1 — Inventory (not optional)

Before writing ANY code, enumerate the shared systems from `feature-tree.md § Foundational Systems`. For each system, decide: **will use** or **not needed for this feature**. Note the import path for every "will use."

Example inventory for a "record-session" feature:

- errors (src/shared/errors/) — will use (AppError subclasses for typed errors)
- db (src/shared/db/) — will use (`getDb()` for the session insert)
- auth (src/shared/auth/) — will use (`requireAuth` — this is a write endpoint)
- logger (src/shared/logger/) — will use (`req.log` for the request-scoped logger)
- env (src/shared/config/env.ts) — not needed directly (used via auth and db)
- types — will use (Zod schema at HTTP boundary)

If you find yourself wanting to `new` up a class that's already wrapped in `src/shared/`, STOP — that's red flag #2 (see `development/RED-FLAGS.md`). Use the getter.

### Step 2 — Route conventions before coding

Open `Conventions.md`. Find the row(s) matching your feature's shape (new API endpoint, new form, new page, etc.). Identify 3-5 relevant convention docs. READ them before writing code.

**Backend projects:** also scan `backend/Conventions.md` for backend-specific routing — the universal Conventions.md may route you to client-side conventions for server-side tasks if you're not careful.

Before writing any code, STATE (in comments, in your plan, or in the feature doc's draft) which conventions you read and how they apply. This is the workflow gate — CLAUDE.md says AI should confirm conventions before first code output.

### Step 3 — Plan (for multi-file features)

For a single-file change (bug fix, obvious edit): skip to Step 4.

For a feature touching 3+ files:
- What files will be created / modified
- Which shared systems from Step 1 are used where
- What new abstractions, if any (and does each satisfy #0 — built once, configured for context?)
- Which tests cover which behaviors (see Step 5 baseline)
- Rollback plan (the commit ladder from Step 7)

Either write this plan inline or in a scratch doc. It's not a ceremony — it's how you catch over-engineering before you ship it.

### Step 4 — Implement

- Use the shared systems from Step 1. Never build ad-hoc.
- Follow the project's folder structure for the new feature (see References.md § How to Add a New Feature).
- Follow convention #0: if a component/service could be reused, build it reusable.
- Prefer composition over configuration over forking. Configuration is preferred; forking is the last resort.
- Never `throw new Error(...)` — use AppError subclasses from `src/shared/errors/`.
- Never `console.log` — use the shared logger.
- Never `new` up a class that has a shared getter (red flag #2).

### Step 5 — Tests (minimum baseline by endpoint type)

For a new HTTP endpoint requiring authentication:
- At least one **auth-fail** test (401 without valid token)
- At least one **validation-fail** test (400 with malformed input)
- At least one **happy-path** test (2xx with valid input, correct response shape)
- At least one **edge-case** test matching the feature's domain (not-found, conflict, unauthorized-for-resource, etc.)

For a public (unauthenticated) endpoint: drop the auth-fail, keep the other three.

For a background job or internal service: at least one happy-path and one failure-path test.

These are baselines. Add more for domain-specific risks (race conditions, concurrent writes, rate-limit boundaries).

Tests live co-located with the feature: `src/features/{name}/{name}.test.ts` (adjust extension/format to project language). Follow the existing scaffold pattern — if `src/features/health/health.test.ts` exists, match that style.

**Test isolation:** when multiple integration test files share a database (common for SQLite / ephemeral setups), assertions must be isolation-resilient. Sibling test files leave rows; an unfiltered list-endpoint test asserting `length === N` will flake. See `development/RED-FLAGS.md` #8 for the four isolation strategies — pick one at scaffold time and document it in References.md. Minimum bar: scoped lookups (set-membership assertions) rather than total-count assertions.

### Step 6 — Verify (run the gates)

Run each of the project's verification commands from `References.md § Commands`. For a typical backend:

```
npm run typecheck   # must exit 0
npm test            # must exit 0, all tests passing including new ones
npm run build       # must exit 0
```

Do NOT proceed to Step 7 if any gate is red. Fix the issue. Do not paper over with skip-tests / eslint-disable / type-assertions-to-any.

### Step 7 — Document + cross-reference

Required artifacts every feature produces:

1. **Feature doc** at `docs/features/{feature-name}.md` using the template below.
2. **feature-tree.md update** — new row with: feature name, location, routes (if any), shared systems used, status, doc path.
3. **References.md update** — only if the feature introduced a new top-level path (first `docs/features/`, new `src/features/*/` subfolder pattern, etc.). Silent drift between code and References.md is red flag #5.

### Step 8 — Commit (granularity = verification gates)

Commit trigger: **a verification gate just passed cleanly.** Per convention #2, each commit is a rollback point.

- Never commit with failing typecheck / tests / build.
- Prefer one commit per feature if it's small and all gates were green after the final change.
- For multi-step features, commit after each gate passes (e.g., commit schema + migration, commit implementation, commit tests, commit docs). The commit history becomes the rollback ladder.
- Commit messages describe the WHY, not just the WHAT. See convention #2.

## Feature Documentation Template

Each feature gets a doc at `docs/features/{feature-name}.md`:

```
# {Feature Name}

## What It Does
[One paragraph: what the feature does from the user's perspective]

## Why It Exists
[Business reason or technical need]

## Systems Used
[Which foundational systems this feature plugs into — match Step 1 inventory]
- Errors: [how used]
- DB: [how used]
- Auth: [permission requirements]
- Logger: [what gets logged]

## API Shape
- **Route(s):** [method + path]
- **Request:** [schema / Zod type name / reference to schema.ts]
- **Response (success):** [shape]
- **Errors:** [table of code → status → message]

## Structure
[Files this feature owns, one-line purpose each. Link the route file to this doc as a header comment.]

## Test Coverage
[Brief list of what's tested — auth-fail, validation-fail, happy-path, edge cases]

## Key Decisions
[Non-obvious choices made during implementation. Trade-offs, deferred work, feature-flag status, etc.]
```

## When a New AI Agent Joins Mid-Project

1. Read `CLAUDE.md` (the enforcer — learn the rules)
2. Read `Conventions.md` (scan the convention index)
3. Read `References.md` (tech stack, system locations, Commands, Overrides, Lessons)
4. Read `feature-tree.md` (what exists, what's in progress)
5. Read `docs/systems/` for systems relevant to the current task
6. Read `docs/features/{feature}.md` for the feature you're working on
7. Read `development/RED-FLAGS.md` once — it's short, it's the failure catalog
8. Start working: the foundational systems are already in place. Use them (don't rebuild them).

## Final gate — automated validator

Run `scripts/validate-develop.sh` before committing:

- No direct shared-class instantiation in features (bypassing getters — red flag #2)
- No console-level output in `src/features/` (red flag — use the shared logger)
- Every `src/features/{name}/` has a matching test file
- Every feature in feature-tree.md has a `docs/features/{name}.md`
- No `throw new Error(` in features (use AppError subclasses — red flag #1 spillover)

If the validator fails, fix the underlying issue. Do not paper over.
