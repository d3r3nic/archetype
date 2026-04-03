# Convention #19: AI Steering & Drift Prevention

## Principle

AI agents drift from the intended path without explicit boundaries. Specifications define scope before implementation starts. Plans define approach before code is written. The human retains authority over architecture, scope, and what NOT to build. AI implements, the human steers. Short iterations with frequent verification prevent drift better than long autonomous runs.

## Reusable System

Create steering artifacts that the team reuses:
- A specification template for defining features before implementation: what to build, why, acceptance criteria, and explicitly what is out of scope
- A plan template for implementation: which files change, in what order, what approach
- Persistent planning files that survive context resets so AI agents can restore context when starting a new session

## Rules

- Write a specification before complex features. Include an explicit "out of scope" section. Without it, AI explores everything.
- Write a plan before multi-file changes. List the files, the changes, and the sequence. Get approval before implementing.
- One change at a time. Verify between changes. Do not batch multiple changes without verification.
- Do exactly what was asked. Do not refactor surrounding code, add improvements, or clean up files that weren't part of the request. AI does this at 80-90% frequency.
- Present options before implementing. When there are multiple approaches, present them with trade-offs and wait for a decision.
- Stop and ask when uncertain. If a requirement is ambiguous or something doesn't make sense, ask. Do not guess. Do not build something that seems wrong.
- Never modify existing foundational systems without explicit permission. These systems affect every feature in the project.
- Start fresh after two failed corrections. If the AI has failed twice on the same issue and the context is polluted with failed approaches, start a new session with a better prompt incorporating what was learned.
- Clear context between unrelated tasks. Never mix unrelated work in one session.
- The human decides architecture, decides what NOT to build, and maintains system comprehension. The AI generates code. Understanding is the human's job.

## Violations

- Starting implementation without a specification or plan for complex features
- Refactoring code adjacent to the requested change ("while I'm here, I'll also...")
- Continuing after multiple failed attempts without starting fresh
- Mixing unrelated tasks in one session (context becomes noisy, quality drops)
- Modifying foundational systems during feature work without permission
- Guessing when requirements are ambiguous instead of asking
- Adding phantom requirements nobody asked for (batch mode, dry-run, legacy format support)
- Building a feature without reading the feature-tree.md to understand what already exists

## Breaking Change Protocol

When a change will alter an existing component API, shared service interface, or foundational system behavior:

1. Do NOT make the breaking change without explicit approval.
2. Document what exists now, what needs to change, why it needs to change, and what will break.
3. Propose a phased approach:
   - Phase 1: Add the new version alongside the old. Mark the old as deprecated.
   - Phase 2: Migrate all usage from old to new.
   - Phase 3: Remove the old version.
4. Present this to the team and wait for explicit go-ahead before starting any phase.

Non-breaking changes (extracting hardcoded values to config, adding missing error handling, fixing imports to use wrappers) can be done immediately while working on a feature. Only changes that alter how OTHER code interacts with a system require the protocol.

## Wrong vs Right

- WRONG: user asks to "add user roles." AI immediately starts writing code across 8 files with no plan.
- RIGHT: user asks to "add user roles." AI first confirms scope: what roles, where they're enforced, what's out of scope. Then proposes a plan. Then implements file by file with verification after each.
- WRONG: user asks to "fix the login button color." AI fixes the color, then also refactors the form structure, updates validation, and adds a loading state that wasn't asked for.
- RIGHT: user asks to "fix the login button color." AI fixes the button color, verifies it, done.
- WRONG: a shared component's API needs to change. AI changes the component and breaks 15 features that use it.
- RIGHT: AI documents what needs to change and proposes a phased migration. New API is added alongside old. Features migrate one at a time. Old API removed after all migration is complete.

## Research Notes

This convention is about AI collaboration workflow, not framework-specific implementation. Apply these principles to every AI-assisted development session regardless of framework. Ensure:
- Specification and plan templates are available in the project
- The team agrees on the plan-before-implement workflow for complex changes
- The team agrees on the breaking change protocol for shared systems
- Feature-tree.md is the first thing read before any work
