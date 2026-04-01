# Convention #12: Testing Strategy

## Principle

Tests verify behavior, not implementation. They describe what the system does from the user's perspective, serving as executable specifications. Test infrastructure is shared - custom renderers, mock factories, and API mocks are built once and used by all features.

## Reusable System

- Test utilities: custom render wrappers with providers pre-configured
- Test data factories: createUser(), createOrder() for realistic test data
- MSW handlers: shared API mocks for consistent test environments
- Test configuration: shared Jest/Vitest config with project conventions

## Rules

- Test behavior, not implementation. Assert what the user sees, not internal state.
- Arrange-Act-Assert structure for every test.
- Mock at boundaries only (API via MSW, timers, browser APIs). Let real code run.
- Colocate test files next to the code they test.
- Test names describe behavior: "should display error when email is invalid."
- Coverage thresholds on critical paths, not 100% everywhere.
- E2E tests cover business-critical user journeys.
- Use data-testid for stable selectors in E2E.

## Violations

- Testing internal state or function calls instead of rendered output
- Mocking internal modules instead of testing real logic
- Tests that break when refactoring (implementation-coupled)
- No tests on critical business logic
- Custom test setup per feature instead of using shared utilities

## References.md Section

- Test runner: which one and command
- Test utilities: path to shared renderers, factories, MSW setup
- Coverage: thresholds and enforcement
- E2E: framework and where tests live
