# Convention #18: Verification-Driven Development

## Principle

Code is not done until it is verified. Every change is followed by a verification step - running tests, building, type-checking, or visually confirming UI. Tests are written before implementation, serving as executable specifications that the AI implements against. Verification is the bottleneck in AI development, not generation.

AI-era reasoning: this is the single highest-leverage practice for AI-assisted development. Without verification loops, AI produces plausible-looking code that is fundamentally wrong. TDD prevents the failure mode where AI writes tests that confirm broken behavior - when tests exist before code, AI cannot cheat.

## Reusable System

- Test utilities: custom render wrappers, mock factories, test data builders
- MSW handlers: mock API responses for consistent test environments
- Build gate: hook or script that blocks completion until verification passes
- Visual verification: screenshot comparison setup for UI changes

## Rules

- Write failing tests BEFORE asking AI to implement.
- Run tests after every significant change. Not at the end. After every change.
- Build verification is a hard gate. Work is not complete until the build passes.
- Type-check is part of verification. `tsc --noEmit` must pass.
- For UI changes, describe or screenshot what the result looks like.
- Test behavior, not implementation. Assert what the user sees, not internal state.
- Mock at boundaries only (API, timers, browser APIs). Let real code run.
- If no test exists for the code being changed, write one first.

## Violations

- Implementing a feature without any tests
- Writing tests after implementation (tests may just confirm broken behavior)
- Skipping test run after changes ("I'll test at the end")
- Calling work done without running the build
- Tests that test implementation details (internal state, function calls) instead of behavior
- Mocking everything instead of testing real logic

## Right vs Wrong

```
WRONG (implement first, test maybe later):
1. AI writes feature code
2. "Looks good"
3. Ship it
4. (bugs found in production)

RIGHT (verify at every step):
1. Write failing test for the expected behavior
2. AI implements code
3. Run test → fails? Fix. Passes? Next test.
4. Run full build + type-check
5. For UI: verify visual output
6. All green → done
```

```
WRONG (testing implementation):
test('calls setUsers with API response', () => {
  expect(setUsers).toHaveBeenCalledWith(mockData)
})

RIGHT (testing behavior):
test('displays user list after loading', async () => {
  render(<UserList />)
  expect(await screen.findByText('John Doe')).toBeInTheDocument()
})
```

## References.md Section

- Test command: exact command to run tests
- Type-check command: exact command to run type checker
- Build command: exact command to verify build
- Test utilities: path to custom render, factories, MSW setup
- Coverage: thresholds and which paths are critical
