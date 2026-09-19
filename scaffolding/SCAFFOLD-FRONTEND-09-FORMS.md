# Frontend scaffold: forms

Part of the frontend scaffold playbook (scaffolding/SCAFFOLD-FRONTEND.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step. Before building, read the conventions it names and write how the system will be built in its References.md section (scaffolding/_preamble.md); when it lands, update its feature-tree.md row and its docs/systems/ page.

## Step 9: Forms
Read: #20; #14; scaffolding/_preamble.md § Convention-mapping rule
Produces: the form foundation: validation, field-level errors, kept drafts
Check: run project: typecheck, lint, build; evidence: what was seen when this was tried: a sample form validating, showing field errors, and keeping its state across steps
Skip when: the product has no form

Build only if References.md lists forms beyond trivial inputs.
- Form library configured.
- Validation schema pattern (one schema = types + validation) using Step 1's validation library.
- Field components with accessible error display (aria-invalid, aria-describedby, labels).
- Multi-step wizard pattern if needed.

**Verify:** a sample form validates, shows field-level errors, preserves state across step navigation.
