# Convention #9: API Integration & Data Fetching

## Applies when

The project's code calls a service over a network: its own server, another team's service, an outside provider, a live stream of updates. A program that calls nothing remote skips this convention. Building the API that others call is backend/conventions/B2-api-design.md.

## Principle

Each remote service is reached through one owner in the code: the client for that service. It holds the address, the caller's identity, the translation between the service's shapes and the project's, error normalization, and the retry and caching policy. Features ask it for what they need by domain action; they never assemble requests themselves. Every call goes to an endpoint the service's contract defines, never a guessed one.

## Reusable System

The API client for each service, or one layer that serves several, recorded in References.md with how features use it. § Boundaries records that only the client's location may use the network directly, so the checks keep features from going around it.

## Rules

- Features never call the network directly. They call the client by domain action (load the order, cancel the booking), never through a generic "send request".
- Endpoints, methods and shapes come from the service's contract (#10) or its current documentation. Verify that an endpoint exists before building on it.
- Translate at the boundary. The service's naming, dates and nesting become the project's shapes inside the client, and responses are validated there (#7). Features never see the raw format.
- Attach identity in one place. Secrets never reach code that people can inspect (#11, #23).
- Decide caching, refresh and invalidation once per kind of data, from how fresh it must be (#5), in the client or the chosen data layer.
- Retry only failures that are transient and safe to repeat (#8).
- Live update channels go through the same owner, which decides reconnection and ordering.

## Violations

- A feature building its own request, headers or error handling.
- Two features reaching the same service through two different paths.
- A call to an endpoint the contract does not define.
- The service's raw response format spread through feature code.
- Responses used without validation.
- Cached data with no rule for when it is stale.

## Wrong vs Right

- WRONG: ten features each call the service with hand-built headers and their own error handling. RIGHT: the client is configured once; a feature asks it for "the user's orders" and gets validated data and a clear error.
- WRONG: components dig through the service's nested response in many places. RIGHT: the client turns it into a flat shape at the boundary; a change in the service's format changes one place.
- WRONG: after creating a record, a feature refetches, patches three caches and navigates by hand. RIGHT: the data layer's recorded invalidation rule refreshes what depends on the change.

## File Upload & Download

Files follow the same rule: one file service handles transfers for every feature.
- Check type and size on the client for fast feedback, and again on the server, which reads the content, not the declared type (B6).
- Choose the path from the files and the storage: straight to storage when files are large and the storage supports it; through the server when the server must inspect or transform them, or when they are small.
- Do not block the person on a transfer unless they need its result to continue. Show progress where the product keeps it visible.
- One viewing component shows files to every feature that needs to.

## Research Notes

Research the chosen stack's client and data-fetching options: how each handles identity, translation, caching, cancellation, retry and live updates, and the storage options for file transfer. Record the client's location, its usage, the cache rules and the file service in References.md, and the network boundary in § Boundaries.
