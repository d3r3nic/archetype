# Convention #1: Project Setup

## Applies when

Every project. What varies: the runtime's own layout conventions, whether the repository is new or already has working structure, and whether the product is one unit or several (a client and a server, several services, a library and its consumers).

## Principle

A project's structure makes responsibilities, dependencies and verification easy to find. Choose the layout from the runtime's maintained conventions and the product's units of change. Never impose one folder layout on every project, and never reorganize a working project without a demonstrated benefit.

## Reusable System

References.md records the entry points, source and test locations, dependency boundaries, configuration source and verification commands. Configuration has one owner: one place reads the environment and validates it, and the rest of the code receives values from that place. Its § Boundaries line keeps other code from reading the environment directly.

## Rules

- Organize related responsibilities so the next change has a discoverable scope. Feature folders, layers, packages and runtime-native layouts are options to weigh, not mandatory shapes.
- Split a module by responsibility when its complexity or navigation calls for it. A shorter file alone is not a better design.
- Choose public interfaces and import conventions that fit the language and its dependency graph.
- Before adding a dependency, check the standard library and what is already installed, then its maintenance, compatibility and cost.
- Add a wrapper when it carries a real policy, lifecycle or integration boundary. A wrapper that only repeats a dependency's operations is bloat.
- Validate required configuration before the behavior that needs it runs, and fail with an actionable message. Keep values that differ between environments out of source.
- Never expose secrets to clients or commit credentials. Keep trust boundaries explicit.
- Preserve an existing repository's history and local guidance during adoption (bootstrap/REPOSITORIES.md). Record consequential structural changes and their affected consumers (#3, #16, #29).

## Violations

- Reorganizing a working project to imitate a template, with no demonstrated benefit.
- Wrapper modules that only repeat a dependency's operations and carry no project policy.
- Required configuration read in many places, or invalid configuration failing late and obscurely.
- One responsibility scattered across unrelated locations with no discoverable entry point.

## Wrong vs Right

- WRONG: move an established runtime-native layout into feature folders because an example used them. RIGHT: examine navigation and change boundaries, then keep or revise the layout with evidence.
- WRONG: read a missing service address deep inside a request. RIGHT: validate required configuration at startup, in its one owner, and report what is missing.
- WRONG: put a secret in client configuration. RIGHT: keep the secret inside the trusted boundary and expose only the capability the client may use.

## Research Notes

Research the chosen runtime's maintained structure, module resolution and configuration patterns where they affect this project, and the cost of migrating an existing layout before changing it. Record the paths and commands in References.md and the configuration boundary in § Boundaries. Do not generate folders from a generic checklist.
