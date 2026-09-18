# Conventions

This is a LOOKUP INDEX. Do not read every convention doc. Scan this list, identify the 2-4 conventions relevant to your current task, and read only those.

This framework operates in 4 phases: Bootstrap (ONBOARD.md) → Scaffold (SCAFFOLD.md) → Develop (DEVELOP.md) → Maintain (MAINTAIN.md).

## Quick Lookup: Which conventions to read per task type

| Task type | Always read | Also read |
|-----------|-------------|-----------|
| Any new feature | #0, #3, #19 | #1 if new folders needed; #28 if UI text/values are involved |
| UI component work | #4, #6, #22, #28 | #14 (accessibility), #27 (check design artifact first), #31 (composition, words) |
| Customer-facing copy / brand values | #28 | #6 (theme tokens), #16 (CONFIG.md) |
| Any UI design decision (states, interactions, hierarchy) | #27, #31, #6 | #22; the session decides within the picked direction and records it (#27); the owner is asked only for identity and what a screen is for (#29) |
| Design session (mockups, a canvas, a design tool or plugin run, a design-system sync) | #27, #29 | #6, #22 (what the code derives from the design), #14 (the floor design content keeps) |
| Interface copy, labels, errors | #31 | #28 (where copy lives), #20 (field errors), #8 (error classes) |
| Design review of a screen | #27 (the review order), #31 | #14, #29 (the reviewer did not build it) |
| Forms | #20, #4, #6 | #7 (validation schemas) |
| API consumption (client-side — fetching from an external API) | #9, #10, #8 | #7 (response types) |
| New API endpoint (server-side — building an API) | backend/B2, #7, #8 | #11 (auth), #23 (input validation); also read backend/Conventions.md for full backend routing |
| Database / migrations | #3, #1 | #7 (model types), #2 (migration commits) |
| Auth (identity) | #11 | #21 (route guards) |
| Permissions / access control | #24, #11 | #3 (architecture) |
| Input validation / security | #23, #7 | #10 (contracts) |
| Security review | #23, #24, #11 | #15 (deps scanning) |
| State management | #5 | #9 (server state) |
| Styling / theming | #6, #22 | #14 (color contrast) |
| Testing | #12, #18 | |
| Build / CI / deploy | #15 | #2 (git hooks), #25 (lint gates) |
| Lint / formatter / enforcement | #25 | #15 (CI gates), #18 (verification) |
| Dev-time project visibility / pulse monitor | #26 | #18 (verification), #16 (documentation) |
| Documentation | #16 | |
| Tracked tasks / project management | development/TASKS.md, development/FRESHNESS.md | project-root protocols/task-context.md; #16, #18, #19 as relevant |
| Repository creation / framework adoption | bootstrap/REPOSITORIES.md, #1, #2 | bootstrap/ONBOARD.md |
| Starting a new AI session | #17, #19, #29 | re-read References.md and PROFILE.md |
| Anything that might need the owner (spend, commitments, live systems, product scope) | #29 | PROFILE.md for the decision-authority setting |
| Deferring work, taking a shortcut, changing the project's stage | #30 | #18 (verification); TECHNICAL-DEBT.md entry with a trigger |

## Convention Index

### #0 Reusability & Composition (META)
Everything built once, configured for context. Governs how all other conventions are implemented. → conventions/00-reusability.md

### Foundation
- #1 Project Setup — file structure, dependencies, environment → conventions/01-project-setup.md
- #2 Git & Version Control — commits as save points, branching, hooks → conventions/02-git.md

### Architecture
- #3 Code Architecture — layers, patterns, feature isolation → conventions/03-architecture.md
- #4 Component Design — component API, hierarchy, wrappers → conventions/04-components.md
- #5 State Management — local-first, server vs client state, data flow → conventions/05-state.md

### Visual
- #6 Styling & Theming — tokens, theme system, responsive, never hardcode → conventions/06-styling.md

### Language
- #7 Type Safety — strict types, no any, runtime validation, types as AI documentation → conventions/07-types.md
- #8 Error Handling & Async — centralized errors, recovery, loading states → conventions/08-errors.md

### Data
- #9 API Integration — centralized API layer, caching, data fetching → conventions/09-api.md
- #10 Frontend-Backend Contract — shared types, generated clients, contract testing → conventions/10-contract.md
- #11 Authentication — centralized auth identity, token management, provider wrapping → conventions/11-auth-security.md

### Security
- #23 Application Security — OWASP, input validation, CORS/CSRF, headers, encryption, audit logging → conventions/23-app-security.md
- #24 Authorization — RBAC/ABAC, service-layer enforcement, object access checks → conventions/24-authorization.md

### Quality
- #12 Testing — TDD, behavior testing, shared test utilities → conventions/12-testing.md
- #13 Performance — code splitting, lazy loading, bundle budgets, user-perceived speed metrics → conventions/13-performance.md
- #14 Accessibility — semantic HTML, keyboard nav, ARIA, focus management → conventions/14-accessibility.md
- #15 Build & CI/CD — pipeline, linting, feature flags, deployment → conventions/15-build-ci.md
- #25 Automated Enforcement — lint rules, formatters, pre-commit hooks, CI gates catch violations at write time → conventions/25-automated-enforcement.md
- #26 Pulse Monitor — dev-only visibility of scaffolded state (project, stack, systems, features, architecture); UI replaceable, data contract durable; applies to projects with a scaffolded code surface → conventions/26-pulse-monitor.md

### Knowledge
- #16 Documentation — comments explain WHY, ADRs, machine-parseable specs → conventions/16-documentation.md

### AI
- #17 Context Management — file size, session hygiene, lost-in-the-middle → conventions/17-context.md
- #18 Verification — TDD for AI, run tests after every change, build gates → conventions/18-verification.md
- #19 AI Steering — specs before code, drift prevention, scope discipline; approval rules read the #29 setting → conventions/19-steering.md
- #29 Decision Authority & Escalation — owner decides the product, AI decides and records everything technical; the escalation categories, one recommendation; no unverified claims; owner safety rails → conventions/29-decision-authority.md
- #30 Operating Profile & Deferral — stage derived from facts (isolated, trial, operational), the floor no stage may defer, trigger-linked deferrals in TECHNICAL-DEBT.md, PROFILE.md → conventions/30-operating-profile.md

### Specialized
- #20 Forms — schema validation, accessible errors, multi-step → conventions/20-forms.md
- #21 Routing — layouts, guards, URL state → conventions/21-routing.md
- #22 Design System — UI wrappers, token-first, component catalog → conventions/22-design-system.md
- #27 Design Foundation — design artifact is source of truth, AI consults it first; when it is silent the session designs within the picked direction and records it; design tools work from the artifact and the owner picks the direction or delegates the pick in words; the state list and the design review order → conventions/27-design-foundation.md
- #28 Config-Driven Brand & Content — every brand/content value lives in one typed config surface, never in view code; templates ship reusable across customers via config-only swap; applies to templates and white-label products → conventions/28-config-driven-content.md
- #31 Interface Craft — one purpose and one primary action per screen; type, space, color, and motion as meaning; words from the person's side in one vocabulary; the default is not a design → conventions/31-interface-craft.md
