# Frontend scaffold: performance, build, and ci

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 11: Performance, build, and CI
Read: #13; #15; #25; scaffolding/_preamble.md § Convention-mapping rule; scaffolding/RED-FLAGS.md § 10. Migrations auto-run in CI/deploy
Produces: the budgets, the build, the pipeline, and the measurements the conventions name
Check: run project: typecheck, lint, test, build; evidence: what was seen when this was tried: a change pushed over the bundle budget, and the vitals collected on a staging build

Build:
- Code splitting: route-based + component-based for heavy dependencies.
- Bundle size budget enforced in CI.
- Web Vitals monitoring wired in for production.
- CI pipeline: lint → typecheck → test → a11y → build → bundle-size-check → deploy.
- Preview deployments per PR.
- Rollback path documented.

**Verify:** a PR that pushes bundle over budget fails CI. Web Vitals collection works on a staging build.
