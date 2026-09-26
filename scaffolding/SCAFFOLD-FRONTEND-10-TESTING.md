# Frontend scaffold: testing

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 10: Testing
Read: #12; #18; #14; scaffolding/RED-FLAGS.md § 16. Env-inlining breaks runtime env mutation in tests; scaffolding/_preamble.md § Convention-mapping rule
Produces: the test setup, the accessibility check in it, and the test command recorded in References.md § Commands
Check: run project: typecheck, lint, test, build; evidence: what was seen when this was tried: a sample screen tested through the shared setup, and a failing accessibility check failing the test command
Depends on: scaffold-frontend.4; scaffold-frontend.8; scaffold-frontend.9

Apply #12 through the recorded decisions, researching the chosen stack's test tools where the record is silent:
- A test runner that handles the project's module and markup transforms, and an environment that renders screens without a real browser where the stack allows.
- One shared setup that every test uses. It renders through the same root composition the app uses (Step 8), reused rather than copied, so tests never run with a different context than production.
- Fakes at the network boundary, not replacements for the project's own modules.
- Builders for test data.
- An automated accessibility check that runs in the test command and fails it on a violation (#14), exercised by at least one test on a shared component.
- The test data client with retries off: a retry on a failing test request hides the real error.
- Test and production client settings may differ where a feature such as cancellation, backoff or streaming behaves unpredictably against a fake network; keep production behavior in the production settings (RED-FLAGS 16).

**Verify:** a sample screen renders and is tested through the shared setup; an accessibility violation makes the test command fail.
