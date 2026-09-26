# Frontend scaffold: error handling

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 3: Error handling
Read: #8; #27 § Rules; scaffolding/_preamble.md § Convention-mapping rule; scaffolding/RED-FLAGS.md § 17. Custom error types broken by the build target
Produces: the one error system for this interface, and the shared state components for every state of the #27 list that is a surface of a screen
Check: run project: typecheck, lint, build; evidence: what was seen when this was tried: an error thrown inside a component, and the network cut
Depends on: scaffold-frontend.2

Apply #8 through the recorded decisions, researching the chosen stack's error-catching levels where the record is silent:
- The error system: the kinds of error the product distinguishes, where they are recorded and reported (a reporting service chosen for the stage and cost, #30), and how each becomes what the person sees.
- The boundaries that catch a failure while a screen renders, at the levels the stack offers (the whole app, a route or screen), each showing a state instead of nothing.
- The shared state components for every state of the #27 list that is a screen surface (disabled and overflow belong to components, #4). Each says what happened, what the person can do, and what was kept. Screens reuse them; none builds its own.

Verify that the error types survive the real build target (RED-FLAGS 17).

**Verify:** an error thrown inside a component is caught and shows the fallback state; cutting the network shows the offline state, not a blank screen.
