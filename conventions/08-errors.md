# Convention #8: Error Handling, Recovery & Async

## Applies when

Every project. What varies is who meets an error and how: a person looking at a screen, a program calling an API, an operator reading a command's output, a job running unattended. Waiting states apply where people wait for work that takes time.

## Principle

No error is swallowed: each one is either handled where something useful can be done about it, or passed to the one error system that classifies, records and reports it. People see words they can act on; the details go to the logs. Every wait has a visible state, and an empty result is not an error.

## Reusable System

One error system per boundary where errors surface: the place that classifies errors, records them with their context, reports them where the project watches, and turns them into what the person or caller sees. Where people wait, the shared waiting, error, empty and offline states are components every screen reuses (#4). References.md records the error system's location and how features use it; § Boundaries keeps features from inventing their own reporting.

## Rules

- A feature handles the errors it can do something about, such as a field error or a conflict, and passes everything else to the error system. It never invents its own reporting, wording or retry.
- Never swallow an error. A catch that only prints is not handling it.
- Tell people what happened and what they can do, in the product's words (#31). Keep stack traces, codes and internal details out of what people see.
- Every operation people wait for shows its waiting, error and success states; nobody is left looking at nothing.
- Keep empty distinct from failed: "no results" is not an error.
- Retry only what is transient and safe to repeat, with a limit, then show the error with a way to try again. Never retry an operation that may have taken effect unless it is idempotent (B5).
- Cancel or ignore work whose result nobody will see, so a late result cannot overwrite current state.
- Verify that the project's error types behave on the real build target; some targets break type checks on custom error classes. Record any fix in References.md.

## Violations

- Each feature handling, wording and reporting errors its own way.
- A screen with its own spinner or error message instead of the shared states.
- An error caught and only printed.
- Stack traces or internal codes shown to people.
- A wait with no visible state.
- An empty result shown as a failure, or a failure shown as empty.
- A payment or message retried blindly after a timeout.

## Wrong vs Right

- WRONG: three features show errors three ways: an alert, a printed line, a silent flag. RIGHT: all three pass errors to the one error system; each handles only what it can fix.
- WRONG: a validation error from the server becomes "Something went wrong". RIGHT: the error system maps it back to the field that caused it.
- WRONG: a skeleton, a spinner and a blank area for the same kind of wait on three screens. RIGHT: one set of shared waiting states, configured per context.

## Research Notes

Research how the chosen stack catches errors at each level (the whole application, a route or screen, a single operation), how it cancels work, how it represents waiting states, and which reporting service fits the project's scale and cost. Record the error system, its classes and how features use it in References.md.
