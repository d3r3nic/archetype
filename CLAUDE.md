# Rules

Before any work: read Conventions.md then References.md

Everything is built once, configured for context. → conventions/00-reusability.md

## Enforcement

- Never build one-off. Use existing systems or build reusable. → conventions/00-reusability.md
- Never hardcode values that should come from configuration (colors, URLs, timeouts, dimensions, limits). → conventions/06-styling.md, conventions/01-project-setup.md
- Never import directly from third-party libraries without project wrappers. → conventions/22-design-system.md, conventions/03-architecture.md
- Never build standard UI components from scratch. Use the established UI library, configured and wrapped. → conventions/22-design-system.md
- Never scatter error handling. Use the centralized error system. → conventions/08-errors.md
- Never create ad-hoc API calls. Use the API layer. → conventions/09-api.md
- Never extract auth from JWT directly. Use the auth utility. → conventions/11-auth-security.md
- Never use `any` type. Use unknown and narrow. → conventions/07-types.md
- Never hardcode secrets or environment-specific values. → conventions/01-project-setup.md
- Never skip verification after changes. Run tests/build. → conventions/18-verification.md
- Never start multi-file changes without a plan. → conventions/19-steering.md
- Never modify existing systems without permission. → conventions/19-steering.md
- Read feature-tree.md before building anything new. Check what already exists. → templates/feature-tree.md
- Update feature-tree.md when adding or modifying features. → templates/feature-tree.md
- Update docs when changing features. → conventions/16-documentation.md
- If uncertain, ask. → conventions/19-steering.md

For project context, commands, and system locations → References.md
