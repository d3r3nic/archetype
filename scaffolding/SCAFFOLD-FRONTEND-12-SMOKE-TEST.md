# Frontend scaffold: smoke-test feature (the integration proof)

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 12: Smoke-test feature (the integration proof)
Read: #12; scaffolding/_preamble.md § Convention-mapping rule; scaffolding/RED-FLAGS.md § 11. Scaffold-complete without integration proof
Produces: one minimal feature that goes through every shared system that was built, with its integration test
Check: run project: typecheck, lint, test, build; evidence: the feature's path, and each shared system it goes through
Depends on: scaffold-frontend.4; scaffold-frontend.8; scaffold-frontend.9; scaffold-frontend.10
Basis: decisions and inputs required

Build a minimal feature that exercises EVERY shared system. Typical choice: a `/profile` or `/settings` page that:
- Auth-protected (Step 7)
- Fetches from API (Step 6)
- Uses state management (Step 5)
- Renders through the component foundation (Step 4)
- Has a form (Step 9 if present)
- Has an integration test (Step 10)
- Passes a11y checks

This is end-to-end integration proof. Without it, scaffold can be "complete" with misconfigured wiring. See `scaffolding/RED-FLAGS.md` "Scaffold-complete without integration proof."

Close on the current direction/context decision basis, with the artifact entry and completed review as inputs. Their Decision basis lines must agree. The review records the tested code revision and capture provenance; a changed basis makes old evidence stale. An unavailable browser leaves the required visual review open.
