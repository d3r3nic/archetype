# Convention #15: Build, CI/CD & Code Quality

## Principle

Quality is enforced automatically, not by convention alone. Linters catch style issues, type checkers catch type errors, tests catch logic errors, and the CI pipeline blocks merging code that fails any check. The pipeline is the final authority. AI-targeted lint rules catch the specific mistakes AI agents make most often.

## Reusable System

Create a quality enforcement pipeline that establishes:
- A linting configuration with AI-targeted rules: ban "any" types, ban console.log in production, ban direct imports from third-party UI libraries, ban non-null assertions
- A formatting configuration applied automatically on save and verified in CI
- A CI pipeline that runs in a predictable sequence: lint, type-check, unit test, build, integration test, end-to-end test, deploy
- Bundle size budgets that fail the build if exceeded
- Feature flag tooling with a cleanup discipline: flags default to off, and flag code is removed after full rollout
- Preview deployments that create a unique URL for every pull request so changes can be visually reviewed before merging
- Instant rollback capability so any deployment can be reversed immediately

## Rules

- The CI pipeline is the merge gate. Code that fails any check does not merge.
- Lint rules target the specific mistakes AI makes: any types, console.log, direct third-party imports, non-null assertions, empty catch blocks.
- Formatting is automated. Never manually format code. Configure format-on-save and verify in CI.
- Feature flags default to off. When a feature is fully rolled out, remove the flag and all conditional code immediately. Stale flags accumulate dead code paths.
- Dead code detection runs periodically. Remove unused exports, files, and dependencies.
- Every deployment can be rolled back instantly. Never deploy without a rollback path.
- Bundle size is monitored. If a change causes the bundle to exceed the budget, the build fails.

## Violations

- Merging code that fails CI checks
- No type-checking in the CI pipeline (only linting)
- Stale feature flags left in code after full rollout
- No rollback capability for deployments
- Empty catch blocks (error silently swallowed with no logging or handling)
- Console.log left in production code
- No AI-targeted lint rules (the default linting config doesn't catch AI-specific mistakes)
- Bundle growing unchecked with no budget enforcement

## Wrong vs Right

- WRONG: CI only runs tests. Code with type errors, lint violations, and oversized bundles merges freely. Quality degrades over time.
- RIGHT: CI runs lint, type-check, test, build, and bundle size check in sequence. Any failure blocks the merge. Quality is enforced mechanically.
- WRONG: a feature flag is created for a new feature. The feature ships, everyone uses it, but the flag code stays in the codebase. Six months later, twenty stale flags with dead code paths.
- RIGHT: when a feature is fully rolled out, the flag is removed and all conditional code is cleaned up in the same sprint.
- WRONG: the linting config uses default rules only. AI generates code with "any" types, console.log statements, and direct UI library imports. None of these are caught.
- RIGHT: AI-targeted lint rules catch the specific mistakes AI makes most often. The linter flags any types, console.log, direct imports, and non-null assertions before the code can be committed.

## Research Notes

When bootstrapping this convention:
- Research the framework's recommended linting tools and configure AI-targeted rules (ban any, ban console.log, ban direct third-party imports, ban non-null assertions, ban empty catch)
- Research the framework's formatting tool and configure format-on-save plus CI verification
- Research CI pipeline setup for the framework's deployment target. Configure the full sequence: lint → type-check → test → build → bundle check → deploy
- Research feature flag tooling that integrates with the framework
- Research bundle analysis and budget enforcement tools for the framework's build tool
- Research dead code detection tools for the language
- Document the pipeline config, lint rules, bundle budgets, and deployment process in References.md
