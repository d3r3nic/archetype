# Convention #25: Automated Enforcement

## Principle

Lint rules, formatters, and pre-commit hooks catch convention violations at write time, before code review. Human attention is scarce; automation never tires. A convention without enforcement is a suggestion. Every convention that can be automated should be.

## Reusable System

Apply #0: configure enforcement once at the project level, apply everywhere.
- Linter config: single source of truth, extended by file type
- Formatter config: single source, one formatter per language
- Pre-commit hooks: run linter + formatter + type check before commit lands
- CI gates: block PRs that fail enforcement; merge is impossible with red checks
- Editor integration: format on save, show lint errors inline

## Rules

- Every convention that CAN be automated SHOULD be. If a rule can be a lint rule, make it one.
- Lint rules block commit, not just warn. Warnings get ignored at scale.
- Format on save AND format pre-commit. Do not debate style in code review.
- Pre-commit hooks must be fast enough that nobody is tempted to bypass them; the project sets the budget in References.md. Slow checks run in CI.
- Never bypass hooks with --no-verify except for documented emergencies with a follow-up fix.
- CI gate is the source of truth. If CI passes, the code is green. If CI fails, nothing merges.
- When a convention violation is caught in code review, add a custom lint rule to catch it next time. Do not rely on memory.
- Lint-suppression directives require an inline comment explaining why. CI fails if the count grows beyond a documented baseline.

## Violations

- Convention rules living only in docs with no automated check
- Lint config set to warn-only (developers ignore warnings at scale)
- Format disagreements in code review (should be auto-fixed by formatter)
- Pre-commit hooks so slow that developers bypass them
- CI green but local broken (environment drift, missing checks)
- Scattered suppression comments with no explanation
- Manual style enforcement ("the linter doesn't catch it but please use camelCase")

## Wrong vs Right

- WRONG: "Remember to import from the API layer, not the HTTP client directly" (rule in docs only)
- RIGHT: Custom lint rule flags direct HTTP-client imports, blocks commit
- WRONG: Team debates variable naming in PR reviews
- RIGHT: Linter enforces naming, review focuses on logic and design
- WRONG: suppression directives scattered through the codebase with no context
- RIGHT: Disables require an explanatory comment; CI fails if disables exceed a threshold
- WRONG: "We have a style guide" (PDF or wiki only, never enforced)
- RIGHT: Style guide IS the linter config; everything enforceable is enforced

## Research Notes

Dated notes: anything named in this section is an example from the time of writing and expires. Verify current options at bootstrap.

When bootstrapping this convention, research:
- The native linter for the language, whether it supports custom rules (most do), and its plugin API
- A pre-commit hook framework for the language, or a language-agnostic one
- Format-on-save editor configuration
- The CI platform's ability to block merges on lint/test failure (required status checks, merge queues, or equivalent)
- Existing community rule sets for security and accessibility in the language's ecosystem
- Which conventions from this framework map to enforceable rules for the chosen language — and which ones remain doc-only (note the gap in References.md)

Document in References.md:
- Which linter(s) are configured and where their config lives
- Which conventions are automated vs doc-only (the gap list is valuable — it shows what relies on AI compliance alone)
- How to add a new custom lint rule (the workflow, not a tutorial)
- Which CI check gates merges and how to run it locally

## Project Overrides

If a file exists at conventions/overrides/25-automated-enforcement.md, read it. It contains project-specific rules that extend or refine this base convention. The base convention always applies. The override file adds project-specific detail.
