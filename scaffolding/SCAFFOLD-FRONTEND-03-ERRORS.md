# Frontend scaffold: error handling

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 3: Error handling
Read: #8; #27 § Rules; scaffolding/_preamble.md § Convention-mapping rule; scaffolding/RED-FLAGS.md § 17. Class prototype broken on transpiled Error subclasses
Produces: the error classes, the error service, the boundaries, and a state component for every state of the #27 list that is a surface of a screen
Check: run project: typecheck, lint, build; evidence: what was seen when this was tried: an error thrown inside a component, and the network cut
Depends on: scaffold-frontend.2

Build:
- Error classes (NetworkError, ValidationError, NotFoundError, AuthError, etc.).
- Error service: catch, classify, log, report (to a crash/error reporting platform).
- Error boundary components (per-route and app-level).
- State components for every state in the list in #27 that is a screen surface (disabled and overflow are component behavior, #4); each says what happened, what to do, and what was kept.
- Unified loading components (full screen, inline, skeleton).

**Verify:** throwing an error inside a component is caught by the boundary and shows the fallback. Network errors display the offline UI, not a white screen.
