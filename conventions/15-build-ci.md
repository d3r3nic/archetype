# Convention #15: Build, CI/CD & Code Quality

## Principle

Quality is enforced automatically, not by convention alone. Linters catch style issues, type checkers catch type errors, tests catch logic errors, and CI blocks merging code that fails any check. The pipeline runs in a predictable sequence. Feature flags control rollout without code branches.

## Reusable System

- CI pipeline: configured sequence of quality checks
- Linting config: shared ESLint configuration
- Formatting config: Prettier with team settings
- Feature flag setup: flag service integration
- Preview deployments: per-PR deployment for review

## Rules

- CI pipeline: install → lint → type-check → unit test → build → E2E → deploy.
- Lint and type-check run in parallel for speed.
- Every PR gets a preview deployment for visual review.
- Feature flags default to off. Clean up flag code after full rollout.
- Any deployment can be instantly rolled back.
- Format on save. Format check in CI.
- Dead code detection runs periodically.

## Violations

- Merging code that fails CI checks
- No type-checking in CI (only linting)
- Stale feature flags left in code after rollout
- No rollback capability
- Manual formatting instead of automated
- catch blocks with only console.log (silent error swallowing)
- No AI-targeted lint rules (any, console.log, direct library imports)

## Right vs Wrong

Examples are illustrative.

```
WRONG (minimal CI):
jobs:
  test:
    run: npm test

RIGHT (full pipeline with AI-era gates):
jobs:
  quality:
    - npm run lint          # catches console.log, any, direct imports
    - npm run typecheck     # catches type assertions
    - npm run test          # catches logic errors
    - npm run build         # catches import errors
    - npx bundlesize        # catches bundle bloat
```

```
WRONG (no AI-targeted linting):
// Default ESLint only

RIGHT (rules that catch AI mistakes):
"no-console": "error",
"@typescript-eslint/no-explicit-any": "error",
"@typescript-eslint/no-non-null-assertion": "warn",
"no-restricted-imports": ["error", { "patterns": ["@mui/*"] }]
```

## References.md Section

- CI platform: which one (GitHub Actions, GitLab CI, etc.)
- Pipeline config: where it's defined
- Lint/format config: paths to ESLint and Prettier configs
- Feature flags: which service and how flags are defined
- Deploy command: how to deploy and rollback
