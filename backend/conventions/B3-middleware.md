# Convention B3: Middleware & Request Pipeline

## Applies when

The service handles requests through a pipeline of shared steps before its handlers: an API server, a web server, a message consumer. What varies: which cross-cutting concerns the service has (identity, rate limits, browser protections, tracing) and what the runtime offers for ordering them.

## Principle

Every cross-cutting concern is handled once, in the pipeline, in a recorded order that fails safe, so no endpoint can forget it. Error handling wraps everything; identity is established before anything that depends on it; input is validated before the handler; every request can be traced. Authorization of an action on a specific record runs where that record is known, in the service layer (#24); the pipeline may carry coarse checks such as "signed in" or "holds a role for this whole area".

## Reusable System

The pipeline: its steps and their order, recorded in References.md with the reason for the order. It generates a request identifier at the entry and carries it through every log line, downstream call and error response; it establishes identity; it applies the service-wide protections; it validates input against each endpoint's definition; and its outermost step turns any failure into the one error format (B2).

## Rules

- Put each cross-cutting concern in the pipeline once. Handlers contain business logic only.
- Record the order and why. Error handling is outermost; identity comes before anything that uses it; validation comes before the handler; rate limiting comes early enough to protect the expensive steps.
- Validate input in the pipeline or at the handler's boundary with the endpoint's one definition (#7). The handler receives validated data.
- Check permission to act on a specific record in the service layer, where the record is known (#24). Never leave it to each handler to remember.
- Generate a request identifier at the entry, propagate it through every log line and downstream call, and return it with errors so people can quote it.
- Log each request's method, route, status and duration. Never log bodies in production; they can carry secrets and personal data.

## Violations

- Identity, validation and business logic mixed in each handler, and one handler forgetting identity.
- An error handler registered where it cannot catch everything, so a failure crashes the process.
- Record-level permission decided in the pipeline without the record, or not at all.
- No request identifier, so a reported error cannot be found in the logs.

## Wrong vs Right

- WRONG: fifty handlers each check identity, check permission and validate the body before working; one forgets identity. RIGHT: the pipeline establishes identity and validates input; the service checks permission on the record; the handler holds only business logic.
- WRONG: a person reports an error and support searches the logs by time. RIGHT: the error carries a request identifier, and one search returns the whole request.

## Research Notes

Research the chosen stack's pipeline mechanism and how it orders steps, request-scoped context for the identifier, and its built-in protections and rate limiting. Record the order, the identifier's header or field, and the logging format in References.md.
