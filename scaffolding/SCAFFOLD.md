# Phase 2: Scaffold

Build the foundational systems described in References.md. Run after bootstrap. Each system is built following convention #0 (Reusability) - built once, configured for context, used by every feature.

## Prerequisites

- Phase 1 (Bootstrap) complete
- References.md exists with tech stack and system descriptions
- feature-tree.md initialized

## Scaffolding Prompt

## How to Run Scaffolding

The scaffold has 13 steps. Do NOT run all 13 in one AI session. Break into 3 sessions to keep context fresh:

**Session 1: Foundation (steps 0-4)**
Infrastructure, types, theme, errors, API layer

**Session 2: Core systems (steps 5-9)**
Database, auth, routing, state, components

**Session 3: Quality & delivery (steps 10-12)**
Forms, testing, CI/CD

Start each session with: "Read CLAUDE.md, Conventions.md, References.md, and feature-tree.md. Continue scaffolding from step [N]."

## Scaffolding Prompt (start of each session)

---

Read CLAUDE.md, Conventions.md, and References.md. Read feature-tree.md to see what's already built.

Build the foundational systems in order. For each system:
1. Read the corresponding convention doc
2. Create the code
3. Write docs/systems/{system-name}.md using the template below
4. Update feature-tree.md marking the system as implemented with paths
5. Update References.md with actual paths (if they differ from the bootstrap plan)
6. Verify it works (run build/tests)
7. Commit (save point)

Systems to build (order matters - later systems depend on earlier ones):

### 0. GIT & PROJECT INIT (#2)
- Initialize git if not done in bootstrap
- .gitignore configured for tech stack
- Pre-commit hooks (lint, format, type-check)
- Branch protection rules documented

### 1. PROJECT STRUCTURE & TYPES (#1, #7)
- Folder structure per References.md
- Path aliases configured
- Strict type checking configured for the language (TypeScript strict, mypy strict, nullable reference types, etc.)
- Shared types directory created
- Validation library installed and configured (Zod, Pydantic, FluentValidation, or language equivalent)
- Barrel exports pattern established
- Linting and formatting configured

### 2. THEME SYSTEM (#6) [frontend]
- Design tokens (colors, spacing, typography, shadows, z-index, breakpoints)
- Theme object as single source of truth
- UI library wrappers (never import directly)
- Dark mode support if needed

### 3. ERROR SYSTEM (#8)
- Error classes (NetworkError, ValidationError, NotFoundError, AuthError)
- Error service (catch, classify, log, report)
- Error boundary components [frontend] or error middleware [backend]
- Error UI components [frontend]: fallback, empty state, offline, loading
- Unified loading components [frontend]: full screen, inline, skeleton

### 4. API LAYER (#9, #10)
- Configured client instance (base URL, interceptors)
- Auth token attachment
- Request/response transformation
- Data fetching library integration [frontend] or route/handler setup [backend]
- Cache strategy configured
- Response envelope/format standardized
- API contract setup if applicable (OpenAPI, tRPC, shared schemas)

### 5. DATABASE (#3) [backend]
- ORM/driver configured and connected
- Schema defined (models, relations, indexes)
- Initial migration created
- Query patterns established (query builders or repository pattern if applicable)
- Seed data script if needed for development
- Migration commands documented in References.md

### 5b. FILE STORAGE (#9, #11) [if project handles file uploads]
- File upload service configured (presigned URLs or platform equivalent)
- File validation (type, size) on client and server
- Upload progress tracking
- Background upload (non-blocking UI)
- File viewing/download service
- Storage paths and naming convention documented

### 6. AUTH SYSTEM (#11)
- Auth service (token storage, refresh, logout cleanup)
- Auth context/provider [frontend] or auth middleware [backend]
- Route guard component [frontend] or auth utility [backend]
- Auth utility function (get authenticated user)

