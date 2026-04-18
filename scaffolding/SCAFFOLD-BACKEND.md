# Scaffold — Backend

Routed from `scaffolding/SCAFFOLD.md` when the project is a backend service (API, worker, service, GraphQL server, gRPC, etc.). The steps below are ordered so each system can be built and verified before the next depends on it.

**Zero-stale rule:** every tooling decision below is research-at-scaffold-time. Linters, frameworks, observability vendors, SAML providers, cloud services — look up the current market leaders for the chosen language/stack when you read the convention doc's Research Notes. Do not treat a specific vendor named here (if any) as THE answer.

**Convention mapping rule:** every step names the conventions it implements. Read those convention docs before building — they contain the principles + research triggers.

## Step 0 — Handoff check (read before building anything)

Read `References.md` in full. Specifically:
- **Compliance section** — is there a regulated-data regime? If yes, the audit-log system (Step 9) is REQUIRED, not optional.
- **Foundational Systems list** — inventory EVERY system listed. Missed systems = silently skipped systems. Compare against the steps below; any system in References.md that doesn't map to a step is a project-specific extension to be built alongside its nearest sibling.
- **Open pre-production gates** in `VERSION-LOG.md` — halt scaffolding until gates resolved (per `bootstrap/RED-FLAGS.md` deploy-gate).

Before each later step, also re-read the convention(s) named in that step.

## Step 1 — Project setup + environment validation

Conventions: #1 (project setup), #7 (types), #2 (git).

Build:
- Language/runtime version pinned (`.nvmrc`, `.tool-versions`, `pyproject.toml`, `go.mod`, etc.).
- Package manager chosen + lockfile committed.
- `tsconfig` / `pyproject` / equivalent in strict mode.
- Linter + formatter configs.
- `.gitignore` for the stack.
- Pre-commit hooks (commit via shared hook framework for the language).
- **Environment validation at STARTUP (not runtime).** `loadEnv()` or equivalent called from `main()` before any service start. Fails loudly on missing/malformed env. See `bootstrap/RED-FLAGS.md` "Env validation at runtime" risk.
- Barrel exports for cross-module imports.

**Verify:** `<pkg-manager> install` succeeds, typechecker runs clean on empty project, linter runs clean, pre-commit hook fires on a test commit, `loadEnv()` throws if you delete a required env var.

## Step 2 — Types foundation

Conventions: #7 (types).

