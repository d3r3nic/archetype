# Convention #15: Build, CI/CD & Code Quality

## Principle

Quality is enforced automatically, not by convention alone. Linters catch style issues, type checkers catch type errors, tests catch logic errors, and the CI pipeline blocks merging code that fails any check. The pipeline is the final authority. Lint rules catch categories of mistakes AI agents make most often; the specific rule IDs are language-dependent.

## Reusable System

Create a quality enforcement pipeline that establishes:
- A linting configuration with rules catching the AI-prone categories: untyped escape hatches (the language's equivalent of `any` or `Any`), console-level output left in production code, direct imports from third-party UI libraries (bypassing project wrappers), unsafe casts / non-null assertions, empty catch / except blocks
- A formatting configuration applied automatically on save and verified in CI
- A CI pipeline that runs in a predictable sequence: lint, type-check, unit test, build, integration test, end-to-end test, deploy
- Bundle size budgets (for client bundles) or equivalent size/perf budgets that fail the build if exceeded
- Feature flag tooling with a cleanup discipline: flags default to off, and flag code is removed after full rollout
- Preview deployments that create a unique URL for every pull request so changes can be visually reviewed before merging
- Instant rollback capability so any deployment can be reversed immediately

## Rules

- The CI pipeline is the merge gate. Code that fails any check does not merge.
- Lint rules target AI-prone categories (listed above). The specific rule IDs depend on the language's linter — research current rule IDs for the chosen stack at bootstrap time.
- Formatting is automated. Never manually format code. Configure format-on-save and verify in CI.
- Feature flags default to off. When a feature is fully rolled out, remove the flag and all conditional code immediately. Stale flags accumulate dead code paths.
- Dead code detection runs periodically. Remove unused exports, files, and dependencies.
- Every deployment can be rolled back instantly. Never deploy without a rollback path.
- Bundle size (or equivalent output size) is monitored. If a change causes the bundle to exceed the budget, the build fails.

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
- WRONG: the linting config uses default rules only. AI generates code with untyped escape hatches, console-level output, direct UI library imports, unsafe casts. None are caught.
- RIGHT: lint rules configured for the AI-prone categories catch these before commit. Research the specific rule IDs for the language's linter (examples by language: TS ESLint, Python Ruff, Go golangci-lint, Rust Clippy, .NET Roslyn analyzers, Ruby RuboCop).

## Research Notes

When bootstrapping this convention, research current tooling for the chosen language/stack:
- Native linter for the language. Configure rules for the AI-prone categories: untyped escape hatches, console-level output, direct third-party UI imports, unsafe casts / non-null-assertions, empty catch/except blocks. Specific rule IDs depend on the linter (ESLint for JS/TS, Ruff or Flake8 + Bandit for Python, golangci-lint for Go, Clippy for Rust, Roslyn analyzers for .NET, RuboCop for Ruby, PHP_CodeSniffer/PHPStan for PHP).
- Native formatter. Configure format-on-save and verify in CI.
- CI platform setup for the deployment target. Configure the full sequence: lint → type-check → test → build → size check → deploy.
- Feature-flag tooling that integrates with the language and framework.
- Bundle/output size analysis and budget enforcement for the build tool.
- Dead code detection tooling for the language.

Document the pipeline config, lint rules (with rule IDs), size budgets, and deployment process in References.md. Mark which rules are AI-prone-category coverage vs general style so the review intent is clear.
