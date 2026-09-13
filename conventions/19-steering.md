# Convention #19: AI Steering & Drift Prevention

## Principle

AI agents drift from the intended path without explicit boundaries. Specifications define scope before implementation starts. Plans define approach before code is written. The owner keeps authority over what the product is, who it serves, what it promises, and what it may spend and commit (#29). Who decides technical questions is a declared project setting: under `owner-decides` the owner approves architecture, plans, and foundational changes; under `ai-decides` the AI decides them, records each decision with its reason, and proceeds. The discipline below holds under both.

## Reusable System

Create steering artifacts that the team reuses:
- A specification template for defining features before implementation: what to build, why, acceptance criteria, and explicitly what is out of scope
- A plan template for implementation: which files change, in what order, what approach
- Persistent planning files that survive context resets so AI agents can restore context when starting a new session
- A decision record (#16, #29) that holds every consequential technical decision with its reason and the alternatives rejected, so a later session restores the why, not only the what

## Rules

These hold under both settings:

- Write a specification before complex features. Include an explicit "out of scope" section. Without it, AI explores everything.
- Write a plan before multi-file changes. List the files, the changes, and the sequence.
- One change at a time. Verify between changes. Do not batch multiple changes without verification.
- Do exactly what was asked. Do not refactor surrounding code, add improvements, or clean up files that weren't part of the request. AI does this unprompted.
- Start fresh after two failed corrections. If the AI has failed twice on the same issue and the context is polluted with failed approaches, start a new session with a better prompt incorporating what was learned.
- Clear context between unrelated tasks. Never mix unrelated work in one session.
- Read feature-tree.md before building anything. Check what already exists.

These read the decision-authority setting in PROFILE.md first:

- Plans. Under `owner-decides`, get approval before implementing. Under `ai-decides`, record the plan at the decision location and proceed.
- Competing approaches. Under `owner-decides`, present them with trade-offs and wait for a decision. Under `ai-decides`, choose, record the alternatives rejected and why, proceed, and tell the owner in the session summary.
- Uncertainty. About scope or product intent, ask the owner under both settings; do not guess, do not build something that seems wrong. About a technical question, under `owner-decides` ask; under `ai-decides` research, decide, record.
- Foundational systems. These affect every feature. Under `owner-decides`, never modify one without explicit permission. Under `ai-decides`, never modify one without a recorded decision and the breaking-change protocol below.
- Comprehension. The owner understands what the product does and what it promises; the decision record carries the technical why. Under `owner-decides` the owner also maintains system comprehension and decides what NOT to build. Under `ai-decides` the AI decides what not to build, records it, and the owner hears it as a recommendation when it changes scope.

## Violations

- Starting implementation without a specification or plan for complex features
- Refactoring code adjacent to the requested change ("while I'm here, I'll also...")
- Continuing after multiple failed attempts without starting fresh
- Mixing unrelated tasks in one session (context becomes noisy, quality drops)
- Modifying foundational systems during feature work without permission (owner-decides) or without a recorded decision (ai-decides)
- Guessing at scope or intent instead of asking the owner
- Asking the owner a technical question under `ai-decides`, or deciding one without recording it
- Waiting for approval under `ai-decides` for work that is already within scope
- Adding phantom requirements nobody asked for (batch mode, dry-run, legacy format support)
- Building a feature without reading the feature-tree.md to understand what already exists

## Breaking Change Protocol

When a change will alter an existing component API, shared service interface, or foundational system behavior:

1. Document what exists now, what needs to change, why it needs to change, and what will break.
2. Propose a phased approach:
   - Phase 1: Add the new version alongside the old. Mark the old as deprecated.
   - Phase 2: Migrate all usage from old to new.
   - Phase 3: Remove the old version.
3. Under `owner-decides`, present this to the team and wait for explicit go-ahead before each phase. Under `ai-decides`, record it at the decision location and proceed phase by phase, verifying between phases. A phase that touches a live customer environment is escalated under both settings (#29).

Non-breaking changes (extracting hardcoded values to config, adding missing error handling, fixing imports to use wrappers) can be done immediately while working on a feature. Only changes that alter how OTHER code interacts with a system require the protocol.

## Wrong vs Right

- WRONG: user asks to "add user roles." AI immediately starts writing code across 8 files with no plan.
- RIGHT: user asks to "add user roles." AI first confirms scope with the owner: which roles, what is out of scope. Then it plans where they are enforced (approved under `owner-decides`, recorded under `ai-decides`). Then implements file by file with verification after each.
- WRONG: user asks to "fix the login button color." AI fixes the color, then also refactors the form structure, updates validation, and adds a loading state that wasn't asked for.
- RIGHT: user asks to "fix the login button color." AI fixes the button color, verifies it, done.
- WRONG: a shared component's API needs to change. AI changes the component and breaks 15 features that use it.
- RIGHT: AI documents what needs to change and proposes a phased migration. New API is added alongside old. Features migrate one at a time. Old API removed after all migration is complete.
- WRONG: under `ai-decides`, the AI asks the owner which caching approach to use. RIGHT: it chooses per #9 and #13, records the alternatives, and moves on.
- WRONG: under `owner-decides`, the AI rewrites a foundational system because a plan from last month mentioned it. RIGHT: permission for this change, now.

## Research Notes

Dated notes: anything named in this section is an example from the time of writing and expires. Verify current options at bootstrap.

This convention is about AI collaboration workflow, not framework-specific implementation. Apply these principles to every AI-assisted development session regardless of framework. Ensure:
- Specification and plan templates are available in the project
- The decision-authority setting and the decision location are recorded in PROFILE.md and References.md at bootstrap (#29, #30)
- The team agrees on the plan-before-implement workflow for complex changes
- The team agrees on the breaking change protocol for shared systems
- Feature-tree.md is the first thing read before any work
