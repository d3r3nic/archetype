# Convention #1: Project Setup

## Principle

A project's file structure, dependency strategy, and environment configuration determine how AI navigates and generates code. Feature-based organization with colocated files gives AI clear scope. Small focused files keep context windows manageable. Consistent structure lets AI predict where things belong without scanning the entire codebase.

AI-era reasoning: folder structure is how AI scopes its context window. Inconsistent structure forces exploration that wastes tokens. Small files (<300 lines) load fully into context. Consistent patterns let AI predict file locations.

## Reusable System

- Project scaffold: established folder structure with clear conventions
- Path aliases: configured once, used everywhere (@/ or ~/)
- Barrel exports: index files that define each feature's public API
- Environment validation: type-safe env var checking at startup
- Dependency wrappers: third-party libraries wrapped behind project interfaces

## Rules

- Group by feature, not by file type. Each feature owns its components, hooks, types, tests.
- Colocate related files. Tests, styles, types live next to the code they belong to.
- Keep files under 300 lines. If a file grows beyond this, split it.
- One responsibility per file. Each file does one thing, exports one primary concept.
- Consistent file structure across all features. Same pattern, same names, same organization.
- Shared code lives in a dedicated shared/ directory, not scattered.
- Features never import from other features. If code needs sharing, move to shared/.
- Evaluate dependencies before adding. Check if native APIs or existing packages cover the need.
- Wrap third-party libraries behind project interfaces for swappability.
- Never hardcode environment-specific values. Use .env files with type-safe validation.
- Never expose secrets to client bundles.

## Violations

- Files with 500+ lines mixing multiple concerns
- Grouping by type: /components/, /hooks/, /utils/ at the top level
- Feature A importing from Feature B's internals
- Adding a dependency without checking if the functionality already exists
- Hardcoded API URLs or environment-specific values in source code
- Inconsistent feature structure (each feature organized differently)

## Right vs Wrong

Examples are illustrative. See References.md for this project's specific implementation.

```
WRONG (grouped by type):
src/
  components/LoginForm.tsx
  components/Dashboard.tsx
  hooks/useAuth.ts
  hooks/useDashboard.ts

RIGHT (grouped by feature):
src/features/
  auth/
    LoginForm.tsx
    useAuth.ts
    types.ts
    index.ts
  dashboard/
    Dashboard.tsx
    useDashboard.ts
    types.ts
    index.ts
```

```
WRONG (importing across features):
// In features/dashboard/
import { authService } from '../auth/services/authService'

RIGHT (using shared system):
// Move to shared if needed by multiple features
import { authService } from '@/shared/auth'
```

## References.md Section

- Folder structure: actual project tree with annotations
- Path alias: configured alias (e.g., @/ maps to src/)
- Package manager: which one and install command
- Env files: hierarchy and prefix convention
- Dependency wrappers: where they live and pattern to follow
