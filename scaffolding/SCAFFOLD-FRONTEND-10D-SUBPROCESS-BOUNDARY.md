# Frontend scaffold: subprocess input boundary

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 10d: Subprocess input boundary
Read: #23; scaffolding/_preamble.md § Convention-mapping rule
Produces: the safe-identifier check at the boundary of every value that reaches a subprocess or a shell-like call
Check: run project: typecheck, lint, test, build; evidence: what was seen when this was tried: an unexpected character sent to that boundary
Skip when: nothing in the product starts a subprocess or a shell command

Every value that reaches a call that starts a process or runs a shell command passes a safe-identifier check first, at the API boundary, not where it is used. Even when arguments are passed as a list with no shell, fail closed on unexpected characters: a second line of defense that costs almost nothing.
