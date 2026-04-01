# Phase 2: Scaffold

This phase builds the foundational systems described in References.md. Run after bootstrap. Each system is built following convention #0 (Reusability) - built once, configured for context, used by every feature.

## Prerequisites

- Phase 1 (Bootstrap) complete
- References.md exists with tech stack and system descriptions
- feature-tree.md initialized

## Scaffolding Prompt

Use this prompt with your AI assistant:

---

Read CLAUDE.md, Conventions.md, and References.md.

Build the foundational systems in this order. After each system:
1. Create the code
2. Write docs/systems/{system-name}.md documenting: what it is, where it lives, how features use it
3. Update feature-tree.md marking the system as implemented
4. Verify it works (run build/tests)

Systems to build (order matters - later systems depend on earlier ones):

1. PROJECT STRUCTURE (#1)
   - Folder structure per References.md
   - Path aliases configured
   - Barrel exports pattern established
   - Linting and formatting configured

2. THEME SYSTEM (#6)
   - Design tokens (colors, spacing, typography, shadows, z-index, breakpoints)
   - Theme object as single source of truth
   - UI library wrappers (never import directly)
   - Dark mode support if needed

3. ERROR SYSTEM (#8)
   - Error classes (NetworkError, ValidationError, NotFoundError, AuthError)
   - Error service (catch, classify, log, report)
   - Error boundary components (app, route, feature level)
   - Error UI components (fallback, empty state, offline, loading)
   - Unified loading components (full screen, inline, skeleton)

4. API LAYER (#9)
   - Configured client instance (base URL, interceptors)
   - Auth token attachment
   - Request/response transformation
   - Data fetching library integration
   - Cache strategy configured

5. AUTH SYSTEM (#11)
   - Auth service (token storage, refresh, logout cleanup)
   - Auth context/provider
   - Route guard component
   - Auth utility function

6. STATE MANAGEMENT (#5)
   - Store configuration
   - Slice pattern template
   - Server state integration with API layer

7. COMPONENT FOUNDATION (#4)
   - Base wrapper components for UI library
   - Layout components (Stack, Grid, Page containers)
   - Consistent component API patterns documented

8. FORM SYSTEM (#20) (if project uses forms)
   - Form library configured
   - Validation schema pattern
   - Form field components with error display
   - Multi-step wizard if needed

9. TESTING SETUP (#12)
   - Test runner configured
   - Custom render wrapper with providers
   - MSW setup for API mocking
   - Test data factories

10. CI/CD (#15)
    - Lint + typecheck + test + build pipeline
    - Pre-commit hooks

---

## System Documentation Template

Each system gets a doc at docs/systems/{system-name}.md:

```
# {System Name}

Convention: #{number} ({convention name})

## What It Is
[One paragraph explaining the system]

## Where It Lives
[Exact file paths]

## How Features Use It
[Import pattern and usage example]

## Configuration
[How to extend or configure for different contexts]
```

## Checklist

After scaffolding, verify:

- [ ] All foundational systems created and working
- [ ] docs/systems/ has a doc for each system
- [ ] feature-tree.md shows all systems as implemented with paths
- [ ] References.md updated with actual paths (if they changed from plan)
- [ ] Build passes
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Base test suite passes

## What Scaffolding Produces

A working, empty project with all foundational systems in place. No features yet. But any feature can be built immediately by plugging into these systems.

This scaffolding is REUSABLE. Projects with the same tech stack can start from this base. Store it as a template repo.

## Scaffolding Documentation

The scaffolding phase itself should be documented as it happens. Every decision made during scaffolding that deviates from the conventions or makes a stack-specific choice should be recorded in References.md under "Convention Overrides."
