# Convention #1: Project Setup

## Principle

A project's file structure, dependency strategy, and environment configuration determine how AI navigates and generates code. Feature-based organization with colocated files gives AI clear scope. Small focused files keep context windows manageable. Consistent structure lets AI predict where things belong without scanning the entire codebase.

## Reusable System

Create a project scaffold that establishes:
- A clear folder structure organized by feature, not by file type. Each feature owns all its related files (logic, types, tests, styles) in one directory.
- A shared directory for cross-feature foundational systems. Features import from shared, never from each other.
- Path aliases so imports are short and consistent across the entire project, not deep relative paths.
- Barrel exports (index files) that define each feature's and each shared module's public API. Internal files stay private.
- Environment variable validation that runs at startup. If a required variable is missing or malformed, the app fails immediately with a clear message rather than failing mysteriously at runtime.
- Dependency wrappers for third-party libraries. Every third-party library is wrapped behind a project interface so it can be swapped without changing feature code.

## Rules

- Organize by feature. Each feature directory contains everything that feature needs. Tests, types, styles, logic - all colocated.
- Keep files under 300 lines. If a file grows beyond this, split it. Small files load fully into AI context.
- One responsibility per file. Each file does one thing and exports one primary concept. AI loads exactly what it needs.
- Every feature has the same internal structure. Consistency lets AI predict where things are without exploring.
- Shared code lives in a dedicated shared directory. Features never import from other features. If something needs sharing, move it to shared.
- Evaluate dependencies before adding them. Check if the functionality already exists in current dependencies or the language's standard library. Prefer fewer, well-maintained dependencies over many small ones.
- Wrap third-party libraries. Never let feature code import a third-party library directly. Wrap it so the project can swap libraries without touching features.
- Never hardcode environment-specific values (URLs, API keys, ports, timeouts). Use environment variables with type-safe validation.
- Never expose secrets to client-side code. Server secrets stay on the server.

## Violations

- Files with 500+ lines mixing multiple concerns
- Organizing by type at the top level (all components in /components, all hooks in /hooks) instead of by feature
- Feature A importing from Feature B's internals
- Adding a dependency without checking if the functionality already exists
- Hardcoded API URLs, ports, or environment-specific values in source code
- Inconsistent feature structure (every feature organized differently)
- Third-party libraries imported directly in feature code without a wrapper
- Environment variables used without validation (missing var causes crash at runtime, not at startup)

## Wrong vs Right

- WRONG: all components in /components, all hooks in /hooks, all utils in /utils. To understand one feature, you jump across five directories.
- RIGHT: /features/auth contains auth components, auth hooks, auth types, auth tests. Everything for auth in one place.
- WRONG: importing a date library directly in 30 feature files. When you switch libraries, you change 30 files.
- RIGHT: one wrapper in shared that imports the date library. Features import from the wrapper. Switching libraries means changing one file.
- WRONG: environment variable used deep in a service. If it's missing, the app starts fine and crashes 10 minutes later when that code path runs.
- RIGHT: all environment variables validated at startup. If anything is missing, the app fails immediately with a clear error message.

## Research Notes

When bootstrapping this convention:
- Research the framework's recommended project structure. Look for feature-based organization patterns specific to the framework.
- Research path alias configuration for the framework's build tool. Set up short import paths from the start.
- Research environment variable validation libraries or patterns for the framework. Find a way to validate all variables at startup with type safety.
- Research the framework's module system and barrel export patterns. Understand how to define public APIs per module.
- Document the folder structure, path aliases, and environment setup in References.md.
