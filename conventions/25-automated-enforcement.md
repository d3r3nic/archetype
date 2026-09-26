# Convention #25: Automated Enforcement

## Principle

Automate observable checks when their reliability and prevention value justify their maintenance and execution cost. Linters, formatters and hooks can enforce a project's accepted contracts; they cannot establish that every decision is appropriate. Use review and evidence for judgments a script cannot make.

## Reusable System

Apply #0: configure enforcement once at the project level, apply everywhere.
- Linter config: single source of truth, extended by file type
- Formatter config: single source, one formatter per language
- Pre-commit hooks: run linter + formatter + type check before commit lands
- CI gates: block PRs that fail enforcement; merge is impossible with red checks
- Editor integration: format on save, show lint errors inline

## Rules

- Select checks for real recurring risks or accepted project contracts. A rule being expressible as a heuristic does not establish that the heuristic is accurate or worth maintaining.
- Lint rules block commit, not just warn. Warnings get ignored at scale.
- Format on save AND format pre-commit. Do not debate style in code review.
- Pre-commit hooks must be fast enough that nobody is tempted to bypass them; the project sets the budget in References.md. Slow checks run in CI.
- Never bypass hooks with --no-verify except for documented emergencies with a follow-up fix.
- Required CI checks must pass before merge. A pass establishes only what those checks exercised; verify the intended behavior and review gaps independently. Investigate an incorrect check against the accepted contract rather than bypassing it.
- When review finds a defect, assess whether a regression test, static check, clearer guidance or another correction best prevents recurrence. Add a custom rule only when it can check the condition reliably at justified cost.
- Lint-suppression directives require an inline comment explaining why. CI fails if the count grows beyond a documented baseline.

## Violations

- A recurring observable failure left without a justified prevention or detection approach
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
- RIGHT: The selected style contract has reliable automated checks; judgment-dependent guidance remains explicit and reviewed.

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

If a file exists at conventions/overrides/25-automated-enforcement.md, read it. It holds this project's own rules for this concern: the detail it adds, and where it departs from this convention and why. Where the two differ, the recorded project choice governs, within the owner's decisions, the floor and the obligations the project's facts add (#30).
