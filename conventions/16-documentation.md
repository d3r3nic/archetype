# Convention #16: Documentation & Decisions

## Principle

Documentation captures what code cannot express: intent, constraints, business reasoning, and architectural decisions. Comments explain WHY, never WHAT. AI over-comments 90-100% of generated code with obvious descriptions - this convention corrects that. Documentation that matters is specifications, decision records, and constraint explanations. Documentation that wastes time restates what the code already says.

## Reusable System

Create a documentation system that establishes:
- An architecture decision record (ADR) template for recording significant decisions with context, reasoning, and trade-offs
- A feature documentation template that every feature fills out: what it does, why it exists, how it integrates, and what decisions were made
- A naming convention: descriptive names that communicate purpose without abbreviations. AI and humans should be able to understand an identifier without context.
- A structured TODO format that links to tracking systems so TODOs are actionable, not forgotten

## Rules

- Comments explain WHY or provide constraints. Never explain WHAT the code does. If the code needs a comment to explain what it does, the code should be rewritten to be clearer.
- If code is self-explanatory, no comment needed. Most code is self-explanatory.
- Every feature has documentation that explains what it does, why it exists, and how it works from a business perspective. Updated after every change. Stale documentation is worse than no documentation.
- Architecture decisions are recorded with context, reasoning, and trade-offs. When someone asks "why did we choose X over Y?" the answer exists in the decision record, not in someone's memory.
- Descriptive naming over brevity. Names that communicate purpose without requiring context. No abbreviations except universally understood ones.
- Magic numbers have explanations. If a timeout is 3000ms, a comment explains why 3000 (the payment gateway SLA requires response within 3 seconds). The number isn't magic anymore.
- Structured TODOs link to tracking: // TODO(scope): description [TICKET-123]. Not bare TODO comments that are never addressed.

## Violations

- Comments explaining what the code does: "// Initialize the user array," "// Loop through each order," "// Check if total is greater than 100"
- Stale documentation that describes a previous version of the code
- Magic numbers with no explanation: TIMEOUT = 3000 (why 3000?), MAX_RETRIES = 5 (why 5?), BATCH_SIZE = 50 (why 50?)
- Domain abbreviations that only insiders understand
- Features with no documentation explaining why they exist
- Bare TODO comments with no ticket reference or context
- Over-commenting: a JSDoc block on every function describing obvious parameters and return values

## Wrong vs Right

- WRONG: every line has a comment. "Initialize the user array." "Loop through each order." "Get the order total." The comments describe what the code already says. They add noise, not value.
- RIGHT: one comment on the business rule that isn't obvious from the code. "Orders over $100 qualify for the loyalty discount per the 2024 partnership agreement (JIRA-1234)." The code shows the logic, the comment explains why.
- WRONG: TIMEOUT = 3000 with no explanation. Someone changes it to 5000 because "bigger is safer." The original value was chosen because the payment gateway's SLA is 3 seconds. Now payments sometimes hang for 5 seconds unnecessarily.
- RIGHT: "Payment gateway SLA requires response within 3 seconds. Exceeding this triggers the fallback payment processor." The next developer understands the constraint and doesn't change it arbitrarily.
- WRONG: a 15-line JSDoc comment on a function called getUserById that documents every parameter and the return type. The function name and types already communicate everything the JSDoc says.
- RIGHT: no comment needed. The function name, parameter types, and return type are the documentation.

## Documentation Formatting

AI-generated documentation wastes tokens on visual formatting that adds no value for AI consumption. Documentation should be optimized for content, not presentation.

Rules:
- No emojis in documentation or code comments. They consume tokens and add no information.
- Minimal markdown formatting. Use plain text headings (Heading: not # Heading) in feature docs where heavy formatting adds overhead. Convention docs and framework docs use markdown for structure.
- No bold or italic for emphasis in feature documentation. If something is important, say it is important in words.
- Focus documentation on content density. Every line should deliver information the reader (human or AI) cannot get from the code itself.

This reduces AI token consumption by 30-40% on documentation files and speeds up parsing.

## Research Notes

When bootstrapping this convention:
- Research ADR (Architecture Decision Record) template formats recommended for the framework or team size
- Research the framework's documentation tooling (component catalogs, API documentation generators)
- Research naming conventions specific to the framework and language
- Set up feature documentation templates and link them to the feature development workflow (convention #19 steering, DEVELOP.md)
- Document the ADR location, documentation templates, naming conventions, and formatting rules in References.md
