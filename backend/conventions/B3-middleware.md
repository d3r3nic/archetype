# Convention B3: Middleware & Request Pipeline

## Principle

A backend request flows through a pipeline of middleware in a specific order. Each step has one job. Authentication happens before authorization. Validation happens before the handler. Error handling wraps everything. When steps are mixed into handlers, some endpoints skip auth, some skip validation, and bugs are inconsistent across the API.

## Reusable System

Create a middleware pipeline that establishes:
- A defined order that every request passes through
- Request ID generation at the entry point (correlation ID for all logs and downstream calls)
- Authentication middleware (extracts and verifies identity)
- Authorization middleware (checks permissions for the specific resource/action)
- Validation middleware (parses and validates request data against schemas)
- Error handling middleware (outermost wrapper, catches everything, returns consistent error responses)

## Rules

- The correct middleware order is: error handler (outermost) → request ID → logging → security headers → rate limiting → authentication → authorization → validation → handler → response serialization.
- Never put authentication or authorization checks inside route handlers. They belong in middleware so every endpoint is protected consistently.
- Never put input validation inside route handlers. Use validation middleware with the schema for that endpoint. The handler receives already-validated, typed data.
- Generate a unique request ID (correlation ID) at the entry point. Propagate it through every log entry, every downstream service call, every error response. Include it in the response headers so consumers can reference it for support.
- Log the method, path, status code, and duration of every request. Never log request bodies in production (they may contain secrets or PII).

## Violations

- Auth check, validation, and business logic all inside the handler. Some handlers remember all three, some forget auth, some skip validation.
- No request ID. Debugging production issues requires manually correlating timestamps across logs.
- Error handler registered after routes. Unhandled exceptions crash the process instead of returning an error response.
- Authorization runs before authentication. Every request fails because identity isn't established yet.

## Wrong vs Right

- WRONG: each handler starts with "check if user is authenticated, check if user has permission, validate the body, then do the work." 50 handlers, each implementing its own auth/validation. One forgets auth. Security hole.
- RIGHT: middleware pipeline handles auth, authorization, and validation BEFORE the handler runs. The handler receives an authenticated user and validated data. It only contains business logic.
- WRONG: no correlation ID. A user reports an error. Support has to search logs by timestamp and guess which request it was among thousands.
- RIGHT: every request gets a unique ID. The error response includes it. The user says "error ID: abc-123." Support queries logs for abc-123 and gets the complete request story.

## Research Notes

When bootstrapping this convention:
- Research the framework's middleware system and how to define execution order.
- Research correlation ID libraries or patterns for the framework.
- Research the framework's built-in security middleware (CORS, HSTS, helmet/equivalent).
- Research rate limiting middleware for the framework.
- Document the middleware order, correlation ID header name, and logging format in References.md.
