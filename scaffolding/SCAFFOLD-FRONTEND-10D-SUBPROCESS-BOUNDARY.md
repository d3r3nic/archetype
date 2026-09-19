# Frontend scaffold: subprocess input boundary

Part of the frontend scaffold playbook (scaffolding/SCAFFOLD-FRONTEND.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step. Before building, read the conventions it names and write how the system will be built in its References.md section (scaffolding/_preamble.md); when it lands, update its feature-tree.md row and its docs/systems/ page.

## Step 10d: Subprocess input boundary
Read: #23
Produces: the safe-identifier check at the boundary of every value that reaches a subprocess or a shell-like call
Check: run project: typecheck, lint, test, build; evidence: what was seen when this was tried: an unexpected character sent to that boundary
Skip when: nothing in the product starts a subprocess or a shell command

Every value that reaches `spawn()`, `exec()`, or any shell-like API **must pass a safe-ident regex first.** Reject at the API boundary, not at use site. Even when using argv (no shell), fail closed on unexpected characters — it's a second line of defense that costs almost nothing.
