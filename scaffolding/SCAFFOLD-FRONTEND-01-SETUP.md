# Frontend scaffold: project setup and types

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 1: Project setup and types
Read: #1; #7; #2; scaffolding/_preamble.md § Convention-mapping rule; scaffolding/RED-FLAGS.md § 7. Env validation at runtime, not startup; scaffolding/RED-FLAGS.md § 16. Env-inlining breaks runtime env mutation in tests; scaffolding/RED-FLAGS.md § 13. Package versions pinned with expirable specifics
Produces: the project skeleton, the validated environment module, the type setup, the linter, the formatter, the pre-commit hook, and the commands recorded in References.md § Commands
Check: run project: typecheck, lint; evidence: what was seen when this was tried: the install, a commit firing the pre-commit hook, and the start failing with a required environment value removed

Build:
- Language/runtime version pinned, package manager chosen + lockfile committed.
- Type checker in strict mode, including the language's strictest available flags (e.g. unchecked indexed access, implicit override, unused locals).
- Linter + formatter configs. **Real rules, not stubs** - one linter config per language scope, extending the framework's recommended set. See "Selected-boundary enforcement" below.
- `.gitignore`, **pre-commit hooks that install automatically on fresh clone** so downstream forks inherit them without manual setup. Research current idiomatic tools for the chosen runtime.
- Environment validation AT STARTUP (`loadEnv()` equivalent on app entry). See `bootstrap/RED-FLAGS.md` "Env validation at runtime."
- Shared types directory, branded IDs, validation library wired in (one schema = type + validator).
- **Build script pattern:** typecheck and bundle run as separate steps. Never combine emit-to-disk with typecheck-only flags.
- **Monorepo template projects:** root package manifest uses the chosen tool's workspace protocol for cross-package deps. Publishing via the tool's publish command (or tarball packing for local testing). For local consumer-site testing of transitive deps, use the tool's resolution-override mechanism to redirect scoped-package resolutions to local tarballs — otherwise transitive deps try to resolve from a public registry that doesn't know your scope yet.

**Selected-boundary enforcement** - Convention #22 requires the project to record its interface boundary. If the project selects adapters, wrappers, or another restricted import surface, enforce that boundary with the current toolchain and test the rule. If direct native or library use is selected, do not manufacture a restricted-import rule that contradicts it.

**Verify:** install succeeds, typechecker + linter run clean, pre-commit fires on commit (runs at least linter + formatter on staged source), deleting a required env var throws on start.