### 7. ROUTING & LAYOUTS (#21) [frontend]
- Route definitions
- Layout components (persistent shells)
- Route guard integration with auth system
- Loading and error states per route

### 8. STATE MANAGEMENT (#5) [frontend]
- Store configuration
- Slice pattern template
- Server state integration with API layer

### 9. COMPONENT FOUNDATION (#4, #14, #22) [frontend]
- Base wrapper components for UI library
- Layout components (Stack, Grid, Page containers)
- Accessible base components (Modal, Dialog, Dropdown with proper ARIA)
- Consistent component API patterns documented
- Storybook or component catalog setup if applicable

### 10. FORM SYSTEM (#20) [if project uses forms]
- Form library configured
- Validation schema pattern (one schema = types + validation)
- Form field components with error display
- Multi-step wizard if needed

### 11. TESTING SETUP (#12, #18)
- Test runner configured
- Custom render wrapper with providers [frontend]
- Network-level API mocking configured (MSW, WireMock, responses, httptest, or language equivalent)
- Test data factories
- Verification command documented in References.md

### 12. CI/CD & PERFORMANCE (#15, #13)
- Lint + typecheck + test + build pipeline
- Code splitting configured (route-based) [frontend]
- Bundle budget set [frontend]
- Preview deployments per PR if applicable

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
[Exact import statement using the project's path alias, e.g.:]
import { NotFoundError } from '@/shared/errors'
import { apiClient } from '@/shared/api'
import { Button, Input } from '@/shared/ui'

[Usage example showing the most common pattern]

## Configuration
[How to extend or configure for different contexts]
```

## Additional Documentation Required After Scaffolding

The scaffolding agent must also produce:

1. **.env.example** in the project root listing every required environment variable with a description but no real values. A new developer or AI agent cloning the project must know what env vars to set.

2. **"How to Add a New Feature" section in References.md** - a project-specific step-by-step showing: what folder to create, what files to include, which shared systems to import, which template feature to copy from.

3. **Database schema overview in References.md** (backend) - list the current models and their key fields so a new agent doesn't have to read the raw schema file to understand what data exists.

4. **API endpoint summary in References.md** (backend) - list all endpoints with method, path, request shape, and response shape. A new agent building a frontend or adding a feature needs to know the API without reading handler code.

5. **All shared UI components must use other shared components internally.** The error display component must use the shared Button. The form must use the shared Input. Shared components never use raw HTML when a shared equivalent exists.

## Checklist

After scaffolding, verify:

- [ ] All foundational systems created and working
- [ ] docs/systems/ has a doc for each system with exact import paths
- [ ] feature-tree.md shows all systems as implemented with paths
- [ ] References.md updated with actual paths
- [ ] References.md has "How to Add a New Feature" section
- [ ] References.md has database schema overview (backend)
- [ ] References.md has API endpoint summary (backend)
- [ ] .env.example exists with all required variables documented
- [ ] Theme supports light AND dark mode
- [ ] Shared UI components use other shared components internally (no raw HTML when a shared equivalent exists)
- [ ] Build passes
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Base test suite passes
- [ ] Initial commit with all scaffolding

## What Scaffolding Produces

A working, empty project with all foundational systems in place. No features yet. Any feature can be built immediately by plugging into these systems.

This scaffolding is REUSABLE. Projects with the same tech stack can start from this base. Store it as a template repo.

## Scaffolding Documentation

Every decision made during scaffolding that deviates from the conventions or makes a stack-specific choice is recorded in References.md under "Convention Overrides."

## Log the Scaffold

After scaffolding completes, append to VERSION-LOG.md:

```
## Scaffold

Date: [today's date]
Session(s): [how many sessions it took]
Systems built:
- [system name] → [location] (convention #N)
- [system name] → [location] (convention #N)
- ...
Systems skipped: [which ones and why]
Dependencies installed: [key packages added]
Conventions read: [which convention docs were read during scaffolding]
Verification: [build passes / tests pass / typecheck passes]
```
