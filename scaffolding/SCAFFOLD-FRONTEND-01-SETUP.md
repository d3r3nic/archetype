# Frontend scaffold: project setup and types

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 1: Project setup and types
Read: #1; #7; #2; #15; scaffolding/_preamble.md § Convention-mapping rule; scaffolding/RED-FLAGS.md § 7. Env validation at runtime, not startup; scaffolding/RED-FLAGS.md § 16. Env-inlining breaks runtime env mutation in tests; scaffolding/RED-FLAGS.md § 13. Package versions pinned with expirable specifics
Produces: the project skeleton, the configuration owner that validates required values at startup, the type setup, the formatter and linter, where the checks run before merge, the commands recorded in References.md § Commands, and the configuration line in References.md § Boundaries
Check: run project: typecheck, lint; evidence: what was seen when this was tried: the install, the recorded checks running where they are recorded to run, and the start failing with a required environment value removed

Apply the setup the bootstrap recorded, researching current practice for the chosen stack where the record is silent:
- The runtime and package manager pinned, with the lock file committed.
- Type checking at the strongest level the project will keep passing, recorded (#7).
- A formatter and a linter with real rules for the mistakes this project must not make (#15, #25), not empty configurations.
- Where the checks run before work reaches the main line, chosen for the stage: a hook that installs itself on every fresh clone, a pipeline, or both (#2, #15). Record it in References.md.
- Configuration's one owner: it reads the environment, validates every required value at startup, and hands values to the rest of the code (#1). Record `` - Configuration: `<pattern that reads the environment>` only in `<its path>` `` in References.md § Boundaries.
- The shared data shapes and the one validation approach for outside data (#7).
- Typecheck and bundling as separate steps, so a check never writes build output.

Where the project selected a restricted import boundary for its interface (#22), enforce it with the toolchain and test the rule. Where direct use was selected, do not add a restriction that contradicts it.

**Verify:** the install succeeds; the type check and the linter run clean; the checks run where the project recorded them; removing a required environment value makes the start fail with a message naming it.
