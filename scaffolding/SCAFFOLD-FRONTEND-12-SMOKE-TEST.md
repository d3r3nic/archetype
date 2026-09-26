# Frontend scaffold: smoke-test feature (the integration proof)

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 12: Smoke-test feature (the integration proof)
Read: #12; scaffolding/_preamble.md § Convention-mapping rule; scaffolding/RED-FLAGS.md § 11. Scaffold-complete without integration proof
Produces: one minimal feature that goes through every shared system that was built, with its integration test
Check: run project: typecheck, lint, test, build; evidence: the feature's path, and each shared system it goes through
Depends on: scaffold-frontend.4; scaffold-frontend.8; scaffold-frontend.9; scaffold-frontend.10
Basis: decisions and inputs required
Skip by: owner

Build a minimal feature that goes through every shared system that was built. A profile or settings screen is a common choice. It:
- sits behind the guard (Step 7, when built);
- reads through the API layer (Step 6, when built);
- uses the shared state (Step 5, when built);
- renders through the component foundation (Step 4);
- has a form (Step 9, when built);
- has an integration test through the shared setup (Step 10);
- passes the accessibility check.

This is end-to-end integration proof. Without it, scaffold can be "complete" with misconfigured wiring. See `scaffolding/RED-FLAGS.md` "Scaffold-complete without integration proof."

Close on the current direction/context decision basis, with the artifact entry and completed review as inputs. Their Decision basis lines must agree. The review records the tested code revision and capture provenance; a changed basis makes old evidence stale. An unavailable browser leaves the required visual review open.
