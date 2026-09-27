# Convention #19: AI Steering & Drift Prevention

## Applies when

Every session that changes the project. What varies is who decides technical questions, a setting in PROFILE.md: under `owner-decides` the owner approves architecture, plans and foundational changes; under `ai-decides` the AI decides them, records each decision with its reason, and proceeds. The owner keeps authority over what the product is, who it serves, what it promises, and what it may spend and commit under both settings (#29).

## Principle

Do what was asked, completely, and nothing that was not. Know the scope before building, plan in proportion to the risk, verify as you go, and keep every change inside the authority the project granted. Drift, whether unrequested features, silent refactors or a changed interface nobody agreed to, is a defect even when it works.

## Reusable System

The steering records: the scope of the current work with what is out of it, the plan where the work needs one, and the decision record (#16, #29) that holds each consequential technical choice with its reason and rejected alternatives. They live in the project's files, so a later session restores the why and not only the what (#17).

## Rules

These hold under both settings:

- Know the scope before building. For work larger than an obvious edit, write down what is in it, what is out of it, and what done looks like.
- Plan in proportion to uncertainty, coupling and consequence: an obvious local fix needs only the change and its check; a change across several parts needs its sequence, affected consumers and checks written down.
- Verify at each coherent step, not only at the end (#18).
- Do exactly what was asked. Do not refactor nearby code, add improvements or clean up files outside the request; propose them separately.
- Add no requirements nobody asked for: extra modes, formats, options or compatibility layers.
- Read what exists before building: feature-tree.md, the relevant code and the shared systems (#0).

These read the decision-authority setting in PROFILE.md first:

- Plans. Under `owner-decides`, get approval before implementing. Under `ai-decides`, record the plan at the decision location and proceed.
- Competing approaches. Under `owner-decides`, present them with their trade-offs and wait. Under `ai-decides`, choose, record the rejected alternatives and why, proceed, and tell the owner in the session summary.
- Uncertainty. About scope or product intent, ask the owner under both settings; never guess and never build something that seems wrong. About a technical question, ask under `owner-decides`; research, decide and record under `ai-decides`.
- Foundational systems. Under `owner-decides`, change one only with the owner's permission. Under `ai-decides`, change one only with a recorded decision, and follow the protocol below when other code depends on it.
- What not to build. Under `owner-decides` the owner decides. Under `ai-decides` the AI decides, records it, and tells the owner as a recommendation when it changes scope.

## Changing an interface others depend on

When a change alters how other code uses a component, a shared service, a contract or a foundational system:

1. Record what exists now, what must change and why, and what depends on it.
2. Keep every dependant working. With one or two callers in the same change, update them together and verify. With many callers, other teams, or released consumers, add the new version beside the old, move the users, verify between moves, then remove the old version (#2).
3. Under `owner-decides`, get the owner's go-ahead before each phase. Under `ai-decides`, record the plan and proceed phase by phase. A phase that touches a live customer environment is escalated under both settings (#29).

A change that does not alter how other code uses the system (moving a value into configuration, adding missing error handling, routing an import through its owner) needs no protocol.

## Violations

- Building before the scope is known.
- "While I was here" changes outside the request.
- Features, modes or options nobody asked for.
- A shared interface changed with its dependants left broken.
- A foundational change made without permission (`owner-decides`) or without a recorded decision (`ai-decides`).
- Guessing at product intent instead of asking.
- Asking the owner a technical question under `ai-decides`, or deciding one without recording it.
- Waiting for approval under `ai-decides` for work already in scope.

## Wrong vs Right

- WRONG: asked to "add user roles", the AI starts editing eight files. RIGHT: it confirms which roles and what is out of scope, plans where roles are enforced (approved or recorded, per the setting), then builds and verifies step by step.
- WRONG: asked to fix a button's color, the AI also restructures the form and adds a loading state. RIGHT: it fixes the color, verifies it, and mentions anything else it noticed.
- WRONG: a shared component's interface changes and fifteen screens break. RIGHT: the dependants are known first; they are moved over and verified, then the old interface is removed.
- WRONG: a one-caller helper in a prototype gets a deprecation period and a migration plan. RIGHT: the helper and its one caller change together in one verified commit.
- WRONG: under `ai-decides`, the AI asks the owner which caching approach to use. RIGHT: it chooses under #9 and #13, records the alternatives, and moves on.

## Research Notes

Research whether the team already has scope, plan or change-management practices worth keeping, and adopt them rather than adding a second set. Record the decision-authority setting and the decision location at bootstrap (PROFILE.md, References.md; #29, #30).