Build:
- Shared type-exports directory for cross-feature types.
- Branded ID types (`UserId`, `OrgId`, etc.) to prevent type confusion at compile time.
- Validation library wired in (the language's current Zod-equivalent).
- Pattern: one schema definition produces both the runtime validator AND the type. No drift between validated input and typed code.

**Verify:** a type-confusion test (passing a `UserId` where an `OrgId` is required) fails to compile. Valid input parses cleanly; invalid input errors with field-level messages.

## Step 3 — Error handling

Conventions: #8 (errors).

Build:
- AppError base class + subclasses (ValidationError, AuthError, NotFoundError, ConflictError, RateLimitError, ExternalServiceError, InternalError — adjust to project domain).
- Error middleware / global handler that maps AppError subclasses to HTTP status codes + machine-readable error codes.
- If GraphQL: error formatter plugin that maps AppError → `errors[].extensions.code`.
- Unit tests on the hierarchy + mapping.

**Verify:** unit tests pass. A `throw new ValidationError(...)` from a route/resolver produces the expected HTTP status and structured response.

## Step 4 — Logging (app log)

Conventions: B4 (logging).

Build:
- Structured logger (language's current pino-equivalent — JSON output).
- Correlation-ID middleware: generates or propagates a request ID; binds it to a child logger per request.
- PII redaction config (allowlist approach): which fields can log, strip everything else.
- Dev pretty-print config; production JSON.

**Verify:** a log line emitted during a request contains the correlation ID. A log line that would contain a PII field (email, phone) emits without the field value, only the key.

## Step 5 — Audit log (SEPARATE system — REQUIRED for regulated data)

Conventions: B4 (logging — audit subsection), #23 (app security).

**This is a separate system from Step 4.** Different storage, retention, mutability, access controls. See B4's "Two distinct logging systems" callout. If References.md compliance section is empty AND regulated-data-gate is "no," this step may be skipped — but if EITHER is yes or default-assumed-yes, this is mandatory. Do not collapse into Step 4.

Build:
- Audit logger interface: `record(actorId, action, resource, details)`.
- Append-only store. Options: append-only table with DB trigger preventing UPDATE/DELETE, WORM-storage object, managed audit platform. Hash-chain entries so tampering is detectable.
- Separate retention policy (typically multi-year per regime).
- Separate access control: engineers should NOT have read access by default; only compliance/audit roles.
- Adapter API documented so production implementation can swap stores without changing callers.

**Verify:** audit records written during a test flow are retrievable. Tampering (editing a record) breaks the hash chain and verification fails.

## Step 6 — Database + migrations

Conventions: B1 (database).

Build:
- ORM/driver configured with single connection pool (one pool per process).
- Schema with soft-delete pattern (`deleted_at` column) where appropriate.
- Multi-tenant projects: EVERY row-owning table has `org_id` / `tenant_id` column AND a composite index starting with it. See `scaffolding/RED-FLAGS.md` "Tenant isolation in schema but not queries" — the schema is only half of the fix.
- Transaction helper for multi-table writes.
- Migration framework configured; initial migration committed.
- Migration safety: destructive changes (drop column, type change) require the two-phase pattern (add new, backfill, cutover, remove old).
- **Migrations NEVER auto-run in production.** CI runs migrations only in staging; prod migrations are a separate gated step. See RED-FLAGS "Migrations auto-run in CI."

**Verify:** initial migration applies cleanly on a fresh DB (use the project's dev-database setup — Docker Compose, Testcontainers, or equivalent). A test query against a multi-tenant table without `org_id` filter either errors (via a query lint) or is caught by Step 8 (Authorization) isolation.

## Step 7 — Auth (authentication)

Conventions: #11 (authentication).

Build:
- Auth provider wrapper at `src/shared/auth/` (or equivalent). Features NEVER import the auth SDK directly — only the wrapper.
- Token/session verification function used by middleware.
- Bearer-token extraction from request.
- `getAuthenticatedUser()` utility that returns the verified user or throws `AuthError`.
- Local-mock mode for tests.
- If enterprise SSO (SAML/OIDC): provider-admin tenant ownership verified (see `bootstrap/RED-FLAGS.md` "Enterprise SSO + not admin"). If user cannot provision, scaffold the SAML-ready adapter and document the dependency.

**Verify:** unit tests on the wrapper; integration test where a mock token produces a verified user; an invalid token produces `AuthError`.

## Step 8 — Authorization (access control + tenant isolation)

Conventions: #24 (authorization).

Build:
- Role-to-permission matrix (or policy engine if RBAC is insufficient).
- `assertCan(actor, action, resource)` utility used at the service/resolver layer. NOT at the UI layer — authorization at the service layer is the source of truth (convention #24 rule).
- **Tenant isolation enforcement** — every repository/query scoped by `org_id` at the query-builder level (via where-clause defaults, RLS policies, or a wrapper that rejects queries without a tenant filter). Schema columns alone are NOT enough. This is the #1 B2B multi-tenant data leak.
- Denied actions are logged to the AUDIT log (Step 5), not the app log.

**Verify:** unit tests that show `assertCan` passes for permitted action, throws for denied, and logs the denial to the audit log. Multi-tenant test: a user in org A cannot read data from org B even via a direct repository call.

## Step 9 — Caching

Conventions: B7 (caching).

Build:
- Cache service wrapping the key-value store (language's Redis client or equivalent).
- `getOrSet(key, ttl, fetch)` utility with stampede prevention (single-flight lock or probabilistic early expiration).
- TTL policy documented per cache.
- Invalidation strategy for mutable data (write-through, delete-on-write, or event-driven).

**Verify:** a `getOrSet` test shows the fetch function runs once across concurrent callers.

## Step 10 — Idempotency (mutation-level)

Conventions: B5 extension (for API mutations, not just jobs).

Build:
- `Idempotency-Key` header accepted on all state-mutating endpoints.
- Redis-backed deduplication with TTL (24h is typical; adjust to project retry windows).
- Pending / done state machine: pending means a concurrent request is in flight; done means the response is cached. Conflicts return the original response.

**Verify:** replaying the same request with the same idempotency key produces the original response, not a duplicate mutation.

## Step 11 — Rate limiting

Conventions: B3 extension (middleware pipeline includes rate limiting), #23 (app security).

Build:
- Per-user limiter on authenticated endpoints.
- Per-IP limiter on public/auth endpoints (login, register, password reset).
- Backing store: Redis counters (research current algorithm options — fixed window, sliding window, token bucket).
- Exemptions for health checks, internal calls.
- Rate-limit responses return 429 with `Retry-After`.

**Verify:** a rapid-fire test exceeds the limit and receives 429 with a non-empty `Retry-After` header.

## Step 12 — API server (REST or GraphQL — branch by References.md)

Conventions: B2 (API design). If REST, the main body of B2. If GraphQL, B2's GraphQL subsection.

### REST branch

Build:
- HTTP server wired up with routes.
- Resource-based URLs, standard status codes per B2.
- Response envelope consistent across endpoints.
- Pagination utility for list endpoints (offset or cursor).
- Validation middleware running Step 2 schemas on every incoming request.
- API versioning (URL path or header per B2).

### GraphQL branch

Build:
- GraphQL server (current language server library). Schema-first builder preferred (code-first-with-types is the second choice).
- Depth limit and cost analysis plugins configured. Defaults: depth 10, cost per request low enough to prevent abuse.
- Field-level authorization via scope-auth or directive-based plugin. EVERY sensitive field has an auth check.
- DataLoader equivalent wired in to prevent N+1 during resolution.
- If mobile/public clients: persisted queries plugin. Arbitrary query execution disabled in production.
- Schema diff check in CI (contract testing — see B2 versioning section).
- Idempotency (Step 10) applied to mutations.

**Verify:** integration tests on a handful of routes/queries. Depth-limit test rejects a too-deep query. Unauthorized access test fails. Pagination test returns expected metadata.

## Step 13 — Middleware pipeline (explicit order)

Conventions: B3 (middleware).

Build middleware in the EXACT order specified by B3:

1. Error handler (outermost — catches everything below)
2. Request ID / correlation ID
3. Request logging (app log)
4. Security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy)
5. CORS (with explicit origin allowlist, never `*` with credentials)
6. Rate limiting (Step 11)
7. Body parsing + body size limit
8. Authentication (Step 7)
9. Authorization (Step 8)
10. Route handler / GraphQL yoga

Wrong order = wrong behavior. Example: if auth runs before CORS, preflight OPTIONS requests fail with 401. If rate-limit runs after auth, an unauthenticated attacker can still exhaust rate limit counters.

**Verify:** trace a test request through each middleware and confirm order. A test request with `Origin: disallowed` fails at CORS (not later). An unauthenticated request fails at Auth, not at the route handler.

## Step 14 — Background jobs

Conventions: B5 (background jobs).

Build:
- Job queue framework (BullMQ, Celery, Sidekiq, equivalent for language).
- Job producer API used by features.
- Worker entry point (separate from HTTP server — separate process / container).
- Idempotency-keys required on every job payload.
- Retry with exponential backoff; DLQ after N retries (typically 3).
- Job failure observability: failures emit logs + metrics (Step 15).

**Verify:** a test job enqueued from the HTTP server runs successfully in a worker. A failing job retries the configured number of times and lands in the DLQ.

## Step 15 — Metrics + health checks

Conventions: B4 (logging & observability).

Build:
- Metrics library wired in (current OpenTelemetry SDK for the language, or Prometheus client).
- RED method per endpoint: Rate, Errors, Duration. p50/p95/p99 histograms.
- Database query duration metric.
- Queue depth + job latency metrics for Step 14.
- `/health/live` endpoint (process alive; no dependency checks; no auth; under 1s response).
- `/health/ready` endpoint (DB + cache + critical dependencies reachable; no auth; under 1s response).

**Verify:** hitting `/health/ready` with DB stopped returns 503. Metrics endpoint returns a non-empty scrape.

## Step 16 — Testing

Conventions: #12 (testing), #18 (verification).

Build:
- Test runner configured (language's current equivalent).
- Test database using Testcontainers (or equivalent) — real DB, not mocks. Convention #12 prefers integration over mocked unit tests.
- Test factories for domain objects (Builder pattern or fixture helpers).
- Custom setup/teardown for shared resources (DB reset, Redis flush).
- Tests organized colocated with code (`.test.ts` next to source file).

**Verify:** `<test-runner>` command runs the base test suite green. Coverage thresholds configured per project.

## Step 17 — Build + CI

Conventions: #15 (build/CI), #2 (git).

Build:
- CI pipeline definition in repo (GitHub Actions / GitLab CI / equivalent).
- Sequence: lint → typecheck → test → build → (containerize) → artifact push.
- Required status checks on main branch (merge blocks if any fail).
- Preview deployments per PR if the platform supports.
- Rollback path documented.
- **Migrations NOT auto-run on deploy.** Staging auto-apply is OK; production migrations are a separate gated workflow per B1.

**Verify:** open a PR with a typecheck failure — CI blocks the merge. Open a PR with a test failure — CI blocks. A passing PR produces an artifact / preview.

## Step 18 — Smoke-test feature (scaffold exit gate)

Build a minimal feature that exercises EVERY shared system. Typical choice: a `ping` or `health-details` endpoint/query that:

- Authenticates the caller (Step 7)
- Authorizes the caller (Step 8)
- Reads from the DB (Step 6)
- Writes to the audit log (Step 5)
- Uses the app log (Step 4)
- Produces a metric (Step 15)
- Returns through the error middleware (Step 3)
- Is covered by an integration test

This is the end-to-end integration proof. Without it, the scaffold can appear "complete" while having misconfigured wiring. See `scaffolding/RED-FLAGS.md` "Scaffold-complete without integration proof."

**Verify:** the smoke-test feature's integration test passes.

## Final gate — automated validator

Run `scripts/validate-scaffold.sh`. Do not commit until it passes. The validator checks:
- Every foundational system in feature-tree.md has a `docs/systems/{name}.md`
- Expected paths exist
- Anti-patterns absent (console-level output in source, direct third-party imports bypassing wrappers, untyped escape hatches without justifying comment)
- Env validation called from startup
- Migrations not in auto-apply CI step

If validator fails, FIX before committing. Do not paper over.

## Post-scaffold output

- Every system listed in `feature-tree.md` marked implemented with its path.
- Every system has a doc at `docs/systems/{name}.md` using the template in `scaffolding/SCAFFOLD.md`.
- `References.md` updated with actual paths, DB schema overview, API summary.
- `.env.example` at project root.
- `VERSION-LOG.md` Scaffold entry.
- Initial "scaffold complete" commit.
