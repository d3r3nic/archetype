# Convention #23: Application Security

## Principle

Security is not a feature — it's a property of every feature. Every input is validated. Every output is encoded. Every secret is managed, never hardcoded. Every error message hides internal details. Every dependency is scanned. AI generates 2.74x more security vulnerabilities than human code and 45% of AI-generated code contains security issues. Security conventions must be explicit because AI does not apply them by default.

## Reusable System

Create a security foundation that establishes:
- Input validation middleware that runs on every endpoint (allowlist approach: only permit known fields, strip everything else)
- Output encoding utilities that prevent XSS (the framework's template engine usually handles this, but raw HTML rendering must be explicitly sanitized)
- Security header configuration applied globally (CSP, HSTS, X-Frame-Options, X-Content-Type-Options)
- CORS configuration with explicit origin allowlist (never wildcard with credentials)
- CSRF protection on state-mutating requests (SameSite cookies, CSRF tokens)
- Rate limiting on public endpoints and authentication endpoints
- Secret management: all secrets from environment variables or a vault, never in code
- Audit logging service (SEPARATE from app logging): who did what, when, from where. Different retention, mutability, and access controls than app logs. Required for regulated data (HIPAA, SOC 2, PCI, GDPR audit-trail, financial). See `backend/conventions/B4-logging.md` for the app-log vs audit-log distinction.

## Rules

- Validate all user input at entry points. Use allowlisting (permit known fields only). Never pass raw user input to services, databases, or templates without validation and sanitization.
- Never render unsanitized user content. Use the framework's built-in escaping. If you must render raw HTML, sanitize with a library first.
- Configure security headers globally: Content-Security-Policy, Strict-Transport-Security, X-Frame-Options, X-Content-Type-Options, Referrer-Policy. Research the framework's recommended security middleware.
- Configure CORS with specific origin allowlists. Never use wildcard (*) with credentials. Understand that preflight OPTIONS requests must be handled.
- Protect state-mutating requests against CSRF. Use SameSite cookie attribute and/or CSRF tokens.
- Rate limit public endpoints, authentication endpoints (login, register, password reset), and any endpoint that triggers expensive operations.
- Never hardcode secrets. All secrets come from environment variables or a secret vault. Rotate secrets periodically. Never commit .env files with real values.
- Never expose internal error details to API consumers. Stack traces, database error messages, file paths, and internal IDs must not appear in production error responses. Log them internally, return a generic message with a correlation ID.
- Encrypt sensitive data at rest (PII, financial data, health records). Use field-level encryption for the most sensitive fields (SSNs, credit cards). Use database-level encryption (TDE) as a baseline.
- All connections use TLS. Never transmit sensitive data over unencrypted channels.
- Scan dependencies for known vulnerabilities in CI. Use lockfile integrity checks. Audit new dependencies before adding them.
- Log security-relevant events: authentication attempts (success and failure), authorization denials, data access to sensitive resources, admin actions, configuration changes. Include correlation ID, user ID, timestamp, and action.
- Handle PII according to applicable regulations. Minimize collection. Define retention periods. Implement deletion capability. Mask or redact PII in logs and non-production environments.

## Violations

- Endpoint accepts any JSON body and passes it to the database without validation. Injection risk.
- User content rendered as raw HTML without sanitization. XSS risk.
- No security headers configured. Clickjacking, MIME sniffing, protocol downgrade risks.
- CORS configured with Access-Control-Allow-Origin: * with credentials. Any origin can make authenticated requests.
- No rate limiting on login endpoint. Brute force attack possible.
- API key hardcoded in source code and committed to git.
- Production error response includes the full stack trace and database connection string.
- SSNs stored in plain text in the database. No encryption at rest.
- No dependency vulnerability scanning. Known CVEs in production dependencies.
- No audit log. An admin deletes a user's data and there's no record of who did it or when.

## Wrong vs Right

- WRONG: endpoint accepts request body and passes it directly to a database query. Attacker sends crafted input that modifies the query.
- RIGHT: endpoint validates against a strict schema (allowlist of known fields, type checks, length limits), strips unknown fields, then passes clean typed data to the service layer.
- WRONG: production error returns { error: "TypeError: Cannot read property 'name' of undefined at /app/src/handlers/users.ts:42" }. Attacker learns the tech stack, file paths, and where the code is fragile.
- RIGHT: production error returns { error: { code: "INTERNAL_ERROR", message: "An unexpected error occurred", requestId: "abc-123" } }. Full details logged internally with the same requestId for debugging.
- WRONG: .env file with DATABASE_URL=postgres://admin:password123@prod-db.example.com:5432/myapp committed to git.
- RIGHT: .env.example committed with variable names and descriptions. Actual values in environment variables or secret vault. CI verifies no secrets in committed files.

## Research Notes

When bootstrapping this convention:
- Research the framework's recommended security middleware (helmet for Node, SecurityHeaders for .NET, django-csp for Python)
- Research CORS configuration for the framework
- Research CSRF protection patterns for the framework (SameSite cookies, token-based)
- Research rate limiting middleware for the framework
- Research dependency scanning tools that integrate with the project's CI (npm audit, Snyk, Socket.dev, pip-audit)
- Research encryption patterns for the language (field-level encryption, key management)
- Research audit logging patterns for the framework
- Document the security middleware, CORS config, rate limit settings, and audit logging in References.md
