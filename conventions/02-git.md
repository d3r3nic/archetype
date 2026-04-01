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

## References.md Section

- Commit format: project's commit convention
- Branch naming: convention for branch names
- Pre-commit: what hooks run and how they're configured
