# Convention B4: Logging & Observability

## Applies when

The service runs somewhere its operators cannot watch directly. What varies: how much people rely on it (#30), where it runs, what routes traffic to it, and whether regulated data or a commitment requires an audit trail. A command-line tool's output to its own user is not logging; its diagnostics still follow the rules below.

## Principle

The service's operation is visible through one logger and signals sized to how much people rely on it, and nothing sensitive is ever written to a log. Logs are structured so they can be searched and alerted on, levels mean something, and every line of a request can be tied together. An audit trail, when one is required, is a separate system with its own storage, retention and access.

**Two systems, never conflated.**
- **Application logs:** operational records for debugging and alerting. Short retention, personal data redacted, read by engineers.
- **Audit trail:** evidence of who did what, when and from where. Long retention, append-only and tamper-evident, separate access, read by auditors. Required when regulated data or a commitment calls for it (#23, #30); treating the two as one log causes compliance failures.

## Reusable System

The observability foundation: the one logger with its structure and redaction; the request identifier from the pipeline (B3); the signals the service's reliance calls for; health answers when something routes traffic or restarts by health; and, when required, the audit trail. References.md records each; § Boundaries keeps production code from writing output around the logger.

## Rules

- Write production output through the one logger. Every entry carries a time in a standard format, a level, the service, the request identifier and a message, plus context fields.
- Use levels for what they mean: error for broken behavior that should alert someone, warning for the unexpected but recovered, information for normal operation, debug for investigation and off in production. An expected business outcome, such as "not found", is not an error.
- Never log secrets, tokens, keys, payment card data or personal data. Log only fields you permit; never whole bodies or whole records.
- When a router or an orchestrator acts on health, answer two questions quickly and without authentication: is the process alive, and can it serve now, with its critical dependencies answering.
- Collect the signals the reliance calls for: at least the rate, errors and duration of requests once people depend on the service, and queue depth where there are queues.
- Verify that a configured exporter, alert or dashboard actually receives data. Configuration that never starts is a silent failure.

## Violations

- Output printed around the logger in production code.
- A whole user record written to a log.
- Everything logged as an error, so real errors drown.
- Log lines of one request that cannot be tied together.
- A health answer that says "fine" while the database is unreachable.
- An audit trail kept in the application logs.

## Wrong vs Right

- WRONG: a request's body is printed as free text on arrival. RIGHT: the logger records the request identifier, method and route, with no body.
- WRONG: a failure is printed with no context. RIGHT: the logger records the operation, the request identifier and the error message at error level.
- WRONG: the health answer is always "fine". RIGHT: the readiness answer checks the database and other critical dependencies and reports unavailable when one is down; the liveness answer only says the process runs.

## Research Notes

Research the chosen stack's structured logging and redaction options, request-scoped context, the health conventions of the hosting platform, and a signal pipeline that follows open standards where they exist. When regulated data applies, research append-only, tamper-evident storage and the retention the regime requires. Record both systems in References.md when both apply.
