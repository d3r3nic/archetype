# Frontend scaffold: design-system and component foundation

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 4: Design-system and component foundation
Read: #4; #22; #14; #31; #27 § Design review; scaffolding/_preamble.md § Convention-mapping rule
Produces: the selected interface foundation and consumer boundary, the components the smoke test and artifact require, their discovery surface, focus behavior, state gallery, and the capture command recorded in References.md § Commands
Check: run project: typecheck, lint, build, capture; evidence: the selected interface pattern exercised on the test surface, its boundary check where one was chosen, and what the captures show
Depends on: scaffold-frontend.2; scaffold-frontend.3
Basis: decisions and inputs required

Build:
- Apply the interface-foundation decision recorded through the preamble: research current options where the record is silent, build only what the artifact and smoke feature require, preserve actual input and accessibility behavior, keep the result discoverable, capture every applicable state in committed schemes and contexts, and enforce only the boundary the project selected.

**Verify:** a test surface uses the project's selected interface pattern and completes its actual interactions. The project commands and any selected boundary check pass. Captures cover every applicable state in every committed scheme and context, and observed focus and input behavior meet the accessibility target.
