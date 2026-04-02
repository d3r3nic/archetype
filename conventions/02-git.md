# Convention #2: Git & Version Control

## Principle

Commits are save points. Each commit represents one verified change that passes all checks. In AI development, commit more frequently than traditional development - after every successful, verified edit. This enables instant rollback when the next change introduces a bug. Commit messages describe what changed and why, serving as history that both humans and AI can trace.

## Reusable System

Create a version control setup that establishes:
- A commit message convention the entire team follows (conventional commits or project standard)
- A branching strategy with clear rules for when to branch and how to name branches
- Pre-commit hooks that automatically run linting, formatting, and type-checking on staged files before every commit
- A pull request template with standard sections so every PR is described consistently

## Rules

- Commit after every successful, verified change. Commits are save points you can rollback to.
- Each commit must pass all checks (lint, type-check, tests). Never commit broken code.
- Commit messages follow the project's convention and describe WHAT changed and WHY.
- Never commit secrets, environment files, or credentials.
- Never force push to the main branch.
- Never skip pre-commit hooks. If a hook fails, fix the issue, don't bypass it.
- Fix files in place. Never create variant files like utils-v2 or helper-new. If something is broken, fix the original file.

## Violations

- Giant commits titled "AI changes" or "update code" covering multiple unrelated changes
- Committing without running verification first
- Committing secrets, .env files, or API keys
- Long-lived branches that drift far from main
- Creating variant files (utils-v2.ts, helper-new.ts) instead of fixing the original
- Using --no-verify to skip failing pre-commit hooks instead of fixing the underlying issue
- Amending published commits that other people are working on

## Wrong vs Right

- WRONG: one commit with 800 changed lines titled "AI changes." Impossible to rollback, impossible to understand.
- RIGHT: ten commits, each 50-80 lines, each with a descriptive message. Each one a rollback point.
- WRONG: pre-commit hook fails because of a lint error. Developer runs commit with --no-verify to skip it.
- RIGHT: pre-commit hook fails. Developer fixes the lint error, stages the fix, commits cleanly.
- WRONG: a function is broken. AI creates utils-v2.ts with the fixed version. Old file stays. Now two files do the same thing.
- RIGHT: a function is broken. AI fixes the function in the original file. One file, one source of truth.

## Research Notes

When bootstrapping this convention:
- Research the framework's recommended commit conventions and any tooling that enforces them (commit linting, changelog generation)
- Research pre-commit hook tooling for the project's language and package manager
- Set up the branching strategy and document it in References.md
- Configure pre-commit hooks to run the project's lint, format, and type-check commands
