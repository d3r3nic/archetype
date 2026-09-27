# Convention #15: Build, CI/CD & Code Quality

## Applies when

Every project that builds, checks or ships code. What varies is the stage (#30): an isolated experiment may run its checks through the step runner on one machine; a product others use runs them automatically before every merge and ships with a way back. Where the product ships (a server, an app store, a package registry, a device) shapes the release path.

## Principle

The project's checks decide what merges: code that fails them does not reach the main line. The checks are the ones this project needs, automated as soon as more than one person or one session depends on them, and they keep the codebase free of bloat. Anything people depend on ships with a way back.

## Reusable System

The project's pipeline: the checks it runs (formatting, linting, types, tests, build, and any size or performance budget the product needs), where they run (a hook, a pipeline, or the step runner), what a merge requires, how a release happens, and how it is undone. References.md records each, with the commands in § Commands.

## Rules

- Merge only what passes the project's recorded checks.
- Automate the checks once more than one person or one session works on the code, or once others depend on the result. Before that, run them through the step runner or by hand, and say so.
- Where the stack has a formatter, formatting is automated and checked, never argued over.
- Configure lint rules for the mistakes this project has actually made or is likely to make, and record why a rule exists. Rules that only add noise are removed.
- Remove dead code, unused dependencies and finished feature flags. A flag exists only while a rollout needs it.
- Add a size or performance budget where a regression would matter to the product (#13), measured the same way every time.
- A release that people depend on can be undone quickly, and the way back is known before the release.
- Know which push or merge releases, and follow the owner's authority for anything that spends money or reaches people (#29).

## Violations

- A failing change merged.
- Checks that exist but that nothing runs.
- Formatting disputes in review that a formatter would settle.
- Dead code, unused dependencies or finished flags left in place.
- A release people depend on with no way back.

## Wrong vs Right

- WRONG: every project copies one fixed pipeline, preview environments and all, whatever its stage. RIGHT: the pipeline carries the checks this project needs now and grows when the facts change.
- WRONG: a shipped feature's flag and both code paths stay for months. RIGHT: when the rollout is done, the flag and the dead path go in the same change.
- WRONG: the default lint rules only, while the same mistake keeps reaching review. RIGHT: a rule that catches that mistake, recorded with its reason.

## Research Notes

Research the chosen stack's formatter, linter, type checker and test runner, the pipeline options for where the project is hosted, and the release and rollback mechanisms of the platforms it ships to. Record the checks, where they run, the budgets and the release path in References.md.
