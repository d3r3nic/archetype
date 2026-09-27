# Frontend scaffold: deployment discipline

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 11a: Deployment discipline
Read: #15; #0; #18; scaffolding/_preamble.md § Convention-mapping rule
Produces: one idempotent deploy command chain, recorded in References.md § Commands, that a fresh clone can run
Check: evidence: what was seen when this was tried: the deploy run from a fresh clone reaching a known-working address, and the chain re-run after a failure; a deploy that spends money or reaches customers waits for the owner (#29)
Skip when: the product is not deployed yet: a local tool, or an isolated stage that deferred deployment with its trigger (#30)

The rules below hold on any hosting; the project records its own commands.

Build and upload boundaries:
- The builder and the uploader may read different ignore files. Write each one's exclusions; do not rely on the builder's to keep files out of the upload. A development-only file excluded from the build can still be uploaded and fail a remote check.

Local chain before deploy:
- The deploy command runs the project's checks first and stops on a failure. Never deploy past a local failure.
- The remote build runs the same checks, so the two cannot drift. An error that only appears remotely means the local chain is missing a step.

Example configuration files:
- When the configuration owner rejects empty values, an example file with optional values left blank fails on first run for whoever copies it. Leave optional values commented out, with a note on when to fill them; give required values an obvious placeholder.

Hosting facts to verify, never assume:
- Read the hosting provider's current documentation before committing to an ingress or certificate path; preview features can be materially less reliable than the provider's main path.
- Grant every permission the deploy needs explicitly. Default permissions differ between a provider's older and newer projects, so automation must not rely on them.
- When several tenants share one entry point, check whether the provider lets it route across account or project boundaries, and choose the tenant boundary from who is billed and who must be isolated.
- A traffic proxy in front of a domain can break the certificate issuer's domain check. Keep the proxy off until the certificate is live.

**Verify:** a fresh clone runs the deploy command and reaches a known-working address with no manual step outside the chain; re-running the chain after a failure resumes or replays cleanly.
