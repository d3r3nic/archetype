# Convention #12: Testing Strategy

## Principle

Tests verify behavior, not implementation. They describe what the system does from the user's perspective, serving as executable specifications. Test infrastructure is a reusable system - custom renderers, mock factories, and API mocks are built once and shared by all features. Tests that break when you refactor are testing the wrong thing.

## Reusable System

Create a test infrastructure that establishes:
- A custom test renderer pre-configured with all the project's providers, contexts, and wrappers. Every test uses this shared renderer instead of setting up providers manually.
- Test data factories that generate realistic test data for each entity in the project. Factories are composable and configurable.
- API mock setup that intercepts HTTP requests at the network level (not by mocking internal modules). Mocks return realistic responses and can simulate errors, delays, and edge cases.
- A consistent test file organization: test files colocated next to the code they test.

## Rules

- Test behavior, not implementation. Assert what the user sees or what the system outputs, not internal state variables or function call counts.
- Mock at boundaries only. Mock the network layer (HTTP requests) and external services. Let everything between the entry point and the boundary run as real code.
- Tests must survive refactoring. If you rename an internal variable or restructure a function without changing behavior, zero tests should break. If they break, they're testing implementation, not behavior.
- Colocate test files next to the code they test. Not in a separate /tests directory.
- Use the shared test renderer, factories, and mocks. Never set up providers or create mock data from scratch in individual test files.
- Test names describe behavior: "displays error message when email is invalid." Not "test1" or "should work."
- Coverage thresholds on critical business paths, not 100% on everything. Focus testing effort where bugs matter most.
- End-to-end tests cover the most critical user journeys: authentication, primary workflows, payment flows.

## Violations

- Tests that assert on internal state variables, function call counts, or implementation details
- Mocking internal modules instead of testing real code paths (mocking the service you're testing)
- Tests that break when you refactor without changing behavior (implementation-coupled tests)
- Custom test setup in every test file (each file configures its own providers and mock data)
- Testing framework guarantees (asserting that the framework renders a div, or that state updates work)
- No tests on critical business logic

## Wrong vs Right

- WRONG: a test asserts that a specific internal function was called with specific arguments. Refactor the function name and the test breaks, even though the behavior is identical.
- RIGHT: a test asserts that after submitting a form, a success message appears on screen. The form can be refactored any way you want and the test still passes as long as the success message shows up.
- WRONG: a test mocks the user service, the auth module, the format utility, and the API client. Every dependency is fake. The test verifies that mocks were called correctly. You're testing your mocks, not your code.
- RIGHT: a test uses the network-level API mock to simulate a realistic API response. Everything between the UI and the network layer runs as real code. The test verifies what the user actually sees.
- WRONG: each test file manually configures providers, creates its own mock data, and sets up its own API mocks. Fifty test files, fifty slightly different setups.
- RIGHT: all tests use the shared renderer, shared factories, and shared API mock handlers. Setup is consistent. Adding a new provider means changing one file.

## Research Notes

When bootstrapping this convention:
- Research the framework's recommended testing libraries and test runner
- Research network-level API mocking tools for the framework (tools that intercept HTTP requests, not module-level mocks)
- Research test data factory patterns and libraries for the language
- Research the framework's custom renderer pattern (how to wrap the renderer with project providers)
- Research end-to-end testing tools for the framework
- Document the test setup, shared utilities, mock configuration, and coverage thresholds in References.md
