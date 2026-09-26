# Scaffold — Backend

Routed from `scaffolding/SCAFFOLD.md` when the project is a backend: an API, a worker, a data pipeline, a service others call. Each step applies the decision the project recorded, researches the chosen stack where the record is silent, builds only what this service needs, and says when it applies. The steps are ordered so each system is built and verified before the next depends on it. A service does not build a system its facts do not call for; it records "not applicable" with the reason, or a deferral with its trigger (#30).

**Read `scaffolding/_preamble.md` first.** It holds the rules shared by every scaffold playbook.

## Step 0 — Handoff check (read before building anything)

Read `References.md` in full, with PROFILE.md:
- **Compliance section** (PROFILE.md holds the regulated-data fact): when a regime applies, the audit trail (Step 5) is required unless the regime requires none, which the Audit log line records with the reason.
- **Foundational Systems list:** inventory every system. Compare it with the steps below; a system with no step is a project-specific extension built beside its nearest sibling. A missed system is a silently skipped one.
- **Open pre-production gates** in `VERSION-LOG.md`: halt until they are resolved (`bootstrap/RED-FLAGS.md`, Deploy Gate).

Before each later step, read the conventions it names.

## Step 1 — Project setup and configuration

Always. Conventions: #1, #2, #15.

- The runtime and package manager pinned, with the lock file committed.
- A formatter and a linter with real rules (#25), and type checking at the strongest level the project will keep passing (#7).
- Where the checks run before work reaches the main line, chosen for the stage (#2, #15), recorded in References.md.
- Configuration's one owner: it reads the environment, validates every required value at startup, before any service starts, and fails with a message naming what is missing (#1). Record its § Boundaries line so nothing else reads the environment.

**Verify:** the install succeeds; the checks run clean where they are recorded to run; removing a required value makes the start fail.

## Step 2 — Types and validation

Always. Conventions: #7.

- One definition per shared data shape, with the static type and the runtime validation derived from each other where the stack allows.
- Where identifiers of different kinds can be confused and the stack can tell them apart cheaply, distinct types for them.

**Verify:** valid input parses; invalid input fails with field-level messages.

## Step 3 — Error handling

Always. Conventions: #8, B2.

- The kinds of error the service distinguishes (validation, identity, not found, conflict, rate limited, an outside service failing, internal), shaped to the domain.
- One mapping from those kinds to the transport's status or error codes and to the one error format (B2), in the outermost layer.
- Tests on the kinds and the mapping.

**Verify:** each kind raised in a handler produces the expected status and the recorded format.

## Step 4 — Application logging

Always for a service. Conventions: B4.

- The one logger, structured, with a development format that people can read.
- The request identifier generated or carried at the entry and attached to every line of the request.
- Redaction by allowlist: only permitted fields are written.
- The § Boundaries line that keeps production code from writing output around the logger.

**Verify:** a line written during a request carries its identifier; a field that would hold personal data is written without its value.

## Step 5 — Audit trail (a separate system)

Applies when regulated data or a commitment requires one (#30). Conventions: B4, #23.

This is not the application log. Different storage, retention, mutability and access; do not fold it into Step 4.
- One recording interface: who, what action, which record, the details.
- An append-only store, protected against changes and deletions, with entries chained so that tampering is detectable.
- Its own retention, from the regime.
- Its own access: engineers cannot read it by default; the roles the regime names can.
- A store that can change without changing the callers.

Record where it lives on the Audit log line of References.md § Compliance: its path in this unit, or `kept by <the service that keeps it>`. The exit gate checks that path, and that the trail is not a memory-only store.

**Verify:** records written during a test flow can be read back; editing one breaks the chain and verification fails.

## Step 6 — Database and migrations

Applies when the service owns a database. Conventions: B1.

- One connection pool per process, and the data-access layer every query goes through; the § Boundaries line that keeps connections inside it.
- Soft delete, where the domain uses it, filtered by a default scope in the data-access layer.
- When one deployment serves several customers: every table that holds a customer's rows carries the tenant, with an index that starts with it, and the data-access layer scopes every query to the caller's tenant. The column alone is half the fix (`scaffolding/RED-FLAGS.md`, section 6).
- A transaction helper for related writes.
- The migration workflow, with the first migration committed, and changes made additively.
- Production migrations only through a manual or gated path. Record the migration command as `migrate:` in References.md § Commands and bound it to its production path in § Boundaries, so it cannot run anywhere else (`scaffolding/RED-FLAGS.md`, section 10).

**Verify:** the first migration applies to a fresh development database; a query without the tenant is refused by the data-access layer.

## Step 7 — Authentication

Applies when callers must prove who they are. Conventions: #11.

- The auth owner: verifies credentials or sessions, gives the pipeline the caller's identity, and maps the provider's identity to the project's own record of the person.
- The provider's library behind the owner, with its § Boundaries line.
- A test mode that produces verified identities without the real provider.
- For enterprise single sign-on: confirm that someone on the owner's side can administer the provider's tenant (`bootstrap/RED-FLAGS.md`); if nobody can yet, build the adapter and record the dependency.

**Verify:** a test credential yields the verified identity; an invalid one is refused as the identity error.

## Step 8 — Authorization and tenant isolation

Applies when access is restricted. Conventions: #24, B1.

- The permission model, defined once, and the one check the service layer calls with the caller, the action and the record.
- Tenant scoping in the data-access layer, when one deployment serves several customers (Step 6). This is where multi-tenant systems most often leak.
- Denials logged, to the audit trail when there is one.

**Verify:** a permitted action passes and a denied one is refused and logged; a caller in one tenant cannot read another tenant's records, even through a direct data-access call.

## Step 9 — Caching

Applies when a measured read needs it (#13). Conventions: B7.

- The cache service, with one key scheme that includes the user or tenant for private data.
- A read-or-fill helper that lets only one caller rebuild a missing entry.
- A staleness rule per kind of cached data, and how changes invalidate it.

**Verify:** concurrent callers of a missing entry cause one rebuild.

## Step 10 — Idempotency of changes

Applies when clients may retry a change or a change has real effects: payments, messages, orders. Conventions: B2, B5.

- An idempotency key accepted on those changes, or operations that are idempotent by design.
- Recorded outcomes kept for the retry window the clients need, with a pending state for a request still in flight; a repeat returns the first result.

**Verify:** the same request repeated with the same key returns the original result and changes nothing twice.

## Step 11 — Rate limiting

Applies when people outside the owner's control can reach the service; an isolated stage may defer it with its trigger (#30). Conventions: B3, #23.

- Limits per caller on authenticated endpoints, and per source on sign-in, registration, password reset and anything expensive, with the counting method chosen for the load.
- Exemptions for health answers and internal calls.
- A limited response that says when to try again.

**Verify:** a burst over the limit is refused with the retry time.

## Step 12 — API server

Applies when the service exposes an API. Conventions: B2, #10.

- The recorded style, applied consistently: naming, methods or operations, the one response format, errors from Step 3.
- Validation of every input at the boundary with Step 2's definitions.
- Paging for every list, with limits chosen from use.
- The evolution approach recorded before the first consumer outside the project's control, and a check that catches a breaking change before merge.
- Step 10 applied to the changes that need it.

When clients compose their own queries:
- depth and cost limits;
- field-level authorization for sensitive fields;
- batched loading of related records, with every loader created per request, inside the request's context. A loader shared across requests caches one tenant's data for the next: a security defect, not a performance one;
- for public or device clients, only allow-listed queries in production, with the allow-list's location recorded in References.md (templates/references-backend.md), which the exit gate checks exists.

**Verify:** integration tests on a few endpoints or queries; an unauthorized call is refused; a list returns its paging information; a query over the depth limit is refused.

## Step 13 — Request pipeline

Applies to a service that handles requests. Conventions: B3, #23.

Build the pipeline in the order the project records, with the reason for the order. It must fail safe:
- error handling outermost;
- the request identifier early, so every later step can log with it;
- browser protections (security headers, allowed cross-origin callers) when browsers call the service, answered before identity so cross-origin preflights work;
- rate limiting before the expensive steps;
- a limit on body size;
- identity before anything that uses it;
- validation before the handler; record-level authorization in the service layer (Step 8).

**Verify:** trace a test request through each step; a disallowed origin is refused before identity; a request without a session is refused before the handler.

## Step 14 — Background jobs

Applies when the service has work people should not wait for. Conventions: B5.

- The one job runner, chosen for the real volume, and the producer interface features use.
- Workers apart from the request-serving processes when load or reliability calls for it.
- Idempotent handlers, bounded retries with a growing delay, failed jobs kept for inspection and made visible.

**Verify:** a job queued by a request runs in a worker; a failing job retries its set number of times and lands with the failed jobs.

## Step 15 — Health and signals

Applies by reliance (#30), and whenever something routes traffic or restarts the service by its health. Conventions: B4.

- Two quick, unauthenticated health answers when something acts on them: the process is alive; it can serve now, with its critical dependencies answering.
- The signals the reliance calls for: at least the rate, errors and duration of requests once people depend on the service, database time, and queue depth and job latency for Step 14.
- Proof that each configured exporter actually delivers.

**Verify:** the readiness answer reports unavailable with the database stopped; the signals arrive where the project reads them.

## Step 16 — Testing

Always. Conventions: #12, #18.

- The test runner and the one shared setup, with the test location the project chose.
- Tests that exercise data access against a disposable real instance of the chosen store where practical, not a fake of the service's own database.
- Builders for domain objects, and a recorded isolation strategy so tests never depend on each other's data (development/RED-FLAGS.md).

**Verify:** the test command runs the base suite green.

## Step 17 — Checks and delivery

Always. Conventions: #15, #2.

- The project's checks run where recorded, and a merge into the main line requires them.
- The build produces what the service ships.
- Production migrations stay out of every automatic path (Step 6).
- A known way back from a release people depend on.
- A release that spends money or reaches customers waits for the owner (#29).

**Verify:** a change that fails a check cannot merge; a passing change produces the release artifact.

## Step 17b — Pulse Monitor (dev-only project visibility)

Applies when the project builds one (#26). Conventions: #26.

Serve the framework's base UI and `.pulse-state.json` through a development-only route, from paths outside every folder the production build or deployment copies; production builds contain neither.
- A route registered only when the environment explicitly says development (an unset or unrecognized environment does not register it): `GET /dev/pulse/` serves the starter UI (markup plus its style and script assets, with `/dev/pulse` redirecting to the trailing-slash address), and `GET /dev/pulse/.pulse-state.json` serves the generated state.
- Copy `archetype/templates/pulse-ui/` into the project, or serve it from the installed framework folder when that sits inside the project.
- A project task that runs `archetype/scripts/pulse-inspect.sh --out <project-owned path>/.pulse-state.json` before serving.
- `docs/systems/pulse-monitor.md` from `archetype/templates/pulse-monitor-spec.md`, with its "Where it's served" section filled in; read the spec's implementation notes before wiring the route.

**Verify:** every section of the pulse route renders with real data; refreshing re-reads the state (run the inspector first for live data). The production artifact's files, hidden files included, hold no snapshot and no pulse UI file, a search of its contents for `Archetype pulse UI` finds nothing, and the production server does not answer the pulse route.

## Step 18 — Smoke-test feature (the integration proof)

Always. Build one minimal feature that goes through every shared system that was built: it identifies and authorizes the caller, reads from the database, writes to the audit trail and the application log, produces a signal, and returns through the error mapping, each where built, with an integration test. Without it the scaffold can look complete with its systems never wired together (`scaffolding/RED-FLAGS.md`, section 11).

**Verify:** the smoke-test feature's integration test passes.

## Final gate — automated validator

Run `scripts/validate-scaffold.sh` and fix what it reports before committing. It checks the records against the project:
- every foundational system in feature-tree.md has its page;
- when the unit handles regulated data: an audit trail at the location References.md § Compliance records, and not a memory-only store (that it is separate from the application log is the review's to read);
- a recorded migration command is bounded in § Boundaries (once the section exists; until then the gate warns), and the § Boundaries lines that exist hold;
- a recorded location for the checks, and a recorded query allow-list, exist;
- the smoke-test feature and the VERSION-LOG.md scaffold entry.

It cannot judge whether a system was built well; the smoke test and the independent review do.

## Post-scaffold output

- Every applicable system in `feature-tree.md` marked implemented with its path, `deferred (TD-N)` with its trigger (#30; a deferred system keeps its row and a page saying what is deferred and until when), `blocked (owner: <action>)` (#29; its page names the action and what stays unavailable), or not applicable with the reason.
- A page per system at `docs/systems/{name}.md`, from the template in `scaffolding/SCAFFOLD.md`.
- `References.md` updated with the real paths, the data model overview, the API summary and the § Boundaries lines.
- The example configuration file.
- The `VERSION-LOG.md` scaffold entry.
- The "scaffold complete" commit.
