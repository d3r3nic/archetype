# Convention #7: Type Safety & Data Validation

## Applies when

Every project that handles data. What varies: whether the language checks types before running, at run time only, or both; and where outside data enters: requests, responses, files, user input, configuration, other services.

## Principle

Data that crosses into the program from outside is validated at the boundary, before anything trusts it. Each data shape has one definition. The type checks the project uses are never silenced to hide a real error. Types and validation are the contracts the next reader, human or AI, relies on, so they must say what is true.

## Reusable System

One definition per shared data shape, in one place, with the static type and the runtime validation derived from each other where the stack allows. Where it does not, one is generated from the other or a check keeps them in step (#0, #10). References.md records the checking level the project holds to, where shared shapes live, and how outside data is validated.

## Rules

- Validate every piece of outside data at the boundary where it enters: requests, responses, files, user input, environment values, messages from other services.
- Define each shared data shape once. Never maintain a hand-written type and a separate validation for the same data.
- Use the strongest checking the stack offers that the project keeps passing, and record the setting. New code meets it.
- Never use an untyped escape, a forced cast or a suppression comment to hide a real type error. Fix the cause: the call site, the shape, or the contract.
- Handle missing values explicitly rather than asserting they cannot happen.
- Make public contracts explicit: what goes in, what comes out, what can fail.
- Where two kinds of identifier or value can be confused (a customer number passed as an order number) and the stack can tell them apart cheaply, make them distinct.

## Violations

- Outside data used without validation because its shape was assumed.
- The same shape defined twice, once as a type and once as a validation, drifting apart.
- A cast, suppression or untyped escape added to make a type error disappear.
- A missing value asserted away instead of handled.
- A new client for a shared service created only to get around a type mismatch.

## Wrong vs Right

- WRONG: a response is used as if it had the expected shape; a different shape crashes it in production. RIGHT: the response is validated where it arrives, and a mismatch fails there with a clear message.
- WRONG: a user shape is written once as a type and again as a validation, and a new field is added to only one. RIGHT: one definition produces both.
- WRONG: a type error is silenced with a cast, and the program breaks at run time. RIGHT: find why the types disagree and fix the cause.

## Research Notes

Research the language's checking modes, how its runtime validation and static types can share one definition, and how it narrows unknown data after validation. Record the checking level, the validation approach and the shared-shape location in References.md.
