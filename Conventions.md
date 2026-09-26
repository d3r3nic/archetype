# Conventions

This is a lookup index. Use the current step or task to identify relevant concerns, including cross-cutting risks. Read their guidance without a document quota; reuse material already current in the session. Each convention opens with when it applies, by how the application works; the standard it holds (#0) is firm, and the form it takes is the project's recorded choice. AGENTS.md describes how to evaluate and record the choice.

This framework operates in 4 phases: Bootstrap (ONBOARD.md) → Scaffold (SCAFFOLD.md) → Develop (DEVELOP.md) → Maintain (MAINTAIN.md).

## Quick Lookup: Which conventions to read per task type

| Task type | Start with | Related concerns |
|-----------|-------------|-----------|
| Any new feature | #0, #3, #19 | #1 if new folders needed; #28 if UI text/values are involved |
| UI component work | #4, #6, #22, #28 | #14 (accessibility), #27 (check design artifact first), #31 (composition, words) |
| Customer-facing copy / brand values | #28 | #6 (theme tokens), #16 (where decisions and records live) |
| Any UI design decision (states, interactions, hierarchy) | #27, #31, #6 | #22; the session decides within the picked direction and records it (#27); the owner is asked only for identity and what a screen is for (#29) |
| Design session (mockups, a canvas, a design tool or plugin run, a design-system sync) | #27, #29 | #6, #22 (what the code derives from the design), #14 (the floor design content keeps) |
| Interface copy, labels, errors | #31 | #28 (where copy lives), #20 (field errors), #8 (error classes) |
| Design review of a screen | #27 (what the review covers), #31 | #14, #29 (the reviewer did not build it) |
| Forms | #20, #4, #6 | #7 (one definition per shape) |
| API consumption (client-side — fetching from an external API) | #9, #10, #8 | #7 (response types) |
| New API endpoint (server-side — building an API) | backend/B2, #7, #8 | #11 (auth), #23 (input validation); also read backend/Conventions.md for full backend routing |
| Database / migrations | backend/B1, #3 | #7 (data shapes), #2 (one reviewable change per migration) |
| Auth (identity) | #11 | #21 (route guards) |
| Permissions / access control | #24, #11 | #3 (architecture) |
| Input validation / security | #23, #7 | #10 (contracts) |
| Security review | #23, #24, #11 | #30 (the floor) |
| State management | #5 | #9 (server state) |
| Styling / theming | #6, #22 | #14 (color contrast) |
| Testing | #12, #18 | |
| Build / CI / deploy | #15 | #2 (history and pushes), #25 (checks) |
| Lint / formatter / enforcement | #25 | #15 (CI gates), #18 (verification) |
| Dev-time project visibility / pulse monitor | #26 | #18 (verification), #16 (documentation) |
| Documentation | #16 | |
| Work outside a playbook's steps (the implementer plan) | development/TASKS.md | #16, #18, #19 as relevant |
| Tasks tracked in a task service the project runs | development/TASKS.md, development/FRESHNESS.md | project-root protocols/task-context.md |
| Repository creation / framework adoption | bootstrap/REPOSITORIES.md | bootstrap/ONBOARD.md; #1 and #2 for the applicable setup and version-control decisions |
| Updating the installed framework | development/UPDATE.md | #2 (one reviewable commit) |
| Two AI assistants taking turns (peer coding) | development/PEER-CODING.md | #29 (independent review, authorizations); the project's peer-coding/SETTINGS.md |
| Starting a new AI session | #17, #19, #29 | re-read References.md and PROFILE.md |
| Anything that might need the owner (spend, commitments, live systems, product scope) | #29 | PROFILE.md for the decision-authority setting |
| Deferring work, taking a shortcut, changing the project's stage | #30 | #18 (verification); TECHNICAL-DEBT.md entry with a trigger |

## Convention Index

### #0 Reusability & Composition (META)
The standard the other conventions apply: build once and reuse, one owner per concern, no duplicated logic or components, no bloat, sized to real usage; separation is the recorded exception. → conventions/00-reusability.md

### Foundation
- #1 Project Setup — file structure, dependencies, environment → conventions/01-project-setup.md
- #2 Git & Version Control — history as recovery and record, checkpoints pushed, the main line kept passing → conventions/02-git.md

### Architecture
- #3 Code Architecture - responsibilities, boundaries and dependency tradeoffs → conventions/03-architecture.md
- #4 Component Design - coherent interfaces and justified component boundaries → conventions/04-components.md
- #5 State Management: ownership, lifetime, propagation and persistence chosen for the domain → conventions/05-state.md

### Visual
- #6 Styling & Theming - visual consistency, chosen schemes and contextual adaptation → conventions/06-styling.md

### Language
- #7 Type Safety & Data Validation — outside data validated at the boundary, one definition per shape, no silenced type errors → conventions/07-types.md
- #8 Error Handling & Async — one error system, nothing swallowed, actionable words for people, a visible state for every wait → conventions/08-errors.md

### Data
- #9 API Integration — one client per remote service, endpoints from the contract, translation at the boundary, file transfer → conventions/09-api.md
- #10 Frontend-Backend Contract — one source of truth for exchanged shapes, one response format, breaking changes caught before release → conventions/10-contract.md
- #11 Authentication — one owner of identity, identity only from the session, credentials stored safely, complete sign-out → conventions/11-auth-security.md

### Security
- #23 Application Security — input validated, output encoded, secrets managed, internals hidden, browser protections where browsers load it, audit trail when required → conventions/23-app-security.md
- #24 Authorization — one permission model, checked where the action runs, against the specific record → conventions/24-authorization.md

### Quality
- #12 Testing — behavior not implementation, fakes only at outer boundaries, shared test setup, effort where failure costs most → conventions/12-testing.md
- #13 Performance - relevant workloads, measured budgets and justified optimization → conventions/13-performance.md
- #14 Accessibility — a recorded target, semantic elements, labels and alternatives, visible focus, every input method → conventions/14-accessibility.md
- #15 Build & CI/CD — the project's checks decide what merges, automated as the project grows, no dead code, a way back from a release → conventions/15-build-ci.md
- #25 Automated Enforcement — reliable checks for recorded rules, § Boundaries for one-owner rules, a check fails or it goes → conventions/25-automated-enforcement.md
- #26 Pulse Monitor — optional dev-only visibility of scaffolded state (project, stack, systems, features, architecture); UI replaceable, data contract durable → conventions/26-pulse-monitor.md

### Knowledge
- #16 Documentation — records hold what code cannot say, one decision location, the decisions the step runner reads → conventions/16-documentation.md

### AI
- #17 Context Management — the project's records carry what the next session needs, one scope at a time → conventions/17-context.md
- #18 Verification: observable outcomes, coherent check boundaries and required gates → conventions/18-verification.md
- #19 AI Steering — do what was asked and nothing more, plans sized to risk, interfaces others depend on changed safely; approval rules read the #29 setting → conventions/19-steering.md
- #29 Decision Authority & Escalation — owner decides the product, AI decides and records everything technical; the escalation categories, one recommendation; no unverified claims; owner safety rails → conventions/29-decision-authority.md
- #30 Operating Profile & Deferral — stage derived from facts (isolated, trial, operational), the floor no stage may defer, trigger-linked deferrals in TECHNICAL-DEBT.md, PROFILE.md → conventions/30-operating-profile.md

### Specialized
- #20 Forms — one form system, validation defined once, errors at their field, nothing typed is lost → conventions/20-forms.md
- #21 Routing — places defined once, one guard, server checks regardless, view state that survives by choice → conventions/21-routing.md
- #22 Design System - one implementation per control, a foundation chosen for fit, the recorded boundary kept → conventions/22-design-system.md
- #27 Design Foundation — design artifact is source of truth, AI consults it first; when it is silent the session designs within the picked direction and records it; design tools work from the artifact and the owner picks the direction or delegates the pick in words; the state list and what a design review covers → conventions/27-design-foundation.md
- #28 Config-Driven Brand & Content — for templates and white-label products: every value that varies by customer in one validated configuration surface, never in view code → conventions/28-config-driven-content.md
- #31 Interface Craft - composition, language and motion evaluated against purpose, medium, constraints and observed use → conventions/31-interface-craft.md
