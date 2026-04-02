# Convention #7: Type Safety & Type System

## Principle

The type system is the first line of defense against bugs and the primary documentation for AI. Strict typing eliminates entire categories of runtime errors. Data from external sources (API responses, user input, environment variables) is validated at runtime with schema libraries. Richer types produce better AI output because they communicate contracts explicitly. One schema definition produces both the type and the validation - never maintain them separately.

## Reusable System

Create a type safety foundation that establishes:
- Strict type checking configuration for the project (the strictest mode the language supports)
- A validation schema library configured and integrated. One schema definition produces both the type and the runtime validation. Never write a type interface AND a validation schema separately for the same data.
- Shared type definitions for concepts used across the project (user types, common response shapes, ID types)
- Branded or opaque ID types that prevent accidentally passing one kind of ID where another is expected (a user ID where an order ID is expected, for example)

## Rules

- Enable the strictest type checking mode the language supports.
- Never use "any" or the language's equivalent of an untyped escape hatch. Use the "unknown" equivalent and narrow with type guards.
- Validate all data from external sources at boundaries (API responses, user input, environment variables) using the schema library. Never trust external data.
- One schema = types + validation. Define the schema once, derive the type from it. Never maintain a separate type definition and a separate validation schema for the same data.
- Explicit return types on all public/exported functions. This documents the contract and prevents accidental return type changes.
- Never use non-null assertions to bypass null checks. Handle the null case properly.
- Never use type assertions to silence real type errors. Fix the underlying type issue.

## Violations

- "any" used anywhere in production code
- API response used without runtime validation (trusting external data shape)
- Separate type definition AND validation schema for the same data structure (they drift apart)
- Type assertion used to silence a real type error instead of fixing it
- Non-null assertion used to bypass a null check instead of handling the null case
- Missing return type on an exported function

## Wrong vs Right

- WRONG: a function accepts "any" and accesses properties without checking. Works in development, crashes in production when the API returns a different shape.
- RIGHT: a function accepts "unknown" and validates it against a schema at the boundary. If the data doesn't match, the error is caught immediately with a clear message.
- WRONG: a User type defined as a TypeScript interface, and separately a UserSchema defined as a Zod/validation schema, with the same fields listed twice. When a field is added to one, the other is forgotten.
- RIGHT: a UserSchema defined once in the validation library. The User type is derived from the schema automatically. One source of truth.
- WRONG: a type error appears. AI adds "as SomeType" to make it go away. The underlying issue remains. It breaks at runtime.
- RIGHT: a type error appears. The developer investigates why the types don't match, fixes the root cause. The types accurately represent the data.

## Research Notes

When bootstrapping this convention:
- Research the language's strict mode configuration options. Enable the maximum strictness.
- Research runtime validation libraries for the language/framework. Find one that integrates well and can derive types from schemas (or vice versa).
- Research branded/opaque type patterns for the language. How do you create ID types that are structurally different from plain strings?
- Research the language's type narrowing patterns (type guards, discriminated unions, pattern matching)
- Document the type checking config, validation library, shared types location, and patterns in References.md
