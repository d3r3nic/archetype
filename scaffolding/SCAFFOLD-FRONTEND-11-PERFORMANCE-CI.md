# Frontend scaffold: performance, build, and CI

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 11: Performance, build, and CI
Read: #13; #15; #25; scaffolding/_preamble.md § Convention-mapping rule; scaffolding/RED-FLAGS.md § 10. Migrations auto-run in CI/deploy
Produces: the checks, the budgets and the build the product needs at its stage, where they run, and the rollback path, recorded in References.md
Check: run project: typecheck, lint, test, build; evidence: what was seen when this was tried: the recorded checks running where they are recorded to run, a change that breaks one failing, and each budget the product set measured

Apply #13 and #15 for this product at its stage (#30), researching the chosen stack's options where the record is silent:
- The project's checks, run where the project recorded they run (Step 1), and failing a change that breaks them.
- Loading and splitting decided from measurement of this product's startup and interactions (#13), not applied everywhere by default.
- A size or performance budget where a regression would matter to the product's people, measured the same way every time, and enforced where a reliable check exists.
- The measurement of real use the product's reliance calls for, once people depend on it.
- A known way back from a release people depend on.

**Verify:** the checks run where recorded and fail a change that breaks one; each budget the project set is measured and its result recorded.
