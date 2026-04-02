# Convention #19: AI Steering & Drift Prevention

## Principle

AI agents drift from the intended path without explicit boundaries. Specifications define scope before implementation starts. Plans define approach before code is written. Circuit breakers prevent infinite exploration. Humans retain authority over architecture, what NOT to build, and system comprehension.

AI-era reasoning: context exhaustion causes AI to forget earlier decisions. Vague requirements propagate errors across parallel sessions. Without "out of scope" boundaries, AI explores everything. The bottleneck has shifted from generation to verification and comprehension.

## Reusable System

- Spec template: standard format for feature specifications (what, why, scope, out of scope, acceptance criteria)
- Plan template: standard format for implementation plans (files to change, approach, dependencies)
- Task tracking: persistent files that survive context resets

## Rules

- Write a spec before complex features. Include an "Out of Scope" section.
- Write a plan before multi-file changes. List files, changes, and sequence.
- One change at a time. Verify between changes. Do not batch.
- Start fresh after 2 failed corrections on the same issue. Context is polluted.
- /clear between unrelated tasks. Never mix unrelated work in one session.
- Never modify existing foundational systems without explicit permission.
- Present options before implementing. Do not assume the approach.
- Stop and ask when uncertain. Do not guess.
- Do exactly what was asked. Do not refactor adjacent code or add improvements.
- Human decides architecture, scope, and what NOT to build. AI implements.

## Violations

- Starting implementation without understanding the full scope
- Refactoring code adjacent to the requested change
- Continuing after multiple failed attempts without starting fresh
- Mixing unrelated tasks in one session (kitchen sink session)
- Modifying foundational systems while working on a feature
- Implementing beyond what was asked ("while I'm here, I'll also...")
- Guessing when requirements are ambiguous instead of asking

## Right vs Wrong

Examples are illustrative.

```
WRONG (no plan, immediate implementation):
User: "Add user roles"
AI: *starts writing code across 8 files*

RIGHT (spec → plan → implement):
User: "Add user roles"
AI: "Here's my understanding of the scope:
  - What: role field on User, role-based route protection
  - Out of scope: permission matrix, role management UI
  - Files to change: [list]
  - Approach: [brief plan]
  Does this match what you need?"
User: "Yes, go ahead"
AI: *implements file by file, verifying after each*
```

```
WRONG (scope creep):
User: "Fix the login button color"
AI: *fixes color, refactors the form, updates validation, adds loading state*

RIGHT (exactly what was asked):
User: "Fix the login button color"
AI: *fixes the button color, verifies it renders correctly*
```

## References.md Section

- Spec template: link to project's spec template if exists
- Plan format: what plans should include for this project
- Approval process: who approves what (architecture changes, breaking changes, etc.)
