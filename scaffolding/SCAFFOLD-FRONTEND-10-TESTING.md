# Frontend scaffold: testing

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 10: Testing
Read: #12; #18; scaffolding/RED-FLAGS.md § 16. Env-inlining breaks runtime env mutation in tests; scaffolding/_preamble.md § Convention-mapping rule
Produces: the test setup, the accessibility check in it, and the test command recorded in References.md § Commands
Check: run project: typecheck, lint, test, build; evidence: what was seen when this was tried: a sample component rendered through its wrapper, and a failing accessibility test blocking the change
Depends on: scaffold-frontend.4; scaffold-frontend.8; scaffold-frontend.9

**Wiring shape** (tools per stack — research current best):
- A test runner that handles the project's module system + JSX/TSX transform.
- A DOM environment (headless) so component tests run without a real browser.
- A testing library whose assertions describe what the user sees, not implementation details.
- A global setup file that registers DOM matchers (auto-importable so each test file doesn't repeat setup).
- A network-level mocker (not module-level mocks) for tests that cross the API boundary.
- In monorepos, each package gets its own test config; packages with no DOM concerns use a plain runtime environment; packages with component concerns use a DOM environment.


Build:
- Test runner configured.
- Custom render wrapper providing Theme + Store + Router + server-state provider + AuthProvider + ErrorBoundary: mirror the production order from Step 8 exactly.
- Network-level API mocking (the stack's current interceptor-based mocker, not module mocks).
- Test data factories.
- Accessibility testing wired in (an automated a11y rule engine) to catch a11y regressions. At least one test on a wrapped component runs it.
- **Test network-layer client has retries disabled.** Retries on failing test fetches mask real errors. Research current test-config pattern for the chosen data-fetching library.
- **Test and production client configs can differ.** Some library features (abort signals, exponential backoff, streaming) interact unpredictably with mocked networks or test DOMs. Keep production semantics in the prod client; diverge for tests as needed. See `scaffolding/RED-FLAGS.md` #16 (env-inlining trap).

**Verify:** render a sample component through the wrapper. A failing a11y test blocks the PR.
