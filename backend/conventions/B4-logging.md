# Convention B4: Logging & Observability

## Principle

Logs, metrics, and health checks are how you know your backend is working. Structured logging (JSON, not free text) enables querying and alerting. Log levels distinguish severity. Sensitive data is never logged. Correlation IDs connect logs across a request's lifecycle. Health checks tell orchestrators whether the service can accept traffic. AI defaults to console-level output for everything — this convention replaces that with a production-grade observability system.

**Two distinct logging systems — do not conflate them.** Most backends need both:

- **App logging** (this convention, default scope) — operational logs for debugging and alerting. Short retention (typically 2 weeks to 90 days). Mutable by log processors. PII-redacted. Queried by engineers.
- **Audit logging** — compliance evidence for "who did what when from where." Long retention (typically 1-7 years depending on regime). Append-only and tamper-evident. Separate access control. Queried by auditors, not engineers.

If the project handles regulated data (HIPAA, SOC 2, PCI, GDPR right-to-audit, financial), an audit log is REQUIRED. See `conventions/23-app-security.md` and the project's compliance regime requirements. The two systems often look similar in code but have fundamentally different storage, retention, and access-control requirements — treating them as one log causes compliance failures.

## Reusable System

Create an observability foundation that establishes:
- A structured logging service (JSON format, proper library like pino, winston, Serilog, loguru). Never console.log.
- Every log entry includes: timestamp (ISO 8601 UTC), level, service name, correlation_id, message.
- Sensitive data redaction: middleware that strips known sensitive fields before logging.
- Two health check endpoints: liveness (process alive, no dependency checks) and readiness (dependencies connected, can serve traffic).
- Metrics collection for: request rate, error rate, response time (p50, p95, p99), database query time.

## Rules

- Never use console.log or print in production code. Use the structured logging service.
- Every log entry is JSON with: timestamp, level, service, correlation_id, message, and optional context fields.
- Log levels: ERROR for broken functionality (triggers alerts), WARN for unexpected but recoverable, INFO for standard operations, DEBUG for troubleshooting (disabled in production).
- Never log at ERROR level for expected business conditions (user not found = WARN or INFO, not ERROR).
- Never log passwords, tokens, API keys, credit card numbers, SSNs, or PII. Use allowlisting: only log fields you explicitly permit. Never log entire request bodies or entire user objects.
- Implement two health endpoints: liveness at /health/live (is the process running?) and readiness at /health/ready (can it serve traffic? checks database, cache, critical dependencies). No authentication required. Must respond under 1 second.
- Emit metrics for: request rate, error rate, response time percentiles, database query time, queue depth. Follow the RED method: Rate, Errors, Duration.

## Violations

- console.log('user created:', user) — logs the entire user object including potential PII.
- Everything logged at ERROR level. Alerts fire constantly, real errors get buried.
- No correlation ID in logs. A request touches 5 services, generates 50 log entries, and there's no way to connect them.
- Health endpoint returns { status: "ok" } without checking database connectivity. Load balancer sends traffic to an instance with a dead database connection.
- No metrics. Production issues discovered from user complaints, not dashboards.

## Wrong vs Right

- WRONG: console.log('Request received', req.body) — free text, logs sensitive data, not queryable.
- RIGHT: logger.info({ correlationId, method: req.method, path: req.path }, 'Request received') — structured JSON, no body logged, queryable.
- WRONG: catch(err) { console.error(err) } — unstructured, no context, no correlation.
- RIGHT: catch(err) { logger.error({ correlationId, operation: 'createOrder', error: err.message }, 'Order creation failed') } — structured, contextual, traceable.
- WRONG: /health returns 200 always. Database is down but the health check still passes.
- RIGHT: /health/ready checks database.ping(), cache.ping(). Returns 503 if any critical dependency is down. /health/live just returns 200 (process is running).

## Research Notes

When bootstrapping this convention:
- Research a structured-logging library for the language.
- Research request-scoped-context / correlation-ID patterns for the framework.
- Research health-check patterns for the deployment platform.
- Research a metrics pipeline for the framework (language-agnostic standards preferred when available).
- Research sensitive-data redaction middleware or logging interceptors.
- **If regulated data:** research audit-log tooling. Append-only storage, tamper-evident options (hash-chained, WORM, managed audit platforms), and multi-year retention. Audit logs are a SEPARATE system from app logs — different storage, mutability, access controls.
- Document BOTH systems (app-logging: library, format, health checks, metrics; audit-logging: storage, retention, access, recorded events) in References.md when applicable.
