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
- Mocking everything instead of testing real logic (you end up testing your mocks)
- Tests that break when refactoring (implementation-coupled)
- No tests on critical business logic
- Custom test setup per feature instead of using shared utilities
- Testing the framework (asserting React renders a div, or useState works)

## Right vs Wrong

Examples are illustrative.

```
WRONG (testing implementation details):
test('should call fetchUsers on mount', () => {
  const spy = jest.spyOn(api, 'fetchUsers');
  render(<UserList />);
  expect(spy).toHaveBeenCalledTimes(1);
});

RIGHT (testing behavior - what the user sees):
test('should display user names after loading', async () => {
  render(<UserList />);
  expect(await screen.findByText('Alice Johnson')).toBeInTheDocument();
});
```

```
WRONG (mock everything, test nothing):
jest.mock('@/services/userService');
jest.mock('@/hooks/useAuth');
jest.mock('@/utils/format');
jest.mock('@/api/client');
// You're testing that mocks return what you told them to

RIGHT (mock at boundaries only - MSW for API):
const server = setupServer(
  rest.post('/api/users', (req, res, ctx) =>
    res(ctx.json({ data: { id: '1', name: req.body.name } }))
  )
);
test('creates user and shows success', async () => {
  render(<CreateUserForm />);
  await userEvent.type(screen.getByLabelText('Name'), 'Alice');
  await userEvent.click(screen.getByRole('button', { name: 'Create' }));
  expect(await screen.findByText('User created')).toBeInTheDocument();
});
```

## References.md Section

- Test runner: which one and command
- Test utilities: path to shared renderers, factories, MSW setup
- Coverage: thresholds and enforcement
- E2E: framework and where tests live
