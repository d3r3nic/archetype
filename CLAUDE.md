# Rules

Do not assume you remember conventions from a previous session. Re-read what's relevant every time.

If References.md does not exist, bootstrap has not run yet. Read bootstrap/ONBOARD.md (or archetype/bootstrap/ONBOARD.md) and run bootstrap first. Do not write code without project context.

## Before Any Work

1. Read References.md and feature-tree.md (always — these are project context)
2. Scan Conventions.md to identify which conventions apply to the current task (it's a lookup index, not a reading list — read ONLY the relevant convention docs, not all 25)
3. If conventions/overrides/, protocols/, or catalogs/ directories exist, check for project-specific rules relevant to the task

Note: if framework files are in an archetype/ subfolder, read from there (archetype/Conventions.md, archetype/References.md, etc.)

## Before Writing Code

Identify which conventions apply to your task. Read those specific convention docs. Before your first code output in a session, state which conventions you read and confirm they apply.

If the task scope expands to touch new areas mid-task, re-scan Conventions.md and read the newly relevant conventions before continuing.

Do not skip this step. Do not write code based on the enforcement rules alone — they catch mistakes but don't explain how the systems work. The convention docs do.

## Enforcement

Everything is built once, configured for context. Before building anything, check what exists. If a system exists, use it and configure it for your context. If not, build it as a reusable service, not a one-off. → conventions/00-reusability.md

- If uncertain, ask. Do not guess, do not assume. → conventions/19-steering.md
- Never build one-off. Use existing systems or build reusable. → conventions/00-reusability.md
- Never hardcode values that should come from configuration (colors, URLs, timeouts, dimensions, limits). → conventions/06-styling.md, conventions/01-project-setup.md
- Never import directly from third-party libraries without project wrappers. → conventions/22-design-system.md, conventions/03-architecture.md
- Never build standard UI components from scratch. Use the established UI library, configured and wrapped. → conventions/22-design-system.md
- Never scatter error handling. Use the centralized error system. → conventions/08-errors.md
- Never create ad-hoc API calls. Use the API layer. → conventions/09-api.md
- Never extract auth from JWT directly. Use the auth utility. → conventions/11-auth-security.md
- Never use `any` type. Use unknown and narrow. → conventions/07-types.md
- Validate all user input at entry points. Never trust client data. → conventions/23-app-security.md
- Authorization checks at the service layer, not UI. Verify the user can access the specific resource. → conventions/24-authorization.md
- Never hardcode secrets or environment-specific values. → conventions/01-project-setup.md
- Never skip verification after changes. Run tests/build. → conventions/18-verification.md
- Commit after every verified change. Each commit is a rollback point. → conventions/02-git.md
- Never start multi-file changes without a plan. → conventions/19-steering.md
- Never modify existing systems without permission. → conventions/19-steering.md
- Never modify CLAUDE.md, Conventions.md, or convention docs without explicit permission.
- Read feature-tree.md before building anything new. Check what already exists.
- Search the codebase for existing implementations before building. feature-tree.md may be stale — the code is the source of truth.
- Update feature-tree.md when adding or modifying features.
- Update docs when changing features. → conventions/16-documentation.md

For project context, commands, and system locations → References.md

If this is a backend project, also read backend/CLAUDE.md and scan backend/Conventions.md.
If this is a frontend project, also read frontend/CLAUDE.md and scan frontend/Conventions.md (when available).
