# Frontend scaffold: error handling

Part of the frontend scaffold playbook (scaffolding/SCAFFOLD-FRONTEND.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step. Before building, read the conventions it names and write how the system will be built in its References.md section (scaffolding/_preamble.md); when it lands, update its feature-tree.md row and its docs/systems/ page.

## Step 3: Error handling
Read: #8; #27 § Rules; scaffolding/_preamble.md § Convention-mapping rule; scaffolding/RED-FLAGS.md § 17. Class prototype broken on transpiled Error subclasses
Produces: the error classes, the error service, the boundaries, and a state component for every state of the #27 list that is a surface of a screen
Check: run project: typecheck, lint, build; evidence: what was seen when this was tried: an error thrown inside a component, and the network cut

Build:
- Error classes (NetworkError, ValidationError, NotFoundError, AuthError, etc.).
- Error service: catch, classify, log, report (to a crash/error reporting platform).
- Error boundary components (per-route and app-level).
- State components for every state in the list in #27 that is a screen surface (disabled and overflow are component behavior, #4); each says what happened, what to do, and what was kept.
- Unified loading components (full screen, inline, skeleton).

**Verify:** throwing an error inside a component is caught by the boundary and shows the fallback. Network errors display the offline UI, not a white screen.
