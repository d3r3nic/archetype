# Convention #3: Code Architecture & Patterns

## Principle

Code is organized in layers with clear boundaries. Each layer has one job. Entry points (handlers, controllers, routes) are thin - they parse input, delegate to services, and return output. Business logic lives in services. Data access is abstracted behind its own layer. Features are self-contained and never import from each other.

## Reusable System

Create a layered architecture that establishes:
- A service layer where all business logic lives. Services are reusable across different entry points (API route, background job, CLI command can all use the same service).
- A data access layer that abstracts database operations. Features use the data layer, never raw queries.
- A shared directory for cross-feature code. When logic needs to be used by multiple features, it moves here.
- Module boundaries enforced through barrel exports. Each module's index file defines what's public. Everything else is private.

## Rules

- Entry points are thin. They parse input, call a service, return the response. No business logic in handlers or controllers.
- Business logic lives in services. Services are testable, reusable, and independent of the entry point.
- Features are self-contained. They never import from other features. If code needs sharing, move it to shared (ask first).
- Duplication between features is better than coupling between features. Coupling creates hidden dependencies.
- No circular dependencies. If module A imports from module B, module B must not import from module A.
- Build only what the spec says. Never add phantom requirements like batch mode, dry-run, or legacy format that nobody asked for. AI does this at a rate of 80-90%.
- Never call functions or modules that don't exist in the project. Verify imports exist before using them.

## Violations

- Business logic in a handler, controller, or UI component
- Feature A importing from Feature B's internals
- Circular dependencies between modules
- Utility functions scattered across random locations with no clear home
- Everything mixed in one file with no layer separation
- Over-specification: adding hypothetical code paths nobody asked for (batch mode, dry-run flags, legacy format support)
- Calling hallucinated helper functions or modules that don't exist in the project
- Never refactoring: adding new code without consolidating duplicate or similar logic

## Wrong vs Right

- WRONG: a handler fetches data from the database, filters it, calculates totals, formats the response, and sends an email. 200 lines of mixed concerns.
- RIGHT: the handler calls orderService.getActiveOrders(). The service handles filtering and calculation. The data layer handles the query. The email service handles notification. Each layer does one thing.
- WRONG: Feature A needs address validation. It imports validateAddress from Feature B's utils directory. Now Feature A breaks if Feature B changes.
- RIGHT: address validation moves to the shared directory. Both features import from shared. No coupling.
- WRONG: AI is asked to create a user. It also adds batch user creation, dry-run mode, and CSV import support that nobody requested.
- RIGHT: AI creates exactly what was asked. One user creation endpoint. Nothing more.

## Research Notes

When bootstrapping this convention:
- Research the framework's recommended architecture patterns for separating entry points, business logic, and data access
- Research module boundary patterns for the framework (how to define public APIs per module, how to prevent internal imports)
- Research the framework's dependency injection or service pattern for making services reusable across different entry points
- Document the layer structure, import rules, and shared directory in References.md
