# Convention B4: Logging & Observability

## Principle

Logs, metrics, and health checks are how you know your backend is working. Structured logging (JSON, not free text) enables querying and alerting. Log levels distinguish severity. Sensitive data is never logged. Correlation IDs connect logs across a request's lifecycle. Health checks tell orchestrators whether the service can accept traffic. AI defaults to console.log for everything — this convention replaces that with a production-grade observability system.

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
- Research structured logging libraries for the framework (pino for Node, Serilog for .NET, loguru for Python, zerolog for Go).
- Research the framework's recommended approach for request-scoped context (correlation IDs).
- Research health check patterns for the deployment platform (Kubernetes probes, ECS health checks, etc.).
- Research metrics libraries for the framework (Prometheus client, OpenTelemetry).
- Research sensitive data redaction middleware or logging interceptors.
- Document the logging library, log format, health check URLs, and metrics endpoints in References.md.
