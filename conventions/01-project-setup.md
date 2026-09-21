# Convention #1: Project Setup

## Principle

A project's structure should make responsibilities, dependencies and verification easy to find. Choose a layout that fits its runtime, delivery model and existing work. Predictability is valuable; imposing the same folder structure on every project is not.

## Reusable System

Record the chosen entry points, source and test locations, dependency boundaries, configuration sources and verification commands in References.md. Reuse an existing sound structure. For a new project, compare the runtime's maintained conventions with the product's likely units of change before creating folders or wrappers.

## Rules

- Organize related responsibilities so the next change has a discoverable scope. Feature folders, layers, packages and runtime-native layouts are options to evaluate, not mandatory shapes.
- Keep modules understandable and readable with the tools in use. Split by responsibility when complexity or navigation warrants it; a shorter file alone does not establish better design.
- Use public interfaces and import conventions appropriate to the language and dependency graph. Choose aliases, index modules or explicit imports based on actual navigation and tooling needs.
- Evaluate dependencies against the standard library and installed capabilities, current maintenance, compatibility and the project's constraints.
- Add a wrapper when it provides a meaningful policy, lifecycle or integration boundary. A direct dependency can be appropriate when another abstraction would add no useful contract.
- Identify external configuration and validate required values before dependent behavior runs. Keep deployment-specific values out of source where changing environments would require code changes.
- Never expose secrets to clients or commit credentials. Keep trust boundaries explicit.
- Preserve an existing repository's history and local guidance during adoption; follow bootstrap/REPOSITORIES.md. Record consequential structural changes and affected consumers (#3, #16, #29).

## Violations

- Reorganizing a working project to imitate a template without a demonstrated benefit
- Creating wrapper modules that only repeat every dependency operation and carry no project policy
- Letting invalid required configuration cause a late, obscure failure
- Scattering one responsibility across unrelated locations without a discoverable entry point

## Wrong vs Right

- WRONG: move an established runtime-native layout into feature folders because the framework example uses them. RIGHT: examine navigation and change boundaries; preserve or revise the layout with evidence.
- WRONG: access a missing service address deep in a request. RIGHT: validate the required configuration before enabling that service and report an actionable error.
- WRONG: hide a secret in client configuration. RIGHT: keep the secret within the trusted boundary and expose only the capability the client may use.

## Research Notes

Dated notes: anything named in this section is an example from the time of writing and expires. Verify current options at bootstrap.

Investigate the chosen runtime's maintained structure, module-resolution and configuration patterns where they affect this project. Check migration costs before changing existing conventions. Record the selected paths and commands in References.md; avoid generating unused folders from a generic checklist.
