# Frontend scaffold: project setup and types

Part of the frontend scaffold playbook (scaffolding/SCAFFOLD-FRONTEND.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step. Before building, read the conventions it names and write how the system will be built in its References.md section (scaffolding/_preamble.md); when it lands, update its feature-tree.md row and its docs/systems/ page.

## Step 1: Project setup and types
Read: #1; #7; #2; scaffolding/_preamble.md § Convention-mapping rule; scaffolding/RED-FLAGS.md § 7. Env validation at runtime, not startup; scaffolding/RED-FLAGS.md § 16. Env-inlining breaks runtime env mutation in tests; scaffolding/RED-FLAGS.md § 13. Package versions pinned with expirable specifics
Produces: the project skeleton, the validated environment module, the type setup, the linter, the formatter, the pre-commit hook, and the commands recorded in References.md § Commands
Check: run project: typecheck, lint; evidence: what was seen when this was tried: the install, a commit firing the pre-commit hook, and the start failing with a required environment value removed

Build:
- Language/runtime version pinned, package manager chosen + lockfile committed.
- Type checker in strict mode, including the language's strictest available flags (e.g. unchecked indexed access, implicit override, unused locals).
- Linter + formatter configs. **Real rules, not stubs** — one linter config per language scope, extending the framework's recommended set. See "Wrapper-boundary enforcement" below.
- `.gitignore`, **pre-commit hooks that install automatically on fresh clone** so downstream forks inherit them without manual setup. Research current idiomatic tools for the chosen runtime.
- Environment validation AT STARTUP (`loadEnv()` equivalent on app entry). See `bootstrap/RED-FLAGS.md` "Env validation at runtime."
- Shared types directory, branded IDs, validation library wired in (one schema = type + validator).
- **Build script pattern:** typecheck and bundle run as separate steps. Never combine emit-to-disk with typecheck-only flags.
- **Monorepo template projects:** root package manifest uses the chosen tool's workspace protocol for cross-package deps. Publishing via the tool's publish command (or tarball packing for local testing). For local consumer-site testing of transitive deps, use the tool's resolution-override mechanism to redirect scoped-package resolutions to local tarballs — otherwise transitive deps try to resolve from a public registry that doesn't know your scope yet.

**Wrapper-boundary enforcement** — Convention #22 says feature code never imports UI-library internals directly. Enforce mechanically via the linter's import-restriction rule: every raw library the `@scope/ui` package wraps belongs on the restricted list for feature + app code. The list grows as you wrap more primitives. Research the linter's current restricted-imports rule syntax.

**Verify:** install succeeds, typechecker + linter run clean, pre-commit fires on commit (runs at least linter + formatter on staged source), deleting a required env var throws on start.
