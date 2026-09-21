# Frontend scaffold: deployment discipline

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 11a: Deployment discipline
Read: #15; #0; #18; scaffolding/_preamble.md § Convention-mapping rule
Produces: one idempotent deploy command chain, recorded in References.md § Commands, that a fresh clone can run
Check: evidence: what was seen when this was tried: the deploy run from a fresh clone reaching a known-working address, and the chain re-run after a failure; a deploy that spends money or reaches customers waits for the owner (#29)

Deployment is where the framework's signals meet the vendor's specifics. The rules below are vendor-agnostic; the template handles the concrete commands.

Build-context and deploy-context ignores:
- The image builder and the deploy-source uploader may be different actors reading different ignore files. Author each actor's ignore surface; do not rely on the image-builder ignore to suppress uploads.
- Dated example: a deploy uploader packed a dev-only test-harness config whose imports had been correctly stripped from the image context, so the remote typecheck failed on a file the image never needed. Exclude such files from BOTH surfaces, not just one.

Local pre-deploy verification:
- Chain local `typecheck → lint → test → build` as a precondition of the deploy command. Never deploy past a local red.
- Remote builds should enforce the same chain so drift between local and remote surfaces fails fast.
- Any error that only surfaces remotely is a sign the local chain is missing a step, not that the remote is "stricter."

Env-schema and example files:
- Schema that rejects empty strings is correct behavior. Example-env files that ship optional keys as blanks are a trap: the consumer copies the file, validation fails on first run, cause is non-obvious.
- In example files, OPTIONAL keys are **commented out**, not set to empty. Comment explains why (the schema rejects empty; uncomment and fill when opting in).
- REQUIRED keys may ship with a safe stub or an obviously-placeholder value that explains the intent.

Ingress, certs, and multi-tenancy:
- Confirm current vendor docs before committing to an ingress/cert path. A vendor's "preview" or "limited GA" feature may have materially worse reliability than their production path. Deprecated-but-available is a trap.
- When placing multiple tenants behind shared ingress, verify the vendor lets its load-balancer backend primitives cross project/account boundaries. If they can't, consolidation into one boundary is forced; choose the multi-tenant boundary by WHO PAYS the vendor bill:
  - Framework consumer pays → consolidate into one platform boundary, attribute cost via labels.
  - End customer pays → each customer gets their own boundary.
- DNS records for shared-ingress setups point to the shared ingress's own address, not to a per-service hostname the vendor assigns.
- When the DNS provider offers a traffic proxy, **verify whether it passes the cert issuer's domain-validation challenge through**. Proxies that terminate or redirect traffic can silently break cert issuance. Default to DNS-only until the cert is live.

IAM and deploy actors:
- Vendor IAM defaults shift across epochs. Projects created in older eras inherited broader defaults; new projects may not. Do not assume inheritance — automation must grant every binding a deploy actor needs, every time. A deploy tool failing with a permission error that names a "default" service agent or account almost always needs that role bound explicitly, because the vendor used to grant it implicitly.

**Verify:** a fresh clone of the project runs the deploy command and a successful deploy reaches a known-working URL without any out-of-band manual steps. The command chain is idempotent: re-running after any failure resumes or replays cleanly.
