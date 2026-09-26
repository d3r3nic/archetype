# Convention #12: Testing Strategy

## Applies when

Every project with behavior worth keeping. What varies: what the product's behavior is (screens, an API, a library, a job, a simulation), where its outer boundaries are (a network, a clock, files, other services, a device), and how much risk a failure carries (#30).

## Principle

Tests verify behavior, not implementation: what a person sees, what a caller receives, what the system records. They survive refactoring and fail when behavior breaks. Test infrastructure is shared like any other system: setup, data builders and fakes are built once and reused by every test. Effort goes where a bug would hurt most.

## Reusable System

The project's test setup: the runner and commands, the shared setup every test uses, builders for test data, fakes for the outer boundaries, and the isolation strategy that keeps tests independent. References.md records them, the test location the project chose, and the critical journeys covered end to end.

## Rules

- Assert behavior: output, visible state, recorded effects. Do not assert internal variables or how often an internal function was called.
- Fake only the outer boundaries: the network, the clock, outside services, hardware. Everything between the entry point and that boundary runs as real code.
- A refactor that keeps behavior breaks no test. When one breaks, it was testing implementation.
- Use the shared setup, builders and fakes. A test file does not build its own copy of them.
- Keep tests independent. Shared data never makes a result depend on the order tests run in (development/RED-FLAGS.md).
- Name a test for the behavior it checks.
- Put the most testing where failure is most costly: money, permissions, data integrity, the main journeys. Cover those journeys end to end.

## Violations

- Tests that assert internal state or call counts.
- Faking the very module under test, so the test checks its own fakes.
- Tests that break on a refactor that kept behavior.
- Every test file with its own setup and data.
- Tests that pass alone and fail together.
- No test on the logic where a bug costs the most.

## Wrong vs Right

- WRONG: a test checks that an internal function was called with certain arguments; renaming the function breaks it. RIGHT: a test submits the form and checks that the confirmation appears; any refactor that keeps that behavior passes.
- WRONG: a test fakes the service, the formatter and the client it is supposed to exercise. RIGHT: the test fakes only the network response and lets everything else run.
- WRONG: fifty test files, fifty slightly different setups. RIGHT: one shared setup; adding a new piece of context changes one file.

## Research Notes

Research the chosen stack's test runners, its ways to fake network and time at the boundary, test data builders, end-to-end tools for the product's platforms, and isolation for any shared store. Record the setup, the commands, the isolation strategy and the covered journeys in References.md.
