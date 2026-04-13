# Convention B2: API Design (Building APIs)

## Principle

APIs are the contract between your backend and its consumers. Every endpoint follows the same URL conventions, uses the correct HTTP methods, returns consistent status codes, and wraps responses in a standard envelope. Inconsistency forces every consumer to handle each endpoint differently. See also universal convention #10 for the contract between frontend and backend.

## Reusable System

Create an API design foundation that establishes:
- URL naming convention applied consistently across all endpoints
- Response envelope used by every endpoint (success, list, error shapes)
- Pagination utility for list endpoints with metadata
- Validation middleware that runs before every handler (see universal #7 for schema validation)
- Status code mapping from error types to HTTP codes (centralized, not per-handler)

## Rules

- Use nouns for resources, not verbs. /users, /orders, /products. Not /getUsers, /createOrder.
- Use plural names consistently. /users/123, not /user/123.
- HTTP methods: GET reads (never mutates), POST creates, PUT replaces entirely, PATCH updates partially, DELETE removes. Never use GET for mutations.
- Use the same status codes for the same situations across ALL endpoints. 201 for creation everywhere, not 201 on one endpoint and 200 on another.
- Common status codes: 200 success, 201 created, 204 no content (delete), 400 bad request, 401 not authenticated, 403 not authorized, 404 not found, 409 conflict, 422 validation error, 429 rate limited, 500 server error.
- Every list endpoint must be paginated. Default page size 20, maximum 100. Never return unlimited results. Return metadata: total, page, limit, hasMore.
- Every endpoint returns the same envelope: { data, meta } for success, { errors: [{ code, message, field? }], meta } for errors. Never return raw arrays at the top level.
- Validate all incoming data at the API boundary before it reaches the service layer. Use allowlisting (permit known fields only), not blocklisting. Strip unknown fields.
- Version the API from day one. URL path versioning (/v1/users) is simplest. Never break existing endpoints — add new fields as optional, remove in new versions only.

## Violations

- Verb-based URLs: /getUser, /deleteOrder, /updateProfile instead of resource-based.
- POST used for everything. GET used for mutations.
- 200 returned for creation on one endpoint, 201 on another. 400 returned for validation errors on one endpoint, 422 on another.
- List endpoint returns all 50,000 records with no pagination.
- One endpoint returns { users, total }, another returns { data, count }, another returns a raw array.
- Endpoint accepts and passes through raw user input to the service without validation.

## Wrong vs Right

- WRONG: /getUsers, /createUser, /deleteUser/123 — verb-based, inconsistent.
- RIGHT: GET /users, POST /users, DELETE /users/123 — resource-based, HTTP method carries the verb.
- WRONG: list endpoint returns all records. Client crashes rendering 50K items. Database does a full table scan.
- RIGHT: GET /users?page=1&limit=20 returns 20 records with { data: [...], meta: { total: 50000, page: 1, limit: 20, hasMore: true } }.
- WRONG: endpoint accepts any JSON body and passes it directly to the database. SQL injection, data corruption.
- RIGHT: endpoint validates against a schema, strips unknown fields, then passes typed, clean data to the service.

## Research Notes

When bootstrapping this convention:
- Research the framework's route definition patterns and how to enforce consistent URL naming.
- Research pagination libraries or patterns for the framework (offset and cursor).
- Research validation middleware for the framework that integrates with the schema library.
- Research API versioning approaches for the framework.
- Document the URL conventions, response envelope, pagination format, and status code mapping in References.md.
