# Session Review

Run after every 3-5 AI coding sessions, or after any session where something went notably wrong or right. Store completed reviews in `docs/reviews/YYYY-MM-DD-topic.md`.

The goal is not perfection. The goal is to catch drift between what the framework prescribes and what the AI actually does, so the framework can evolve.

## Session Info

- Date:
- Duration:
- Task(s) completed:
- Conventions that should have applied:
- AI tool and model used:

## Review Questions

### 1. Did the AI read the conventions it should have?

Evidence: look for "Reading conventions X, Y" or similar statements. If the AI skipped the workflow gate, note which task type triggered it.

Answer:

### 2. Did the AI violate any enforcement rule?

Examples: hardcoded values, direct library imports, scattered error handling, ad-hoc API calls, skipped verification, uncommitted work, modified CLAUDE.md without permission.

Answer:

### 3. Did any convention's wording cause confusion?

Which convention, what was unclear, what would clarify it?

Answer:

### 4. Did the AI try to modify enforcement files without permission?

CLAUDE.md, Conventions.md, convention docs. If yes, which file and what did it try to change?

Answer:

### 5. Did the lookup table route to the right conventions?

For each task the AI picked up, did Conventions.md's task-type table point at the right rows? What task types are missing?

Answer:

## Drift

Count and describe every drift incident (AI doing something the framework would prohibit or recommend against):

- Drift #1: what the AI did | what it should have done | convention missed
- Drift #2:

## What went right

Worth preserving explicitly — not just what broke.

-

## Action Items

Concrete changes to make to the framework:

- [ ] Update convention #X wording: [what and why]
- [ ] Add lookup table row for task type: [which]
- [ ] Add CLAUDE.md rule: [what]
- [ ] Add hook: [trigger + action]
- [ ] Other:

## Suggested Convention Improvements

Free-form notes. Anything from "this sentence is unclear" to "we might need a new convention for X."

-
