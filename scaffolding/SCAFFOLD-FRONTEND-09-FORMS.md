# Frontend scaffold: forms

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 9: Forms
Read: #20; #14; scaffolding/_preamble.md § Convention-mapping rule
Produces: the form foundation: validation, field-level errors, kept drafts
Check: run project: typecheck, lint, build; evidence: what was seen when this was tried: a sample form validating, showing field errors, and keeping its state across steps
Depends on: scaffold-frontend.4; scaffold-frontend.5
Skip when: the product has no form

Build only if References.md lists forms beyond trivial inputs.
- Form library configured.
- Validation schema pattern (one schema = types + validation) using Step 1's validation library.
- Field components with accessible error display (aria-invalid, aria-describedby, labels).
- Multi-step wizard pattern if needed.

**Verify:** a sample form validates, shows field-level errors, preserves state across step navigation.
