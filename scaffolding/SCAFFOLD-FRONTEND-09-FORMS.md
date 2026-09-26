# Frontend scaffold: forms

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 9: Forms
Read: #20; #14; scaffolding/_preamble.md § Convention-mapping rule
Produces: the form system: validation from the one shape definition, errors at their fields, kept drafts
Check: run project: typecheck, lint, build; evidence: what was seen when this was tried: a sample form validating, showing field errors, and keeping its state across steps
Depends on: scaffold-frontend.4; scaffold-frontend.5
Skip when: the product has no form

Apply #20 through the recorded decisions: the one form system every form uses, validation from the data's one shape definition (#7), field components whose errors are tied to their fields for assistive technology, server errors mapped onto fields, drafts kept or a warning before leaving, and steps for a long form when the product needs them.

**Verify:** a sample form validates, shows each error at its field, maps a server error onto its field, and keeps what was typed across steps.
