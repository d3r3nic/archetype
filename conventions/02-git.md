# Convention #2: Git & Version Control

## Principle

Commits are save points. Each commit represents one verified change that passes all checks. In AI development, commit more frequently - after every successful edit. This enables rollback when the next AI change introduces bugs. Commit messages describe what changed and why, serving as history that both humans and AI can trace.

## Reusable System

- Commit convention: agreed format (conventional commits or project standard)
- Branch strategy: agreed branching model
- Pre-commit hooks: automated lint, format, type-check on staged files
- PR template: standard sections for pull request descriptions

## Rules

- Commit after every successful, verified change. Commits are save points.
- Each commit passes all checks (lint, type-check, tests).
- Commit messages follow the project's convention (e.g., feat:, fix:, chore:).
- Never commit secrets, .env files, or credentials.
- Never force push to main/master.
- Never skip pre-commit hooks.

## Violations

- Giant commits titled "AI changes" or "update code"
- Committing without running verification
- Committing .env files or API keys
- Long-lived branches that drift far from main
- Creating variant files (utils-v2.ts, helper-new.ts) instead of fixing the original
- Using --no-verify to skip failing hooks instead of fixing the issue

## Right vs Wrong

Examples are illustrative.

```
WRONG (AI mega-commit):
git commit -m "AI changes"
git commit -m "update code"
git commit -m "fix everything"

RIGHT (granular save points):
git commit -m "feat(auth): add JWT token refresh on 401"
git commit -m "test(auth): add token refresh integration tests"
git commit -m "fix(auth): handle concurrent refresh race condition"
```

```
WRONG (variant files when stuck):
utils.ts → utils-v2.ts → utils-new.ts → helpers-fixed.ts

RIGHT (fix in place):
# Fix the existing file, test, commit
git diff utils.ts   # understand what changed
# fix, test, commit
```

```
WRONG (skip hooks):
git commit --no-verify -m "fix lint later"

RIGHT (fix the issue):
npm run lint -- --fix
git add .
git commit -m "fix(auth): resolve ESLint import order"
```

## References.md Section

- Commit format: project's commit convention
- Branch naming: convention for branch names
- Pre-commit: what hooks run and how they're configured
