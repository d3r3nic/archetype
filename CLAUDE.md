# Rules

Before any work: read Conventions.md then References.md

Everything is built once, configured for context. → conventions/00-reusability.md

## Enforcement

- Never build one-off. Use existing systems or build reusable. → conventions/00-reusability.md
- Never hardcode colors, spacing, dimensions. Use the theme system. → conventions/06-styling.md
- Never import directly from UI libraries. Use project wrappers. → conventions/22-design-system.md
- Never scatter error handling. Use the centralized error system. → conventions/08-errors.md
- Never create ad-hoc API calls. Use the API layer. → conventions/09-api.md
- Never extract auth from JWT directly. Use the auth utility. → conventions/11-auth-security.md
- Never hardcode secrets or environment-specific values. → conventions/01-project-setup.md
- Never skip verification after changes. Run tests/build. → conventions/18-verification.md
- Never start multi-file changes without a plan. → conventions/19-steering.md
- Never modify existing systems without permission. → conventions/19-steering.md
- If uncertain, ask. → conventions/19-steering.md

For project context, commands, and system locations → References.md
