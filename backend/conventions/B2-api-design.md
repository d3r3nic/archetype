# Convention B2: API Design (Building APIs)

For calling other services, see universal convention #9; for the shapes both sides share, #10.

## Applies when

The service exposes an API that others call: its own client, other services, outside developers. What varies: who the consumers are and whether they are under the project's control, the API style chosen for them (resource-oriented, remote procedures, a query language clients compose, an event stream), and whether consumers can be updated together with the server.

## Principle

The API is a contract, and one style is applied consistently across it. Every endpoint validates input at the boundary, returns the one recorded response format, maps errors the same way, and bounds what it returns. The API evolves without breaking consumers the project does not control. Inconsistency forces every consumer to handle each endpoint differently; that is duplicated work pushed onto every caller.

## Reusable System

The API foundation: the style and its naming rules, the one response format for success, lists and errors, the paging method, the validation at the boundary (#7, #23), the single mapping from errors to the transport's status or error codes, and the evolution approach. References.md records each; features use them and never define their own.

## Rules

- Choose the style for the consumers and apply it consistently: names, methods or operations, and the same error for the same situation everywhere.
- Reads never change anything.
- Validate every input at the boundary before it reaches the domain: allow known fields, drop the rest (#23).
- Return the one recorded response format from every endpoint. Map errors in one place, never per handler.
- Bound every list: page it, with limits chosen from real usage, and say how to get the next page.
- Decide how the API evolves before the first consumer outside the project's control: add without breaking, deprecate before removing, and version or evolve by the chosen method.
- Where clients may retry a change (flaky networks, device apps), accept an idempotency key or make the operation naturally idempotent, so a retry cannot apply twice.
- If clients compose their own queries: limit depth and cost, authorize at the field level where fields differ in sensitivity, batch lookups per request so resolving a query does not issue a query per item, and accept only allow-listed queries from public or device clients. Evolve by deprecation.

## Violations

- Endpoints that name, shape or report errors each their own way.
- A read that changes data.
- Unvalidated input passed to the domain.
- A list that returns everything.
- A breaking change released to consumers the project does not control.
- A retried payment or message applied twice.
- A client-composed query with no depth or cost limit, or arbitrary queries accepted from public clients.

## Wrong vs Right

- WRONG: one endpoint returns a list and a total, another a result and a count, another a bare list. RIGHT: every endpoint returns the one recorded format.
- WRONG: a list endpoint returns fifty thousand records and the client crashes rendering them. RIGHT: the endpoint returns a page with what is needed to fetch the next.
- WRONG: a field is renamed and every released app version breaks. RIGHT: the new field is added, the old one deprecated and removed only after the consumers moved.
- WRONG: a device app retries a timed-out order and two orders are placed. RIGHT: the retry carries the same idempotency key and returns the first result.

## Research Notes

Research the API styles that fit the consumers, the chosen stack's routing, validation, paging and error-mapping options, the evolution practices for the chosen style, and, for client-composed queries, depth and cost limiting, allow-listing, field-level authorization and per-request batching. Record the style, the response format, the paging method, the error mapping and the evolution approach in References.md.
