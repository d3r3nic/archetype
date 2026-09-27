# Convention #10: Frontend-Backend Contract

## Applies when

Two separately built parts exchange data: a client and its server, two services, an application and a library it publishes. It applies whether they live in one repository or several. A program with no such boundary skips this convention.

## Principle

Both sides of a boundary use one source of truth for the shapes they exchange, and a breaking change is caught before any consumer meets it. The API's responses follow one format, chosen once, for data, errors and paging alike. A shape written by hand on both sides will drift.

## Reusable System

The contract: one definition of the exchanged shapes, the form of which the project chooses (a specification, a shared schema package, a typed call layer, or generation from one side), recorded in References.md. It also records how each side gets its types from it, the one response format, and the check that detects a breaking change before merge.

## Rules

- Define exchanged shapes once. Never write the same shape by hand on both sides.
- Derive each side's types from the contract, by generation or sharing. Where neither is possible, a check compares the two.
- Use one response format across the API, for success, errors and paging, and record it. Every endpoint keeps to it.
- Detect breaking changes in the project's checks before merge, and handle them through #19 when others depend on the interface.
- Translate at the boundary (#9): consumers work with clean shapes, not the raw response structure.

## Violations

- The same shape written by hand on both sides.
- A breaking change that no check catches before release.
- Endpoints that each return a differently shaped result or error.
- A contract change released without its consumers updated.

## Wrong vs Right

- WRONG: the server adds a field to a shape that the client wrote separately; the client breaks on data it did not expect. RIGHT: one definition; both sides get the change through generation or sharing, and the check shows what changed.
- WRONG: one endpoint returns a list and a total, another a result and a count, another something else again. RIGHT: one recorded response format; one way to read every endpoint.

## Research Notes

Research the contract options for the chosen stack: specification formats, shared schema packages, typed call layers, generators, and tools that compare two versions of a contract. Record the contract's location, the response format and the breaking-change check in References.md.
